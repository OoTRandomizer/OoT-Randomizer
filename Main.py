from collections import OrderedDict
import logging
import platform
import random
import subprocess
import time
import os, os.path
import sys
import struct
import zipfile
import io
import hashlib
import copy

from World import World
from State import State
from Spoiler import Spoiler
from Rom import Rom
from Patches import patch_rom
from Cosmetics import patch_cosmetics
from DungeonList import create_dungeons
from Fill import distribute_items_restrictive, FillError
from Item import Item
from ItemPool import generate_itempool
from Hints import buildGossipHints
from Utils import default_output_path, is_bundled, subprocess_args, data_path
from version import __version__
from N64Patch import create_patch_file, apply_patch_file
from SettingsList import setting_infos, logic_tricks
from Rules import set_rules, set_shop_rules
from Plandomizer import Distribution
from Playthrough import Playthrough
from EntranceShuffle import set_entrances
from LocationList import set_drop_location_names


class dummy_window():
    def __init__(self):
        pass
    def update_status(self, text):
        pass
    def update_progress(self, val):
        pass


def main(settings, window=dummy_window()):

    start = time.process_time()

    logger = logging.getLogger('')

    worlds = []

    for trick in logic_tricks.values():
        settings.__dict__[trick['name']] = trick['name'] in settings.allowed_tricks

    settings.load_distribution()

    # we load the rom before creating the seed so that error get caught early
    if settings.compress_rom == 'None' and not settings.create_spoiler:
        raise Exception('`No Output` must have spoiler enabled to produce anything.')

    if settings.compress_rom != 'None':
        window.update_status('Loading ROM')
        rom = Rom(settings.rom)
    else:
        rom = None

    if not settings.world_count:
        settings.world_count = 1
    if settings.world_count < 1 or settings.world_count > 255:
        raise Exception('World Count must be between 1 and 255')
    if settings.player_num > settings.world_count or settings.player_num < 1:
        if settings.compress_rom not in ['None', 'Patch']:
            raise Exception('Player Num must be between 1 and %d' % settings.world_count)
        else:
            settings.player_num = 1

    logger.info('OoT Randomizer Version %s  -  Seed: %s', __version__, settings.seed)
    settings.remove_disabled()
    logger.info('(Original) Settings string: %s\n', settings.settings_string)
    random.seed(settings.numeric_seed)
    settings.resolve_random_settings()
    logger.debug(settings.get_settings_display())
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            spoiler = generate(settings, window)
            break
        except FillError as fe:
            logger.warn('Failed attempt %d of %d: %s', attempt, max_attempts, fe)
            if attempt >= max_attempts:
                raise
            else:
                logger.info('Retrying...\n\n')
    return patch_and_output(settings, window, spoiler, rom, start)


def generate(settings, window):
    logger = logging.getLogger('')
    worlds = []
    for i in range(0, settings.world_count):
        worlds.append(World(settings))

    window.update_status('Creating the Worlds')
    for id, world in enumerate(worlds):
        world.id = id
        world.distribution = settings.distribution.world_dists[id]
        logger.info('Generating World %d.' % id)

        window.update_progress(0 + 1*(id + 1)/settings.world_count)
        logger.info('Creating Overworld')

        # Determine MQ Dungeons
        dungeon_pool = list(world.dungeon_mq)
        dist_num_mq = world.distribution.configure_dungeons(world, dungeon_pool)

        if world.mq_dungeons_random:
            for dungeon in dungeon_pool:
                world.dungeon_mq[dungeon] = random.choice([True, False])
            world.mq_dungeons = list(world.dungeon_mq.values()).count(True)
        else:
            mqd_picks = random.sample(dungeon_pool, world.mq_dungeons - dist_num_mq)
            for dung in mqd_picks:
                world.dungeon_mq[dung] = True

        overworld_data = os.path.join(data_path('World'), 'Overworld.json')
        world.load_regions_from_json(overworld_data)

        create_dungeons(world)

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

    logger.info('Setting Entrances.')
    set_entrances(worlds)

    window.update_status('Placing the Items')
    logger.info('Fill the world.')
    distribute_items_restrictive(window, worlds)
    window.update_progress(35)

    spoiler = Spoiler(worlds)
    if settings.create_spoiler:
        window.update_status('Calculating Spoiler Data')
        logger.info('Calculating playthrough.')
        create_playthrough(spoiler)
        window.update_progress(50)
    if settings.create_spoiler or settings.hints != 'none':
        window.update_status('Calculating Hint Data')
        State.update_required_items(spoiler)
        for world in worlds:
            world.update_useless_areas(spoiler)
            buildGossipHints(spoiler, world)
        window.update_progress(55)
    spoiler.build_file_hash()
    return spoiler


