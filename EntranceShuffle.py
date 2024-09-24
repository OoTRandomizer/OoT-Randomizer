from __future__ import annotations
import random
import logging
from collections import OrderedDict
from collections.abc import Iterable, Container
from itertools import chain
from typing import TYPE_CHECKING, Optional

from Fill import ShuffleError
from Search import Search
from Region import Region, TimeOfDay
from Rules import set_entrances_based_rules
from State import State
from Item import ItemFactory
from Hints import HintArea, HintAreaNotFound
from HintList import misc_item_hint_table

if TYPE_CHECKING:
    from Entrance import Entrance
    from Location import Location
    from Item import Item
    from World import World


def set_all_entrances_data(world: World) -> None:
    for type, forward_entry, *return_entry in entrance_shuffle_table:
        forward_entrance = world.get_entrance(forward_entry[0])
        forward_entrance.data = forward_entry[1]
        forward_entrance.type = type
        forward_entrance.primary = True
        if type == 'Grotto':
            forward_entrance.data['index'] = 0x1000 + forward_entrance.data['grotto_id']
        if return_entry:
            return_entry = return_entry[0]
            return_entrance = world.get_entrance(return_entry[0])
            return_entrance.data = return_entry[1]
            return_entrance.type = type
            forward_entrance.bind_two_way(return_entrance)
            if type == 'Grotto':
                return_entrance.data['index'] = 0x7FFF


def assume_entrance_pool(entrance_pool: list[Entrance]) -> list[Entrance]:
    assumed_pool = []
    for entrance in entrance_pool:
        assumed_forward = entrance.assume_reachable()
        if entrance.reverse is not None:
            assumed_return = entrance.reverse.assume_reachable()
            if (entrance.type in ('Dungeon', 'Grotto', 'Grave') and entrance.reverse.name != 'Spirit Temple Lobby -> Desert Colossus From Spirit Lobby') or \
               (entrance.type == 'Interior' and entrance.world and entrance.world.shuffle_special_interior_entrances):
                # In most cases, Dungeon, Grotto/Grave and Simple Interior exits shouldn't be assumed able to give access to their parent region
                assumed_return.set_rule(lambda state, **kwargs: False)
            assumed_forward.bind_two_way(assumed_return)
        assumed_pool.append(assumed_forward)
    return assumed_pool


def build_one_way_targets(world: World, types_to_include: Iterable[str], exclude: Container[str] = (), target_region_names: Container[str] = ()) -> list[Entrance]:
    one_way_entrances: list[Entrance] = []
    for pool_type in types_to_include:
        one_way_entrances += world.get_shufflable_entrances(type=pool_type)
    valid_one_way_entrances = list(filter(lambda entrance: entrance.name not in exclude, one_way_entrances))
    if target_region_names:
        return [entrance.get_new_target() for entrance in valid_one_way_entrances
                if entrance.connected_region.name in target_region_names]
    return [entrance.get_new_target() for entrance in valid_one_way_entrances]


#   Abbreviations
#       DMC     Death Mountain Crater
#       DMT     Death Mountain Trail
#       GC      Goron City
#       GF      Gerudo Fortress
#       GS      Gold Skulltula
#       GV      Gerudo Valley
#       HC      Hyrule Castle
#       HF      Hyrule Field
#       KF      Kokiri Forest
#       LH      Lake Hylia
#       LLR     Lon Lon Ranch
#       LW      Lost Woods
#       OGC     Outside Ganon's Castle
#       SFM     Sacred Forest Meadow
#       ToT     Temple of Time
#       ZD      Zora's Domain
#       ZF      Zora's Fountain
#       ZR      Zora's River

