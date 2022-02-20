from collections import OrderedDict
import copy
import hashlib
import io
import itertools
import logging
import os, os.path
import platform
import random
import shutil
import subprocess
import sys
import struct
import time
import zipfile

from World import World
from Spoiler import Spoiler
from Rom import Rom
from Patches import patch_rom
from Cosmetics import patch_cosmetics
from DungeonList import create_dungeons
from Fill import distribute_items_restrictive, ShuffleError
from Item import Item
from ItemPool import generate_itempool
from Hints import buildGossipHints
from HintList import clearHintExclusionCache
from Utils import default_output_path, is_bundled, subprocess_args, data_path
from N64Patch import create_patch_file, apply_patch_file
from SettingsList import setting_infos, logic_tricks
from Rules import set_rules, set_shop_rules
from Plandomizer import Distribution
from Search import Search, RewindableSearch
from EntranceShuffle import set_entrances
from LocationList import set_drop_location_names
from Goals import update_goal_items, maybe_set_light_arrows, replace_goal_names
from version import __version__


class dummy_window():
    def __init__(self):
        pass
    def update_status(self, text):
        pass
    def update_progress(self, val):
        pass


def main(settings, window=dummy_window(), max_attempts=10):
    clearHintExclusionCache()
    logger = logging.getLogger('')
    start = time.process_time()

    rom = resolve_settings(settings, window=window)

    max_attempts = max(max_attempts, 1)
    for attempt in range(1, max_attempts + 1):
        try:
            spoiler = generate(settings, window=window)
            break
        except ShuffleError as e:
            logger.warning('Failed attempt %d of %d: %s', attempt, max_attempts, e)
            if attempt >= max_attempts:
                raise
            else:
                logger.info('Retrying...\n\n')
            settings.reset_distribution()
    patch_and_output(settings, window, spoiler, rom)
    logger.debug('Total Time: %s', time.process_time() - start)
    return spoiler


def resolve_settings(settings, window=dummy_window()):
    logger = logging.getLogger('')

    old_tricks = settings.allowed_tricks
    settings.load_distribution()

    # compare pointers to lists rather than contents, so even if the two are identical
    # we'll still log the error and note the dist file overrides completely.
    if old_tricks and old_tricks is not settings.allowed_tricks:
        logger.error('Tricks are set in two places! Using only the tricks from the distribution file.')

    for trick in logic_tricks.values():
        settings.__dict__[trick['name']] = trick['name'] in settings.allowed_tricks

    # we load the rom before creating the seed so that errors get caught early
    if settings.compress_rom == 'None' and not settings.create_spoiler:
        raise Exception('`No Output` must have spoiler enabled to produce anything.')

    if settings.compress_rom not in ['None', 'Temp']:
        window.update_status('Loading ROM')
        rom = Rom(settings.rom)
    else:
        rom = None

    if not settings.world_count:
        settings.world_count = 1
    elif settings.world_count < 1 or settings.world_count > 255:
        raise Exception('World Count must be between 1 and 255')

    # Bounds-check the player_num settings, in case something's gone wrong we want to know.
    if settings.player_num < 1:
        raise Exception(f'Invalid player num: {settings.player_num}; must be between (1, {settings.world_count})')
    if settings.player_num > settings.world_count:
        if settings.compress_rom not in ['None', 'Patch', 'Temp']:
            raise Exception(f'Player Num is {settings.player_num}; must be between (1, {settings.world_count})')
        settings.player_num = settings.world_count

    # Set to a custom hint distribution if plando is overriding the distro
    if len(settings.hint_dist_user) != 0:
        settings.hint_dist = 'custom'

    logger.info('OoT Randomizer Version %s  -  Seed: %s', __version__, settings.seed)
    settings.remove_disabled()
    logger.info('(Original) Settings string: %s\n', settings.settings_string)
    random.seed(settings.numeric_seed)
    settings.resolve_random_settings(cosmetic=False)
    logger.debug(settings.get_settings_display())
    return rom


def generate(settings, window=dummy_window()):
    worlds = build_world_graphs(settings, window=window)
    place_items(settings, worlds, window=window)
    if worlds[0].enable_goal_hints:
        replace_goal_names(worlds)
    return make_spoiler(settings, worlds, window=window)


