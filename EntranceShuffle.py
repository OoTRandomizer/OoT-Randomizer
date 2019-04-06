import random
import logging
from Playthrough import Playthrough
from Rules import set_entrances_based_rules
from Entrance import Entrance


def get_entrance_pool(type):
    return {name: data for (name, data) in entrance_shuffle_table.items() if data[0] == type}


entrance_shuffle_table = {
    'Outside Deku Tree -> Deku Tree Lobby':                     ('Dungeon',  { 'forward': 0x0000, 'return' : 0x0209, 'blue' : 0x0457 }),
    'Dodongos Cavern Entryway -> Dodongos Cavern Beginning':    ('Dungeon',  { 'forward': 0x0004, 'return' : 0x0242, 'blue' : 0x047A }),
    'Zoras Fountain -> Jabu Jabus Belly Beginning':             ('Dungeon',  { 'forward': 0x0028, 'return' : 0x0221, 'blue' : 0x010E }),
    'Sacred Forest Meadow -> Forest Temple Lobby':              ('Dungeon',  { 'forward': 0x0169, 'return' : 0x0215, 'blue' : 0x0608 }),
    'Death Mountain Crater Central -> Fire Temple Lower':       ('Dungeon',  { 'forward': 0x0165, 'return' : 0x024A, 'blue' : 0x0564 }),
    'Lake Hylia -> Water Temple Lobby':                         ('Dungeon',  { 'forward': 0x0010, 'return' : 0x021D, 'blue' : 0x060C }),
    'Desert Colossus -> Spirit Temple Lobby':                   ('Dungeon',  { 'forward': 0x0082, 'return' : 0x01E1, 'blue' : 0x0610 }),
    'Shadow Temple Warp Region -> Shadow Temple Entryway':      ('Dungeon',  { 'forward': 0x0037, 'return' : 0x0205, 'blue' : 0x0580 }),
    'Kakariko Village -> Bottom of the Well':                   ('Dungeon',  { 'forward': 0x0098, 'return' : 0x02A6, }),
    'Zoras Fountain -> Ice Cavern Beginning':                   ('Dungeon',  { 'forward': 0x0088, 'return' : 0x03D4, }),
    'Gerudo Fortress -> Gerudo Training Grounds Lobby':         ('Dungeon',  { 'forward': 0x0008, 'return' : 0x03A8, }),

    'Kokiri Forest -> Mido House':                              ('Interior', { 'forward': 0x0433, 'return': 0x0443 }),
    'Kokiri Forest -> Saria House':                             ('Interior', { 'forward': 0x0437, 'return': 0x0447 }),
    'Kokiri Forest -> House of Twins':                          ('Interior', { 'forward': 0x009C, 'return': 0x033C }),
    'Kokiri Forest -> Know It All House':                       ('Interior', { 'forward': 0x00C9, 'return': 0x026A }),
    'Kokiri Forest -> Kokiri Shop':                             ('Interior', { 'forward': 0x00C1, 'return': 0x0266 }),
    'Lake Hylia -> Lake Hylia Lab':                             ('Interior', { 'forward': 0x0043, 'return': 0x03CC }),
    'Lake Hylia -> Fishing Hole':                               ('Interior', { 'forward': 0x045F, 'return': 0x0309 }),
    'Gerudo Valley Far Side -> Carpenter Tent':                 ('Interior', { 'forward': 0x03A0, 'return': 0x03D0 }),
    'Castle Town -> Castle Town Rupee Room':                    ('Interior', { 'forward': 0x007E, 'return': 0x026E }),
    'Castle Town -> Castle Town Mask Shop':                     ('Interior', { 'forward': 0x0530, 'return': 0x01D1 }),
    'Castle Town -> Castle Town Bombchu Bowling':               ('Interior', { 'forward': 0x0507, 'return': 0x03BC }),
    'Castle Town -> Castle Town Potion Shop':                   ('Interior', { 'forward': 0x0388, 'return': 0x02A2 }),
    'Castle Town -> Castle Town Treasure Chest Game':           ('Interior', { 'forward': 0x0063, 'return': 0x01D5 }),
    'Castle Town -> Castle Town Bombchu Shop':                  ('Interior', { 'forward': 0x0528, 'return': 0x03C0 }),
    'Castle Town -> Castle Town Man in Green House':            ('Interior', { 'forward': 0x043B, 'return': 0x0067 }),
    'Kakariko Village -> Carpenter Boss House':                 ('Interior', { 'forward': 0x02FD, 'return': 0x0349 }),
    'Kakariko Village -> House of Skulltula':                   ('Interior', { 'forward': 0x0550, 'return': 0x04EE }),
    'Kakariko Village -> Impas House':                          ('Interior', { 'forward': 0x039C, 'return': 0x0345 }),
    'Kakariko Village -> Impas House Back':                     ('Interior', { 'forward': 0x05C8, 'return': 0x05DC }),
    'Kakariko Village -> Odd Medicine Building':                ('Interior', { 'forward': 0x0072, 'return': 0x034D }),
    'Graveyard -> Dampes House':                                ('Interior', { 'forward': 0x030D, 'return': 0x0355 }),
    'Goron City -> Goron Shop':                                 ('Interior', { 'forward': 0x037C, 'return': 0x03FC }),
    'Zoras Domain -> Zora Shop':                                ('Interior', { 'forward': 0x0380, 'return': 0x03C4 }),
    'Lon Lon Ranch -> Talon House':                             ('Interior', { 'forward': 0x004F, 'return': 0x0378 }),
    'Lon Lon Ranch -> Ingo Barn':                               ('Interior', { 'forward': 0x02F9, 'return': 0x042F }),
    'Lon Lon Ranch -> Lon Lon Corner Tower':                    ('Interior', { 'forward': 0x05D0, 'return': 0x05D4 }),
    'Castle Town -> Castle Town Bazaar':                        ('Interior', { 'forward': 0x052C, 'return': 0x03B8, 'exit_address': 0xBEFD74 }),
    'Castle Town -> Castle Town Shooting Gallery':              ('Interior', { 'forward': 0x016D, 'return': 0x01CD, 'exit_address': 0xBEFD7C }),
    'Kakariko Village -> Kakariko Bazaar':                      ('Interior', { 'forward': 0x00B7, 'return': 0x0201, 'exit_address': 0xBEFD72 }),
    'Kakariko Village -> Kakariko Shooting Gallery':            ('Interior', { 'forward': 0x003B, 'return': 0x0463, 'exit_address': 0xBEFD7A }),
    'Desert Colossus -> Colossus Fairy':                        ('Interior', { 'forward': 0x0588, 'return': 0x057C, 'exit_address': 0xBEFD82 }),
    'Hyrule Castle Grounds -> Hyrule Castle Fairy':             ('Interior', { 'forward': 0x0578, 'return': 0x0340, 'exit_address': 0xBEFD80 }),
    'Ganons Castle Grounds -> Ganons Castle Fairy':             ('Interior', { 'forward': 0x04C2, 'return': 0x0340, 'exit_address': 0xBEFD6C }),
    'Death Mountain Crater Lower -> Crater Fairy':              ('Interior', { 'forward': 0x04BE, 'return': 0x0482, 'exit_address': 0xBEFD6A }),
    'Death Mountain Summit -> Mountain Summit Fairy':           ('Interior', { 'forward': 0x0315, 'return': 0x045B, 'exit_address': 0xBEFD68 }),
    'Zoras Fountain -> Zoras Fountain Fairy':                   ('Interior', { 'forward': 0x0371, 'return': 0x0394, 'exit_address': 0xBEFD7E }),

    'Desert Colossus -> Desert Colossus Grotto':                ('Grotto',   { 'scene': 0x5C, 'grotto_var': 0x00FD }),
    'Lake Hylia -> Lake Hylia Grotto':                          ('Grotto',   { 'scene': 0x57, 'grotto_var': 0x00EF }),
    'Zora River -> Zora River Storms Grotto':                   ('Grotto',   { 'scene': 0x54, 'grotto_var': 0x01EB }),
    'Zora River -> Zora River Plateau Bombable Grotto':         ('Grotto',   { 'scene': 0x54, 'grotto_var': 0x10E6 }),
    'Zora River -> Zora River Plateau Open Grotto':             ('Grotto',   { 'scene': 0x54, 'grotto_var': 0x0029 }),
    'Death Mountain Crater Lower -> DMC Hammer Grotto':         ('Grotto',   { 'scene': 0x61, 'grotto_var': 0x00F9 }),
    'Death Mountain Crater Upper -> Top of Crater Grotto':      ('Grotto',   { 'scene': 0x61, 'grotto_var': 0x007A }),
    'Goron City -> Goron City Grotto':                          ('Grotto',   { 'scene': 0x62, 'grotto_var': 0x00FB }),
    'Death Mountain -> Mountain Storms Grotto':                 ('Grotto',   { 'scene': 0x60, 'grotto_var': 0x0157 }),
    'Death Mountain -> Mountain Bombable Grotto':               ('Grotto',   { 'scene': 0x60, 'grotto_var': 0x00F8 }),
    'Kakariko Village -> Kakariko Back Grotto':                 ('Grotto',   { 'scene': 0x52, 'grotto_var': 0x0028 }),
    'Kakariko Village -> Kakariko Bombable Grotto':             ('Grotto',   { 'scene': 0x52, 'grotto_var': 0x02E7 }),
    'Hyrule Castle Grounds -> Castle Storms Grotto':            ('Grotto',   { 'scene': 0x5F, 'grotto_var': 0x01F6 }),
    'Hyrule Field -> Field North Lon Lon Grotto':               ('Grotto',   { 'scene': 0x51, 'grotto_var': 0x02E1 }),
    'Hyrule Field -> Field Kakariko Grotto':                    ('Grotto',   { 'scene': 0x51, 'grotto_var': 0x02E5 }),
    'Hyrule Field -> Field Far West Castle Town Grotto':        ('Grotto',   { 'scene': 0x51, 'grotto_var': 0x10FF }),
    'Hyrule Field -> Field West Castle Town Grotto':            ('Grotto',   { 'scene': 0x51, 'grotto_var': 0x0000 }),
    'Hyrule Field -> Field Valley Grotto':                      ('Grotto',   { 'scene': 0x51, 'grotto_var': 0x02E4 }),
    'Hyrule Field -> Field Near Lake Inside Fence Grotto':      ('Grotto',   { 'scene': 0x51, 'grotto_var': 0x02E6 }),
    'Hyrule Field -> Field Near Lake Outside Fence Grotto':     ('Grotto',   { 'scene': 0x51, 'grotto_var': 0x0003 }),
    'Hyrule Field -> Remote Southern Grotto':                   ('Grotto',   { 'scene': 0x51, 'grotto_var': 0x0022 }),
    'Lon Lon Ranch -> Lon Lon Grotto':                          ('Grotto',   { 'scene': 0x63, 'grotto_var': 0x00FC }),
    'Sacred Forest Meadow Entryway -> Front of Meadow Grotto':  ('Grotto',   { 'scene': 0x56, 'grotto_var': 0x02ED }),
    'Sacred Forest Meadow -> Meadow Storms Grotto':             ('Grotto',   { 'scene': 0x56, 'grotto_var': 0x01EE }),
    'Sacred Forest Meadow -> Meadow Fairy Grotto':              ('Grotto',   { 'scene': 0x56, 'grotto_var': 0x10FF }),
    'Lost Woods Beyond Mido -> Lost Woods Sales Grotto':        ('Grotto',   { 'scene': 0x5B, 'grotto_var': 0x00F5 }),
    'Lost Woods -> Lost Woods Generic Grotto':                  ('Grotto',   { 'scene': 0x5B, 'grotto_var': 0x0014 }),
    'Kokiri Forest -> Kokiri Forest Storms Grotto':             ('Grotto',   { 'scene': 0x55, 'grotto_var': 0x012C }),
    'Zoras Domain -> Zoras Domain Storms Grotto':               ('Grotto',   { 'scene': 0x58, 'grotto_var': 0x11FF }),
    'Gerudo Fortress -> Gerudo Fortress Storms Grotto':         ('Grotto',   { 'scene': 0x5D, 'grotto_var': 0x11FF }),
    'Gerudo Valley Far Side -> Gerudo Valley Storms Grotto':    ('Grotto',   { 'scene': 0x5A, 'grotto_var': 0x01F0 }),
    'Gerudo Valley -> Gerudo Valley Octorok Grotto':            ('Grotto',   { 'scene': 0x5A, 'grotto_var': 0x00F2 }),
    'Lost Woods Beyond Mido -> Deku Theater':                   ('Grotto',   { 'scene': 0x5B, 'grotto_var': 0x00F3 }),
}


