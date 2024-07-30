from __future__ import annotations
import itertools
import json
import logging
import os
import random
import sys
import urllib.request
from collections import OrderedDict, defaultdict
from collections.abc import Callable, Iterable
from enum import Enum
from typing import TYPE_CHECKING, Optional
from urllib.error import URLError, HTTPError

from HintList import Hint, get_hint, get_multi, get_hint_group, get_upgrade_hint_list, hint_exclusions, \
    misc_item_hint_table, misc_location_hint_table
from Item import Item, make_event_item
from ItemList import REWARD_COLORS
from Messages import Message, COLOR_MAP, update_message_by_id
from Region import Region
from Search import Search
from TextBox import line_wrap
from Utils import data_path

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    TypeAlias = str

if TYPE_CHECKING:
    from Dungeon import Dungeon
    from Entrance import Entrance
    from Goals import GoalCategory
    from Location import Location
    from Spoiler import Spoiler
    from World import World

Spot: TypeAlias = "Entrance | Location | Region"
HintReturn: TypeAlias = "Optional[tuple[GossipText, Optional[list[Location]]]]"
HintFunc: TypeAlias = "Callable[[Spoiler, World, set[str]], HintReturn]"
BarrenFunc: TypeAlias = "Callable[[Spoiler, World, set[str], set[str]], HintReturn]"

bingoBottlesForHints: set[str] = {
    "Bottle", "Bottle with Red Potion", "Bottle with Green Potion", "Bottle with Blue Potion",
    "Bottle with Fairy", "Bottle with Fish", "Bottle with Blue Fire", "Bottle with Bugs",
    "Bottle with Big Poe", "Bottle with Poe",
}

defaultHintDists: list[str] = [
    'balanced.json',
    'bingo.json',
    'chaos.json',
    'chaos_no_goal.json',
    'coop.json',
    'ddr.json',
    'important_checks.json',
    'league.json',
    'mw_path.json',
    'mw_woth.json',
    'scrubs.json',
    'strong.json',
    'tournament.json',
    'useless.json',
    'very_strong.json',
    'very_strong_magic.json',
    'weekly.json',
]

unHintableWothItems: set[str] = {*REWARD_COLORS, 'Triforce Piece', 'Gold Skulltula Token', 'Piece of Heart', 'Piece of Heart (Treasure Chest Game)', 'Heart Container'}


class RegionRestriction(Enum):
    NONE = 0,
    DUNGEON = 1,
    OVERWORLD = 2,


class GossipStone:
    def __init__(self, name: str, location: str) -> None:
        self.name: str = name
        self.location: str = location
        self.reachable: bool = True


class GossipText:
    def __init__(self, text: str, colors: Optional[list[str]] = None, hinted_locations: Optional[list[str]] = None,
                 hinted_items: Optional[list[str]] = None, prefix: str = "They say that ", capitalize: bool = True) -> None:
        text = prefix + text
        if capitalize:
            text = text[:1].upper() + text[1:]
        self.text: str = text
        self.colors: Optional[list[str]] = colors
        self.hinted_locations: Optional[list[str]] = hinted_locations
        self.hinted_items: Optional[list[str]] = hinted_items

    def to_json(self) -> dict:
        return {'text': self.text, 'colors': self.colors, 'hinted_locations': self.hinted_locations, 'hinted_items': self.hinted_items}

    def __str__(self) -> str:
        return get_raw_text(line_wrap(color_text(self)))


#   Abbreviations
#       DMC     Death Mountain Crater
#       DMT     Death Mountain Trail
#       GC      Goron City
#       GV      Gerudo Valley
#       HC      Hyrule Castle
#       HF      Hyrule Field
#       KF      Kokiri Forest
#       LH      Lake Hylia
#       LW      Lost Woods
#       SFM     Sacred Forest Meadow
#       ToT     Temple of Time
#       ZD      Zora's Domain
#       ZF      Zora's Fountain
#       ZR      Zora's River

gossipLocations: dict[int, GossipStone] = {
    0x0405: GossipStone('DMC (Bombable Wall)',              'DMC Gossip Stone'),
    0x0404: GossipStone('DMT (Biggoron)',                   'DMT Gossip Stone'),
    0x041A: GossipStone('Colossus (Spirit Temple)',         'Colossus Gossip Stone'),
    0x0414: GossipStone('Dodongos Cavern (Bombable Wall)',  'Dodongos Cavern Gossip Stone'),
    0x0411: GossipStone('GV (Waterfall)',                   'GV Gossip Stone'),
    0x0415: GossipStone('GC (Maze)',                        'GC Maze Gossip Stone'),
    0x0419: GossipStone('GC (Medigoron)',                   'GC Medigoron Gossip Stone'),
    0x040A: GossipStone('Graveyard (Shadow Temple)',        'Graveyard Gossip Stone'),
    0x0412: GossipStone('HC (Malon)',                       'HC Malon Gossip Stone'),
    0x040B: GossipStone('HC (Rock Wall)',                   'HC Rock Wall Gossip Stone'),
    0x0413: GossipStone('HC (Storms Grotto)',               'HC Storms Grotto Gossip Stone'),
    0x041F: GossipStone('KF (Deku Tree Left)',              'KF Deku Tree Gossip Stone (Left)'),
    0x0420: GossipStone('KF (Deku Tree Right)',             'KF Deku Tree Gossip Stone (Right)'),
    0x041E: GossipStone('KF (Outside Storms)',              'KF Gossip Stone'),
    0x0403: GossipStone('LH (Lab)',                         'LH Lab Gossip Stone'),
    0x040F: GossipStone('LH (Southeast Corner)',            'LH Gossip Stone (Southeast)'),
    0x0408: GossipStone('LH (Southwest Corner)',            'LH Gossip Stone (Southwest)'),
    0x041D: GossipStone('LW (Bridge)',                      'LW Gossip Stone'),
    0x0416: GossipStone('SFM (Maze Lower)',                 'SFM Maze Gossip Stone (Lower)'),
    0x0417: GossipStone('SFM (Maze Upper)',                 'SFM Maze Gossip Stone (Upper)'),
    0x041C: GossipStone('SFM (Saria)',                      'SFM Saria Gossip Stone'),
    0x0406: GossipStone('ToT (Left)',                       'ToT Gossip Stone (Left)'),
    0x0407: GossipStone('ToT (Left-Center)',                'ToT Gossip Stone (Left-Center)'),
    0x0410: GossipStone('ToT (Right)',                      'ToT Gossip Stone (Right)'),
    0x040E: GossipStone('ToT (Right-Center)',               'ToT Gossip Stone (Right-Center)'),
    0x0409: GossipStone('ZD (Mweep)',                       'ZD Gossip Stone'),
    0x0401: GossipStone('ZF (Fairy)',                       'ZF Fairy Gossip Stone'),
    0x0402: GossipStone('ZF (Jabu)',                        'ZF Jabu Gossip Stone'),
    0x040D: GossipStone('ZR (Near Grottos)',                'ZR Near Grottos Gossip Stone'),
    0x040C: GossipStone('ZR (Near Domain)',                 'ZR Near Domain Gossip Stone'),
    0x041B: GossipStone('HF (Cow Grotto)',                  'HF Cow Grotto Gossip Stone'),

    0x0430: GossipStone('HF (Near Market Grotto)',          'HF Near Market Grotto Gossip Stone'),
    0x0432: GossipStone('HF (Southeast Grotto)',            'HF Southeast Grotto Gossip Stone'),
    0x0433: GossipStone('HF (Open Grotto)',                 'HF Open Grotto Gossip Stone'),
    0x0438: GossipStone('Kak (Open Grotto)',                'Kak Open Grotto Gossip Stone'),
    0x0439: GossipStone('ZR (Open Grotto)',                 'ZR Open Grotto Gossip Stone'),
    0x043C: GossipStone('KF (Storms Grotto)',               'KF Storms Grotto Gossip Stone'),
    0x0444: GossipStone('LW (Near Shortcuts Grotto)',       'LW Near Shortcuts Grotto Gossip Stone'),
    0x0447: GossipStone('DMT (Storms Grotto)',              'DMT Storms Grotto Gossip Stone'),
    0x044A: GossipStone('DMC (Upper Grotto)',               'DMC Upper Grotto Gossip Stone'),
}

gossipLocations_reversemap: dict[str, int] = {
    stone.name: stone_id for stone_id, stone in gossipLocations.items()
}


def get_item_generic_name(item: Item) -> str:
    if item.unshuffled_dungeon_item and item.type != 'DungeonReward':
        return item.type
    else:
        return item.name


def is_restricted_dungeon_item(item: Item) -> bool:
    if item.world is None:
        return False
    return (
        ((item.map or item.compass) and item.world.settings.shuffle_mapcompass == 'dungeon') or
        (item.type == 'SmallKey' and item.world.settings.shuffle_smallkeys == 'dungeon') or
        (item.type == 'BossKey' and item.world.settings.shuffle_bosskeys == 'dungeon') or
        (item.type == 'GanonBossKey' and item.world.settings.shuffle_ganon_bosskey == 'dungeon') or
        (item.type == 'SilverRupee' and item.world.settings.shuffle_silver_rupees == 'dungeon') or
        (item.type == 'DungeonReward' and item.world.settings.shuffle_dungeon_rewards in ('vanilla', 'reward', 'dungeon'))
    )


