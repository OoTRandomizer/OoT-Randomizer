import random
import logging
from Fill import ShuffleError
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
            if entrance.type in ('Dungeon', 'Interior', 'Grotto', 'Grave', 'SpecialGrave'):
                # Dungeon, Grotto/Grave and Simple Interior exits shouldn't be assumed to be able to give access to their parent region
                assumed_return.set_rule(lambda state: False)
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
    ('Dungeon',         ('Fire Temple Entrance -> Fire Temple Lower',                       { 'index': 0x0165 }),
                        ('Fire Temple Lower -> Fire Temple Entrance',                       { 'index': 0x024A, 'blue_warp': 0x0564 })),
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
    ('Interior',        ('Kakariko Village Backyard -> Odd Medicine Building',              { 'index': 0x0072 }),
                        ('Odd Medicine Building -> Kakariko Village Backyard',              { 'index': 0x034D })),
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
    ('Interior',        ('Death Mountain Crater Lower Nearby -> Crater Fairy',              { 'index': 0x04BE }),
                        ('Crater Fairy -> Death Mountain Crater Lower Local',               { 'index': 0x0482, 'dynamic_address': 0xBEFD6A })),
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
    ('SpecialInterior', ('Kakariko Village -> Kakariko Potion Shop Front',                  { 'index': 0x0384 }),
                        ('Kakariko Potion Shop Front -> Kakariko Village',                  { 'index': 0x044B })),
    ('SpecialInterior', ('Kakariko Village Backyard -> Kakariko Potion Shop Back',          { 'index': 0x03EC }),
                        ('Kakariko Potion Shop Back -> Kakariko Village Backyard',          { 'index': 0x04FF })),

    ('Grotto',          ('Desert Colossus -> Desert Colossus Grotto',                       { 'grotto_id': 0x00, 'entrance': 0x05BC, 'content': 0xFD, 'scene': 0x5C }),
                        ('Desert Colossus Grotto -> Desert Colossus',                       { 'grotto_id': 0x00 })),
    ('Grotto',          ('Lake Hylia -> Lake Hylia Grotto',                                 { 'grotto_id': 0x01, 'entrance': 0x05A4, 'content': 0xEF, 'scene': 0x57 }),
                        ('Lake Hylia Grotto -> Lake Hylia',                                 { 'grotto_id': 0x01 })),
    ('Grotto',          ('Zora River -> Zora River Storms Grotto',                          { 'grotto_id': 0x02, 'entrance': 0x05BC, 'content': 0xEB, 'scene': 0x54 }),
                        ('Zora River Storms Grotto -> Zora River',                          { 'grotto_id': 0x02 })),
    ('Grotto',          ('Zora River -> Zora River Plateau Bombable Grotto',                { 'grotto_id': 0x03, 'entrance': 0x036D, 'content': 0xE6, 'scene': 0x54 }),
                        ('Zora River Plateau Bombable Grotto -> Zora River',                { 'grotto_id': 0x03 })),
    ('Grotto',          ('Zora River -> Zora River Plateau Open Grotto',                    { 'grotto_id': 0x04, 'entrance': 0x003F, 'content': 0x29, 'scene': 0x54 }),
                        ('Zora River Plateau Open Grotto -> Zora River',                    { 'grotto_id': 0x04 })),
    ('Grotto',          ('Death Mountain Crater Lower Nearby -> DMC Hammer Grotto',         { 'grotto_id': 0x05, 'entrance': 0x05A4, 'content': 0xF9, 'scene': 0x61 }),
                        ('DMC Hammer Grotto -> Death Mountain Crater Lower Local',          { 'grotto_id': 0x05 })),
    ('Grotto',          ('Death Mountain Crater Upper Nearby -> Top of Crater Grotto',      { 'grotto_id': 0x06, 'entrance': 0x003F, 'content': 0x7A, 'scene': 0x61 }),
                        ('Top of Crater Grotto -> Death Mountain Crater Upper Local',       { 'grotto_id': 0x06 })),
    ('Grotto',          ('Goron City -> Goron City Grotto',                                 { 'grotto_id': 0x07, 'entrance': 0x05A4, 'content': 0xFB, 'scene': 0x62 }),
                        ('Goron City Grotto -> Goron City',                                 { 'grotto_id': 0x07 })),
    ('Grotto',          ('Death Mountain -> Mountain Storms Grotto',                        { 'grotto_id': 0x08, 'entrance': 0x003F, 'content': 0x57, 'scene': 0x60 }),
                        ('Mountain Storms Grotto -> Death Mountain',                        { 'grotto_id': 0x08 })),
    ('Grotto',          ('Death Mountain Summit -> Mountain Bombable Grotto',               { 'grotto_id': 0x09, 'entrance': 0x05FC, 'content': 0xF8, 'scene': 0x60 }),
                        ('Mountain Bombable Grotto -> Death Mountain Summit',               { 'grotto_id': 0x09 })),
    ('Grotto',          ('Kakariko Village Backyard -> Kakariko Back Grotto',               { 'grotto_id': 0x0A, 'entrance': 0x003F, 'content': 0x28, 'scene': 0x52 }),
                        ('Kakariko Back Grotto -> Kakariko Village Backyard',               { 'grotto_id': 0x0A })),
    ('Grotto',          ('Kakariko Village -> Kakariko Bombable Grotto',                    { 'grotto_id': 0x0B, 'entrance': 0x05A0, 'content': 0xE7, 'scene': 0x52 }),
                        ('Kakariko Bombable Grotto -> Kakariko Village',                    { 'grotto_id': 0x0B })),
    ('Grotto',          ('Hyrule Castle Grounds -> Castle Storms Grotto',                   { 'grotto_id': 0x0C, 'entrance': 0x05B8, 'content': 0xF6, 'scene': 0x5F }),
                        ('Castle Storms Grotto -> Hyrule Castle Grounds',                   { 'grotto_id': 0x0C })),
    ('Grotto',          ('Hyrule Field -> Field North Lon Lon Grotto',                      { 'grotto_id': 0x0D, 'entrance': 0x05C0, 'content': 0xE1, 'scene': 0x51 }),
                        ('Field North Lon Lon Grotto -> Hyrule Field',                      { 'grotto_id': 0x0D })),
    ('Grotto',          ('Hyrule Field -> Field Kakariko Grotto',                           { 'grotto_id': 0x0E, 'entrance': 0x0598, 'content': 0xE5, 'scene': 0x51 }),
                        ('Field Kakariko Grotto -> Hyrule Field',                           { 'grotto_id': 0x0E })),
    ('Grotto',          ('Hyrule Field -> Field Far West Castle Town Grotto',               { 'grotto_id': 0x0F, 'entrance': 0x036D, 'content': 0xFF, 'scene': 0x51 }),
                        ('Field Far West Castle Town Grotto -> Hyrule Field',               { 'grotto_id': 0x0F })),
    ('Grotto',          ('Hyrule Field -> Field West Castle Town Grotto',                   { 'grotto_id': 0x10, 'entrance': 0x003F, 'content': 0x00, 'scene': 0x51 }),
                        ('Field West Castle Town Grotto -> Hyrule Field',                   { 'grotto_id': 0x10 })),
    ('Grotto',          ('Hyrule Field -> Field Valley Grotto',                             { 'grotto_id': 0x11, 'entrance': 0x05A8, 'content': 0xE4, 'scene': 0x51 }),
                        ('Field Valley Grotto -> Hyrule Field',                             { 'grotto_id': 0x11 })),
    ('Grotto',          ('Hyrule Field -> Field Near Lake Inside Fence Grotto',             { 'grotto_id': 0x12, 'entrance': 0x059C, 'content': 0xE6, 'scene': 0x51 }),
                        ('Field Near Lake Inside Fence Grotto -> Hyrule Field',             { 'grotto_id': 0x12 })),
    ('Grotto',          ('Hyrule Field -> Field Near Lake Outside Fence Grotto',            { 'grotto_id': 0x13, 'entrance': 0x003F, 'content': 0x03, 'scene': 0x51 }),
                        ('Field Near Lake Outside Fence Grotto -> Hyrule Field',            { 'grotto_id': 0x13 })),
    ('Grotto',          ('Hyrule Field -> Remote Southern Grotto',                          { 'grotto_id': 0x14, 'entrance': 0x003F, 'content': 0x22, 'scene': 0x51 }),
                        ('Remote Southern Grotto -> Hyrule Field',                          { 'grotto_id': 0x14 })),
    ('Grotto',          ('Lon Lon Ranch -> Lon Lon Grotto',                                 { 'grotto_id': 0x15, 'entrance': 0x05A4, 'content': 0xFC, 'scene': 0x63 }),
                        ('Lon Lon Grotto -> Lon Lon Ranch',                                 { 'grotto_id': 0x15 })),
    ('Grotto',          ('Sacred Forest Meadow Entryway -> Front of Meadow Grotto',         { 'grotto_id': 0x16, 'entrance': 0x05B4, 'content': 0xED, 'scene': 0x56 }),
                        ('Front of Meadow Grotto -> Sacred Forest Meadow Entryway',         { 'grotto_id': 0x16 })),
    ('Grotto',          ('Sacred Forest Meadow -> Meadow Storms Grotto',                    { 'grotto_id': 0x17, 'entrance': 0x05BC, 'content': 0xEE, 'scene': 0x56 }),
                        ('Meadow Storms Grotto -> Sacred Forest Meadow',                    { 'grotto_id': 0x17 })),
    ('Grotto',          ('Sacred Forest Meadow -> Meadow Fairy Grotto',                     { 'grotto_id': 0x18, 'entrance': 0x036D, 'content': 0xFF, 'scene': 0x56 }),
                        ('Meadow Fairy Grotto -> Sacred Forest Meadow',                     { 'grotto_id': 0x18 })),
    ('Grotto',          ('Lost Woods Beyond Mido -> Lost Woods Sales Grotto',               { 'grotto_id': 0x19, 'entrance': 0x05B0, 'content': 0xF5, 'scene': 0x5B }),
                        ('Lost Woods Sales Grotto -> Lost Woods Beyond Mido',               { 'grotto_id': 0x19 })),
    ('Grotto',          ('Lost Woods -> Lost Woods Generic Grotto',                         { 'grotto_id': 0x1A, 'entrance': 0x003F, 'content': 0x14, 'scene': 0x5B }),
                        ('Lost Woods Generic Grotto -> Lost Woods',                         { 'grotto_id': 0x1A })),
    ('Grotto',          ('Kokiri Forest -> Kokiri Forest Storms Grotto',                    { 'grotto_id': 0x1B, 'entrance': 0x003F, 'content': 0x2C, 'scene': 0x55 }),
                        ('Kokiri Forest Storms Grotto -> Kokiri Forest',                    { 'grotto_id': 0x1B })),
    ('Grotto',          ('Zoras Domain -> Zoras Domain Storms Grotto',                      { 'grotto_id': 0x1C, 'entrance': 0x036D, 'content': 0xFF, 'scene': 0x58 }),
                        ('Zoras Domain Storms Grotto -> Zoras Domain',                      { 'grotto_id': 0x1C })),
    ('Grotto',          ('Gerudo Fortress -> Gerudo Fortress Storms Grotto',                { 'grotto_id': 0x1D, 'entrance': 0x036D, 'content': 0xFF, 'scene': 0x5D }),
                        ('Gerudo Fortress Storms Grotto -> Gerudo Fortress',                { 'grotto_id': 0x1D })),
    ('Grotto',          ('Gerudo Valley Far Side -> Gerudo Valley Storms Grotto',           { 'grotto_id': 0x1E, 'entrance': 0x05BC, 'content': 0xF0, 'scene': 0x5A }),
                        ('Gerudo Valley Storms Grotto -> Gerudo Valley Far Side',           { 'grotto_id': 0x1E })),
    ('Grotto',          ('Gerudo Valley -> Gerudo Valley Octorok Grotto',                   { 'grotto_id': 0x1F, 'entrance': 0x05AC, 'content': 0xF2, 'scene': 0x5A }),
                        ('Gerudo Valley Octorok Grotto -> Gerudo Valley',                   { 'grotto_id': 0x1F })),
    ('Grotto',          ('Lost Woods Beyond Mido -> Deku Theater',                          { 'grotto_id': 0x20, 'entrance': 0x05C4, 'content': 0xF3, 'scene': 0x5B }),
                        ('Deku Theater -> Lost Woods Beyond Mido',                          { 'grotto_id': 0x20 })),

    ('Grave',           ('Graveyard -> Shield Grave',                                       { 'index': 0x004B }),
                        ('Shield Grave -> Graveyard',                                       { 'index': 0x035D })),
    ('Grave',           ('Graveyard -> Heart Piece Grave',                                  { 'index': 0x031C }),
                        ('Heart Piece Grave -> Graveyard',                                  { 'index': 0x0361 })),
    ('Grave',           ('Graveyard -> Composer Grave',                                     { 'index': 0x002D }),
                        ('Composer Grave -> Graveyard',                                     { 'index': 0x050B })),

    ('SpecialGrave',    ('Graveyard -> Dampes Grave',                                       { 'index': 0x044F }),
                        ('Dampes Grave -> Graveyard',                                       { 'index': 0x0359 })),

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
    ('Overworld',       ('Hyrule Field -> Castle Town Entrance',                            { 'index': 0x0276 }),
                        ('Castle Town Entrance -> Hyrule Field',                            { 'index': 0x01FD })),
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
    ('Overworld',       ('Darunias Chamber -> Death Mountain Crater Lower Local',           { 'index': 0x0246 }),
                        ('Death Mountain Crater Lower Nearby -> Darunias Chamber',          { 'index': 0x01C1 })),
    ('Overworld',       ('Death Mountain Summit -> Death Mountain Crater Upper Local',      { 'index': 0x0147 }),
                        ('Death Mountain Crater Upper Nearby -> Death Mountain Summit',     { 'index': 0x01BD })),
    ('Overworld',       ('Zora River Behind Waterfall -> Zoras Domain',                     { 'index': 0x0108 }),
                        ('Zoras Domain -> Zora River Behind Waterfall',                     { 'index': 0x019D })),
    ('Overworld',       ('Zoras Domain Behind King Zora -> Zoras Fountain',                 { 'index': 0x0225 }),
                        ('Zoras Fountain -> Zoras Domain Behind King Zora',                 { 'index': 0x01A1 })),

    ('OwlDrop',         ('Lake Hylia Owl Flight -> Hyrule Field',                           { 'index': 0x027E, 'code_address': 0xAC9F26 })),
    ('OwlDrop',         ('Death Mountain Summit Owl Flight -> Kakariko Village',            { 'index': 0x0554, 'code_address': 0xAC9EF2 })),
]


