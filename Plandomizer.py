import itertools
import json
import logging
import re
import random
import uuid

from functools import reduce

from Fill import FillError
from Hints import gossipLocations, GossipText
from Item import ItemFactory, ItemIterator, IsItem
from ItemPool import item_groups, rewardlist, get_junk_item
from Location import LocationIterator, LocationFactory, IsLocation
from LocationList import location_groups
from Playthrough import Playthrough
from Spoiler import HASH_ICONS
from version import __version__
from Utils import random_choices
from JSONDump import dump_obj, CollapseList, CollapseDict, AllignedDict, SortedDict


per_world_keys = (
    'starting_items',
    'item_pool',
    'dungeons',
    'trials',
    ':entrances',
    'locations',
    ':woth_locations',
    ':barren_regions',
    'gossip_stones',
)


search_groups = {
    **location_groups,
    **item_groups,
}


def SimpleRecord(props):
    class Record(object):
        def __init__(self, src_dict=None):
            self.update(src_dict, update_all=True)


        def update(self, src_dict, update_all=False):
            if src_dict is None:
                src_dict = {}
            for k, p in props.items():
                if update_all or k in src_dict:
                    setattr(self, k, src_dict.get(k, p))


        def to_json(self):
            return {k: getattr(self, k) for (k, d) in props.items() if getattr(self, k) != d}


        def __str__(self):
            return dump_obj(self.to_json())
    return Record


class DungeonRecord(SimpleRecord({'mq': None})):
    def __init__(self, src_dict='random'):
        if src_dict == 'random':
            src_dict = {'mq': None}
        if src_dict == 'mq':
            src_dict = {'mq': True}
        if src_dict == 'vanilla':
            src_dict = {'mq': False}
        super().__init__(src_dict)


    def to_json(self):
        if self.mq is None:
            return 'random'
        return 'mq' if self.mq else 'vanilla'


class GossipRecord(SimpleRecord({'text': None, 'colors': None})):
    def to_json(self):
        if self.colors is not None:
            self.colors = CollapseList(self.colors)
        return CollapseDict(super().to_json())


class ItemPoolRecord(SimpleRecord({'type': 'set', 'count': 1})):
    def __init__(self, src_dict=1):
        if isinstance(src_dict, int):
            src_dict = {'count':src_dict}
        super().__init__(src_dict)


    def to_json(self):
        if self.type == 'set':
            return self.count
        else:
            return CollapseDict(super().to_json())


    def update(self, src_dict, update_all=False):
        super().update(src_dict, update_all)
        if self.count < 0:
            raise ValueError("Count cannot be negative in a ItemPoolRecord.")
        if self.type not in ['add', 'remove', 'set']:
            raise ValueError("Type must be 'add', 'remove', or 'set' in a ItemPoolRecord.")


class LocationRecord(SimpleRecord({'item': None, 'player': None, 'price': None, 'model': None})):
    def __init__(self, src_dict):
        if isinstance(src_dict, str):
            src_dict = {'item':src_dict}
        super().__init__(src_dict)


    def to_json(self):
        self_dict = super().to_json()
        if list(self_dict.keys()) == ['item']:
            return str(self.item)
        else:
            return CollapseDict(self_dict)


    @staticmethod
    def from_item(item):
        if item.world.settings.world_count > 1:
            player = item.world.id + 1
        else:
            player = None if item.location is not None and item.world is item.location.world else (item.world.id + 1)

        return LocationRecord({
            'item': item.name,
            'player': player,
            'model': item.looks_like_item.name if item.looks_like_item is not None and item.location.has_preview() and can_cloak(item, item.looks_like_item) else None,
            'price': item.price,
        })


class EntranceRecord(SimpleRecord({'target': None})):
    def __init__(self, src_dict):
        if isinstance(src_dict, str):
            src_dict = {'target':src_dict}
        super().__init__(src_dict)


    def to_json(self):
        return self.target


class StarterRecord(SimpleRecord({'count': 1})):
    def __init__(self, src_dict=1):
        if isinstance(src_dict, int):
            src_dict = {'count': src_dict}
        super().__init__(src_dict)


    def to_json(self):
        return self.count