entrance_shuffle_table = [
    ('Dungeon',         ('KF Outside Deku Tree -> Deku Tree Lobby',                         { 'index': 0x0000 }),
                        ('Deku Tree Lobby -> KF Outside Deku Tree',                         { 'index': 0x0209 })),
    ('Dungeon',         ('Death Mountain -> Dodongos Cavern Beginning',                     { 'index': 0x0004 }),
                        ('Dodongos Cavern Beginning -> Death Mountain',                     { 'index': 0x0242 })),
    ('Dungeon',         ('Zoras Fountain -> Jabu Jabus Belly Beginning',                    { 'index': 0x0028 }),
                        ('Jabu Jabus Belly Beginning -> Zoras Fountain',                    { 'index': 0x0221 })),
    ('Dungeon',         ('SFM Forest Temple Entrance Ledge -> Forest Temple Lobby',         { 'index': 0x0169 }),
                        ('Forest Temple Lobby -> SFM Forest Temple Entrance Ledge',         { 'index': 0x0215 })),
    ('Dungeon',         ('DMC Fire Temple Entrance -> Fire Temple Lower',                   { 'index': 0x0165 }),
                        ('Fire Temple Lower -> DMC Fire Temple Entrance',                   { 'index': 0x024A })),
    ('Dungeon',         ('Lake Hylia -> Water Temple Lobby',                                { 'index': 0x0010 }),
                        ('Water Temple Lobby -> Lake Hylia',                                { 'index': 0x021D })),
    ('Dungeon',         ('Graveyard Warp Pad Region -> Shadow Temple Entryway',             { 'index': 0x0037 }),
                        ('Shadow Temple Entryway -> Graveyard Warp Pad Region',             { 'index': 0x0205 })),
    ('Dungeon',         ('Desert Colossus -> Spirit Temple Lobby',                          { 'index': 0x0082 }),
                        ('Spirit Temple Lobby -> Desert Colossus From Spirit Lobby',        { 'index': 0x01E1 })),
    ('Dungeon',         ('Kakariko Village -> Bottom of the Well',                          { 'index': 0x0098 }),
                        ('Bottom of the Well -> Kakariko Village',                          { 'index': 0x02A6 })),
    ('Dungeon',         ('ZF Ice Ledge -> Ice Cavern Beginning',                            { 'index': 0x0088 }),
                        ('Ice Cavern Beginning -> ZF Ice Ledge',                            { 'index': 0x03D4 })),
    ('Dungeon',         ('Gerudo Fortress -> Gerudo Training Ground Lobby',                 { 'index': 0x0008 }),
                        ('Gerudo Training Ground Lobby -> Gerudo Fortress',                 { 'index': 0x03A8 })),

    ('DungeonSpecial',  ('Ganons Castle Grounds -> Ganons Castle Lobby',                    { 'index': 0x0467 }),
                        ('Ganons Castle Lobby -> Castle Grounds From Ganons Castle',        { 'index': 0x023D })),

    ('ChildBoss',       ('Deku Tree Before Boss -> Queen Gohma Boss Room',                  { 'index': 0x040f, 'savewarp_addresses': [ 0xB06292, 0xBC6162, 0xBC60AE ] }),
                        ('Queen Gohma Boss Room -> Deku Tree Before Boss',                  { 'index': 0x0252 })),
    ('ChildBoss',       ('Dodongos Cavern Before Boss -> King Dodongo Boss Room',           { 'index': 0x040b, 'savewarp_addresses': [ 0xB062B6, 0xBC616E ] }),
                        ('King Dodongo Boss Room -> Dodongos Cavern Mouth',                 { 'index': 0x00c5 })),
    ('ChildBoss',       ('Jabu Jabus Belly Before Boss -> Barinade Boss Room',              { 'index': 0x0301, 'savewarp_addresses': [ 0xB062C2, 0xBC60C2 ] }),
                        ('Barinade Boss Room -> Jabu Jabus Belly Before Boss',              { 'index': 0x0407 })),
    ('AdultBoss',       ('Forest Temple Before Boss -> Phantom Ganon Boss Room',            { 'index': 0x000c, 'savewarp_addresses': [ 0xB062CE, 0xBC6182 ] }),
                        ('Phantom Ganon Boss Room -> Forest Temple Before Boss',            { 'index': 0x024E })),
    ('AdultBoss',       ('Fire Temple Before Boss -> Volvagia Boss Room',                   { 'index': 0x0305, 'savewarp_addresses': [ 0xB062DA, 0xBC60CE ] }),
                        ('Volvagia Boss Room -> Fire Temple Before Boss',                   { 'index': 0x0175 })),
    ('AdultBoss',       ('Water Temple Before Boss -> Morpha Boss Room',                    { 'index': 0x0417, 'savewarp_addresses': [ 0xB062E6, 0xBC6196 ] }),
                        ('Morpha Boss Room -> Water Temple Before Boss',                    { 'index': 0x0423 })),
    ('AdultBoss',       ('Shadow Temple Before Boss -> Bongo Bongo Boss Room',              { 'index': 0x0413, 'savewarp_addresses': [ 0xB062FE, 0xBC61AA ] }),
                        ('Bongo Bongo Boss Room -> Shadow Temple Before Boss',              { 'index': 0x02B2 })),
    ('AdultBoss',       ('Spirit Temple Before Boss -> Twinrova Boss Room',                 { 'index': 0x008D, 'savewarp_addresses': [ 0xB062F2, 0xBC6122 ] }),
                        ('Twinrova Boss Room -> Spirit Temple Before Boss',                 { 'index': 0x02F5 })),

    ('SpecialBoss',     ('Ganons Castle Main -> Ganons Castle Tower',                       { 'index': 0x041B }),
                        ('Ganons Castle Tower -> Ganons Castle Main',                       { 'index': 0x0534 })),

    ('Interior',        ('Kokiri Forest -> KF Midos House',                                 { 'index': 0x0433 }),
                        ('KF Midos House -> Kokiri Forest',                                 { 'index': 0x0443 })),
    ('Interior',        ('Kokiri Forest -> KF Sarias House',                                { 'index': 0x0437 }),
                        ('KF Sarias House -> Kokiri Forest',                                { 'index': 0x0447 })),
    ('Interior',        ('Kokiri Forest -> KF House of Twins',                              { 'index': 0x009C }),
                        ('KF House of Twins -> Kokiri Forest',                              { 'index': 0x033C })),
    ('Interior',        ('Kokiri Forest -> KF Know It All House',                           { 'index': 0x00C9 }),
                        ('KF Know It All House -> Kokiri Forest',                           { 'index': 0x026A })),
    ('Interior',        ('Kokiri Forest -> KF Kokiri Shop',                                 { 'index': 0x00C1 }),
                        ('KF Kokiri Shop -> Kokiri Forest',                                 { 'index': 0x0266 })),
    ('Interior',        ('Lake Hylia -> LH Lab',                                            { 'index': 0x0043 }),
                        ('LH Lab -> Lake Hylia',                                            { 'index': 0x03CC })),
    ('Interior',        ('LH Fishing Island -> LH Fishing Hole',                            { 'index': 0x045F }),
                        ('LH Fishing Hole -> LH Fishing Island',                            { 'index': 0x0309 })),
    ('Interior',        ('GV Fortress Side -> GV Carpenter Tent',                           { 'index': 0x03A0 }),
                        ('GV Carpenter Tent -> GV Fortress Side',                           { 'index': 0x03D0 })),
    ('Interior',        ('Market Entrance -> Market Guard House',                           { 'index': 0x007E }),
                        ('Market Guard House -> Market Entrance',                           { 'index': 0x026E })),
    ('Interior',        ('Market -> Market Mask Shop',                                      { 'index': 0x0530 }),
                        ('Market Mask Shop -> Market',                                      { 'index': 0x01D1, 'addresses': [0xC6DA5E] })),
    ('Interior',        ('Market -> Market Bombchu Bowling',                                { 'index': 0x0507 }),
                        ('Market Bombchu Bowling -> Market',                                { 'index': 0x03BC })),
    ('Interior',        ('Market -> Market Potion Shop',                                    { 'index': 0x0388 }),
                        ('Market Potion Shop -> Market',                                    { 'index': 0x02A2 })),
    ('Interior',        ('Market -> Market Treasure Chest Game',                            { 'index': 0x0063 }),
                        ('Market Treasure Chest Game -> Market',                            { 'index': 0x01D5 })),
    ('Interior',        ('Market Back Alley -> Market Bombchu Shop',                        { 'index': 0x0528 }),
                        ('Market Bombchu Shop -> Market Back Alley',                        { 'index': 0x03C0 })),
    ('Interior',        ('Market Back Alley -> Market Man in Green House',                  { 'index': 0x043B }),
                        ('Market Man in Green House -> Market Back Alley',                  { 'index': 0x0067 })),
    ('Interior',        ('Kakariko Village -> Kak Carpenter Boss House',                    { 'index': 0x02FD }),
                        ('Kak Carpenter Boss House -> Kakariko Village',                    { 'index': 0x0349 })),
    ('Interior',        ('Kakariko Village -> Kak House of Skulltula',                      { 'index': 0x0550 }),
                        ('Kak House of Skulltula -> Kakariko Village',                      { 'index': 0x04EE })),
    ('Interior',        ('Kakariko Village -> Kak Impas House',                             { 'index': 0x039C }),
                        ('Kak Impas House -> Kakariko Village',                             { 'index': 0x0345 })),
    ('Interior',        ('Kak Impas Ledge -> Kak Impas House Back',                         { 'index': 0x05C8 }),
                        ('Kak Impas House Back -> Kak Impas Ledge',                         { 'index': 0x05DC })),
    ('Interior',        ('Kak Backyard -> Kak Odd Medicine Building',                       { 'index': 0x0072 }),
                        ('Kak Odd Medicine Building -> Kak Backyard',                       { 'index': 0x034D })),
    ('Interior',        ('Graveyard -> Graveyard Dampes House',                             { 'index': 0x030D }),
                        ('Graveyard Dampes House -> Graveyard',                             { 'index': 0x0355 })),
    ('Interior',        ('Goron City -> GC Shop',                                           { 'index': 0x037C }),
                        ('GC Shop -> Goron City',                                           { 'index': 0x03FC })),
    ('Interior',        ('Zoras Domain -> ZD Shop',                                         { 'index': 0x0380 }),
                        ('ZD Shop -> Zoras Domain',                                         { 'index': 0x03C4 })),
    ('Interior',        ('Lon Lon Ranch -> LLR Talons House',                               { 'index': 0x004F }),
                        ('LLR Talons House -> Lon Lon Ranch',                               { 'index': 0x0378 })),
    ('Interior',        ('Lon Lon Ranch -> LLR Stables',                                    { 'index': 0x02F9 }),
                        ('LLR Stables -> Lon Lon Ranch',                                    { 'index': 0x042F })),
    ('Interior',        ('Lon Lon Ranch -> LLR Tower',                                      { 'index': 0x05D0 }),
                        ('LLR Tower -> Lon Lon Ranch',                                      { 'index': 0x05D4 })),
    ('Interior',        ('Market -> Market Bazaar',                                         { 'index': 0x052C }),
                        ('Market Bazaar -> Market',                                         { 'index': 0x03B8, 'addresses': [0xBEFD74] })),
    ('Interior',        ('Market -> Market Shooting Gallery',                               { 'index': 0x016D }),
                        ('Market Shooting Gallery -> Market',                               { 'index': 0x01CD, 'addresses': [0xBEFD7C] })),
    ('Interior',        ('Kakariko Village -> Kak Bazaar',                                  { 'index': 0x00B7 }),
                        ('Kak Bazaar -> Kakariko Village',                                  { 'index': 0x0201, 'addresses': [0xBEFD72] })),
    ('Interior',        ('Kakariko Village -> Kak Shooting Gallery',                        { 'index': 0x003B }),
                        ('Kak Shooting Gallery -> Kakariko Village',                        { 'index': 0x0463, 'addresses': [0xBEFD7A] })),
    ('Interior',        ('Desert Colossus -> Colossus Great Fairy Fountain',                { 'index': 0x0588 }),
                        ('Colossus Great Fairy Fountain -> Desert Colossus',                { 'index': 0x057C, 'addresses': [0xBEFD82] })),
    ('Interior',        ('Hyrule Castle Grounds -> HC Great Fairy Fountain',                { 'index': 0x0578 }),
                        ('HC Great Fairy Fountain -> Castle Grounds',                       { 'index': 0x0340, 'addresses': [0xBEFD80] })),
    ('Interior',        ('Ganons Castle Grounds -> OGC Great Fairy Fountain',               { 'index': 0x04C2 }),
                        ('OGC Great Fairy Fountain -> Castle Grounds',                      { 'index': 0x0340, 'addresses': [0xBEFD6C] })),
    ('Interior',        ('DMC Lower Nearby -> DMC Great Fairy Fountain',                    { 'index': 0x04BE }),
                        ('DMC Great Fairy Fountain -> DMC Lower Local',                     { 'index': 0x0482, 'addresses': [0xBEFD6A] })),
    ('Interior',        ('Death Mountain Summit -> DMT Great Fairy Fountain',               { 'index': 0x0315 }),
                        ('DMT Great Fairy Fountain -> Death Mountain Summit',               { 'index': 0x045B, 'addresses': [0xBEFD68] })),
    ('Interior',        ('Zoras Fountain -> ZF Great Fairy Fountain',                       { 'index': 0x0371 }),
                        ('ZF Great Fairy Fountain -> Zoras Fountain',                       { 'index': 0x0394, 'addresses': [0xBEFD7E] })),

    ('SpecialInterior', ('Kokiri Forest -> KF Links House',                                 { 'index': 0x0272 }),
                        ('KF Links House -> Kokiri Forest',                                 { 'index': 0x0211 })),
    ('SpecialInterior', ('ToT Entrance -> Temple of Time',                                  { 'index': 0x0053 }),
                        ('Temple of Time -> ToT Entrance',                                  { 'index': 0x0472 })),
    ('SpecialInterior', ('Kakariko Village -> Kak Windmill',                                { 'index': 0x0453 }),
                        ('Kak Windmill -> Kakariko Village',                                { 'index': 0x0351 })),
    ('SpecialInterior', ('Kakariko Village -> Kak Potion Shop Front',                       { 'index': 0x0384 }),
                        ('Kak Potion Shop Front -> Kakariko Village',                       { 'index': 0x044B })),
    ('SpecialInterior', ('Kak Backyard -> Kak Potion Shop Back',                            { 'index': 0x03EC }),
                        ('Kak Potion Shop Back -> Kak Backyard',                            { 'index': 0x04FF })),

    ('Hideout',         ('Gerudo Fortress -> Hideout 1 Torch Jail',                         { 'index': 0x0486 }),
                        ('Hideout 1 Torch Jail -> Gerudo Fortress',                         { 'index': 0x0231 })),
    ('Hideout',         ('GF Entrances Behind Crates -> Hideout 1 Torch Jail',              { 'index': 0x048A }),
                        ('Hideout 1 Torch Jail -> GF Entrances Behind Crates',              { 'index': 0x0235 })),
    ('Hideout',         ('GF Entrances Behind Crates -> Hideout Kitchen Hallway',           { 'index': 0x048E }),
                        ('Hideout Kitchen Hallway -> GF Entrances Behind Crates',           { 'index': 0x0239 })),
    ('Hideout',         ('Gerudo Fortress -> Hideout Kitchen Hallway',                      { 'index': 0x0492 }),
                        ('Hideout Kitchen Hallway -> Gerudo Fortress',                      { 'index': 0x02AA })),
    ('Hideout',         ('Gerudo Fortress -> Hideout 4 Torches Jail',                       { 'index': 0x0496 }),
                        ('Hideout 4 Torches Jail -> Gerudo Fortress',                       { 'index': 0x02BA })),
    ('Hideout',         ('GF Roof Entrance Cluster -> Hideout 4 Torches Jail',              { 'index': 0x049A }),
                        ('Hideout 4 Torches Jail -> GF Roof Entrance Cluster',              { 'index': 0x02BE })),
    ('Hideout',         ('Gerudo Fortress -> Hideout 2 Torches Jail',                       { 'index': 0x049E }),
                        ('Hideout 2 Torches Jail -> Gerudo Fortress',                       { 'index': 0x02C2 })),
    ('Hideout',         ('GF Roof Entrance Cluster -> Hideout 2 Torches Jail',              { 'index': 0x04A2 }),
                        ('Hideout 2 Torches Jail -> GF Roof Entrance Cluster',              { 'index': 0x02C6 })),
    ('Hideout',         ('GF Roof Entrance Cluster -> Hideout Kitchen Front',               { 'index': 0x04A6 }),
                        ('Hideout Kitchen Front -> GF Roof Entrance Cluster',               { 'index': 0x02D2 })),
    ('Hideout',         ('GF Kitchen Roof Access -> Hideout Kitchen Rear',                  { 'index': 0x04AA }),
                        ('Hideout Kitchen Rear -> GF Kitchen Roof Access',                  { 'index': 0x02D6 })),
    ('Hideout',         ('GF Break Room Entrance -> Hideout Break Room',                    { 'index': 0x04AE }),
                        ('Hideout Break Room -> GF Break Room Entrance',                    { 'index': 0x02DA })),
    ('Hideout',         ('GF Balcony -> Hideout Hall to Balcony',                           { 'index': 0x04B2 }),
                        ('Hideout Hall to Balcony -> GF Balcony',                           { 'index': 0x02DE })),
    ('Hideout',         ('GF 3 Torches Jail Exterior -> Hideout 3 Torches Jail',            { 'index': 0x0570 }),
                        ('Hideout 3 Torches Jail -> GF 3 Torches Jail Exterior',            { 'index': 0x03A4 })),

    ('Grotto',          ('Desert Colossus -> Colossus Grotto',                              { 'grotto_id': 0x00, 'entrance': 0x05BC, 'content': 0xFD, 'scene': 0x5C }),
                        ('Colossus Grotto -> Desert Colossus',                              { 'grotto_id': 0x00, 'savewarp_fallback': 0x01F1 })),
    ('Grotto',          ('Lake Hylia -> LH Grotto',                                         { 'grotto_id': 0x01, 'entrance': 0x05A4, 'content': 0xEF, 'scene': 0x57 }),
                        ('LH Grotto -> Lake Hylia',                                         { 'grotto_id': 0x01, 'savewarp_fallback': 0x0604 })),
    ('Grotto',          ('Zora River -> ZR Storms Grotto',                                  { 'grotto_id': 0x02, 'entrance': 0x05BC, 'content': 0xEB, 'scene': 0x54 }),
                        ('ZR Storms Grotto -> Zora River',                                  { 'grotto_id': 0x02, 'savewarp_fallback': 0x0199 })),
    ('Grotto',          ('Zora River -> ZR Fairy Grotto',                                   { 'grotto_id': 0x03, 'entrance': 0x036D, 'content': 0xE6, 'scene': 0x54 }),
                        ('ZR Fairy Grotto -> Zora River',                                   { 'grotto_id': 0x03, 'savewarp_fallback': 0x0199 })),
    ('Grotto',          ('Zora River -> ZR Open Grotto',                                    { 'grotto_id': 0x04, 'entrance': 0x003F, 'content': 0x29, 'scene': 0x54 }),
                        ('ZR Open Grotto -> Zora River',                                    { 'grotto_id': 0x04, 'savewarp_fallback': 0x0199 })),
    ('Grotto',          ('DMC Lower Nearby -> DMC Hammer Grotto',                           { 'grotto_id': 0x05, 'entrance': 0x05A4, 'content': 0xF9, 'scene': 0x61 }),
                        ('DMC Hammer Grotto -> DMC Lower Local',                            { 'grotto_id': 0x05, 'savewarp_fallback': 0x0246 })),
    ('Grotto',          ('DMC Upper Nearby -> DMC Upper Grotto',                            { 'grotto_id': 0x06, 'entrance': 0x003F, 'content': 0x7A, 'scene': 0x61 }),
                        ('DMC Upper Grotto -> DMC Upper Local',                             { 'grotto_id': 0x06, 'savewarp_fallback': 0x0147 })),
    ('Grotto',          ('GC Grotto Platform -> GC Grotto',                                 { 'grotto_id': 0x07, 'entrance': 0x05A4, 'content': 0xFB, 'scene': 0x62 }),
                        ('GC Grotto -> GC Grotto Platform',                                 { 'grotto_id': 0x07, 'savewarp_fallback': 0x014D })), #TODO (out-of-logic access to Goron City)
    ('Grotto',          ('Death Mountain -> DMT Storms Grotto',                             { 'grotto_id': 0x08, 'entrance': 0x003F, 'content': 0x57, 'scene': 0x60 }),
                        ('DMT Storms Grotto -> Death Mountain',                             { 'grotto_id': 0x08, 'savewarp_fallback': 0x01B9 })),
    ('Grotto',          ('Death Mountain Summit -> DMT Cow Grotto',                         { 'grotto_id': 0x09, 'entrance': 0x05FC, 'content': 0xF8, 'scene': 0x60 }),
                        ('DMT Cow Grotto -> Death Mountain Summit',                         { 'grotto_id': 0x09, 'savewarp_fallback': 0x045B })),
    ('Grotto',          ('Kak Backyard -> Kak Open Grotto',                                 { 'grotto_id': 0x0A, 'entrance': 0x003F, 'content': 0x28, 'scene': 0x52 }),
                        ('Kak Open Grotto -> Kak Backyard',                                 { 'grotto_id': 0x0A, 'savewarp_fallback': 0x04FF })),
    ('Grotto',          ('Kakariko Village -> Kak Redead Grotto',                           { 'grotto_id': 0x0B, 'entrance': 0x05A0, 'content': 0xE7, 'scene': 0x52 }),
                        ('Kak Redead Grotto -> Kakariko Village',                           { 'grotto_id': 0x0B, 'savewarp_fallback': 0x0349 })),
    ('Grotto',          ('Hyrule Castle Grounds -> HC Storms Grotto',                       { 'grotto_id': 0x0C, 'entrance': 0x05B8, 'content': 0xF6, 'scene': 0x5F }),
                        ('HC Storms Grotto -> Castle Grounds',                              { 'grotto_id': 0x0C, 'savewarp_fallback': 0x0340 })),
    ('Grotto',          ('Hyrule Field -> HF Tektite Grotto',                               { 'grotto_id': 0x0D, 'entrance': 0x05C0, 'content': 0xE1, 'scene': 0x51 }),
                        ('HF Tektite Grotto -> Hyrule Field',                               { 'grotto_id': 0x0D, 'savewarp_fallback': 0x01F9 })),
    ('Grotto',          ('Hyrule Field -> HF Near Kak Grotto',                              { 'grotto_id': 0x0E, 'entrance': 0x0598, 'content': 0xE5, 'scene': 0x51 }),
                        ('HF Near Kak Grotto -> Hyrule Field',                              { 'grotto_id': 0x0E, 'savewarp_fallback': 0x017D })),
    ('Grotto',          ('Hyrule Field -> HF Fairy Grotto',                                 { 'grotto_id': 0x0F, 'entrance': 0x036D, 'content': 0xFF, 'scene': 0x51 }),
                        ('HF Fairy Grotto -> Hyrule Field',                                 { 'grotto_id': 0x0F, 'savewarp_fallback': 0x027E })),
    ('Grotto',          ('Hyrule Field -> HF Near Market Grotto',                           { 'grotto_id': 0x10, 'entrance': 0x003F, 'content': 0x00, 'scene': 0x51 }),
                        ('HF Near Market Grotto -> Hyrule Field',                           { 'grotto_id': 0x10, 'savewarp_fallback': 0x027E })),
    ('Grotto',          ('Hyrule Field -> HF Cow Grotto',                                   { 'grotto_id': 0x11, 'entrance': 0x05A8, 'content': 0xE4, 'scene': 0x51 }),
                        ('HF Cow Grotto -> Hyrule Field',                                   { 'grotto_id': 0x11, 'savewarp_fallback': 0x018D })),
    ('Grotto',          ('Hyrule Field -> HF Inside Fence Grotto',                          { 'grotto_id': 0x12, 'entrance': 0x059C, 'content': 0xE6, 'scene': 0x51 }),
                        ('HF Inside Fence Grotto -> Hyrule Field',                          { 'grotto_id': 0x12, 'savewarp_fallback': 0x0189 })),
    ('Grotto',          ('Hyrule Field -> HF Open Grotto',                                  { 'grotto_id': 0x13, 'entrance': 0x003F, 'content': 0x03, 'scene': 0x51 }),
                        ('HF Open Grotto -> Hyrule Field',                                  { 'grotto_id': 0x13, 'savewarp_fallback': 0x0189 })),
    ('Grotto',          ('Hyrule Field -> HF Southeast Grotto',                             { 'grotto_id': 0x14, 'entrance': 0x003F, 'content': 0x22, 'scene': 0x51 }),
                        ('HF Southeast Grotto -> Hyrule Field',                             { 'grotto_id': 0x14, 'savewarp_fallback': 0x0189 })),
    ('Grotto',          ('Lon Lon Ranch -> LLR Grotto',                                     { 'grotto_id': 0x15, 'entrance': 0x05A4, 'content': 0xFC, 'scene': 0x63 }),
                        ('LLR Grotto -> Lon Lon Ranch',                                     { 'grotto_id': 0x15, 'savewarp_fallback': 0x05D4 })),
    ('Grotto',          ('SFM Entryway -> SFM Wolfos Grotto',                               { 'grotto_id': 0x16, 'entrance': 0x05B4, 'content': 0xED, 'scene': 0x56 }),
                        ('SFM Wolfos Grotto -> SFM Entryway',                               { 'grotto_id': 0x16, 'savewarp_fallback': 0x00FC })),
    ('Grotto',          ('Sacred Forest Meadow -> SFM Storms Grotto',                       { 'grotto_id': 0x17, 'entrance': 0x05BC, 'content': 0xEE, 'scene': 0x56 }),
                        ('SFM Storms Grotto -> Sacred Forest Meadow',                       { 'grotto_id': 0x17, 'savewarp_fallback': 0x0600 })),
    ('Grotto',          ('Sacred Forest Meadow -> SFM Fairy Grotto',                        { 'grotto_id': 0x18, 'entrance': 0x036D, 'content': 0xFF, 'scene': 0x56 }),
                        ('SFM Fairy Grotto -> Sacred Forest Meadow',                        { 'grotto_id': 0x18, 'savewarp_fallback': 0x0600 })),
    ('Grotto',          ('LW Beyond Mido -> LW Scrubs Grotto',                              { 'grotto_id': 0x19, 'entrance': 0x05B0, 'content': 0xF5, 'scene': 0x5B }),
                        ('LW Scrubs Grotto -> LW Beyond Mido',                              { 'grotto_id': 0x19, 'savewarp_fallback': 0x01A9 })),
    ('Grotto',          ('Lost Woods -> LW Near Shortcuts Grotto',                          { 'grotto_id': 0x1A, 'entrance': 0x003F, 'content': 0x14, 'scene': 0x5B }),
                        ('LW Near Shortcuts Grotto -> Lost Woods',                          { 'grotto_id': 0x1A, 'savewarp_fallback': 0x04D6 })),
    ('Grotto',          ('Kokiri Forest -> KF Storms Grotto',                               { 'grotto_id': 0x1B, 'entrance': 0x003F, 'content': 0x2C, 'scene': 0x55 }),
                        ('KF Storms Grotto -> Kokiri Forest',                               { 'grotto_id': 0x1B, 'savewarp_fallback': 0x0286 })),
    ('Grotto',          ('Zoras Domain -> ZD Storms Grotto',                                { 'grotto_id': 0x1C, 'entrance': 0x036D, 'content': 0xFF, 'scene': 0x58 }),
                        ('ZD Storms Grotto -> Zoras Domain',                                { 'grotto_id': 0x1C, 'savewarp_fallback': 0x0108 })),
    ('Grotto',          ('GF Entrances Behind Crates -> GF Storms Grotto',                  { 'grotto_id': 0x1D, 'entrance': 0x036D, 'content': 0xFF, 'scene': 0x5D }),
                        ('GF Storms Grotto -> GF Entrances Behind Crates',                  { 'grotto_id': 0x1D, 'savewarp_fallback': 0x0235 })),
    ('Grotto',          ('GV Fortress Side -> GV Storms Grotto',                            { 'grotto_id': 0x1E, 'entrance': 0x05BC, 'content': 0xF0, 'scene': 0x5A }),
                        ('GV Storms Grotto -> GV Fortress Side',                            { 'grotto_id': 0x1E, 'savewarp_fallback': 0x022D })),
    ('Grotto',          ('GV Grotto Ledge -> GV Octorok Grotto',                            { 'grotto_id': 0x1F, 'entrance': 0x05AC, 'content': 0xF2, 'scene': 0x5A }),
                        ('GV Octorok Grotto -> GV Grotto Ledge',                            { 'grotto_id': 0x1F, 'savewarp_fallback': 0x0117 })), #TODO (out-of-logic access to Gerudo Valley)
    ('Grotto',          ('LW Beyond Mido -> Deku Theater',                                  { 'grotto_id': 0x20, 'entrance': 0x05C4, 'content': 0xF3, 'scene': 0x5B }),
                        ('Deku Theater -> LW Beyond Mido',                                  { 'grotto_id': 0x20, 'savewarp_fallback': 0x01A9 })),

    ('Grave',           ('Graveyard -> Graveyard Shield Grave',                             { 'index': 0x004B }),
                        ('Graveyard Shield Grave -> Graveyard',                             { 'index': 0x035D })),
    ('Grave',           ('Graveyard -> Graveyard Heart Piece Grave',                        { 'index': 0x031C }),
                        ('Graveyard Heart Piece Grave -> Graveyard',                        { 'index': 0x0361 })),
    ('Grave',           ('Graveyard -> Graveyard Royal Familys Tomb',                       { 'index': 0x002D }),
                        ('Graveyard Royal Familys Tomb -> Graveyard',                       { 'index': 0x050B })),
    ('Grave',           ('Graveyard -> Graveyard Dampes Grave',                             { 'index': 0x044F }),
                        ('Graveyard Dampes Grave -> Graveyard',                             { 'index': 0x0359 })),

    ('Overworld',       ('Kokiri Forest -> LW Bridge From Forest',                          { 'index': 0x05E0 }),
                        ('LW Bridge -> Kokiri Forest',                                      { 'index': 0x020D })),
    ('Overworld',       ('Kokiri Forest -> Lost Woods',                                     { 'index': 0x011E }),
                        ('LW Forest Exit -> Kokiri Forest',                                 { 'index': 0x0286 })),
    ('Overworld',       ('Lost Woods -> GC Woods Warp',                                     { 'index': 0x04E2 }),
                        ('GC Woods Warp -> Lost Woods',                                     { 'index': 0x04D6 })),
    ('Overworld',       ('Lost Woods -> Zora River',                                        { 'index': 0x01DD }),
                        ('Zora River -> LW Underwater Entrance',                            { 'index': 0x04DA })),
    ('Overworld',       ('LW Beyond Mido -> SFM Entryway',                                  { 'index': 0x00FC }),
                        ('SFM Entryway -> LW Beyond Mido',                                  { 'index': 0x01A9 })),
    ('Overworld',       ('LW Bridge -> Hyrule Field',                                       { 'index': 0x0185 }),
                        ('Hyrule Field -> LW Bridge',                                       { 'index': 0x04DE })),
    ('Overworld',       ('Hyrule Field -> Lake Hylia',                                      { 'index': 0x0102 }),
                        ('Lake Hylia -> Hyrule Field',                                      { 'index': 0x0189 })),
    ('Overworld',       ('Hyrule Field -> Gerudo Valley',                                   { 'index': 0x0117 }),
                        ('Gerudo Valley -> Hyrule Field',                                   { 'index': 0x018D })),
    ('Overworld',       ('Hyrule Field -> Market Entrance',                                 { 'index': 0x0276 }),
                        ('Market Entrance -> Hyrule Field',                                 { 'index': 0x01FD })),
    ('Overworld',       ('Hyrule Field -> Kakariko Village',                                { 'index': 0x00DB }),
                        ('Kakariko Village -> Hyrule Field',                                { 'index': 0x017D })),
    ('Overworld',       ('Hyrule Field -> ZR Front',                                        { 'index': 0x00EA }),
                        ('ZR Front -> Hyrule Field',                                        { 'index': 0x0181 })),
    ('Overworld',       ('Hyrule Field -> Lon Lon Ranch',                                   { 'index': 0x0157 }),
                        ('Lon Lon Ranch -> Hyrule Field',                                   { 'index': 0x01F9 })),
    ('Overworld',       ('Lake Hylia -> Zoras Domain',                                      { 'index': 0x0328 }),
                        ('Zoras Domain -> Lake Hylia',                                      { 'index': 0x0560 })),
    ('Overworld',       ('GV Fortress Side -> Gerudo Fortress',                             { 'index': 0x0129 }),
                        ('Gerudo Fortress -> GV Fortress Side',                             { 'index': 0x022D })),
    ('Overworld',       ('GF Outside Gate -> Wasteland Near Fortress',                      { 'index': 0x0130 }),
                        ('Wasteland Near Fortress -> GF Outside Gate',                      { 'index': 0x03AC })),
    ('Overworld',       ('Wasteland Near Colossus -> Desert Colossus',                      { 'index': 0x0123 }),
                        ('Desert Colossus -> Wasteland Near Colossus',                      { 'index': 0x0365 })),
    ('Overworld',       ('Market Entrance -> Market',                                       { 'index': 0x00B1 }),
                        ('Market -> Market Entrance',                                       { 'index': 0x0033 })),
    ('Overworld',       ('Market -> Castle Grounds',                                        { 'index': 0x0138 }),
                        ('Castle Grounds -> Market',                                        { 'index': 0x025A })),
    ('Overworld',       ('Market -> ToT Entrance',                                          { 'index': 0x0171 }),
                        ('ToT Entrance -> Market',                                          { 'index': 0x025E })),
    ('Overworld',       ('Kakariko Village -> Graveyard',                                   { 'index': 0x00E4 }),
                        ('Graveyard -> Kakariko Village',                                   { 'index': 0x0195 })),
    ('Overworld',       ('Kak Behind Gate -> Death Mountain',                               { 'index': 0x013D }),
                        ('Death Mountain -> Kak Behind Gate',                               { 'index': 0x0191 })),
    ('Overworld',       ('Death Mountain -> Goron City',                                    { 'index': 0x014D }),
                        ('Goron City -> Death Mountain',                                    { 'index': 0x01B9 })),
    ('Overworld',       ('GC Darunias Chamber -> DMC Lower Local',                          { 'index': 0x0246 }),
                        ('DMC Lower Nearby -> GC Darunias Chamber',                         { 'index': 0x01C1 })),
    ('Overworld',       ('Death Mountain Summit -> DMC Upper Local',                        { 'index': 0x0147 }),
                        ('DMC Upper Nearby -> Death Mountain Summit',                       { 'index': 0x01BD })),
    ('Overworld',       ('ZR Behind Waterfall -> Zoras Domain',                             { 'index': 0x0108 }),
                        ('Zoras Domain -> ZR Behind Waterfall',                             { 'index': 0x019D })),
    ('Overworld',       ('ZD Behind King Zora -> Zoras Fountain',                           { 'index': 0x0225 }),
                        ('Zoras Fountain -> ZD Behind King Zora',                           { 'index': 0x01A1 })),

    ('OverworldOneWay', ('GV Lower Stream -> Lake Hylia',                                   { 'index': 0x0219 })),

    ('OwlDrop',         ('LH Owl Flight -> Hyrule Field',                                   { 'index': 0x027E, 'addresses': [0xAC9F26] })),
    ('OwlDrop',         ('DMT Owl Flight -> Kak Impas Rooftop',                             { 'index': 0x0554, 'addresses': [0xAC9EF2] })),

    ('Spawn',           ('Child Spawn -> KF Links House',                                   { 'index': 0x00BB, 'addresses': [0xB06342] })),
    ('Spawn',           ('Adult Spawn -> Temple of Time',                                   { 'index': 0x05F4, 'addresses': [0xB06332] })),

    ('WarpSong',        ('Minuet of Forest Warp -> Sacred Forest Meadow',                   { 'index': 0x0600, 'addresses': [0xBF023C] })),
    ('WarpSong',        ('Bolero of Fire Warp -> DMC Central Local',                        { 'index': 0x04F6, 'addresses': [0xBF023E] })),
    ('WarpSong',        ('Serenade of Water Warp -> Lake Hylia',                            { 'index': 0x0604, 'addresses': [0xBF0240] })),
    ('WarpSong',        ('Requiem of Spirit Warp -> Desert Colossus',                       { 'index': 0x01F1, 'addresses': [0xBF0242] })),
    ('WarpSong',        ('Nocturne of Shadow Warp -> Graveyard Warp Pad Region',            { 'index': 0x0568, 'addresses': [0xBF0244] })),
    ('WarpSong',        ('Prelude of Light Warp -> Temple of Time',                         { 'index': 0x05F4, 'addresses': [0xBF0246] })),

    ('BlueWarp',        ('Queen Gohma Boss Room -> KF Outside Deku Tree',                   { 'index': 0x0457, 'addresses': [0xAC93A2, 0xCA3142, 0xCA316A] })),
    ('BlueWarp',        ('King Dodongo Boss Room -> Death Mountain',                        { 'index': 0x047A, 'addresses': [0xAC9336, 0xCA30CA, 0xCA30EA] })),
    ('BlueWarp',        ('Barinade Boss Room -> Zoras Fountain',                            { 'index': 0x010E, 'addresses': [0xAC936A, 0xCA31B2, 0xCA3702] })),
    ('BlueWarp',        ('Phantom Ganon Boss Room -> Sacred Forest Meadow',                 { 'index': 0x0608, 'addresses': [0xAC9F96, 0xCA3D66, 0xCA3D5A, 0xCA3D32], 'child_index': 0x0600 })),
    ('BlueWarp',        ('Volvagia Boss Room -> DMC Central Local',                         { 'index': 0x0564, 'addresses': [0xACA516, 0xCA3DF2, 0xCA3DE6, 0xCA3DBE], 'child_index': 0x04F6 })),
    ('BlueWarp',        ('Morpha Boss Room -> Lake Hylia',                                  { 'index': 0x060C, 'addresses': [0xAC995A, 0xCA3E82, 0xCA3E76, 0xCA3E4A], 'child_index': 0x0604 })),
    ('BlueWarp',        ('Bongo Bongo Boss Room -> Graveyard Warp Pad Region',              { 'index': 0x0580, 'addresses': [0xACA496, 0xCA3FA2, 0xCA3F96, 0xCA3F6A], 'child_index': 0x0568 })),
    ('BlueWarp',        ('Twinrova Boss Room -> Desert Colossus',                           { 'index': 0x0610, 'addresses': [0xACA402, 0xCA3F12, 0xCA3F06, 0xCA3EDA], 'child_index': 0x01F1 })),

    ('Extra',           ('ZD Eyeball Frog Timeout -> Zoras Domain',                         { 'index': 0x0153 })),
    ('Extra',           ('ZR Top of Waterfall -> Zora River',                               { 'index': 0x0199 })),
]