class EntranceShuffleError(ShuffleError):
    pass


# Set entrances of all worlds, first initializing them to their default regions, then potentially shuffling part of them
def set_entrances(worlds):
    for world in worlds:
        world.initialize_entrances()

    if worlds[0].entrance_shuffle != 'off':
        shuffle_random_entrances(worlds)

    set_entrances_based_rules(worlds)


# Shuffles entrances that need to be shuffled in all worlds
def shuffle_random_entrances(worlds):

    # Store all locations reachable before shuffling to differentiate which locations were already unreachable from those we made unreachable
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]
    max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)

    non_drop_locations = [location for world in worlds for location in world.get_locations() if location.type not in ('Drop', 'Event')]
    max_playthrough.visit_locations(non_drop_locations)
    locations_to_ensure_reachable = list(filter(max_playthrough.visited, non_drop_locations))

    # Shuffle all entrances within their own worlds
    for world in worlds:

        # Determine entrance pools based on settings, to be shuffled in the order we set them by
        entrance_pools = OrderedDict()

        if worlds[0].shuffle_special_indoor_entrances:
            entrance_pools['SpecialInterior'] = entrance_instances(world, get_entrance_pool('SpecialInterior'))

        if worlds[0].shuffle_overworld_entrances:
            entrance_pools['Overworld'] = entrance_instances(world, get_entrance_pool('Overworld'))
            # Overworld entrances should be shuffled from both directions, unlike other types of entrances
            for entrance in entrance_pools['Overworld'].copy():
                entrance.reverse.primary = True
                entrance_pools['Overworld'].append(entrance.reverse)
            entrance_pools['OwlDrop'] = entrance_instances(world, get_entrance_pool('OwlDrop'))

        if worlds[0].shuffle_dungeon_entrances:
            entrance_pools['Dungeon'] = entrance_instances(world, get_entrance_pool('Dungeon'))
            # The fill algorithm will already make sure gohma is reachable, however it can end up putting
            # a forest escape via the hands of spirit on Deku leading to Deku on spirit in logic. This is
            # not really a closed forest anymore, so specifically remove Deku Tree from closed forest.
            if worlds[0].open_forest == 'closed':
                entrance_pools['Dungeon'].remove(world.get_entrance('Outside Deku Tree -> Deku Tree Lobby'))
                world.get_entrance('Outside Deku Tree -> Deku Tree Lobby').shuffled = False
                world.get_entrance('Deku Tree Lobby -> Outside Deku Tree').shuffled = False

        if worlds[0].shuffle_interior_entrances:
            entrance_pools['Interior'] = entrance_instances(world, get_entrance_pool('Interior')) + entrance_pools.get('SpecialInterior', [])

        if worlds[0].shuffle_grotto_entrances:
            entrance_pools['GrottoGrave'] = entrance_instances(world, get_entrance_pool('Grotto') + get_entrance_pool('Grave'))
            if worlds[0].shuffle_special_indoor_entrances:
                entrance_pools['GrottoGrave'] += entrance_instances(world, get_entrance_pool('SpecialGrave'))

        # Set the assumption that all entrances are reachable
        target_entrance_pools = {}
        for pool_type, entrance_pool in entrance_pools.items():
            target_entrance_pools[pool_type] = assume_pool_reachable(world, entrance_pool)

        # Special interiors need to be handled specifically by placing them in reverse and among all interiors, including normal ones
        if 'SpecialInterior' in entrance_pools:
            entrance_pools['SpecialInterior'] = [entrance.reverse for entrance in entrance_pools['SpecialInterior']]
            target_entrance_pools['SpecialInterior'] = [entrance.reverse for entrance in target_entrance_pools['Interior']]

        # Owl Drops are extra entrances that will be connected to an owl drop or will be a duplicate entrance to an overworld entrance
        # We don't assume they are reachable until placing them because we don't want the placement algorithm to expect all overworld regions to be reachable
        if 'OwlDrop' in entrance_pools:
            duplicate_overworld_targets = [target.copy(target.parent_region) for target in target_entrance_pools['Overworld']]
            for target in duplicate_overworld_targets:
                target.connect(world.get_region(target.connected_region))
                target.parent_region.exits.append(target)
            target_entrance_pools['OwlDrop'] += duplicate_overworld_targets
            for target in target_entrance_pools['OwlDrop']:
                target.set_rule(lambda state: False)

        # Set entrances defined in the distribution
        world.distribution.set_shuffled_entrances(worlds, entrance_pools, target_entrance_pools, locations_to_ensure_reachable, complete_itempool)

        # Shuffle all entrances among the pools to shuffle
        for pool_type, entrance_pool in entrance_pools.items():
            if pool_type == 'SpecialInterior':
                # When placing special interiors, we pre place ToT and Links House first, making sure the assumed access rules are always valid
                temple_of_time_exit = world.get_entrance('Temple of Time -> Temple of Time Exterior')
                links_house_exit = world.get_entrance('Links House -> Kokiri Forest')
                for target in target_entrance_pools[pool_type]:
                    target.set_rule(lambda state: temple_of_time_exit.connected_region == None or (links_house_exit.connected_region == None and state.is_child()))
                shuffle_entrance_pool(worlds, [temple_of_time_exit], target_entrance_pools[pool_type], locations_to_ensure_reachable)
                shuffle_entrance_pool(worlds, [links_house_exit], target_entrance_pools[pool_type], locations_to_ensure_reachable)

            shuffle_entrance_pool(worlds, entrance_pool, target_entrance_pools[pool_type], locations_to_ensure_reachable)

            if pool_type == 'OwlDrop':
                # Delete all unused owl drop targets after placing the entrances, since the unused targets won't ever be replaced
                for target in target_entrance_pools[pool_type]:
                    delete_target_entrance(target)

    # Multiple checks after shuffling entrances to make sure everything went fine
    max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)

    # Check that all shuffled entrances are properly connected to a region
    for world in worlds:
        for entrance in world.get_shuffled_entrances():
            if entrance.connected_region == None:
                logging.getLogger('').error('%s was shuffled but still isn\'t connected to any region [World %d]', entrance, world.id)

    # Check for game beatability in all worlds
    if not max_playthrough.can_beat_game(False):
        raise EntranceShuffleError('Cannot beat game!')

    # Validate the worlds one last time to ensure all special conditions are still valid
    try:
        validate_worlds(worlds, None, locations_to_ensure_reachable, complete_itempool)
    except EntranceShuffleError as error:
        raise EntranceShuffleError('Worlds are not valid after shuffling entrances, Reason: %s' % error)


