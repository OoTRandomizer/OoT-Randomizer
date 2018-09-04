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

from BaseClasses import World, CollectionState, Item
from EntranceShuffle import link_entrances
from Rom import LocalRom
from Patches import patch_rom
from Regions import create_regions
from Dungeons import create_dungeons
from Rules import set_rules
from Fill import distribute_items_restrictive
from ItemList import generate_itempool
from Utils import default_output_path
from version import __version__

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
        logger.info('Generating World %d.' % id)

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
    window.update_status('Calculating Hint Data')
    CollectionState.update_required_items(worlds)
    window.update_progress(55)

    logger.info('Patching ROM.')

    if settings.world_count > 1:
        outfilebase = 'OoT_%s_%s_W%dP%d' % (worlds[0].settings_string, worlds[0].seed, worlds[0].world_count, worlds[0].player_num)
    else:
        outfilebase = 'OoT_%s_%s' % (worlds[0].settings_string, worlds[0].seed)

    output_dir = default_output_path(settings.output_dir)

    if settings.compress_rom != 'None':
        window.update_status('Patching ROM')
        rom = LocalRom(settings)
        patch_rom(worlds[settings.player_num - 1], rom)
        window.update_progress(65)

        rom_path = os.path.join(output_dir, '%s.z64' % outfilebase)

        window.update_status('Saving Uncompressed ROM')
        rom.write_to_file(rom_path)
        if settings.compress_rom == 'True':
            window.update_status('Compressing ROM')
            logger.info('Compressing ROM.')
            if platform.system() == 'Windows':
                if 8 * struct.calcsize("P") == 64:
                    run_process(window, logger, ["Compress\\Compress.exe", rom_path, os.path.join(output_dir, '%s-comp.z64' % outfilebase)])
                else:
                    run_process(window, logger, ["Compress\\Compress32.exe", rom_path, os.path.join(output_dir, '%s-comp.z64' % outfilebase)])
                os.remove(rom_path)
            elif platform.system() == 'Linux':
                run_process(window, logger, ["Compress/Compress", rom_path, os.path.join(output_dir, '%s-comp.z64' % outfilebase)])
                os.remove(rom_path)
            elif platform.system() == 'Darwin':
                run_process(window, logger, ["Compress/Compress.out", rom_path, os.path.join(output_dir, '%s-comp.z64' % outfilebase)])
                os.remove(rom_path)
            else:
                logger.info('OS not supported for compression')
            window.update_progress(95)


    if settings.create_spoiler:
        window.update_status('Creating Spoiler Log')
        worlds[settings.player_num - 1].spoiler.to_file(os.path.join(output_dir, '%s_Spoiler.txt' % outfilebase))

    window.update_progress(100)
    window.update_status('Success: Rom patched successfully')
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
                window.update_progress(65 + ((1 - (files / filecount)) * 30))
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

    state_list = [CollectionState(world) for world in worlds]

    # Get all item locations in the worlds
    collection_spheres = []
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
        if reachable_items_locations:
            collection_spheres.append(reachable_items_locations)

    # in the second phase, we cull each sphere such that the game is still beatable, reducing each 
    # range of influence to the bare minimum required inside it. Effectively creates a min play
    for num, sphere in reversed(list(enumerate(collection_spheres))):
        to_delete = []
        for location in sphere:
            # we remove the item at location and check if game is still beatable
            logging.getLogger('').debug('Checking if %s is required to beat the game.', location.item.name)
            old_item = location.item
            old_state_list = [state.copy() for state in state_list]

            location.item = None
            state_list[old_item.world.id].remove(old_item)
            CollectionState.remove_locations(state_list)
            if CollectionState.can_beat_game(state_list, False):
                to_delete.append(location)
            else:
                # still required, got to keep it around
                state_list = old_state_list
                location.item = old_item

        # cull entries in spheres for spoiler walkthrough at end
        for location in to_delete:
            sphere.remove(location)
    collection_spheres = [sphere for sphere in collection_spheres if sphere]

    # we can finally output our playthrough
    for world in old_worlds:
        world.spoiler.playthrough = OrderedDict([(str(i + 1), {location: location.item for location in sphere}) for i, sphere in enumerate(collection_spheres)])