# Basically, the entrances in the list above that go to:
# - DMC Central Local (child access for the bean and skull)
# - Desert Colossus (child access to colossus and spirit)
# - Graveyard Warp Pad Region (access to shadow, plus the gossip stone)
# We will always need to pick one from each list to receive a one-way entrance
# if shuffling warp songs (depending on other settings).
# Table maps: short key -> ([target regions], [allowed types])
priority_entrance_table = {
    'Bolero': (['DMC Central Local'], ['OwlDrop', 'WarpSong', 'OverworldOneWay']),
    'Nocturne': (['Graveyard Warp Pad Region'], ['OwlDrop', 'Spawn', 'WarpSong', 'OverworldOneWay']),
    'Requiem': (['Desert Colossus', 'Desert Colossus From Spirit Lobby'], ['OwlDrop', 'Spawn', 'WarpSong', 'OverworldOneWay']),
}


class EntranceShuffleError(ShuffleError):
    pass


# Set entrances of all worlds, first initializing them to their default regions, then potentially shuffling part of them
def set_entrances(worlds: list[World], savewarps_to_connect: list[tuple[Entrance, str]]) -> None:
    for world in worlds:
        world.initialize_entrances()

    for savewarp, replaces in savewarps_to_connect:
        savewarp.replaces = savewarp.world.get_entrance(replaces)
        savewarp.connect(savewarp.replaces.connected_region)

    for world in worlds:
        if world.settings.logic_rules != 'glitched':
            # Set entrance data for all entrances, even those we aren't shuffling
            set_all_entrances_data(world)

    if worlds[0].entrance_shuffle:
        shuffle_random_entrances(worlds)

    set_entrances_based_rules(worlds)