class TrialRecord(SimpleRecord({'active': None})):
    def __init__(self, src_dict='random'):
        if src_dict == 'random':
            src_dict = {'active': None}
        if src_dict == 'active':
            src_dict = {'active': True}
        if src_dict == 'inactive':
            src_dict = {'active': False}
        super().__init__(src_dict)


    def to_json(self):
        if self.active is None:
            return 'random'
        return 'active' if self.active else 'inactive'



class WorldDistribution(object):
    def __init__(self, distribution, id, src_dict={}):
        self.distribution = distribution
        self.id = id
        self.base_pool = []
        self.update(src_dict, update_all=True)


    def update(self, src_dict, update_all=False):
        update_dict = {
            'dungeons': {name: DungeonRecord(record) for (name, record) in src_dict.get('dungeons', {}).items()},
            'trials': {name: TrialRecord(record) for (name, record) in src_dict.get('trials', {}).items()},
            'item_pool': {name: ItemPoolRecord(record) for (name, record) in src_dict.get('item_pool', {}).items()},
            'starting_items': {name: StarterRecord(record) for (name, record) in src_dict.get('starting_items', {}).items()},
            'entrances': None,
            'locations': {name: [LocationRecord(rec) for rec in record] if is_pattern(name) else LocationRecord(record) for (name, record) in src_dict.get('locations', {}).items() if not is_output_only(name)},
            'woth_locations': None,
            'barren_regions': None,
            'gossip_stones': {name: [GossipRecord(rec) for rec in record] if is_pattern(name) else GossipRecord(record) for (name, record) in src_dict.get('gossip_stones', {}).items()},
        }

        if update_all:
            self.__dict__.update(update_dict)
        else:
            for k in src_dict:
                if k in update_dict:
                    value = update_dict[k]
                    if self.__dict__.get(k, None) is None:
                        setattr(self, k, value)
                    elif isinstance(value, dict):
                        getattr(self, k).update(value)
                    elif isinstance(value, list):
                        getattr(self, k).extend(value)
                    else:
                        setattr(self, k, None)


    def to_json(self):
        return {
            'starting_items': SortedDict({name: record.to_json() for (name, record) in self.starting_items.items()}),
            'dungeons': {name: record.to_json() for (name, record) in self.dungeons.items()},
            'trials': {name: record.to_json() for (name, record) in self.trials.items()},
            'item_pool': SortedDict({name: record.to_json() for (name, record) in self.item_pool.items()}),
            ':entrances': None if self.entrances is None else {name: record.to_json() for (name, record) in self.entrances.items()},
            'locations': {name: [rec.to_json() for rec in record] if is_pattern(name) else record.to_json() for (name, record) in self.locations.items()},
            ':woth_locations': None if self.woth_locations is None else {name: record.to_json() for (name, record) in self.woth_locations.items()},
            ':barren_regions': self.barren_regions,
            'gossip_stones': SortedDict({name: [rec.to_json() for rec in record] if is_pattern(name) else record.to_json() for (name, record) in self.gossip_stones.items()}),
        }


    def __str__(self):
        return dump_obj(self.to_json())


    def configure_dungeons(self, world, dungeon_pool):
        dist_num_mq = 0
        for (name, record) in self.dungeons.items():
            if record.mq is not None:
                dungeon_pool.remove(name)
                if record.mq:
                    dist_num_mq += 1
                    world.dungeon_mq[name] = True
        return dist_num_mq


    def configure_trials(self, trial_pool):
        dist_chosen = []
        for (name, record) in self.trials.items():
            if record.active is not None:
                trial_pool.remove(name)
                if record.active:
                    dist_chosen.append(name)
        return dist_chosen


    def pool_remove_item(self, pools, item_name, count, world_id=None, use_base_pool=True):
        removed_items = []

        base_remove_matcher = pattern_matcher(item_name)
        remove_matcher = lambda item: base_remove_matcher(item) and ((item in self.base_pool) ^ (not use_base_pool))
        if world_id is None:
            predicate = remove_matcher
        else:
            predicate = lambda item: item.world.id == world_id and remove_matcher(item.name)

        for i in range(count):
            removed_item = pull_random_element(pools, predicate)
            if removed_item is None:
                if not use_base_pool:
                    if IsItem(item_name):
                        raise KeyError('No remaining items matching "%s" to be removed.' % (item_name))
                    else:
                        raise KeyError('No items matching "%s"' % (item_name))
                else:
                    removed_items.extend(self.pool_remove_item(pools, item_name, count - i, world_id=world_id, use_base_pool=False))
                    break
            if use_base_pool:
                if world_id is None:
                    self.base_pool.remove(removed_item)
                else:
                    self.base_pool.remove(removed_item.name)
            removed_items.append(removed_item)

        return removed_items


    def pool_add_item(self, pool, item_name, count):
        added_items = []
        if item_name == '#Junk':
            added_items = get_junk_item(count)
        elif is_pattern(item_name):
            add_matcher = lambda item: pattern_matcher(item_name)(item.name)
            candidates = [item.name for item in ItemIterator(predicate=add_matcher)]
            if len(candidates) == 0:
                raise RuntimeError("Unknown item could not be added: " + item_name)
            added_items = random_choices(candidates, k=count)
        else:
            if not IsItem(item_name):
                raise RuntimeError("Unknown item could not be added: " + item_name)
            added_items = [item_name] * count

        for item in added_items:
            pool.append(item)

        return added_items


    def alter_pool(self, world, pool):
        self.base_pool = list(pool)
        pool_size = len(pool)
        bottle_matcher = pattern_matcher("#Bottle")
        trade_matcher  = pattern_matcher("#AdultTrade")

        for item_name, record in self.item_pool.items():
            if record.type == 'add':
                self.pool_add_item(pool, item_name, record.count)
            if record.type == 'remove':
                self.pool_remove_item([pool], item_name, record.count)

        for item_name, record in self.item_pool.items():
            if record.type == 'set':
                if item_name == '#Junk':
                    raise ValueError('#Junk item group cannot have a set number of items')
                predicate = pattern_matcher(item_name)
                pool_match = [item for item in pool if predicate(item)]
                for item in pool_match:
                    self.base_pool.remove(item)

                add_count = record.count - len(pool_match)
                if add_count > 0:
                    added_items = self.pool_add_item(pool, item_name, add_count)
                    for item in added_items:
                        if bottle_matcher(item):
                            self.pool_remove_item([pool], "#Bottle", 1)
                        elif trade_matcher(item):
                            self.pool_remove_item([pool], "#AdultTrade", 1)
                else:
                    removed_items = self.pool_remove_item([pool], item_name, -add_count)
                    for item in removed_items:
                        if bottle_matcher(item):
                            self.pool_add_item([pool], "#Bottle", 1)
                        elif trade_matcher(item):
                            self.pool_add_item([pool], "#AdultTrade", 1)

        junk_to_add = pool_size - len(pool)
        if junk_to_add > 0:
            junk_items = self.pool_add_item(pool, "#Junk", junk_to_add)
        else:
            junk_items = self.pool_remove_item([pool], "#Junk", -junk_to_add)

        return pool


    def collect_starters(self, state):
        for (name, record) in self.starting_items.items():
            for _ in range(record.count):
                try:
                    item = ItemFactory("Bottle" if name == "Bottle with Milk (Half)" else name)
                except KeyError:
                    continue
                state.collect(item)


    def fill_bosses(self, world, prize_locs, prizepool):
        count = 0
        for (name, record) in pattern_dict_items(self.locations):
            boss = pull_item_or_location([prize_locs], world, name)
            if boss is None:
                try:
                    location = LocationFactory(name)
                except KeyError:
                    raise RuntimeError('Unknown boss in world %d: %s' % (world.id + 1, name))
                if location.type == 'Boss':
                    raise RuntimeError('Boss or already placed in world %d: %s' % (world.id + 1, name))
                else:
                    continue
            if record.player is not None and (record.player - 1) != self.id:
                raise RuntimeError('A boss can only give rewards in its own world')
            reward = pull_item_or_location([prizepool], world, record.item)
            if reward is None:
                if IsItem(record.item):
                    raise RuntimeError('Reward already placed in world %d: %s' % (world.id + 1, record.item))
                else:
                    raise RuntimeError('Reward unknown in world %d: %s' % (world.id + 1, record.item))
            count += 1
            world.push_item(boss, reward, True)
        return count


    def fill(self, window, worlds, location_pools, item_pools):
        world = worlds[self.id]
        for (location_name, record) in pattern_dict_items(self.locations):
            if record.item is None:
                continue

            player_id = self.id if record.player is None else record.player - 1

            location_matcher = lambda loc: loc.world.id == world.id and loc.name == location_name
            location = pull_first_element(location_pools, location_matcher)
            if location is None:
                try:
                    location = LocationFactory(location_name)
                except KeyError:
                    raise RuntimeError('Unknown location in world %d: %s' % (world.id + 1, name))
                if location.type == 'Boss':
                    continue
                else:
                    raise RuntimeError('Location already filled in world %d: %s' % (self.id + 1, location_name))

            try:
                item = self.pool_remove_item(item_pools, record.item, 1, world_id=player_id)[0]
            except KeyError:
                try:
                    self.pool_remove_item(item_pools, "#Junk", 1, world_id=player_id)
                    item_matcher = lambda item: pattern_matcher(record.item)(item.name)
                    item = random.choice(list(ItemIterator(item_matcher, worlds[player_id])))
                except KeyError:
                    raise RuntimeError('Too many items were added to world %d, and not enough junk is available to be removed.' % (self.id + 1))

            if record.price is not None:
                item.price = record.price
            location.world.push_item(location, item, True)
            if item.advancement:
                playthrough = Playthrough.max_explore([world.state for world in worlds], itertools.chain.from_iterable(item_pools))
                if not playthrough.can_beat_game(False):
                    raise FillError('%s in world %d is not reachable without %s in world %d!' % (location.name, self.id + 1, item.name, player_id + 1))
            window.fillcount += 1
            window.update_progress(5 + ((window.fillcount / window.locationcount) * 30))


    def cloak(self, worlds, location_pools, model_pools):
        for (name, record) in pattern_dict_items(self.locations):
            if record.model is None:
                continue

            player_id = self.id if record.player is None else record.player - 1
            world = worlds[player_id]

            try:
                location = LocationFactory(name)
            except KeyError:
                raise RuntimeError('Unknown location in world %d: %s' % (world.id + 1, name))
            if location.type == 'Boss':
                continue

            location = pull_item_or_location(location_pools, world, name)
            if location is None:
                raise RuntimeError('Location already cloaked in world %d: %s' % (self.id + 1, name))
            model = pull_item_or_location(model_pools, world, record.model, remove=False)
            if model is None:
                raise RuntimeError('Unknown model in world %d: %s' % (self.id + 1, record.model))
            if can_cloak(location.item, model):
                location.item.looks_like_item = model


    def configure_gossip(self, spoiler, stoneIDs):
        for (name, record) in pattern_dict_items(self.gossip_stones):
            matcher = pattern_matcher(name)
            stoneID = pull_random_element([stoneIDs], lambda id: matcher(gossipLocations[id].name))
            if stoneID is None:
                raise RuntimeError('Gossip stone unknown or already assigned in world %d: %s' % (self.id + 1, name))
            spoiler.hints[self.id][stoneID] = GossipText(text=record.text, colors=record.colors)


    def give_item(self, item, count=1):
        if item in self.starting_items:
            self.starting_items[item].count += count
        else:
            self.starting_items[item] = StarterRecord(count)


    def give_items(self, save_context):
        for (name, record) in self.starting_items.items():
            if record.count == 0:
                continue
            save_context.give_item(name, record.count)


    def get_starting_item(self, item):
        if item in self.starting_items:
            return self.starting_items[item].count
        else:
            return 0


