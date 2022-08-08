import logging
import os
import random
from collections import OrderedDict
import urllib.request
from urllib.error import URLError, HTTPError
import json
from enum import Enum
import itertools

from HintList import getHint, getMulti, getHintGroup, getUpgradeHintList, hintExclusions, misc_item_hint_table
from Item import MakeEventItem
from Messages import COLOR_MAP, update_message_by_id
from Region import Region
from Search import Search
from TextBox import line_wrap
from Utils import random_choices, data_path


bingoBottlesForHints = (
    "Bottle", "Bottle with Red Potion","Bottle with Green Potion", "Bottle with Blue Potion",
    "Bottle with Fairy", "Bottle with Fish", "Bottle with Blue Fire", "Bottle with Bugs",
    "Bottle with Big Poe", "Bottle with Poe",
)

defaultHintDists = [
    'balanced.json', 'bingo.json', 'chaos.json', 'ddr.json', 'scrubs.json', 'strong.json', 'tournament.json', 'useless.json', 'very_strong.json', 'very_strong_magic.json', 'weekly.json'
]

unHintableWothItems = ['Triforce Piece', 'Gold Skulltula Token']

class RegionRestriction(Enum):
    NONE = 0,
    DUNGEON = 1,
    OVERWORLD = 2,


class GossipStone():
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.reachable = True


class GossipText():
    def __init__(self, text, colors=None, hinted_locations=None, hinted_items=None, prefix="They say that "):
        text = prefix + text
        text = text[:1].upper() + text[1:]
        self.text = text
        self.colors = colors
        self.hinted_locations = hinted_locations
        self.hinted_items = hinted_items


    def to_json(self):
        return {'text': self.text, 'colors': self.colors, 'hinted_locations': self.hinted_locations, 'hinted_items': self.hinted_items}


    def __str__(self):
        return get_raw_text(line_wrap(colorText(self)))

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