# Shuffle all entrances within a provided pool
def shuffle_entrance_pool(worlds, entrance_pool, target_entrances, locations_to_ensure_reachable, retry_count=20):

    # Split entrances between those that have requirements (restrictive) and those that do not (soft). These are primarily age or time of day requirements.
    restrictive_entrances, soft_entrances = split_entrances_by_requirements(worlds, entrance_pool, target_entrances)

    while retry_count:
        retry_count -= 1
        rollbacks = []

        try:
            # Shuffle restrictive entrances first while more regions are available in order to heavily reduce the chances of the placement failing.
            shuffle_entrances(worlds, restrictive_entrances, target_entrances, rollbacks, locations_to_ensure_reachable)

            # Shuffle the rest of the entrances, we don't have to check for beatability or reachability of locations when placing those
            shuffle_entrances(worlds, soft_entrances, target_entrances, rollbacks)

            # Fully validate the resulting worlds to ensure everything is still fine after shuffling this pool
            complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]
            validate_worlds(worlds, None, locations_to_ensure_reachable, complete_itempool)

            # If all entrances could be connected without issues, log connections and continue
            for entrance, target in rollbacks:
                confirm_replacement(entrance, target)
            return

        except EntranceShuffleError as error:
            for entrance, target in rollbacks:
                restore_connections(entrance, target)
            logging.getLogger('').info('Failed to place all entrances in a pool for world %d. Will retry %d more times', entrance_pool[0].world.id, retry_count)
            logging.getLogger('').info('\t%s' % error)

    raise EntranceShuffleError('Entrance placement attempt count exceeded for world %d' % entrance_pool[0].world.id)


