import io
import hashlib
import logging
import os
import struct
import random

from HintList import getHint, getHintGroup, Hint, hintExclusions
from Item import MakeEventItem
from Messages import update_message_by_id
from Playthrough import Playthrough
from TextBox import line_wrap
from Utils import random_choices


class GossipStone():
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.reachable = True


class GossipText():
    def __init__(self, text, colors=None, prefix="They say that "):
        text = prefix + text
        text = text[:1].upper() + text[1:]
        self.text = text
        self.colors = colors


    def to_json(self):
        return {'text': self.text, 'colors': self.colors}


    def __str__(self):
        return get_raw_text(line_wrap(colorText(self)))


gossipLocations = {
    0x0405: GossipStone('Death Mountain Crater (Bombable Wall)','Death Mountain Crater Gossip Stone'),
    0x0404: GossipStone('Death Mountain Trail (Biggoron)',      'Death Mountain Trail Gossip Stone'),
    0x041A: GossipStone('Desert Colossus (Spirit Temple)',      'Desert Colossus Gossip Stone'),
    0x0414: GossipStone('Dodongos Cavern (Bombable Wall)',      'Dodongos Cavern Gossip Stone'),
    0x0411: GossipStone('Gerudo Valley (Waterfall)',            'Gerudo Valley Gossip Stone'),
    0x0415: GossipStone('Goron City (Maze)',                    'Goron City Maze Gossip Stone'),
    0x0419: GossipStone('Goron City (Medigoron)',               'Goron City Medigoron Gossip Stone'),
    0x040A: GossipStone('Graveyard (Shadow Temple)',            'Graveyard Gossip Stone'),
    0x0412: GossipStone('Hyrule Castle (Malon)',                'Hyrule Castle Malon Gossip Stone'),
    0x040B: GossipStone('Hyrule Castle (Rock Wall)',            'Hyrule Castle Rock Wall Gossip Stone'),
    0x0413: GossipStone('Hyrule Castle (Storms Grotto)',        'Castle Storms Grotto Gossip Stone'),
    0x041B: GossipStone('Hyrule Field (Hammer Grotto)',         'Field Valley Grotto Gossip Stone'),
    0x041F: GossipStone('Kokiri Forest (Deku Tree Left)',       'Deku Tree Gossip Stone (Left)'),
    0x0420: GossipStone('Kokiri Forest (Deku Tree Right)',      'Deku Tree Gossip Stone (Right)'),
    0x041E: GossipStone('Kokiri Forest (Storms)',               'Kokiri Forest Gossip Stone'),
    0x0403: GossipStone('Lake Hylia (Lab)',                     'Lake Hylia Lab Gossip Stone'),
    0x040F: GossipStone('Lake Hylia (Southeast Corner)',        'Lake Hylia Gossip Stone (Southeast)'),
    0x0408: GossipStone('Lake Hylia (Southwest Corner)',        'Lake Hylia Gossip Stone (Southwest)'),
    0x041D: GossipStone('Lost Woods (Bridge)',                  'Lost Woods Gossip Stone'),
    0x0416: GossipStone('Sacred Forest Meadow (Maze Lower)',    'Sacred Forest Meadow Maze Gossip Stone (Lower)'),
    0x0417: GossipStone('Sacred Forest Meadow (Maze Upper)',    'Sacred Forest Meadow Maze Gossip Stone (Upper)'),
    0x041C: GossipStone('Sacred Forest Meadow (Saria)',         'Sacred Forest Meadow Saria Gossip Stone'),
    0x0406: GossipStone('Temple of Time (Left)',                'Temple of Time Gossip Stone (Left)'),
    0x0407: GossipStone('Temple of Time (Left-Center)',         'Temple of Time Gossip Stone (Left-Center)'),
    0x0410: GossipStone('Temple of Time (Right)',               'Temple of Time Gossip Stone (Right)'),
    0x040E: GossipStone('Temple of Time (Right-Center)',        'Temple of Time Gossip Stone (Right-Center)'),
    0x0409: GossipStone('Zoras Domain (Mweep)',                 'Zoras Domain Gossip Stone'),
    0x0401: GossipStone('Zoras Fountain (Fairy)',               'Zoras Fountain Fairy Gossip Stone'),
    0x0402: GossipStone('Zoras Fountain (Jabu)',                'Zoras Fountain Jabu Gossip Stone'),
    0x040D: GossipStone('Zoras River (Plateau)',                'Zoras River Plateau Gossip Stone'),
    0x040C: GossipStone('Zoras River (Waterfall)',              'Zoras River Waterfall Gossip Stone'),

    0x0430: GossipStone('Hyrule Field (Castle Moat Grotto)',    'Field West Castle Town Grotto Gossip Stone'),
    0x0432: GossipStone('Hyrule Field (Rock Grotto)',           'Remote Southern Grotto Gossip Stone'),
    0x0433: GossipStone('Hyrule Field (Open Grotto)',           'Field Near Lake Outside Fence Grotto Gossip Stone'),
    0x0438: GossipStone('Kakariko (Potion Grotto)',             'Kakariko Back Grotto Gossip Stone'),
    0x0439: GossipStone('Zoras River (Open Grotto)',            'Zora River Plateau Open Grotto Gossip Stone'),
    0x043C: GossipStone('Kokiri Forest (Storms Grotto)',        'Kokiri Forest Storms Grotto Gossip Stone'),
    0x0444: GossipStone('Lost Woods (Rock Grotto)',             'Lost Woods Generic Grotto Gossip Stone'),
    0x0447: GossipStone('Death Mountain Trail (Storms Grotto)', 'Mountain Storms Grotto Gossip Stone'),
    0x044A: GossipStone('Death Mountain Crater (Rock Grotto)',  'Top of Crater Grotto Gossip Stone'),
}