def add_hint(spoiler: Spoiler, world: World, groups: list[list[int]], gossip_text: GossipText, count: int,
             locations: Optional[list[Location]] = None, force_reachable: bool = False, hint_type: str = None) -> bool:
    random.shuffle(groups)
    skipped_groups = []
    duplicates = []
    first = True
    success = True

    # Prevent randomizer from placing hint in removed locations for this hint type
    if 'remove_stones' in world.hint_dist_user['distribution'][hint_type]:
        removed_stones = world.hint_dist_user['distribution'][hint_type]['remove_stones']
        for group in groups:
            gossip_names = [gossipLocations[id].name for id in group]
            if any(map(lambda name: name in removed_stones, gossip_names)):
                skipped_groups.append(group)

        for group in skipped_groups:
            groups.remove(group)

    # early failure if not enough
    if len(groups) < int(count):
        return False

    # move all priority stones to the front of the list so they get picked first
    if 'priority_stones' in world.hint_dist_user['distribution'][hint_type]:
        priority_stones = world.hint_dist_user['distribution'][hint_type]['priority_stones']

        # iterate in reverse so that the top priority stone gets inserted at index 0 last
        for priority_stone in reversed(priority_stones):
            matching_groups = list(filter(lambda group: list(set([priority_stone]) & set([gossipLocations[id].name for id in group])), groups))
            if len(matching_groups) > 0:
                index = groups.index(matching_groups[0])
                priority_group = groups.pop(index)
                groups.insert(0, priority_group)

    # Randomly round up, if we have enough groups left
    total = int(random.random() + count) if len(groups) > count else int(count)
    while total:
        if groups:
            group = groups.pop(0)

            if any(map(lambda id: gossipLocations[id].reachable, group)):
                stone_names = [gossipLocations[id].location for id in group]
                stone_locations = [world.get_location(stone_name) for stone_name in stone_names]

                reachable = True
                if locations:
                    for location in locations:
                        if not any(map(lambda stone_location: can_reach_hint(spoiler.worlds, stone_location, location), stone_locations)):
                            reachable = False

                if not first or reachable:
                    if first and locations:
                        # just name the event item after the gossip stone directly
                        event_item = None
                        for i, stone_name in enumerate(stone_names):
                            # place the same event item in each location in the group
                            if event_item is None:
                                event_item = make_event_item(stone_name, stone_locations[i], event_item)
                            else:
                                make_event_item(stone_name, stone_locations[i], event_item)
                        assert event_item is not None

                        # This mostly guarantees that we don't lock the player out of an item hint
                        # by establishing a (hint -> item) -> hint -> item -> (first hint) loop
                        for location in locations:
                            location.add_rule(world.parser.parse_rule(repr(event_item.name)))

                    total -= 1
                    first = False
                    for id in group:
                        spoiler.hints[world.id][id] = gossip_text
                    # Immediately start choosing duplicates from stones we passed up earlier
                    while duplicates and total:
                        group = duplicates.pop(0)
                        total -= 1
                        for id in group:
                            spoiler.hints[world.id][id] = gossip_text
                else:
                    # Temporarily skip this stone but consider it for duplicates
                    duplicates.append(group)
            else:
                if not force_reachable:
                    # The stones are not readable at all in logic, so we ignore any kind of logic here
                    if not first:
                        total -= 1
                        for id in group:
                            spoiler.hints[world.id][id] = gossip_text
                    else:
                        # Temporarily skip this stone but consider it for duplicates
                        duplicates.append(group)
                else:
                    # If flagged to guarantee reachable, then skip
                    # If no stones are reachable, then this will place nothing
                    skipped_groups.append(group)
        else:
            # Out of groups
            if not force_reachable and len(duplicates) >= total:
                # Didn't find any appropriate stones for this hint, but maybe enough completely unreachable ones.
                # We'd rather not use reachable stones for this.
                unr = [group for group in duplicates if all(map(lambda id: not gossipLocations[id].reachable, group))]
                if len(unr) >= total:
                    duplicates = [group for group in duplicates if group not in unr[:total]]
                    for group in unr[:total]:
                        for id in group:
                            spoiler.hints[world.id][id] = gossip_text
                    # Success
                    break
            # Failure
            success = False
            break
    groups.extend(duplicates)
    groups.extend(skipped_groups)
    return success


def can_reach_hint(worlds: list[World], hint_location: Location, location: Location) -> bool:
    if location is None:
        return True

    old_item = location.item
    location.item = None
    search = Search.max_explore([world.state for world in worlds])
    location.item = old_item

    return (search.spot_access(hint_location)
            and (hint_location.type != 'HintStone' or search.state_list[location.world.id].guarantee_hint()))


def write_gossip_stone_hints(spoiler: Spoiler, world: World, messages: list[Message]) -> None:
    for id, gossip_text in spoiler.hints[world.id].items():
        update_message_by_id(messages, id, str(gossip_text), 0x23)


def filter_trailing_space(text: str) -> str:
    if text.endswith('& '):
        return text[:-1]
    else:
        return text


hintPrefixes: list[str] = [
    'a few ',
    'some ',
    'plenty of ',
    'a ',
    'an ',
    'the ',
    '',
]


def get_simple_hint_no_prefix(item: Item) -> Hint:
    hint = get_hint(item.name, True).text

    for prefix in hintPrefixes:
        if hint.startswith(prefix):
            # return without the prefix
            return hint[len(prefix):]

    # no prefex
    return hint


def color_text(gossip_text: GossipText) -> str:
    text = gossip_text.text
    colors = list(gossip_text.colors) if gossip_text.colors is not None else []
    color = 'White'

    while '#' in text:
        split_text = text.split('#', 2)
        if len(colors) > 0:
            color = colors.pop(0)

        for prefix in hintPrefixes:
            if split_text[1].startswith(prefix):
                split_text[0] += split_text[1][:len(prefix)]
                split_text[1] = split_text[1][len(prefix):]
                break

        split_text[1] = '\x05' + COLOR_MAP[color] + split_text[1] + '\x05\x40'
        text = ''.join(split_text)

    return text


class HintAreaNotFound(RuntimeError):
    pass


class HintArea(Enum):
    # internal name          prepositions        display name                  short name                color         internal dungeon name
    #                        vague     clear
    ROOT                   = 'in',     'in',     "Link's pocket",              'Free',                   'White',      None
    HYRULE_FIELD           = 'in',     'in',     'Hyrule Field',               'Hyrule Field',           'Light Blue', None
    LON_LON_RANCH          = 'at',     'at',     'Lon Lon Ranch',              'Lon Lon Ranch',          'Light Blue', None
    MARKET                 = 'in',     'in',     'the Market',                 'Market',                 'Light Blue', None
    TEMPLE_OF_TIME         = 'inside', 'inside', 'the Temple of Time',         'Temple of Time',         'Light Blue', None
    CASTLE_GROUNDS         = 'on',     'on',     'the Castle Grounds',         None,                     'Light Blue', None # required for warp songs
    HYRULE_CASTLE          = 'at',     'at',     'Hyrule Castle',              'Hyrule Castle',          'Light Blue', None
    OUTSIDE_GANONS_CASTLE  = None,     None,     "outside Ganon's Castle",     "Outside Ganon's Castle", 'Light Blue', None
    INSIDE_GANONS_CASTLE   = 'inside', None,     "inside Ganon's Castle",      "Inside Ganon's Castle",  'Light Blue', 'Ganons Castle'
    GANONDORFS_CHAMBER     = 'in',     'in',     "Ganondorf's Chamber",        "Ganondorf's Chamber",    'Light Blue', None
    KOKIRI_FOREST          = 'in',     'in',     'Kokiri Forest',              "Kokiri Forest",          'Green',      None
    DEKU_TREE              = 'inside', 'inside', 'the Deku Tree',              "Deku Tree",              'Green',      'Deku Tree'
    LOST_WOODS             = 'in',     'in',     'the Lost Woods',             "Lost Woods",             'Green',      None
    SACRED_FOREST_MEADOW   = 'at',     'at',     'the Sacred Forest Meadow',   "Sacred Forest Meadow",   'Green',      None
    FOREST_TEMPLE          = 'in',     'in',     'the Forest Temple',          "Forest Temple",          'Green',      'Forest Temple'
    DEATH_MOUNTAIN_TRAIL   = 'on',     'on',     'the Death Mountain Trail',   "Death Mountain Trail",   'Red',        None
    DODONGOS_CAVERN        = 'within', 'in',     "Dodongo's Cavern",           "Dodongo's Cavern",       'Red',        'Dodongos Cavern'
    GORON_CITY             = 'in',     'in',     'Goron City',                 "Goron City",             'Red',        None
    DEATH_MOUNTAIN_CRATER  = 'in',     'in',     'the Death Mountain Crater',  "Death Mountain Crater",  'Red',        None
    FIRE_TEMPLE            = 'on',     'in',     'the Fire Temple',            "Fire Temple",            'Red',        'Fire Temple'
    ZORA_RIVER             = 'at',     'at',     "Zora's River",               "Zora's River",           'Blue',       None
    ZORAS_DOMAIN           = 'at',     'at',     "Zora's Domain",              "Zora's Domain",          'Blue',       None
    ZORAS_FOUNTAIN         = 'at',     'at',     "Zora's Fountain",            "Zora's Fountain",        'Blue',       None
    JABU_JABUS_BELLY       = 'in',     'inside', "Jabu Jabu's Belly",          "Jabu Jabu's Belly",      'Blue',       'Jabu Jabus Belly'
    ICE_CAVERN             = 'inside', 'in'    , 'the Ice Cavern',             "Ice Cavern",             'Blue',       'Ice Cavern'
    LAKE_HYLIA             = 'at',     'at',     'Lake Hylia',                 "Lake Hylia",             'Blue',       None
    WATER_TEMPLE           = 'under',  'in',     'the Water Temple',           "Water Temple",           'Blue',       'Water Temple'
    KAKARIKO_VILLAGE       = 'in',     'in',     'Kakariko Village',           "Kakariko Village",       'Pink',       None
    BOTTOM_OF_THE_WELL     = 'within', 'at',     'the Bottom of the Well',     "Bottom of the Well",     'Pink',       'Bottom of the Well'
    GRAVEYARD              = 'in',     'in',     'the Graveyard',              "Graveyard",              'Pink',       None
    SHADOW_TEMPLE          = 'within', 'in',     'the Shadow Temple',          "Shadow Temple",          'Pink',       'Shadow Temple'
    GERUDO_VALLEY          = 'at',     'at',     'Gerudo Valley',              "Gerudo Valley",          'Yellow',     None
    GERUDO_FORTRESS        = 'at',     'at',     "Gerudo's Fortress",          "Gerudo's Fortress",      'Yellow',     None
    THIEVES_HIDEOUT        = 'in',     'in',     "the Thieves' Hideout",       "Thieves' Hideout",       'Yellow',     None
    GERUDO_TRAINING_GROUND = 'within', 'on',     'the Gerudo Training Ground', "Gerudo Training Ground", 'Yellow',     'Gerudo Training Ground'
    HAUNTED_WASTELAND      = 'in',     'in',     'the Haunted Wasteland',      "Haunted Wasteland",      'Yellow',     None
    DESERT_COLOSSUS        = 'at',     'at',     'the Desert Colossus',        "Desert Colossus",        'Yellow',     None
    SPIRIT_TEMPLE          = 'inside', 'in',     'the Spirit Temple',          "Spirit Temple",          'Yellow',     'Spirit Temple'

    # Performs a breadth first search to find the closest hint area from a given spot (region, location, or entrance).
    # May fail to find a hint if the given spot is only accessible from the root and not from any other region with a hint area
    @staticmethod
    def at(spot: Spot, use_alt_hint: bool = False) -> HintArea:
        if isinstance(spot, Region):
            original_parent = spot
        else:
            original_parent = spot.parent_region
        already_checked = []
        spot_queue = [spot]
        fallback_spot_queue = []

        while spot_queue or fallback_spot_queue:
            if not spot_queue:
                spot_queue = fallback_spot_queue
                fallback_spot_queue = []
            current_spot = spot_queue.pop(0)
            already_checked.append(current_spot)

            if isinstance(current_spot, Region):
                parent_region = current_spot
            else:
                parent_region = current_spot.parent_region

            if parent_region.hint and (original_parent.name == 'Root' or parent_region.name != 'Root'):
                if use_alt_hint and parent_region.alt_hint:
                    return parent_region.alt_hint
                return parent_region.hint

            for entrance in parent_region.entrances:
                if entrance not in already_checked:
                    # prioritize two-way entrances
                    if entrance.type in ('OverworldOneWay', 'OwlDrop', 'Spawn', 'WarpSong'):
                        fallback_spot_queue.append(entrance)
                    else:
                        spot_queue.append(entrance)

        raise HintAreaNotFound('No hint area could be found for %s [World %d]' % (spot, spot.world.id))

    @classmethod
    def for_dungeon(cls, dungeon_name: str) -> Optional[HintArea]:
        if '(' in dungeon_name and ')' in dungeon_name:
            # A dungeon item name was passed in - get the name of the dungeon from it.
            dungeon_name = dungeon_name[dungeon_name.index('(') + 1:dungeon_name.index(')')]

        if dungeon_name == "Thieves Hideout":
            # Special case for Thieves' Hideout since it's not considered a dungeon
            return cls.THIEVES_HIDEOUT

        if dungeon_name == "Treasure Chest Game":
            # Special case for Treasure Chest Game keys: treat them as part of the market hint area regardless of where the treasure box shop actually is.
            return cls.MARKET

        for hint_area in cls:
            if hint_area.dungeon_name is not None and hint_area.dungeon_name in dungeon_name:
                return hint_area
        return None

    def preposition(self, clearer_hints: bool) -> str:
        return self.value[1 if clearer_hints else 0]

    def __str__(self) -> str:
        return self.value[2]

    # used for dungeon reward locations in the pause menu
    @property
    def short_name(self) -> str:
        return self.value[3]

    # Hint areas are further grouped into colored sections of the map by association with the medallions.
    # These colors are used to generate the text boxes for shuffled warp songs.
    @property
    def color(self) -> str:
        return self.value[4]

    @property
    def dungeon_name(self) -> Optional[str]:
        return self.value[5]

    @property
    def is_dungeon(self) -> bool:
        return self.dungeon_name is not None

    def dungeon(self, world: World) -> Optional[Dungeon]:
        dungeons = [dungeon for dungeon in world.dungeons if dungeon.name == self.dungeon_name]
        if dungeons:
            return dungeons[0]

    def is_dungeon_item(self, item: Item) -> bool:
        for dungeon in item.world.dungeons:
            if dungeon.name == self.dungeon_name:
                return dungeon.is_dungeon_item(item)
        return False

    # Formats the hint text for this area with proper grammar.
    # Dungeons are hinted differently depending on the clearer_hints setting.
    def text(self, clearer_hints: bool, preposition: bool = False, use_2nd_person: bool = False, world: Optional[int] = None) -> str:
        if self.is_dungeon and self.dungeon_name:
            text = get_hint(self.dungeon_name, clearer_hints).text
        else:
            text = str(self)
        prefix, suffix = text.replace('#', '').split(' ', 1)
        if world is None:
            if prefix == "Link's":
                if use_2nd_person:
                    text = f'your {suffix}'
                else:
                    text = f"@'s {suffix}"
        else:
            replace_prefixes = ('a', 'an', 'the')
            move_prefixes = ('outside', 'inside')
            if prefix in replace_prefixes:
                text = f"world {world}'s {suffix}"
            elif prefix in move_prefixes:
                text = f"{prefix} world {world}'s {suffix}"
            elif prefix == "Link's":
                text = f"player {world}'s {suffix}"
            else:
                text = f"world {world}'s {text}"
        if '#' not in text:
            text = f'#{text}#'
        if preposition and self.preposition(clearer_hints) is not None:
            text = f'{self.preposition(clearer_hints)} {text}'
        return text


