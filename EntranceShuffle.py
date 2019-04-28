import random
import logging
from collections import OrderedDict
from Playthrough import Playthrough
from Rules import set_entrances_based_rules
from Entrance import Entrance
from State import State
from Item import ItemFactory


def get_entrance_pool(type):
    return [entrance_data for entrance_data in entrance_shuffle_table if entrance_data[0] == type]


def entrance_instances(world, entrance_pool):
    entrance_instances = []
    for type, forward_entrance, *return_entrance in entrance_pool:
        forward_entrance = set_shuffled_entrance(world, forward_entrance[0], forward_entrance[1], type)
        forward_entrance.primary = True
        if return_entrance:
            return_entrance = return_entrance[0]
            return_entrance = set_shuffled_entrance(world, return_entrance[0], return_entrance[1], type)
            forward_entrance.bind_two_way(return_entrance)
        entrance_instances.append(forward_entrance)
    return entrance_instances


def set_shuffled_entrance(world, name, data, type):
    entrance = world.get_entrance(name)
    entrance.type = type
    entrance.data = data
    entrance.shuffled = True
    return entrance


def assume_pool_reachable(world, entrance_pool):
    assumed_pool = []
    for entrance in entrance_pool:
        assumed_forward = entrance.assume_reachable()
        if entrance.reverse != None:
            assumed_return = entrance.reverse.assume_reachable()
            if entrance.type in ['Dungeon', 'Interior', 'Grotto']:
                # Dungeon, Grotto and Simple Interior exits shouldn't be assumed to be able to give access to their parent region
                assumed_return.access_rule = lambda state: False
            assumed_forward.bind_two_way(assumed_return)
        assumed_pool.append(assumed_forward)
    return assumed_pool