def getItemGenericName(item):
    if item.dungeonitem:
        return item.type
    else:
        return item.name


def isRestrictedDungeonItem(dungeon, item):
    if (item.map or item.compass) and dungeon.world.shuffle_mapcompass == 'dungeon':
        return item in dungeon.dungeon_items
    if item.smallkey and dungeon.world.shuffle_smallkeys == 'dungeon':
        return item in dungeon.small_keys
    if item.bosskey and dungeon.world.shuffle_bosskeys == 'dungeon':
        return item in dungeon.boss_key
    return False


def stone_reachability(world, stone_location):
    # just name the event item after the gossip stone directly
    MakeEventItem(stone_location, world.get_location(stone_location))

    return lambda state: state.has(stone_location)


def add_hint(spoiler, world, IDs, gossip_text, count, location=None, force_reachable=False):
    random.shuffle(IDs)
    skipped_ids = []
    first = True
    success = True
    while random.random() < count:
        if IDs:
            id = IDs.pop(0)

            if gossipLocations[id].reachable:
                stone_location = gossipLocations[id].location
                if not first or can_reach_stone(spoiler.worlds, stone_location, location):
                    if first and location:
                        # This mostly guarantees that we don't lock the player out of an item hint
                        # by establishing a (hint -> item) -> hint -> item -> (first hint) loop
                        location.add_rule(stone_reachability(world, stone_location))

                    count -= 1
                    first = False
                    spoiler.hints[world.id][id] = gossip_text
                else:
                    skipped_ids.append(id)
            else:
                if not force_reachable:
                    # The stones are not readable at all in logic, so we ignore any kind of logic here
                    count -= 1
                    spoiler.hints[world.id][id] = gossip_text
                else:
                    # If flagged to guarantee reachable, then skip
                    # If no stones are reachable, then this will place nothing
                    skipped_ids.append(id)                
        else:
            success = False
            break
    IDs.extend(skipped_ids)
    return success


def can_reach_stone(worlds, stone_location, location):
    if location == None:
        return True

    old_item = location.item
    location.item = None
    playthrough = Playthrough.max_explore([world.state for world in worlds])
    location.item = old_item

    return (playthrough.state_list[location.world.id].can_reach(stone_location, resolution_hint='Location')
            and playthrough.state_list[location.world.id].guarantee_hint())


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
    colorMap = {
        'White':      '\x40',
        'Red':        '\x41',
        'Green':      '\x42',
        'Blue':       '\x43',
        'Light Blue': '\x44',
        'Pink':       '\x45',
        'Yellow':     '\x46',
        'Black':      '\x47',
    }

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
        
        splitText[1] = '\x05' + colorMap[color] + splitText[1] + '\x05\x40'
        text = ''.join(splitText)

    return text