class Distribution(object):
    def __init__(self, settings, src_dict={}):
        self.settings = settings
        self.world_dists = [WorldDistribution(self, id) for id in range(settings.world_count)]
        self.update(src_dict, update_all=True)


    def fill(self, window, worlds, location_pools, item_pools):
        playthrough = Playthrough.max_explore([world.state for world in worlds], itertools.chain.from_iterable(item_pools))
        if not playthrough.can_beat_game(False):
            raise FillError('Item pool does not contain items required to beat game!')

        for world_dist in self.world_dists:
            world_dist.fill(window, worlds, location_pools, item_pools)


    def cloak(self, worlds, location_pools, model_pools):
        for world_dist in self.world_dists:
            world_dist.cloak(worlds, location_pools, model_pools)


    def update(self, src_dict, update_all=False):
        update_dict = {
            'file_hash': (src_dict.get('file_hash', []) + [None, None, None, None, None])[0:5],
            'playthrough': None,
        }

        if update_all:
            self.__dict__.update(update_dict)
            for world in self.world_dists:
                world.update({}, update_all=True)
        else:
            for k in src_dict:
                setattr(self, k, update_dict[k])

        for k in per_world_keys:
            if k in src_dict:
                for world_id, world in enumerate(self.world_dists):
                    world_key = 'World %d' % (world_id + 1)
                    if world_key in src_dict[k]:
                        world.update({k: src_dict[k][world_key]})
                        del src_dict[k][world_key]
                for world in self.world_dists:
                    if src_dict[k]:
                        world.update({k: src_dict[k]})


    def to_json(self, include_output=True, spoiler=True):
        self_dict = {
            ':version': __version__,
            'file_hash': CollapseList(self.file_hash),
            ':seed': self.settings.seed,
            ':settings_string': self.settings.settings_string,
            ':settings': self.settings.to_json(),
        }

        if spoiler:
            world_dist_dicts = [world_dist.to_json() for world_dist in self.world_dists]
            if self.settings.world_count > 1:
                for k in per_world_keys:
                    self_dict[k] = {}
                    for id, world_dist_dict in enumerate(world_dist_dicts):
                        self_dict[k]['World %d' % (id + 1)] = world_dist_dict[k]
            else:
                self_dict.update({k: world_dist_dicts[0][k] for k in per_world_keys})

            if self.playthrough is not None:
                self_dict[':playthrough'] = AllignedDict({
                    sphere_nr: {
                        name: record.to_json() for name, record in sphere.items()
                    }
                    for (sphere_nr, sphere) in self.playthrough.items()
                }, depth=2)

        if not include_output:
            strip_output_only(self_dict)
        return self_dict


    def to_str(self, include_output_only=True, spoiler=True):
        return dump_obj(self.to_json(include_output_only, spoiler))


    def __str__(self):
        return dump_obj(self.to_json())


    def update_spoiler(self, spoiler):
        self.file_hash = [HASH_ICONS[icon] for icon in spoiler.file_hash]

        if not self.settings.create_spoiler:
            return

        spoiler.parse_data()

        for world in spoiler.worlds:
            world_dist = self.world_dists[world.id]
            world_dist.dungeons = {dung: DungeonRecord({ 'mq': world.dungeon_mq[dung] }) for dung in world.dungeon_mq}
            world_dist.trials = {trial: TrialRecord({ 'active': not world.skipped_trials[trial] }) for trial in world.skipped_trials}
            world_dist.entrances = {ent: EntranceRecord(target) for (ent, target) in spoiler.entrances[world.id].items()}
            world_dist.locations = {loc: LocationRecord.from_item(item) for (loc, item) in spoiler.locations[world.id].items()}
            world_dist.woth_locations = {loc.name: LocationRecord.from_item(loc.item) for loc in spoiler.required_locations[world.id]}
            world_dist.barren_regions = [*world.empty_areas]
            world_dist.gossip_stones = {gossipLocations[loc].name: GossipRecord(spoiler.hints[world.id][loc].to_json()) for loc in spoiler.hints[world.id]}
            world_dist.item_pool = {}

        for world in spoiler.worlds:
            for (_, item) in spoiler.locations[world.id].items():
                if item.dungeonitem or item.type == 'Event':
                    continue
                player_dist = item.world.distribution
                if item.name in player_dist.item_pool:
                    player_dist.item_pool[item.name].count += 1
                else:
                    player_dist.item_pool[item.name] = ItemPoolRecord()

        self.playthrough = {}
        for (sphere_nr, sphere) in spoiler.playthrough.items():
            loc_rec_sphere = {}
            self.playthrough[sphere_nr] = loc_rec_sphere
            for location in sphere:
                if spoiler.settings.world_count > 1:
                    location_key = '%s [W%d]' % (location.name, location.world.id + 1)
                else:
                    location_key = location.name

                loc_rec_sphere[location_key] = LocationRecord.from_item(location.item)


    @staticmethod
    def from_file(settings, filename):
        with open(filename) as infile:
            src_dict = json.load(infile)
        return Distribution(settings, src_dict)


    def to_file(self, filename):
        json = self.to_str(spoiler=self.settings.create_spoiler)
        with open(filename, 'w') as outfile:
            outfile.write(json)