# Shuffles entrances that need to be shuffled in all worlds
def shuffle_random_entrances(worlds: list[World]) -> None:
    # Store all locations reachable before shuffling to differentiate which locations were already unreachable from those we made unreachable
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]
    max_search = Search.max_explore([world.state for world in worlds], complete_itempool)

    non_drop_locations = [location for world in worlds for location in world.get_locations() if location.type not in ('Drop', 'Event')]
    max_search.visit_locations(non_drop_locations)
    locations_to_ensure_reachable = list(filter(max_search.visited, non_drop_locations))
    placed_one_way_entrances = None

    # Shuffle all entrances within their own worlds
    for world in worlds:
        # Determine entrance pools based on settings, to be shuffled in the order we set them by
        one_way_entrance_pools = OrderedDict()
        entrance_pools = OrderedDict()
        one_way_priorities = {}

        if worlds[0].settings.shuffle_gerudo_valley_river_exit:
            one_way_entrance_pools['OverworldOneWay'] = world.get_shufflable_entrances(type='OverworldOneWay')

        if worlds[0].settings.owl_drops:
            one_way_entrance_pools['OwlDrop'] = world.get_shufflable_entrances(type='OwlDrop')

        if worlds[0].settings.spawn_positions:
            one_way_entrance_pools['Spawn'] = world.get_shufflable_entrances(type='Spawn')
            if 'child' not in worlds[0].settings.spawn_positions:
                one_way_entrance_pools['Spawn'].remove(world.get_entrance('Child Spawn -> KF Links House'))
            elif 'adult' not in worlds[0].settings.spawn_positions:
                one_way_entrance_pools['Spawn'].remove(world.get_entrance('Adult Spawn -> Temple of Time'))

        if worlds[0].settings.warp_songs:
            one_way_entrance_pools['WarpSong'] = world.get_shufflable_entrances(type='WarpSong')
            if worlds[0].settings.reachable_locations != 'beatable' and worlds[0].settings.logic_rules == 'glitchless':
                # In glitchless, there aren't any other ways to access these areas
                wincons = {worlds[0].settings.bridge, worlds[0].settings.shuffle_ganon_bosskey}
                if worlds[0].settings.shuffle_ganon_bosskey == 'on_lacs':
                    wincons.add(worlds[0].settings.lacs_condition)
                if worlds[0].settings.shuffle_dungeon_rewards != 'dungeon' and (
                    worlds[0].settings.shuffle_dungeon_rewards not in ('vanilla', 'reward')
                    or worlds[0].mixed_pools_bosses
                ):
                    wincons -= {'dungeons', 'stones', 'medallions'}
                if (
                    worlds[0].settings.reachable_locations == 'all'
                    or ('tokens' in wincons and worlds[0].settings.tokensanity in ('off', 'dungeons'))
                ):
                    one_way_priorities['Bolero'] = priority_entrance_table['Bolero']
                if (
                    worlds[0].settings.reachable_locations == 'all'
                    or 'dungeons' in wincons
                    or ('stones' in wincons and 'medallions' in wincons)
                    or ('tokens' in wincons and worlds[0].settings.tokensanity in ('off', 'overworld'))
                ):
                    one_way_priorities['Nocturne'] = priority_entrance_table['Nocturne']
                if (
                    not worlds[0].shuffle_dungeon_entrances
                    and not worlds[0].settings.shuffle_overworld_entrances
                    and not worlds[0].shuffle_special_interior_entrances
                    and (
                        worlds[0].settings.reachable_locations == 'all'
                        or 'dungeons' in wincons
                        or ('stones' in wincons and 'medallions' in wincons)
                        or ('tokens' in wincons and worlds[0].settings.tokensanity != 'all')
                    )
                ):
                    one_way_priorities['Requiem'] = priority_entrance_table['Requiem']

        if worlds[0].settings.shuffle_bosses == 'full':
            entrance_pools['Boss'] = world.get_shufflable_entrances(type='ChildBoss', only_primary=True)
            entrance_pools['Boss'] += world.get_shufflable_entrances(type='AdultBoss', only_primary=True)
            if worlds[0].settings.shuffle_ganon_tower:
                entrance_pools['Boss'] += world.get_shufflable_entrances(type='SpecialBoss', only_primary=True)
            if worlds[0].settings.open_forest == 'closed':
                # Deku is forced vanilla below, so Queen Gohma must be vanilla to ensure she is reachable.
                # This is already enforced by the fill algorithm in most cases, but this covers the odd settings combination where it isn't.
                entrance_pools['Boss'].remove(world.get_entrance('Deku Tree Before Boss -> Queen Gohma Boss Room'))
        elif worlds[0].settings.shuffle_bosses == 'limited':
            entrance_pools['ChildBoss'] = world.get_shufflable_entrances(type='ChildBoss', only_primary=True)
            entrance_pools['AdultBoss'] = world.get_shufflable_entrances(type='AdultBoss', only_primary=True)
            if worlds[0].settings.shuffle_ganon_tower:
                entrance_pools['AdultBoss'] += world.get_shufflable_entrances(type='SpecialBoss', only_primary=True)
            if worlds[0].settings.open_forest == 'closed':
                # Deku is forced vanilla below, so Queen Gohma must be vanilla to ensure she is reachable.
                # This is already enforced by the fill algorithm in most cases, but this covers the odd settings combination where it isn't.
                entrance_pools['ChildBoss'].remove(world.get_entrance('Deku Tree Before Boss -> Queen Gohma Boss Room'))

        if worlds[0].shuffle_dungeon_entrances:
            entrance_pools['Dungeon'] = world.get_shufflable_entrances(type='Dungeon', only_primary=True)
            # The fill algorithm will already make sure gohma is reachable, however it can end up putting
            # a forest escape via the hands of spirit on Deku leading to Deku on spirit in logic. This is
            # not really a closed forest anymore, so specifically remove Deku Tree from closed forest.
            if worlds[0].settings.open_forest == 'closed':
                entrance_pools['Dungeon'].remove(world.get_entrance('KF Outside Deku Tree -> Deku Tree Lobby'))
            if worlds[0].shuffle_special_dungeon_entrances:
                entrance_pools['Dungeon'] += world.get_shufflable_entrances(type='DungeonSpecial', only_primary=True)

        if worlds[0].shuffle_interior_entrances:
            entrance_pools['Interior'] = world.get_shufflable_entrances(type='Interior', only_primary=True)
            if worlds[0].shuffle_special_interior_entrances:
                entrance_pools['Interior'] += world.get_shufflable_entrances(type='SpecialInterior', only_primary=True)
            if worlds[0].settings.shuffle_hideout_entrances:
                entrance_pools['Interior'] += world.get_shufflable_entrances(type='Hideout', only_primary=True)

        if worlds[0].settings.shuffle_grotto_entrances:
            entrance_pools['GrottoGrave'] = world.get_shufflable_entrances(type='Grotto', only_primary=True)
            entrance_pools['GrottoGrave'] += world.get_shufflable_entrances(type='Grave', only_primary=True)

        if worlds[0].settings.shuffle_overworld_entrances:
            entrance_pools['Overworld'] = world.get_shufflable_entrances(type='Overworld')

        # Set shuffled entrances as such
        for entrance in list(chain.from_iterable(one_way_entrance_pools.values())) + list(chain.from_iterable(entrance_pools.values())):
            entrance.shuffled = True
            if entrance.reverse:
                entrance.reverse.shuffled = True

        # Build target entrance pools and set the assumption for entrances being reachable
        one_way_target_entrance_pools = {}
        for pool_type, entrance_pool in one_way_entrance_pools.items():
            # One way entrances are extra entrances that will be connected to entrance positions from a selection of entrance pools
            if pool_type == 'OverworldOneWay':
                valid_target_types = ('WarpSong', 'BlueWarp', 'OwlDrop', 'OverworldOneWay', 'Overworld', 'Extra')
                one_way_target_entrance_pools[pool_type] = build_one_way_targets(world, valid_target_types, exclude=['Prelude of Light Warp -> Temple of Time'])
            elif pool_type == 'OwlDrop':
                valid_target_types = ('WarpSong', 'BlueWarp', 'OwlDrop', 'OverworldOneWay', 'Overworld', 'Extra')
                one_way_target_entrance_pools[pool_type] = build_one_way_targets(world, valid_target_types, exclude=['Prelude of Light Warp -> Temple of Time'])
                for target in one_way_target_entrance_pools[pool_type]:
                    target.set_rule(lambda state, age=None, **kwargs: age == 'child')
            elif pool_type == 'Spawn':
                valid_target_types = ('Spawn', 'WarpSong', 'BlueWarp', 'OwlDrop', 'OverworldOneWay', 'Overworld', 'Interior', 'SpecialInterior', 'Extra')
                # Restrict spawn entrances from linking to regions with no or extremely specific glitchless itemless escapes.
                one_way_target_entrance_pools[pool_type] = build_one_way_targets(world, valid_target_types, exclude=['Volvagia Boss Room -> DMC Central Local', 'Bolero of Fire Warp -> DMC Central Local', 'Queen Gohma Boss Room -> KF Outside Deku Tree'])
            elif pool_type == 'WarpSong':
                valid_target_types = ('Spawn', 'WarpSong', 'BlueWarp', 'OwlDrop', 'OverworldOneWay', 'Overworld', 'Interior', 'SpecialInterior', 'Extra')
                one_way_target_entrance_pools[pool_type] = build_one_way_targets(world, valid_target_types)
            # Ensure that when trying to place the last entrance of a one way pool, we don't assume the rest of the targets are reachable
            for target in one_way_target_entrance_pools[pool_type]:
                target.add_rule((lambda entrances=entrance_pool: (lambda state, **kwargs: any(
                    entrance.connected_region is None for entrance in entrances)))())
        # Disconnect all one way entrances at this point (they need to be connected during all of the above process)
        for entrance in chain.from_iterable(one_way_entrance_pools.values()):
            entrance.disconnect()

        target_entrance_pools = {}
        for pool_type, entrance_pool in entrance_pools.items():
            target_entrance_pools[pool_type] = assume_entrance_pool(entrance_pool)

        # Set entrances defined in the distribution
        world.distribution.set_shuffled_entrances(worlds, {**one_way_entrance_pools, **entrance_pools}, {**one_way_target_entrance_pools, **target_entrance_pools}, locations_to_ensure_reachable, complete_itempool)

        # Check placed one way entrances and trim.
        # The placed entrances are already pointing at their new regions.
        placed_entrances = [entrance for entrance in chain.from_iterable(one_way_entrance_pools.values())
                            if entrance.replaces is not None]
        replaced_entrances = [entrance.replaces for entrance in placed_entrances]
        # Remove replaced entrances so we don't place two in one target.
        for remaining_target in chain.from_iterable(one_way_target_entrance_pools.values()):
            if remaining_target.replaces and remaining_target.replaces in replaced_entrances:
                delete_target_entrance(remaining_target)
        # Remove priority targets if any placed entrances point at their region(s).
        for key, (regions, _) in priority_entrance_table.items():
            if key in one_way_priorities:
                for entrance in placed_entrances:
                    if entrance.connected_region and entrance.connected_region.name in regions:
                        del one_way_priorities[key]
                        break

        # Place priority entrances
        placed_one_way_entrances = shuffle_one_way_priority_entrances(worlds, world, one_way_priorities, one_way_entrance_pools, one_way_target_entrance_pools, locations_to_ensure_reachable, complete_itempool, retry_count=2)

        # Delete all targets that we just placed from one way target pools so multiple one way entrances don't use the same target
        replaced_entrances = [entrance.replaces for entrance in chain.from_iterable(one_way_entrance_pools.values())]
        for remaining_target in chain.from_iterable(one_way_target_entrance_pools.values()):
            if remaining_target.replaces in replaced_entrances:
                delete_target_entrance(remaining_target)

        # Shuffle all entrances among the pools to shuffle
        for pool_type, entrance_pool in one_way_entrance_pools.items():
            placed_one_way_entrances += shuffle_entrance_pool(world, worlds, entrance_pool, one_way_target_entrance_pools[pool_type], locations_to_ensure_reachable, check_all=True, placed_one_way_entrances=placed_one_way_entrances)
            # Delete all targets that we just placed from other one way target pools so multiple one way entrances don't use the same target
            replaced_entrances = [entrance.replaces for entrance in entrance_pool]
            for remaining_target in chain.from_iterable(one_way_target_entrance_pools.values()):
                if remaining_target.replaces in replaced_entrances:
                    delete_target_entrance(remaining_target)
            # Delete all unused extra targets after placing a one way pool, since the unused targets won't ever be replaced
            for unused_target in one_way_target_entrance_pools[pool_type]:
                delete_target_entrance(unused_target)

        for pool_type, entrance_pool in entrance_pools.items():
            shuffle_entrance_pool(world, worlds, entrance_pool, target_entrance_pools[pool_type], locations_to_ensure_reachable, placed_one_way_entrances=placed_one_way_entrances)

        # Determine blue warp targets
        # if a boss room is inside a boss door, make the blue warp go outside the dungeon's entrance
        boss_exits = {
            'Queen Gohma Boss Room -> Deku Tree Before Boss': world.get_entrance('Deku Tree Lobby -> KF Outside Deku Tree'),
            'King Dodongo Boss Room -> Dodongos Cavern Mouth': world.get_entrance('Dodongos Cavern Beginning -> Death Mountain'),
            'Barinade Boss Room -> Jabu Jabus Belly Before Boss': world.get_entrance('Jabu Jabus Belly Beginning -> Zoras Fountain'),
            'Phantom Ganon Boss Room -> Forest Temple Before Boss': world.get_entrance('Forest Temple Lobby -> SFM Forest Temple Entrance Ledge'),
            'Volvagia Boss Room -> Fire Temple Before Boss': world.get_entrance('Fire Temple Lower -> DMC Fire Temple Entrance'),
            'Morpha Boss Room -> Water Temple Before Boss': world.get_entrance('Water Temple Lobby -> Lake Hylia'),
            'Bongo Bongo Boss Room -> Shadow Temple Before Boss': world.get_entrance('Shadow Temple Entryway -> Graveyard Warp Pad Region'),
            'Twinrova Boss Room -> Spirit Temple Before Boss': world.get_entrance('Spirit Temple Lobby -> Desert Colossus From Spirit Lobby'),
        }
        # if a boss room is inside a dungeon entrance (or inside a dungeon which is inside a dungeon entrance), make the blue warp go to that dungeon's blue warp target
        dungeon_exits = {
            'Deku Tree Lobby -> KF Outside Deku Tree': world.get_entrance('Queen Gohma Boss Room -> KF Outside Deku Tree'),
            'Dodongos Cavern Beginning -> Death Mountain': world.get_entrance('King Dodongo Boss Room -> Death Mountain'),
            'Jabu Jabus Belly Beginning -> Zoras Fountain': world.get_entrance('Barinade Boss Room -> Zoras Fountain'),
            'Forest Temple Lobby -> SFM Forest Temple Entrance Ledge': world.get_entrance('Phantom Ganon Boss Room -> Sacred Forest Meadow'),
            'Fire Temple Lower -> DMC Fire Temple Entrance': world.get_entrance('Volvagia Boss Room -> DMC Central Local'),
            'Water Temple Lobby -> Lake Hylia': world.get_entrance('Morpha Boss Room -> Lake Hylia'),
            'Shadow Temple Entryway -> Graveyard Warp Pad Region': world.get_entrance('Bongo Bongo Boss Room -> Graveyard Warp Pad Region'),
            'Spirit Temple Lobby -> Desert Colossus From Spirit Lobby': world.get_entrance('Twinrova Boss Room -> Desert Colossus'),
        }

        for (blue_warp, boss_door_exit) in (
            (world.get_entrance('Queen Gohma Boss Room -> KF Outside Deku Tree'), world.get_entrance('Queen Gohma Boss Room -> Deku Tree Before Boss')),
            (world.get_entrance('King Dodongo Boss Room -> Death Mountain'), world.get_entrance('King Dodongo Boss Room -> Dodongos Cavern Mouth')),
            (world.get_entrance('Barinade Boss Room -> Zoras Fountain'), world.get_entrance('Barinade Boss Room -> Jabu Jabus Belly Before Boss')),
            (world.get_entrance('Phantom Ganon Boss Room -> Sacred Forest Meadow'), world.get_entrance('Phantom Ganon Boss Room -> Forest Temple Before Boss')),
            (world.get_entrance('Volvagia Boss Room -> DMC Central Local'), world.get_entrance('Volvagia Boss Room -> Fire Temple Before Boss')),
            (world.get_entrance('Morpha Boss Room -> Lake Hylia'), world.get_entrance('Morpha Boss Room -> Water Temple Before Boss')),
            (world.get_entrance('Bongo Bongo Boss Room -> Graveyard Warp Pad Region'), world.get_entrance('Bongo Bongo Boss Room -> Shadow Temple Before Boss')),
            (world.get_entrance('Twinrova Boss Room -> Desert Colossus'), world.get_entrance('Twinrova Boss Room -> Spirit Temple Before Boss')),
        ):
            target = boss_door_exit.replaces or boss_door_exit
            if True: #TODO not world.settings.decouple_entrances
                while target.name in boss_exits:
                    target = boss_exits[target.name].replaces or boss_exits[target.name]
                if target.name in dungeon_exits:
                    target = dungeon_exits[target.name]
            blue_warp.connect(world.get_region(target.name.split(' -> ')[1]))
            blue_warp.replaces = target


    # Multiple checks after shuffling entrances to make sure everything went fine
    max_search = Search.max_explore([world.state for world in worlds], complete_itempool)

    # Check that all shuffled entrances are properly connected to a region
    for world in worlds:
        for entrance in world.get_shuffled_entrances():
            if entrance.connected_region is None:
                logging.getLogger('').error('%s was shuffled but still isn\'t connected to any region [World %d]', entrance, world.id)
            if entrance.replaces is None:
                logging.getLogger('').error('%s was shuffled but still doesn\'t replace any entrance [World %d]', entrance, world.id)
        if len(world.get_region('Root Exits').exits) > 8:
            for exit in world.get_region('Root Exits').exits:
                logging.getLogger('').error('Root Exit: %s, Connected Region: %s', exit, exit.connected_region)
            raise RuntimeError('Something went wrong, Root has too many entrances left after shuffling entrances [World %d]' % world.id)

    # Check for game beatability in all worlds
    if not max_search.can_beat_game(False):
        raise EntranceShuffleError('Cannot beat game!')

    # Validate the worlds one last time to ensure all special conditions are still valid
    for world in worlds:
        try:
            validate_world(world, worlds, None, locations_to_ensure_reachable, complete_itempool, placed_one_way_entrances=placed_one_way_entrances)
        except EntranceShuffleError as error:
            raise EntranceShuffleError('Worlds are not valid after shuffling entrances, Reason: %s' % error)


