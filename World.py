from State import State
from Region import Region
from Entrance import Entrance
from Location import Location, LocationFactory
from LocationList import business_scrubs
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
        self.scrub_prices = {}
        self.light_arrow_location = None

        # dump settings directly into world's namespace
        # this gives the world an attribute for every setting listed in Settings.py
        self.settings = settings
        self.__dict__.update(settings.__dict__)

        # evaluate settings (important for logic, nice for spoiler)
        if self.big_poe_count_random:
            self.big_poe_count = random.randint(1, 10)
        if self.starting_tod == 'random':
            setting_info = get_setting_info('starting_tod')
            choices = [ch for ch in setting_info.choices if ch not in ['default', 'random']]
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


    def set_scrub_prices(self):
        # Get Deku Scrub Locations
        scrub_locations = [location for location in self.get_locations() if 'Deku Scrub' in location.name]
        scrub_dictionary = {}
        for location in scrub_locations:
            if location.default not in scrub_dictionary:
                scrub_dictionary[location.default] = []
            scrub_dictionary[location.default].append(location)

        # Loop through each type of scrub.
        for (scrub_item, default_price, text_id, text_replacement) in business_scrubs:
            price = default_price
            if self.shuffle_scrubs == 'low':
                price = 10
            elif self.shuffle_scrubs == 'random':
                # this is a random value between 0-99
                # average value is ~33 rupees
                price = int(random.betavariate(1, 2) * 99)

            # Set price in the dictionary as well as the location.
            self.scrub_prices[scrub_item] = price
            if scrub_item in scrub_dictionary:
                for location in scrub_dictionary[scrub_item]:
                    location.price = price
                    if location.item is not None:
                        location.item.price = price


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
            raise KeyError('No such region %s' % regionname)


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
            raise KeyError('No such entrance %s' % entrance)


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
        raise KeyError('No such location %s' % location)


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

    # Useless areas are areas that have contain no items that could ever
    # be used to complete the seed. Unfortunately this is very difficult
    # to calculate since that involves trying every possible path and item
    # set collected to know this. To simplify this we instead just get areas
    # that don't have any items that could ever be required in any seed.
    # We further cull this list with woth info. This is an overestimate of
    # the true list of possible useless areas, but this will generate a 
    # reasonably sized list of areas that fit this property.
    def update_useless_areas(self, spoiler):
        areas = {}
        # Link's Pocket and None are not real areas
        excluded_areas = [None, "Link's Pocket"]
        for location in self.get_locations():
            # We exclude event and locked locations. This means that medallions
            # and stones are not considered here. This is not really an accurate
            # way of doing this, but it's the only way to allow dungeons to appear.
            # So barren hints do not include these dungeon rewards.
            if location.hint in excluded_areas or \
               location.locked or \
               location.item is None or \
               location.item.type == "Event":
                continue

            area = location.hint

            # Build the area list and their items
            if area not in areas:
                areas[area] = {
                    'locations': [],
                }
            areas[area]['locations'].append(location)

        # Generate area list meta data
        for area,area_info in areas.items():
            # whether an area is a dungeon is calculated to prevent too many
            # dungeon barren hints since they are quite powerful. The area
            # names don't quite match the internal dungeon names so we need to
            # check if any location in the area has a dungeon.
            area_info['dungeon'] = False
            for location in area_info['locations']:
                if location.parent_region.dungeon is not None:
                    area_info['dungeon'] = True
                    break
            # Weight the area's chance of being chosen based on its size.
            # Small areas are more likely to barren, so we apply this weight
            # to make all areas have a more uniform chance of being chosen
            area_info['weight'] = len(area_info['locations'])

        # these are items that can never be required but are still considered major items
        exclude_item_list = [
            'Double Defense',
            'Ice Arrows',
            'Serenade of Water',
            'Prelude of Light',
            'Biggoron Sword',
        ]
        if self.damage_multiplier != 'ohko' and self.damage_multiplier != 'quadruple' and self.shuffle_scrubs == 'off':
            # nayru's love may be required to prevent forced damage
            exclude_item_list.append('Nayrus Love')
        if self.hints != 'agony':
            # Stone of Agony only required if it's used for hints
            exclude_item_list.append('Stone of Agony')

        # The idea here is that if an item shows up in woth, then the only way
        # that another copy of that major item could ever be required is if it
        # is a progressive item. Normally this applies to things like bows, bombs
        # bombchus, bottles, slingshot, magic and ocarina. However if plentiful
        # item pool is enabled this could be applied to any item.
        duplicate_item_woth = {}
        woth_loc = [location for world_woth in spoiler.required_locations.values() for location in world_woth]
        for world in spoiler.worlds:
            duplicate_item_woth[world.id] = {}
        for location in woth_loc:
            if not location.item.special.get('progressive', False):
                # Progressive items may need multiple copies to make progression
                # so we can't make this culling for those kinds of items.
                duplicate_item_woth[location.item.world.id][location.item.name] = location
            if 'Bottle' in location.item.name and \
                location.item.name not in ['Bottle with Letter', 'Bottle with Big Poe']:
                    # Bottles can have many names but they are all generally the same in logic
                    # The problem is that Ruto's Letter and Big Poe might not be usuable as a 
                    # Bottle immediately, so they might need to use a regular bottle in
                    # addition to that one. Conversely finding a bottle might mean you still
                    # need ruto's letter or big poe. So to work with this, we ignore those
                    # two special bottles as being bottles
                    duplicate_item_woth[location.item.world.id]['Bottle'] = location

        # generate the empty area list
        self.empty_areas = {}
        for area,area_info in areas.items():
            useless_area = True
            for location in area_info['locations']:
                if location.item.majoritem:
                    if (location.item.name in exclude_item_list):
                        continue

                    if 'Bottle' in location.item.name and location.item.name not in ['Bottle with Letter', 'Bottle with Big Poe']:
                        dupe_location = duplicate_item_woth[location.item.world.id].get('Bottle', location)
                    else:
                        dupe_location = duplicate_item_woth[location.item.world.id].get(location.item.name, location)

                    if (dupe_location.world.id != location.world.id or dupe_location.name != location.name):
                        continue

                    useless_area = False
                    break
            if useless_area:
                self.empty_areas[area] = area_info
