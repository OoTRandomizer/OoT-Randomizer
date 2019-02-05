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
from Rom import LocalRom
from Patches import patch_rom
from Cosmetics import patch_cosmetics
from DungeonList import create_dungeons
from Fill import distribute_items_restrictive
from Item import Item
from ItemPool import generate_itempool
from Hints import buildGossipHints
from Utils import default_output_path, is_bundled, subprocess_args, data_path
from version import __version__
from N64Patch import create_patch_file, apply_patch_file
from SettingsList import setting_infos, logic_tricks
from Rules import set_rules


class dummy_window():
    def __init__(self):
        pass
    def update_status(self, text):
        pass
    def update_progress(self, val):
        pass


def main(settings, window=dummy_window()):

    start = time.clock()

    logger = logging.getLogger('')

    worlds = []

    allowed_tricks = {}
    for trick in logic_tricks.values():
        settings.__dict__[trick['name']] = trick['name'] in settings.allowed_tricks


    # we load the rom before creating the seed so that error get caught early
    if settings.compress_rom == 'None' and not settings.create_spoiler:
        raise Exception('`No Output` must have spoiler enabled to produce anything.')

    if settings.compress_rom != 'None':
        window.update_status('Loading ROM')
        rom = LocalRom(settings)

    if not settings.world_count:
        settings.world_count = 1
    if settings.world_count < 1 or settings.world_count > 255:
        raise Exception('World Count must be between 1 and 255')
    if settings.player_num > settings.world_count or settings.player_num < 1:
        if settings.compress_rom not in ['None', 'Patch']:
            raise Exception('Player Num must be between 1 and %d' % settings.world_count)
        else:
            settings.player_num = 1

    settings.remove_disabled()

    logger.info('OoT Randomizer Version %s  -  Seed: %s\n\n', __version__, settings.seed)
    random.seed(settings.numeric_seed)
    for i in range(0, settings.world_count):
        worlds.append(World(settings))

    window.update_status('Creating the Worlds')
    for id, world in enumerate(worlds):
        world.id = id
        logger.info('Generating World %d.' % id)

        window.update_progress(0 + 1*(id + 1)/settings.world_count)
        logger.info('Creating Overworld')

        # Determine MQ Dungeons
        td_count = len(world.dungeon_mq)
        if world.mq_dungeons_random:
            world.mq_dungeons = random.randint(0, td_count)
        mqd_count = world.mq_dungeons
        mqd_picks = random.sample(list(world.dungeon_mq), mqd_count)
        for dung in mqd_picks:
            world.dungeon_mq[dung] = True


        overworld_data = os.path.join(data_path('World'), 'Overworld.json')
        world.load_regions_from_json(overworld_data)

        create_dungeons(world)

        world.initialize_entrances()

        if settings.shopsanity != 'off':
            world.random_shop_prices()
        world.set_scrub_prices()

        window.update_progress(0 + 4*(id + 1)/settings.world_count)
        logger.info('Calculating Access Rules.')
        set_rules(world)

        window.update_progress(0 + 5*(id + 1)/settings.world_count)
        logger.info('Generating Item Pool.')
        generate_itempool(world)


    window.update_status('Placing the Items')
    logger.info('Fill the world.')
    distribute_items_restrictive(window, worlds)
    window.update_progress(35)

    spoiler = Spoiler(worlds)
    cosmetics_log = None
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

    logger.info('Patching ROM.')

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
            patch_cosmetics(settings, rom)
            window.update_progress(65 + 20*(world.id + 1)/settings.world_count)

            window.update_status('Creating Patch File')
            output_path = os.path.join(output_dir, patchfilename)
            file_list.append(patchfilename)
            create_patch_file(rom, output_path)
            rom.restore()
            window.update_progress(65 + 30*(world.id + 1)/settings.world_count)

        if settings.world_count > 1:
            window.update_status('Creating Patch Archive')
            output_path = os.path.join(output_dir, '%s.zpfz' % outfilebase)
            with zipfile.ZipFile(output_path, mode="w") as patch_archive:
                for index, file in enumerate(file_list):
                    file_path = os.path.join(output_dir, file)
                    patch_archive.write(file_path, 'P%d.zpf' % (index + 1), compress_type=zipfile.ZIP_DEFLATED)
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
        for setting in world.settings.__dict__:
            world.settings.__dict__[setting] = world.__dict__[setting]

    if settings.create_spoiler:
        window.update_status('Creating Spoiler Log')
        spoiler.to_file(os.path.join(output_dir, '%s_Spoiler.txt' % outfilebase))
    else:
        window.update_status('Creating Settings Log')
        spoiler.to_file(os.path.join(output_dir, '%s_Settings.txt' % outfilebase))
    logger.info("Created spoiler log at: %s" % ('%s_Settings.txt' % outfilebase))

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
    logger.debug('Total Time: %s', time.clock() - start)

    return worlds[settings.player_num - 1]