def shuffle_one_way_priority_entrances(worlds: list[World], world: World, one_way_priorities: dict[str, tuple[list[str], list[str]]],
                                       one_way_entrance_pools: dict[str, list[Entrance]], one_way_target_entrance_pools: dict[str, list[Entrance]],
                                       locations_to_ensure_reachable: Iterable[Location], complete_itempool: list[Item],
                                       retry_count: int = 2) -> list[tuple[Entrance, Entrance]]:
    while retry_count:
        retry_count -= 1
        rollbacks = []

        try:
            for key, (regions, types) in one_way_priorities.items():
                place_one_way_priority_entrance(worlds, world, key, regions, types, rollbacks, locations_to_ensure_reachable, complete_itempool, one_way_entrance_pools, one_way_target_entrance_pools)

            # If all entrances could be connected without issues, log connections and continue
            for entrance, target in rollbacks:
                confirm_replacement(entrance, target)
            return rollbacks

        except EntranceShuffleError as error:
            for entrance, target in rollbacks:
                restore_connections(entrance, target)
            logging.getLogger('').info('Failed to place all priority one-way entrances for world %d. Will retry %d more times', world.id, retry_count)
            logging.getLogger('').info('\t%s' % error)

    if world.settings.custom_seed:
        raise EntranceShuffleError('Entrance placement attempt count exceeded for world %d. Ensure the \"Seed\" field is empty and retry a few times.' % world.id)
    if world.settings.distribution_file:
        raise EntranceShuffleError('Entrance placement attempt count exceeded for world %d. Some entrances in the Plandomizer File may have to be changed to create a valid seed. Reach out to Support on Discord for help.' % world.id)
    raise EntranceShuffleError('Entrance placement attempt count exceeded for world %d. Retry a few times or reach out to Support on Discord for help.' % world.id)


