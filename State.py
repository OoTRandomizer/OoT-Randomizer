from collections import Counter, defaultdict
import copy


class State(object):

    def __init__(self, parent):
        self.prog_items = Counter()
        self.world = parent
        self.region_cache = {}
        self.location_cache = {}
        self.entrance_cache = {}
        self.recursion_count = 0
        self.collected_locations = {}


    def clear_cached_unreachable(self):
        # we only need to invalidate results which were False, places we could reach before we can still reach after adding more items
        self.region_cache = {k: v for k, v in self.region_cache.items() if v}
        self.location_cache = {k: v for k, v in self.location_cache.items() if v}
        self.entrance_cache = {k: v for k, v in self.entrance_cache.items() if v}


    def copy(self, new_world=None):
        if not new_world:
            new_world = self.world
        new_state = State(new_world)
        new_state.prog_items = copy.copy(self.prog_items)
        new_state.region_cache = copy.copy(self.region_cache)
        new_state.location_cache = copy.copy(self.location_cache)
        new_state.entrance_cache = copy.copy(self.entrance_cache)
        new_state.collected_locations = copy.copy(self.collected_locations)
        return new_state


    def can_reach(self, spot, resolution_hint=None):
        try:
            spot_type = spot.spot_type
            if spot_type == 'Location':
                correct_cache = self.location_cache
            elif spot_type == 'Region':
                correct_cache = self.region_cache
            elif spot_type == 'Entrance':
                correct_cache = self.entrance_cache
            else:
                raise AttributeError
        except AttributeError:
            # try to resolve a name
            if resolution_hint == 'Location':
                spot = self.world.get_location(spot)
                correct_cache = self.location_cache
            elif resolution_hint == 'Entrance':
                spot = self.world.get_entrance(spot)
                correct_cache = self.entrance_cache
            else:
                # default to Region
                spot = self.world.get_region(spot)
                correct_cache = self.region_cache

        if spot.recursion_count > 0:
            return False

        if spot not in correct_cache:
            # for the purpose of evaluating results, recursion is resolved by always denying recursive access (as that ia what we are trying to figure out right now in the first place
            spot.recursion_count += 1
            self.recursion_count += 1
            can_reach = spot.can_reach(self)
            spot.recursion_count -= 1
            self.recursion_count -= 1

            # we only store qualified false results (i.e. ones not inside a hypothetical)
            if not can_reach:
                if self.recursion_count == 0:
                    correct_cache[spot] = can_reach
            else:
                correct_cache[spot] = can_reach
            return can_reach
        return correct_cache[spot]


    def item_name(self, location):
        location = self.world.get_location(location)
        if location.item is None:
            return None
        return location.item.name


    def has(self, item, count=1):
        return self.prog_items[item] >= count


    def item_count(self, item):
        return self.prog_items[item]


    def is_adult(self):
        return self.has('Master Sword')


    def can_child_attack(self):
        return  self.has_slingshot() or \
                self.has('Boomerang') or \
                self.has_sticks() or \
                self.has_explosives() or \
                self.has('Kokiri Sword') or \
                (self.has('Dins Fire') and self.has('Magic Meter'))


    def can_stun_deku(self):
        return  self.is_adult() or \
                self.can_child_attack() or \
                self.has_nuts() or \
                self.has('Buy Deku Shield')


    def has_nuts(self):
        return self.has('Buy Deku Nut (5)') or self.has('Buy Deku Nut (10)') or self.has('Deku Nut Drop')


    def has_sticks(self):
        return self.has('Buy Deku Stick (1)') or self.has('Deku Stick Drop')


    def has_bow(self):
        return self.has('Bow')


    def has_slingshot(self):
        return self.has('Slingshot')


    def has_bombs(self):
        return self.has('Bomb Bag')


    def has_blue_fire(self):
        return self.has_bottle() and \
                (self.can_reach('Ice Cavern')
                or self.can_reach('Ganons Castle Water Trial')
                or self.has('Buy Blue Fire')
                or (self.world.dungeon_mq['Gerudo Training Grounds'] and self.can_reach('Gerudo Training Grounds Stalfos Room')))


    def has_ocarina(self):
        return (self.has('Ocarina') or self.has("Fairy Ocarina") or self.has("Ocarina of Time"))


    def can_play(self, song):
        return self.has_ocarina() and self.has(song)


    def can_use(self, item):
        magic_items = ['Dins Fire', 'Farores Wind', 'Nayrus Love', 'Lens of Truth']
        adult_items = ['Bow', 'Hammer', 'Iron Boots', 'Hover Boots', 'Magic Bean']
        magic_arrows = ['Fire Arrows', 'Light Arrows']
        if item in magic_items:
            return self.has(item) and self.has('Magic Meter')
        elif item in adult_items:
            return self.has(item) and self.is_adult()
        elif item in magic_arrows:
            return self.has(item) and self.is_adult() and self.has_bow() and self.has('Magic Meter')
        elif item == 'Hookshot':
            return self.has('Progressive Hookshot') and self.is_adult()
        elif item == 'Longshot':
            return self.has('Progressive Hookshot', 2) and self.is_adult()
        elif item == 'Silver Gauntlets':
            return self.has('Progressive Strength Upgrade', 2) and self.is_adult()
        elif item == 'Golden Gauntlets':
            return self.has('Progressive Strength Upgrade', 3) and self.is_adult()
        elif item == 'Scarecrow':
            return self.has('Progressive Hookshot') and self.is_adult() and self.has_ocarina()
        elif item == 'Distant Scarecrow':
            return self.has('Progressive Hookshot', 2) and self.is_adult() and self.has_ocarina()
        else:
            return self.has(item)


    def can_buy_bombchus(self):
        return self.has('Buy Bombchu (5)') or \
               self.has('Buy Bombchu (10)') or \
               self.has('Buy Bombchu (20)') or \
               self.can_reach('Castle Town Bombchu Bowling') or \
               self.can_reach('Haunted Wasteland Bombchu Salesman', 'Location')


    def has_bombchus(self):
        return (self.world.bombchus_in_logic and \
                    (any(pritem.startswith('Bombchus') for pritem in self.prog_items) and \
                        self.can_buy_bombchus())) \
            or (not self.world.bombchus_in_logic and self.has('Bomb Bag') and \
                        self.can_buy_bombchus())


    def has_bombchus_item(self):
        return (self.world.bombchus_in_logic and \
                (any(pritem.startswith('Bombchus') for pritem in self.prog_items) \
                or (self.has('Progressive Wallet') and self.can_reach('Haunted Wasteland')))) \
            or (not self.world.bombchus_in_logic and self.has('Bomb Bag'))


    def has_explosives(self):
        return self.has_bombs() or self.has_bombchus()


    def can_blast_or_smash(self):
        return self.has_explosives() or (self.is_adult() and self.has('Hammer'))


    def can_dive(self):
        return self.has('Progressive Scale')


    def can_see_with_lens(self):
        return ((self.has('Magic Meter') and self.has('Lens of Truth')) or self.world.logic_lens != 'all')


    def has_projectile(self, age='either'):
        if age == 'child':
            return self.has_explosives() or self.has_slingshot() or self.has('Boomerang')
        elif age == 'adult':
            return self.has_explosives() or self.has_bow() or self.has('Progressive Hookshot')
        elif age == 'both':
            return self.has_explosives() or ((self.has_bow() or self.has('Progressive Hookshot')) and (self.has_slingshot() or self.has('Boomerang')))
        else:
            return self.has_explosives() or ((self.has_bow() or self.has('Progressive Hookshot')) or (self.has_slingshot() or self.has('Boomerang')))


    def has_GoronTunic(self):
        return (self.has('Goron Tunic') or self.has('Buy Goron Tunic'))


    def has_ZoraTunic(self):
        return (self.has('Zora Tunic') or self.has('Buy Zora Tunic'))


    def can_leave_forest(self):
        return self.world.open_forest or self.can_reach(self.world.get_location('Queen Gohma'))


    def can_finish_adult_trades(self):
        zora_thawed = (self.can_play('Zeldas Lullaby') or (self.has('Hover Boots') and self.world.logic_zora_with_hovers)) and self.has_blue_fire()
        carpenter_access = self.has('Epona') or self.has('Progressive Hookshot', 2)
        return (self.has('Claim Check') or ((self.has('Progressive Strength Upgrade') or self.can_blast_or_smash() or self.has_bow()) and (((self.has('Eyedrops') or self.has('Eyeball Frog') or self.has('Prescription') or self.has('Broken Sword')) and zora_thawed) or ((self.has('Poachers Saw') or self.has('Odd Mushroom') or self.has('Cojiro') or self.has('Pocket Cucco') or self.has('Pocket Egg')) and zora_thawed and carpenter_access))))


    def has_bottle(self):
        is_normal_bottle = lambda item: (item.startswith('Bottle') and item != 'Bottle with Letter' and (item != 'Bottle with Big Poe' or self.is_adult()))
        return any(is_normal_bottle(pritem) for pritem in self.prog_items)


    def bottle_count(self):
        return sum([pritem for pritem in self.prog_items if pritem.startswith('Bottle') and pritem != 'Bottle with Letter' and (pritem != 'Bottle with Big Poe' or self.is_adult())])


    def has_hearts(self, count):
        # Warning: This only considers items that are marked as advancement items
        return self.heart_count() >= count


    def heart_count(self):
        # Warning: This only considers items that are marked as advancement items
        return (
            self.item_count('Heart Container')
            + self.item_count('Piece of Heart') // 4
            + 3 # starting hearts
        )


    def has_fire_source(self):
        return self.can_use('Dins Fire') or self.can_use('Fire Arrows')


    def guarantee_hint(self):
        if(self.world.hints == 'mask'):
            # has the mask of truth
            return self.has('Zeldas Letter') and self.can_play('Sarias Song') and self.has('Kokiri Emerald') and self.has('Goron Ruby') and self.has('Zora Sapphire')
        elif(self.world.hints == 'agony'):
            # has the Stone of Agony
            return self.has('Stone of Agony')
        return True


    def nighttime(self):
        if self.world.logic_no_night_tokens_without_suns_song:
            return self.can_play('Suns Song')
        return True


    def had_night_start(self):
        stod = self.world.starting_tod
        # These are all between 6:30 and 18:00
        if (stod == 'evening' or        # 18
            stod == 'dusk' or           # 21
            stod == 'midnight' or       # 00
            stod == 'witching-hour' or  # 03
            stod == 'early-morning'):   # 06
            return True
        else:
            return False


    def can_finish_GerudoFortress(self):
        if self.world.gerudo_fortress == 'normal':
            return self.has('Small Key (Gerudo Fortress)', 4) and (self.can_use('Bow') or self.can_use('Hookshot') or self.can_use('Hover Boots') or self.world.logic_gerudo_kitchen)
        elif self.world.gerudo_fortress == 'fast':
            return self.has('Small Key (Gerudo Fortress)', 1) and self.is_adult()
        else:
            return self.is_adult()


    # Be careful using this function. It will not collect any
    # items that may be locked behind the item, only the item itself.
    def collect(self, item):
        if item.advancement:
            self.prog_items[item.name] += 1
            self.clear_cached_unreachable()


    # Be careful using this function. It will not uncollect any
    # items that may be locked behind the item, only the item itself.
    def remove(self, item):
        if self.prog_items[item.name] > 0:
            self.prog_items[item.name] -= 1
            if self.prog_items[item.name] <= 0:
                del self.prog_items[item.name]

            # invalidate collected cache. unreachable locations are still unreachable
            self.region_cache =   {k: v for k, v in self.region_cache.items() if not v}
            self.location_cache = {k: v for k, v in self.location_cache.items() if not v}
            self.entrance_cache = {k: v for k, v in self.entrance_cache.items() if not v}
            self.recursion_count = 0


    def __getstate__(self):
        return self.__dict__.copy()


    def __setstate__(self, state):
        self.__dict__.update(state)


    def __getattr__(self, item):
        if item.startswith('can_reach_'):
            return self.can_reach(item[10])
        elif item.startswith('has_'):
            return self.has(item[4])

        raise RuntimeError('Cannot parse %s.' % item)


    # This function returns a list of states that is each of the base_states
    # with every item still in the itempool. It only adds items that belong
    # to its respective world. See fill_restrictive
    @staticmethod
    def get_states_with_items(base_state_list, itempool):
        new_state_list = []
        for base_state in base_state_list:
            new_state = base_state.copy()
            for item in itempool:
                if item.world.id == base_state.world.id: # Check world
                    new_state.collect(item)
            new_state_list.append(new_state)
        State.collect_locations(new_state_list)
        return new_state_list


    # This collected all item locations available in the state list given that
    # the states have collected items. The purpose is that it will search for
    # all new items that become accessible with a new item set
    @staticmethod
    def collect_locations(state_list):
        # Get all item locations in the worlds
        item_locations = [location for state in state_list for location in state.world.get_filled_locations() if location.item.advancement]

        # will loop if there is more items opened up in the previous iteration. Always run once
        reachable_items_locations = True
        while reachable_items_locations:
            # get reachable new items locations
            reachable_items_locations = [location for location in item_locations if location.name not in state_list[location.world.id].collected_locations and state_list[location.world.id].can_reach(location)]
            for location in reachable_items_locations:
                # Mark the location collected in the state world it exists in
                state_list[location.world.id].collected_locations[location.name] = True
                # Collect the item for the state world it is for
                state_list[location.item.world.id].collect(location.item)


    # This returns True is every state is beatable. It's important to ensure
    # all states beatable since items required in one world can be in another.
    @staticmethod
    def can_beat_game(state_list, scan_for_items=True):
        if scan_for_items:
            # Check if already beaten
            game_beaten = True
            for state in state_list:
                if not state.has('Triforce'):
                    game_beaten = False
                    break
            if game_beaten:
                return True

            # collect all available items
            new_state_list = [state.copy() for state in state_list]
            State.collect_locations(new_state_list)
        else:
            new_state_list = state_list

        # if the every state got the Triforce, then return True
        for state in new_state_list:
            if not state.has('Triforce'):
                return False
        return True


    @staticmethod
    def update_required_items(spoiler):
        worlds = spoiler.worlds
        state_list = [world.state for world in worlds]

        # get list of all of the progressive items that can appear in hints
        all_locations = [location for world in worlds for location in world.get_filled_locations()]
        item_locations = [location for location in all_locations if location.item.majoritem and not location.locked]

        # if the playthrough was generated, filter the list of locations to the
        # locations in the playthrough. The required locations is a subset of these
        # locations. Can't use the locations directly since they are location to the
        # copied spoiler world, so must try to find the matching locations by name
        if spoiler.playthrough:
            spoiler_locations = defaultdict(lambda: [])
            for location in [location for _,sphere in spoiler.playthrough.items() for location in sphere]:
                spoiler_locations[location.name].append(location.world.id)
            item_locations = list(filter(lambda location: location.world.id in spoiler_locations[location.name], item_locations))

        required_locations = []
        reachable_items_locations = True
        while (item_locations and reachable_items_locations):
            reachable_items_locations = [location for location in all_locations if location.name not in state_list[location.world.id].collected_locations and state_list[location.world.id].can_reach(location)]
            for location in reachable_items_locations:
                # Try to remove items one at a time and see if the game is still beatable
                if location in item_locations:
                    old_item = location.item
                    location.item = None
                    if not State.can_beat_game(state_list):
                        required_locations.append(location)
                    location.item = old_item
                    item_locations.remove(location)
                state_list[location.world.id].collected_locations[location.name] = True
                state_list[location.item.world.id].collect(location.item)

        # Filter the required location to only include location in the world
        required_locations_dict = {}
        for world in worlds:
            required_locations_dict[world.id] = list(filter(lambda location: location.world.id == world.id, required_locations))
        spoiler.required_locations = required_locations_dict