def get_hint_area(spot):
    if spot.parent_region.dungeon:
        return spot.parent_region.dungeon.hint
    elif spot.parent_region.hint:
        return spot.parent_region.hint
    for entrance in spot.parent_region.entrances:
        if entrance.parent_region.hint:
            return entrance.parent_region.hint
    raise RuntimeError('No hint area could be found for %s [World %d]' % (spot, spot.world.id))


def get_woth_hint(spoiler, world, checked):
    locations = spoiler.required_locations[world.id]
    locations = list(filter(lambda location: location.name not in checked, locations))
    if not locations:
        return None

    location = random.choice(locations)
    checked.append(location.name)

    if location.parent_region.dungeon:
        location_text = getHint(location.parent_region.dungeon.name, world.clearer_hints).text
    else:
        location_text = get_hint_area(location)

    return (GossipText('#%s# is on the way of the hero.' % location_text, ['Light Blue']), location)


def get_barren_hint(spoiler, world, checked):
    areas = list(filter(lambda area: 
        area not in checked and \
        not (world.barren_dungeon and world.empty_areas[area]['dungeon']), 
        world.empty_areas.keys()))

    if not areas:
        return None

    area_weights = [world.empty_areas[area]['weight'] for area in areas]

    area = random_choices(areas, weights=area_weights)[0]
    if world.hint_dist != 'very_strong' and world.empty_areas[area]['dungeon']:
        world.barren_dungeon = True

    checked.append(area)

    return (GossipText("plundering #%s# is a foolish choice." % area, ['Pink']), None)


def get_good_item_hint(spoiler, world, checked):
    locations = [location for location in world.get_filled_locations()
            if not location.name in checked and \
            location.item.majoritem and \
            not location.locked]
    if not locations:
        return None

    location = random.choice(locations)
    checked.append(location.name)

    item_text = getHint(getItemGenericName(location.item), world.clearer_hints).text
    if location.parent_region.dungeon:
        location_text = getHint(location.parent_region.dungeon.name, world.clearer_hints).text
        return (GossipText('#%s# hoards #%s#.' % (location_text, item_text), ['Green', 'Red']), location)
    else:
        location_text = get_hint_area(location)
        return (GossipText('#%s# can be found at #%s#.' % (item_text, location_text), ['Red', 'Green']), location)


def get_random_location_hint(spoiler, world, checked):
    locations = [location for location in world.get_filled_locations()
            if not location.name in checked and \
            location.item.type not in ('Drop', 'Event', 'Shop', 'DungeonReward') and \
            not (location.parent_region.dungeon and \
                isRestrictedDungeonItem(location.parent_region.dungeon, location.item)) and
            not location.locked]
    if not locations:
        return None

    location = random.choice(locations)
    checked.append(location.name)
    dungeon = location.parent_region.dungeon

    item_text = getHint(getItemGenericName(location.item), world.clearer_hints).text
    if dungeon:
        location_text = getHint(dungeon.name, world.clearer_hints).text
        return (GossipText('#%s# hoards #%s#.' % (location_text, item_text), ['Green', 'Red']), location)
    else:
        location_text = get_hint_area(location)
        return (GossipText('#%s# can be found at #%s#.' % (item_text, location_text), ['Red', 'Green']), location)


def get_specific_hint(spoiler, world, checked, type):
    hintGroup = getHintGroup(type, world)
    hintGroup = list(filter(lambda hint: hint.name not in checked, hintGroup))
    if not hintGroup:
        return None

    hint = random.choice(hintGroup)
    location = world.get_location(hint.name)
    checked.append(location.name)

    location_text = hint.text
    if '#' not in location_text:
        location_text = '#%s#' % location_text   
    item_text = getHint(getItemGenericName(location.item), world.clearer_hints).text

    return (GossipText('%s #%s#.' % (location_text, item_text), ['Green', 'Red']), location)