def patch_and_output(settings, window, spoiler, rom, start):
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
                    cosmetics_log_filename = "%sP%d_Cosmetics.txt" % (outfilebase, world.id + 1)
                else:
                    cosmetics_log_filename = '%s_Cosmetics.txt' % outfilebase
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

    elif settings.compress_rom != 'None':
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
            logger.info("Created compessed rom at: %s" % output_compress_path)
        else:
            logger.info("Created uncompessed rom at: %s" % output_path)
        window.update_progress(95)

    for world in worlds:
        for info in setting_infos:
            world.settings.__dict__[info.name] = world.__dict__[info.name]

    settings.distribution.update_spoiler(spoiler)
    if settings.create_spoiler:
        window.update_status('Creating Spoiler Log')
        spoiler_path = os.path.join(output_dir, '%s_Spoiler.json' % outfilebase)
        settings.distribution.to_file(spoiler_path)
        logger.info("Created spoiler log at: %s" % ('%s_Spoiler.json' % outfilebase))
    else:
        window.update_status('Creating Settings Log')
        settings_path = os.path.join(output_dir, '%s_Settings.json' % outfilebase)
        settings.distribution.to_file(settings_path)
        logger.info("Created settings log at: %s" % ('%s_Settings.json' % outfilebase))

    if settings.create_cosmetics_log and cosmetics_log:
        window.update_status('Creating Cosmetics Log')
        if settings.world_count > 1 and not settings.output_file:
            filename = "%sP%d_Cosmetics.txt" % (outfilebase, settings.player_num)
        else:
            filename = '%s_Cosmetics.txt' % outfilebase
        cosmetic_path = os.path.join(output_dir, filename)
        cosmetics_log.to_file(cosmetic_path)
        logger.info("Created cosmetic log at: %s" % cosmetic_path)

    window.update_progress(100)
    if cosmetics_log and cosmetics_log.error:
        window.update_status('Success: Rom patched successfully. Some cosmetics could not be applied.')
    else:
        window.update_status('Success: Rom patched successfully')
    logger.info('Done. Enjoy.')
    logger.debug('Total Time: %s', time.process_time() - start)

    return worlds[settings.player_num - 1]


def from_patch_file(settings, window=dummy_window()):
    start = time.process_time()
    logger = logging.getLogger('')

    # we load the rom before creating the seed so that error get caught early
    if settings.compress_rom == 'None' or settings.compress_rom == 'Patch':
        raise Exception('Output Type must be a ROM when patching from a patch file.')
    window.update_status('Loading ROM')
    rom = Rom(settings.rom)

    logger.info('Patching ROM.')

    filename_split = os.path.basename(settings.patch_file).split('.')

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
        logger.info("Created compessed rom at: %s" % output_compress_path)
    else:
        logger.info("Created uncompessed rom at: %s" % output_path)

    window.update_progress(95)

    if settings.create_cosmetics_log and cosmetics_log:
        window.update_status('Creating Cosmetics Log')
        if settings.world_count > 1 and not settings.output_file:
            filename = "%sP%d_Cosmetics.txt" % (outfilebase, settings.player_num)
        else:
            filename = '%s_Cosmetics.txt' % outfilebase
        cosmetic_path = os.path.join(output_dir, filename)
        cosmetics_log.to_file(cosmetic_path)
        logger.info("Created cosmetic log at: %s" % cosmetic_path)

    window.update_progress(100)
    if cosmetics_log and cosmetics_log.error:
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

    filename_split = os.path.basename(settings.patch_file).split('.')

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
    rom.original = patched_base_rom

    rom.update_crc()
    create_patch_file(rom, patchfilename)
    logger.info("Created patchfile at: %s" % patchfilename)
    window.update_progress(95)

    if settings.create_cosmetics_log and cosmetics_log:
        window.update_status('Creating Cosmetics Log')
        if settings.world_count > 1 and not settings.output_file:
            filename = "%sP%d_Cosmetics.txt" % (outfilebase, settings.player_num)
        else:
            filename = '%s_Cosmetics.txt' % outfilebase
        cosmetic_path = os.path.join(output_dir, filename)
        cosmetics_log.to_file(cosmetic_path)
        logger.info("Created cosmetic log at: %s" % cosmetic_path)

    window.update_progress(100)
    if cosmetics_log and cosmetics_log.error:
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