# Shuffle all entrances within a provided pool
def shuffle_entrance_pool(world: World, worlds: list[World], entrance_pool: list[Entrance], target_entrances: list[Entrance],
                          locations_to_ensure_reachable: Iterable[Location], check_all: bool = False, retry_count: int = 20,
                          placed_one_way_entrances: Optional[list[tuple[Entrance, Entrance]]] = None) -> list[tuple[Entrance, Entrance]]:
    if placed_one_way_entrances is None:
        placed_one_way_entrances = []
    # Split entrances between those that have requirements (restrictive) and those that do not (soft). These are primarily age or time of day requirements.
    restrictive_entrances, soft_entrances = split_entrances_by_requirements(worlds, entrance_pool, target_entrances)

    while retry_count:
        retry_count -= 1
        rollbacks = []

        try:
            # Shuffle restrictive entrances first while more regions are available in order to heavily reduce the chances of the placement failing.
            shuffle_entrances(worlds, restrictive_entrances, target_entrances, rollbacks, locations_to_ensure_reachable, placed_one_way_entrances=placed_one_way_entrances)

            # Shuffle the rest of the entrances, we don't have to check for beatability/reachability of locations when placing those, unless specified otherwise
            if check_all:
                shuffle_entrances(worlds, soft_entrances, target_entrances, rollbacks, locations_to_ensure_reachable, placed_one_way_entrances=placed_one_way_entrances)
            else:
                shuffle_entrances(worlds, soft_entrances, target_entrances, rollbacks, placed_one_way_entrances=placed_one_way_entrances)

            # Fully validate the resulting world to ensure everything is still fine after shuffling this pool
            complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]
            validate_world(world, worlds, None, locations_to_ensure_reachable, complete_itempool, placed_one_way_entrances=placed_one_way_entrances)

            # If all entrances could be connected without issues, log connections and continue
            for entrance, target in rollbacks:
                confirm_replacement(entrance, target)
            return rollbacks

        except EntranceShuffleError as error:
            for entrance, target in rollbacks:
                restore_connections(entrance, target)
            logging.getLogger('').info('Failed to place all entrances in a pool for world %d. Will retry %d more times', entrance_pool[0].world.id, retry_count)
            logging.getLogger('').info('\t%s' % error)

    if world.settings.custom_seed:
        raise EntranceShuffleError('Entrance placement attempt count exceeded for world %d. Ensure the \"Seed\" field is empty and retry a few times.' % world.id)
    if world.settings.distribution_file:
        raise EntranceShuffleError('Entrance placement attempt count exceeded for world %d. Some entrances in the Plandomizer File may have to be changed to create a valid seed. Reach out to Support on Discord for help.' % world.id)
    raise EntranceShuffleError('Entrance placement attempt count exceeded for world %d. Retry a few times or reach out to Support on Discord for help.' % world.id)


