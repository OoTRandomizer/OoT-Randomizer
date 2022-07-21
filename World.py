from collections import OrderedDict
import copy
import logging
import random
import json

from Entrance import Entrance
from Goals import Goal, GoalCategory
from HintList import getRequiredHints, misc_item_hint_table
from Hints import HintArea, hint_dist_keys, HintDistFiles
from Item import ItemFactory, ItemInfo, MakeEventItem
from Location import Location, LocationFactory
from LocationList import business_scrubs
from Plandomizer import InvalidFileException
from Region import Region, TimeOfDay
from RuleParser import Rule_AST_Transformer
from SettingsList import get_setting_info, get_settings_from_section
from State import State
from Utils import read_logic_file

class World(object):

    def __init__(self, id, settings, resolveRandomizedSettings=True):
        self.id = id
        self.dungeons = []
        self.regions = []
        self.itempool = []
        self._cached_locations = None
        self._entrance_cache = {}
        self._region_cache = {}
        self._location_cache = {}
        self.required_locations = []
        self.shop_prices = {}
        self.scrub_prices = {}
        self.maximum_wallets = 0
        self.misc_hint_item_locations = {}
        self.triforce_count = 0
        self.total_starting_triforce_count = 0
        self.bingosync_url = None

        self.parser = Rule_AST_Transformer(self)
        self.event_items = set()

        # dump settings directly into world's namespace
        # this gives the world an attribute for every setting listed in Settings.py
        self.settings = settings
        self.distribution = settings.distribution.world_dists[id]

        # rename a few attributes...
        self.keysanity = settings.shuffle_smallkeys in ['keysanity', 'remove', 'any_dungeon', 'overworld']
        self.check_beatable_only = settings.reachable_locations != 'all'

        self.shuffle_special_interior_entrances = settings.shuffle_interior_entrances == 'all'
        self.shuffle_interior_entrances = settings.shuffle_interior_entrances in ['simple', 'all']

        self.shuffle_special_dungeon_entrances = settings.shuffle_dungeon_entrances == 'all'
        self.shuffle_dungeon_entrances = settings.shuffle_dungeon_entrances in ['simple', 'all']

        self.entrance_shuffle = (
            self.shuffle_interior_entrances or settings.shuffle_grotto_entrances or self.shuffle_dungeon_entrances
            or settings.shuffle_overworld_entrances or settings.owl_drops or settings.warp_songs
            or settings.spawn_positions or (settings.shuffle_bosses != 'off')
        )

        self.ensure_tod_access = self.shuffle_interior_entrances or settings.shuffle_overworld_entrances or settings.spawn_positions
        self.disable_trade_revert = self.shuffle_interior_entrances or settings.shuffle_overworld_entrances

        if (
            settings.open_forest == 'closed'
            and (
                self.shuffle_special_interior_entrances or settings.shuffle_overworld_entrances
                or settings.warp_songs or settings.spawn_positions or (settings.shuffle_bosses != 'off')
            )
        ):
            self.settings.open_forest = 'closed_deku'

        if settings.triforce_goal_per_world > settings.triforce_count_per_world:
            raise ValueError("Triforces required cannot be more than the triforce count.")
        self.triforce_goal = settings.triforce_goal_per_world * settings.world_count

        if settings.triforce_hunt:
            # Pin shuffle_ganon_bosskey to 'triforce' when triforce_hunt is enabled
            # (specifically, for randomize_settings)
            self.settings.shuffle_ganon_bosskey = 'triforce'

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
            'Gerudo Training Ground': False,
            'Forest Temple': False,
            'Fire Temple': False,
            'Water Temple': False,
            'Spirit Temple': False,
            'Shadow Temple': False,
            'Ganons Castle': False
        }

        if resolveRandomizedSettings:
            self.resolve_random_settings()

        if len(settings.hint_dist_user) == 0:
            for d in HintDistFiles():
                with open(d, 'r') as dist_file:
                    dist = json.load(dist_file)
                if dist['name'] == self.settings.hint_dist:
                    self.hint_dist_user = dist
        else:
            self.settings.hint_dist = 'custom'
            self.hint_dist_user = self.settings.hint_dist_user

        # Hack for legacy hint distributions from before the goal, dual and dual_always hint
        # types was created. Keeps validation happy.
        for hint_type in ('goal', 'dual', 'dual_always', 'entrance_always'):
            if 'distribution' in self.hint_dist_user and hint_type not in self.hint_dist_user['distribution']:
                self.hint_dist_user['distribution'][hint_type] = {"order": 0, "weight": 0.0, "fixed": 0, "copies": 0}
        if 'use_default_goals' not in self.hint_dist_user:
            self.hint_dist_user['use_default_goals'] = True
        if 'upgrade_hints' not in self.hint_dist_user:
            self.hint_dist_user['upgrade_hints'] = 'off'

        # Validate hint distribution format
        # Originally built when I was just adding the type distributions
        # Location/Item Additions and Overrides are not validated
        hint_dist_valid = False
        if all(key in self.hint_dist_user['distribution'] for key in hint_dist_keys):
            hint_dist_valid = True
            sub_keys = {'order', 'weight', 'fixed', 'copies'}
            for key in self.hint_dist_user['distribution']:
                if not all(sub_key in sub_keys for sub_key in self.hint_dist_user['distribution'][key]):
                    hint_dist_valid = False
        if not hint_dist_valid:
            raise InvalidFileException("""Hint distributions require all hint types be present in the distro 
                                          (trial, always, dual_always, woth, barren, item, song, overworld, dungeon, entrance,
                                          sometimes, dual, random, junk, named-item, goal). If a hint type should not be
                                          shuffled, set its order to 0. Hint type format is \"type\": { 
                                          \"order\": 0, \"weight\": 0.0, \"fixed\": 0, \"copies\": 0 }""")

        self.added_hint_types = {}
        self.item_added_hint_types = {}
        self.hint_exclusions = set()
        if settings.skip_child_zelda:
            self.hint_exclusions.add('Song from Impa')
        self.hint_type_overrides = {}
        self.item_hint_type_overrides = {}

        for dist in hint_dist_keys:
            self.added_hint_types[dist] = []
            for loc in self.hint_dist_user['add_locations']:
                if 'types' in loc:
                    if dist in loc['types']:
                        self.added_hint_types[dist].append(loc['location'])
            self.item_added_hint_types[dist] = []
            for i in self.hint_dist_user['add_items']:
                if dist in i['types']:
                    self.item_added_hint_types[dist].append(i['item'])
            self.hint_type_overrides[dist] = []
            for loc in self.hint_dist_user['remove_locations']:
                if dist in loc['types']:
                    self.hint_type_overrides[dist].append(loc['location'])
            self.item_hint_type_overrides[dist] = []
            for i in self.hint_dist_user['remove_items']:
                if dist in i['types']:
                    self.item_hint_type_overrides[dist].append(i['item'])


        self.hint_text_overrides = {}
        for loc in self.hint_dist_user['add_locations']:
            if 'text' in loc:
                # Arbitrarily throw an error at 80 characters to prevent overfilling the text box.
                if len(loc['text']) > 80:
                    raise Exception('Custom hint text too large for %s', loc['location'])
                self.hint_text_overrides.update({loc['location']: loc['text']})

        self.item_hints = self.settings.item_hints + self.item_added_hint_types["named-item"]
        self.named_item_pool = list(self.item_hints)

        self.always_hints = [hint.name for hint in getRequiredHints(self)]

        self.misc_hint_items = {hint_type: self.hint_dist_user.get('misc_hint_items', {}).get(hint_type, data['default_item']) for hint_type, data in misc_item_hint_table.items()}

        self.state = State(self)

        # Allows us to cut down on checking whether some items are required
        self.max_progressions = {name: item.special.get('progressive', 1) for name, item in ItemInfo.items.items()}
        max_tokens = 0
        if self.settings.bridge == 'tokens':
            max_tokens = max(max_tokens, self.settings.bridge_tokens)
        if self.settings.lacs_condition == 'tokens':
            max_tokens = max(max_tokens, self.settings.lacs_tokens)
        if self.settings.shuffle_ganon_bosskey == 'tokens':
            max_tokens = max(max_tokens, self.settings.ganon_bosskey_tokens)
        tokens = [50, 40, 30, 20, 10]
        for t in tokens:
            if f'Kak {t} Gold Skulltula Reward' not in self.settings.disabled_locations:
                max_tokens = max(max_tokens, t)
                break
        self.max_progressions['Gold Skulltula Token'] = max_tokens
        max_hearts = 0
        if self.settings.bridge == 'hearts':
            max_hearts = max(max_hearts, self.settings.bridge_hearts)
        if self.settings.lacs_condition == 'hearts':
            max_hearts = max(max_hearts, self.settings.lacs_hearts)
        if self.settings.shuffle_ganon_bosskey == 'hearts':
            max_hearts = max(max_hearts, self.settings.ganon_bosskey_hearts)
        self.max_progressions['Heart Container'] = max_hearts
        self.max_progressions['Piece of Heart'] = max_hearts * 4
        self.max_progressions['Piece of Heart (Treasure Chest Game)'] = max_hearts * 4
        # Additional Ruto's Letter become Bottle, so we may have to collect two.
        self.max_progressions['Rutos Letter'] = 2

        # Available Gold Skulltula Tokens in world. Set to proper value in ItemPool.py.
        self.available_tokens = 100

        # Disable goal hints if the hint distro does not require them.
        # WOTH locations are always searched.
        self.enable_goal_hints = False
        if ('distribution' in self.hint_dist_user and
           'goal' in self.hint_dist_user['distribution'] and
           (self.hint_dist_user['distribution']['goal']['fixed'] != 0 or
                self.hint_dist_user['distribution']['goal']['weight'] != 0)):
            self.enable_goal_hints = True

        # Initialize default goals for win condition
        self.goal_categories = OrderedDict()
        if self.hint_dist_user['use_default_goals']:
            self.set_goals()

        # import goals from hint plando
        if 'custom_goals' in self.hint_dist_user:
            for category in self.hint_dist_user['custom_goals']:
                if category['category'] in self.goal_categories:
                    cat = self.goal_categories[category['category']]
                else:
                    cat = GoalCategory(category['category'], category['priority'], minimum_goals=category['minimum_goals'])
                for goal in category['goals']:
                    cat.add_goal(Goal(self, goal['name'], goal['hint_text'], goal['color'], items=list({'name': i['name'], 'quantity': i['quantity'], 'minimum': i['minimum'], 'hintable': i['hintable']} for i in goal['items'])))
                if 'count_override' in category:
                    cat.goal_count = category['count_override']
                else:
                    cat.goal_count = len(cat.goals)
                if 'lock_entrances' in category:
                    cat.lock_entrances = list(category['lock_entrances'])
                self.goal_categories[cat.name] = cat

        # Sort goal hint categories by priority
        # For most settings this will be Bridge, GBK
        self.goal_categories = OrderedDict(sorted(self.goal_categories.items(), key=lambda kv: kv[1].priority))

        # Turn on one hint per goal if all goal categories contain the same goals.
        # Reduces the changes of randomly choosing one smaller category over and
        # over again after the first round through the categories.
        if len(self.goal_categories) > 0:
            self.one_hint_per_goal = True
            goal_list1 = [goal.name for goal in list(self.goal_categories.values())[0].goals]
            for category in self.goal_categories.values():
                if goal_list1 != [goal.name for goal in category.goals]:
                    self.one_hint_per_goal = False

        # initialize category check for first rounds of goal hints
        self.hinted_categories = []

        # Quick item lookup for All Goals Reachable setting
        self.goal_items = []
        for cat_name, category in self.goal_categories.items():
            for goal in category.goals:
                for item in goal.items:
                    self.goal_items.append(item['name'])

        # Separate goal categories into locked and unlocked for search optimization
        self.locked_goal_categories = dict(filter(lambda category: category[1].lock_entrances, self.goal_categories.items()))
        self.unlocked_goal_categories = dict(filter(lambda category: not category[1].lock_entrances, self.goal_categories.items()))

    def copy(self):
        new_world = World(self.id, self.settings, False)
        new_world.skipped_trials = copy.copy(self.skipped_trials)
        new_world.dungeon_mq = copy.copy(self.dungeon_mq)
        new_world.shop_prices = copy.copy(self.shop_prices)
        new_world.triforce_goal = self.triforce_goal
        new_world.triforce_count = self.triforce_count
        new_world.total_starting_triforce_count = self.total_starting_triforce_count
        new_world.maximum_wallets = self.maximum_wallets
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
            setattr(new_world, randomized_item, getattr(self.settings, randomized_item))

        new_world.always_hints = list(self.always_hints)
        new_world.max_progressions = copy.copy(self.max_progressions)
        new_world.available_tokens = self.available_tokens

        return new_world


    def set_random_bridge_values(self):
        if self.settings.bridge == 'medallions':
            self.settings.bridge_medallions = 6
            self.randomized_list.append('bridge_medallions')
        if self.settings.bridge == 'dungeons':
            self.settings.bridge_rewards = 9
            self.randomized_list.append('bridge_rewards')
        if self.settings.bridge == 'stones':
            self.settings.bridge_stones = 3
            self.randomized_list.append('bridge_stones')


    def resolve_random_settings(self):
        # evaluate settings (important for logic, nice for spoiler)
        self.randomized_list = []
        dist_keys = []
        if '_settings' in self.distribution.distribution.src_dict:
            dist_keys = self.distribution.distribution.src_dict['_settings'].keys()
        if self.settings.randomize_settings:
            setting_info = get_setting_info('randomize_settings')
            self.randomized_list.extend(setting_info.disable[True]['settings'])
            for section in setting_info.disable[True]['sections']:
                self.randomized_list.extend(get_settings_from_section(section))
                # Remove settings specified in the distribution
                self.randomized_list = [x for x in self.randomized_list if x not in dist_keys]
            for setting in list(self.randomized_list):
                if (setting == 'bridge_medallions' and self.settings.bridge != 'medallions') \
                        or (setting == 'bridge_stones' and self.settings.bridge != 'stones') \
                        or (setting == 'bridge_rewards' and self.settings.bridge != 'dungeons') \
                        or (setting == 'bridge_tokens' and self.settings.bridge != 'tokens') \
                        or (setting == 'bridge_hearts' and self.settings.bridge != 'hearts') \
                        or (setting == 'lacs_medallions' and self.settings.lacs_condition != 'medallions') \
                        or (setting == 'lacs_stones' and self.settings.lacs_condition != 'stones') \
                        or (setting == 'lacs_rewards' and self.settings.lacs_condition != 'dungeons') \
                        or (setting == 'lacs_tokens' and self.settings.lacs_condition != 'tokens') \
                        or (setting == 'lacs_hearts' and self.settings.lacs_condition != 'hearts') \
                        or (setting == 'ganon_bosskey_medallions' and self.settings.shuffle_ganon_bosskey != 'medallions') \
                        or (setting == 'ganon_bosskey_stones' and self.settings.shuffle_ganon_bosskey != 'stones') \
                        or (setting == 'ganon_bosskey_rewards' and self.settings.shuffle_ganon_bosskey != 'dungeons') \
                        or (setting == 'ganon_bosskey_tokens' and self.settings.shuffle_ganon_bosskey != 'tokens') \
                        or (setting == 'ganon_bosskey_hearts' and self.settings.shuffle_ganon_bosskey != 'hearts'):
                    self.randomized_list.remove(setting)
        if self.settings.big_poe_count_random and 'big_poe_count' not in dist_keys:
            self.settings.big_poe_count = random.randint(1, 10)
            self.randomized_list.append('big_poe_count')
        # If set to random in GUI, we don't want to randomize if it was specified as non-random in the distribution
        if (self.settings.starting_tod == 'random'
            and ('starting_tod' not in dist_keys
             or self.distribution.distribution.src_dict['_settings']['starting_tod'] == 'random')):
            setting_info = get_setting_info('starting_tod')
            choices = [ch for ch in setting_info.choices if ch not in ['default', 'random']]
            self.settings.starting_tod = random.choice(choices)
            self.randomized_list.append('starting_tod')
        if (self.settings.starting_age == 'random'
            and ('starting_age' not in dist_keys
             or self.distribution.distribution.src_dict['_settings']['starting_age'] == 'random')):
            if self.settings.open_forest == 'closed':
                # adult is not compatible
                self.settings.starting_age = 'child'
            else:
                self.settings.starting_age = random.choice(['child', 'adult'])
            self.randomized_list.append('starting_age')
        if self.settings.chicken_count_random and 'chicken_count' not in dist_keys:
            self.settings.chicken_count = random.randint(0, 7)
            self.randomized_list.append('chicken_count')
        
        # Determine dungeons with shortcuts
        dungeons = ['Deku Tree', 'Dodongos Cavern', 'Jabu Jabus Belly', 'Forest Temple', 'Fire Temple', 'Water Temple', 'Shadow Temple', 'Spirit Temple']
        if (self.settings.dungeon_shortcuts_choice == 'random'):
            self.settings.dungeon_shortcuts = random.sample(dungeons, random.randint(0, len(dungeons)))
            self.randomized_list.append('dungeon_shortcuts')
        elif (self.settings.dungeon_shortcuts_choice == 'all'):
            self.settings.dungeon_shortcuts = dungeons

        # Handle random Rainbow Bridge condition
        if (self.settings.bridge == 'random'
            and ('bridge' not in dist_keys
             or self.distribution.distribution.src_dict['_settings']['bridge'] == 'random')):
            possible_bridge_requirements = ["open", "medallions", "dungeons", "stones", "vanilla"]
            self.settings.bridge = random.choice(possible_bridge_requirements)
            self.set_random_bridge_values()
            self.randomized_list.append('bridge')

        # Determine Ganon Trials
        trial_pool = list(self.skipped_trials)
        dist_chosen = self.distribution.configure_trials(trial_pool)
        dist_num_chosen = len(dist_chosen)

        if self.settings.trials_random and 'trials' not in dist_keys:
            self.settings.trials = dist_num_chosen + random.randint(0, len(trial_pool))
            self.randomized_list.append('trials')
        num_trials = int(self.settings.trials)
        if num_trials < dist_num_chosen:
            raise RuntimeError("%d trials set to active on world %d, but only %d active trials allowed." % (dist_num_chosen, self.id, num_trials))
        chosen_trials = random.sample(trial_pool, num_trials - dist_num_chosen)
        for trial in self.skipped_trials:
            if trial not in chosen_trials and trial not in dist_chosen:
                self.skipped_trials[trial] = True

        # Determine MQ Dungeons
        dungeon_pool = list(self.dungeon_mq)
        dist_num_mq = self.distribution.configure_dungeons(self, dungeon_pool)

        if self.settings.mq_dungeons_mode == 'random' and 'mq_dungeons_count' not in dist_keys:
            for dungeon in dungeon_pool:
                self.dungeon_mq[dungeon] = random.choice([True, False])
            self.randomized_list.append('mq_dungeons_count')
        elif self.settings.mq_dungeons_mode in ['mq', 'vanilla']:
            for dung in self.dungeon_mq.keys():
                self.dungeon_mq[dung] = True if self.settings.mq_dungeons_mode == 'mq' else False
        elif self.settings.mq_dungeons_mode == 'specific':
            for dung in self.settings.mq_dungeons_specific:
                self.dungeon_mq[dung] = True
        else:
            if self.settings.mq_dungeons_count < dist_num_mq:
                raise RuntimeError("%d dungeons are set to MQ on world %d, but only %d MQ dungeons allowed." % (dist_num_mq, self.id, self.settings.mq_dungeons_count))
            mqd_picks = random.sample(dungeon_pool, self.settings.mq_dungeons_count - dist_num_mq)
            for dung in mqd_picks:
                self.dungeon_mq[dung] = True

        self.settings.mq_dungeons_count = list(self.dungeon_mq.values()).count(True)
        self.distribution.configure_randomized_settings(self)


    def load_regions_from_json(self, file_path):
        region_json = read_logic_file(file_path)

        for region in region_json:
            new_region = Region(region['region_name'])
            new_region.world = self
            if 'scene' in region:
                new_region.scene = region['scene']
            if 'hint' in region:
                new_region.hint_name = region['hint']
            if 'dungeon' in region:
                new_region.dungeon = region['dungeon']
            if 'time_passes' in region:
                new_region.time_passes = region['time_passes']
                new_region.provides_time = TimeOfDay.ALL
            if new_region.name == 'Ganons Castle Grounds':
                new_region.provides_time = TimeOfDay.DAMPE
            if 'locations' in region:
                for location, rule in region['locations'].items():
                    new_location = LocationFactory(location)
                    new_location.parent_region = new_region
                    new_location.rule_string = rule
                    if self.settings.logic_rules != 'none':
                        self.parser.parse_spot_rule(new_location)
                    if new_location.never:
                        # We still need to fill the location even if ALR is off.
                        logging.getLogger('').debug('Unreachable location: %s', new_location.name)
                    new_location.world = self
                    new_region.locations.append(new_location)
            if 'events' in region:
                for event, rule in region['events'].items():
                    # Allow duplicate placement of events
                    lname = '%s from %s' % (event, new_region.name)
                    new_location = Location(lname, type='Event', parent=new_region)
                    new_location.rule_string = rule
                    if self.settings.logic_rules != 'none':
                        self.parser.parse_spot_rule(new_location)
                    if new_location.never:
                        logging.getLogger('').debug('Dropping unreachable event: %s', new_location.name)
                    else:
                        new_location.world = self
                        new_region.locations.append(new_location)
                        MakeEventItem(event, new_location)
            if 'exits' in region:
                for exit, rule in region['exits'].items():
                    new_exit = Entrance('%s -> %s' % (new_region.name, exit), new_region)
                    new_exit.connected_region = exit
                    new_exit.rule_string = rule
                    if self.settings.logic_rules != 'none':
                        self.parser.parse_spot_rule(new_exit)
                    if new_exit.never:
                        logging.getLogger('').debug('Dropping unreachable exit: %s', new_exit.name)
                    else:
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
            if self.settings.shopsanity == 'random':
                shop_item_count = random.randint(0,4)
            else:
                shop_item_count = int(self.settings.shopsanity)

            for location in region.locations:
                if location.type == 'Shop':
                    if location.name[-1:] in shop_item_indexes[:shop_item_count]:
                        if self.settings.shopsanity_prices == 'random':
                            self.shop_prices[location.name] = int(random.betavariate(1.5, 2) * 60) * 5
                        elif self.settings.shopsanity_prices == 'random_starting':
                            self.shop_prices[location.name] = random.randrange(0,100,5)
                        elif self.settings.shopsanity_prices == 'random_adult':
                            self.shop_prices[location.name] = random.randrange(0,201,5)
                        elif self.settings.shopsanity_prices == 'random_giant':
                            self.shop_prices[location.name] = random.randrange(0,501,5)
                        elif self.settings.shopsanity_prices == 'random_tycoon':
                            self.shop_prices[location.name] = random.randrange(0,1000,5)
                        elif self.settings.shopsanity_prices == 'affordable':
                            self.shop_prices[location.name] = 10


    def set_scrub_prices(self):
        # Get Deku Scrub Locations
        scrub_locations = [location for location in self.get_locations() if location.type in ['Scrub', 'GrottoScrub']]
        scrub_dictionary = {}
        for location in scrub_locations:
            if location.default not in scrub_dictionary:
                scrub_dictionary[location.default] = []
            scrub_dictionary[location.default].append(location)

        # Loop through each type of scrub.
        for (scrub_item, default_price, text_id, text_replacement) in business_scrubs:
            price = default_price
            if self.settings.shuffle_scrubs == 'low':
                price = 10
            elif self.settings.shuffle_scrubs == 'random':
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

    def set_goals(self):
        # Default goals are divided into 3 primary categories:
        # Bridge, Ganon's Boss Key, and Trials
        # The Triforce Hunt goal is mutually exclusive with
        # these categories given the vastly different playstyle.
        #
        # Goal priorities determine where hintable locations are placed.
        # For example, an item required for both trials and bridge would
        # be hinted only for bridge. This accomplishes two objectives:
        #   1) Locations are not double counted for different stages
        #      of the game
        #   2) Later category location lists are not diluted by early
        #      to mid game locations
        #
        # Entrance locks set restrictions on all goals in a category to
        # ensure unreachable goals are not hintable. This is only used
        # for the Rainbow Bridge to filter out goals hard-locked by
        # Inside Ganon's Castle access.
        #
        # Minimum goals for a category tell the randomizer if the
        # category meta-goal is satisfied by starting items. This
        # is straightforward for dungeon reward goals where X rewards
        # is the same as the minimum goals. For Triforce Hunt, Trials,
        # and Skull conditions, there is only one goal in the category
        # requesting X copies within the goal, so minimum goals has to
        # be 1 for these.
        b = GoalCategory('rainbow_bridge', 10, lock_entrances=['Ganons Castle Grounds -> Ganons Castle Lobby'])
        gbk = GoalCategory('ganon_bosskey', 20)
        trials = GoalCategory('trials', 30, minimum_goals=1)
        th = GoalCategory('triforce_hunt', 30, goal_count=round(self.settings.triforce_goal_per_world / 10), minimum_goals=1)
        trial_goal = Goal(self, 'the Tower', 'path to #the Tower#', 'White', items=[], create_empty=True)

        if self.settings.triforce_hunt and self.settings.triforce_goal_per_world > 0:
            # "Hintable" value of False means the goal items themselves cannot
            # be hinted directly. This is used for Triforce Hunt and Skull
            # conditions to restrict hints to useful items instead of the win
            # condition. Dungeon rewards do not need this restriction as they are
            # already unhintable at a lower level.
            #
            # This restriction does NOT apply to Light Arrows or Ganon's Castle Boss
            # Key, which makes these items directly hintable in their respective goals
            # assuming they do not get hinted by another hint type (always, woth with
            # an earlier order in the hint distro, etc).
            th.add_goal(Goal(self, 'gold', 'path of #gold#', 'Yellow', items=[{'name': 'Triforce Piece', 'quantity': self.settings.triforce_count_per_world, 'minimum': self.settings.triforce_goal_per_world, 'hintable': False}]))
            self.goal_categories[th.name] = th
        # Category goals are defined for each possible setting for each category.
        # Bridge can be Stones, Medallions, Dungeons, Skulls, or Vanilla.
        # Ganon's Boss Key can be Stones, Medallions, Dungeons, Skulls, LACS or
        # one of the keysanity variants.
        # Trials is one goal that is only on if at least one trial is on in the world.
        # If there are no win conditions beyond Kill Ganon (open bridge, GBK removed,
        # no trials), a fallback "path of the hero" clone of WOTH is created. Path
        # wording is used to distinguish the hint type even though the hintable location
        # set is identical to WOTH.
        if not self.settings.triforce_hunt:
            # Bridge goals will always be defined as they have the most immediate priority
            if self.settings.bridge != 'open' and not self.shuffle_special_dungeon_entrances:
                # "Replace" hint text dictionaries are used to reference the
                # dungeon boss holding the specified reward. Only boss names/paths
                # are defined for this feature, and it is not extendable via plando.
                # Goal hint text colors are based on the dungeon reward, not the boss.
                if ((self.settings.bridge_stones > 0 and self.settings.bridge == 'stones') or (self.settings.bridge_rewards > 0 and self.settings.bridge == 'dungeons')):
                    b.add_goal(Goal(self, 'Kokiri Emerald', { 'replace': 'Kokiri Emerald' }, 'Light Blue', items=[{'name': 'Kokiri Emerald', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.add_goal(Goal(self, 'Goron Ruby', { 'replace': 'Goron Ruby' }, 'Light Blue', items=[{'name': 'Goron Ruby', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.add_goal(Goal(self, 'Zora Sapphire', { 'replace': 'Zora Sapphire' }, 'Light Blue', items=[{'name': 'Zora Sapphire', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.minimum_goals = self.settings.bridge_stones if self.settings.bridge == 'stones' else self.settings.bridge_rewards
                if (self.settings.bridge_medallions > 0 and self.settings.bridge == 'medallions') or (self.settings.bridge_rewards > 0 and self.settings.bridge == 'dungeons'):
                    b.add_goal(Goal(self, 'Forest Medallion', { 'replace': 'Forest Medallion' }, 'Green', items=[{'name': 'Forest Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.add_goal(Goal(self, 'Fire Medallion', { 'replace': 'Fire Medallion' }, 'Red', items=[{'name': 'Fire Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.add_goal(Goal(self, 'Water Medallion', { 'replace': 'Water Medallion' }, 'Blue', items=[{'name': 'Water Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.add_goal(Goal(self, 'Shadow Medallion', { 'replace': 'Shadow Medallion' }, 'Pink', items=[{'name': 'Shadow Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.add_goal(Goal(self, 'Spirit Medallion', { 'replace': 'Spirit Medallion' }, 'Yellow', items=[{'name': 'Spirit Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.add_goal(Goal(self, 'Light Medallion', { 'replace': 'Light Medallion' }, 'Light Blue', items=[{'name': 'Light Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.minimum_goals = self.settings.bridge_medallions if self.settings.bridge == 'medallions' else self.settings.bridge_rewards
                if self.settings.bridge == 'vanilla':
                    b.add_goal(Goal(self, 'Shadow Medallion', { 'replace': 'Shadow Medallion' }, 'Pink', items=[{'name': 'Shadow Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    b.add_goal(Goal(self, 'Spirit Medallion', { 'replace': 'Spirit Medallion' }, 'Yellow', items=[{'name': 'Spirit Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                    min_goals = 2
                    # With plentiful item pool, multiple copies of Light Arrows are available,
                    # but both are not guaranteed reachable. Setting a goal quantity of the
                    # item pool value with a minimum quantity of 1 attempts to hint all items
                    # required to get all copies of Light Arrows, but will fall back to just
                    # one copy if the other is unreachable.
                    #
                    # Similar criteria is used for Ganon's Boss Key in plentiful keysanity.
                    if not 'Light Arrows' in self.item_added_hint_types['always']:
                        if self.settings.item_pool_value == 'plentiful':
                            arrows = 2
                        else:
                            arrows = 1
                        b.add_goal(Goal(self, 'Evil\'s Bane', 'path to #Evil\'s Bane#', 'Light Blue', items=[{'name': 'Light Arrows', 'quantity': arrows, 'minimum': 1, 'hintable': True}]))
                        min_goals += 1
                    b.minimum_goals = min_goals
                # Goal count within a category is currently unused. Testing is in progress
                # to potentially use this for weighting certain goals for hint selection.
                b.goal_count = len(b.goals)
                if (self.settings.bridge_tokens > 0
                    and self.settings.bridge == 'tokens'
                    and (self.settings.shuffle_ganon_bosskey != 'tokens'
                            or self.settings.bridge_tokens >= self.settings.ganon_bosskey_tokens)
                    and (self.settings.shuffle_ganon_bosskey != 'on_lacs' or self.settings.lacs_condition != 'tokens'
                            or self.settings.bridge_tokens >= self.settings.lacs_tokens)):
                    b.add_goal(Goal(self, 'Skulls', 'path of #Skulls#', 'Pink', items=[{'name': 'Gold Skulltula Token', 'quantity': 100, 'minimum': self.settings.bridge_tokens, 'hintable': False}]))
                    b.goal_count = round(self.settings.bridge_tokens / 10)
                    b.minimum_goals = 1
                if (self.settings.bridge_hearts > self.settings.starting_hearts
                    and self.settings.bridge == 'hearts'
                    and (self.settings.shuffle_ganon_bosskey != 'hearts'
                            or self.settings.bridge_hearts >= self.settings.ganon_bosskey_hearts)
                    and (self.settings.shuffle_ganon_bosskey != 'on_lacs' or self.settings.lacs_condition != 'hearts'
                            or self.settings.bridge_hearts >= self.settings.lacs_hearts)):
                    b.add_goal(Goal(self, 'hearts', 'path of #hearts#', 'Red', items=[{'name': 'Piece of Heart', 'quantity': (20 - self.settings.starting_hearts) * 4, 'minimum': (self.settings.bridge_hearts - self.settings.starting_hearts) * 4, 'hintable': False}]))
                    b.goal_count = round((self.settings.bridge_hearts - 3) / 2)
                    b.minimum_goals = 1
                self.goal_categories[b.name] = b

            # If the Ganon's Boss Key condition is the same or similar conditions
            # as Bridge, do not create the goals if Bridge goals already cover
            # GBK goals. For example, 3 dungeon GBK would not have its own goals
            # if it is 4 medallion bridge.
            #
            # Even if created, there is no guarantee GBK goals will find new
            # locations to hint. If duplicate goals are defined for Bridge and
            # all of these goals are accessible without Ganon's Castle access,
            # the GBK category is redundant and not used for hint selection.
            if ((self.settings.ganon_bosskey_stones > 0
                    and self.settings.shuffle_ganon_bosskey == 'stones'
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_stones > self.settings.bridge_stones or self.settings.bridge != 'stones'))
                or (self.settings.lacs_stones > 0
                    and self.settings.shuffle_ganon_bosskey == 'on_lacs' and self.settings.lacs_condition == 'stones'
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_stones > self.settings.bridge_stones or self.settings.bridge != 'stones'))
                or (self.settings.ganon_bosskey_rewards > 0
                    and self.settings.shuffle_ganon_bosskey == 'dungeons'
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_rewards > self.settings.bridge_medallions or self.settings.bridge != 'medallions')
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_rewards > self.settings.bridge_stones or self.settings.bridge != 'stones')
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_rewards > self.settings.bridge_rewards or self.settings.bridge != 'dungeons')
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_rewards > 2 or self.settings.bridge != 'vanilla'))
                or (self.settings.lacs_rewards > 0
                    and self.settings.shuffle_ganon_bosskey == 'on_lacs' and self.settings.lacs_condition == 'dungeons'
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_rewards > self.settings.bridge_medallions or self.settings.bridge != 'medallions')
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_rewards > self.settings.bridge_stones or self.settings.bridge != 'stones')
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_rewards > self.settings.bridge_rewards or self.settings.bridge != 'dungeons')
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_rewards > 2 or self.settings.bridge != 'vanilla'))):
                gbk.add_goal(Goal(self, 'Kokiri Emerald', { 'replace': 'Kokiri Emerald' }, 'Yellow', items=[{'name': 'Kokiri Emerald', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.add_goal(Goal(self, 'Goron Ruby', { 'replace': 'Goron Ruby' }, 'Yellow', items=[{'name': 'Goron Ruby', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.add_goal(Goal(self, 'Zora Sapphire', { 'replace': 'Zora Sapphire' }, 'Yellow', items=[{'name': 'Zora Sapphire', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.minimum_goals = (self.settings.ganon_bosskey_stones if self.settings.shuffle_ganon_bosskey == 'stones'
                    else self.settings.lacs_stones if self.settings.shuffle_ganon_bosskey == 'on_lacs' and self.settings.lacs_condition == 'stones'
                    else self.settings.ganon_bosskey_rewards if self.settings.shuffle_ganon_bosskey == 'dungeons'
                    else self.settings.lacs_rewards)
            if ((self.settings.ganon_bosskey_medallions > 0
                    and self.settings.shuffle_ganon_bosskey == 'medallions'
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_medallions > self.settings.bridge_medallions or self.settings.bridge != 'medallions')
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_medallions > 2 or self.settings.bridge != 'vanilla'))
                or (self.settings.lacs_medallions > 0
                    and self.settings.shuffle_ganon_bosskey == 'on_lacs' and self.settings.lacs_condition == 'medallions'
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_medallions > self.settings.bridge_medallions or self.settings.bridge != 'medallions')
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_medallions > 2 or self.settings.bridge != 'vanilla'))
                or (self.settings.ganon_bosskey_rewards > 0
                    and self.settings.shuffle_ganon_bosskey == 'dungeons'
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_rewards > self.settings.bridge_medallions or self.settings.bridge != 'medallions')
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_rewards > self.settings.bridge_stones or self.settings.bridge != 'stones')
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_rewards > self.settings.bridge_rewards or self.settings.bridge != 'dungeons')
                    and (self.shuffle_special_dungeon_entrances or self.settings.ganon_bosskey_rewards > 2 or self.settings.bridge != 'vanilla'))
                or (self.settings.lacs_rewards > 0
                    and self.settings.shuffle_ganon_bosskey == 'on_lacs' and self.settings.lacs_condition == 'dungeons'
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_rewards > self.settings.bridge_medallions or self.settings.bridge != 'medallions')
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_rewards > self.settings.bridge_stones or self.settings.bridge != 'stones')
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_rewards > self.settings.bridge_rewards or self.settings.bridge != 'dungeons')
                    and (self.shuffle_special_dungeon_entrances or self.settings.lacs_rewards > 2 or self.settings.bridge != 'vanilla'))):
                gbk.add_goal(Goal(self, 'Forest Medallion', { 'replace': 'Forest Medallion' }, 'Green', items=[{'name': 'Forest Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.add_goal(Goal(self, 'Fire Medallion', { 'replace': 'Fire Medallion' }, 'Red', items=[{'name': 'Fire Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.add_goal(Goal(self, 'Water Medallion', { 'replace': 'Water Medallion' }, 'Blue', items=[{'name': 'Water Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.add_goal(Goal(self, 'Shadow Medallion', { 'replace': 'Shadow Medallion' }, 'Pink', items=[{'name': 'Shadow Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.add_goal(Goal(self, 'Spirit Medallion', { 'replace': 'Spirit Medallion' }, 'Yellow', items=[{'name': 'Spirit Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.add_goal(Goal(self, 'Light Medallion', { 'replace': 'Light Medallion' }, 'Light Blue', items=[{'name': 'Light Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.minimum_goals = (self.settings.ganon_bosskey_medallions if self.settings.shuffle_ganon_bosskey == 'medallions'
                    else self.settings.lacs_medallions if self.settings.shuffle_ganon_bosskey == 'on_lacs' and self.settings.lacs_condition == 'medallions'
                    else self.settings.ganon_bosskey_rewards if self.settings.shuffle_ganon_bosskey == 'dungeons'
                    else self.settings.lacs_rewards)
            if self.settings.shuffle_ganon_bosskey == 'on_lacs' and self.settings.lacs_condition == 'vanilla':
                gbk.add_goal(Goal(self, 'Shadow Medallion', { 'replace': 'Shadow Medallion' }, 'Pink', items=[{'name': 'Shadow Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.add_goal(Goal(self, 'Spirit Medallion', { 'replace': 'Spirit Medallion' }, 'Yellow', items=[{'name': 'Spirit Medallion', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                gbk.minimum_goals = 2
            gbk.goal_count = len(gbk.goals)
            if (self.settings.ganon_bosskey_tokens > 0
                and self.settings.shuffle_ganon_bosskey == 'tokens'
                and (self.shuffle_special_dungeon_entrances
                        or self.settings.bridge != 'tokens'
                        or self.settings.bridge_tokens < self.settings.ganon_bosskey_tokens)):
                gbk.add_goal(Goal(self, 'Skulls', 'path of #Skulls#', 'Pink', items=[{'name': 'Gold Skulltula Token', 'quantity': 100, 'minimum': self.settings.ganon_bosskey_tokens, 'hintable': False}]))
                gbk.goal_count = round(self.settings.ganon_bosskey_tokens / 10)
                gbk.minimum_goals = 1
            if (self.settings.lacs_tokens > 0
                and self.settings.shuffle_ganon_bosskey == 'on_lacs' and self.settings.lacs_condition == 'tokens'
                and (self.shuffle_special_dungeon_entrances
                        or self.settings.bridge != 'tokens'
                        or self.settings.bridge_tokens < self.settings.lacs_tokens)):
                gbk.add_goal(Goal(self, 'Skulls', 'path of #Skulls#', 'Pink', items=[{'name': 'Gold Skulltula Token', 'quantity': 100, 'minimum': self.settings.lacs_tokens, 'hintable': False}]))
                gbk.goal_count = round(self.settings.lacs_tokens / 10)
                gbk.minimum_goals = 1
            if (self.settings.ganon_bosskey_hearts > self.settings.starting_hearts
                and self.settings.shuffle_ganon_bosskey == 'hearts'
                and (self.settings.bridge != 'hearts'
                        or self.settings.bridge_hearts < self.settings.ganon_bosskey_hearts)):
                gbk.add_goal(Goal(self, 'hearts', 'path of #hearts#', 'Red', items=[{'name': 'Piece of Heart', 'quantity': (20 - self.settings.starting_hearts) * 4, 'minimum': (self.settings.ganon_bosskey_hearts - self.settings.starting_hearts) * 4, 'hintable': False}]))
                gbk.goal_count = round((self.settings.ganon_bosskey_hearts - 3) / 2)
                gbk.minimum_goals = 1
            if (self.settings.lacs_hearts > self.settings.starting_hearts
                and self.settings.shuffle_ganon_bosskey == 'on_lacs' and self.settings.lacs_condition == 'hearts'
                and (self.settings.bridge != 'hearts'
                        or self.settings.bridge_hearts < self.settings.lacs_hearts)):
                gbk.add_goal(Goal(self, 'hearts', 'path of #hearts#', 'Red', items=[{'name': 'Piece of Heart', 'quantity': (20 - self.settings.starting_hearts) * 4, 'minimum': (self.settings.lacs_hearts - self.settings.starting_hearts) * 4, 'hintable': False}]))
                gbk.goal_count = round((self.settings.lacs_hearts - 3) / 2)
                gbk.minimum_goals = 1

            # Ganon's Boss Key shuffled directly in the world will always
            # generate a category/goal pair, though locations are not
            # guaranteed if the higher priority Bridge category contains
            # all required locations for GBK
            if self.settings.shuffle_ganon_bosskey in ['dungeon', 'overworld', 'any_dungeon', 'keysanity']:
                # Make priority even with trials as the goal is no longer centered around dungeon completion or collectibles
                gbk.priority = 30
                gbk.goal_count = 1
                if self.settings.item_pool_value == 'plentiful':
                    keys = 2
                else:
                    keys = 1
                gbk.add_goal(Goal(self, 'the Key', 'path to #the Key#', 'Light Blue', items=[{'name': 'Boss Key (Ganons Castle)', 'quantity': keys, 'minimum': 1, 'hintable': True}]))
                gbk.minimum_goals = 1
            if gbk.goals:
                self.goal_categories[gbk.name] = gbk

            # To avoid too many goals in the hint selection phase,
            # trials are reduced to one goal with six items to obtain.
            if self.skipped_trials['Forest'] == False:
                trial_goal.items.append({'name': 'Forest Trial Clear', 'quantity': 1, 'minimum': 1, 'hintable': True})
                trials.goal_count += 1
            if self.skipped_trials['Fire'] == False:
                trial_goal.items.append({'name': 'Fire Trial Clear', 'quantity': 1, 'minimum': 1, 'hintable': True})
                trials.goal_count += 1
            if self.skipped_trials['Water'] == False:
                trial_goal.items.append({'name': 'Water Trial Clear', 'quantity': 1, 'minimum': 1, 'hintable': True})
                trials.goal_count += 1
            if self.skipped_trials['Shadow'] == False:
                trial_goal.items.append({'name': 'Shadow Trial Clear', 'quantity': 1, 'minimum': 1, 'hintable': True})
                trials.goal_count += 1
            if self.skipped_trials['Spirit'] == False:
                trial_goal.items.append({'name': 'Spirit Trial Clear', 'quantity': 1, 'minimum': 1, 'hintable': True})
                trials.goal_count += 1
            if self.skipped_trials['Light'] == False:
                trial_goal.items.append({'name': 'Light Trial Clear', 'quantity': 1, 'minimum': 1, 'hintable': True})
                trials.goal_count += 1

            # Trials category is finalized and saved only if at least one trial is on
            # If random trials are on and one world in multiworld gets 0 trials, still
            # add the goal to prevent key errors. Since no items fulfill the goal, it
            # will always be invalid for that world and not generate hints.
            if self.settings.trials > 0 or self.settings.trials_random:
                trials.add_goal(trial_goal)
                self.goal_categories[trials.name] = trials

            if (self.shuffle_special_dungeon_entrances or self.settings.bridge == 'open') and (self.settings.shuffle_ganon_bosskey == 'remove' or self.settings.shuffle_ganon_bosskey == 'vanilla') and self.settings.trials == 0:
                g = GoalCategory('ganon', 30, goal_count=1)
                # Equivalent to WOTH, but added in case WOTH hints are disabled in favor of goal hints
                g.add_goal(Goal(self, 'the hero', 'path of #the hero#', 'White', items=[{'name': 'Triforce', 'quantity': 1, 'minimum': 1, 'hintable': True}]))
                g.minimum_goals = 1
                self.goal_categories[g.name] = g

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
        return self.get_restricted_dungeon_items() + self.itempool


    # get a list of items that should stay in their proper dungeon
    def get_restricted_dungeon_items(self):
        itempool = []
        if self.settings.shuffle_mapcompass == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.dungeon_items])
        if self.settings.shuffle_smallkeys == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.small_keys])
        if self.settings.shuffle_bosskeys == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons if dungeon.name != 'Ganons Castle' for item in dungeon.boss_key])
        if self.settings.shuffle_ganon_bosskey == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons if dungeon.name == 'Ganons Castle' for item in dungeon.boss_key])

        for item in itempool:
            item.world = self
        return itempool


    # get a list of items that don't have to be in their proper dungeon
    def get_unrestricted_dungeon_items(self):
        itempool = []
        if self.settings.shuffle_mapcompass in ['any_dungeon', 'overworld', 'keysanity']:
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.dungeon_items])
        if self.settings.shuffle_smallkeys in ['any_dungeon', 'overworld', 'keysanity']:
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.small_keys])
        if self.settings.shuffle_bosskeys in ['any_dungeon', 'overworld', 'keysanity']:
            itempool.extend([item for dungeon in self.dungeons if dungeon.name != 'Ganons Castle' for item in dungeon.boss_key])
        if self.settings.shuffle_ganon_bosskey in ['any_dungeon', 'overworld', 'keysanity']:
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
        return filter(Location.has_no_item, self.get_locations())


    def get_filled_locations(self):
        return filter(Location.has_item, self.get_locations())


    def get_progression_locations(self):
        return filter(Location.has_progression_item, self.get_locations())


    def get_entrances(self):
        return [exit for region in self.regions for exit in region.exits]


    def get_shufflable_entrances(self, type=None, only_primary=False):
        return [entrance for entrance in self.get_entrances() if (type == None or entrance.type == type) and (not only_primary or entrance.primary)]


    def get_shuffled_entrances(self, type=None, only_primary=False):
        return [entrance for entrance in self.get_shufflable_entrances(type=type, only_primary=only_primary) if entrance.shuffled]


    def get_boss_map(self):
        map = dict((boss, boss) for boss in self.boss_location_names)
        if self.settings.shuffle_bosses == 'off':
            return map

        for type in ('ChildBoss', 'AdultBoss'):
            for entrance in self.get_shuffled_entrances(type, True):
                if 'boss' not in entrance.data:
                    continue
                map[entrance.data['boss']] = entrance.replaces.data['boss']
        return map

    def region_has_shortcuts(self, region_name):
        region = self.get_region(region_name)
        dungeon_name = HintArea.at(region).dungeon_name
        return dungeon_name in self.settings.dungeon_shortcuts


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
        excluded_areas = [None, HintArea.ROOT]
        for location in self.get_locations():
            location_hint = HintArea.at(location)

            # We exclude event and locked locations. This means that medallions
            # and stones are not considered here. This is not really an accurate
            # way of doing this, but it's the only way to allow dungeons to appear.
            # So barren hints do not include these dungeon rewards.
            if location_hint in excluded_areas or \
               location.locked or \
               location.name in self.hint_exclusions or \
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
        ]
        if (self.settings.damage_multiplier != 'ohko' and self.settings.damage_multiplier != 'quadruple' and
            self.settings.shuffle_scrubs == 'off' and not self.settings.shuffle_grotto_entrances):
            # nayru's love may be required to prevent forced damage
            exclude_item_list.append('Nayrus Love')
        if self.settings.logic_grottos_without_agony and self.settings.hints != 'agony':
            # Stone of Agony skippable if not used for hints or grottos
            exclude_item_list.append('Stone of Agony')
        if not self.shuffle_special_interior_entrances and not self.settings.shuffle_overworld_entrances and not self.settings.warp_songs:
            # Serenade and Prelude are never required unless one of those settings is enabled
            exclude_item_list.append('Serenade of Water')
            exclude_item_list.append('Prelude of Light')
        if self.settings.logic_rules == 'glitchless':
            # Both two-handed swords can be required in glitch logic, so only consider them foolish in glitchless
            exclude_item_list.append('Biggoron Sword')
            exclude_item_list.append('Giants Knife')
        if self.settings.plant_beans:
            # Magic Beans are useless if beans are already planted
            exclude_item_list.append('Magic Bean')
            exclude_item_list.append('Buy Magic Bean')
            exclude_item_list.append('Magic Bean Pack')
        if not self.settings.blue_fire_arrows:
            # Ice Arrows can only be required when the Blue Fire Arrows setting is enabled
            exclude_item_list.append('Ice Arrows')

        for i in self.item_hint_type_overrides['barren']:
            if i in exclude_item_list:
                exclude_item_list.remove(i)

        for i in self.item_added_hint_types['barren']:
            if not (i in exclude_item_list):
                exclude_item_list.append(i)

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

            if item.name == 'Rutos Letter' and item.name in duplicate_item_woth[world_id]:
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

            if item_name not in self.item_hint_type_overrides['barren']:
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

                if ((not location.item.majoritem) or (location.item.name in exclude_item_list)) and \
                    (location.item.name not in self.item_hint_type_overrides['barren']):
                    # Minor items are always useless in logic
                    continue

                is_bottle = False
                if item.name == 'Rutos Letter' and item.name in duplicate_item_woth[world_id]:
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
                elif item.name == 'Progressive Wallet':
                    dupe_locations = duplicate_item_woth[world_id].get(item.name, [])
                    max_progressive = self.maximum_wallets
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