def build_world_graphs(settings, window=dummy_window()):
    logger = logging.getLogger('')
    worlds = []
    for i in range(0, settings.world_count):
        worlds.append(World(i, copy.copy(settings)))

    window.update_status('Creating the Worlds')
    for id, world in enumerate(worlds):
        logger.info('Generating World %d.' % (id + 1))

        window.update_progress(0 + 1*(id + 1)/settings.world_count)
        logger.info('Creating Overworld')

        if settings.logic_rules == 'glitched':
            overworld_data = os.path.join(data_path('Glitched World'), 'Overworld.json')
        else:
            overworld_data = os.path.join(data_path('World'), 'Overworld.json')

        # Compile the json rules based on settings
        world.load_regions_from_json(overworld_data)
        create_dungeons(world)
        world.create_internal_locations()

        if settings.shopsanity != 'off':
            world.random_shop_prices()
        world.set_scrub_prices()

        window.update_progress(0 + 4*(id + 1)/settings.world_count)
        logger.info('Calculating Access Rules.')
        set_rules(world)

        window.update_progress(0 + 5*(id + 1)/settings.world_count)
        logger.info('Generating Item Pool.')
        generate_itempool(world)
        set_shop_rules(world)
        set_drop_location_names(world)
        world.fill_bosses()

    if settings.triforce_hunt:
        settings.distribution.configure_triforce_hunt(worlds)

    logger.info('Setting Entrances.')
    set_entrances(worlds)
    return worlds


def place_items(settings, worlds, window=dummy_window()):
    logger = logging.getLogger('')
    window.update_status('Placing the Items')
    logger.info('Fill the world.')
    distribute_items_restrictive(window, worlds)
    window.update_progress(35)


def make_spoiler(settings, worlds, window=dummy_window()):
    logger = logging.getLogger('')
    spoiler = Spoiler(worlds)
    if settings.create_spoiler:
        window.update_status('Calculating Spoiler Data')
        logger.info('Calculating playthrough.')
        create_playthrough(spoiler)
        window.update_progress(50)
    if settings.create_spoiler or settings.hints != 'none':
        window.update_status('Calculating Hint Data')
        logger.info('Calculating hint data.')
        update_goal_items(spoiler)
        buildGossipHints(spoiler, worlds)
        window.update_progress(55)
    elif settings.misc_hints:
        # Ganon may still provide the Light Arrows hint
        find_light_arrows(spoiler)
    spoiler.build_file_hash()
    return spoiler