# Split entrances based on their requirements to figure out how each entrance should be handled when shuffling them
def split_entrances_by_requirements(worlds: list[World], entrances_to_split: list[Entrance], assumed_entrances: list[Entrance]) -> tuple[list[Entrance], list[Entrance]]:
    # First, disconnect all root assumed entrances and save which regions they were originally connected to, so we can reconnect them later
    original_connected_regions = {}
    entrances_to_disconnect = set(assumed_entrances).union(entrance.reverse for entrance in assumed_entrances if entrance.reverse)
    for entrance in entrances_to_disconnect:
        if entrance.connected_region:
            original_connected_regions[entrance] = entrance.disconnect()

    # Generate the states with all assumed entrances disconnected
    # This ensures no assumed entrances corresponding to those we are shuffling are required in order for an entrance to be reachable as some age/tod
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]
    max_search = Search.max_explore([world.state for world in worlds], complete_itempool)

    restrictive_entrances = []
    soft_entrances = []

    for entrance in entrances_to_split:
        # Here, we find entrances that may be unreachable under certain conditions
        if not max_search.spot_access(entrance, age='both', tod=TimeOfDay.ALL):
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


def replace_entrance(worlds: list[World], entrance: Entrance, target: Entrance, rollbacks: list[tuple[Entrance, Entrance]],
                     locations_to_ensure_reachable: Iterable[Location], itempool: list[Item], placed_one_way_entrances: Optional[list[tuple[Entrance, Entrance]]] = None) -> bool:
    if placed_one_way_entrances is None:
        placed_one_way_entrances = []
    try:
        check_entrances_compatibility(entrance, target, rollbacks, placed_one_way_entrances)
        change_connections(entrance, target)
        validate_world(entrance.world, worlds, entrance, locations_to_ensure_reachable, itempool, placed_one_way_entrances=placed_one_way_entrances)
        rollbacks.append((entrance, target))
        return True
    except EntranceShuffleError as error:
        # If the entrance can't be placed there, log a debug message and change the connections back to what they were previously
        logging.getLogger('').debug('Failed to connect %s To %s (Reason: %s) [World %d]',
                                    entrance, entrance.connected_region or target.connected_region, error, entrance.world.id)
        if entrance.connected_region:
            restore_connections(entrance, target)
    return False


# Connect one random entrance from entrance pools to one random target in the respective target pool.
# Entrance chosen will have one of the allowed types.
# Target chosen will lead to one of the allowed regions.
def place_one_way_priority_entrance(worlds: list[World], world: World, priority_name: str, allowed_regions: Container[str], allowed_types: Iterable[str],
                                    rollbacks: list[tuple[Entrance, Entrance]], locations_to_ensure_reachable: Iterable[Location], complete_itempool: list[Item],
                                    one_way_entrance_pools: dict[str, list[Entrance]], one_way_target_entrance_pools: dict[str, list[Entrance]]) -> None:
    # Combine the entrances for allowed types in one list.
    # Shuffle this list.
    # Pick the first one not already set, not adult spawn, that has a valid target entrance.
    # Assemble then clear entrances from the pool and target pools as appropriate.
    avail_pool = list(chain.from_iterable(one_way_entrance_pools[t] for t in allowed_types if t in one_way_entrance_pools))
    random.shuffle(avail_pool)
    for entrance in avail_pool:
        if entrance.replaces:
            continue
        # Only allow Adult Spawn as sole Nocturne access if hints != mask.
        # Otherwise, child access is required here (adult access assumed or guaranteed later).
        if entrance.parent_region.name == 'Adult Spawn':
            if priority_name != 'Nocturne' or entrance.world.settings.hints == "mask":
                continue
        # If not shuffling dungeons, Nocturne requires adult access.
        if not entrance.world.shuffle_dungeon_entrances and priority_name == 'Nocturne':
            if entrance.type not in ('OverworldOneWay', 'WarpSong') and entrance.parent_region.name != 'Adult Spawn':
                continue
        for target in one_way_target_entrance_pools[entrance.type]:
            if target.connected_region and target.connected_region.name in allowed_regions:
                if replace_entrance(worlds, entrance, target, rollbacks, locations_to_ensure_reachable, complete_itempool):
                    logging.getLogger('').debug(f'Priority placement for {priority_name}: placing {entrance} as {target}')
                    return
    raise EntranceShuffleError(f'Unable to place priority one-way entrance for {priority_name} [World {world.id}].')


# Shuffle entrances by placing them instead of entrances in the provided target entrances list
# While shuffling entrances, the algorithm will ensure worlds are still valid based on multiple criterias
def shuffle_entrances(worlds: list[World], entrances: list[Entrance], target_entrances: list[Entrance], rollbacks: list[tuple[Entrance, Entrance]],
                      locations_to_ensure_reachable: Iterable[Location] = (), placed_one_way_entrances: Optional[list[tuple[Entrance, Entrance]]] = None) -> None:
    if placed_one_way_entrances is None:
        placed_one_way_entrances = []
    # Retrieve all items in the itempool, all worlds included
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]

    random.shuffle(entrances)

    # Place all entrances in the pool, validating worlds during every placement
    for entrance in entrances:
        if entrance.connected_region is not None:
            continue
        random.shuffle(target_entrances)

        for target in target_entrances:
            if target.connected_region is None:
                continue

            if replace_entrance(worlds, entrance, target, rollbacks, locations_to_ensure_reachable, complete_itempool, placed_one_way_entrances=placed_one_way_entrances):
                break

        if entrance.connected_region is None:
            raise EntranceShuffleError('No more valid entrances to replace with %s in world %d' % (entrance, entrance.world.id))


# Check and validate that an entrance is compatible to replace a specific target
def check_entrances_compatibility(entrance: Entrance, target: Entrance, rollbacks: list[tuple[Entrance, Entrance]] = (),
                                  placed_one_way_entrances: Optional[list[tuple[Entrance, Entrance]]] = None) -> None:
    if placed_one_way_entrances is None:
        placed_one_way_entrances = []
    # An entrance shouldn't be connected to its own scene, so we fail in that situation
    if entrance.parent_region.get_scene() and entrance.parent_region.get_scene() == target.connected_region.get_scene():
        raise EntranceShuffleError('Self scene connections are forbidden')

    # One way entrances shouldn't lead to the same hint area as other already chosen one way entrances
    if entrance.type in ('OverworldOneWay', 'OwlDrop', 'Spawn', 'WarpSong'):
        try:
            hint_area = HintArea.at(target.connected_region)
        except HintAreaNotFound:
            pass # not connected to a hint area yet, will be checked when shuffling two-way entrances
        else:
            # Check all already placed entrances of the same type (including priority entrances placed separately)
            for rollback in (*rollbacks, *placed_one_way_entrances):
                try:
                    placed_entrance = rollback[0]
                    if entrance.type == placed_entrance.type and HintArea.at(placed_entrance.connected_region) == hint_area:
                        raise EntranceShuffleError(f'Another {entrance.type} entrance already leads to {hint_area}')
                except HintAreaNotFound:
                    pass