class EntranceShuffleError(RuntimeError):
    pass


# Set entrances of all worlds, first initializing them to their default regions, then potentially shuffling part of them
def set_entrances(worlds):
    for world in worlds:
        world.initialize_entrances()

    if worlds[0].entrance_shuffle != 'off':
        shuffle_entrances(worlds)

    set_entrances_based_rules(worlds)


# Shuffles entrances that need to be shuffled in all worlds
def shuffle_entrances(worlds):

    # Store all locations unreachable to differentiate which locations were already unreachable from those we made unreachable while shuffling entrances
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]
    max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)

    all_locations = [location for world in worlds for location in world.get_locations()]
    max_playthrough.visit_locations(all_locations)
    already_unreachable_locations = [location for location in all_locations if not max_playthrough.visited(location)]

    # Shuffle all entrance pools based on settings

    if worlds[0].shuffle_dungeon_entrances:
        dungeon_entrance_pool = get_entrance_pool('Dungeon')
        # The fill algorithm will already make sure gohma is reachable, however it can end up putting
        # a forest escape via the hands of spirit on Deku leading to Deku on spirit in logic. This is
        # not really a closed forest anymore, so specifically remove Deku Tree from closed forest.
        if (not worlds[0].open_forest):
            del dungeon_entrance_pool["Outside Deku Tree -> Deku Tree Lobby"]
        shuffle_entrance_pool(worlds, dungeon_entrance_pool, already_unreachable_locations)

    if worlds[0].shuffle_interior_entrances:
        interior_entrance_pool = get_entrance_pool('Interior')
        shuffle_entrance_pool(worlds, interior_entrance_pool, already_unreachable_locations)

    if worlds[0].shuffle_grotto_entrances:
        grotto_entrance_pool = get_entrance_pool('Grotto')
        shuffle_entrance_pool(worlds, grotto_entrance_pool, already_unreachable_locations)

    # Multiple checks after shuffling entrances to make sure everything went fine

    for world in worlds:
        entrances_shuffled = world.get_shuffled_entrances()

        # Check that all target regions have exactly one entrance among those we shuffled
        target_regions = [entrance.connected_region for entrance in entrances_shuffled]
        for region in target_regions:
            region_shuffled_entrances = list(filter(lambda entrance: entrance in entrances_shuffled, region.entrances))
            if len(region_shuffled_entrances) != 1:
                logging.getLogger('').error('%s has %d shuffled entrances after shuffling, expected exactly 1 [World %d]',
                                                region, len(region_shuffled_entrances), world.id)

    # New playthrough with shuffled entrances
    max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)
    max_playthrough.visit_locations(all_locations)

    # Log all locations unreachable due to shuffling entrances
    alr_compliant = True
    if not worlds[0].check_beatable_only:
        for location in all_locations:
            if not location in already_unreachable_locations and \
               not max_playthrough.visited(location):
                logging.getLogger('').error('Location now unreachable after shuffling entrances: %s [World %d]', location, location.world.id)
                alr_compliant = False

    # Check for game beatability in all worlds
    # Can this ever fail, if Triforce is in complete_itempool?
    if not max_playthrough.can_beat_game(False):
        raise EntranceShuffleError('Cannot beat game!')

    # Throw an error if shuffling entrances broke the contract of ALR (All Locations Reachable)
    if not alr_compliant:
        raise EntranceShuffleError('ALR is enabled but not all locations are reachable!')