def get_song_hint(spoiler, world, checked):
    return get_specific_hint(spoiler, world, checked, 'song')


def get_minigame_hint(spoiler, world, checked):
    return get_specific_hint(spoiler, world, checked, 'minigame')


def get_overworld_hint(spoiler, world, checked):
    return get_specific_hint(spoiler, world, checked, 'overworld')


def get_dungeon_hint(spoiler, world, checked):
    return get_specific_hint(spoiler, world, checked, 'dungeon')


def get_entrance_hint(spoiler, world, checked):
    if world.entrance_shuffle == 'off':
        return None

    entrance_hints = getHintGroup('entrance', world)
    entrance_hints = list(filter(lambda hint: hint.name not in checked, entrance_hints))
    valid_entrance_hints = [entrance_hint for entrance_hint in entrance_hints if world.get_entrance(entrance_hint.name).shuffled]

    if not valid_entrance_hints:
        return None

    entrance_hint = random.choice(valid_entrance_hints)
    entrance = world.get_entrance(entrance_hint.name)
    checked.append(entrance.name)

    entrance_text = entrance_hint.text

    if '#' not in entrance_text:
        entrance_text = '#%s#' % entrance_text

    connected_region = entrance.connected_region
    if connected_region.dungeon:
        region_text = getHint(connected_region.dungeon.name, world.clearer_hints).text
    else:
        region_text = getHint(connected_region.name, world.clearer_hints).text

    if '#' not in region_text:
        region_text = '#%s#' % region_text

    return (GossipText('%s %s.' % (entrance_text, region_text), ['Light Blue', 'Green']), None)


def get_junk_hint(spoiler, world, checked):
    hints = getHintGroup('junk', world)
    hints = list(filter(lambda hint: hint.name not in checked, hints))
    if not hints:
        return None

    hint = random.choice(hints)
    checked.append(hint.name)

    return (GossipText(hint.text, prefix=''), None)


hint_func = {
    'trial':    lambda spoiler, world, checked: None,
    'always':   lambda spoiler, world, checked: None,
    'woth':     get_woth_hint,
    'barren':   get_barren_hint,
    'item':     get_good_item_hint,
    'song':     get_song_hint,
    'minigame': get_minigame_hint,
    'ow':       get_overworld_hint,
    'dungeon':  get_dungeon_hint,
    'entrance': get_entrance_hint,
    'random':   get_random_location_hint,
    'junk':     get_junk_hint,
}


# (relative weight, count)
# count: number of times each hint is placed. 0 means none!
# trial and always are special, and their weights irrelevant.
hint_dist_sets = {
    'useless': {
        'trial':    (0.0, 0),
        'always':   (0.0, 0),
        'woth':     (0.0, 0),
        'barren':   (0.0, 0),
        'item':     (0.0, 0),
        'song':     (0.0, 0),
        'minigame': (0.0, 0),
        'ow':       (0.0, 0),
        'dungeon':  (0.0, 0),
        'entrance': (0.0, 0),
        'random':   (0.0, 0),
        'junk':     (9.0, 1),
    },
    'balanced': {
        'trial':    (0.0, 1),
        'always':   (0.0, 1),
        'woth':     (3.5, 1),
        'barren':   (2.0, 1),
        'item':     (5.0, 1),
        'song':     (1.0, 1),
        'minigame': (0.5, 1),
        'ow':       (2.0, 1),
        'dungeon':  (1.5, 1),
        'entrance': (3.0, 1),
        'random':   (6.0, 1),
        'junk':     (3.0, 1),
    },
    'strong': {
        'trial':    (0.0, 1),
        'always':   (0.0, 2),
        'woth':     (3.0, 2),
        'barren':   (3.0, 1),
        'item':     (1.0, 1),
        'song':     (0.33, 1),
        'minigame': (0.33, 1),
        'ow':       (0.66, 1),
        'dungeon':  (0.66, 1),
        'entrance': (1.0, 1),
        'random':   (2.0, 1),
        'junk':     (0.0, 0),
    },
    'very_strong': {
        'trial':    (0.0, 1),
        'always':   (0.0, 2),
        'woth':     (3.0, 2),
        'barren':   (3.0, 1),
        'item':     (1.0, 1),
        'song':     (0.5, 1),
        'minigame': (0.5, 1),
        'ow':       (1.5, 1),
        'dungeon':  (1.5, 1),
        'entrance': (2.0, 1),
        'random':   (0.0, 0),
        'junk':     (0.0, 0),
    },
    'tournament': {
        # (number of hints, count per hint)
        'trial':    (0.0, 2),
        'always':   (0.0, 2),
        'woth':     (4.0, 2),
        'barren':   (2.0, 2),
        'item':     (0.0, 1),
        'song':     (1.0, 1),
        'minigame': (0.0, 1),
        'ow':       (2.0, 1),
        'dungeon':  (3.0, 1),
        'entrance': (4.0, 1),
        'random':   (0.0, 1),
        'junk':     (0.0, 0),
    },
}