def get_woth_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    locations = spoiler.required_locations[world.id]
    locations = list(filter(lambda location:
        location.name not in checked
        and not (world.woth_dungeon >= world.hint_dist_user['dungeons_woth_limit'] and HintArea.at(location).is_dungeon)
        and location.name not in world.hint_exclusions
        and location.name not in world.hint_type_overrides['woth']
        and location.item.name not in world.item_hint_type_overrides['woth']
        and location.item.name not in unHintableWothItems,
        locations))

    if not locations:
        return None

    location = random.choice(locations)
    checked.add(location.name)

    hint_area = HintArea.at(location)
    if hint_area.is_dungeon:
        world.woth_dungeon += 1
    location_text = hint_area.text(world.settings.clearer_hints)

    return GossipText('%s is on the way of the hero.' % location_text, ['Light Blue'], [location.name], [location.item.name]), [location]


def get_checked_areas(world: World, checked: set[str]) -> set[HintArea | str]:
    def get_area_from_name(check: str) -> HintArea | str:
        try:
            location = world.get_location(check)
        except Exception:
            return check
        # Don't consider dungeons as already hinted from the reward hint on the Temple of Time altar
        if (location.type == 'Boss' or location.name == 'ToT Reward from Rauru') and world.settings.shuffle_dungeon_rewards in ('vanilla', 'reward'):
            return None
        return HintArea.at(location)

    return set(get_area_from_name(check) for check in checked)


def get_goal_category(spoiler: Spoiler, world: World, goal_categories: dict[str, GoalCategory]) -> GoalCategory:
    cat_sizes = []
    cat_names = []
    zero_weights = True
    goal_category = None
    for cat_name, category in goal_categories.items():
        # Only add weights if the category has goals with hintable items
        if world.id in spoiler.goal_locations and cat_name in spoiler.goal_locations[world.id]:
            # Build lists for weighted choice
            if category.weight > 0:
                zero_weights = False
            # If one hint per goal is on, only add a category for random selection if:
            #   1. Unhinted goals exist in the category, or
            #   2. All goals in all categories have been hinted at least once
            if (not world.one_hint_per_goal or
               len([goal for goal in category.goals if goal.weight > 0]) > 0 or
               len([goal for cat in world.goal_categories.values() for goal in cat.goals if goal.weight == 0]) == len([goal for cat in world.goal_categories.values() for goal in cat.goals])):
                cat_sizes.append(category.weight)
                cat_names.append(category.name)
            # Depends on category order to choose next in the priority list
            # Each category is guaranteed a hint first round, then weighted based on goal count
            if not goal_category and category.name not in world.hinted_categories:
                goal_category = category
                world.hinted_categories.append(category.name)

    # random choice if each category has at least one hint
    if not goal_category and len(cat_names) > 0:
        if zero_weights:
            goal_category = goal_categories[random.choice(cat_names)]
        else:
            goal_category = goal_categories[random.choices(cat_names, weights=cat_sizes)[0]]

    return goal_category


def get_goal_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    goal_category = get_goal_category(spoiler, world, world.goal_categories)

    # check if no goals were generated (and thus no categories available)
    if not goal_category:
        return None

    goals = goal_category.goals
    category_locations = []
    zero_weights = True
    required_location_reverse_map = defaultdict(list)

    # Filters Goal.required_locations to those still eligible to be hinted.
    hintable_required_locations_filter = (lambda required_location:
        required_location[0].name not in checked
        and required_location[0].name not in world.hint_exclusions
        and required_location[0].name not in world.hint_type_overrides['goal']
        and required_location[0].item.name not in world.item_hint_type_overrides['goal']
        and required_location[0].item.name not in unHintableWothItems)

    # Collect unhinted locations for the category across all category goals.
    # If all locations for all goals in the category are hinted, try remaining goal categories
    # If all locations for all goal categories are hinted, return no hint.
    while not required_location_reverse_map:
        # Filter hinted goals until every goal in the category has been hinted.
        weights = []
        zero_weights = True
        for goal in goals:
            if goal.weight > 0:
                zero_weights = False
            weights.append(goal.weight)

        # Collect set of unhinted locations for the category. Reduces the bias
        # from locations in multiple goals for the category.
        required_location_reverse_map = defaultdict(list)
        for goal in goals:
            if zero_weights or goal.weight > 0:
                hintable_required_locations = list(filter(hintable_required_locations_filter, goal.required_locations))
                for required_location in hintable_required_locations:
                    for world_id in required_location[3]:
                        required_location_reverse_map[required_location[0]].append((goal, world_id))

        if not required_location_reverse_map:
            del world.goal_categories[goal_category.name]
            goal_category = get_goal_category(spoiler, world, world.goal_categories)
            if not goal_category:
                return None
            else:
                goals = goal_category.goals

    location, goal_list = random.choice(list(required_location_reverse_map.items()))
    goal, world_id = random.choice(goal_list)
    checked.add(location.name)

    # Make sure this wasn't the last hintable location for other goals.
    # If so, set weights to zero. This is important for one-hint-per-goal.
    # Locations are unique per-category, so we don't have to check the others.
    last_chance_overrides = []
    for other_goal in goals:
        if not zero_weights and other_goal.weight <= 0:
            continue

        hintable_required_locations = list(filter(hintable_required_locations_filter, other_goal.required_locations))
        if not hintable_required_locations:
            other_goal.weight = 0
            if world.one_hint_per_goal:
                for required_location in other_goal.required_locations:
                    if required_location[0] == location:
                        for other_world_id in required_location[3]:
                            last_chance_overrides.append((other_goal, other_world_id))
    if (last_chance_overrides):
        # Replace randomly chosen goal with a goal that has all its locations
        # hinted without being directly hinted itself.
        goal, world_id = random.choice(last_chance_overrides)

    # Goal weight to zero mitigates double hinting this goal
    # Once all goals in a category are 0, selection is true random
    goal.weight = 0

    location_text = HintArea.at(location).text(world.settings.clearer_hints)
    if world_id == world.id:
        player_text = "the"
        goal_text = goal.hint_text
    else:
        player_text = "Player %s's" % (world_id + 1)
        goal_text = spoiler.goal_categories[world_id][goal_category.name].get_goal(goal.name).hint_text

    return GossipText('%s is on %s %s.' % (location_text, player_text, goal_text), ['Light Blue', goal.color], [location.name], [location.item.name]), [location]