# Shuffle all entrances within a provided pool for all worlds
def shuffle_entrance_pool(worlds, entrance_pool, already_unreachable_locations):

    # Shuffle entrances only within their own world
    for world in worlds:

        # Initialize entrances to shuffle with their addresses and shuffle type
        entrances_to_shuffle = []
        for entrance_name, (type, addresses) in entrance_pool.items():
            entrance = world.get_entrance(entrance_name)
            entrance.type = type
            entrance.addresses = addresses
            # Regions should associate specific entrances with specific addresses. But for the moment, keep it simple as dungeon and
            # interior ER only ever has one rando entrance per region.
            if entrance.connected_region.addresses is not None:
                raise EntranceShuffleError('Entrance rando of regions with multiple rando entrances not supported [World %d]' % world.id)
            entrance.connected_region.addresses = addresses
            entrance.shuffled = True
            entrances_to_shuffle.append(entrance)

        # Split entrances between those that have requirements (restrictive) and those that do not (soft). These are primarly age requirements.
        # Restrictive entrances should be placed first while more regions are available. The remaining regions are then just placed on
        # soft entrances without any need for logic.
        restrictive_entrances, soft_entrances = split_entrances_by_requirements(worlds, entrances_to_shuffle)

        # Assumed Fill: Unplace, and assume we have access to entrances by connecting them to the root of reachability
        root = world.get_region('Root')
        target_regions = [entrance.disconnect() for entrance in entrances_to_shuffle]
        target_entrances = []
        for target_region in target_regions:
            fill_entrance = Entrance("Root -> " + target_region.name, root)
            fill_entrance.connect(target_region)
            root.exits.append(fill_entrance)
            target_entrances.append(fill_entrance)

        shuffle_entrances_restrictive(worlds, restrictive_entrances, target_entrances, already_unreachable_locations)
        shuffle_entrances_fast(worlds, soft_entrances, target_entrances)