#builds out general hints based on location and whether an item is required or not
def buildGossipHints(spoiler, world):
    # rebuild hint exclusion list
    hintExclusions(world, clear_cache=True)

    world.barren_dungeon = False

    playthrough = Playthrough.max_explore([w.state for w in spoiler.worlds])
    for stone in gossipLocations.values():
        stone.reachable = (
            playthrough.state_list[world.id].can_reach(stone.location, resolution_hint='Location')
            and playthrough.state_list[world.id].guarantee_hint())

    checkedLocations = []

    stoneIDs = list(gossipLocations.keys())

    world.distribution.configure_gossip(spoiler, stoneIDs)

    random.shuffle(stoneIDs)

    hint_dist = hint_dist_sets[world.hint_dist]
    hint_types, hint_prob = zip(*hint_dist.items())
    hint_prob, _ = zip(*hint_prob)

    # Add required location hints
    alwaysLocations = getHintGroup('always', world)
    for hint in alwaysLocations:
        location = world.get_location(hint.name)
        checkedLocations.append(hint.name)

        location_text = getHint(location.name, world.clearer_hints).text
        if '#' not in location_text:
            location_text = '#%s#' % location_text
        item_text = getHint(getItemGenericName(location.item), world.clearer_hints).text
        add_hint(spoiler, world, stoneIDs, GossipText('%s #%s#.' % (location_text, item_text), ['Green', 'Red']), hint_dist['always'][1], location, force_reachable=True)

    # Add trial hints
    if world.trials_random and world.trials == 6:
        add_hint(spoiler, world, stoneIDs, GossipText("#Ganon's Tower# is protected by a powerful barrier.", ['Pink']), hint_dist['trial'][1], force_reachable=True)
    elif world.trials_random and world.trials == 0:
        add_hint(spoiler, world, stoneIDs, GossipText("Sheik dispelled the barrier around #Ganon's Tower#.", ['Yellow']), hint_dist['trial'][1], force_reachable=True)
    elif world.trials < 6 and world.trials > 3:
        for trial,skipped in world.skipped_trials.items():
            if skipped:
                add_hint(spoiler, world, stoneIDs,GossipText("the #%s Trial# was dispelled by Sheik." % trial, ['Yellow']), hint_dist['trial'][1], force_reachable=True)
    elif world.trials <= 3 and world.trials > 0:
        for trial,skipped in world.skipped_trials.items():
            if not skipped:
                add_hint(spoiler, world, stoneIDs, GossipText("the #%s Trial# protects Ganon's Tower." % trial, ['Pink']), hint_dist['trial'][1], force_reachable=True)

    hint_types = list(hint_types)
    hint_prob  = list(hint_prob)
    hint_counts = {}

    if world.hint_dist == "tournament":
        fixed_hint_types = []
        for hint_type in hint_types:
            fixed_hint_types.extend([hint_type] * int(hint_dist[hint_type][0]))

    while stoneIDs:
        if world.hint_dist == "tournament":
            if fixed_hint_types:
                hint_type = fixed_hint_types.pop(0)
            else:
                hint_type = 'random'
        else:
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
            except IndexError:
                raise Exception('Not enough valid hints to fill gossip stone locations.')

        hint = hint_func[hint_type](spoiler, world, checkedLocations)

        if hint == None:
            index = hint_types.index(hint_type)
            hint_prob[index] = 0
            if world.hint_dist == "tournament" and hint_type == 'random':
                raise Exception('Not enough valid %s hints for tournament distribution' % hint_type)
        else:
            gossip_text, location = hint
            place_ok = add_hint(spoiler, world, stoneIDs, gossip_text, hint_dist[hint_type][1], location)
            if place_ok:
                hint_counts[hint_type] = hint_counts.get(hint_type, 0) + 1
            if not place_ok and world.hint_dist == "tournament":
                fixed_hint_types.insert(0, hint_type)