def patch_and_output(settings, window, spoiler, rom):
    logger = logging.getLogger('')
    logger.info('Patching ROM.')
    worlds = spoiler.worlds
    cosmetics_log = None

    settings_string_hash = hashlib.sha1(settings.settings_string.encode('utf-8')).hexdigest().upper()[:5]
    if settings.output_file:
        outfilebase = settings.output_file
    elif settings.world_count > 1:
        outfilebase = 'OoT_%s_%s_W%d' % (settings_string_hash, settings.seed, settings.world_count)
    else:
        outfilebase = 'OoT_%s_%s' % (settings_string_hash, settings.seed)

    output_dir = default_output_path(settings.output_dir)

    if settings.compress_rom == 'Patch':
        rng_state = random.getstate()
        file_list = []
        window.update_progress(65)
        for world in worlds:
            if settings.world_count > 1:
                window.update_status('Patching ROM: Player %d' % (world.id + 1))
                patchfilename = '%sP%d.zpf' % (outfilebase, world.id + 1)
            else:
                window.update_status('Patching ROM')
                patchfilename = '%s.zpf' % outfilebase

            random.setstate(rng_state)
            patch_rom(spoiler, world, rom)
            cosmetics_log = patch_cosmetics(settings, rom)
            rom.update_header()

            window.update_progress(65 + 20*(world.id + 1)/settings.world_count)

            window.update_status('Creating Patch File')
            output_path = os.path.join(output_dir, patchfilename)
            file_list.append(patchfilename)
            create_patch_file(rom, output_path)
            rom.restore()
            window.update_progress(65 + 30*(world.id + 1)/settings.world_count)

            if settings.create_cosmetics_log and cosmetics_log:
                window.update_status('Creating Cosmetics Log')
                if settings.world_count > 1:
                    cosmetics_log_filename = "%sP%d_Cosmetics.json" % (outfilebase, world.id + 1)
                else:
                    cosmetics_log_filename = '%s_Cosmetics.json' % outfilebase
                cosmetics_log.to_file(os.path.join(output_dir, cosmetics_log_filename))
                file_list.append(cosmetics_log_filename)
            cosmetics_log = None

        if settings.world_count > 1:
            window.update_status('Creating Patch Archive')
            output_path = os.path.join(output_dir, '%s.zpfz' % outfilebase)
            with zipfile.ZipFile(output_path, mode="w") as patch_archive:
                for file in file_list:
                    file_path = os.path.join(output_dir, file)
                    patch_archive.write(file_path, file.replace(outfilebase, ''), compress_type=zipfile.ZIP_DEFLATED)
            for file in file_list:
                os.remove(os.path.join(output_dir, file))
        logger.info("Created patchfile at: %s" % output_path)
        window.update_progress(95)

    elif settings.compress_rom not in ['None', 'Temp']:
        window.update_status('Patching ROM')
        patch_rom(spoiler, worlds[settings.player_num - 1], rom)
        cosmetics_log = patch_cosmetics(settings, rom)
        window.update_progress(65)

        window.update_status('Saving Uncompressed ROM')
        if settings.world_count > 1:
            filename = "%sP%d.z64" % (outfilebase, settings.player_num)
        else:
            filename = '%s.z64' % outfilebase
        output_path = os.path.join(output_dir, filename)
        rom.write_to_file(output_path)
        if settings.compress_rom == 'True':
            window.update_status('Compressing ROM')
            logger.info('Compressing ROM.')

            if is_bundled():
                compressor_path = "."
            else:
                compressor_path = "Compress"

            if platform.system() == 'Windows':
                if 8 * struct.calcsize("P") == 64:
                    compressor_path += "\\Compress.exe"
                else:
                    compressor_path += "\\Compress32.exe"
            elif platform.system() == 'Linux':
                if platform.uname()[4] == 'aarch64' or platform.uname()[4] == 'arm64':
                    compressor_path += "/Compress_ARM64"
                else:
                    compressor_path += "/Compress"
            elif platform.system() == 'Darwin':
                compressor_path += "/Compress.out"
            else:
                compressor_path = ""
                logger.info('OS not supported for compression')

            output_compress_path = output_path[:output_path.rfind('.')] + '-comp.z64'
            if compressor_path != "":
                run_process(window, logger, [compressor_path, output_path, output_compress_path])
            os.remove(output_path)
            logger.info("Created compressed rom at: %s" % output_compress_path)
        else:
            logger.info("Created uncompressed rom at: %s" % output_path)
        window.update_progress(95)

    if not settings.create_spoiler or settings.output_settings:
        settings.distribution.update_spoiler(spoiler, False)
        window.update_status('Creating Settings Log')
        settings_path = os.path.join(output_dir, '%s_Settings.json' % outfilebase)
        settings.distribution.to_file(settings_path, False)
        logger.info("Created settings log at: %s" % ('%s_Settings.json' % outfilebase))
    if settings.create_spoiler:
        settings.distribution.update_spoiler(spoiler, True)
        window.update_status('Creating Spoiler Log')
        spoiler_path = os.path.join(output_dir, '%s_Spoiler.json' % outfilebase)
        settings.distribution.to_file(spoiler_path, True)
        logger.info("Created spoiler log at: %s" % ('%s_Spoiler.json' % outfilebase))

    if settings.create_cosmetics_log and cosmetics_log:
        window.update_status('Creating Cosmetics Log')
        if settings.world_count > 1 and not settings.output_file:
            filename = "%sP%d_Cosmetics.json" % (outfilebase, settings.player_num)
        else:
            filename = '%s_Cosmetics.json' % outfilebase
        cosmetic_path = os.path.join(output_dir, filename)
        cosmetics_log.to_file(cosmetic_path)
        logger.info("Created cosmetic log at: %s" % cosmetic_path)

    if settings.enable_distribution_file:
        window.update_status('Copying Distribution File')
        try:
            filename = os.path.join(output_dir, '%s_Distribution.json' % outfilebase)
            shutil.copyfile(settings.distribution_file, filename)
            logger.info("Copied distribution file to: %s" % filename)
        except:
            logger.info('Distribution file copy failed.')

    window.update_progress(100)
    if cosmetics_log and cosmetics_log.errors:
        window.update_status('Success: Rom patched successfully. Some cosmetics could not be applied.')
    else:
        window.update_status('Success: Rom patched successfully')
    logger.info('Done. Enjoy.')