def get_barren_hint(spoiler: Spoiler, world: World, checked: set[str], all_checked: set[str]) -> HintReturn:
    if not hasattr(world, 'get_barren_hint_prev'):
        world.get_barren_hint_prev = RegionRestriction.NONE

    checked_areas = get_checked_areas(world, checked)
    areas = list(filter(lambda area:
        area not in checked_areas
        and str(area) not in world.hint_type_overrides['barren']
        and not (world.barren_dungeon >= world.hint_dist_user['dungeons_barren_limit'] and world.empty_areas[area]['dungeon'])
        and any(
            location.name not in all_checked
            and location.name not in world.hint_exclusions
            and location.name not in hint_exclusions(world)
            and HintArea.at(location) == area
            for location in world.get_locations()
        ),
        world.empty_areas))

    if not areas:
        return None

    # Randomly choose between overworld or dungeon
    dungeon_areas = list(filter(lambda area: world.empty_areas[area]['dungeon'], areas))
    overworld_areas = list(filter(lambda area: not world.empty_areas[area]['dungeon'], areas))
    if not dungeon_areas:
        # no dungeons left, default to overworld
        world.get_barren_hint_prev = RegionRestriction.OVERWORLD
    elif not overworld_areas:
        # no overworld left, default to dungeons
        world.get_barren_hint_prev = RegionRestriction.DUNGEON
    else:
        if world.get_barren_hint_prev == RegionRestriction.NONE:
            # 50/50 draw on the first hint
            world.get_barren_hint_prev = random.choices([RegionRestriction.DUNGEON, RegionRestriction.OVERWORLD], [0.5, 0.5])[0]
        elif world.get_barren_hint_prev == RegionRestriction.DUNGEON:
            # weights 75% against drawing dungeon again
            world.get_barren_hint_prev = random.choices([RegionRestriction.DUNGEON, RegionRestriction.OVERWORLD], [0.25, 0.75])[0]
        elif world.get_barren_hint_prev == RegionRestriction.OVERWORLD:
            # weights 75% against drawing overworld again
            world.get_barren_hint_prev = random.choices([RegionRestriction.DUNGEON, RegionRestriction.OVERWORLD], [0.75, 0.25])[0]

    if world.get_barren_hint_prev == RegionRestriction.DUNGEON:
        areas = dungeon_areas
    else:
        areas = overworld_areas
    if not areas:
        return None

    area_weights = [world.empty_areas[area]['weight'] for area in areas]

    area = random.choices(areas, weights=area_weights)[0]
    if world.empty_areas[area]['dungeon']:
        world.barren_dungeon += 1

    checked.add(area)

    return GossipText("plundering %s is a foolish choice." % area.text(world.settings.clearer_hints), ['Pink']), None


def is_not_checked(locations: Iterable[Location], checked: set[HintArea | str]) -> bool:
    return not any(location.name in checked or HintArea.at(location) in checked for location in locations)


def get_good_item_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    locations = list(filter(lambda location:
        is_not_checked([location], checked)
        and ((location.item.majoritem
            and location.item.name not in unHintableWothItems)
                or location.name in world.added_hint_types['item']
                or location.item.name in world.item_added_hint_types['item'])
        and not location.locked
        and location.name not in world.hint_exclusions
        and location.name not in world.hint_type_overrides['item']
        and location.item.name not in world.item_hint_type_overrides['item'],
        world.get_filled_locations()))
    if not locations:
        return None

    location = random.choice(locations)
    checked.add(location.name)

    item_text = get_hint(get_item_generic_name(location.item), world.settings.clearer_hints).text
    hint_area = HintArea.at(location)
    if hint_area.is_dungeon:
        location_text = hint_area.text(world.settings.clearer_hints)
        return GossipText('%s hoards #%s#.' % (location_text, item_text), ['Red', 'Green'], [location.name], [location.item.name]), [location]
    else:
        location_text = hint_area.text(world.settings.clearer_hints, preposition=True)
        return GossipText('#%s# can be found %s.' % (item_text, location_text), ['Green', 'Red'], [location.name], [location.item.name]), [location]


def get_specific_item_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    if len(world.named_item_pool) == 0:
        logger = logging.getLogger('')
        logger.info("Named item hint requested, but pool is empty.")
        return None
    if world.settings.world_count == 1:
        while True:
            itemname = world.named_item_pool.pop(0)
            if itemname == "Bottle" and world.settings.hint_dist == "bingo":
                locations = [
                    location for location in world.get_filled_locations()
                    if (is_not_checked([location], checked)
                        and location.name not in world.hint_exclusions
                        and location.item.name in bingoBottlesForHints
                        and not location.locked
                        and location.name not in world.hint_type_overrides['named-item']
                        )
                ]
            else:
                locations = [
                    location for location in world.get_filled_locations()
                    if (is_not_checked([location], checked)
                        and location.name not in world.hint_exclusions
                        and location.item.name == itemname
                        and not location.locked
                        and location.name not in world.hint_type_overrides['named-item']
                        )
                ]

            if len(locations) > 0:
                break

            elif world.hint_dist_user['named_items_required']:
                raise Exception("Unable to hint item {}".format(itemname))

            else:
                logger = logging.getLogger('')
                logger.info("Unable to hint item {}".format(itemname))

            if len(world.named_item_pool) == 0:
                return None

        location = random.choice(locations)
        checked.add(location.name)
        item_text = get_hint(get_item_generic_name(location.item), world.settings.clearer_hints).text

        hint_area = HintArea.at(location)
        if world.hint_dist_user.get('vague_named_items', False):
            location_text = hint_area.text(world.settings.clearer_hints)
            return GossipText('%s may be on the hero\'s path.' % location_text, ['Green'], [location.name], [location.item.name]), [location]
        elif hint_area.is_dungeon:
            location_text = hint_area.text(world.settings.clearer_hints)
            return GossipText('%s hoards #%s#.' % (location_text, item_text), ['Red', 'Green'], [location.name], [location.item.name]), [location]
        else:
            location_text = hint_area.text(world.settings.clearer_hints, preposition=True)
            return GossipText('#%s# can be found %s.' % (item_text, location_text), ['Green', 'Red'], [location.name], [location.item.name]), [location]

    else:
        while True:
            # This operation is likely to be costly (especially for large multiworlds), so cache the result for later
            # named_item_locations: Filtered locations from all worlds that may contain named-items
            try:
                named_item_locations = spoiler._cached_named_item_locations
                always_locations = spoiler._cached_always_locations
            except AttributeError:
                worlds = spoiler.worlds
                all_named_items = set(itertools.chain.from_iterable([w.named_item_pool for w in worlds]))
                if "Bottle" in all_named_items and world.settings.hint_dist == "bingo":
                    all_named_items.update(bingoBottlesForHints)
                named_item_locations = [location for w in worlds for location in w.get_filled_locations() if (location.item.name in all_named_items)]
                spoiler._cached_named_item_locations = named_item_locations

                always_hints = [(hint, w.id) for w in worlds for hint in get_hint_group('always', w)]
                always_locations = []
                for hint, id  in always_hints:
                    location = worlds[id].get_location(hint.name)
                    if location.item.name in bingoBottlesForHints and world.settings.hint_dist == 'bingo':
                        always_item = 'Bottle'
                    else:
                        always_item = location.item.name
                    always_locations.append((always_item, location.item.world.id))
                spoiler._cached_always_locations = always_locations

            itemname = world.named_item_pool.pop(0)
            if itemname == "Bottle" and world.settings.hint_dist == "bingo":
                locations = [
                    location for location in named_item_locations
                    if (is_not_checked([location], checked)
                        and location.item.world.id == world.id
                        and location.name not in world.hint_exclusions
                        and location.item.name in bingoBottlesForHints
                        and not location.locked
                        and (itemname, world.id) not in always_locations
                        and location.name not in world.hint_type_overrides['named-item'])
                ]
            else:
                locations = [
                    location for location in named_item_locations
                    if (is_not_checked([location], checked)
                        and location.item.world.id == world.id
                        and location.name not in world.hint_exclusions
                        and location.item.name == itemname
                        and not location.locked
                        and (itemname, world.id) not in always_locations
                        and location.name not in world.hint_type_overrides['named-item'])
                ]

            if len(locations) > 0:
                break

            elif world.hint_dist_user['named_items_required'] and (itemname, world.id) not in always_locations:
                raise Exception("Unable to hint item {} in world {}".format(itemname, world.id))

            else:
                logger = logging.getLogger('')
                if (itemname, world.id) not in spoiler._cached_always_locations:
                    logger.info("Hint for item {} in world {} skipped due to Always hint".format(itemname, world.id))
                else:
                    logger.info("Unable to hint item {} in world {}".format(itemname, world.id))

            if len(world.named_item_pool) == 0:
                return None

        location = random.choice(locations)
        checked.add(location.name)
        item_text = get_hint(get_item_generic_name(location.item), world.settings.clearer_hints).text

        hint_area = HintArea.at(location)
        if world.hint_dist_user.get('vague_named_items', False):
            location_text = hint_area.text(world.settings.clearer_hints, world=location.world.id + 1)
            return GossipText('%s may be on the hero\'s path.' % location_text, ['Green'], [location.name], [location.item.name]), [location]
        elif hint_area.is_dungeon:
            location_text = hint_area.text(world.settings.clearer_hints, world=location.world.id + 1)
            return GossipText('%s hoards #%s#.' % (location_text, item_text), ['Red', 'Green'], [location.name], [location.item.name]), [location]
        else:
            location_text = hint_area.text(world.settings.clearer_hints, preposition=True, world=location.world.id + 1)
            return GossipText('#%s# can be found %s.' % (item_text, location_text), ['Green', 'Red'], [location.name], [location.item.name]), [location]


def get_random_location_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    locations = list(filter(lambda location:
        is_not_checked([location], checked)
        and location.item.type not in ('Drop', 'Event', 'Shop')
        and not is_restricted_dungeon_item(location.item)
        and not location.locked
        and location.name not in world.hint_exclusions
        and location.name not in world.hint_type_overrides['item']
        and location.item.name not in world.item_hint_type_overrides['item']
        and (location.world.settings.empty_dungeons_mode == 'none' or not location.world.empty_dungeons[HintArea.at(location).dungeon_name].empty),
        world.get_filled_locations()))
    if not locations:
        return None

    location = random.choice(locations)
    checked.add(location.name)
    item_text = get_hint(get_item_generic_name(location.item), world.settings.clearer_hints).text

    hint_area = HintArea.at(location)
    if hint_area.is_dungeon:
        location_text = hint_area.text(world.settings.clearer_hints)
        return GossipText('%s hoards #%s#.' % (location_text, item_text), ['Red', 'Green'], [location.name], [location.item.name]), [location]
    else:
        location_text = hint_area.text(world.settings.clearer_hints, preposition=True)
        return GossipText('#%s# can be found %s.' % (item_text, location_text), ['Green', 'Red'], [location.name], [location.item.name]), [location]


