import itertools
import json
import logging
import re
import random

from functools import reduce
from collections import defaultdict

from Fill import FillError
from EntranceShuffle import EntranceShuffleError, change_connections, confirm_replacement, validate_world, check_entrances_compatibility
from Hints import gossipLocations, GossipText
from Item import ItemFactory, ItemInfo, ItemIterator, IsItem
from ItemPool import item_groups, get_junk_item
from Location import LocationIterator, LocationFactory, IsLocation
from LocationList import location_groups, location_table
from Search import Search
from Spoiler import HASH_ICONS
from version import __version__
from Utils import random_choices
from JSONDump import dump_obj, CollapseList, CollapseDict, AlignedDict, SortedDict
import StartingItems
from SettingsList import build_close_match, validate_settings


class InvalidFileException(Exception):
    pass


per_world_keys = (
    'randomized_settings',
    'item_pool',
    'dungeons',
    'trials',
    'songs',
    'entrances',
    'locations',
    ':skipped_locations',
    ':woth_locations',
    ':goal_locations',
    ':barren_regions',
    'gossip_stones',
)


def SimpleRecord(props):
    class Record(object):
        def __init__(self, src_dict=None):
            self.update(src_dict, update_all=True)


        def update(self, src_dict, update_all=False):
            if src_dict is None:
                src_dict = {}
            if isinstance(src_dict, list):
                src_dict = {"item": src_dict}
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
            'price': item.location.price,
        })


class EntranceRecord(SimpleRecord({'region': None, 'origin': None})):
    def __init__(self, src_dict):
        if isinstance(src_dict, str):
            src_dict = {'region':src_dict}
        if 'from' in src_dict:
            src_dict['origin'] = src_dict['from']
            del src_dict['from']
        super().__init__(src_dict)


    def to_json(self):
        self_dict = super().to_json()
        if list(self_dict.keys()) == ['region']:
            return str(self.region)
        else:
            self_dict['from'] = self_dict['origin']
            del self_dict['origin']
            return CollapseDict(self_dict)


    @staticmethod
    def from_entrance(entrance):
        if entrance.replaces.primary and entrance.replaces.type in ('Interior', 'SpecialInterior', 'Grotto', 'Grave'):
            origin_name = None
        else:
            origin_name = entrance.replaces.parent_region.name
        return EntranceRecord({
            'region': entrance.connected_region.name,
            'origin': origin_name,
        })


class StarterRecord(SimpleRecord({'count': 1})):
    def __init__(self, src_dict=1):
        if isinstance(src_dict, int):
            src_dict = {'count': src_dict}
        super().__init__(src_dict)


    def copy(self):
        return StarterRecord(self.count)


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


class SongRecord(SimpleRecord({'notes': None})):
    def __init__(self, src_dict=None):
        if src_dict is None or isinstance(src_dict, str):
            src_dict = {'notes': src_dict}
        super().__init__(src_dict)


    def to_json(self):
        return self.notes