def from_patch_file(settings, window=dummy_window()):
    start = time.process_time()
    logger = logging.getLogger('')

    # we load the rom before creating the seed so that error get caught early
    if settings.compress_rom in ['None', 'Patch', 'Temp']:
        raise Exception('Output Type must be a ROM when patching from a patch file.')
    window.update_status('Loading ROM')
    rom = Rom(settings.rom)

    logger.info('Patching ROM.')

    filename_split = os.path.basename(settings.patch_file).rpartition('.')

    if settings.output_file:
        outfilebase = settings.output_file
    else:
        outfilebase = filename_split[0]

    extension = filename_split[-1]

    output_dir = default_output_path(settings.output_dir)
    output_path = os.path.join(output_dir, outfilebase)

    window.update_status('Patching ROM')
    if extension == 'zpf':
        subfile = None
    else:
        subfile = 'P%d.zpf' % (settings.player_num)
        if not settings.output_file:
            output_path += 'P%d' % (settings.player_num)
    apply_patch_file(rom, settings.patch_file, subfile)
    cosmetics_log = None
    if settings.repatch_cosmetics:
        cosmetics_log = patch_cosmetics(settings, rom)
    window.update_progress(65)

    window.update_status('Saving Uncompressed ROM')
    uncompressed_output_path = output_path + '.z64'
    rom.write_to_file(uncompressed_output_path)
    if settings.compress_rom == 'True':
        window.update_status('Compressing ROM')
        logger.info('Compressing ROM.')

        if is_bundled():
            compressor_path = "."
        else:
            compressor_path = "Compress"

        if platform.system() == 'Windows':
            if 8 * struct.calcsize("P") == 64:
                compressor_path += "\\Compress.exe"
            else:
                compressor_path += "\\Compress32.exe"
        elif platform.system() == 'Linux':
            compressor_path += "/Compress"
        elif platform.system() == 'Darwin':
            compressor_path += "/Compress.out"
        else:
            compressor_path = ""
            logger.info('OS not supported for compression')

        output_compress_path = output_path + '-comp.z64'
        if compressor_path != "":
            run_process(window, logger, [compressor_path, uncompressed_output_path, output_compress_path])
        os.remove(uncompressed_output_path)
        logger.info("Created compressed rom at: %s" % output_compress_path)
    else:
        logger.info("Created uncompressed rom at: %s" % output_path)

    window.update_progress(95)

    if settings.create_cosmetics_log and cosmetics_log:
        window.update_status('Creating Cosmetics Log')
        if settings.world_count > 1 and not settings.output_file:
            filename = "%sP%d_Cosmetics.json" % (outfilebase, settings.player_num)
        else:
            filename = '%s_Cosmetics.json' % outfilebase
        cosmetic_path = os.path.join(output_dir, filename)
        cosmetics_log.to_file(cosmetic_path)
        logger.info("Created cosmetic log at: %s" % cosmetic_path)

    window.update_progress(100)
    if cosmetics_log and cosmetics_log.errors:
        window.update_status('Success: Rom patched successfully. Some cosmetics could not be applied.')
    else:
        window.update_status('Success: Rom patched successfully')

    logger.info('Done. Enjoy.')
    logger.debug('Total Time: %s', time.process_time() - start)

    return True