# Split entrances based on their requirements to figure out how each entrance should be handled when shuffling them
def split_entrances_by_requirements(worlds, entrances_to_split, assumed_entrances):

    # First, disconnect all root assumed entrances and save which regions they were originally connected to, so we can reconnect them later
    original_connected_regions = {}
    entrances_to_disconnect = set(assumed_entrances).union(entrance.reverse for entrance in assumed_entrances if entrance.reverse)
    for entrance in entrances_to_disconnect:
        if entrance.connected_region:
            original_connected_regions[entrance] = entrance.disconnect()

    # Generate the states with all assumed entrances disconnected
    # This ensures no assumed entrances corresponding to those we are shuffling are required in order for an entrance to be reachable as some age/tod
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]
    max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)

    restrictive_entrances = []
    soft_entrances = []

    for entrance in entrances_to_split:
        # Here, we find entrances that may be unreachable under certain conditions
        if not max_playthrough.state_list[entrance.world.id].as_both(entrance, tod='all'):
            restrictive_entrances.append(entrance)
            continue
        # If an entrance is reachable as both ages and all times of day with all the other entrances disconnected,
        # then it can always be made accessible in all situations by the Fill algorithm, no matter which combination of entrances we end up with.
        # Thus, those entrances aren't bound to any specific requirements and are very versatile during placement.
        soft_entrances.append(entrance)

    # Reconnect all disconnected entrances afterwards
    for entrance in entrances_to_disconnect:
        if entrance in original_connected_regions:
            entrance.connect(original_connected_regions[entrance])

    return restrictive_entrances, soft_entrances