# Split entrances based on their requirements to figure out how each entrance should be handled when shuffling them
# This is done to ensure that we can place them in an order less likely to fail, and with the appropriate method to optimize the placement speed
# Indeed, some entrances should be handled before others, and this also allows us to determine which entrances don't need to check for reachability
# If all entrances were handled in a random order, the algorithm could have high chances to fail to connect the last few entrances because of requirements
def split_entrances_by_requirements(worlds, entrances_to_split):

    # Retrieve all items in the itempool, all worlds included
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]

    # First, disconnect all entrances and save which regions they were originally connected to, so we can reconnect them later
    original_connected_regions = {}
    for entrance in entrances_to_split:
        original_connected_regions[entrance.name] = entrance.disconnect()

    # Generate the states with all entrances disconnected
    # This ensures that no pre existing entrances among those to shuffle are required in order for an entrance to be reachable as one age
    # Some entrances may not be reachable because of this, but this is fine as long as we deal with those entrances as being very limited
    max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)

    restrictive_entrances = []
    soft_entrances = []

    for entrance in entrances_to_split:
        # Here, we find entrances that may be unreachable under certain conditions
        if not max_playthrough.state_list[entrance.world.id].can_reach(entrance, age='both', tod='all'):
            restrictive_entrances.append(entrance)
            continue
        # If an entrance is reachable as both ages and all times of day with all the other entrances disconnected,
        # then it can always be made accessible in all situations by the Fill algorithm, no matter which combination of entrances we end up with.
        # Thus, those entrances aren't bound to any specific requirements and are very versatile during placement.
        soft_entrances.append(entrance)

    # Reconnect all entrances afterwards
    for entrance in entrances_to_split:
        entrance.connect(original_connected_regions[entrance.name])

    return restrictive_entrances, soft_entrances