def get_specific_hint(spoiler: Spoiler, world: World, checked: set[str], hint_type: str) -> HintReturn:
    def is_valid_hint(hint: Hint) -> bool:
        location = world.get_location(hint.name)
        if not is_not_checked([world.get_location(hint.name)], checked):
            return False
        if location.world.settings.empty_dungeons_mode != 'none' and location.world.empty_dungeons[HintArea.at(location).dungeon_name].empty:
            return False
        return True

    hint_group = get_hint_group(hint_type, world)
    hint_group = list(filter(is_valid_hint, hint_group))
    if not hint_group:
        return None

    hint = random.choice(hint_group)

    if world.hint_dist_user['upgrade_hints'] in ['on', 'limited']:
        upgrade_list = get_upgrade_hint_list(world, [hint.name])
        upgrade_list = list(filter(lambda upgrade: is_not_checked([world.get_location(location) for location in get_multi(
            upgrade.name).locations], checked), upgrade_list))

        if upgrade_list is not None:
            multi = None

            for upgrade in upgrade_list:
                upgrade_multi = get_multi(upgrade.name)

                if not multi or len(multi.locations) < len(upgrade_multi.locations):
                    hint = upgrade
                    multi = get_multi(hint.name)

            if multi:
                return get_specific_multi_hint(spoiler, world, checked, hint)

    location = world.get_location(hint.name)
    checked.add(location.name)

    if location.name in world.hint_text_overrides:
        location_text = world.hint_text_overrides[location.name]
    else:
        location_text = hint.text
    if '#' not in location_text:
        location_text = '#%s#' % location_text
    item_text = get_hint(get_item_generic_name(location.item), world.settings.clearer_hints).text

    return GossipText('%s #%s#.' % (location_text, item_text), ['Red', 'Green'], [location.name], [location.item.name]), [location]


def get_sometimes_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    return get_specific_hint(spoiler, world, checked, 'sometimes')


def get_song_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    return get_specific_hint(spoiler, world, checked, 'song')


def get_overworld_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    return get_specific_hint(spoiler, world, checked, 'overworld')


def get_dungeon_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    return get_specific_hint(spoiler, world, checked, 'dungeon')


def get_random_multi_hint(spoiler: Spoiler, world: World, checked: set[str], hint_type: str) -> HintReturn:
    hint_group = get_hint_group(hint_type, world)
    multi_hints = list(filter(lambda hint: is_not_checked([world.get_location(location) for location in get_multi(
        hint.name).locations], checked), hint_group))

    if not multi_hints:
        return None

    hint = random.choice(multi_hints)

    if world.hint_dist_user['upgrade_hints'] in ['on', 'limited']:
        multi = get_multi(hint.name)

        upgrade_list = get_upgrade_hint_list(world, multi.locations)
        upgrade_list = list(filter(lambda upgrade: is_not_checked([world.get_location(location) for location in get_multi(
            upgrade.name).locations], checked), upgrade_list))

        if upgrade_list:
            for upgrade in upgrade_list:
                upgrade_multi = get_multi(upgrade.name)

                if len(multi.locations) < len(upgrade_multi.locations):
                    hint = upgrade
                    multi = get_multi(hint.name)

    return get_specific_multi_hint(spoiler, world, checked, hint)


def get_specific_multi_hint(spoiler: Spoiler, world: World, checked: set[str], hint: Hint) -> HintReturn:
    multi = get_multi(hint.name)
    locations = [world.get_location(location) for location in multi.locations]

    for location in locations:
        checked.add(location.name)

    if hint.name in world.hint_text_overrides:
        multi_text = world.hint_text_overrides[hint.name]
    else:
        multi_text = hint.text
    if '#' not in multi_text:
        multi_text = '#%s#' % multi_text

    location_count = len(locations)
    colors = ['Red']
    gossip_string = '%s '
    for i in range(location_count):
        colors.append('Green')
        if i == location_count - 1:
            gossip_string = gossip_string + 'and #%s#.'
        else:
            gossip_string = gossip_string + '#%s# '

    items = [location.item for location in locations]
    text_segments = [multi_text] + [get_hint(get_item_generic_name(item), world.settings.clearer_hints).text for item in items]
    return GossipText(gossip_string % tuple(text_segments), colors, [location.name for location in locations], [item.name for item in items]), locations


def get_dual_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    return get_random_multi_hint(spoiler, world, checked, 'dual')


def get_entrance_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    if not world.entrance_shuffle:
        return None

    entrance_hints = list(filter(lambda hint: hint.name not in checked, get_hint_group('entrance', world)))
    shuffled_entrance_hints = list(filter(lambda entrance_hint: world.get_entrance(entrance_hint.name).shuffled, entrance_hints))

    regions_with_hint = [hint.name for hint in get_hint_group('region', world)]
    valid_entrance_hints = list(filter(lambda entrance_hint:
                                       (world.get_entrance(entrance_hint.name).connected_region.name in regions_with_hint or
                                        world.get_entrance(entrance_hint.name).connected_region.dungeon), shuffled_entrance_hints))

    if not valid_entrance_hints:
        return None

    entrance_hint = random.choice(valid_entrance_hints)
    entrance = world.get_entrance(entrance_hint.name)
    checked.add(entrance.name)

    entrance_text = entrance_hint.text

    if '#' not in entrance_text:
        entrance_text = '#%s#' % entrance_text

    connected_region = entrance.connected_region
    if connected_region.dungeon:
        region_text = get_hint(connected_region.dungeon.name, world.settings.clearer_hints).text
    else:
        region_text = get_hint(connected_region.name, world.settings.clearer_hints).text

    if '#' not in region_text:
        region_text = '#%s#' % region_text

    return GossipText('%s %s.' % (entrance_text, region_text), ['Green', 'Light Blue']), None


def get_junk_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    hints = get_hint_group('junk', world)
    hints = list(filter(lambda hint: hint.name not in checked, hints))
    if not hints:
        return None

    hint = random.choice(hints)
    checked.add(hint.name)

    return GossipText(hint.text, prefix=''), None


def get_important_check_hint(spoiler: Spoiler, world: World, checked: set[str]) -> HintReturn:
    top_level_locations = []
    for location in world.get_filled_locations():
        if (HintArea.at(location).text(world.settings.clearer_hints) not in top_level_locations
                and (HintArea.at(location).text(world.settings.clearer_hints) + ' Important Check') not in checked
                and HintArea.at(location) != HintArea.ROOT):
            top_level_locations.append(HintArea.at(location).text(world.settings.clearer_hints))
    hint_loc = random.choice(top_level_locations)
    item_count = 0
    for location in world.get_filled_locations():
        region = HintArea.at(location).text(world.settings.clearer_hints)
        if region == hint_loc:
            if (location.item.majoritem
                # exclude locked items
                and not location.locked
                # exclude triforce pieces as it defeats the idea of a triforce hunt
                and not location.item.name == 'Triforce Piece'
                and not (location.name == 'Song from Impa' and 'Zeldas Letter' in world.settings.starting_items and 'Zeldas Letter' not in world.settings.shuffle_child_trade)
                # Special cases where the item is only considered major for important checks hints
                or location.item.name == 'Biggoron Sword'
                or location.item.name == 'Double Defense'
                # Handle make keys not in own dungeon major items
                or (location.item.type == 'SmallKey' and not (world.settings.shuffle_smallkeys == 'dungeon' or world.settings.shuffle_smallkeys == 'vanilla'))
                or (location.item.type == 'HideoutSmallKey' and not world.settings.shuffle_hideoutkeys == 'vanilla')
                or (location.item.type == 'TCGSmallKey' and not world.settings.shuffle_tcgkeys == 'vanilla')
                or (location.item.type == 'BossKey' and not (world.settings.shuffle_bosskeys == 'dungeon' or world.settings.shuffle_bosskeys == 'vanilla'))
                or (location.item.type == 'GanonBossKey' and not (world.settings.shuffle_ganon_bosskey == 'vanilla'
                    or world.settings.shuffle_ganon_bosskey == 'dungeon' or world.settings.shuffle_ganon_bosskey == 'on_lacs'
                    or world.settings.shuffle_ganon_bosskey == 'stones' or world.settings.shuffle_ganon_bosskey == 'medallions'
                    or world.settings.shuffle_ganon_bosskey == 'dungeons' or world.settings.shuffle_ganon_bosskey == 'tokens'))):
                item_count = item_count + 1

    checked.add(hint_loc + ' Important Check')

    if item_count == 0:
        numcolor = 'Red'
    elif item_count == 1:
        numcolor = 'Pink'
    elif item_count == 2:
        numcolor = 'Yellow'
    elif item_count == 3:
        numcolor = 'Light Blue'
    else:
        numcolor = 'Green'

    return GossipText('#%s# has #%d# major item%s.' % (hint_loc, item_count, "s" if item_count != 1 else ""), ['Green', numcolor]), None


hint_func: dict[str, HintFunc | BarrenFunc] = {
    'trial':            lambda spoiler, world, checked: None,
    'always':           lambda spoiler, world, checked: None,
    'dual_always':      lambda spoiler, world, checked: None,
    'entrance_always':  lambda spoiler, world, checked: None,
    'woth':             get_woth_hint,
    'goal':             get_goal_hint,
    'barren':           get_barren_hint,
    'item':             get_good_item_hint,
    'sometimes':        get_sometimes_hint,
    'dual':             get_dual_hint,
    'song':             get_song_hint,
    'overworld':        get_overworld_hint,
    'dungeon':          get_dungeon_hint,
    'entrance':         get_entrance_hint,
    'random':           get_random_location_hint,
    'junk':             get_junk_hint,
    'named-item':       get_specific_item_hint,
    'important_check':  get_important_check_hint,
}

hint_dist_keys: set[str] = set(hint_func)


def build_bingo_hint_list(board_url: str) -> list[str]:
    try:
        if len(board_url) > 256:
            raise URLError(f"URL too large {len(board_url)}")
        with urllib.request.urlopen(board_url + "/board") as board:
            if board.length and 0 < board.length < 4096:
                goal_list = board.read()
            else:
                raise URLError(f"Board of invalid size {board.length}")
    except (URLError, HTTPError) as e:
        logger = logging.getLogger('')
        logger.info(f"Could not retrieve board info. Using default bingo hints instead: {e}")
        with open(data_path('Bingo/generic_bingo_hints.json'), 'r') as bingoFile:
            generic_bingo = json.load(bingoFile)
        return generic_bingo['settings']['item_hints']

    # Goal list returned from Bingosync is a sequential list of all of the goals on the bingo board, starting at top-left and moving to the right.
    # Each goal is a dictionary with attributes for name, slot, and colours. The only one we use is the name
    goal_list = [goal['name'] for goal in json.loads(goal_list)]
    with open(data_path('Bingo/bingo_goals.json'), 'r') as bingoFile:
        goal_hint_requirements = json.load(bingoFile)

    hints_to_add = {}
    for goal in goal_list:
        # Using 'get' here ensures some level of forward compatibility, where new goals added to randomiser bingo won't
        # cause the generator to crash (though those hints won't have item hints for them)
        requirements = goal_hint_requirements.get(goal, {})
        if len(requirements) != 0:
            for item in requirements:
                hints_to_add[item] = max(hints_to_add.get(item, 0), requirements[item]['count'])

    # Items to be hinted need to be included in the item_hints list once for each instance you want hinted
    # (e.g. if you want all three strength upgrades to be hintes it needs to be in the list three times)
    hints = []
    for key, value in hints_to_add.items():
        for _ in range(value):
            hints.append(key)

    # Since there's no way to verify if the Bingosync URL is actually for OoTR, this exception catches that case
    if len(hints) == 0:
        raise Exception('No item hints found for goals on Bingosync card. Verify Bingosync URL is correct, or leave field blank for generic bingo hints.')
    return hints