def from_patch_file(settings, window=dummy_window()):
    start = time.clock()
    logger = logging.getLogger('')

    # we load the rom before creating the seed so that error get caught early
    if settings.compress_rom == 'None' or settings.compress_rom == 'Patch':
        raise Exception('Output Type must be a ROM when patching from a patch file.')
    window.update_status('Loading ROM')
    rom = LocalRom(settings)

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
    logger.debug('Total Time: %s', time.clock() - start)

    return True


def cosmetic_patch(settings, window=dummy_window()):
    start = time.clock()
    logger = logging.getLogger('')

    if settings.patch_file == '':
        raise Exception('Cosmetic Only must have a patch file supplied.')

    window.update_status('Loading ROM')
    rom = LocalRom(settings)

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

    rom.update_crc()
    rom.original = copy.copy(rom.buffer)
    rom.changed_address = {}
    rom.changed_dma = {}
    rom.force_patch = []

    window.update_status('Patching ROM')
    patchfilename = '%s_Cosmetic.zpf' % output_path
    cosmetics_log = patch_cosmetics(settings, rom)
    window.update_progress(80)

    window.update_status('Creating Patch File')
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
    logger.debug('Total Time: %s', time.clock() - start)

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
    required_locations = []
    item_locations = [location for state in state_list for location in state.world.get_filled_locations() if location.item.advancement]

    # in the first phase, we create the generous spheres. Collecting every item in a sphere will
    # mean that every item in the next sphere is collectable. Will contain every reachable item
    logging.getLogger('').debug('Building up collection spheres.')

    # will loop if there is more items opened up in the previous iteration. Always run once
    reachable_items_locations = True
    while reachable_items_locations:
        # get reachable new items locations
        reachable_items_locations = [location for location in item_locations if location.name not in state_list[location.world.id].collected_locations and state_list[location.world.id].can_reach(location)]
        for location in reachable_items_locations:
            # Mark the location collected in the state world it exists in
            state_list[location.world.id].collected_locations[location.name] = True
            # Collect the item for the state world it is for
            state_list[location.item.world.id].collect(location.item)
            required_locations.append(location)

    # in the second phase, we cull each sphere such that the game is still beatable, reducing each
    # range of influence to the bare minimum required inside it. Effectively creates a min play
    for location in reversed(required_locations):
        # we remove the item at location and check if game is still beatable
        logging.getLogger('').debug('Checking if %s is required to beat the game.', location.item.name)
        old_item = location.item

        # Uncollect the item location. Removing it from the collected_locations
        # will ensure that can_beat_game will try to collect it if it can.
        # Because we search in reverse sphere order, all the later spheres will
        # have their locations flagged to be re-searched.
        location.item = None
        state_list[old_item.world.id].remove(old_item)
        del state_list[location.world.id].collected_locations[location.name]

        # remove the item from the world and test if the game is still beatable
        if State.can_beat_game(state_list):
            # cull entries for spoiler walkthrough at end
            required_locations.remove(location)
        else:
            # still required, got to keep it around
            location.item = old_item

    # This ensures the playthrough shows items being collected in the proper order.
    collection_spheres = []
    while required_locations:
        sphere = [location for location in required_locations if state_list[location.world.id].can_reach(location)]
        for location in sphere:
            required_locations.remove(location)
            state_list[location.item.world.id].collect(location.item)
        collection_spheres.append(sphere)

    # we can finally output our playthrough
    spoiler.playthrough = OrderedDict([(str(i + 1), {location: location.item for location in sphere}) for i, sphere in enumerate(collection_spheres)])
