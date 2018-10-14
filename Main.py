from collections import OrderedDict
from itertools import zip_longest
import json
import logging
import platform
import random
import subprocess
import time
import os
import struct

from BaseClasses import World, CollectionState, Item, Spoiler
from EntranceShuffle import link_entrances
from Rom import LocalRom
from Patches import patch_rom
from Regions import create_regions
from Dungeons import create_dungeons
from Rules import set_rules
from Fill import distribute_items_restrictive
from ItemList import generate_itempool
from Hints import buildGossipHints
from Utils import default_output_path
from version import __version__
from OcarinaSongs import verify_scarecrow_song_str

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

    # verify that the settings are valid
    if settings.free_scarecrow:
        verify_scarecrow_song_str(settings.scarecrow_song, settings.ocarina_songs)

    # initialize the world

    worlds = []
    if settings.compress_rom == 'None':
        settings.create_spoiler = True
        settings.update()

    if not settings.world_count:
        settings.world_count = 1
    if settings.world_count < 1:
        raise Exception('World Count must be at least 1')
    if settings.player_num > settings.world_count or settings.player_num < 1:
        raise Exception('Player Num must be between 1 and %d' % settings.world_count)

    for i in range(0, settings.world_count):
        worlds.append(World(settings))

    random.seed(worlds[0].numeric_seed)

    logger.info('OoT Randomizer Version %s  -  Seed: %s\n\n', __version__, worlds[0].seed)

    window.update_status('Creating the Worlds')
    for id, world in enumerate(worlds):
        world.id = id
        world.player_num = id
        logger.info('Generating World %d.' % id)

        world.spoiler = Spoiler(worlds)

        window.update_progress(0 + (((id + 1) / settings.world_count) * 1))
        logger.info('Creating Overworld')
        if world.quest == 'master':
            for dungeon in world.dungeon_mq:
                world.dungeon_mq[dungeon] = True
        elif world.quest == 'mixed':
            for dungeon in world.dungeon_mq:
                world.dungeon_mq[dungeon] = random.choice([True, False])
        else:
            for dungeon in world.dungeon_mq:
                world.dungeon_mq[dungeon] = False
        create_regions(world)

        window.update_progress(0 + (((id + 1) / settings.world_count) * 2))
        logger.info('Creating Dungeons')
        create_dungeons(world)

        window.update_progress(0 + (((id + 1) / settings.world_count) * 3))
        logger.info('Linking Entrances')
        link_entrances(world)

        if settings.shopsanity != 'off':
            world.random_shop_prices()

        window.update_progress(0 + (((id + 1) / settings.world_count) * 4))
        logger.info('Calculating Access Rules.')
        set_rules(world)

        window.update_progress(0 + (((id + 1) / settings.world_count) * 5))
        logger.info('Generating Item Pool.')
        generate_itempool(world)

    window.update_status('Placing the Items')
    logger.info('Fill the world.')
    distribute_items_restrictive(window, worlds)
    window.update_progress(35)

    if settings.create_spoiler:
        window.update_status('Calculating Spoiler Data')
        logger.info('Calculating playthrough.')
        create_playthrough(worlds)
        window.update_progress(50)
    if settings.hints != 'none':
        window.update_status('Calculating Hint Data')
        CollectionState.update_required_items(worlds)
        if settings.generate_all:
            for id, world in enumerate(worlds):
                buildGossipHints(world)
        else:
            buildGossipHints(worlds[settings.player_num - 1])
        window.update_progress(55)

    window.update_status('Creating Files')

    if settings.generate_all:
        for id, world in enumerate(worlds):
            apply_patch_and_compress(settings, world, window, logger)
    else:
        apply_patch_and_compress(settings, worlds[settings.player_num - 1], window, logger)

    window.update_progress(100)
    window.update_status('Success: Files created')
    logger.info('Done. Enjoy.')
    logger.debug('Total Time: %s', time.clock() - start)

    return worlds[settings.player_num - 1]

def run_process(window, logger, args):
    process = subprocess.Popen(args, bufsize=1, stdout=subprocess.PIPE)
    filecount = None
    while True:
        line = process.stdout.readline()
        if line != b'':
            find_index = line.find(b'files remaining')
            if find_index > -1:
                files = int(line[:find_index].strip())
                if filecount == None:
                    filecount = files
            logger.info(line.decode('utf-8').strip('\n'))
        else:
            break

def create_playthrough(worlds):
    if worlds[0].check_beatable_only and not CollectionState.can_beat_game([world.state for world in worlds]):
        raise RuntimeError('Uncopied is broken too.')
    # create a copy as we will modify it
    old_worlds = worlds
    worlds = [world.copy() for world in worlds]

    # if we only check for beatable, we can do this sanity check first before writing down spheres
    if worlds[0].check_beatable_only and not CollectionState.can_beat_game([world.state for world in worlds]):
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
        if CollectionState.can_beat_game(state_list):
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
    for world in old_worlds:
        world.spoiler.playthrough = OrderedDict([(str(i + 1), {location: location.item for location in sphere}) for i, sphere in enumerate(collection_spheres)])

def apply_patch_and_compress(settings, world, window, logger):
    if settings.world_count > 1:
        outfilebase = 'OoT_%s_%s_W%dP%d' % (world.settings_string, world.seed, world.world_count, (world.player_num + 1))
    else:
        outfilebase = 'OoT_%s_%s' % (world.settings_string, world.seed)

    output_dir = default_output_path(settings.output_dir)

    if settings.compress_rom != 'None':
        logger.info('Patching ROM %d.' % world.id)
        rom = LocalRom(settings)
        patch_rom(world, rom)
        window.update_progress(55 + (40 / settings.world_count) * (world.id + 1 / 4))

        rom_path = os.path.join(output_dir, '%s.z64' % outfilebase)

        logger.info('Saving Uncompressed ROM.')
        rom.write_to_file(rom_path)
        window.update_progress(55 + (40 / settings.world_count) * (world.id + 2 / 4))

        if settings.compress_rom == 'True':
            logger.info('Compressing ROM.')

            compressor_path = ""
            if platform.system() == 'Windows':
                if 8 * struct.calcsize("P") == 64:
                    compressor_path = "Compress\\Compress.exe"
                else:
                    compressor_path = "Compress\\Compress32.exe"
            elif platform.system() == 'Linux':
                compressor_path = "Compress/Compress"
            elif platform.system() == 'Darwin':
                compressor_path = "Compress/Compress.out"
            else:
                logger.info('OS not supported for compression')

            run_process(window, logger, [compressor_path, rom_path, os.path.join(output_dir, '%s-comp.z64' % outfilebase)])
            os.remove(rom_path)
        window.update_progress(55 + (40 / settings.world_count) * (world.id + 3 / 4))


    if settings.create_spoiler:
        logger.info('Creating Spoiler Log.')
        world.spoiler.to_file(os.path.join(output_dir, '%s_Spoiler.txt' % outfilebase))
        window.update_progress(55 + (40 / settings.world_count) * (world.id + 4 / 4))