# Shuffle entrances by connecting them to a region among the provided target regions list
# While shuffling entrances, the algorithm will use states generated from all items yet to be placed to figure how entrances can be placed
# If ALR is enabled, this will mean checking that all locations previously reachable are still reachable every time we try to place an entrance
# Otherwise, only the beatability of the game may be assured, which is what would be expected without ALR enabled
def shuffle_entrances_restrictive(worlds, entrances, target_entrances, already_unreachable_locations, retry_count=16):

    all_locations = [location for world in worlds for location in world.get_locations()]

    # Retrieve all items in the itempool, all worlds included
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]

    for _ in range(retry_count):
        success = True;
        random.shuffle(entrances)
        rollbacks = []

        for entrance in entrances:
            random.shuffle(target_entrances)

            for target in target_entrances:
                entrance.connect(target.disconnect())

                # Regenerate the playthrough because the final states might have changed after connecting/disconnecting entrances
                max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)

                # If we only have to check that the game is still beatable, and the game is indeed still beatable, we can use that region
                can_connect = True
                if not (worlds[0].check_beatable_only and max_playthrough.can_beat_game(False)):
                    max_playthrough.visit_locations(all_locations)

                    # Figure out if this entrance can be connected to the region being tested
                    # We consider that it can be connected if ALL locations previously reachable are still reachable
                    for location in all_locations:
                        if not location in already_unreachable_locations and \
                           not max_playthrough.visited(location):
                            logging.getLogger('').debug('Failed to connect %s To %s (because of %s) [World %d]',
                                                            entrance, entrance.connected_region, location, entrance.world.id)

                            can_connect = False
                            break

                if can_connect:
                    rollbacks.append((target, entrance))
                    used_target = target
                    break

                # The entrance and target combo no good, undo and continue try the next
                target.connect(entrance.disconnect())

            if entrance.connected_region is None:
                # An entrance failed to place every remaining target. This attempt is a bust.
                success = False
                break

            target_entrances.remove(used_target)

        if success:
            for target, entrance in rollbacks:
                logging.getLogger('').debug('Connected %s To %s [World %d]', entrance, entrance.connected_region, entrance.world.id)
                target.parent_region.exits.remove(target)
                del target
            return

        for target, entrance in rollbacks:
            region = entrance.disconnect()
            target_entrances.append(target)
            target.connect(region)

        logging.getLogger('').debug('Entrance placement attempt failed [World %d]', entrances[0].world.id)

    raise EntranceShuffleError('Fill attempt retry count exceeded [World %d]' % entrances[0].world.id)

# Shuffle entrances by connecting them to a random region among the provided target regions list
# This doesn't check for reachability nor beatability and just connects all entrances to random regions
# This is only meant to be used to shuffle entrances that we already know as completely versatile
# Which means that they can't ever permanently prevent the access of any locations, no matter how they are placed
def shuffle_entrances_fast(worlds, entrances, target_entrances):

    random.shuffle(target_entrances)
    for entrance in entrances:
        target = target_entrances.pop()
        entrance.connect(target.disconnect())
        target.parent_region.exits.remove(target)
        del target
        logging.getLogger('').debug('Connected %s To %s [World %d]', entrance, entrance.connected_region, entrance.world.id)

