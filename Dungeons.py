import random

from BaseClasses import Dungeon
from Items import ItemFactory


def create_dungeons(world):
    def make_dungeon(name, dungeon_regions, boss_key, small_keys, dungeon_items):
        dungeon = Dungeon(name, dungeon_regions, boss_key, small_keys, dungeon_items)
        for region in dungeon.regions:
            world.get_region(region).dungeon = dungeon
        return dungeon

    if world.dungeon_mq['DT']:
        DT = make_dungeon(
            'Deku Tree', 
            ['Deku Tree Lobby', 'Deku Tree Compass Room', 'Deku Tree Boss Room'], 
            None, [],
            ItemFactory(['Map (Deku Tree)', 'Compass (Deku Tree)']))
    else:
        DT = make_dungeon(
            'Deku Tree', 
            ['Deku Tree Lobby', 'Deku Tree Slingshot Room', 'Deku Tree Boss Room'], 
            None, [],
            ItemFactory(['Map (Deku Tree)', 'Compass (Deku Tree)']))

    if world.dungeon_mq['DC']:
        DC = make_dungeon(
            'Dodongos Cavern', 
            ['Dodongos Cavern Beginning', 'Dodongos Cavern Lobby', 'Dodongos Cavern Boss Area'], 
            None, [], 
            ItemFactory(['Map (Dodongos Cavern)', 'Compass (Dodongos Cavern)']))
    else:
        DC = make_dungeon(
            'Dodongos Cavern', 
            ['Dodongos Cavern Beginning', 'Dodongos Cavern Lobby', 'Dodongos Cavern Climb', 'Dodongos Cavern Far Bridge', 
             'Dodongos Cavern Boss Area'], 
            None, [], 
            ItemFactory(['Map (Dodongos Cavern)', 'Compass (Dodongos Cavern)']))

    JB = make_dungeon(
        'Jabu Jabus Belly', 
        ['Jabu Jabus Belly Beginning', 'Jabu Jabus Belly Main', 'Jabu Jabus Belly Depths', 'Jabu Jabus Belly Boss Area'], 
        None, [], 
        ItemFactory(['Map (Jabu Jabus Belly)', 'Compass (Jabu Jabus Belly)']))

    FoT = make_dungeon(
        'Forest Temple', 
        ['Forest Temple Lobby', 'Forest Temple NW Outdoors', 'Forest Temple NE Outdoors', 'Forest Temple Falling Room', 
         'Forest Temple Block Push Room', 'Forest Temple Straightened Hall', 'Forest Temple Outside Upper Ledge', 
         'Forest Temple Bow Region', 'Forest Temple Boss Region'], 
        ItemFactory('Boss Key (Forest Temple)'), 
        ItemFactory(['Small Key (Forest Temple)'] * 5), 
        ItemFactory(['Map (Forest Temple)', 'Compass (Forest Temple)']))

    BW = make_dungeon(
        'Bottom of the Well', 
        ['Bottom of the Well'], 
        None, 
        ItemFactory(['Small Key (Bottom of the Well)'] * 3), 
        ItemFactory(['Map (Bottom of the Well)', 'Compass (Bottom of the Well)']))
    FiT = make_dungeon(
        'Fire Temple', 
        ['Fire Temple Lower', 'Fire Temple Middle', 'Fire Temple Upper'], 
        ItemFactory('Boss Key (Fire Temple)'), 
        ItemFactory(['Small Key (Fire Temple)'] * 8), 
        ItemFactory(['Map (Fire Temple)', 'Compass (Fire Temple)']))

    IC = make_dungeon(
        'Ice Cavern', 
        ['Ice Cavern'], 
        None, [], 
        ItemFactory(['Map (Ice Cavern)', 'Compass (Ice Cavern)']))

    WT = make_dungeon(
        'Water Temple', 
        ['Water Temple Lobby', 'Water Temple Middle Water Level', 'Water Temple Dark Link Region'], 
        ItemFactory('Boss Key (Water Temple)'), 
        ItemFactory(['Small Key (Water Temple)'] * 6), 
        ItemFactory(['Map (Water Temple)', 'Compass (Water Temple)']))

    ShT = make_dungeon(
        'Shadow Temple', 
        ['Shadow Temple Beginning', 'Shadow Temple First Beamos', 'Shadow Temple Huge Pit', 'Shadow Temple Wind Tunnel', 
         'Shadow Temple Beyond Boat'], 
        ItemFactory('Boss Key (Shadow Temple)'), 
        ItemFactory(['Small Key (Shadow Temple)'] * 5), 
        ItemFactory(['Map (Shadow Temple)', 'Compass (Shadow Temple)']))

    GTG = make_dungeon(
        'Gerudo Training Grounds', 
        ['Gerudo Training Grounds Lobby', 'Gerudo Training Grounds Central Maze', 
         'Gerudo Training Grounds Central Maze Right', 'Gerudo Training Grounds Lava Room', 
         'Gerudo Training Grounds Hammer Room', 'Gerudo Training Grounds Eye Statue Lower', 
         'Gerudo Training Grounds Eye Statue Upper', 'Gerudo Training Grounds Heavy Block Room'], 
        None, 
        ItemFactory(['Small Key (Gerudo Training Grounds)'] * 9), 
        [])

    SpT = make_dungeon(
        'Spirit Temple', 
        ['Spirit Temple Lobby', 'Child Spirit Temple', 'Child Spirit Temple Climb', 'Early Adult Spirit Temple',
         'Spirit Temple Central Chamber', 'Spirit Temple Beyond Central Locked Door', 'Spirit Temple Beyond Final Locked Door'], 
        ItemFactory('Boss Key (Spirit Temple)'),
        ItemFactory(['Small Key (Spirit Temple)'] * 5), 
        ItemFactory(['Map (Spirit Temple)', 'Compass (Spirit Temple)']))

    GC = make_dungeon(
        'Ganons Castle', 
        ['Ganons Castle Lobby', 'Ganons Castle Forest Trial', 'Ganons Castle Fire Trial', 'Ganons Castle Water Trial', 
         'Ganons Castle Shadow Trial', 'Ganons Castle Spirit Trial', 'Ganons Castle Light Trial', 'Ganons Castle Tower'], 
        ItemFactory('Boss Key (Ganons Castle)'), 
        ItemFactory(['Small Key (Ganons Castle)'] * 2), 
        [])

    world.dungeons = [DT, DC, JB, FoT, BW, FiT, IC, WT, ShT, GTG, SpT, GC]