class WorldDistribution(object):
    def __init__(self, distribution, id, src_dict={}):
        self.distribution = distribution
        self.id = id
        self.base_pool = []
        self.major_group = []
        self.song_as_items = False
        self.skipped_locations = []
        self.effective_starting_items = {}
        self.update(src_dict, update_all=True)


    def update(self, src_dict, update_all=False):
        if 'starting_items' in src_dict:
            raise ValueError('"starting_items" at the top level is no longer supported, please move it into "settings"')

        update_dict = {
            'randomized_settings': {name: record for (name, record) in src_dict.get('randomized_settings', {}).items()},
            'dungeons': {name: DungeonRecord(record) for (name, record) in src_dict.get('dungeons', {}).items()},
            'trials': {name: TrialRecord(record) for (name, record) in src_dict.get('trials', {}).items()},
            'songs': {name: SongRecord(record) for (name, record) in src_dict.get('songs', {}).items()},
            'item_pool': {name: ItemPoolRecord(record) for (name, record) in src_dict.get('item_pool', {}).items()},
            'entrances': {name: EntranceRecord(record) for (name, record) in src_dict.get('entrances', {}).items()},
            'locations': {name: [LocationRecord(rec) for rec in record] if is_pattern(name) else LocationRecord(record) for (name, record) in src_dict.get('locations', {}).items() if not is_output_only(name)},
            'woth_locations': None,
            'goal_locations': None,
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
            'randomized_settings': self.randomized_settings,
            'dungeons': {name: record.to_json() for (name, record) in self.dungeons.items()},
            'trials': {name: record.to_json() for (name, record) in self.trials.items()},
            'songs': {name: record.to_json() for (name, record) in self.songs.items()},
            'item_pool': SortedDict({name: record.to_json() for (name, record) in self.item_pool.items()}),
            'entrances': {name: record.to_json() for (name, record) in self.entrances.items()},
            'locations': {name: [rec.to_json() for rec in record] if is_pattern(name) else record.to_json() for (name, record) in self.locations.items()},
            ':skipped_locations': {loc.name: LocationRecord.from_item(loc.item).to_json() for loc in self.skipped_locations},
            ':woth_locations': None if self.woth_locations is None else {name: record.to_json() for (name, record) in self.woth_locations.items()},
            ':goal_locations': self.goal_locations,
            ':barren_regions': self.barren_regions,
            'gossip_stones': SortedDict({name: [rec.to_json() for rec in record] if is_pattern(name) else record.to_json() for (name, record) in self.gossip_stones.items()}),
        }


    def __str__(self):
        return dump_obj(self.to_json())


    def pattern_matcher(self, pattern):
        if isinstance(pattern, list):
            pattern_list = []
            for pattern_item in pattern:
                pattern_list.append(self.pattern_matcher(pattern_item))
            return reduce(lambda acc, sub_matcher: lambda item: sub_matcher(item) or acc(item), pattern_list, lambda _: False)

        invert = pattern.startswith('!')
        if invert:
            pattern = pattern[1:]
        if pattern.startswith('#'):   
            group = self.distribution.search_groups[pattern[1:]]
            if pattern == '#MajorItem':
                if not self.major_group: # If necessary to compute major_group, do so only once
                    self.major_group = [item for item in group if item in self.base_pool]
                    # Songs included by default, remove them if songs not set to anywhere
                    if self.distribution.settings.shuffle_song_items != "any":
                        self.major_group = [x for x in self.major_group if x not in item_groups['Song']]
                    # Special handling for things not included in base_pool
                    if self.distribution.settings.triforce_hunt:
                        self.major_group.append('Triforce Piece')
                    major_tokens = ((self.distribution.settings.shuffle_ganon_bosskey == 'on_lacs' and
                            self.distribution.settings.lacs_condition == 'tokens') or
                            self.distribution.settings.shuffle_ganon_bosskey == 'tokens' or self.distribution.settings.bridge == 'tokens')
                    if self.distribution.settings.tokensanity == 'all' and major_tokens:
                        self.major_group.append('Gold Skulltula Token')
                    if self.distribution.settings.shuffle_smallkeys == 'keysanity':
                        for dungeon in ['Bottom of the Well', 'Forest Temple', 'Fire Temple', 'Water Temple',
                                        'Shadow Temple', 'Spirit Temple', 'Gerudo Training Ground', 'Ganons Castle']:
                            if dungeon in self.distribution.settings.key_rings:
                                self.major_group.append(f"Small Key Ring ({dungeon})")
                            else:
                                self.major_group.append(f"Small Key ({dungeon})")
                    if self.distribution.settings.shuffle_hideoutkeys == 'keysanity':
                        if 'Thieves Hideout' in self.distribution.settings.key_rings:
                            self.major_group.append('Small Key Ring (Thieves Hideout)')
                        else:
                            self.major_group.append('Small Key (Thieves Hideout)')
                    if self.distribution.settings.shuffle_bosskeys == 'keysanity':
                        keys = [name for name, item in ItemInfo.items.items() if item.type == 'BossKey' and name != 'Boss Key']
                        self.major_group.extend(keys)
                    if self.distribution.settings.shuffle_ganon_bosskey == 'keysanity':
                        keys = [name for name, item in ItemInfo.items.items() if item.type == 'GanonBossKey']
                        self.major_group.extend(keys)
                group = self.major_group
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

    # adds the location entry only if there is no record for that location already
    def add_location(self, new_location, new_item):
        for (location, record) in self.locations.items():
            pattern = self.pattern_matcher(location)
            if pattern(new_location):
                raise KeyError('Cannot add location that already exists')
        self.locations[new_location] = LocationRecord(new_item)


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


    def configure_songs(self):
        dist_notes = {}
        for (name, record) in self.songs.items():
            if record.notes is not None:
                dist_notes[name] = record.notes
        return dist_notes


    # Add randomized_settings defined in distribution to world's randomized settings list
    def configure_randomized_settings(self, world):
        for name, record in self.randomized_settings.items():
            setattr(world, name, record)
            if name not in world.randomized_list:
                world.randomized_list.append(name)


    def pool_remove_item(self, pools, item_name, count, world_id=None, use_base_pool=True):
        removed_items = []

        base_remove_matcher = self.pattern_matcher(item_name)
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
        if item_name == '#Junk':
            added_items = get_junk_item(count, pool=pool, plando_pool=self.item_pool)
        elif is_pattern(item_name):
            add_matcher = lambda item: self.pattern_matcher(item_name)(item.name)
            candidates = [
                item.name for item in ItemIterator(predicate=add_matcher)
                if item.name not in self.item_pool or self.item_pool[item.name].count != 0
            ]  # Only allow items to be candidates if they haven't been set to 0
            if len(candidates) == 0:
                raise RuntimeError("Unknown item, or item set to 0 in the item pool could not be added: " + repr(item_name) + ". " + build_close_match(item_name, 'item'))
            added_items = random_choices(candidates, k=count)
        else:
            if not IsItem(item_name):
                raise RuntimeError("Unknown item could not be added: " + repr(item_name) + ". " + build_close_match(item_name, 'item'))
            added_items = [item_name] * count

        for item in added_items:
            pool.append(item)

        return added_items


    def alter_pool(self, world, pool):
        self.base_pool = list(pool)
        pool_size = len(pool)
        bottle_matcher = self.pattern_matcher("#Bottle")
        trade_matcher  = self.pattern_matcher("#AdultTrade")
        bottles = 0

        for item_name, record in self.item_pool.items():
            if record.type == 'add':
                self.pool_add_item(pool, item_name, record.count)
            if record.type == 'remove':
                self.pool_remove_item([pool], item_name, record.count)

        remove_egg = False
        for item_name, record in self.item_pool.items():
            if record.type == 'set':
                if item_name == '#Junk':
                    raise ValueError('#Junk item group cannot have a set number of items')
                elif item_name == 'Weird Egg' and not self.distribution.settings.shuffle_weird_egg:
                    remove_egg = True
                    continue
                elif item_name == 'Weird Egg' and self.item_pool['Weird Egg'].count > 1:
                    self.item_pool['Weird Egg'].count = 1
                    continue
                predicate = self.pattern_matcher(item_name)
                pool_match = [item for item in pool if predicate(item)]
                for item in pool_match:
                    self.base_pool.remove(item)

                add_count = record.count - len(pool_match)
                if add_count > 0:
                    added_items = self.pool_add_item(pool, item_name, add_count)
                    for item in added_items:
                        if bottle_matcher(item):
                            bottles += 1
                        elif trade_matcher(item):
                            self.pool_remove_item([pool], "#AdultTrade", 1)
                else:
                    removed_items = self.pool_remove_item([pool], item_name, -add_count)
                    for item in removed_items:
                        if bottle_matcher(item):
                            bottles -= 1
                        elif trade_matcher(item):
                            self.pool_add_item(pool, "#AdultTrade", 1)           
        if remove_egg:
            del self.item_pool['Weird Egg']

        if bottles > 0:
            self.pool_remove_item([pool], '#Bottle', bottles)
        else:
            self.pool_add_item(pool, '#Bottle', -bottles)

        for item_name, record in self.starting_items.items():
            if bottle_matcher(item_name):
                self.pool_remove_item([pool], "#Bottle", record.count)
            elif trade_matcher(item_name):
                self.pool_remove_item([pool], "#AdultTrade", record.count)
            elif IsItem(item_name):
                try:
                    self.pool_remove_item([pool], item_name, record.count)
                except KeyError:
                    pass
                if item_name in item_groups["Song"]:
                    self.song_as_items = True

        junk_to_add = pool_size - len(pool)
        if junk_to_add > 0:
            junk_items = self.pool_add_item(pool, "#Junk", junk_to_add)
        else:
            junk_items = self.pool_remove_item([pool], "#Junk", -junk_to_add)

        return pool


    def set_complete_itempool(self, pool):
        self.item_pool = {}
        for item in pool:
            if item.dungeonitem or item.type in ('Drop', 'Event', 'DungeonReward'):
                continue
            if item.name in self.item_pool:
                self.item_pool[item.name].count += 1
            else:
                self.item_pool[item.name] = ItemPoolRecord()


    def collect_starters(self, state):
        for (name, record) in self.starting_items.items():
            for _ in range(record.count):
                item = ItemFactory("Bottle" if name == "Bottle with Milk (Half)" else name)
                state.collect(item)


    def pool_replace_item(self, item_pools, item_group, player_id, new_item, worlds):
        removed_item = self.pool_remove_item(item_pools, item_group, 1, world_id=player_id)[0]
        item_matcher = lambda item: self.pattern_matcher(new_item)(item.name)
        if self.item_pool[removed_item.name].count > 1:
            self.item_pool[removed_item.name].count -= 1
        else:
            del self.item_pool[removed_item.name]
        if new_item == "#Junk":
            if self.distribution.settings.enable_distribution_file:
                return ItemFactory(get_junk_item(1, self.base_pool, self.item_pool))[0]
            else:  # Generator settings that add junk to the pool should not be strict about the item_pool definitions
                return ItemFactory(get_junk_item(1))[0]
        return random.choice(list(ItemIterator(item_matcher, worlds[player_id])))


    def set_shuffled_entrances(self, worlds, entrance_pools, target_entrance_pools, locations_to_ensure_reachable, itempool):
        for (name, record) in self.entrances.items():
            if record.region is None:
                continue
            try:
                if not worlds[self.id].get_entrance(name):
                    raise RuntimeError('Unknown entrance in world %d: %s. %s' % (self.id + 1, name, build_close_match(name, 'entrance', entrance_pools)))
            except KeyError:
                raise RuntimeError('Unknown entrance in world %d: %s. %s' % (self.id + 1, name, build_close_match(name, 'entrance', entrance_pools)))

            entrance_found = False
            for pool_type, entrance_pool in entrance_pools.items():
                try:
                    matched_entrance = next(filter(lambda entrance: entrance.name == name, entrance_pool))
                except StopIteration:
                    continue

                entrance_found = True
                if matched_entrance.connected_region != None:
                    if matched_entrance.type == 'Overworld':
                        continue
                    else:
                        raise RuntimeError('Entrance already shuffled in world %d: %s' % (self.id + 1, name))

                target_region = record.region

                matched_targets_to_region = list(filter(lambda target: target.connected_region and target.connected_region.name == target_region, 
                                                        target_entrance_pools[pool_type]))
                if not matched_targets_to_region:
                    raise RuntimeError('No entrance found to replace with %s that leads to %s in world %d' % 
                                                (matched_entrance, target_region, self.id + 1))

                if record.origin:
                    target_parent = record.origin
                    try:
                        matched_target = next(filter(lambda target: target.replaces.parent_region.name == target_parent, matched_targets_to_region))
                    except StopIteration:
                        raise RuntimeError('No entrance found to replace with %s that leads to %s from %s in world %d' % 
                                                (matched_entrance, target_region, target_parent, self.id + 1))
                else:
                    matched_target = matched_targets_to_region[0]
                    target_parent = matched_target.parent_region.name

                if matched_target.connected_region == None:
                    raise RuntimeError('Entrance leading to %s from %s is already shuffled in world %d' % 
                                            (target_region, target_parent, self.id + 1))

                try:
                    check_entrances_compatibility(matched_entrance, matched_target)
                    change_connections(matched_entrance, matched_target)
                    validate_world(matched_entrance.world, worlds, None, locations_to_ensure_reachable, itempool)
                except EntranceShuffleError as error:
                    raise RuntimeError('Cannot connect %s To %s in world %d (Reason: %s)' % 
                                            (matched_entrance, matched_entrance.connected_region or matched_target.connected_region, self.id + 1, error))

                confirm_replacement(matched_entrance, matched_target)

            if not entrance_found:
                raise RuntimeError('Entrance does not belong to a pool of shuffled entrances in world %d: %s' % (self.id + 1, name))


    def pattern_dict_items(self, pattern_dict):
        """Retrieve a location by pattern.

        :param pattern_dict: the location dictionary. Capable of containing a pattern.
        :return: tuple:
                    0: the name of the location
                    1: the item to place at the location
        """
        # TODO: This has the same issue with the invert pattern as items do.
        #  It pulls randomly(?) from all locations instead of ones that make sense.
        #  e.g. "!Queen Gohma" results in "KF Kokiri Sword Chest"
        for (key, value) in pattern_dict.items():
            if is_pattern(key):
                pattern = lambda loc: self.pattern_matcher(key)(loc.name)
                for location in LocationIterator(pattern):
                    yield location.name, value
            else:
                yield key, value


    def get_valid_items_from_record(self, itempool, used_items, record):
        """Gets items that are valid for placement.

        :param itempool: a list of the item pool to search through for the record
        :param used_items: a list of the items already used from the item pool
        :param record: the item record to choose from
        :return: list:
                    All items in the record that exist in the item pool but have not already been used. Can be empty.
        """
        valid_items = []
        predicate = self.pattern_matcher(record.item)
        if isinstance(record.item, list):
            for choice in record.item:
                if choice[0] == '#' and choice[1:] in item_groups:
                    for item in itempool:
                        if predicate(item.name):
                            valid_items.append(choice)
                            break
            for item in itempool:
                if item.name in record.item and predicate(item.name):
                    valid_items.append(item.name)
        else:
            if record.item[0] == '#' and record.item[1:] in item_groups:
                for item in itempool:
                    if predicate(item.name):
                        valid_items = [record.item]
                        break
            else:
                valid_items = [record.item]
        if used_items is not None:
            for used_item in used_items:
                if used_item in valid_items:
                    valid_items.remove(used_item)

        return valid_items


    def pull_item_or_location(self, pools, world, name, remove=True):
        """Finds and removes (unless told not to do so) an item or location matching the criteria from a list of pools.

        :param pools: the item pools to pull from
        :param world: the world the pools belong to
        :param name: the name of the element to pull from the pools
        :param remove:
                True: Remove the element pulled from the pool
                False: Keep element pulled in the pool
        :return: the element pulled from the pool
        """
        if is_pattern(name):
            matcher = self.pattern_matcher(name)
            return pull_random_element(pools, lambda e: e.world is world and matcher(e.name), remove)
        else:
            return pull_first_element(pools, lambda e: e.world is world and e.name == name, remove)


    def fill_bosses(self, world, prize_locs, prizepool):
        count = 0
        used_items = []
        for (name, record) in self.pattern_dict_items(self.locations):
            boss = self.pull_item_or_location([prize_locs], world, name)
            if boss is None:
                try:
                    location = LocationFactory(name)
                except KeyError:
                    raise RuntimeError('Unknown location in world %d: %r. %s' % (world.id + 1, name, build_close_match(name, 'location')))
                if location.type == 'Boss':
                    raise RuntimeError('Boss or already placed in world %d: %s' % (world.id + 1, name))
                else:
                    continue

            if record.player is not None and (record.player - 1) != self.id:
                raise RuntimeError('A boss can only give rewards in its own world')

            valid_items = self.get_valid_items_from_record(prizepool, used_items, record)
            if valid_items:  # Choices still available in the item pool, choose one, mark it as a used item
                record.item = random_choices(valid_items)[0]
                if used_items is not None:
                    used_items.append(record.item)

            reward = self.pull_item_or_location([prizepool], world, record.item)
            if reward is None:
                if record.item not in item_groups['DungeonReward']:
                    raise RuntimeError('Cannot place non-dungeon reward %s in world %d on location %s.' % (record.item, self.id + 1, name))
                if IsItem(record.item):
                    raise RuntimeError('Reward already placed in world %d: %s' % (world.id + 1, record.item))
                else:
                    raise RuntimeError('Reward unknown in world %d: %s' % (world.id + 1, record.item))
            count += 1
            world.push_item(boss, reward, True)
        return count

    def fill(self, window, worlds, location_pools, item_pools):
        """Fills the world with restrictions defined in a plandomizer JSON distribution file.

        :param window:
        :param worlds: A list of the world objects that define the rules of each game world.
        :param location_pools: A list containing all of the location pools.
            0: Shop Locations
            1: Song Locations
            2: Fill locations
        :param item_pools: A list containing all of the item pools.
            0: Shop Items
            1: Dungeon Items
            2: Songs
            3: Progression Items
            4: Priority Items
            5: The rest of the Item pool
        """
        world = worlds[self.id]
        locations = {}
        if self.locations:
            locations = {loc: self.locations[loc] for loc in random.sample(sorted(self.locations), len(self.locations))}
        used_items = []
        for (location_name, record) in self.pattern_dict_items(locations):
            if record.item is None:
                continue
            valid_items = []
            if record.item == "#Vanilla": # Get vanilla item at this location from the location table
                valid_items.append(location_table[location_name][4]) 
            else: # Do normal method of getting valid items for this location
                valid_items = self.get_valid_items_from_record(world.itempool, used_items, record)
            if not valid_items:
                # Item pool values exceeded. Remove limited items from the list and choose a random value from it
                limited_items = ['Weird Egg', '#AdultTrade', '#Bottle']
                if isinstance(record.item, list):
                    allowed_choices = []
                    for item in record.item:
                        if item in limited_items or item in item_groups['AdultTrade'] or item in item_groups['Bottle']:
                            continue
                        allowed_choices.append(item)
                    record.item = random_choices(allowed_choices)[0]
            else:  # Choices still available in item pool, choose one, mark it as a used item
                record.item = random_choices(valid_items)[0]
                if used_items is not None and record.item[0] != '#':
                    used_items.append(record.item)

            player_id = self.id if record.player is None else record.player - 1

            location_matcher = lambda loc: loc.world.id == world.id and loc.name.lower() == location_name.lower()
            location = pull_first_element(location_pools, location_matcher)
            if location is None:
                try:
                    location = LocationFactory(location_name)
                except KeyError:
                    raise RuntimeError('Unknown location in world %d: %r. %s' % (world.id + 1, location_name, build_close_match(location_name, 'location')))
                if location.type == 'Boss':
                    continue
                elif location.name in world.settings.disabled_locations:
                    continue
                else:
                    raise RuntimeError('Location already filled in world %d: %s' % (self.id + 1, location_name))

            if record.item in item_groups['DungeonReward']:
                raise RuntimeError('Cannot place dungeon reward %s in world %d in location %s.' % (record.item, self.id + 1, location_name))

            if record.item == '#Junk' and location.type == 'Song' and world.settings.shuffle_song_items == 'song':
                record.item = '#JunkSong'

            ignore_pools = None
            is_invert = self.pattern_matcher(record.item)('!')
            if is_invert and location.type != 'Song' and world.settings.shuffle_song_items == 'song':
                ignore_pools = [2]
            if is_invert and location.type == 'Song' and world.settings.shuffle_song_items == 'song':
                ignore_pools = [i for i in range(len(item_pools)) if i != 2]
            # location.price will be None for Shop Buy items
            if location.type == 'Shop' and location.price is None:
                ignore_pools = [i for i in range(len(item_pools)) if i != 0]

            item = self.get_item(ignore_pools, item_pools, location, player_id, record, worlds)

            if location.type == 'Song' and item.type != 'Song':
                self.song_as_items = True
            location.world.push_item(location, item, True)

            if item.advancement:
                search = Search.max_explore([world.state for world in worlds], itertools.chain.from_iterable(item_pools))
                if not search.can_beat_game(False):
                    raise FillError('%s in world %d is not reachable without %s in world %d!' % (location.name, self.id + 1, item.name, player_id + 1))
            window.fillcount += 1
            window.update_progress(5 + ((window.fillcount / window.locationcount) * 30))

    def get_item(self, ignore_pools, item_pools, location, player_id, record, worlds):
        """Get or create the item specified by the record and replace something in the item pool with it

        :param ignore_pools: Pools to not replace items in
        :param item_pools: A list containing all of the item pools.
        :param location: Location record currently being assigned an item
        :param player_id: Integer representing the current player's ID number
        :param record: Item record from the distribution file to assign to a location
        :param worlds: A list of the world objects that define the rules of each game world.
        :return: item
        """
        world = worlds[player_id]
        if ignore_pools:
            pool = [pool if i not in ignore_pools else [] for i, pool in enumerate(item_pools)]
        else:
            pool = item_pools
        try:
            item = self.pool_remove_item(pool, record.item, 1, world_id=player_id)[0]
        except KeyError:
            if location.type == 'Shop' and "Buy" in record.item:
                try:
                    removed_item = self.pool_remove_item(pool, "Buy *", 1, world_id=player_id)[0]
                    if removed_item.name in self.item_pool:
                        # Update item_pool after item is removed
                        if self.item_pool[removed_item.name].count == 1:
                            del self.item_pool[removed_item.name]
                        else:
                            self.item_pool[removed_item.name].count -= 1
                    item = ItemFactory([record.item], world=world)[0]
                except KeyError:
                    raise RuntimeError(
                        'Too many shop buy items were added to world %d, and not enough shop buy items are available in the item pool to be removed.' % (
                                    self.id + 1))
            elif record.item in item_groups['Bottle']:
                try:
                    item = self.pool_replace_item(pool, "#Bottle", player_id, record.item, worlds)
                except KeyError:
                    raise RuntimeError(
                        'Too many bottles were added to world %d, and not enough bottles are available in the item pool to be removed.' % (
                                    self.id + 1))
            elif record.item in item_groups['AdultTrade']:
                try:
                    item = self.pool_replace_item(pool, "#AdultTrade", player_id, record.item, worlds)
                except KeyError:
                    raise RuntimeError(
                        'Too many adult trade items were added to world %d, and not enough adult trade items are available in the item pool to be removed.' % (
                                    self.id + 1))
            elif record.item == "Weird Egg":
                # If Letter has not been shown to guard before obtaining a second weird egg a softlock can occur
                # if there are important items at deku theater or an important location locked behind the gate
                # or if Keaton Mask gets overwritten before giving it to the guard.
                try:
                    item = self.pool_replace_item(pool, "Weird Egg", player_id, record.item, worlds)
                except KeyError:
                    raise RuntimeError('Weird Egg already placed in World %d.' % (self.id + 1))
            else:
                try:
                    item = self.pool_replace_item(item_pools, "#Junk", player_id, record.item, worlds)
                except KeyError:
                    raise RuntimeError(
                        'Too many items were added to world %d, and not enough junk is available to be removed.' % (self.id + 1))
                except IndexError:
                    raise RuntimeError(
                        'Unknown item %r being placed on location %s in world %d. %s' % (record.item, location, self.id + 1, build_close_match(record.item, 'item')))
            # Update item_pool after item is replaced
            if item.name not in self.item_pool:
                self.item_pool[item.name] = ItemPoolRecord()
            else:
                self.item_pool[item.name].count += 1
        except IndexError:
            raise RuntimeError(
                'Unknown item %r being placed on location %s in world %d. %s' % (record.item, location, self.id + 1, build_close_match(record.item, 'item')))
        # Ensure pool copy is persisted to real pool
        for i, new_pool in enumerate(pool):
            if new_pool:
                item_pools[i] = new_pool
        return item

    def cloak(self, worlds, location_pools, model_pools):
        for (name, record) in self.pattern_dict_items(self.locations):
            if record.model is None:
                continue

            player_id = self.id if record.player is None else record.player - 1
            world = worlds[player_id]

            try:
                location = LocationFactory(name)
            except KeyError:
                raise RuntimeError('Unknown location in world %d: %r. %s' % (world.id + 1, name, build_close_match(name, 'location')))
            if location.type == 'Boss':
                continue

            location = self.pull_item_or_location(location_pools, world, name, remove=False)
            if location is None:
                raise RuntimeError('Location already cloaked in world %d: %s' % (self.id + 1, name))
            model = self.pull_item_or_location(model_pools, world, record.model, remove=False)
            if model is None:
                raise RuntimeError('Unknown model in world %d: %s' % (self.id + 1, record.model))
            if can_cloak(location.item, model):
                location.item.looks_like_item = model


    def configure_gossip(self, spoiler, stoneIDs):
        for (name, record) in self.pattern_dict_items(self.gossip_stones):
            matcher = self.pattern_matcher(name)
            stoneID = pull_random_element([stoneIDs], lambda id: matcher(gossipLocations[id].name))
            if stoneID is None:
                # Allow planning of explicit textids
                match = re.match(r"^(?:\$|x|0x)?([0-9a-f]{4})$", name, flags=re.IGNORECASE)
                if match:
                    stoneID = int(match[1], base=16)
                else:
                    raise RuntimeError('Gossip stone unknown or already assigned in world %d: %r. %s' % (self.id + 1, name, build_close_match(name, 'stone')))
            spoiler.hints[self.id][stoneID] = GossipText(text=record.text, colors=record.colors, prefix='')


    def give_items(self, save_context):
        # copy Triforce pieces to all worlds
        triforce_count = sum(
            world_dist.effective_starting_items['Triforce Piece'].count
            for world_dist in self.distribution.world_dists
            if 'Triforce Piece' in world_dist.effective_starting_items
        )
        if triforce_count > 0:
            save_context.give_item('Triforce Piece', triforce_count)

        for (name, record) in self.effective_starting_items.items():
            if name == 'Triforce Piece' or record.count == 0:
                continue
            save_context.give_item(name, record.count)


    def get_starting_item(self, item):
        items = self.starting_items
        if item in items:
            return items[item].count
        else:
            return 0

    @property
    def starting_items(self):
        return self.distribution.starting_items_from_settings(self.id)

    def configure_effective_starting_items(self, worlds, world):
        items = {item_name: record.copy() for item_name, record in self.starting_items.items()}

        if world.settings.start_with_rupees:
            add_starting_item_with_ammo(items, 'Rupees', 999)
        if world.settings.start_with_consumables:
            add_starting_item_with_ammo(items, 'Deku Sticks', 99)
            add_starting_item_with_ammo(items, 'Deku Nuts', 99)

        skipped_locations = ['Links Pocket']
        if world.settings.skip_child_zelda:
            skipped_locations += ['HC Malon Egg', 'HC Zeldas Letter', 'Song from Impa']
        for iter_world in worlds:
            for location in skipped_locations:
                loc = iter_world.get_location(location)
                if iter_world.id == world.id:
                    self.skipped_locations.append(loc)
                if loc.item is not None and world.id == loc.item.world.id:
                    add_starting_item_with_ammo(items, loc.item.name)

        self.effective_starting_items = items



