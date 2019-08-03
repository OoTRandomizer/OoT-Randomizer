from State import State
from Region import Region
from Entrance import Entrance
from Hints import get_hint_area
from Location import Location, LocationFactory
from LocationList import business_scrubs
from DungeonList import create_dungeons
from Rules import set_rules, set_shop_rules
from Item import Item, ItemFactory
from RuleParser import Rule_AST_Transformer
from SettingsList import get_setting_info
import logging
import copy
import io
import json
import random
import re

class World(object):

    def __init__(self, id, settings):
        self.id = id
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

        self.parser = Rule_AST_Transformer(self)
        self.event_items = set()

        # dump settings directly into world's namespace
        # this gives the world an attribute for every setting listed in Settings.py
        self.settings = settings
        self.__dict__.update(settings.__dict__)
        self.distribution = settings.distribution.world_dists[id]

        if self.open_forest == 'closed' and self.entrance_shuffle in ['all-indoors', 'all']:
            self.open_forest = 'closed_deku'

        # rename a few attributes...
        self.keysanity = self.shuffle_smallkeys in ['keysanity', 'remove']
        self.check_beatable_only = not self.all_reachable
    
        self.shuffle_dungeon_entrances = self.entrance_shuffle != 'off'
        self.shuffle_grotto_entrances = self.entrance_shuffle in ['simple-indoors', 'all-indoors', 'all']
        self.shuffle_interior_entrances = self.entrance_shuffle in ['simple-indoors', 'all-indoors', 'all']
        self.shuffle_special_indoor_entrances = self.entrance_shuffle in ['all-indoors', 'all']
        self.shuffle_overworld_entrances = self.entrance_shuffle == 'all'

        self.disable_trade_revert = self.shuffle_interior_entrances or self.shuffle_overworld_entrances

        # Determine LACS Condition
        if self.shuffle_ganon_bosskey == 'lacs_medallions':
            self.lacs_condition = 'medallions'
        elif self.shuffle_ganon_bosskey == 'lacs_dungeons':
            self.lacs_condition = 'dungeons'
        elif self.shuffle_ganon_bosskey == 'lacs_stones':
            self.lacs_condition = 'stones'
        else:
            self.lacs_condition = 'vanilla'

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

        self.resolve_random_settings()

        # Create attributes for each skull reward amount for logic
        self.skull_price_10 = self.skull_reward_multiplier * 1
        self.skull_price_20 = self.skull_reward_multiplier * 2
        self.skull_price_30 = self.skull_reward_multiplier * 3
        self.skull_price_40 = self.skull_reward_multiplier * 4
        self.skull_price_50 = self.skull_reward_multiplier * 5


    def copy(self):
        new_world = World(self.id, self.settings)
        new_world.skipped_trials = copy.copy(self.skipped_trials)
        new_world.dungeon_mq = copy.copy(self.dungeon_mq)
        new_world.big_poe_count = copy.copy(self.big_poe_count)
        new_world.starting_tod = self.starting_tod
        new_world.starting_age = self.starting_age
        new_world.can_take_damage = self.can_take_damage
        new_world.shop_prices = copy.copy(self.shop_prices)
        new_world.distribution = self.distribution

        new_world.regions = [region.copy(new_world) for region in self.regions]
        for region in new_world.regions:
            for exit in region.exits:
                exit.connect(new_world.get_region(exit.connected_region))

        new_world.dungeons = [dungeon.copy(new_world) for dungeon in self.dungeons]
        new_world.itempool = [item.copy(new_world) for item in self.itempool]
        new_world.state = self.state.copy(new_world)

        # copy any randomized settings to match the original copy
        new_world.randomized_list = list(self.randomized_list)
        for randomized_item in new_world.randomized_list:
            setattr(new_world, randomized_item, getattr(self, randomized_item))

        return new_world


    def resolve_random_settings(self):
        # evaluate settings (important for logic, nice for spoiler)
        self.randomized_list = []
        if self.big_poe_count_random:
            self.big_poe_count = random.randint(1, 10)
            self.randomized_list.append('big_poe_count')
        if self.starting_tod == 'random':
            setting_info = get_setting_info('starting_tod')
            choices = [ch for ch in setting_info.choices if ch not in ['default', 'random']]
            self.starting_tod = random.choice(choices)
            self.randomized_list.append('starting_tod')
        if self.starting_age == 'random':
            self.starting_age = random.choice(['child', 'adult'])
            self.randomized_list.append('starting_age')
        if self.chicken_count_random:
            self.chicken_count = random.randint(0, 7)
            self.randomized_list.append('chicken_count')
        if self.skull_reward_multiplier_random:
            self.skull_reward_multiplier = random.randint(1, 20)
            self.randomized_list.append('skull_reward_multiplier')

        # Determine Ganon Trials
        trial_pool = list(self.skipped_trials)
        dist_chosen = self.distribution.configure_trials(trial_pool)
        dist_num_chosen = len(dist_chosen)

        if self.trials_random:
            self.trials = dist_num_chosen + random.randint(0, len(trial_pool))
            self.randomized_list.append('trials')
        num_trials = int(self.trials)
        choosen_trials = random.sample(trial_pool, num_trials - dist_num_chosen)
        for trial in self.skipped_trials:
            if trial not in choosen_trials and trial not in dist_chosen:
                self.skipped_trials[trial] = True

        # Determine MQ Dungeons
        dungeon_pool = list(self.dungeon_mq)
        dist_num_mq = self.distribution.configure_dungeons(self, dungeon_pool)

        if self.mq_dungeons_random:
            for dungeon in dungeon_pool:
                self.dungeon_mq[dungeon] = random.choice([True, False])
            self.mq_dungeons = list(self.dungeon_mq.values()).count(True)
            self.randomized_list.append('mq_dungeons')
        else:
            mqd_picks = random.sample(dungeon_pool, self.mq_dungeons - dist_num_mq)
            for dung in mqd_picks:
                self.dungeon_mq[dung] = True


    def load_regions_from_json(self, file_path):
        json_string = ""
        with io.open(file_path, 'r') as file:
            for line in file.readlines():
                json_string += line.split('#')[0].replace('\n', ' ')
        json_string = re.sub(' +', ' ', json_string)
        try:
            region_json = json.loads(json_string)
        except json.JSONDecodeError as error:
            raise Exception("JSON parse error around text:\n" + \
                            json_string[error.pos-35:error.pos+35] + "\n" + \
                            "                                   ^^\n")
            
        for region in region_json:
            new_region = Region(region['region_name'])
            new_region.world = self
            if 'scene' in region:
                new_region.scene = region['scene']
            if 'hint' in region:
                new_region.hint = region['hint']
            if 'dungeon' in region:
                new_region.dungeon = region['dungeon']
            if 'time_passes' in region:
                new_region.time_passes = region['time_passes']
            if 'locations' in region:
                for location, rule in region['locations'].items():
                    new_location = LocationFactory(location)
                    new_location.parent_region = new_region
                    new_location.rule_string = rule
                    if self.logic_rules != 'none':
                        self.parser.parse_spot_rule(new_location)
                    new_location.world = self
                    new_region.locations.append(new_location)
            if 'events' in region:
                for event, rule in region['events'].items():
                    # Allow duplicate placement of events
                    lname = '%s from %s' % (event, new_region.name)
                    new_location = Location(lname, type='Event', parent=new_region)
                    new_location.rule_string = rule
                    if self.logic_rules != 'none':
                        self.parser.parse_spot_rule(new_location)
                    new_location.world = self
                    new_region.locations.append(new_location)
                    self.push_item(new_location, ItemFactory(event, self, event=True))
                    new_location.locked = True
                    self.event_items.add(event)
            if 'exits' in region:
                for exit, rule in region['exits'].items():
                    new_exit = Entrance('%s -> %s' % (new_region.name, exit), new_region)
                    new_exit.connected_region = exit
                    new_exit.rule_string = rule
                    if self.logic_rules != 'none':
                        self.parser.parse_spot_rule(new_exit)
                    new_region.exits.append(new_exit)
            self.regions.append(new_region)


    def create_internal_locations(self):
        self.parser.create_delayed_rules()
        assert self.parser.events <= self.event_items, 'Parse error: undefined items %r' % (self.parser.events - self.event_items)


    def initialize_entrances(self):
        for region in self.regions:
            for exit in region.exits:
                exit.connect(self.get_region(exit.connected_region))
                exit.world = self


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


    rewardlist = (
        'Kokiri Emerald',
        'Goron Ruby',
        'Zora Sapphire',
        'Forest Medallion',
        'Fire Medallion',
        'Water Medallion',
        'Spirit Medallion',
        'Shadow Medallion',
        'Light Medallion'
    )
    boss_location_names = (
        'Queen Gohma',
        'King Dodongo',
        'Barinade',
        'Phantom Ganon',
        'Volvagia',
        'Morpha',
        'Bongo Bongo',
        'Twinrova',
        'Links Pocket'
    )
    def fill_bosses(self, bossCount=9):
        boss_rewards = ItemFactory(self.rewardlist, self)
        boss_locations = [self.get_location(loc) for loc in self.boss_location_names]

        placed_prizes = [loc.item.name for loc in boss_locations if loc.item is not None]
        unplaced_prizes = [item for item in boss_rewards if item.name not in placed_prizes]
        empty_boss_locations = [loc for loc in boss_locations if loc.item is None]
        prizepool = list(unplaced_prizes)
        prize_locs = list(empty_boss_locations)

        bossCount -= self.distribution.fill_bosses(self, prize_locs, prizepool)

        while bossCount:
            bossCount -= 1
            random.shuffle(prizepool)
            random.shuffle(prize_locs)
            item = prizepool.pop()
            loc = prize_locs.pop()
            self.push_item(loc, item)


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


    def get_itempool_with_dungeon_items(self):
        return self.get_restricted_dungeon_items() + self.get_unrestricted_dungeon_items() + self.itempool


    # get a list of items that should stay in their proper dungeon
    def get_restricted_dungeon_items(self):
        itempool = []
        if self.shuffle_mapcompass == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.dungeon_items])
        if self.shuffle_smallkeys == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.small_keys])
        if self.shuffle_bosskeys == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons if dungeon.name != 'Ganons Castle' for item in dungeon.boss_key])
        if self.shuffle_ganon_bosskey == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons if dungeon.name == 'Ganons Castle' for item in dungeon.boss_key])

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
            itempool.extend([item for dungeon in self.dungeons if dungeon.name != 'Ganons Castle' for item in dungeon.boss_key])
        if self.shuffle_ganon_bosskey == 'keysanity':
            itempool.extend([item for dungeon in self.dungeons if dungeon.name == 'Ganons Castle' for item in dungeon.boss_key])

        for item in itempool:
            item.world = self
        return itempool


    def find_items(self, item):
        return [location for location in self.get_locations() if location.item is not None and location.item.name == item]


    def push_item(self, location, item, manual=False):
        if not isinstance(location, Location):
            location = self.get_location(location)

        # This check should never be false normally, but is here as a sanity check
        if location.can_fill_fast(item, manual):
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


    def get_entrances(self):
        return [entrance for region in self.regions for entrance in region.entrances]


    def get_shuffled_entrances(self, type=None):
        return [entrance for entrance in self.get_entrances() if entrance.shuffled and (type == None or entrance.type == type)]


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
            location_hint = get_hint_area(location)

            # We exclude event and locked locations. This means that medallions
            # and stones are not considered here. This is not really an accurate
            # way of doing this, but it's the only way to allow dungeons to appear.
            # So barren hints do not include these dungeon rewards.
            if location_hint in excluded_areas or \
               location.locked or \
               location.item is None or \
               location.item.type in ('Event', 'DungeonReward'):
                continue

            area = location_hint

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
            'Biggoron Sword',
        ]
        if (self.damage_multiplier != 'ohko' and self.damage_multiplier != 'quadruple' and 
            self.shuffle_scrubs == 'off' and not self.shuffle_grotto_entrances):
            # nayru's love may be required to prevent forced damage
            exclude_item_list.append('Nayrus Love')
        if self.hints != 'agony':
            # Stone of Agony only required if it's used for hints
            exclude_item_list.append('Stone of Agony')
        if not self.shuffle_special_indoor_entrances and not self.shuffle_overworld_entrances:
            # Serenade and Prelude are never required with vanilla Links House/ToT and overworld entrances
            exclude_item_list.append('Serenade of Water')
            exclude_item_list.append('Prelude of Light')

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
            world_id = location.item.world.id
            item = location.item

            if item.name == 'Bottle with Letter' and item.name in duplicate_item_woth[world_id]:
                # Only the first Letter counts as a letter, subsequent ones are Bottles.
                # It doesn't matter which one is considered bottle/letter, since they will
                # both we considered not useless.
                item_name = 'Bottle'
            elif item.special.get('bottle', False):
                # Bottles can have many names but they are all generally the same in logic.
                # The letter and big poe bottles will give a bottle item, so no additional
                # checks are required for them.
                item_name = 'Bottle'
            else:
                item_name = item.name

            if item_name not in duplicate_item_woth[world_id]:
                duplicate_item_woth[world_id][item_name] = []
            duplicate_item_woth[world_id][item_name].append(location)

        # generate the empty area list
        self.empty_areas = {}

        for area,area_info in areas.items():
            useless_area = True
            for location in area_info['locations']:
                world_id = location.item.world.id
                item = location.item

                if (not location.item.majoritem) or (location.item.name in exclude_item_list):
                    # Minor items are always useless in logic
                    continue

                is_bottle = False
                if item.name == 'Bottle with Letter' and item.name in duplicate_item_woth[world_id]:
                    # If this is the required Letter then it is not useless
                    dupe_locations = duplicate_item_woth[world_id][item.name]
                    for dupe_location in dupe_locations:
                        if dupe_location.world.id == location.world.id and dupe_location.name == location.name:
                            useless_area = False
                            break
                    # Otherwise it is treated as a bottle
                    is_bottle = True

                if is_bottle or item.special.get('bottle', False):
                    # Bottle Items are all interchangable. Logic currently only needs
                    # a max on 1 bottle, but this might need to be changed in the
                    # future if using multiple bottles for fire temple diving is added
                    # to logic
                    dupe_locations = duplicate_item_woth[world_id].get('Bottle', [])
                    max_progressive = 1
                elif item.name == 'Bottle with Big Poe':
                    # The max number of requred Big Poe Bottles is based on the setting
                    dupe_locations = duplicate_item_woth[world_id].get(item.name, [])
                    max_progressive = self.settings.big_poe_count
                else:
                    dupe_locations = duplicate_item_woth[world_id].get(item.name, [])
                    max_progressive = item.special.get('progressive', 1)

                # If this is a required item location, then it is not useless
                for dupe_location in dupe_locations:
                    if dupe_location.world.id == location.world.id and dupe_location.name == location.name:
                        useless_area = False
                        break

                # If there are sufficient required item known, then the remaining
                # copies of the items are useless.
                if len(dupe_locations) < max_progressive:
                    useless_area = False
                    break

            if useless_area:
                self.empty_areas[area] = area_info