def always_named_item(world: World, locations: Iterable[Location]):
    for location in locations:
        if location.item.name in bingoBottlesForHints and world.settings.hint_dist == 'bingo':
            always_item = 'Bottle'
        else:
            always_item = location.item.name
        if always_item in world.named_item_pool and world.settings.world_count == 1:
            world.named_item_pool.remove(always_item)


def build_gossip_hints(spoiler: Spoiler, worlds: list[World]) -> None:
    from Dungeon import Dungeon

    checked_locations = dict()
    # Add misc. item hint locations to "checked" locations if the respective hint is reachable without the hinted item.
    for world in worlds:
        for location in world.hinted_dungeon_reward_locations.values():
            if world.settings.enhance_map_compass:
                if world.mixed_pools_bosses or world.settings.shuffle_dungeon_rewards not in ('vanilla', 'reward'):
                    # In these settings, there is not necessarily one dungeon reward in each dungeon,
                    # so we instead have each compass hint the area of its dungeon's vanilla reward.
                    compass_locations = [
                        compass_location
                        for compass_world in worlds
                        for compass_location in compass_world.get_filled_locations()
                        if Dungeon.from_vanilla_reward(location.item) is None # Light Medallion area is shown in menu from beginning of game
                        or (
                            compass_location.item.name == Dungeon.from_vanilla_reward(location.item).item_name('Compass')
                            and compass_location.item.world == world
                        )
                    ]
                else:
                    # Each compass hints which reward is in its dungeon.
                    compass_locations = [
                        compass_location
                        for compass_world in worlds
                        for compass_location in compass_world.get_filled_locations()
                        if HintArea.at(location).dungeon_name is None # free/ToT reward is shown in menu from beginning of game
                        or (
                            compass_location.item.name == HintArea.at(location).dungeon(location.world).item_name('Compass')
                            and compass_location.item.world == world
                        )
                    ]
                for compass_location in compass_locations:
                    if can_reach_hint(worlds, compass_location, location):
                        item_world = location.world
                        if item_world.id not in checked_locations:
                            checked_locations[item_world.id] = set()
                        checked_locations[item_world.id].add(location.name)
                        break
            else:
                if 'altar' in world.settings.misc_hints and can_reach_hint(worlds, world.get_location('ToT Child Altar Hint' if location.item.info.stone else 'ToT Adult Altar Hint'), location):
                    item_world = location.world
                    if item_world.id not in checked_locations:
                        checked_locations[item_world.id] = set()
                    checked_locations[item_world.id].add(location.name)
        for hint_type, location in world.misc_hint_item_locations.items():
            if hint_type in world.settings.misc_hints and can_reach_hint(worlds, world.get_location(misc_item_hint_table[hint_type]['hint_location']), location):
                item_world = location.world
                if item_world.id not in checked_locations:
                    checked_locations[item_world.id] = set()
                checked_locations[item_world.id].add(location.name)
        for hint_type in world.misc_hint_location_items.keys():
            location = world.get_location(misc_location_hint_table[hint_type]['item_location'])
            if hint_type in world.settings.misc_hints and can_reach_hint(worlds, world.get_location(misc_location_hint_table[hint_type]['hint_location']), location):
                item_world = location.world
                if item_world.id not in checked_locations:
                    checked_locations[item_world.id] = set()
                checked_locations[item_world.id].add(location.name)
        for dungeon_name, info in world.empty_dungeons.items():
            if info.empty:
                for region in world.regions:
                    if region.dungeon != None and region.dungeon.name == dungeon_name:
                        precompleted_locations = list(map(lambda location: location.name, region.locations))
                        checked_locations[world.id].update(precompleted_locations)

    # Build all the hints.
    for world in worlds:
        world.update_useless_areas(spoiler)
        build_world_gossip_hints(spoiler, world, checked_locations.pop(world.id, None))