entrance_shuffle_table = [
    ('Dungeon',         ('Outside Deku Tree -> Deku Tree Lobby',                            { 'index': 0x0000 }),
                        ('Deku Tree Lobby -> Outside Deku Tree',                            { 'index': 0x0209, 'blue_warp': 0x0457 })),
    ('Dungeon',         ('Dodongos Cavern Entryway -> Dodongos Cavern Beginning',           { 'index': 0x0004 }),
                        ('Dodongos Cavern Beginning -> Dodongos Cavern Entryway',           { 'index': 0x0242, 'blue_warp': 0x047A })),
    ('Dungeon',         ('Zoras Fountain -> Jabu Jabus Belly Beginning',                    { 'index': 0x0028 }),
                        ('Jabu Jabus Belly Beginning -> Zoras Fountain',                    { 'index': 0x0221, 'blue_warp': 0x010E })),
    ('Dungeon',         ('Sacred Forest Meadow -> Forest Temple Lobby',                     { 'index': 0x0169 }),
                        ('Forest Temple Lobby -> Sacred Forest Meadow',                     { 'index': 0x0215, 'blue_warp': 0x0608 })),
    ('Dungeon',         ('Death Mountain Crater Central -> Fire Temple Lower',              { 'index': 0x0165 }),
                        ('Fire Temple Lower -> Death Mountain Crater Central',              { 'index': 0x024A, 'blue_warp': 0x0564 })),
    ('Dungeon',         ('Lake Hylia -> Water Temple Lobby',                                { 'index': 0x0010 }),
                        ('Water Temple Lobby -> Lake Hylia',                                { 'index': 0x021D, 'blue_warp': 0x060C })),
    ('Dungeon',         ('Desert Colossus -> Spirit Temple Lobby',                          { 'index': 0x0082 }),
                        ('Spirit Temple Lobby -> Desert Colossus',                          { 'index': 0x01E1, 'blue_warp': 0x0610 })),
    ('Dungeon',         ('Shadow Temple Warp Region -> Shadow Temple Entryway',             { 'index': 0x0037 }),
                        ('Shadow Temple Entryway -> Shadow Temple Warp Region',             { 'index': 0x0205, 'blue_warp': 0x0580 })),
    ('Dungeon',         ('Kakariko Village -> Bottom of the Well',                          { 'index': 0x0098 }),
                        ('Bottom of the Well -> Kakariko Village',                          { 'index': 0x02A6 })),
    ('Dungeon',         ('Zoras Fountain -> Ice Cavern Beginning',                          { 'index': 0x0088 }),
                        ('Ice Cavern Beginning -> Zoras Fountain',                          { 'index': 0x03D4 })),
    ('Dungeon',         ('Gerudo Fortress -> Gerudo Training Grounds Lobby',                { 'index': 0x0008 }),
                        ('Gerudo Training Grounds Lobby -> Gerudo Fortress',                { 'index': 0x03A8 })),

    ('Interior',        ('Kokiri Forest -> Mido House',                                     { 'index': 0x0433 }),
                        ('Mido House -> Kokiri Forest',                                     { 'index': 0x0443 })),
    ('Interior',        ('Kokiri Forest -> Saria House',                                    { 'index': 0x0437 }),
                        ('Saria House -> Kokiri Forest',                                    { 'index': 0x0447 })),
    ('Interior',        ('Kokiri Forest -> House of Twins',                                 { 'index': 0x009C }),
                        ('House of Twins -> Kokiri Forest',                                 { 'index': 0x033C })),
    ('Interior',        ('Kokiri Forest -> Know It All House',                              { 'index': 0x00C9 }),
                        ('Know It All House -> Kokiri Forest',                              { 'index': 0x026A })),
    ('Interior',        ('Kokiri Forest -> Kokiri Shop',                                    { 'index': 0x00C1 }),
                        ('Kokiri Shop -> Kokiri Forest',                                    { 'index': 0x0266 })),
    ('Interior',        ('Lake Hylia -> Lake Hylia Lab',                                    { 'index': 0x0043 }),
                        ('Lake Hylia Lab -> Lake Hylia',                                    { 'index': 0x03CC })),
    ('Interior',        ('Lake Hylia -> Fishing Hole',                                      { 'index': 0x045F }),
                        ('Fishing Hole -> Lake Hylia',                                      { 'index': 0x0309 })),
    ('Interior',        ('Gerudo Valley Far Side -> Carpenter Tent',                        { 'index': 0x03A0 }),
                        ('Carpenter Tent -> Gerudo Valley Far Side',                        { 'index': 0x03D0 })),
    ('Interior',        ('Castle Town Entrance -> Castle Town Rupee Room',                  { 'index': 0x007E }),
                        ('Castle Town Rupee Room -> Castle Town Entrance',                  { 'index': 0x026E })),
    ('Interior',        ('Castle Town -> Castle Town Mask Shop',                            { 'index': 0x0530 }),
                        ('Castle Town Mask Shop -> Castle Town',                            { 'index': 0x01D1 })),
    ('Interior',        ('Castle Town -> Castle Town Bombchu Bowling',                      { 'index': 0x0507 }),
                        ('Castle Town Bombchu Bowling -> Castle Town',                      { 'index': 0x03BC })),
    ('Interior',        ('Castle Town -> Castle Town Potion Shop',                          { 'index': 0x0388 }),
                        ('Castle Town Potion Shop -> Castle Town',                          { 'index': 0x02A2 })),
    ('Interior',        ('Castle Town -> Castle Town Treasure Chest Game',                  { 'index': 0x0063 }),
                        ('Castle Town Treasure Chest Game -> Castle Town',                  { 'index': 0x01D5 })),
    ('Interior',        ('Castle Town -> Castle Town Bombchu Shop',                         { 'index': 0x0528 }),
                        ('Castle Town Bombchu Shop -> Castle Town',                         { 'index': 0x03C0 })),
    ('Interior',        ('Castle Town -> Castle Town Man in Green House',                   { 'index': 0x043B }),
                        ('Castle Town Man in Green House -> Castle Town',                   { 'index': 0x0067 })),
    ('Interior',        ('Kakariko Village -> Carpenter Boss House',                        { 'index': 0x02FD }),
                        ('Carpenter Boss House -> Kakariko Village',                        { 'index': 0x0349 })),
    ('Interior',        ('Kakariko Village -> House of Skulltula',                          { 'index': 0x0550 }),
                        ('House of Skulltula -> Kakariko Village',                          { 'index': 0x04EE })),
    ('Interior',        ('Kakariko Village -> Impas House',                                 { 'index': 0x039C }),
                        ('Impas House -> Kakariko Village',                                 { 'index': 0x0345 })),
    ('Interior',        ('Kakariko Village -> Impas House Back',                            { 'index': 0x05C8 }),
                        ('Impas House Back -> Kakariko Village',                            { 'index': 0x05DC })),
    ('Interior',        ('Kakariko Village -> Odd Medicine Building',                       { 'index': 0x0072 }),
                        ('Odd Medicine Building -> Kakariko Village',                       { 'index': 0x034D })),
    ('Interior',        ('Graveyard -> Dampes House',                                       { 'index': 0x030D }),
                        ('Dampes House -> Graveyard',                                       { 'index': 0x0355 })),
    ('Interior',        ('Goron City -> Goron Shop',                                        { 'index': 0x037C }),
                        ('Goron Shop -> Goron City',                                        { 'index': 0x03FC })),
    ('Interior',        ('Zoras Domain -> Zora Shop',                                       { 'index': 0x0380 }),
                        ('Zora Shop -> Zoras Domain',                                       { 'index': 0x03C4 })),
    ('Interior',        ('Lon Lon Ranch -> Talon House',                                    { 'index': 0x004F }),
                        ('Talon House -> Lon Lon Ranch',                                    { 'index': 0x0378 })),
    ('Interior',        ('Lon Lon Ranch -> Ingo Barn',                                      { 'index': 0x02F9 }),
                        ('Ingo Barn -> Lon Lon Ranch',                                      { 'index': 0x042F })),
    ('Interior',        ('Lon Lon Ranch -> Lon Lon Corner Tower',                           { 'index': 0x05D0 }),
                        ('Lon Lon Corner Tower -> Lon Lon Ranch',                           { 'index': 0x05D4 })),
    ('Interior',        ('Castle Town -> Castle Town Bazaar',                               { 'index': 0x052C }),
                        ('Castle Town Bazaar -> Castle Town',                               { 'index': 0x03B8, 'dynamic_address': 0xBEFD74 })),
    ('Interior',        ('Castle Town -> Castle Town Shooting Gallery',                     { 'index': 0x016D }),
                        ('Castle Town Shooting Gallery -> Castle Town',                     { 'index': 0x01CD, 'dynamic_address': 0xBEFD7C })),
    ('Interior',        ('Kakariko Village -> Kakariko Bazaar',                             { 'index': 0x00B7 }),
                        ('Kakariko Bazaar -> Kakariko Village',                             { 'index': 0x0201, 'dynamic_address': 0xBEFD72 })),
    ('Interior',        ('Kakariko Village -> Kakariko Shooting Gallery',                   { 'index': 0x003B }),
                        ('Kakariko Shooting Gallery -> Kakariko Village',                   { 'index': 0x0463, 'dynamic_address': 0xBEFD7A })),
    ('Interior',        ('Desert Colossus -> Colossus Fairy',                               { 'index': 0x0588 }),
                        ('Colossus Fairy -> Desert Colossus',                               { 'index': 0x057C, 'dynamic_address': 0xBEFD82 })),
    ('Interior',        ('Hyrule Castle Grounds -> Hyrule Castle Fairy',                    { 'index': 0x0578 }),
                        ('Hyrule Castle Fairy -> Castle Grounds',                           { 'index': 0x0340, 'dynamic_address': 0xBEFD80 })),
    ('Interior',        ('Ganons Castle Grounds -> Ganons Castle Fairy',                    { 'index': 0x04C2 }),
                        ('Ganons Castle Fairy -> Castle Grounds',                           { 'index': 0x0340, 'dynamic_address': 0xBEFD6C })),
    ('Interior',        ('Death Mountain Crater Lower -> Crater Fairy',                     { 'index': 0x04BE }),
                        ('Crater Fairy -> Death Mountain Crater Lower',                     { 'index': 0x0482, 'dynamic_address': 0xBEFD6A })),
    ('Interior',        ('Death Mountain Summit -> Mountain Summit Fairy',                  { 'index': 0x0315 }),
                        ('Mountain Summit Fairy -> Death Mountain Summit',                  { 'index': 0x045B, 'dynamic_address': 0xBEFD68 })),
    ('Interior',        ('Zoras Fountain -> Zoras Fountain Fairy',                          { 'index': 0x0371 }),
                        ('Zoras Fountain Fairy -> Zoras Fountain',                          { 'index': 0x0394, 'dynamic_address': 0xBEFD7E })),

    ('SpecialInterior', ('Kokiri Forest -> Links House',                                    { 'index': 0x0272 }),
                        ('Links House -> Kokiri Forest',                                    { 'index': 0x0211 })),
    ('SpecialInterior', ('Temple of Time Exterior -> Temple of Time',                       { 'index': 0x0053 }),
                        ('Temple of Time -> Temple of Time Exterior',                       { 'index': 0x0472 })),
    ('SpecialInterior', ('Kakariko Village -> Windmill',                                    { 'index': 0x0453 }),
                        ('Windmill -> Kakariko Village',                                    { 'index': 0x0351 })),

    ('Grotto',          ('Desert Colossus -> Desert Colossus Grotto',                       { 'scene': 0x5C, 'grotto_var': 0x00FD })),
    ('Grotto',          ('Lake Hylia -> Lake Hylia Grotto',                                 { 'scene': 0x57, 'grotto_var': 0x00EF })),
    ('Grotto',          ('Zora River -> Zora River Storms Grotto',                          { 'scene': 0x54, 'grotto_var': 0x01EB })),
    ('Grotto',          ('Zora River -> Zora River Plateau Bombable Grotto',                { 'scene': 0x54, 'grotto_var': 0x10E6 })),
    ('Grotto',          ('Zora River -> Zora River Plateau Open Grotto',                    { 'scene': 0x54, 'grotto_var': 0x0029 })),
    ('Grotto',          ('Death Mountain Crater Lower -> DMC Hammer Grotto',                { 'scene': 0x61, 'grotto_var': 0x00F9 })),
    ('Grotto',          ('Death Mountain Crater Upper -> Top of Crater Grotto',             { 'scene': 0x61, 'grotto_var': 0x007A })),
    ('Grotto',          ('Goron City -> Goron City Grotto',                                 { 'scene': 0x62, 'grotto_var': 0x00FB })),
    ('Grotto',          ('Death Mountain -> Mountain Storms Grotto',                        { 'scene': 0x60, 'grotto_var': 0x0157 })),
    ('Grotto',          ('Death Mountain -> Mountain Bombable Grotto',                      { 'scene': 0x60, 'grotto_var': 0x00F8 })),
    ('Grotto',          ('Kakariko Village -> Kakariko Back Grotto',                        { 'scene': 0x52, 'grotto_var': 0x0028 })),
    ('Grotto',          ('Kakariko Village -> Kakariko Bombable Grotto',                    { 'scene': 0x52, 'grotto_var': 0x02E7 })),
    ('Grotto',          ('Hyrule Castle Grounds -> Castle Storms Grotto',                   { 'scene': 0x5F, 'grotto_var': 0x01F6 })),
    ('Grotto',          ('Hyrule Field -> Field North Lon Lon Grotto',                      { 'scene': 0x51, 'grotto_var': 0x02E1 })),
    ('Grotto',          ('Hyrule Field -> Field Kakariko Grotto',                           { 'scene': 0x51, 'grotto_var': 0x02E5 })),
    ('Grotto',          ('Hyrule Field -> Field Far West Castle Town Grotto',               { 'scene': 0x51, 'grotto_var': 0x10FF })),
    ('Grotto',          ('Hyrule Field -> Field West Castle Town Grotto',                   { 'scene': 0x51, 'grotto_var': 0x0000 })),
    ('Grotto',          ('Hyrule Field -> Field Valley Grotto',                             { 'scene': 0x51, 'grotto_var': 0x02E4 })),
    ('Grotto',          ('Hyrule Field -> Field Near Lake Inside Fence Grotto',             { 'scene': 0x51, 'grotto_var': 0x02E6 })),
    ('Grotto',          ('Hyrule Field -> Field Near Lake Outside Fence Grotto',            { 'scene': 0x51, 'grotto_var': 0x0003 })),
    ('Grotto',          ('Hyrule Field -> Remote Southern Grotto',                          { 'scene': 0x51, 'grotto_var': 0x0022 })),
    ('Grotto',          ('Lon Lon Ranch -> Lon Lon Grotto',                                 { 'scene': 0x63, 'grotto_var': 0x00FC })),
    ('Grotto',          ('Sacred Forest Meadow Entryway -> Front of Meadow Grotto',         { 'scene': 0x56, 'grotto_var': 0x02ED })),
    ('Grotto',          ('Sacred Forest Meadow -> Meadow Storms Grotto',                    { 'scene': 0x56, 'grotto_var': 0x01EE })),
    ('Grotto',          ('Sacred Forest Meadow -> Meadow Fairy Grotto',                     { 'scene': 0x56, 'grotto_var': 0x10FF })),
    ('Grotto',          ('Lost Woods Beyond Mido -> Lost Woods Sales Grotto',               { 'scene': 0x5B, 'grotto_var': 0x00F5 })),
    ('Grotto',          ('Lost Woods -> Lost Woods Generic Grotto',                         { 'scene': 0x5B, 'grotto_var': 0x0014 })),
    ('Grotto',          ('Kokiri Forest -> Kokiri Forest Storms Grotto',                    { 'scene': 0x55, 'grotto_var': 0x012C })),
    ('Grotto',          ('Zoras Domain -> Zoras Domain Storms Grotto',                      { 'scene': 0x58, 'grotto_var': 0x11FF })),
    ('Grotto',          ('Gerudo Fortress -> Gerudo Fortress Storms Grotto',                { 'scene': 0x5D, 'grotto_var': 0x11FF })),
    ('Grotto',          ('Gerudo Valley Far Side -> Gerudo Valley Storms Grotto',           { 'scene': 0x5A, 'grotto_var': 0x01F0 })),
    ('Grotto',          ('Gerudo Valley -> Gerudo Valley Octorok Grotto',                   { 'scene': 0x5A, 'grotto_var': 0x00F2 })),
    ('Grotto',          ('Lost Woods Beyond Mido -> Deku Theater',                          { 'scene': 0x5B, 'grotto_var': 0x00F3 })),

    ('Overworld',       ('Kokiri Forest -> Lost Woods Bridge From Forest',                  { 'index': 0x05E0 }),
                        ('Lost Woods Bridge -> Kokiri Forest',                              { 'index': 0x020D })),
    ('Overworld',       ('Kokiri Forest -> Lost Woods',                                     { 'index': 0x011E }),
                        ('Lost Woods Forest Exit -> Kokiri Forest',                         { 'index': 0x0286 })),
    ('Overworld',       ('Lost Woods -> Goron City Woods Warp',                             { 'index': 0x04E2 }),
                        ('Goron City Woods Warp -> Lost Woods',                             { 'index': 0x04D6 })),
    ('Overworld',       ('Lost Woods -> Zora River',                                        { 'index': 0x01DD }),
                        ('Zora River -> Lost Woods',                                        { 'index': 0x04DA })),
    ('Overworld',       ('Lost Woods Beyond Mido -> Sacred Forest Meadow Entryway',         { 'index': 0x00FC }),
                        ('Sacred Forest Meadow Entryway -> Lost Woods Beyond Mido',         { 'index': 0x01A9 })),
    ('Overworld',       ('Lost Woods Bridge -> Hyrule Field',                               { 'index': 0x0185 }),
                        ('Hyrule Field -> Lost Woods Bridge',                               { 'index': 0x04DE })),
    ('Overworld',       ('Hyrule Field -> Lake Hylia',                                      { 'index': 0x0102 }),
                        ('Lake Hylia -> Hyrule Field',                                      { 'index': 0x0189 })),
    ('Overworld',       ('Hyrule Field -> Gerudo Valley',                                   { 'index': 0x0117 }),
                        ('Gerudo Valley -> Hyrule Field',                                   { 'index': 0x018D })),
    ('Overworld',       ('Hyrule Field -> Kakariko Village',                                { 'index': 0x00DB }),
                        ('Kakariko Village -> Hyrule Field',                                { 'index': 0x017D })),
    ('Overworld',       ('Hyrule Field -> Zora River Front',                                { 'index': 0x00EA }),
                        ('Zora River Front -> Hyrule Field',                                { 'index': 0x0181 })),
    ('Overworld',       ('Hyrule Field -> Lon Lon Ranch',                                   { 'index': 0x0157 }),
                        ('Lon Lon Ranch -> Hyrule Field',                                   { 'index': 0x01F9 })),
    ('Overworld',       ('Lake Hylia -> Zoras Domain',                                      { 'index': 0x0328 }),
                        ('Zoras Domain -> Lake Hylia',                                      { 'index': 0x0560 })),
    ('Overworld',       ('Gerudo Valley Far Side -> Gerudo Fortress',                       { 'index': 0x0129 }),
                        ('Gerudo Fortress -> Gerudo Valley Far Side',                       { 'index': 0x022D })),
    ('Overworld',       ('Gerudo Fortress Outside Gate -> Haunted Wasteland Near Fortress', { 'index': 0x0130 }),
                        ('Haunted Wasteland Near Fortress -> Gerudo Fortress Outside Gate', { 'index': 0x03AC })),
    ('Overworld',       ('Haunted Wasteland Near Colossus -> Desert Colossus',              { 'index': 0x0123 }),
                        ('Desert Colossus -> Haunted Wasteland Near Colossus',              { 'index': 0x0365 })),
    ('Overworld',       ('Castle Town Entrance -> Castle Town',                             { 'index': 0x00B1 }),
                        ('Castle Town -> Castle Town Entrance',                             { 'index': 0x0033 })),
    ('Overworld',       ('Castle Town -> Castle Grounds',                                   { 'index': 0x0138 }),
                        ('Castle Grounds -> Castle Town',                                   { 'index': 0x025A })),
    ('Overworld',       ('Castle Town -> Temple of Time Exterior',                          { 'index': 0x0171 }),
                        ('Temple of Time Exterior -> Castle Town',                          { 'index': 0x025E })),
    ('Overworld',       ('Kakariko Village -> Graveyard',                                   { 'index': 0x00E4 }),
                        ('Graveyard -> Kakariko Village',                                   { 'index': 0x0195 })),
    ('Overworld',       ('Kakariko Village Behind Gate -> Death Mountain',                  { 'index': 0x013D }),
                        ('Death Mountain -> Kakariko Village Behind Gate',                  { 'index': 0x0191 })),
    ('Overworld',       ('Death Mountain -> Goron City',                                    { 'index': 0x014D }),
                        ('Goron City -> Death Mountain',                                    { 'index': 0x01B9 })),
    ('Overworld',       ('Darunias Chamber -> Death Mountain Crater Lower',                 { 'index': 0x0246 }),
                        ('Death Mountain Crater Lower -> Darunias Chamber',                 { 'index': 0x01C1 })),
    ('Overworld',       ('Death Mountain Summit -> Death Mountain Crater Upper',            { 'index': 0x0147 }),
                        ('Death Mountain Crater Upper -> Death Mountain Summit',            { 'index': 0x01BD })),
    ('Overworld',       ('Zora River Behind Waterfall -> Zoras Domain',                     { 'index': 0x0108 }),
                        ('Zoras Domain -> Zora River Behind Waterfall',                     { 'index': 0x019D })),
    ('Overworld',       ('Zoras Domain Behind King Zora -> Zoras Fountain',                 { 'index': 0x0225 }),
                        ('Zoras Fountain -> Zoras Domain Behind King Zora',                 { 'index': 0x01A1 })),

    ('OwlDrop',         ('Lake Hylia Owl Flight -> Hyrule Field',                           { 'index': 0x027E })),
    ('OwlDrop',         ('Death Mountain Summit Owl Flight -> Kakariko Village',            { 'index': 0x0554 })),
]


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