def strip_output_only(obj):
    if isinstance(obj, list):
        for elem in obj:
            strip_output_only(elem)
    elif isinstance(obj, dict):
        output_only_keys = [key for key in obj if is_output_only(key)]
        for key in output_only_keys:
            del obj[key]
        for elem in obj.values():
            strip_output_only(elem)


def can_cloak(actual_item, model):
    return actual_item.index == 0x7C # Ice Trap


def is_output_only(pattern):
    return pattern.startswith(':')


def is_pattern(pattern):
    return pattern.startswith('!') or pattern.startswith('*') or pattern.startswith('#') or pattern.endswith('*')


def pattern_matcher(pattern):
    if isinstance(pattern, list):
        pattern_list = []
        for pattern_item in enumerate(pattern):
            pattern_list.append(pattern_matcher(pattern_item))
        return reduce(lambda acc, sub_matcher: lambda item: sub_matcher(item) or acc(item), pattern_list, lambda: False)

    invert = pattern.startswith('!')
    if invert:
        pattern = pattern[1:]
    if pattern.startswith('#'):
        group = search_groups[pattern[1:]]
        return lambda s: invert != (s in group)
    wildcard_begin = pattern.startswith('*')
    if wildcard_begin:
        pattern = pattern[1:]
    wildcard_end = pattern.endswith('*')
    if wildcard_end:
        pattern = pattern[:-1]
        if wildcard_begin:
            return lambda s: invert != (pattern in s)
        else:
            return lambda s: invert != s.startswith(pattern)
    else:
        if wildcard_begin:
            return lambda s: invert != s.endswith(pattern)
        else:
            return lambda s: invert != (s == pattern)