# builds out general hints based on location and whether an item is required or not
def build_world_gossip_hints(spoiler: Spoiler, world: World, checked_locations: Optional[set[str]] = None) -> None:
    world.barren_dungeon = 0
    world.woth_dungeon = 0

    search = Search.max_explore([w.state for w in spoiler.worlds])
    for stone in gossipLocations.values():
        stone.reachable = (
            search.spot_access(world.get_location(stone.location))
            and search.state_list[world.id].guarantee_hint())

    if checked_locations is None:
        checked_locations = set()
    checked_always_locations = set()

    stone_ids = list(gossipLocations.keys())

    world.distribution.configure_gossip(spoiler, stone_ids)

    # If all gossip stones already have plando'd hints, do not roll any more
    if len(stone_ids) == 0:
        return

    if 'disabled' in world.hint_dist_user:
        for stone_name in world.hint_dist_user['disabled']:
            try:
                stone_id = gossipLocations_reversemap[stone_name]
            except KeyError:
                raise ValueError(f'Gossip stone location "{stone_name}" is not valid')
            if stone_id in stone_ids:
                stone_ids.remove(stone_id)
                (gossip_text, _) = get_junk_hint(spoiler, world, checked_locations)
                spoiler.hints[world.id][stone_id] = gossip_text

    stone_groups = []
    if 'groups' in world.hint_dist_user:
        for group_names in world.hint_dist_user['groups']:
            group = []
            for stone_name in group_names:
                try:
                    stone_id = gossipLocations_reversemap[stone_name]
                except KeyError:
                    raise ValueError(f'Gossip stone location "{stone_name}" is not valid')

                if stone_id in stone_ids:
                    stone_ids.remove(stone_id)
                    group.append(stone_id)
            if len(group) != 0:
                stone_groups.append(group)
    # put the remaining locations into singleton groups
    stone_groups.extend([[id] for id in stone_ids])

    random.shuffle(stone_groups)

    # Create list of items for which we want hints. If Bingosync URL is supplied, include items specific to that bingo.
    # If not (or if the URL is invalid), use generic bingo hints
    if world.settings.hint_dist == "bingo":
        with open(data_path('Bingo/generic_bingo_hints.json'), 'r') as bingoFile:
            bingo_defaults = json.load(bingoFile)
        if world.settings.bingosync_url and world.settings.bingosync_url.startswith("https://bingosync.com/"): # Verify that user actually entered a bingosync URL
            logger = logging.getLogger('')
            logger.info("Got Bingosync URL. Building board-specific goals.")
            world.item_hints = build_bingo_hint_list(world.settings.bingosync_url)
        else:
            world.item_hints = bingo_defaults['settings']['item_hints']

        if world.settings.tokensanity in ("overworld", "all") and "Suns Song" not in world.item_hints:
            world.item_hints.append("Suns Song")

        if world.settings.shopsanity != "off" and "Progressive Wallet" not in world.item_hints:
            world.item_hints.append("Progressive Wallet")

    # Removes items from item_hints list if they are included in starting gear.
    # This method ensures that the right number of copies are removed, e.g.
    # if you start with one strength and hints call for two, you still get
    # one hint for strength. This also handles items from Skip Child Zelda.
    for itemname, record in world.distribution.effective_starting_items.items():
        for _ in range(record.count):
            if itemname in world.item_hints:
                world.item_hints.remove(itemname)

    world.named_item_pool = list(world.item_hints)

    # Make sure the total number of hints won't pass 40. If so, we limit the always and trial hints
    if world.settings.hint_dist == "bingo":
        num_trial_hints = [0, 1, 2, 3, 2, 1, 0]
        if (2 * len(world.item_hints) + 2 * len(get_hint_group('always', world)) + 2 * num_trial_hints[world.settings.trials] > 40) and (world.hint_dist_user['named_items_required']):
            world.hint_dist_user['distribution']['always']['copies'] = 1
            world.hint_dist_user['distribution']['trial']['copies'] = 1

    # Load hint distro from distribution file or pre-defined settings
    #
    # 'fixed' key is used to mimic the tournament distribution, creating a list of fixed hint types to fill
    # Once the fixed hint type list is exhausted, weighted random choices are taken like all non-tournament sets
    # This diverges from the tournament distribution where leftover stones are filled with sometimes hints (or random if no sometimes locations remain to be hinted)
    sorted_dist = {}
    type_count = 1
    hint_dist = OrderedDict({})
    fixed_hint_types = []
    max_order = 0
    for hint_type in world.hint_dist_user['distribution']:
        if world.hint_dist_user['distribution'][hint_type]['order'] > 0:
            hint_order = int(world.hint_dist_user['distribution'][hint_type]['order'])
            sorted_dist[hint_order] = hint_type
            if max_order < hint_order:
                max_order = hint_order
            type_count = type_count + 1
    if (type_count - 1) < max_order:
        raise Exception("There are gaps in the custom hint orders. Please revise your plando file to remove them.")
    for i in range(1, type_count):
        hint_type = sorted_dist[i]
        if world.hint_dist_user['distribution'][hint_type]['copies'] > 0:
            fixed_num = world.hint_dist_user['distribution'][hint_type]['fixed']
            hint_weight = world.hint_dist_user['distribution'][hint_type]['weight']
        else:
            logging.getLogger('').warning("Hint copies is zero for type %s. Assuming this hint type should be disabled.", hint_type)
            fixed_num = 0
            hint_weight = 0
        hint_dist[hint_type] = (hint_weight, world.hint_dist_user['distribution'][hint_type]['copies'])
        hint_dist.move_to_end(hint_type)
        fixed_hint_types.extend([hint_type] * int(fixed_num))

    hint_types, hint_prob = zip(*hint_dist.items())
    hint_prob, _ = zip(*hint_prob)

    # Add required dual location hints, only if hint copies > 0
    if 'dual_always' in hint_dist and hint_dist['dual_always'][1] > 0:
        always_duals = get_hint_group('dual_always', world)
        for hint in always_duals:
            multi = get_multi(hint.name)
            first_location = world.get_location(multi.locations[0])
            second_location = world.get_location(multi.locations[1])
            checked_always_locations.add(first_location.name)
            checked_always_locations.add(second_location.name)

            always_named_item(world, [first_location, second_location])

            if hint.name in world.hint_text_overrides:
                location_text = world.hint_text_overrides[hint.name]
            else:
                location_text = get_hint(hint.name, world.settings.clearer_hints).text
            if '#' not in location_text:
                location_text = '#%s#' % location_text
            first_item_text = get_hint(get_item_generic_name(first_location.item), world.settings.clearer_hints).text
            second_item_text = get_hint(get_item_generic_name(second_location.item), world.settings.clearer_hints).text
            add_hint(spoiler, world, stone_groups, GossipText('%s #%s# and #%s#.' % (location_text, first_item_text, second_item_text), ['Red', 'Green', 'Green'], [first_location.name, second_location.name], [first_location.item.name, second_location.item.name]), hint_dist['dual_always'][1], [first_location, second_location], force_reachable=True, hint_type='dual_always')
            logging.getLogger('').debug('Placed dual_always hint for %s.', hint.name)

    # Add required location hints, only if hint copies > 0
    if hint_dist['always'][1] > 0:
        always_locations = list(filter(lambda hint: is_not_checked([world.get_location(hint.name)], checked_always_locations),
                                       get_hint_group('always', world)))
        for hint in always_locations:
            location = world.get_location(hint.name)
            checked_always_locations.add(hint.name)

            always_named_item(world, [location])

            if location.name in world.hint_text_overrides:
                location_text = world.hint_text_overrides[location.name]
            else:
                location_text = get_hint(location.name, world.settings.clearer_hints).text
            if '#' not in location_text:
                location_text = '#%s#' % location_text
            item_text = get_hint(get_item_generic_name(location.item), world.settings.clearer_hints).text
            add_hint(spoiler, world, stone_groups, GossipText('%s #%s#.' % (location_text, item_text), ['Red', 'Green'], [location.name], [location.item.name]), hint_dist['always'][1], [location], force_reachable=True, hint_type='always')
            logging.getLogger('').debug('Placed always hint for %s.', location.name)

    # Add required entrance hints, only if hint copies > 0
    if world.entrance_shuffle and 'entrance_always' in hint_dist and hint_dist['entrance_always'][1] > 0:
        always_entrances = get_hint_group('entrance_always', world)
        for entrance_hint in always_entrances:
            entrance = world.get_entrance(entrance_hint.name)
            connected_region = entrance.connected_region
            if entrance.shuffled and (connected_region.dungeon or any(hint.name == connected_region.name for hint in
                                                                      get_hint_group('region', world))):
                checked_always_locations.add(entrance.name)

                entrance_text = entrance_hint.text
                if '#' not in entrance_text:
                    entrance_text = '#%s#' % entrance_text

                if connected_region.dungeon:
                    region_text = get_hint(connected_region.dungeon.name, world.settings.clearer_hints).text
                else:
                    region_text = get_hint(connected_region.name, world.settings.clearer_hints).text
                if '#' not in region_text:
                    region_text = '#%s#' % region_text

                add_hint(spoiler, world, stone_groups, GossipText('%s %s.' % (entrance_text, region_text), ['Green', 'Light Blue']), hint_dist['entrance_always'][1], None, force_reachable=True, hint_type='entrance_always')

    # Add trial hints, only if hint copies > 0
    if hint_dist['trial'][1] > 0:
        if world.settings.trials_random and world.settings.trials == 6:
            add_hint(spoiler, world, stone_groups, GossipText("#Ganon's Tower# is protected by a powerful barrier.", ['Pink']), hint_dist['trial'][1], force_reachable=True, hint_type='trial')
        elif world.settings.trials_random and world.settings.trials == 0:
            add_hint(spoiler, world, stone_groups, GossipText("Sheik dispelled the barrier around #Ganon's Tower#.", ['Yellow']), hint_dist['trial'][1], force_reachable=True, hint_type='trial')
        elif 3 < world.settings.trials < 6:
            if world.hint_dist_user['combine_trial_hints'] and world.settings.trials < 5:
                add_hint(spoiler, world, stone_groups, GossipText("the #%s Trials# were dispelled by Sheik." % natjoin(trial for trial, skipped in world.skipped_trials.items() if skipped), ['Yellow']), hint_dist['trial'][1], force_reachable=True, hint_type='trial')
            else:
                for trial, skipped in world.skipped_trials.items():
                    if skipped:
                        add_hint(spoiler, world, stone_groups, GossipText("the #%s Trial# was dispelled by Sheik." % trial, ['Yellow']), hint_dist['trial'][1], force_reachable=True, hint_type='trial')
        elif 0 < world.settings.trials <= 3:
            if world.hint_dist_user['combine_trial_hints'] and world.settings.trials > 1:
                add_hint(spoiler, world, stone_groups, GossipText("the #%s Trials# protect Ganon's Tower." % natjoin(trial for trial, skipped in world.skipped_trials.items() if not skipped), ['Pink']), hint_dist['trial'][1], force_reachable=True, hint_type='trial')
            else:
                for trial, skipped in world.skipped_trials.items():
                    if not skipped:
                        add_hint(spoiler, world, stone_groups, GossipText("the #%s Trial# protects Ganon's Tower." % trial, ['Pink']), hint_dist['trial'][1], force_reachable=True, hint_type='trial')

    # Add user-specified hinted item locations if using a built-in hint distribution
    # Raise error if hint copies is zero
    if len(world.named_item_pool) > 0 and world.hint_dist_user['named_items_required']:
        if hint_dist['named-item'][1] == 0:
            raise Exception('User-provided item hints were requested, but copies per named-item hint is zero')
        else:
            # Prevent conflict between Ganondorf Light Arrows hint and required named item hints.
            # Assumes that a "wasted" hint is desired since Light Arrows have to be added
            # explicitly to the list for named item hints.
            filtered_checked = set(checked_locations | checked_always_locations)
            for location in (checked_locations | checked_always_locations):
                try:
                    if world.get_location(location).item.name == 'Light Arrows':
                        filtered_checked.remove(location)
                except KeyError:
                    pass  # checked_always_locations can also contain entrances from entrance_always hints, ignore those here
            for i in range(0, len(world.named_item_pool)):
                hint = get_specific_item_hint(spoiler, world, filtered_checked)
                if hint:
                    checked_locations.update(filtered_checked - checked_always_locations)
                    gossip_text, location = hint
                    place_ok = add_hint(spoiler, world, stone_groups, gossip_text, hint_dist['named-item'][1], location, hint_type='named-item')
                    if not place_ok:
                        raise Exception('Not enough gossip stones for user-provided item hints')

    # Shuffle named items hints
    # When all items are not required to be hinted, this allows for
    # opportunity-style hints to be drawn at random from the defined list.
    random.shuffle(world.named_item_pool)

    hint_types = list(hint_types)
    hint_prob  = list(hint_prob)
    hint_counts = {}

    custom_fixed = True
    while stone_groups:
        if fixed_hint_types:
            hint_type = fixed_hint_types.pop(0)
            copies = hint_dist[hint_type][1]
            if copies > len(stone_groups):
                # Quiet to avoid leaking information.
                logging.getLogger('').debug(f'Not enough gossip stone locations ({len(stone_groups)} groups) for fixed hint type {hint_type} with {copies} copies, proceeding with available stones.')
                copies = len(stone_groups)
        else:
            custom_fixed = False
            # Make sure there are enough stones left for each hint type
            num_types = len(hint_types)
            hint_types = list(filter(lambda htype: hint_dist[htype][1] <= len(stone_groups), hint_types))
            new_num_types = len(hint_types)
            if new_num_types == 0:
                raise Exception('Not enough gossip stone locations for remaining weighted hint types.')
            elif new_num_types < num_types:
                hint_prob = []
                for htype in hint_types:
                    hint_prob.append(hint_dist[htype][0])
            try:
                # Weight the probabilities such that hints that are over the expected proportion
                # will be drawn less, and hints that are under will be drawn more.
                # This tightens the variance quite a bit. The variance can be adjusted via the power
                weighted_hint_prob = []
                for w1_type, w1_prob in zip(hint_types, hint_prob):
                    p = w1_prob
                    if p != 0: # If the base prob is 0, then it's 0
                        for w2_type, w2_prob in zip(hint_types, hint_prob):
                            if w2_prob != 0: # If the other prob is 0, then it has no effect
                                # Raising this term to a power greater than 1 will decrease variance
                                # Conversely, a power less than 1 will increase variance
                                p = p * (((hint_counts.get(w2_type, 0) / w2_prob) + 1) / ((hint_counts.get(w1_type, 0) / w1_prob) + 1))
                    weighted_hint_prob.append(p)

                hint_type = random.choices(hint_types, weights=weighted_hint_prob)[0]
                copies = hint_dist[hint_type][1]
            except IndexError:
                raise Exception('Not enough valid hints to fill gossip stone locations.')

        all_checked_locations = checked_locations | checked_always_locations
        if hint_type == 'barren':
            hint = hint_func[hint_type](spoiler, world, checked_locations, all_checked_locations)
        else:
            hint = hint_func[hint_type](spoiler, world, all_checked_locations)
            checked_locations.update(all_checked_locations - checked_always_locations)

        if hint is None:
            index = hint_types.index(hint_type)
            hint_prob[index] = 0
            # Zero out the probability in the base distribution in case the probability list is modified
            # to fit hint types in remaining gossip stones
            hint_dist[hint_type] = (0.0, copies)
        else:
            gossip_text, locations = hint
            place_ok = add_hint(spoiler, world, stone_groups, gossip_text, copies, locations, hint_type=hint_type)
            if place_ok:
                hint_counts[hint_type] = hint_counts.get(hint_type, 0) + 1
                if locations is None:
                    logging.getLogger('').debug('Placed %s hint.', hint_type)
                else:
                    logging.getLogger('').debug('Placed %s hint for %s.', hint_type, ', '.join([location.name for location in locations]))
            if not place_ok and custom_fixed:
                logging.getLogger('').debug('Failed to place %s fixed hint for %s.', hint_type, ', '.join([location.name for location in locations]))
                fixed_hint_types.insert(0, hint_type)


# builds text that is displayed at the temple of time altar for child and adult, rewards pulled based off of item in a fixed order.
def build_altar_hints(world: World, messages: list[Message], include_rewards: bool = True, include_wincons: bool = True) -> None:
    # text that appears at altar as a child.
    child_text = '\x08'
    if include_rewards:
        boss_rewards_spiritual_stones = [(reward, REWARD_COLORS[reward]) for reward in (
            'Kokiri Emerald',
            'Goron Ruby',
            'Zora Sapphire',
        )]
        child_text += get_hint('Spiritual Stone Text Start', world.settings.clearer_hints).text + '\x04'
        for (reward, color) in boss_rewards_spiritual_stones:
            child_text += build_boss_string(reward, color, world)
    child_text += get_hint('Child Altar Text End', world.settings.clearer_hints).text
    child_text += '\x0B'
    update_message_by_id(messages, 0x707A, get_raw_text(child_text), 0x20)

    # text that appears at altar as an adult.
    adult_text = '\x08'
    adult_text += get_hint('Adult Altar Text Start', world.settings.clearer_hints).text + '\x04'
    if include_rewards:
        boss_rewards_medallions = [(reward, REWARD_COLORS[reward]) for reward in (
            'Light Medallion',
            'Forest Medallion',
            'Fire Medallion',
            'Water Medallion',
            'Shadow Medallion',
            'Spirit Medallion',
        )]
        for (reward, color) in boss_rewards_medallions:
            adult_text += build_boss_string(reward, color, world)
    if include_wincons:
        adult_text += build_bridge_reqs_string(world)
        adult_text += '\x04'
        adult_text += build_ganon_boss_key_string(world)
    else:
        adult_text += get_hint('Adult Altar Text End', world.settings.clearer_hints).text
    adult_text += '\x0B'
    update_message_by_id(messages, 0x7057, get_raw_text(adult_text), 0x20)