class Distribution(object):
    def __init__(self, settings, src_dict=None):
        self.src_dict = src_dict or {}
        self.settings = settings
        self.search_groups = {
            **location_groups,
            **item_groups,
        } 
        if self.src_dict and 'custom_groups' in self.src_dict:
            self.search_groups.update(self.src_dict['custom_groups'])
        
        self.world_dists = [WorldDistribution(self, id) for id in range(settings.world_count)]
        # One-time init
        update_dict = {
            'file_hash': (self.src_dict.get('file_hash', []) + [None, None, None, None, None])[0:5],
            'playthrough': None,
            'entrance_playthrough': None,
            '_settings': self.src_dict.get('settings', {}),
        }

        self.settings.__dict__.update(update_dict['_settings'])
        if 'settings' in self.src_dict:
            validate_settings(self.src_dict['settings'])
            self.src_dict['_settings'] = self.src_dict['settings']
            del self.src_dict['settings']

        self.__dict__.update(update_dict)

        # Init we have to do every time we retry
        self.reset()


    # adds the location entry only if there is no record for that location already
    def add_location(self, new_location, new_item):
        for world_dist in self.world_dists:
            try:
                world_dist.add_location(new_location, new_item)
            except KeyError:
                print('Cannot place item at excluded location because it already has an item defined in the Distribution.')


    def fill(self, window, worlds, location_pools, item_pools):
        search = Search.max_explore([world.state for world in worlds], itertools.chain.from_iterable(item_pools))
        if not search.can_beat_game(False):
            raise FillError('Item pool does not contain items required to beat game!')

        for world_dist in self.world_dists:
            world_dist.fill(window, worlds, location_pools, item_pools)


    def cloak(self, worlds, location_pools, model_pools):
        for world_dist in self.world_dists:
            world_dist.cloak(worlds, location_pools, model_pools)


    def configure_triforce_hunt(self, worlds):
        total_count = 0
        total_starting_count = 0
        for world in worlds:
            world.triforce_count = world.distribution.item_pool['Triforce Piece'].count
            if 'Triforce Piece' in world.distribution.starting_items:
                world.triforce_count += world.distribution.starting_items['Triforce Piece'].count
                total_starting_count += world.distribution.starting_items['Triforce Piece'].count
            if world.settings.skip_child_zelda and 'Song from Impa' in world.distribution.locations and world.distribution.locations['Song from Impa'].item == 'Triforce Piece':
                total_starting_count += 1
            total_count += world.triforce_count

        if total_count < worlds[0].triforce_goal:
            raise RuntimeError('Not enough Triforce Pieces in the worlds. There should be at least %d and there are only %d.' % (worlds[0].triforce_goal, total_count))

        if total_starting_count >= worlds[0].triforce_goal:
            raise RuntimeError('Too many Triforce Pieces in starting items. There should be at most %d and there are %d.' % (worlds[0].triforce_goal - 1, total_starting_count))

        for world in worlds:
            world.total_starting_triforce_count = total_starting_count # used later in Rules.py


    def reset(self):
        for world in self.world_dists:
            world.update({}, update_all=True)

        world_names = ['World %d' % (i + 1) for i in range(len(self.world_dists))]

        for k in per_world_keys:
            # Anything starting with ':' is output-only and we ignore it in world.update anyway.
            if k in self.src_dict and k[0] != ':':
                if isinstance(self.src_dict[k], dict):
                    # For each entry here of the form 'World %d', apply that entry to that world.
                    # If there are any entries that aren't of this form,
                    # apply them all to each world.
                    for world_id, world_name in enumerate(world_names):
                        if world_name in self.src_dict[k]:
                            self.world_dists[world_id].update({k: self.src_dict[k][world_name]})
                    src_all = {key: val for key, val in self.src_dict[k].items() if key not in world_names}
                    if src_all:
                        for world in self.world_dists:
                            world.update({k: src_all})
                else:
                    # Since it's not by world, apply to all worlds.
                    for world in self.world_dists:
                        world.update({k: self.src_dict[k]})


    def starting_items_from_settings(self, world_id):
        data = defaultdict(lambda: StarterRecord(0))
        if isinstance(self.settings.starting_items, dict):
            if self.settings.starting_equipment:
                raise ValueError('Incompatible starting item settings. Either move starting_equipment into starting_items or make starting_items a list')
            if self.settings.starting_songs:
                raise ValueError('Incompatible starting item settings. Either move starting_songs into starting_items or make starting_items a list')

            world_names = ['World %d' % (i + 1) for i in range(len(self.world_dists))]

            # For each entry here of the form 'World %d', apply that entry to that world.
            # If there are any entries that aren't of this form,
            # apply them all to each world.
            if world_names[world_id] in self.settings.starting_items:
                data.update((item_name, StarterRecord(count)) for item_name, count in self.settings.starting_items[world_names[world_id]].items())
            data.update(
                (item_name, StarterRecord(count))
                for item_name, count in self.settings.starting_items.items()
                if item_name not in world_names
            )
        else:
            starting_items = list(itertools.chain(self.settings.starting_equipment, self.settings.starting_items, self.settings.starting_songs))
            for itemsetting in starting_items:
                if itemsetting in StartingItems.everything:
                    item = StartingItems.everything[itemsetting]
                    if not item.special:
                        add_starting_item_with_ammo(data, item.itemname)
                    else:
                        if item.itemname == 'Rutos Letter' and self.settings.zora_fountain != 'open':
                            data['Rutos Letter'].count += 1
                        elif item.itemname in ['Bottle', 'Rutos Letter']:
                            data['Bottle'].count += 1
                        else:
                            raise KeyError("invalid special item: {}".format(item.itemname))
                else:
                    raise KeyError("invalid starting item: {}".format(itemsetting))

        # add hearts
        if self.settings.starting_hearts > 3:
            num_hearts_to_collect = self.settings.starting_hearts - 3
            if num_hearts_to_collect % 2 == 1:
                data['Piece of Heart'].count += 4
                num_hearts_to_collect -= 1
            for i in range(0, num_hearts_to_collect, 2):
                data['Piece of Heart'].count += 4
                data['Heart Container'].count += 1
            if self.settings.starting_hearts >= 20:
                data['Piece of Heart'].count -= 1
            if self.settings.item_pool_value == 'plentiful':
                data['Heart Container'].count += data['Piece of Heart'].count // 4
                data['Piece of Heart'].count = data['Piece of Heart'].count % 4

        return data


    def to_json(self, include_output=True, spoiler=True):
        self_dict = {
            ':version': __version__,
            'file_hash': CollapseList(self.file_hash),
            ':seed': self.settings.seed,
            ':settings_string': self.settings.settings_string,
            ':enable_distribution_file': self.settings.enable_distribution_file,
            'settings': self.settings.to_json(),
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
                self_dict[':playthrough'] = AlignedDict({
                    sphere_nr: SortedDict({
                        name: record.to_json() for name, record in sphere.items()
                    })
                    for (sphere_nr, sphere) in self.playthrough.items()
                }, depth=2)

            if self.entrance_playthrough is not None and len(self.entrance_playthrough) > 0:
                self_dict[':entrance_playthrough'] = AlignedDict({
                    sphere_nr: SortedDict({
                        name: record.to_json() for name, record in sphere.items()
                    })
                    for (sphere_nr, sphere) in self.entrance_playthrough.items()
                }, depth=2)

        if not include_output:
            strip_output_only(self_dict)
            self_dict['settings'] = dict(self._settings)
        return self_dict


    def to_str(self, include_output_only=True, spoiler=True):
        return dump_obj(self.to_json(include_output_only, spoiler))


    def __str__(self):
        return dump_obj(self.to_json())


    def update_spoiler(self, spoiler, output_spoiler):
        self.file_hash = [HASH_ICONS[icon] for icon in spoiler.file_hash]

        if not output_spoiler:
            return

        spoiler.parse_data()

        for world in spoiler.worlds:
            world_dist = self.world_dists[world.id]
            world_dist.randomized_settings = {randomized_item: getattr(world.settings, randomized_item) for randomized_item in world.randomized_list}
            world_dist.dungeons = {dung: DungeonRecord({ 'mq': world.dungeon_mq[dung] }) for dung in world.dungeon_mq}
            world_dist.trials = {trial: TrialRecord({ 'active': not world.skipped_trials[trial] }) for trial in world.skipped_trials}
            if hasattr(world, 'song_notes'):
                world_dist.songs = {song: SongRecord({ 'notes': str(world.song_notes[song]) }) for song in world.song_notes}
            world_dist.entrances = {ent.name: EntranceRecord.from_entrance(ent) for ent in spoiler.entrances[world.id]}
            world_dist.locations = {loc: LocationRecord.from_item(item) for (loc, item) in spoiler.locations[world.id].items()}
            world_dist.woth_locations = {loc.name: LocationRecord.from_item(loc.item) for loc in spoiler.required_locations[world.id]}
            world_dist.goal_locations = {}
            if world.id in spoiler.goal_locations and spoiler.goal_locations[world.id]:
                for cat_name, goals in spoiler.goal_locations[world.id].items():
                    world_dist.goal_locations[cat_name] = {}
                    for goal_name, location_worlds in goals.items():
                        goal = spoiler.goal_categories[world.id][cat_name].get_goal(goal_name)
                        goal_text = goal.hint_text.replace('#', '')
                        goal_text = goal_text[0].upper() + goal_text[1:]
                        # Add Token/Triforce Piece reachability data
                        if goal.items[0]['name'] == 'Triforce Piece':
                            goal_text +=  ' (' + str(goal.items[0]['quantity']) + '/' + str(world.triforce_count) + ' reachable)'
                        if goal.items[0]['name'] == 'Gold Skulltula Token':
                            goal_text +=  ' (' + str(goal.items[0]['quantity']) + '/100 reachable)'
                        world_dist.goal_locations[cat_name][goal_text] = {}
                        for location_world, locations in location_worlds.items():
                            if len(self.world_dists) == 1:
                                world_dist.goal_locations[cat_name][goal_text] = {loc.name: LocationRecord.from_item(loc.item).to_json() for loc in locations}
                            else:
                                world_dist.goal_locations[cat_name][goal_text]['from World ' + str(location_world + 1)] = {loc.name: LocationRecord.from_item(loc.item).to_json() for loc in locations}
            world_dist.barren_regions = [*world.empty_areas]
            world_dist.gossip_stones = {}
            for loc in spoiler.hints[world.id]:
                hint = GossipRecord(spoiler.hints[world.id][loc].to_json())
                if loc in gossipLocations:
                    world_dist.gossip_stones[gossipLocations[loc].name] = hint
                else:
                    world_dist.gossip_stones["0x{:04X}".format(loc)] = hint

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

        self.entrance_playthrough = {}
        for (sphere_nr, sphere) in spoiler.entrance_playthrough.items():
            if len(sphere) > 0:
                ent_rec_sphere = {}
                self.entrance_playthrough[sphere_nr] = ent_rec_sphere
                for entrance in sphere:
                    if spoiler.settings.world_count > 1:
                        entrance_key = '%s [W%d]' % (entrance.name, entrance.world.id + 1)
                    else:
                        entrance_key = entrance.name

                    ent_rec_sphere[entrance_key] = EntranceRecord.from_entrance(entrance)


    @staticmethod
    def from_file(settings, filename):
        if any(map(filename.endswith, ['.z64', '.n64', '.v64'])):
            raise InvalidFileException("Your Ocarina of Time ROM doesn't belong in the plandomizer setting. If you don't know what plandomizer is, or don't plan to use it, leave that setting blank and try again.")

        try:
            with open(filename, encoding='utf-8') as infile:
                src_dict = json.load(infile)
        except json.decoder.JSONDecodeError as e:
            raise InvalidFileException(f"Invalid Plandomizer File. Make sure the file is a valid JSON file. Failure reason: {str(e)}") from None
        return Distribution(settings, src_dict)


    def to_file(self, filename, output_spoiler):
        json = self.to_str(spoiler=output_spoiler)
        with open(filename, 'w', encoding='utf-8') as outfile:
            outfile.write(json)


def add_starting_item_with_ammo(starting_items, item_name, count=1):
    if item_name not in starting_items:
        starting_items[item_name] = StarterRecord(0)
    starting_items[item_name].count += count
    for item in StartingItems.inventory.values():
        if item.itemname == item_name and item.ammo:
            for ammo, qty in item.ammo.items():
                if ammo not in starting_items:
                    starting_items[ammo] = StarterRecord(0)
                starting_items[ammo].count = qty[starting_items[item_name].count - 1]
            break


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