def create_playthrough(spoiler):
    worlds = spoiler.worlds
    if worlds[0].check_beatable_only and not State.can_beat_game([world.state for world in worlds]):
        raise RuntimeError('Uncopied is broken too.')
    # create a copy as we will modify it
    old_worlds = worlds
    worlds = copy_worlds(worlds)

    # if we only check for beatable, we can do this sanity check first before writing down spheres
    if worlds[0].check_beatable_only and not State.can_beat_game([world.state for world in worlds]):
        raise RuntimeError('Cannot beat game. Something went terribly wrong here!')

    state_list = [world.state for world in worlds]

    # Get all item locations in the worlds
    item_locations = [location for state in state_list for location in state.world.get_filled_locations() if location.item.advancement]
    # Generate a list of spheres by iterating over reachable locations without collecting as we go.
    # Collecting every item in one sphere means that every item
    # in the next sphere is collectable. Will contain every reachable item this way.
    logger = logging.getLogger('')
    logger.debug('Building up collection spheres.')
    collection_spheres = []
    playthrough = Playthrough(state_list)
    while True:
        # Not collecting while the generator runs means we only get one sphere at a time
        # Otherwise, an item we collect could influence later item collection in the same sphere
        collected = list(playthrough.iter_reachable_locations(item_locations))
        if not collected: break
        for location in collected:
            # Collect the item for the state world it is for
            state_list[location.item.world.id].collect(location.item)
        collection_spheres.append(collected)
    logger.info('Collected %d spheres', len(collection_spheres))

    # Reduce each sphere in reverse order, by checking if the game is beatable
    # when we remove the item. We do this to make sure that progressive items
    # like bow and slingshot appear as early as possible rather than as late as possible.
    required_locations = []
    for sphere in reversed(collection_spheres):
        for location in sphere:
            # we remove the item at location and check if the game is still beatable in case the item could be required
            old_item = location.item
            location.item = None

            # Uncollect the item and location.
            state_list[old_item.world.id].remove(old_item)
            playthrough.unvisit(location)

            # An item can only be required if it isn't already obtained or if it's progressive
            if state_list[old_item.world.id].item_count(old_item.name) < old_item.special.get('progressive', 1):
                # Test whether the game is still beatable from here.
                logger.debug('Checking if %s is required to beat the game.', old_item.name)
                if not playthrough.can_beat_game():
                    # still required, so reset the item
                    location.item = old_item
                    required_locations.append(location)

    # Regenerate the spheres as we might not reach places the same way anymore.
    playthrough.reset()  # playthrough state has no items, okay to reuse sphere 0 cache
    collection_spheres = []
    entrance_spheres = []
    remaining_entrances = set(entrance for world in worlds for entrance in world.get_shuffled_entrances() if entrance.primary)
    while True:
        # Not collecting while the generator runs means we only get one sphere at a time
        # Otherwise, an item we collect could influence later item collection in the same sphere
        collected = list(playthrough.iter_reachable_locations(required_locations))
        accessed_entrances = set(filter(lambda entrance: state_list[entrance.world.id].can_reach(entrance), remaining_entrances))
        if not collected: break
        for location in collected:
            # Collect the item for the state world it is for
            state_list[location.item.world.id].collect(location.item)
        collection_spheres.append(collected)
        entrance_spheres.append(accessed_entrances)
        remaining_entrances -= accessed_entrances
    logger.info('Collected %d final spheres', len(collection_spheres))

    # Then we can finally output our playthrough
    spoiler.playthrough = OrderedDict((str(i + 1), {location: location.item for location in sphere}) for i, sphere in enumerate(collection_spheres))

    if worlds[0].entrance_shuffle != 'off':
        spoiler.entrance_playthrough = OrderedDict((str(i + 1), list(sphere)) for i, sphere in enumerate(entrance_spheres))