gossipLocations = {
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

gossipLocations_reversemap = {
    stone.name : stone_id for stone_id, stone in gossipLocations.items()
}

def getItemGenericName(item):
    if item.unshuffled_dungeon_item:
        return item.type
    else:
        return item.name


def is_restricted_dungeon_item(item):
    return (
        ((item.map or item.compass) and item.world.settings.shuffle_mapcompass == 'dungeon') or
        (item.type == 'SmallKey' and item.world.settings.shuffle_smallkeys == 'dungeon') or
        (item.type == 'BossKey' and item.world.settings.shuffle_bosskeys == 'dungeon') or
        (item.type == 'GanonBossKey' and item.world.settings.shuffle_ganon_bosskey == 'dungeon')
    )


def add_hint(spoiler, world, groups, gossip_text, count, locations=[], force_reachable=False):
    random.shuffle(groups)
    skipped_groups = []
    duplicates = []
    first = True
    success = True
    # early failure if not enough
    if len(groups) < int(count):
        return False
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
                                event_item = MakeEventItem(stone_name, stone_locations[i], event_item)
                            else:
                                MakeEventItem(stone_name, stone_locations[i], event_item)

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


def can_reach_hint(worlds, hint_location, location):
    if location == None:
        return True

    old_item = location.item
    location.item = None
    search = Search.max_explore([world.state for world in worlds])
    location.item = old_item

    return (search.spot_access(hint_location)
            and (hint_location.type != 'HintStone' or search.state_list[location.world.id].guarantee_hint()))


def writeGossipStoneHints(spoiler, world, messages):
    for id, gossip_text in spoiler.hints[world.id].items():
        update_message_by_id(messages, id, str(gossip_text), 0x23)


def filterTrailingSpace(text):
    if text.endswith('& '):
        return text[:-1]
    else:
        return text


hintPrefixes = [
    'a few ',
    'some ',
    'plenty of ',
    'a ',
    'an ',
    'the ',
    '',
]

def getSimpleHintNoPrefix(item):
    hint = getHint(item.name, True).text

    for prefix in hintPrefixes:
        if hint.startswith(prefix):
            # return without the prefix
            return hint[len(prefix):]

    # no prefex
    return hint


def colorText(gossip_text):
    text = gossip_text.text
    colors = list(gossip_text.colors) if gossip_text.colors is not None else []
    color = 'White'

    while '#' in text:
        splitText = text.split('#', 2)
        if len(colors) > 0:
            color = colors.pop()

        for prefix in hintPrefixes:
            if splitText[1].startswith(prefix):
                splitText[0] += splitText[1][:len(prefix)]
                splitText[1] = splitText[1][len(prefix):]
                break

        splitText[1] = '\x05' + COLOR_MAP[color] + splitText[1] + '\x05\x40'
        text = ''.join(splitText)

    return text


class HintAreaNotFound(RuntimeError):
    pass


class HintArea(Enum):
    # internal name          prepositions        display name                  color         internal dungeon name
    #                        vague     clear
    ROOT                   = 'in',     'in',     "Link's Pocket",              'White',      None
    HYRULE_FIELD           = 'in',     'in',     'Hyrule Field',               'Light Blue', None
    LON_LON_RANCH          = 'at',     'at',     'Lon Lon Ranch',              'Light Blue', None
    MARKET                 = 'in',     'in',     'the Market',                 'Light Blue', None
    TEMPLE_OF_TIME         = 'inside', 'inside', 'the Temple of Time',         'Light Blue', None
    CASTLE_GROUNDS         = 'on',     'on',     'the Castle Grounds',         'Light Blue', None # required for warp songs
    HYRULE_CASTLE          = 'at',     'at',     'Hyrule Castle',              'Light Blue', None
    OUTSIDE_GANONS_CASTLE  = None,     None,     "outside Ganon's Castle",     'Light Blue', None
    INSIDE_GANONS_CASTLE   = 'inside', None,     "inside Ganon's Castle",      'Light Blue', 'Ganons Castle'
    KOKIRI_FOREST          = 'in',     'in',     'Kokiri Forest',              'Green',      None
    DEKU_TREE              = 'inside', 'inside', 'the Deku Tree',              'Green',      'Deku Tree'
    LOST_WOODS             = 'in',     'in',     'the Lost Woods',             'Green',      None
    SACRED_FOREST_MEADOW   = 'at',     'at',     'the Sacred Forest Meadow',   'Green',      None
    FOREST_TEMPLE          = 'in',     'in',     'the Forest Temple',          'Green',      'Forest Temple'
    DEATH_MOUNTAIN_TRAIL   = 'on',     'on',     'the Death Mountain Trail',   'Red',        None
    DODONGOS_CAVERN        = 'within', 'in',     "Dodongo's Cavern",           'Red',        'Dodongos Cavern'
    GORON_CITY             = 'in',     'in',     'Goron City',                 'Red',        None
    DEATH_MOUNTAIN_CRATER  = 'in',     'in',     'the Death Mountain Crater',  'Red',        None
    FIRE_TEMPLE            = 'on',     'in',     'the Fire Temple',            'Red',        'Fire Temple'
    ZORA_RIVER             = 'at',     'at',     "Zora's River",               'Blue',       None
    ZORAS_DOMAIN           = 'at',     'at',     "Zora's Domain",              'Blue',       None
    ZORAS_FOUNTAIN         = 'at',     'at',     "Zora's Fountain",            'Blue',       None
    JABU_JABUS_BELLY       = 'in',     'inside', "Jabu Jabu's Belly",          'Blue',       'Jabu Jabus Belly'
    ICE_CAVERN             = 'inside', 'in'    , 'the Ice Cavern',             'Blue',       'Ice Cavern'
    LAKE_HYLIA             = 'at',     'at',     'Lake Hylia',                 'Blue',       None
    WATER_TEMPLE           = 'under',  'in',     'the Water Temple',           'Blue',       'Water Temple'
    KAKARIKO_VILLAGE       = 'in',     'in',     'Kakariko Village',           'Pink',       None
    BOTTOM_OF_THE_WELL     = 'within', 'at',     'the Bottom of the Well',     'Pink',       'Bottom of the Well'
    GRAVEYARD              = 'in',     'in',     'the Graveyard',              'Pink',       None
    SHADOW_TEMPLE          = 'within', 'in',     'the Shadow Temple',          'Pink',       'Shadow Temple'
    GERUDO_VALLEY          = 'at',     'at',     'Gerudo Valley',              'Yellow',     None
    GERUDO_FORTRESS        = 'at',     'at',     "Gerudo's Fortress",          'Yellow',     None
    GERUDO_TRAINING_GROUND = 'within', 'on',     'the Gerudo Training Ground', 'Yellow',     'Gerudo Training Ground'
    HAUNTED_WASTELAND      = 'in',     'in',     'the Haunted Wasteland',      'Yellow',     None
    DESERT_COLOSSUS        = 'at',     'at',     'the Desert Colossus',        'Yellow',     None
    SPIRIT_TEMPLE          = 'inside', 'in',     'the Spirit Temple',          'Yellow',     'Spirit Temple'

    # Peforms a breadth first search to find the closest hint area from a given spot (region, location, or entrance).
    # May fail to find a hint if the given spot is only accessible from the root and not from any other region with a hint area
    @staticmethod
    def at(spot):
        if isinstance(spot, Region):
            original_parent = spot
        else:
            original_parent = spot.parent_region
        already_checked = []
        spot_queue = [spot]

        while spot_queue:
            current_spot = spot_queue.pop(0)
            already_checked.append(current_spot)

            if isinstance(current_spot, Region):
                parent_region = current_spot
            else:
                parent_region = current_spot.parent_region

            if parent_region.hint and (original_parent.name == 'Root' or parent_region.name != 'Root'):
                return parent_region.hint

            spot_queue.extend(list(filter(lambda ent: ent not in already_checked, parent_region.entrances)))

        raise HintAreaNotFound('No hint area could be found for %s [World %d]' % (spot, spot.world.id))

    def __str__(self):
        return self.value[2]

    # Hint areas are further grouped into colored sections of the map by association with the medallions.
    # These colors are used to generate the text boxes for shuffled warp songs.
    @property
    def color(self):
        return self.value[3]

    @property
    def dungeon_name(self):
        return self.value[4]

    @property
    def is_dungeon(self):
        return self.dungeon_name is not None

    def is_dungeon_item(self, item):
        for dungeon in item.world.dungeons:
            if dungeon.name == self.dungeon_name:
                return dungeon.is_dungeon_item(item)
        return False

    def preposition(self, clearer_hints):
        return self.value[1 if clearer_hints else 0]

    # Formats the hint text for this area with proper grammar.
    # Dungeons are hinted differently depending on the clearer_hints setting.
    def text(self, clearer_hints, preposition=False, world=None):
        if self.is_dungeon:
            text = getHint(self.dungeon_name, clearer_hints).text
        else:
            text = str(self)
        prefix, suffix = text.replace('#', '').split(' ', 1)
        if world is None:
            if prefix == "Link's":
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


def get_woth_hint(spoiler, world, checked):
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

    return (GossipText('%s is on the way of the hero.' % location_text, ['Light Blue'], [location.name], [location.item.name]), [location])

def get_checked_areas(world, checked):
    def get_area_from_name(check):
        try:
            location = world.get_location(check)
        except Exception:
            return check
        return HintArea.at(location)

    return set(get_area_from_name(check) for check in checked)

def get_goal_category(spoiler, world, goal_categories):
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

def get_goal_hint(spoiler, world, checked):
    goal_category = get_goal_category(spoiler, world, world.goal_categories)

    # check if no goals were generated (and thus no categories available)
    if not goal_category:
        return None

    goals = goal_category.goals
    goal_locations = []

    # Choose random goal and check if any locations are already hinted.
    # If all locations for a goal are hinted, remove the goal from the list and try again.
    # If all locations for all goals are hinted, try remaining goal categories
    # If all locations for all goal categories are hinted, return no hint.
    while not goal_locations:
        if not goals:
            del world.goal_categories[goal_category.name]
            goal_category = get_goal_category(spoiler, world, world.goal_categories)
            if not goal_category:
                return None
            else:
                goals = goal_category.goals

        weights = []
        zero_weights = True
        for goal in goals:
            if goal.weight > 0:
                zero_weights = False
            weights.append(goal.weight)

        if zero_weights:
            goal = random.choice(goals)
        else:
            goal = random.choices(goals, weights=weights)[0]

        goal_locations = list(filter(lambda location:
            location[0].name not in checked
            and location[0].name not in world.hint_exclusions
            and location[0].name not in world.hint_type_overrides['goal']
            and location[0].item.name not in world.item_hint_type_overrides['goal']
            and location[0].item.name not in unHintableWothItems,
            goal.required_locations))

        if not goal_locations:
            goals.remove(goal)

    # Goal weight to zero mitigates double hinting this goal
    # Once all goals in a category are 0, selection is true random
    goal.weight = 0
    location_tuple = random.choice(goal_locations)
    location = location_tuple[0]
    world_ids = location_tuple[3]
    world_id = random.choice(world_ids)
    checked.add(location.name)

    location_text = HintArea.at(location).text(world.settings.clearer_hints)
    if world_id == world.id:
        player_text = "the"
        goal_text = goal.hint_text
    else:
        player_text = "Player %s's" % (world_id + 1)
        goal_text = spoiler.goal_categories[world_id][goal_category.name].get_goal(goal.name).hint_text

    return (GossipText('%s is on %s %s.' % (location_text, player_text, goal_text), [goal.color, 'Light Blue'], [location.name], [location.item.name]), [location])


def get_barren_hint(spoiler, world, checked, allChecked):
    if not hasattr(world, 'get_barren_hint_prev'):
        world.get_barren_hint_prev = RegionRestriction.NONE

    checked_areas = get_checked_areas(world, checked)
    areas = list(filter(lambda area:
        area not in checked_areas
        and area not in world.hint_type_overrides['barren']
        and not (world.barren_dungeon >= world.hint_dist_user['dungeons_barren_limit'] and world.empty_areas[area]['dungeon'])
        and any(
            location.name not in allChecked
            and location.name not in world.hint_exclusions
            and location.name not in hintExclusions(world)
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

    area = random_choices(areas, weights=area_weights)[0]
    if world.empty_areas[area]['dungeon']:
        world.barren_dungeon += 1

    checked.add(area)

    return (GossipText("plundering %s is a foolish choice." % area.text(world.settings.clearer_hints), ['Pink']), None)


def is_not_checked(locations, checked):
    return not any(location.name in checked or HintArea.at(location) in checked for location in locations)


def get_good_item_hint(spoiler, world, checked):
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

    item_text = getHint(getItemGenericName(location.item), world.settings.clearer_hints).text
    hint_area = HintArea.at(location)
    if hint_area.is_dungeon:
        location_text = hint_area.text(world.settings.clearer_hints)
        return (GossipText('%s hoards #%s#.' % (location_text, item_text), ['Green', 'Red'], [location.name], [location.item.name]), [location])
    else:
        location_text = hint_area.text(world.settings.clearer_hints, preposition=True)
        return (GossipText('#%s# can be found %s.' % (item_text, location_text), ['Red', 'Green'], [location.name], [location.item.name]), [location])


def get_specific_item_hint(spoiler, world, checked):
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
        item_text = getHint(getItemGenericName(location.item), world.settings.clearer_hints).text

        hint_area = HintArea.at(location)
        if world.hint_dist_user.get('vague_named_items', False):
            location_text = hint_area.text(world.settings.clearer_hints)
            return (GossipText('%s may be on the hero\'s path.' % (location_text), ['Green'], [location.name], [location.item.name]), [location])
        elif hint_area.is_dungeon:
            location_text = hint_area.text(world.settings.clearer_hints)
            return (GossipText('%s hoards #%s#.' % (location_text, item_text), ['Green', 'Red'], [location.name], [location.item.name]), [location])
        else:
            location_text = hint_area.text(world.settings.clearer_hints, preposition=True)
            return (GossipText('#%s# can be found %s.' % (item_text, location_text), ['Red', 'Green'], [location.name], [location.item.name]), [location])

    else:
        while True:
            #This operation is likely to be costly (especially for large multiworlds), so cache the result for later
            #named_item_locations: Filtered locations from all worlds that may contain named-items
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

                always_hints = [(hint, w.id) for w in worlds for hint in getHintGroup('always', w)]                    
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
        item_text = getHint(getItemGenericName(location.item), world.settings.clearer_hints).text

        hint_area = HintArea.at(location)
        if world.hint_dist_user.get('vague_named_items', False):
            location_text = hint_area.text(world.settings.clearer_hints, world=location.world.id + 1)
            return (GossipText('%s may be on the hero\'s path.' % (location_text), ['Green'], [location.name], [location.item.name]), [location])
        elif hint_area.is_dungeon:
            location_text = hint_area.text(world.settings.clearer_hints, world=location.world.id + 1)
            return (GossipText('%s hoards #%s#.' % (location_text, item_text), ['Green', 'Red'], [location.name], [location.item.name]), [location])
        else:
            location_text = hint_area.text(world.settings.clearer_hints, preposition=True, world=location.world.id + 1)
            return (GossipText('#%s# can be found %s.' % (item_text, location_text), ['Red', 'Green'], [location.name], [location.item.name]), [location])


def get_random_location_hint(spoiler, world, checked):
    locations = list(filter(lambda location:
        is_not_checked([location], checked)
        and location.item.type not in ('Drop', 'Event', 'Shop', 'DungeonReward')
        and not is_restricted_dungeon_item(location.item)
        and not location.locked
        and location.name not in world.hint_exclusions
        and location.name not in world.hint_type_overrides['item']
        and location.item.name not in world.item_hint_type_overrides['item'],
        world.get_filled_locations()))
    if not locations:
        return None

    location = random.choice(locations)
    checked.add(location.name)
    item_text = getHint(getItemGenericName(location.item), world.settings.clearer_hints).text

    hint_area = HintArea.at(location)
    if hint_area.is_dungeon:
        location_text = hint_area.text(world.settings.clearer_hints)
        return (GossipText('%s hoards #%s#.' % (location_text, item_text), ['Green', 'Red'], [location.name], [location.item.name]), [location])
    else:
        location_text = hint_area.text(world.settings.clearer_hints, preposition=True)
        return (GossipText('#%s# can be found %s.' % (item_text, location_text), ['Red', 'Green'], [location.name], [location.item.name]), [location])


def get_specific_hint(spoiler, world, checked, type):
    hintGroup = getHintGroup(type, world)
    hintGroup = list(filter(lambda hint: is_not_checked([world.get_location(hint.name)], checked), hintGroup))
    if not hintGroup:
        return None

    hint = random.choice(hintGroup)

    if world.hint_dist_user['upgrade_hints'] in ['on', 'limited']:
        upgrade_list = getUpgradeHintList(world, [hint.name])
        upgrade_list = list(filter(lambda upgrade: is_not_checked([world.get_location(location) for location in getMulti(upgrade.name).locations], checked), upgrade_list))

        if upgrade_list is not None:
            multi = None

            for upgrade in upgrade_list:
                upgrade_multi = getMulti(upgrade.name)

                if not multi or len(multi.locations) < len(upgrade_multi.locations):
                    hint = upgrade
                    multi = getMulti(hint.name)

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
    item_text = getHint(getItemGenericName(location.item), world.settings.clearer_hints).text

    return (GossipText('%s #%s#.' % (location_text, item_text), ['Green', 'Red'], [location.name], [location.item.name]), [location])


def get_sometimes_hint(spoiler, world, checked):
    return get_specific_hint(spoiler, world, checked, 'sometimes')


def get_song_hint(spoiler, world, checked):
    return get_specific_hint(spoiler, world, checked, 'song')


def get_overworld_hint(spoiler, world, checked):
    return get_specific_hint(spoiler, world, checked, 'overworld')


def get_dungeon_hint(spoiler, world, checked):
    return get_specific_hint(spoiler, world, checked, 'dungeon')

def get_random_multi_hint(spoiler, world, checked, type):
    hint_group = getHintGroup(type, world)
    multi_hints = list(filter(lambda hint: is_not_checked([world.get_location(location) for location in getMulti(hint.name).locations], checked), hint_group))

    if not multi_hints:
        return None

    hint = random.choice(multi_hints)

    if world.hint_dist_user['upgrade_hints'] in ['on', 'limited']:
        multi = getMulti(hint.name)

        upgrade_list = getUpgradeHintList(world, multi.locations)
        upgrade_list = list(filter(lambda upgrade: is_not_checked([world.get_location(location) for location in getMulti(upgrade.name).locations], checked), upgrade_list))

        if upgrade_list:
            for upgrade in upgrade_list:
                upgrade_multi = getMulti(upgrade.name)

                if len(multi.locations) < len(upgrade_multi.locations):
                    hint = upgrade
                    multi = getMulti(hint.name)

    return get_specific_multi_hint(spoiler, world, checked, hint)

def get_specific_multi_hint(spoiler, world, checked, hint):
    multi = getMulti(hint.name)
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
        colors = ['Green'] + colors
        if i == location_count - 1:
            gossip_string = gossip_string + 'and #%s#'
        else:
            gossip_string = gossip_string + '#%s# '

    items = [location.item for location in locations]
    text_segments = [multi_text] + [getHint(getItemGenericName(item), world.settings.clearer_hints).text for item in items]
    return (GossipText(gossip_string % tuple(text_segments), colors, [location.name for location in locations], [item.name for item in items]), locations)

def get_dual_hint(spoiler, world, checked):
    return get_random_multi_hint(spoiler, world, checked, 'dual')

def get_entrance_hint(spoiler, world, checked):
    if not world.entrance_shuffle:
        return None

    entrance_hints = list(filter(lambda hint: hint.name not in checked, getHintGroup('entrance', world)))
    shuffled_entrance_hints = list(filter(lambda entrance_hint: world.get_entrance(entrance_hint.name).shuffled, entrance_hints))

    regions_with_hint = [hint.name for hint in getHintGroup('region', world)]
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
        region_text = getHint(connected_region.dungeon.name, world.settings.clearer_hints).text
    else:
        region_text = getHint(connected_region.name, world.settings.clearer_hints).text

    if '#' not in region_text:
        region_text = '#%s#' % region_text

    return (GossipText('%s %s.' % (entrance_text, region_text), ['Light Blue', 'Green']), None)


def get_junk_hint(spoiler, world, checked):
    hints = getHintGroup('junk', world)
    hints = list(filter(lambda hint: hint.name not in checked, hints))
    if not hints:
        return None

    hint = random.choice(hints)
    checked.add(hint.name)

    return (GossipText(hint.text, prefix=''), None)


hint_func = {
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
    'named-item':       get_specific_item_hint
}

hint_dist_keys = {
    'trial',
    'always',
    'dual_always',
    'entrance_always',
    'woth',
    'goal',
    'barren',
    'item',
    'song',
    'overworld',
    'dungeon',
    'entrance',
    'sometimes',
    'dual',
    'random',
    'junk',
    'named-item'
}


def buildBingoHintList(boardURL):
    try:
        if len(boardURL) > 256:
            raise URLError(f"URL too large {len(boardURL)}")
        with urllib.request.urlopen(boardURL + "/board") as board:
            if board.length and 0 < board.length < 4096:
                goalList = board.read()
            else:
                raise HTTPError(f"Board of invalid size {board.length}")
    except (URLError, HTTPError) as e:
        logger = logging.getLogger('')
        logger.info(f"Could not retrieve board info. Using default bingo hints instead: {e}")
        with open(data_path('Bingo/generic_bingo_hints.json'), 'r') as bingoFile:
            genericBingo = json.load(bingoFile)
        return genericBingo['settings']['item_hints']

    # Goal list returned from Bingosync is a sequential list of all of the goals on the bingo board, starting at top-left and moving to the right.
    # Each goal is a dictionary with attributes for name, slot, and colours. The only one we use is the name
    goalList = [goal['name'] for goal in json.loads(goalList)]
    with open(data_path('Bingo/bingo_goals.json'), 'r') as bingoFile:
        goalHintRequirements = json.load(bingoFile)

    hintsToAdd = {}
    for goal in goalList:
        # Using 'get' here ensures some level of forward compatibility, where new goals added to randomiser bingo won't
        # cause the generator to crash (though those hints won't have item hints for them)
        requirements = goalHintRequirements.get(goal,{})
        if len(requirements) != 0:
            for item in requirements:
                hintsToAdd[item] = max(hintsToAdd.get(item, 0), requirements[item]['count'])

    # Items to be hinted need to be included in the item_hints list once for each instance you want hinted
    # (e.g. if you want all three strength upgrades to be hintes it needs to be in the list three times)
    hints = []
    for key, value in hintsToAdd.items():
        for _ in range(value):
            hints.append(key)

    #Since there's no way to verify if the Bingosync URL is actually for OoTR, this exception catches that case
    if len(hints) == 0:
        raise Exception('No item hints found for goals on Bingosync card. Verify Bingosync URL is correct, or leave field blank for generic bingo hints.')
    return hints


def alwaysNamedItem(world, locations):
    for location in locations:
        if location.item.name in bingoBottlesForHints and world.settings.hint_dist == 'bingo':
            always_item = 'Bottle'
        else:
            always_item = location.item.name
        if always_item in world.named_item_pool and world.settings.world_count == 1:
            world.named_item_pool.remove(always_item)


def buildGossipHints(spoiler, worlds):
    checkedLocations = dict()
    # Add misc. item hint locations to "checked" locations if the respective hint is reachable without the hinted item.
    for world in worlds:
        for hint_type, location in world.misc_hint_item_locations.items():
            if hint_type in world.settings.misc_hints and can_reach_hint(worlds, world.get_location(misc_item_hint_table[hint_type]['hint_location']), location):
                item_world = location.world
                if item_world.id not in checkedLocations:
                    checkedLocations[item_world.id] = set()
                checkedLocations[item_world.id].add(location.name)

    # Build all the hints.
    for world in worlds:
        world.update_useless_areas(spoiler)
        buildWorldGossipHints(spoiler, world, checkedLocations.pop(world.id, None))


# builds out general hints based on location and whether an item is required or not
def buildWorldGossipHints(spoiler, world, checkedLocations=None):

    world.barren_dungeon = 0
    world.woth_dungeon = 0

    search = Search.max_explore([w.state for w in spoiler.worlds])
    for stone in gossipLocations.values():
        stone.reachable = (
            search.spot_access(world.get_location(stone.location))
            and search.state_list[world.id].guarantee_hint())

    if checkedLocations is None:
        checkedLocations = set()
    checkedAlwaysLocations = set()

    stoneIDs = list(gossipLocations.keys())

    world.distribution.configure_gossip(spoiler, stoneIDs)

    # If all gossip stones already have plando'd hints, do not roll any more
    if len(stoneIDs) == 0:
        return

    if 'disabled' in world.hint_dist_user:
        for stone_name in world.hint_dist_user['disabled']:
            try:
                stone_id = gossipLocations_reversemap[stone_name]
            except KeyError:
                raise ValueError(f'Gossip stone location "{stone_name}" is not valid')
            if stone_id in stoneIDs:
                stoneIDs.remove(stone_id)
                (gossip_text, _) = get_junk_hint(spoiler, world, checkedLocations)
                spoiler.hints[world.id][stone_id] = gossip_text

    stoneGroups = []
    if 'groups' in world.hint_dist_user:
        for group_names in world.hint_dist_user['groups']:
            group = []
            for stone_name in group_names:
                try:
                    stone_id = gossipLocations_reversemap[stone_name]
                except KeyError:
                    raise ValueError(f'Gossip stone location "{stone_name}" is not valid')

                if stone_id in stoneIDs:
                    stoneIDs.remove(stone_id)
                    group.append(stone_id)
            if len(group) != 0:
                stoneGroups.append(group)
    # put the remaining locations into singleton groups
    stoneGroups.extend([[id] for id in stoneIDs])

    random.shuffle(stoneGroups)

    # Create list of items for which we want hints. If Bingosync URL is supplied, include items specific to that bingo.
    # If not (or if the URL is invalid), use generic bingo hints
    if world.settings.hint_dist == "bingo":
        with open(data_path('Bingo/generic_bingo_hints.json'), 'r') as bingoFile:
            bingoDefaults = json.load(bingoFile)
        if world.bingosync_url is not None and world.bingosync_url.startswith("https://bingosync.com/"): # Verify that user actually entered a bingosync URL
            logger = logging.getLogger('')
            logger.info("Got Bingosync URL. Building board-specific goals.")
            world.item_hints = buildBingoHintList(world.bingosync_url)
        else:
            world.item_hints = bingoDefaults['settings']['item_hints']

        if world.settings.tokensanity in ("overworld", "all") and "Suns Song" not in world.item_hints:
            world.item_hints.append("Suns Song")

        if world.settings.shopsanity != "off" and "Progressive Wallet" not in world.item_hints:
            world.item_hints.append("Progressive Wallet")


    #Removes items from item_hints list if they are included in starting gear.
    #This method ensures that the right number of copies are removed, e.g.
    #if you start with one strength and hints call for two, you still get
    #one hint for strength. This also handles items from Skip Child Zelda.
    for itemname, record in world.distribution.effective_starting_items.items():
        for _ in range(record.count):
            if itemname in world.item_hints:
                world.item_hints.remove(itemname)

    world.named_item_pool = list(world.item_hints)

    #Make sure the total number of hints won't pass 40. If so, we limit the always and trial hints
    if world.settings.hint_dist == "bingo":
        numTrialHints = [0,1,2,3,2,1,0]
        if (2*len(world.item_hints) + 2*len(getHintGroup('always', world)) + 2*numTrialHints[world.settings.trials] > 40) and (world.hint_dist_user['named_items_required']):
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
        alwaysDuals = getHintGroup('dual_always', world)
        for hint in alwaysDuals:
            multi = getMulti(hint.name)
            firstLocation = world.get_location(multi.locations[0])
            secondLocation = world.get_location(multi.locations[1])
            checkedAlwaysLocations.add(firstLocation.name)
            checkedAlwaysLocations.add(secondLocation.name)

            alwaysNamedItem(world, [firstLocation, secondLocation])

            if hint.name in world.hint_text_overrides:
                location_text = world.hint_text_overrides[hint.name]
            else:
                location_text = getHint(hint.name, world.settings.clearer_hints).text
            if '#' not in location_text:
                location_text = '#%s#' % location_text
            first_item_text = getHint(getItemGenericName(firstLocation.item), world.settings.clearer_hints).text
            second_item_text = getHint(getItemGenericName(secondLocation.item), world.settings.clearer_hints).text
            add_hint(spoiler, world, stoneGroups, GossipText('%s #%s# and #%s#.' % (location_text, first_item_text, second_item_text), ['Green', 'Green', 'Red'], [firstLocation.name, secondLocation.name], [firstLocation.item.name, secondLocation.item.name]), hint_dist['dual_always'][1], [firstLocation, secondLocation], force_reachable=True)
            logging.getLogger('').debug('Placed dual_always hint for %s.', hint.name)

    # Add required location hints, only if hint copies > 0
    if hint_dist['always'][1] > 0:
        alwaysLocations = list(filter(lambda hint: is_not_checked([world.get_location(hint.name)], checkedAlwaysLocations), getHintGroup('always', world)))
        for hint in alwaysLocations:
            location = world.get_location(hint.name)
            checkedAlwaysLocations.add(hint.name)

            alwaysNamedItem(world, [location])

            if location.name in world.hint_text_overrides:
                location_text = world.hint_text_overrides[location.name]
            else:
                location_text = getHint(location.name, world.settings.clearer_hints).text
            if '#' not in location_text:
                location_text = '#%s#' % location_text
            item_text = getHint(getItemGenericName(location.item), world.settings.clearer_hints).text
            add_hint(spoiler, world, stoneGroups, GossipText('%s #%s#.' % (location_text, item_text), ['Green', 'Red'], [location.name], [location.item.name]), hint_dist['always'][1], [location], force_reachable=True)
            logging.getLogger('').debug('Placed always hint for %s.', location.name)

    # Add required entrance hints, only if hint copies > 0
    if world.entrance_shuffle and 'entrance_always' in hint_dist and hint_dist['entrance_always'][1] > 0:
        alwaysEntrances = getHintGroup('entrance_always', world)
        for entrance_hint in alwaysEntrances:
            entrance = world.get_entrance(entrance_hint.name)
            connected_region = entrance.connected_region
            if entrance.shuffled and (connected_region.dungeon or any(hint.name == connected_region.name for hint in getHintGroup('region', world))):
                checkedAlwaysLocations.add(entrance.name)

                entrance_text = entrance_hint.text
                if '#' not in entrance_text:
                    entrance_text = '#%s#' % entrance_text

                if connected_region.dungeon:
                    region_text = getHint(connected_region.dungeon.name, world.settings.clearer_hints).text
                else:
                    region_text = getHint(connected_region.name, world.settings.clearer_hints).text
                if '#' not in region_text:
                    region_text = '#%s#' % region_text

                add_hint(spoiler, world, stoneGroups, GossipText('%s %s.' % (entrance_text, region_text), ['Light Blue', 'Green']), hint_dist['entrance_always'][1], None, force_reachable=True)

    # Add trial hints, only if hint copies > 0
    if hint_dist['trial'][1] > 0:
        if world.settings.trials_random and world.settings.trials == 6:
            add_hint(spoiler, world, stoneGroups, GossipText("#Ganon's Tower# is protected by a powerful barrier.", ['Pink']), hint_dist['trial'][1], force_reachable=True)
        elif world.settings.trials_random and world.settings.trials == 0:
            add_hint(spoiler, world, stoneGroups, GossipText("Sheik dispelled the barrier around #Ganon's Tower#.", ['Yellow']), hint_dist['trial'][1], force_reachable=True)
        elif world.settings.trials < 6 and world.settings.trials > 3:
            for trial,skipped in world.skipped_trials.items():
                if skipped:
                    add_hint(spoiler, world, stoneGroups,GossipText("the #%s Trial# was dispelled by Sheik." % trial, ['Yellow']), hint_dist['trial'][1], force_reachable=True)
        elif world.settings.trials <= 3 and world.settings.trials > 0:
            for trial,skipped in world.skipped_trials.items():
                if not skipped:
                    add_hint(spoiler, world, stoneGroups, GossipText("the #%s Trial# protects Ganon's Tower." % trial, ['Pink']), hint_dist['trial'][1], force_reachable=True)

    # Add user-specified hinted item locations if using a built-in hint distribution
    # Raise error if hint copies is zero
    if len(world.named_item_pool) > 0 and world.hint_dist_user['named_items_required']:
        if hint_dist['named-item'][1] == 0:
            raise Exception('User-provided item hints were requested, but copies per named-item hint is zero')
        else:
            # Prevent conflict between Ganondorf Light Arrows hint and required named item hints.
            # Assumes that a "wasted" hint is desired since Light Arrows have to be added
            # explicitly to the list for named item hints.
            filtered_checked = set(checkedLocations | checkedAlwaysLocations)
            for location in (checkedLocations | checkedAlwaysLocations):
                if world.get_location(location).item.name == 'Light Arrows':
                    filtered_checked.remove(location)
            for i in range(0, len(world.named_item_pool)):
                hint = get_specific_item_hint(spoiler, world, filtered_checked)
                if hint:
                    checkedLocations.update(filtered_checked - checkedAlwaysLocations)
                    gossip_text, location = hint
                    place_ok = add_hint(spoiler, world, stoneGroups, gossip_text, hint_dist['named-item'][1], location)
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
    while stoneGroups:
        if fixed_hint_types:
            hint_type = fixed_hint_types.pop(0)
            copies = hint_dist[hint_type][1]
            if copies > len(stoneGroups):
                # Quiet to avoid leaking information.
                logging.getLogger('').debug(f'Not enough gossip stone locations ({len(stoneGroups)} groups) for fixed hint type {hint_type} with {copies} copies, proceeding with available stones.')
                copies = len(stoneGroups)
        else:
            custom_fixed = False
            # Make sure there are enough stones left for each hint type
            num_types = len(hint_types)
            hint_types = list(filter(lambda htype: hint_dist[htype][1] <= len(stoneGroups), hint_types))
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

                hint_type = random_choices(hint_types, weights=weighted_hint_prob)[0]
                copies = hint_dist[hint_type][1]
            except IndexError:
                raise Exception('Not enough valid hints to fill gossip stone locations.')

        allCheckedLocations = checkedLocations | checkedAlwaysLocations
        if hint_type == 'barren':
            hint = hint_func[hint_type](spoiler, world, checkedLocations, allCheckedLocations)
        else:
            hint = hint_func[hint_type](spoiler, world, allCheckedLocations)
            checkedLocations.update(allCheckedLocations - checkedAlwaysLocations)

        if hint == None:
            index = hint_types.index(hint_type)
            hint_prob[index] = 0
            # Zero out the probability in the base distribution in case the probability list is modified
            # to fit hint types in remaining gossip stones
            hint_dist[hint_type] = (0.0, copies)
        else:
            gossip_text, locations = hint
            place_ok = add_hint(spoiler, world, stoneGroups, gossip_text, copies, locations)
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
def buildAltarHints(world, messages, include_rewards=True, include_wincons=True):
    # text that appears at altar as a child.
    child_text = '\x08'
    if include_rewards:
        bossRewardsSpiritualStones = [
            ('Kokiri Emerald',   'Green'), 
            ('Goron Ruby',       'Red'), 
            ('Zora Sapphire',    'Blue'),
        ]
        child_text += getHint('Spiritual Stone Text Start', world.settings.clearer_hints).text + '\x04'
        for (reward, color) in bossRewardsSpiritualStones:
            child_text += buildBossString(reward, color, world)
    child_text += getHint('Child Altar Text End', world.settings.clearer_hints).text
    child_text += '\x0B'
    update_message_by_id(messages, 0x707A, get_raw_text(child_text), 0x20)

    # text that appears at altar as an adult.
    adult_text = '\x08'
    adult_text += getHint('Adult Altar Text Start', world.settings.clearer_hints).text + '\x04'
    if include_rewards:
        bossRewardsMedallions = [
            ('Light Medallion',  'Light Blue'),
            ('Forest Medallion', 'Green'),
            ('Fire Medallion',   'Red'),
            ('Water Medallion',  'Blue'),
            ('Shadow Medallion', 'Pink'),
            ('Spirit Medallion', 'Yellow'),
        ]
        for (reward, color) in bossRewardsMedallions:
            adult_text += buildBossString(reward, color, world)
    if include_wincons:
        adult_text += buildBridgeReqsString(world)
        adult_text += '\x04'
        adult_text += buildGanonBossKeyString(world)
    else:
        adult_text += getHint('Adult Altar Text End', world.settings.clearer_hints).text
    adult_text += '\x0B'
    update_message_by_id(messages, 0x7057, get_raw_text(adult_text), 0x20)


# pulls text string from hintlist for reward after sending the location to hintlist.
def buildBossString(reward, color, world):
    for location in world.get_filled_locations():
        if location.item.name == reward:
            item_icon = chr(location.item.special['item_id'])
            location_text = HintArea.at(location).text(world.settings.clearer_hints, preposition=True)
            return str(GossipText("\x08\x13%sOne %s..." % (item_icon, location_text), [color], prefix='')) + '\x04'
    return ''


def buildBridgeReqsString(world):
    string = "\x13\x12" # Light Arrow Icon
    if world.settings.bridge == 'open':
        string += "The awakened ones will have #already created a bridge# to the castle where the evil dwells."
    else:
        item_req_string = getHint('bridge_' + world.settings.bridge, world.settings.clearer_hints).text
        if world.settings.bridge == 'medallions':
            item_req_string = str(world.settings.bridge_medallions) + ' ' + item_req_string
        elif world.settings.bridge == 'stones':
            item_req_string = str(world.settings.bridge_stones) + ' ' + item_req_string
        elif world.settings.bridge == 'dungeons':
            item_req_string = str(world.settings.bridge_rewards) + ' ' + item_req_string
        elif world.settings.bridge == 'tokens':
            item_req_string = str(world.settings.bridge_tokens) + ' ' + item_req_string
        elif world.settings.bridge == 'hearts':
            item_req_string = str(world.settings.bridge_hearts) + ' ' + item_req_string
        if '#' not in item_req_string:
            item_req_string = '#%s#' % item_req_string
        string += "The awakened ones will await for the Hero to collect %s." % item_req_string
    return str(GossipText(string, ['Green'], prefix=''))


def buildGanonBossKeyString(world):
    string = "\x13\x74" # Boss Key Icon
    if world.settings.shuffle_ganon_bosskey == 'remove':
        string += "And the door to the \x05\x41evil one\x05\x40's chamber will be left #unlocked#."
    else:
        if world.settings.shuffle_ganon_bosskey == 'on_lacs':
            item_req_string = getHint('lacs_' + world.settings.lacs_condition, world.settings.clearer_hints).text
            if world.settings.lacs_condition == 'medallions':
                item_req_string = str(world.settings.lacs_medallions) + ' ' + item_req_string
            elif world.settings.lacs_condition == 'stones':
                item_req_string = str(world.settings.lacs_stones) + ' ' + item_req_string
            elif world.settings.lacs_condition == 'dungeons':
                item_req_string = str(world.settings.lacs_rewards) + ' ' + item_req_string
            elif world.settings.lacs_condition == 'tokens':
                item_req_string = str(world.settings.lacs_tokens) + ' ' + item_req_string
            elif world.settings.lacs_condition == 'hearts':
                item_req_string = str(world.settings.lacs_hearts) + ' ' + item_req_string
            if '#' not in item_req_string:
                item_req_string = '#%s#' % item_req_string
            bk_location_string = "provided by Zelda once %s are retrieved" % item_req_string
        elif world.settings.shuffle_ganon_bosskey in ['stones', 'medallions', 'dungeons', 'tokens', 'hearts']:
            item_req_string = getHint('ganonBK_' + world.settings.shuffle_ganon_bosskey, world.settings.clearer_hints).text
            if world.settings.shuffle_ganon_bosskey == 'medallions':
                item_req_string = str(world.settings.ganon_bosskey_medallions) + ' ' + item_req_string
            elif world.settings.shuffle_ganon_bosskey == 'stones':
                item_req_string = str(world.settings.ganon_bosskey_stones) + ' ' + item_req_string
            elif world.settings.shuffle_ganon_bosskey == 'dungeons':
                item_req_string = str(world.settings.ganon_bosskey_rewards) + ' ' + item_req_string
            elif world.settings.shuffle_ganon_bosskey == 'tokens':
                item_req_string = str(world.settings.ganon_bosskey_tokens) + ' ' + item_req_string
            elif world.settings.shuffle_ganon_bosskey == 'hearts':
                item_req_string = str(world.settings.ganon_bosskey_hearts) + ' ' + item_req_string
            if '#' not in item_req_string:
                item_req_string = '#%s#' % item_req_string
            bk_location_string = "automatically granted once %s are retrieved" % item_req_string
        else:
            bk_location_string = getHint('ganonBK_' + world.settings.shuffle_ganon_bosskey, world.settings.clearer_hints).text
        string += "And the \x05\x41evil one\x05\x40's key will be %s." % bk_location_string
    return str(GossipText(string, ['Yellow'], prefix=''))


# fun new lines for Ganon during the final battle
def buildGanonText(world, messages):
    # empty now unused messages to make space for ganon lines
    update_message_by_id(messages, 0x70C8, " ")
    update_message_by_id(messages, 0x70C9, " ")
    update_message_by_id(messages, 0x70CA, " ")

    # lines before battle
    ganonLines = getHintGroup('ganonLine', world)
    random.shuffle(ganonLines)
    text = get_raw_text(ganonLines.pop().text)
    update_message_by_id(messages, 0x70CB, text)


def buildMiscItemHints(world, messages):
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
                area = HintArea.at(location).text(world.settings.clearer_hints, world=None if location.world.id == world.id else location.world.id + 1)
                if item == data['default_item']:
                    text = data['default_item_text'].format(area=area)
                else:
                    text = data['custom_item_text'].format(area=area, item=getHint(getItemGenericName(location.item), world.settings.clearer_hints).text)
            elif 'custom_item_fallback' in data:
                if 'default_item_fallback' in data and item == data['default_item']:
                    text = data['default_item_fallback']
                else:
                    text = data['custom_item_fallback'].format(item=item)
            else:
                text = getHint('Validation Line', world.settings.clearer_hints).text
                for location in world.get_filled_locations():
                    if location.name == 'Ganons Tower Boss Key Chest':
                        text += f"#{getHint(getItemGenericName(location.item), world.settings.clearer_hints).text}#"
                        break
            for find, replace in data.get('replace', {}).items():
                text = text.replace(find, replace)

            update_message_by_id(messages, data['id'], str(GossipText(text, ['Green'], prefix='')))


def get_raw_text(string):
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


def HintDistFiles():
    return [os.path.join(data_path('Hints/'), d) for d in defaultHintDists] + [
            os.path.join(data_path('Hints/'), d)
            for d in sorted(os.listdir(data_path('Hints/')))
            if d.endswith('.json') and d not in defaultHintDists]


def HintDistList():
    dists = {}
    for d in HintDistFiles():
        with open(d, 'r') as dist_file:
            dist = json.load(dist_file)
        dist_name = dist['name']
        gui_name = dist['gui_name']
        dists.update({ dist_name: gui_name })
    return dists


def HintDistTips():
    tips = ""
    first_dist = True
    line_char_limit = 33
    for d in HintDistFiles():
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