# Shuffle entrances by placing them instead of entrances in the provided target entrances list
# While shuffling entrances, the algorithm will ensure worlds are still valid based on multiple criterias
def shuffle_entrances(worlds, entrances, target_entrances, rollbacks, locations_to_ensure_reachable=[]):

    # Retrieve all items in the itempool, all worlds included
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]

    random.shuffle(entrances)

    # Place all entrances in the pool, validating worlds during every placement
    for entrance in entrances:
        if entrance.connected_region != None:
            continue
        random.shuffle(target_entrances)

        for target in target_entrances:
            if target.connected_region == None:
                continue

            # An entrance shouldn't be connected to its own scene, so we fail in that situation
            if entrance.parent_region.scene and entrance.parent_region.scene == target.connected_region.scene:
                logging.getLogger('').debug('Failed to connect %s To %s (Reason: Self scene connections are forbidden) [World %d]',
                                            entrance, target.connected_region, entrance.world.id)
                continue

            change_connections(entrance, target)

            try:
                validate_worlds(worlds, entrance, locations_to_ensure_reachable, complete_itempool)
                rollbacks.append((entrance, target))
                break
            except EntranceShuffleError as error:
                # If the entrance can't be placed there, log a debug message and change the connections back to what they were previously
                logging.getLogger('').debug('Failed to connect %s To %s (Reason: %s) [World %d]',
                                            entrance, entrance.connected_region, error, entrance.world.id)
                restore_connections(entrance, target)

        if entrance.connected_region == None:
            raise EntranceShuffleError('No more valid entrances to replace with %s in world %d' % (entrance, entrance.world.id))