# builds boss reward text that is displayed at the temple of time altar for child and adult, pull based off of item in a fixed order.
def buildBossRewardHints(world, messages):
    # text that appears at altar as a child.
    bossRewardsSpiritualStones = [
        ('Kokiri Emerald',   'Green'), 
        ('Goron Ruby',       'Red'), 
        ('Zora Sapphire',    'Blue'),
    ]
    child_text = '\x08'
    child_text += getHint('Spiritual Stone Text Start', world.clearer_hints).text
    for (reward, color) in bossRewardsSpiritualStones:
        child_text += buildBossString(reward, color, world)
    child_text += getHint('Spiritual Stone Text End', world.clearer_hints).text
    child_text += '\x0B'
    update_message_by_id(messages, 0x707A, get_raw_text(child_text), 0x20)

    # text that appears at altar as an adult.
    bossRewardsMedallions = [
        ('Light Medallion',  'Light Blue'),
        ('Forest Medallion', 'Green'),
        ('Fire Medallion',   'Red'),
        ('Water Medallion',  'Blue'),
        ('Shadow Medallion', 'Pink'),
        ('Spirit Medallion', 'Yellow'),
    ]
    adult_text = '\x08'
    adult_text += getHint('Medallion Text Start', world.clearer_hints).text
    for (reward, color) in bossRewardsMedallions:
        adult_text += buildBossString(reward, color, world)
    adult_text += getHint('Medallion Text End', world.clearer_hints).text
    adult_text += '\x0B'
    update_message_by_id(messages, 0x7057, get_raw_text(adult_text), 0x20)


# pulls text string from hintlist for reward after sending the location to hintlist.
def buildBossString(reward, color, world):
    for location in world.get_filled_locations():
        if location.item.name == reward:
            item_icon = chr(location.item.special['item_id'])
            location_text = getHint(location.name, world.clearer_hints).text
            return str(GossipText("\x08\x13%s%s" % (item_icon, location_text), [color], prefix='')) + '\x04'
    return ''


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

    # light arrow hint or validation chest item
    if world.trials == 0:
        text = get_raw_text(getHint('Light Arrow Location', world.clearer_hints).text)
        if world.distribution.get_starting_item('Light Arrows') > 0:
            text += "\x05\x42your pocket\x05\x40"
        else:
            location = world.light_arrow_location
            location_hint = get_hint_area(location).replace('Ganon\'s Castle', 'my castle')
            if world.id != location.world.id:
                text += "\x05\x42Player %d's\x05\x40 %s" % (location.world.id +1, get_raw_text(location_hint))
            else:
                text += get_raw_text(location_hint)
        text += '!'
    else:
        text = get_raw_text(getHint('Validation Line', world.clearer_hints).text)
        for location in world.get_filled_locations():
            if location.name == 'Ganons Tower Boss Key Chest':
                text += get_raw_text(getHint(getItemGenericName(location.item), world.clearer_hints).text)
                text += '!'
                break

    update_message_by_id(messages, 0x70CC, text)


def get_raw_text(string):
    text = ''
    for char in string:
        if char == '^':
            text += '\x04' # box break
        elif char == '&':
            text += '\x01' #new line
        elif char == '@':
            text += '\x0F' #print player name
        elif char == '#':
            text += '\x05\x40' #sets color to white
        else:
            text += char
    return text