def cosmetic_patch(settings, window=dummy_window()):
    start = time.process_time()
    logger = logging.getLogger('')

    if settings.patch_file == '':
        raise Exception('Cosmetic Only must have a patch file supplied.')

    window.update_status('Loading ROM')
    rom = Rom(settings.rom)

    logger.info('Patching ROM.')

    filename_split = os.path.basename(settings.patch_file).rpartition('.')

    if settings.output_file:
        outfilebase = settings.output_file
    else:
        outfilebase = filename_split[0]

    extension = filename_split[-1]

    output_dir = default_output_path(settings.output_dir)
    output_path = os.path.join(output_dir, outfilebase)

    window.update_status('Patching ROM')
    if extension == 'zpf':
        subfile = None
    else:
        subfile = 'P%d.zpf' % (settings.player_num)
    apply_patch_file(rom, settings.patch_file, subfile)
    window.update_progress(65)

    # clear changes from the base patch file
    patched_base_rom = copy.copy(rom.buffer)
    rom.changed_address = {}
    rom.changed_dma = {}
    rom.force_patch = []

    window.update_status('Patching ROM')
    patchfilename = '%s_Cosmetic.zpf' % output_path
    cosmetics_log = patch_cosmetics(settings, rom)
    window.update_progress(80)

    window.update_status('Creating Patch File')

    # base the new patch file on the base patch file
    rom.original.buffer = patched_base_rom
    rom.update_header()
    create_patch_file(rom, patchfilename)
    logger.info("Created patchfile at: %s" % patchfilename)
    window.update_progress(95)

    if settings.create_cosmetics_log and cosmetics_log:
        window.update_status('Creating Cosmetics Log')
        if settings.world_count > 1 and not settings.output_file:
            filename = "%sP%d_Cosmetics.json" % (outfilebase, settings.player_num)
        else:
            filename = '%s_Cosmetics.json' % outfilebase
        cosmetic_path = os.path.join(output_dir, filename)
        cosmetics_log.to_file(cosmetic_path)
        logger.info("Created cosmetic log at: %s" % cosmetic_path)

    window.update_progress(100)
    if cosmetics_log and cosmetics_log.errors:
        window.update_status('Success: Rom patched successfully. Some cosmetics could not be applied.')
    else:
        window.update_status('Success: Rom patched successfully')

    logger.info('Done. Enjoy.')
    logger.debug('Total Time: %s', time.process_time() - start)

    return True


def run_process(window, logger, args):
    process = subprocess.Popen(args, **subprocess_args(True))
    filecount = None
    while True:
        line = process.stdout.readline()
        if line != b'':
            find_index = line.find(b'files remaining')
            if find_index > -1:
                files = int(line[:find_index].strip())
                if filecount == None:
                    filecount = files
                window.update_progress(65 + 30*(1 - files/filecount))
            logger.info(line.decode('utf-8').strip('\n'))
        else:
            break


def copy_worlds(worlds):
    worlds = [world.copy() for world in worlds]
    Item.fix_worlds_after_copy(worlds)
    return worlds


def find_light_arrows(spoiler):
    search = Search([world.state for world in spoiler.worlds])
    for location in search.iter_reachable_locations(search.progression_locations()):
        search.collect(location.item)
        maybe_set_light_arrows(location)