# pulls text string from hintlist for reward after sending the location to hintlist.
def build_boss_string(reward: str, color: str, world: World) -> str:
    item_icon = chr(Item(reward).special['item_id'])
    if reward in world.distribution.effective_starting_items and world.distribution.effective_starting_items[reward].count > 0:
        if world.settings.clearer_hints:
            text = GossipText(f"\x08\x13{item_icon}One #@ already has#...", [color], prefix='')
        else:
            text = GossipText(f"\x08\x13{item_icon}One in #@'s pocket#...", [color], prefix='')
    else:
        location = world.hinted_dungeon_reward_locations[reward]
        location_text = HintArea.at(location).text(world.settings.clearer_hints, preposition=True, world=None if location.world.id == world.id else location.world.id + 1)
        text = GossipText(f"\x08\x13{item_icon}One {location_text}...", [color], prefix='')
    return str(text) + '\x04'


def build_bridge_reqs_string(world: World) -> str:
    string = "\x13\x3C" # Master Sword icon
    if world.settings.bridge == 'open':
        string += "The awakened ones will have #already created a bridge# to the castle where the evil dwells."
    else:
        if world.settings.bridge == 'vanilla':
            item_req_string = "the #Shadow and Spirit Medallions# as well as the #Light Arrows#"
        else:
            count, singular, plural = {
                'stones':     (world.settings.bridge_stones,     "#Spiritual Stone#",              "#Spiritual Stones#"),
                'medallions': (world.settings.bridge_medallions, "#Medallion#",                    "#Medallions#"),
                'dungeons':   (world.settings.bridge_rewards,    "#Spiritual Stone or Medallion#", "#Spiritual Stones and Medallions#"),
                'tokens':     (world.settings.bridge_tokens,     "#Gold Skulltula Token#",         "#Gold Skulltula Tokens#"),
                'hearts':     (world.settings.bridge_hearts,     "#heart#",                        "#hearts#"),
            }[world.settings.bridge]
            item_req_string = f'{count} {singular if count == 1 else plural}'
        if world.settings.clearer_hints:
            string += f"The rainbow bridge will be built once the Hero collects {item_req_string}."
        else:
            string += f"The awakened ones will await for the Hero to collect {item_req_string}."
    return str(GossipText(string, ['Green'], prefix=''))


def build_ganon_boss_key_string(world: World) -> str:
    string = "\x13\x74" # Boss Key Icon
    if world.settings.shuffle_ganon_bosskey == 'remove':
        string += "And the door to the \x05\x41evil one\x05\x40's chamber will be left #unlocked#."
    else:
        if world.settings.shuffle_ganon_bosskey == 'on_lacs':
            if world.settings.lacs_condition == 'vanilla':
                item_req_string = "the #Shadow and Spirit Medallions#"
                count = 2
            else:
                count, singular, plural = {
                    'stones':     (world.settings.lacs_stones,     "#Spiritual Stone#",              "#Spiritual Stones#"),
                    'medallions': (world.settings.lacs_medallions, "#Medallion#",                    "#Medallions#"),
                    'dungeons':   (world.settings.lacs_rewards,    "#Spiritual Stone or Medallion#", "#Spiritual Stones and Medallions#"),
                    'tokens':     (world.settings.lacs_tokens,     "#Gold Skulltula Token#",         "#Gold Skulltula Tokens#"),
                    'hearts':     (world.settings.lacs_hearts,     "#heart#",                        "#hearts#"),
                }[world.settings.lacs_condition]
                item_req_string = f'{count} {singular if count == 1 else plural}'
            bk_location_string = f"provided by Zelda once {item_req_string} {'is' if count == 1 else 'are'} retrieved"
        elif world.settings.shuffle_ganon_bosskey in ('stones', 'medallions', 'dungeons', 'tokens', 'hearts'):
            count, singular, plural = {
                'stones':     (world.settings.ganon_bosskey_stones,     "#Spiritual Stone#",              "#Spiritual Stones#"),
                'medallions': (world.settings.ganon_bosskey_medallions, "#Medallion#",                    "#Medallions#"),
                'dungeons':   (world.settings.ganon_bosskey_rewards,    "#Spiritual Stone or Medallion#", "#Spiritual Stones and Medallions#"),
                'tokens':     (world.settings.ganon_bosskey_tokens,     "#Gold Skulltula Token#",         "#Gold Skulltula Tokens#"),
                'hearts':     (world.settings.ganon_bosskey_hearts,     "#heart#",                        "#hearts#"),
            }[world.settings.shuffle_ganon_bosskey]
            item_req_string = f'{count} {singular if count == 1 else plural}'
            bk_location_string = f"automatically granted once {item_req_string} {'is' if count == 1 else 'are'} retrieved"
        else:
            bk_location_string = get_hint('ganonBK_' + world.settings.shuffle_ganon_bosskey,
                                          world.settings.clearer_hints).text
        string += "And the \x05\x41evil one\x05\x40's key will be %s." % bk_location_string
    return str(GossipText(string, ['Yellow'], prefix=''))


# fun new lines for Ganon during the final battle
def build_ganon_text(world: World, messages: list[Message]) -> None:
    # empty now unused messages to make space for ganon lines
    update_message_by_id(messages, 0x70C8, " ")
    update_message_by_id(messages, 0x70C9, " ")
    update_message_by_id(messages, 0x70CA, " ")

    # lines before battle
    ganonLines = get_hint_group('ganonLine', world)
    random.shuffle(ganonLines)
    text = get_raw_text(ganonLines.pop().text)
    update_message_by_id(messages, 0x70CB, text)


def build_misc_item_hints(world: World, messages: list[Message], allow_duplicates: bool = False) -> None:
    for hint_type, data in misc_item_hint_table.items():
        if hint_type in world.settings.misc_hints:
            item = world.misc_hint_items[hint_type]
            if item in world.distribution.effective_starting_items and world.distribution.effective_starting_items[item].count > 0:
                if item == data['default_item']:
                    text = data['default_item_text'].format(area='#your pocket#')
                else:
                    text = data['custom_item_text'].format(area='#your pocket#', item=item)
            elif hint_type in world.misc_hint_item_locations:
                location = world.misc_hint_item_locations[hint_type]
                area = HintArea.at(location, use_alt_hint=data['use_alt_hint']).text(world.settings.clearer_hints, world=None if location.world.id == world.id else location.world.id + 1)
                if item == data['default_item']:
                    text = data['default_item_text'].format(area=area)
                else:
                    text = data['custom_item_text'].format(area=area, item=get_hint(get_item_generic_name(location.item), world.settings.clearer_hints).text)
            elif 'custom_item_fallback' in data:
                if 'default_item_fallback' in data and item == data['default_item']:
                    text = data['default_item_fallback']
                else:
                    text = data['custom_item_fallback'].format(item=item)
            else:
                text = get_hint('Validation Line', world.settings.clearer_hints).text
                for location in world.get_filled_locations():
                    if location.name == 'Ganons Tower Boss Key Chest':
                        text += f"#{get_hint(get_item_generic_name(location.item), world.settings.clearer_hints).text}#"
                        break
            for find, replace in data.get('replace', {}).items():
                text = text.replace(find, replace)

            update_message_by_id(messages, data['id'], str(GossipText(text, ['Green'], prefix='')), allow_duplicates=allow_duplicates)


def build_misc_location_hints(world: World, messages: list[Message]) -> None:
    for hint_type, data in misc_location_hint_table.items():
        text = data['location_fallback']
        if hint_type in world.settings.misc_hints:
            if hint_type in world.misc_hint_location_items:
                item = world.misc_hint_location_items[hint_type]
                text = data['location_text'].format(item=get_hint(get_item_generic_name(item),
                                                                  world.settings.clearer_hints).text)

        update_message_by_id(messages, data['id'], str(GossipText(text, ['Green'], prefix='')), 0x23)


def get_raw_text(string: str) -> str:
    text = ''
    for char in string:
        if char == '^':
            text += '\x04' # box break
        elif char == '&':
            text += '\x01' # new line
        elif char == '@':
            text += '\x0F' # print player name
        elif char == '#':
            text += '\x05\x40' # sets color to white
        else:
            text += char
    return text


# build a list of elements in English
def natjoin(elements: Iterable[str], conjunction: str = 'and') -> Optional[str]:
    elements = list(elements)
    if len(elements) == 0:
        return None
    elif len(elements) == 1:
        return elements[0]
    elif len(elements) == 2:
        return f'{elements[0]} {conjunction} {elements[1]}'
    else:
        *rest, last = elements
        return f'{", ".join(rest)}, {conjunction} {last}'


def hint_dist_files() -> list[str]:
    return [os.path.join(data_path('Hints/'), d) for d in defaultHintDists] + [
            os.path.join(data_path('Hints/'), d)
            for d in sorted(os.listdir(data_path('Hints/')))
            if d.endswith('.json') and d not in defaultHintDists]


def hint_dist_list() -> dict[str, str]:
    dists = {}
    for d in hint_dist_files():
        with open(d, 'r') as dist_file:
            try:
                dist = json.load(dist_file)
            except json.JSONDecodeError as e:
                raise ValueError(f'Could not parse hint distribution file {os.path.basename(d)!r}. Make sure the file is valid JSON or reach out to Support on Discord for help. Details: {e}') from e
        dists[dist['name']] = dist['gui_name']
    return dists


def hint_dist_tips() -> str:
    tips = ""
    first_dist = True
    line_char_limit = 33
    for d in hint_dist_files():
        if not first_dist:
            tips = tips + "\n"
        else:
            first_dist = False
        with open(d, 'r') as dist_file:
            dist = json.load(dist_file)
        gui_name = dist['gui_name']
        desc = dist['description']
        i = 0
        end_of_line = False
        tips = tips + "<b>"
        for c in gui_name:
            if c == " " and end_of_line:
                tips = tips + "\n"
                end_of_line = False
            else:
                tips = tips + c
                i = i + 1
                if i > line_char_limit:
                    end_of_line = True
                    i = 0
        tips = tips + "</b>: "
        i = i + 2
        for c in desc:
            if c == " " and end_of_line:
                tips = tips + "\n"
                end_of_line = False
            else:
                tips = tips + c
                i = i + 1
                if i > line_char_limit:
                    end_of_line = True
                    i = 0
        tips = tips + "\n"
    return tips