def pattern_dict_items(pattern_dict):
    for (key, value) in pattern_dict.items():
        if is_pattern(key):
            pattern = lambda loc: pattern_matcher(key)(loc.name)
            for location in LocationIterator(pattern):
                yield(location.name, value)
        else:
            yield (key, value)


def pull_first_element(pools, predicate=lambda k:True, remove=True):
    for pool in pools:
        for element in pool:
            if predicate(element):
                if remove:
                    pool.remove(element)
                return element
    return None


def pull_random_element(pools, predicate=lambda k:True, remove=True):
    candidates = [(element, pool) for pool in pools for element in pool if predicate(element)]
    if len(candidates) == 0:
        return None
    element, pool = random.choice(candidates)
    if remove:
        pool.remove(element)
    return element


def pull_all_elements(pools, predicate=lambda k:True, remove=True):
    elements = []
    for pool in pools:
        for element in pool:
            if predicate(element):
                if remove:
                    pool.remove(element)
                elements.append(element)

    if len(elements) == 0:
        return None
    return elements


# Finds and removes (unless told not to do so) an item or location matching the criteria from a list of pools.
def pull_item_or_location(pools, world, name, remove=True):
    if is_pattern(name):
        matcher = pattern_matcher(name)
        return pull_random_element(pools, lambda e: e.world is world and matcher(e.name), remove)
    else:
        return pull_first_element(pools, lambda e: e.world is world and e.name == name, remove)