def create_playthrough(spoiler):
    worlds = spoiler.worlds
    if worlds[0].check_beatable_only and not Search([world.state for world in worlds]).can_beat_game():
        raise RuntimeError('Uncopied is broken too.')
    # create a copy as we will modify it
    old_worlds = worlds
    worlds = copy_worlds(worlds)

    # if we only check for beatable, we can do this sanity check first before writing down spheres
    if worlds[0].check_beatable_only and not Search([world.state for world in worlds]).can_beat_game():
        raise RuntimeError('Cannot beat game. Something went terribly wrong here!')

    search = RewindableSearch([world.state for world in worlds])
    # Get all item locations in the worlds
    item_locations = search.progression_locations()
    # Omit certain items from the playthrough
    internal_locations = {location for location in item_locations if location.internal}
    # Generate a list of spheres by iterating over reachable locations without collecting as we go.
    # Collecting every item in one sphere means that every item
    # in the next sphere is collectable. Will contain every reachable item this way.
    logger = logging.getLogger('')
    logger.debug('Building up collection spheres.')
    collection_spheres = []
    entrance_spheres = []
    remaining_entrances = set(entrance for world in worlds for entrance in world.get_shuffled_entrances())

    while True:
        search.checkpoint()
        # Not collecting while the generator runs means we only get one sphere at a time
        # Otherwise, an item we collect could influence later item collection in the same sphere
        collected = list(search.iter_reachable_locations(item_locations))
        if not collected: break
        # Gather the new entrances before collecting items.
        collection_spheres.append(collected)
        accessed_entrances = set(filter(search.spot_access, remaining_entrances))
        entrance_spheres.append(accessed_entrances)
        remaining_entrances -= accessed_entrances
        for location in collected:
            # Collect the item for the state world it is for
            search.state_list[location.item.world.id].collect(location.item)
            maybe_set_light_arrows(location)
    logger.info('Collected %d spheres', len(collection_spheres))
    spoiler.full_playthrough = dict((location.name, i + 1) for i, sphere in enumerate(collection_spheres) for location in sphere)
    spoiler.max_sphere = len(collection_spheres)

    # Reduce each sphere in reverse order, by checking if the game is beatable
    # when we remove the item. We do this to make sure that progressive items
    # like bow and slingshot appear as early as possible rather than as late as possible.
    required_locations = []
    for sphere in reversed(collection_spheres):
        for location in sphere:
            # we remove the item at location and check if the game is still beatable in case the item could be required
            old_item = location.item

            # Uncollect the item and location.
            search.state_list[old_item.world.id].remove(old_item)
            search.unvisit(location)

            # Generic events might show up or not, as usual, but since we don't
            # show them in the final output, might as well skip over them. We'll
            # still need them in the final pass, so make sure to include them.
            if location.internal:
                required_locations.append(location)
                continue

            location.item = None

            # An item can only be required if it isn't already obtained or if it's progressive
            if search.state_list[old_item.world.id].item_count(old_item.name) < old_item.world.max_progressions[old_item.name]:
                # Test whether the game is still beatable from here.
                logger.debug('Checking if %s is required to beat the game.', old_item.name)
                if not search.can_beat_game():
                    # still required, so reset the item
                    location.item = old_item
                    required_locations.append(location)

    # Reduce each entrance sphere in reverse order, by checking if the game is beatable when we disconnect the entrance.
    required_entrances = []
    for sphere in reversed(entrance_spheres):
        for entrance in sphere:
            # we disconnect the entrance and check if the game is still beatable
            old_connected_region = entrance.disconnect()

            # we use a new search to ensure the disconnected entrance is no longer used
            sub_search = Search([world.state for world in worlds])

            # Test whether the game is still beatable from here.
            logger.debug('Checking if reaching %s, through %s, is required to beat the game.', old_connected_region.name, entrance.name)
            if not sub_search.can_beat_game():
                # still required, so reconnect the entrance
                entrance.connect(old_connected_region)
                required_entrances.append(entrance)

    # Regenerate the spheres as we might not reach places the same way anymore.
    search.reset() # search state has no items, okay to reuse sphere 0 cache
    collection_spheres = []
    entrance_spheres = []
    remaining_entrances = set(required_entrances)
    collected = set()
    while True:
        # Not collecting while the generator runs means we only get one sphere at a time
        # Otherwise, an item we collect could influence later item collection in the same sphere
        collected.update(search.iter_reachable_locations(required_locations))
        if not collected: break
        internal = collected & internal_locations
        if internal:
            # collect only the internal events but don't record them in a sphere
            for location in internal:
                search.state_list[location.item.world.id].collect(location.item)
            # Remaining locations need to be saved to be collected later
            collected -= internal
            continue
        # Gather the new entrances before collecting items.
        collection_spheres.append(list(collected))
        accessed_entrances = set(filter(search.spot_access, remaining_entrances))
        entrance_spheres.append(accessed_entrances)
        remaining_entrances -= accessed_entrances
        for location in collected:
            # Collect the item for the state world it is for
            search.state_list[location.item.world.id].collect(location.item)
        collected.clear()
    logger.info('Collected %d final spheres', len(collection_spheres))

    # Then we can finally output our playthrough
    spoiler.playthrough = OrderedDict((str(i + 1), {location: location.item for location in sphere}) for i, sphere in enumerate(collection_spheres))
    # Copy our light arrows, since we set them in the world copy
    for w, sw in zip(worlds, spoiler.worlds):
        if w.light_arrow_location:
            # But the actual location saved here may be in a different world
            sw.light_arrow_location = spoiler.worlds[w.light_arrow_location.world.id].get_location(w.light_arrow_location.name)

    if worlds[0].entrance_shuffle:
        spoiler.entrance_playthrough = OrderedDict((str(i + 1), list(sphere)) for i, sphere in enumerate(entrance_spheres))
