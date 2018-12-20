from State import State
from Region import Region
from Entrance import Entrance
from Location import Location, LocationFactory
from DungeonList import create_dungeons
from Rules import set_rules, set_shop_rules
from Item import Item
from RuleParser import parse_rule_string
from SettingsList import get_setting_info
import logging
import copy
import io
import json
import random

class World(object):

    def __init__(self, settings):
        self.shuffle = 'vanilla'
        self.dungeons = []
        self.regions = []
        self.itempool = []
        self.state = State(self)
        self._cached_locations = None
        self._entrance_cache = {}
        self._region_cache = {}
        self._location_cache = {}
        self.required_locations = []
        self.shop_prices = {}
        self.light_arrow_location = None

        # dump settings directly into world's namespace
        # this gives the world an attribute for every setting listed in Settings.py
        self.settings = settings
        self.__dict__.update(settings.__dict__)
        # evaluate settings (important for logic, nice for spoiler)
        if self.starting_tod == 'random':
            setting_info = get_setting_info('starting_tod')
            choices = [ch for ch in setting_info.choices.values() if ch not in ['default', 'random']]
            self.starting_tod = random.choice(choices)
        # rename a few attributes...
        self.keysanity = self.shuffle_smallkeys != 'dungeon'
        self.check_beatable_only = not self.all_reachable
        # trials that can be skipped will be decided later
        self.skipped_trials = {
            'Forest': False,
            'Fire': False,
            'Water': False,
            'Spirit': False,
            'Shadow': False,
            'Light': False
        }
        # dungeon forms will be decided later
        self.dungeon_mq = {
            'Deku Tree': False,
            'Dodongos Cavern': False,
            'Jabu Jabus Belly': False,
            'Bottom of the Well': False,
            'Ice Cavern': False,
            'Gerudo Training Grounds': False,
            'Forest Temple': False,
            'Fire Temple': False,
            'Water Temple': False,
            'Spirit Temple': False,
            'Shadow Temple': False,
            'Ganons Castle': False
        }

        self.can_take_damage = True


    def copy(self):
        new_world = World(self.settings)
        new_world.skipped_trials = copy.copy(self.skipped_trials)
        new_world.dungeon_mq = copy.copy(self.dungeon_mq)
        new_world.big_poe_count = copy.copy(self.big_poe_count)
        new_world.can_take_damage = self.can_take_damage
        new_world.shop_prices = copy.copy(self.shop_prices)
        new_world.id = self.id

        new_world.regions = [region.copy(new_world) for region in self.regions]
        for region in new_world.regions:
            for exit in region.exits:
                exit.connect(new_world.get_region(exit.connected_region))

        new_world.dungeons = [dungeon.copy(new_world) for dungeon in self.dungeons]
        new_world.itempool = [item.copy(new_world) for item in self.itempool]
        new_world.state = self.state.copy(new_world)

        return new_world


    def load_regions_from_json(self, file_path):
        json_string = ""
        with io.open(file_path, 'r') as file:
            for line in file.readlines():
                json_string += line.split('#')[0].replace('\n', ' ')
        region_json = json.loads(json_string)

        for region in region_json:
            new_region = Region(region['region_name'])
            new_region.world = self
            if 'dungeon' in region:
                new_region.dungeon = region['dungeon']
            if 'locations' in region:
                for location, rule in region['locations'].items():
                    new_location = LocationFactory(location)
                    new_location.parent_region = new_region
                    if self.logic_rules != 'none':
                        new_location.access_rule = parse_rule_string(rule, self)
                    new_location.world = self
                    new_region.locations.append(new_location)
            if 'exits' in region:
                for exit, rule in region['exits'].items():
                    new_exit = Entrance('%s -> %s' % (new_region.name, exit), new_region)
                    new_exit.connected_region = exit
                    if self.logic_rules != 'none':
                        new_exit.access_rule = parse_rule_string(rule, self)
                    new_region.exits.append(new_exit)
            self.regions.append(new_region)


    def initialize_entrances(self):
        for region in self.regions:
            for exit in region.exits:
                exit.connect(self.get_region(exit.connected_region))        


    def initialize_regions(self):
        for region in self.regions:
            region.world = self
            for location in region.locations:
                location.world = self


    def initialize_items(self):
        for item in self.itempool:
            item.world = self
        for region in self.regions:
            for location in region.locations:
                if location.item != None:
                    location.item.world = self
        for item in [item for dungeon in self.dungeons for item in dungeon.all_items]:
            item.world = self


    def random_shop_prices(self):
        shop_item_indexes = ['7', '5', '8', '6']
        self.shop_prices = {}
        for region in self.regions:
            if self.shopsanity == 'random':
                shop_item_count = random.randint(0,4)
            else:
                shop_item_count = int(self.shopsanity)

            for location in region.locations:
                if location.type == 'Shop':
                    if location.name[-1:] in shop_item_indexes[:shop_item_count]:
                        self.shop_prices[location.name] = int(random.betavariate(1.5, 2) * 60) * 5


    def get_region(self, regionname):
        if isinstance(regionname, Region):
            return regionname
        try:
            return self._region_cache[regionname]
        except KeyError:
            for region in self.regions:
                if region.name == regionname:
                    self._region_cache[regionname] = region
                    return region
            raise RuntimeError('No such region %s' % regionname)


    def get_entrance(self, entrance):
        if isinstance(entrance, Entrance):
            return entrance
        try:
            return self._entrance_cache[entrance]
        except KeyError:
            for region in self.regions:
                for exit in region.exits:
                    if exit.name == entrance:
                        self._entrance_cache[entrance] = exit
                        return exit
            raise RuntimeError('No such entrance %s' % entrance)


    def get_location(self, location):
        if isinstance(location, Location):
            return location
        try:
            return self._location_cache[location]
        except KeyError:
            for region in self.regions:
                for r_location in region.locations:
                    if r_location.name == location:
                        self._location_cache[location] = r_location
                        return r_location
        raise RuntimeError('No such location %s' % location)


    def get_items(self):
        return [loc.item for loc in self.get_filled_locations()] + self.itempool


    # get a list of items that should stay in their proper dungeon
    def get_restricted_dungeon_items(self):
        itempool = []
        if self.shuffle_mapcompass == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.dungeon_items])
        if self.shuffle_smallkeys == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.small_keys])
        if self.shuffle_bosskeys == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.boss_key])

        for item in itempool:
            item.world = self
        return itempool


    # get a list of items that don't have to be in their proper dungeon
    def get_unrestricted_dungeon_items(self):
        itempool = []
        if self.shuffle_mapcompass == 'keysanity':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.dungeon_items])
        if self.shuffle_smallkeys == 'keysanity':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.small_keys])
        if self.shuffle_bosskeys == 'keysanity':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.boss_key])

        for item in itempool:
            item.world = self
        return itempool


    def find_items(self, item):
        return [location for location in self.get_locations() if location.item is not None and location.item.name == item]


    def push_item(self, location, item):
        if not isinstance(location, Location):
            location = self.get_location(location)

        # This check should never be false normally, but is here as a sanity check
        if location.can_fill_fast(item):
            location.item = item
            item.location = location
            item.price = location.price if location.price is not None else item.price
            location.price = item.price

            logging.getLogger('').debug('Placed %s [World %d] at %s [World %d]', item, item.world.id if hasattr(item, 'world') else -1, location, location.world.id if hasattr(location, 'world') else -1)
        else:
            raise RuntimeError('Cannot assign item %s to location %s.' % (item, location))


    def get_locations(self):
        if self._cached_locations is None:
            self._cached_locations = []
            for region in self.regions:
                self._cached_locations.extend(region.locations)
        return self._cached_locations


    def get_unfilled_locations(self):
        return [location for location in self.get_locations() if location.item is None]


    def get_filled_locations(self):
        return [location for location in self.get_locations() if location.item is not None]


    def get_reachable_locations(self, state=None):
        if state is None:
            state = self.state
        return [location for location in self.get_locations() if state.can_reach(location)]


    def get_placeable_locations(self, state=None):
        if state is None:
            state = self.state
        return [location for location in self.get_locations() if location.item is None and state.can_reach(location)]


    def unlocks_new_location(self, item):
        temp_state = self.state.copy()
        temp_state.clear_cached_unreachable()
        temp_state.collect(item)

        for location in self.get_unfilled_locations():
            if temp_state.can_reach(location) and not self.state.can_reach(location):
                return True

        return False


    def has_beaten_game(self, state):
        return state.has('Triforce')


    def update_useless_areas(self):
        areas = {}
        excluded_areas = [None, "Link's Pocket", "Ganon's Tower"]
        for location in self.get_locations():
            if location.hint in excluded_areas or \
               location.locked or \
               location.item is None or \
               location.item.type == "Event":
                continue
            if location.hint in areas:
                areas[location.hint].append(location)
            else:
                areas[location.hint] = [location]

        self.empty_areas = []
        for area,locations in areas.items():
            useless_area = True
            for location in locations:
                if location.item.majoritem:
                    useless_area = False
                    break
            if useless_area:
                self.empty_areas.append(area)