# Validate the provided worlds' structures, raising an error if it's not valid based on our criterias
def validate_worlds(worlds, entrance_placed, locations_to_ensure_reachable, itempool):

    max_playthrough = None

    if locations_to_ensure_reachable:
        max_playthrough = Playthrough.max_explore([world.state for world in worlds], itempool)
        # If ALR is enabled, ensure all locations we want to keep reachable are indeed still reachable 
        # Otherwise, just continue if the game is still beatable
        if not (worlds[0].check_beatable_only and max_playthrough.can_beat_game(False)):
            max_playthrough.visit_locations(locations_to_ensure_reachable)
            for location in locations_to_ensure_reachable:
                if not max_playthrough.visited(location):
                    raise EntranceShuffleError('%s is unreachable' % location.name)

    if (entrance_placed == None and worlds[0].shuffle_special_indoor_entrances) or \
       (entrance_placed != None and entrance_placed.type in ['SpecialInterior', 'Overworld']):
        if max_playthrough == None:
            max_playthrough = Playthrough.max_explore([world.state for world in worlds], itempool)

        for world in worlds:
            # Links House entrance should be reachable as child at some point in the seed
            links_house_entrance = get_entrance_replacing(world.get_region('Links House'), 'Kokiri Forest -> Links House')
            if not max_playthrough.state_list[world.id].as_age(links_house_entrance, adult=False):
                raise EntranceShuffleError('Links House Entrance is never reachable as child')

            # Temple of Time entrance should be reachable as both ages at some point in the seed
            temple_of_time_entrance = get_entrance_replacing(world.get_region('Temple of Time'), 'Temple of Time Exterior -> Temple of Time')
            if not max_playthrough.state_list[world.id].as_both(temple_of_time_entrance):
                raise EntranceShuffleError('Temple of Time Entrance is never reachable as both ages')

            # Windmill door entrance should be reachable as both ages at some point in the seed
            windmill_door_entrance = get_entrance_replacing(world.get_region('Windmill'), 'Kakariko Village -> Windmill')
            if not max_playthrough.state_list[world.id].as_both(windmill_door_entrance):
                raise EntranceShuffleError('Windmill Door Entrance is never reachable as both ages')

            # Potion Shop front door should be reachable as both ages at some point in the seed
            potion_front_entrance = get_entrance_replacing(world.get_region('Kakariko Potion Shop Front'), 'Kakariko Village -> Kakariko Potion Shop Front')
            if not max_playthrough.state_list[world.id].as_both(potion_front_entrance):
                raise EntranceShuffleError('Adult Potion Front Entrance is never reachable as both ages')

            # Potion Shop back door should be reachable as adult at some point in the seed
            potion_back_entrance = get_entrance_replacing(world.get_region('Kakariko Potion Shop Back'), 'Kakariko Village Backyard -> Kakariko Potion Shop Back')
            if not max_playthrough.state_list[world.id].as_age(potion_back_entrance, adult=True):
                raise EntranceShuffleError('Adult Potion Back Entrance is never reachable as Adult')

            if  potion_front_entrance.parent_region.hint is not None and \
                potion_back_entrance.parent_region.hint is not None and \
                potion_front_entrance.parent_region.hint != potion_back_entrance.parent_region.hint:
                raise EntranceShuffleError('Adult Potion Shop Entrances not in same hint region')

        # At least one valid starting region with all basic refills should be reachable without using any items at the beginning of the seed
        no_items_playthrough = Playthrough([State(world) for world in worlds])

        valid_starting_regions = ['Kokiri Forest', 'Kakariko Village']
        for world in worlds:
            if not any(region for region in valid_starting_regions if no_items_playthrough.can_reach(world.get_region(region))):
                raise EntranceShuffleError('Invalid starting area')

        # For now, we consider that time of day must always be reachable as both ages without having collected any items (except in closed forest)
        # In ER, Time of day logic normally considers that the player always has access to time passing from the root so this is important to ensure
        # This also means that, in order to test for this, we have to temporarily remove that assumption about root access to time passing
        for world in worlds:
            world.get_region('Root').can_reach = lambda state: state.tod == None
        no_time_passing_playthrough = Playthrough.with_items([world.state for world in worlds], [ItemFactory('Time Travel', world=world) for world in worlds])
        for world in worlds:
            world.get_region('Root').can_reach = lambda state: True

        for world in worlds:
            if not (any(region for region in no_time_passing_playthrough.reachable_regions('child') if region.time_passes and region.world == world) and
                    any(region for region in no_time_passing_playthrough.reachable_regions('adult') if region.time_passes and region.world == world)):
                raise EntranceShuffleError('Time passing is not guaranteed as both ages')

        # When starting as adult, child Link should be able to reach ToT without having collected any items
        # This is important to ensure that the player never loses access to the pedestal after going child
        if any(world.starting_age == 'adult' for world in worlds):
            # We can reuse the playthrough previously generated as this situation is the same except we have root time passing access now
            time_travel_playthrough = no_time_passing_playthrough.copy()

            for world in worlds:
                if world.starting_age == 'adult' and not time_travel_playthrough.can_reach(world.get_region('Temple of Time'), age='child'):
                    raise EntranceShuffleError('Links House to Temple of Time path as child is not guaranteed')

    if entrance_placed == None or (entrance_placed != None and entrance_placed.type in ['Interior', 'SpecialInterior', 'Overworld']):
        # The Big Poe Shop should always be accessible as adult without the need to use any bottles
        # Since we can't guarantee that items in the pool won't be placed behind bottles, we guarantee the access without using any items
        # This is important to ensure that players can never lock their only bottles by filling them with Big Poes they can't sell
        no_items_time_travel_playthrough = Playthrough.with_items([State(world) for world in worlds], [ItemFactory('Time Travel', world=world) for world in worlds])

        for world in worlds:
            if not no_items_time_travel_playthrough.can_reach(world.get_region('Castle Town Rupee Room'), age='adult'):
                raise EntranceShuffleError('Big Poe Shop access is not guaranteed as adult')

    return