# Validate the provided worlds' structures, raising an error if it's not valid based on our criterias
def validate_world(world: World, worlds: list[World], entrance_placed: Optional[Entrance], locations_to_ensure_reachable: Iterable[Location],
                   itempool: list[Item], placed_one_way_entrances: Optional[list[tuple[Entrance, Entrance]]] = None) -> None:
    if placed_one_way_entrances is None:
        placed_one_way_entrances = []
    # For various reasons, we don't want the player to end up through certain entrances as the wrong age
    # This means we need to hard check that none of the relevant entrances are ever reachable as that age
    # This is mostly relevant when shuffling special interiors (such as windmill or kak potion shop)
    # Warp Songs and Overworld Spawns can also end up inside certain indoors so those need to be handled as well
    # Allowing child to enter Spirit from the boss would severely complicate key logic
    CHILD_FORBIDDEN = ['OGC Great Fairy Fountain -> Castle Grounds', 'GV Carpenter Tent -> GV Fortress Side', 'Ganons Castle Lobby -> Castle Grounds', 'Bongo Bongo Boss Room -> Shadow Temple Before Boss', 'Twinrova Boss Room -> Spirit Temple Before Boss']
    ADULT_FORBIDDEN = ['HC Great Fairy Fountain -> Castle Grounds', 'HC Storms Grotto -> Castle Grounds', 'Bongo Bongo Boss Room -> Shadow Temple Before Boss', 'Twinrova Boss Room -> Spirit Temple Before Boss']
    if world.dungeon_mq['Forest Temple'] and 'Forest Temple' in world.settings.dungeon_shortcuts:
        CHILD_FORBIDDEN.append('Phantom Ganon Boss Room -> Forest Temple Before Boss')
        ADULT_FORBIDDEN.append('Phantom Ganon Boss Room -> Forest Temple Before Boss')

    for entrance in world.get_shufflable_entrances():
        if entrance.shuffled:
            if entrance.replaces:
                if entrance.replaces.name in CHILD_FORBIDDEN and not entrance_unreachable_as(entrance, 'child', already_checked=[entrance.replaces.reverse]):
                    raise EntranceShuffleError('%s is replaced by an entrance with a potential child access' % entrance.replaces.name)
                elif entrance.replaces.name in ADULT_FORBIDDEN and not entrance_unreachable_as(entrance, 'adult', already_checked=[entrance.replaces.reverse]):
                    raise EntranceShuffleError('%s is replaced by an entrance with a potential adult access' % entrance.replaces.name)
        else:
            if entrance.name in CHILD_FORBIDDEN and not entrance_unreachable_as(entrance, 'child', already_checked=[entrance.reverse]):
                raise EntranceShuffleError('%s is potentially accessible as child' % entrance.name)
            elif entrance.name in ADULT_FORBIDDEN and not entrance_unreachable_as(entrance, 'adult', already_checked=[entrance.reverse]):
                raise EntranceShuffleError('%s is potentially accessible as adult' % entrance.name)

    if locations_to_ensure_reachable:
        max_search = Search.max_explore([w.state for w in worlds], itempool)
        if world.check_beatable_only:
            if worlds[0].settings.reachable_locations == 'goals':
                # If this entrance is required for a goal, it must be placed somewhere reachable.
                # We also need to check to make sure the game is beatable, since custom goals might not imply that.
                predicate = lambda state: state.won() and state.has_all_item_goals()
            else:
                # If the game is not beatable without this entrance, it must be placed somewhere reachable.
                predicate = State.won
            perform_access_check = not max_search.can_beat_game(scan_for_items=False, predicate=predicate)
        else:
            # All entrances must be placed somewhere reachable.
            perform_access_check = True
        if perform_access_check:
            max_search.visit_locations(locations_to_ensure_reachable)
            for location in locations_to_ensure_reachable:
                if not max_search.visited(location):
                    raise EntranceShuffleError('%s is unreachable' % location.name)

    if (
        world.shuffle_interior_entrances and (
            (world.dungeon_rewards_hinted and (world.mixed_pools_bosses or world.settings.shuffle_dungeon_rewards in ('regional', 'overworld', 'anywhere')))
            or any(hint_type in world.settings.misc_hints for hint_type in misc_item_hint_table) or world.settings.hints != 'none'
        ) and (entrance_placed is None or entrance_placed.type in ['Interior', 'SpecialInterior'])
    ):
        # Ensure Kak Potion Shop entrances are in the same hint area so there is no ambiguity as to which entrance is used for hints
        potion_front_entrance = get_entrance_replacing(world.get_region('Kak Potion Shop Front'), 'Kakariko Village -> Kak Potion Shop Front')
        potion_back_entrance = get_entrance_replacing(world.get_region('Kak Potion Shop Back'), 'Kak Backyard -> Kak Potion Shop Back')
        if potion_front_entrance is not None and potion_back_entrance is not None and not same_hint_area(potion_front_entrance, potion_back_entrance):
            raise EntranceShuffleError('Kak Potion Shop entrances are not in the same hint area')

        # When cows are shuffled, ensure the same thing for Impa's House, since the cow is reachable from both sides
        if world.settings.shuffle_cows:
            impas_front_entrance = get_entrance_replacing(world.get_region('Kak Impas House'), 'Kakariko Village -> Kak Impas House')
            impas_back_entrance = get_entrance_replacing(world.get_region('Kak Impas House Back'), 'Kak Impas Ledge -> Kak Impas House Back')
            if impas_front_entrance is not None and impas_back_entrance is not None and not same_hint_area(impas_front_entrance, impas_back_entrance):
                raise EntranceShuffleError('Kak Impas House entrances are not in the same hint area')

    if (world.shuffle_special_interior_entrances or world.settings.shuffle_overworld_entrances or world.settings.spawn_positions) and \
       (entrance_placed == None or entrance_placed.type in ('SpecialInterior', 'Hideout', 'Overworld', 'OverworldOneWay', 'Spawn', 'WarpSong', 'OwlDrop')):
        # At least one valid starting region with all basic refills should be reachable without using any items at the beginning of the seed
        # Note this creates new empty states rather than reuse the worlds' states (which already have starting items)
        no_items_search = Search([State(w) for w in worlds])

        valid_starting_regions = ('Kokiri Forest', 'Kakariko Village')
        if not any(no_items_search.can_reach(world.get_region(region)) for region in valid_starting_regions):
            raise EntranceShuffleError('Invalid starting area')

        # Check that a region where time passes is always reachable as both ages without having collected any items
        time_travel_search = Search.with_items([w.state for w in worlds], [ItemFactory('Time Travel', world=w) for w in worlds])

        if not (any(region for region in time_travel_search.reachable_regions('child') if region.time_passes and region.world == world) and
                any(region for region in time_travel_search.reachable_regions('adult') if region.time_passes and region.world == world)):
            raise EntranceShuffleError('Time passing is not guaranteed as both ages')

        # The player should be able to get back to ToT after going through time, without having collected any items
        # This is important to ensure that the player never loses access to the pedestal after going through time
        if world.settings.starting_age == 'child' and not time_travel_search.can_reach(world.get_region('Temple of Time'), age='adult'):
            raise EntranceShuffleError('Path to Temple of Time as adult is not guaranteed')
        elif world.settings.starting_age == 'adult' and not time_travel_search.can_reach(world.get_region('Temple of Time'), age='child'):
            raise EntranceShuffleError('Path to Temple of Time as child is not guaranteed')

    if (world.shuffle_interior_entrances or world.settings.shuffle_overworld_entrances) and \
       (entrance_placed == None or entrance_placed.type in ('Interior', 'SpecialInterior', 'Hideout', 'Overworld', 'OverworldOneWay', 'Spawn', 'WarpSong', 'OwlDrop')):
        # The Big Poe Shop should always be accessible as adult without the need to use any bottles
        # This is important to ensure that players can never lock their only bottles by filling them with Big Poes they can't sell
        # We can use starting items in this check as long as there are no exits requiring the use of a bottle without refills
        time_travel_search = Search.with_items([w.state for w in worlds], [ItemFactory('Time Travel', world=w) for w in worlds])

        if not time_travel_search.can_reach(world.get_region('Market Guard House'), age='adult'):
            raise EntranceShuffleError('Big Poe Shop access is not guaranteed as adult')

    # placing a two-way entrance can connect a one-way entrance to a hint area,
    # so the restriction also needs to be checked here
    for idx1 in range(len(placed_one_way_entrances)):
        try:
            entrance1 = placed_one_way_entrances[idx1][0]
            hint_area1 = HintArea.at(entrance1.connected_region)
        except HintAreaNotFound:
            pass
        else:
            for idx2 in range(idx1):
                try:
                    entrance2 = placed_one_way_entrances[idx2][0]
                    if entrance1.type == entrance2.type and hint_area1 == HintArea.at(entrance2.connected_region):
                        raise EntranceShuffleError(f'Multiple {entrance1.type} entrances lead to {hint_area1}')
                except HintAreaNotFound:
                    pass


# Returns whether or not we can affirm the entrance can never be accessed as the given age
def entrance_unreachable_as(entrance: Entrance, age: str, already_checked: Optional[list[Entrance]] = None) -> bool:
    if already_checked is None:
        already_checked = []

    already_checked.append(entrance)

    # The following cases determine when we say an entrance is not safe to affirm unreachable as the given age
    if entrance.type in ('WarpSong', 'OverworldOneWay', 'Overworld'):
        # Note that we consider all overworld entrances as potentially accessible as both ages, to be completely safe
        return False
    elif entrance.type == 'OwlDrop':
        return age == 'adult'
    elif entrance.name == 'Child Spawn -> KF Links House':
        return age == 'adult'
    elif entrance.name == 'Adult Spawn -> Temple of Time':
        return age == 'child'

    # Other entrances such as Interior, Dungeon or Grotto are fine unless they have a parent which is one of the above cases
    # Recursively check parent entrances to verify that they are also not reachable as the wrong age
    for parent_entrance in entrance.parent_region.entrances:
        if parent_entrance in already_checked: continue
        unreachable = entrance_unreachable_as(parent_entrance, age, already_checked)
        if not unreachable:
            return False

    return True


# Returns whether two entrances are in the same hint area
def same_hint_area(first: Entrance, second: Entrance) -> bool:
    try:
        return HintArea.at(first) == HintArea.at(second)
    except HintAreaNotFound:
        return False


# Shorthand function to find an entrance with the requested name leading to a specific region
def get_entrance_replacing(region: Region, entrance_name: str) -> Optional[Entrance]:
    original_entrance = region.world.get_entrance(entrance_name)

    if not original_entrance.shuffled:
        return original_entrance

    try:
        return next(filter(lambda entrance:
            entrance.replaces and entrance.replaces.name == entrance_name
            and entrance.parent_region and entrance.parent_region.name != 'Root Exits'
            and entrance.type not in ('OverworldOneWay', 'OwlDrop', 'Spawn', 'WarpSong', 'BlueWarp'),
        region.entrances))
    except StopIteration:
        return None


# Change connections between an entrance and a target assumed entrance, in order to test the connections afterwards if necessary
def change_connections(entrance: Entrance, target_entrance: Entrance) -> None:
    entrance.connect(target_entrance.disconnect())
    entrance.replaces = target_entrance.replaces
    if entrance.reverse:
        target_entrance.replaces.reverse.connect(entrance.reverse.assumed.disconnect())
        target_entrance.replaces.reverse.replaces = entrance.reverse


# Restore connections between an entrance and a target assumed entrance
def restore_connections(entrance: Entrance, target_entrance: Entrance) -> None:
    target_entrance.connect(entrance.disconnect())
    entrance.replaces = None
    if entrance.reverse:
        entrance.reverse.assumed.connect(target_entrance.replaces.reverse.disconnect())
        target_entrance.replaces.reverse.replaces = None


# Confirm the replacement of a target entrance by a new entrance, logging the new connections and completely deleting the target entrances
def confirm_replacement(entrance: Entrance, target_entrance: Entrance) -> None:
    delete_target_entrance(target_entrance)
    logging.getLogger('').debug('Connected %s To %s [World %d]', entrance, entrance.connected_region, entrance.world.id)
    if entrance.reverse:
        replaced_reverse = target_entrance.replaces.reverse
        delete_target_entrance(entrance.reverse.assumed)
        logging.getLogger('').debug('Connected %s To %s [World %d]', replaced_reverse, replaced_reverse.connected_region, replaced_reverse.world.id)


# Delete an assumed target entrance, by disconnecting it if needed and removing it from its parent region
def delete_target_entrance(target_entrance: Entrance) -> None:
    if target_entrance.connected_region is not None:
        target_entrance.disconnect()
    if target_entrance.parent_region is not None:
        target_entrance.parent_region.exits.remove(target_entrance)
        target_entrance.parent_region = None