# Shorthand function to find an entrance with the requested name leading to a specific region
def get_entrance_replacing(region, entrance_name):
    try:
        return next(filter(lambda entrance: entrance.replaces and entrance.replaces.name == entrance_name, region.entrances))
    except StopIteration:
        return region.world.get_entrance(entrance_name)


# Change connections between an entrance and a target assumed entrance, in order to test the connections afterwards if necessary
def change_connections(entrance, target_entrance):
    entrance.connect(target_entrance.disconnect())
    entrance.replaces = target_entrance.replaces
    if entrance.reverse:
        target_entrance.replaces.reverse.connect(entrance.reverse.assumed.disconnect())
        target_entrance.replaces.reverse.replaces = entrance.reverse.assumed.replaces


# Restore connections between an entrance and a target assumed entrance
def restore_connections(entrance, target_entrance):
    target_entrance.connect(entrance.disconnect())
    entrance.replaces = None
    if entrance.reverse:
        entrance.reverse.assumed.connect(target_entrance.replaces.reverse.disconnect())
        target_entrance.replaces.reverse.replaces = None


# Confirm the replacement of a target entrance by a new entrance, logging the new connections and completely deleting the target entrances
def confirm_replacement(entrance, target_entrance):
    delete_target_entrance(target_entrance)
    logging.getLogger('').debug('Connected %s To %s [World %d]', entrance, entrance.connected_region, entrance.world.id)
    if entrance.reverse:
        replaced_reverse = target_entrance.replaces.reverse
        delete_target_entrance(entrance.reverse.assumed)
        logging.getLogger('').debug('Connected %s To %s [World %d]', replaced_reverse, replaced_reverse.connected_region, replaced_reverse.world.id)


# Delete an assumed target entrance, by disconnecting it if needed and removing it from its parent region
def delete_target_entrance(target_entrance):
    if target_entrance.connected_region != None:
        target_entrance.disconnect()
    if target_entrance.parent_region != None:
        target_entrance.parent_region.exits.remove(target_entrance)
        target_entrance.parent_region = None
