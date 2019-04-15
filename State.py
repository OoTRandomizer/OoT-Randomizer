from collections import Counter, defaultdict
import copy
import itertools

from Item import ItemInfo
from Playthrough import Playthrough
from Region import Region



class State(object):

    def __init__(self, parent):
        self.prog_items = Counter()
        self.world = parent
        self.region_cache = { 'child': {}, 'adult': {} }
        self.recursion_count = { 'child': 0, 'adult': 0 }
        self.current_spot = None
        self.adult = None
        self.tod = None
        self.playthrough = None


    ## Ensure that this will always have a value
    @property
    def is_glitched(self):
        return self.world.logic_rules != 'glitchless'


    def clear_cached_unreachable(self):
        # we only need to invalidate results which were False, places we could reach before we can still reach after adding more items
        for cache_type in self.region_cache:
            self.region_cache[cache_type] = {k: v for k, v in self.region_cache[cache_type].items() if v}


    def clear_cache(self):
        self.region_cache = { 'child': {}, 'adult': {} }


    def copy(self, new_world=None):
        if not new_world:
            new_world = self.world
        new_state = State(new_world)
        new_state.prog_items = copy.copy(self.prog_items)
        new_state.region_cache = {k: copy.copy(v) for k,v in self.region_cache.items()}
        return new_state


    def get_spot(self, spot, resolution_hint='Region'):
        if isinstance(spot, str):
            # try to resolve a name
            if resolution_hint == 'Location':
                return self.world.get_location(spot)
            elif resolution_hint == 'Entrance':
                return self.world.get_entrance(spot)
            elif resolution_hint == 'Region':
                return self.world.get_region(spot)
            else:
                raise AttributeError('Unknown resolution hint type: ' + str(resolution_hint))
        else:
            return spot


    def can_reach(self, spot=None, resolution_hint='Region', age=None, tod=None):
        if spot == None:
            # Default to the current spot's parent region, to allow can_reach to be used without arguments inside access rules
            spot = self.current_spot.parent_region
        else:
            spot = self.get_spot(spot, resolution_hint)

        if tod == 'all':
            return self.can_reach(spot, age=age, tod='day') and self.can_reach(spot, age=age, tod='night')
        elif tod != None:
            return self.with_tod(lambda state: state.can_reach(spot, age=age), tod)

        if age == None:
            # If the age parameter is missing, the current age should be used, but if it's not defined either, we default to age='either'
            if self.adult == None:
                return self.as_either(lambda state: state.can_reach(spot))
        elif age == 'either':
            return self.as_either(lambda state: state.can_reach(spot))
        elif age == 'both':
           return self.as_both(lambda state: state.can_reach(spot))
        elif age == 'adult':
            return self.as_adult(lambda state: state.can_reach(spot))
        elif age == 'child':
            return self.as_child(lambda state: state.can_reach(spot))
        else:
            raise AttributeError('Unknown age parameter type: ' + str(age))

        if not isinstance(spot, Region):
            return spot.can_reach(self)

        # If we are currently checking for reachability with a specific time of day and the time can be changed here,
        # we want to continue the reachability test without a time of day, to make sure we could actually get there
        if self.tod != None and self.can_change_time(spot):
            return self.with_tod(lambda state: state.can_reach(spot), None)

        # If we reached this point, it means the current age should be used
        if self.adult:
            age_type = 'adult'
        else:
            age_type = 'child'

        if spot.recursion_count[age_type] > 0:
            return False

        if self.tod == None and self.playthrough != None:
            if self.playthrough.can_reach(spot, age=age_type):
                return True

        # The normal cache can't be used while checking for reachability with a specific time of day
        if self.tod == None and spot in self.region_cache[age_type]:
            return self.region_cache[age_type][spot]

        # for the purpose of evaluating results, recursion is resolved by always denying recursive access (as that is what we are trying to figure out right now in the first place
        spot.recursion_count[age_type] += 1
        self.recursion_count[age_type] += 1

        can_reach = spot.can_reach(self)

        spot.recursion_count[age_type] -= 1
        self.recursion_count[age_type] -= 1

        # we store true results and qualified false results (i.e. ones not inside a hypothetical)
        if can_reach or self.recursion_count[age_type] == 0:
            self.region_cache[age_type][spot] = can_reach

        return can_reach


    def as_either(self, lambda_rule):
        return self.as_adult(lambda_rule) or self.as_child(lambda_rule)


    def as_both(self, lambda_rule):
        return self.as_adult(lambda_rule) and self.as_child(lambda_rule)


    def as_adult(self, lambda_rule):
        return self.can_become_adult() and self.with_age(lambda_rule, 'adult')


    def as_child(self, lambda_rule):
        return self.can_become_child() and self.with_age(lambda_rule, 'child')


    def with_age(self, lambda_rule, age):
        # It's important to set the age property back to what it was originally after executing the rule here
        original_adult = self.adult
        self.adult = (age == 'adult')
        lambda_rule_result = lambda_rule(self)
        self.adult = original_adult
        return lambda_rule_result


    def with_spot(self, lambda_rule, spot):
        # It's important to set the spot property back to what it was originally after executing the rule here
        original_spot = self.current_spot
        self.current_spot = spot
        lambda_rule_result = lambda_rule(self)
        self.current_spot = original_spot
        return lambda_rule_result


    def as_either_here(self, lambda_rule=lambda state: True):
        return self.as_either(self.add_reachability(lambda_rule))


    def as_both_here(self, lambda_rule=lambda state: True):
        return self.as_both(self.add_reachability(lambda_rule))


    def as_adult_here(self, lambda_rule=lambda state: True):
        return self.as_adult(self.add_reachability(lambda_rule))


    def as_child_here(self, lambda_rule=lambda state: True):
        return self.as_child(self.add_reachability(lambda_rule))


    def add_reachability(self, lambda_rule):
        return lambda state: state.can_reach() and lambda_rule(state)


    def at_day(self):
        return self.at_tod('day')


    def at_night(self):
        return self.at_tod('night')


    def at_tod(self, tod):
        if self.tod == None:
            return self.with_tod(lambda state: state.can_reach(), tod)
        else:
            return self.tod == tod


    def with_tod(self, lambda_rule, tod):
        # It's important to set the tod property back to what it was originally after executing the rule here
        original_tod = self.tod
        self.tod = tod
        lambda_rule_result = lambda_rule(self)
        self.tod = original_tod
        return lambda_rule_result


    def can_change_time(self, region):
        # For now we assume that Sun's Song can be used to change time anywhere,
        # and that all time of day states used in logic can be reached by playing Sun's Song
        return region.time_passes or self.can_play('Suns Song')


    def item_name(self, location):
        location = self.world.get_location(location)
        if location.item is None:
            return None
        return location.item.name


    def has(self, item, count=1):
        return self.prog_items[item] >= count


    def has_any(self, predicate):
        return any(map(predicate, self.prog_items))

    def has_any_of(self, items):
        return any(map(self.prog_items.__contains__, items))

    def has_all_of(self, items):
        return all(map(self.prog_items.__contains__, items))


    def item_count(self, item):
        return self.prog_items[item]


    def can_become_adult(self):
        return self.world.starting_age == 'adult' or self.has('Time Travel')


    def can_become_child(self):
        return self.world.starting_age == 'child' or self.has('Time Travel')


    def is_adult(self):
        return self.adult


    def is_child(self):
        return not self.adult


    def is_starting_age(self):
        return self.adult == (self.world.starting_age == 'adult')


    def can_child_attack(self):
        return  self.is_child() and \
                   (self.has_slingshot() or \
                    self.has('Boomerang') or \
                    self.has_sticks() or \
                    self.has_explosives() or \
                    self.has('Kokiri Sword') or \
                    self.can_use('Dins Fire'))

    def can_child_damage(self):
        return  self.is_child() and \
                   (self.has_slingshot() or \
                    self.has_sticks() or \
                    self.has_explosives() or \
                    self.has('Kokiri Sword') or \
                    self.can_use('Dins Fire'))


    def can_stun_deku(self):
        return  self.is_adult() or \
                self.can_child_attack() or \
                self.has_nuts() or \
                self.can_use('Deku Shield')


    def has_nuts(self):
        return self.has_any_of(['Buy Deku Nut (5)', 'Buy Deku Nut (10)', 'Deku Nut Drop'])


    def has_sticks(self):
        return self.has_any_of(['Buy Deku Stick (1)', 'Deku Stick Drop'])


    def has_bow(self):
        return self.has('Bow')


    def has_slingshot(self):
        return self.has('Slingshot')


    def has_bombs(self):
        return self.has('Bomb Bag')


    def has_blue_fire(self):
        return self.has_any_of(['Buy Blue Fire', 'Blue Fire Drop'])


    def has_ocarina(self):
        return self.has_any_of(['Ocarina', 'Fairy Ocarina', 'Ocarina of Time'])


    def can_play(self, song):
        return self.has_ocarina() and self.has(song)


    def can_use(self, item):
        magic_items = ['Dins Fire', 'Farores Wind', 'Nayrus Love', 'Lens of Truth']
        adult_items = ['Bow', 'Hammer', 'Iron Boots', 'Hover Boots', 'Epona']
        adult_buy_or_find = ['Goron Tunic', 'Zora Tunic']
        child_items = ['Slingshot', 'Boomerang', 'Kokiri Sword']
        magic_arrows = ['Fire Arrows', 'Light Arrows']
        if item in magic_items:
            return self.has(item) and self.has('Magic Meter')
        elif item in child_items:
            return self.has(item) and self.is_child()
        elif item in adult_buy_or_find:
            return (self.has(item) or self.has('Buy ' + item)) and self.is_adult()
        elif item in adult_items:
            return self.has(item) and self.is_adult()
        elif item in magic_arrows:
            return self.has(item) and self.is_adult() and self.has_bow() and self.has('Magic Meter')
        elif item == 'Sticks':
            return self.has_sticks() and self.is_child()
        elif item == 'Deku Shield':
            return self.has('Buy Deku Shield') and self.is_child()
        elif item == 'Hookshot':
            return self.has('Progressive Hookshot') and self.is_adult()
        elif item == 'Longshot':
            return self.has('Progressive Hookshot', 2) and self.is_adult()
        elif item == 'Silver Gauntlets':
            return self.has('Progressive Strength Upgrade', 2) and self.is_adult()
        elif item == 'Golden Gauntlets':
            return self.has('Progressive Strength Upgrade', 3) and self.is_adult()
        elif item == 'Scarecrow':
            return self.has('Progressive Hookshot') and self.is_adult() and self.can_play('Scarecrow Song')
        elif item == 'Distant Scarecrow':
            return self.has('Progressive Hookshot', 2) and self.is_adult() and self.can_play('Scarecrow Song')
        elif item == 'Magic Bean':
            # Magic Bean usability automatically checks for reachability as child to the current spot's parent region (with as_child_here)
            return self.as_child_here(lambda state: state.has('Magic Bean')) and self.is_adult()
        else:
            return self.has(item)


    def can_buy_bombchus(self):
        return self.has_any_of(['Buy Bombchu (5)', 'Buy Bombchu (10)', 'Buy Bombchu (20)', 'More Bombchus'])


    def has_bombchus(self):
        if self.can_buy_bombchus():
            if self.world.bombchus_in_logic:
                return self.has_any_of(['Bombchus', 'Bombchus (5)', 'Bombchus (10)', 'Bombchus (20)', 'More Bombchus'])
            else:
                return self.has('Bomb Bag')
        else:
            return False


    def has_bombchus_item(self):
        if self.world.bombchus_in_logic:
            return self.has_any(lambda pritem: pritem.startswith('Bombchus'))
        else:
            return self.has('Bomb Bag')


    def has_explosives(self):
        return self.has_bombs() or self.has_bombchus()


    def can_blast_or_smash(self):
        return self.has_explosives() or self.can_use('Hammer')


    def can_dive(self):
        return self.has('Progressive Scale')


    def can_see_with_lens(self):
        return ((self.has('Magic Meter') and self.has('Lens of Truth')) or self.world.logic_lens != 'all')


    def can_plant_bugs(self):
        return self.is_child() and self.has_bugs()


    def has_bugs(self):
        return self.has_bottle() and \
            (self.can_leave_forest() or self.has_sticks() or self.has('Kokiri Sword') or
             self.has('Boomerang') or self.has_explosives() or self.has('Buy Bottle Bug'))


    def can_use_projectile(self):
        return self.has_explosives() or \
               (self.is_adult() and (self.has_bow() or self.has('Progressive Hookshot'))) or \
               (self.is_child() and (self.has_slingshot() or self.has('Boomerang')))


    def has_projectile(self, age='either'):
        if self.has_explosives():
            return True
        if age == 'child':
            return self.has_slingshot() or self.has('Boomerang')
        elif age == 'adult':
            return self.has_bow() or self.has('Progressive Hookshot')
        elif age == 'both':
            return ((self.has_bow() or self.has('Progressive Hookshot'))
                    and (self.has_slingshot() or self.has('Boomerang')))
        else:
            return ((self.has_bow() or self.has('Progressive Hookshot'))
                    or (self.has_slingshot() or self.has('Boomerang')))


    def can_leave_forest(self):
        return self.world.open_forest or self.is_adult() or self.is_glitched or self.can_reach(self.world.get_location('Queen Gohma'), age='either')


    def can_finish_adult_trades(self):
        if self.is_glitched:
            zora_thawed = self.can_reach('Zoras Domain', age='adult')
            carpenter_access = self.can_reach('Gerudo Valley Far Side', age='adult')
            has_low_trade = (self.has('Poachers Saw') or self.has('Odd Mushroom') or self.has('Cojiro') or self.has('Pocket Cucco') or self.has('Pocket Egg'))
            has_high_trade = (self.has('Eyedrops') or self.has('Eyeball Frog') or self.has('Prescription') or self.has('Broken Sword'))
            return self.can_reach('Death Mountain Crater Upper', age='adult') and (
                self.has('Claim Check')
                or (zora_thawed and (has_high_trade or (has_low_trade and carpenter_access))))
        else:
            zora_thawed = self.can_reach('Zoras Domain', age='adult') and self.has_blue_fire()
            pocket_egg = self.has('Pocket Egg')
            pocket_cucco = self.has('Pocket Cucco') or pocket_egg
            cojiro = self.has('Cojiro') or (pocket_cucco and self.can_reach('Carpenter Boss House', age='adult'))
            odd_mushroom = self.has('Odd Mushroom') or cojiro
            odd_poultice = odd_mushroom and self.can_reach('Odd Medicine Building', age='adult')
            poachers_saw = self.has('Poachers Saw') or odd_poultice
            broken_sword = self.has('Broken Sword') or (poachers_saw and self.can_reach('Gerudo Valley Far Side', age='adult'))
            prescription = self.has('Prescription') or broken_sword
            eyeball_frog = (self.has('Eyeball Frog') or prescription) and zora_thawed
            eyedrops = (self.has('Eyedrops') or eyeball_frog) and self.can_reach('Lake Hylia Lab', age='adult') and zora_thawed
            return (self.has('Claim Check')
                    or (eyedrops and
                        (self.world.shuffle_interior_entrances
                            or self.has('Progressive Strength Upgrade')
                            or self.can_blast_or_smash()
                            or self.has_bow()
                            or self.world.logic_biggoron_bolero)))


    def has_skull_mask(self):
        return self.has('Zeldas Letter') and self.can_reach('Castle Town Mask Shop')


    def has_mask_of_truth(self):
        # Must befriend Skull Kid to sell Skull Mask, all stones to spawn running man.
        return self.has_skull_mask() and self.can_play('Sarias Song') and self.has_all_of(['Kokiri Emerald', 'Goron Ruby', 'Zora Sapphire'])


    def has_bottle(self):
        # Extra Ruto's Letter are automatically emptied
        return self.has_any(ItemInfo.isBottle) or self.has('Bottle with Letter', 2)


    def bottle_count(self):
        # Extra Ruto's Letter are automatically emptied
        return sum(filter(ItemInfo.isBottle, self.prog_items)) + max(self.prog_items['Bottle with Letter'] - 1, 0)


    def has_hearts(self, count):
        # Warning: This only considers items that are marked as advancement items
        return self.heart_count() >= count


    def has_shield(self):
        #The mirror shield does not count as it cannot reflect deku scrub attack
        return ((self.is_adult() and self.has('Buy Hylian Shield')) or
                (self.is_child() and self.has('Buy Deku Shield')))


    def heart_count(self):
        # Warning: This only considers items that are marked as advancement items
        return (
            self.item_count('Heart Container')
            + self.item_count('Piece of Heart') // 4
            + 3 # starting hearts
        )


    def has_fire_source(self):
        return self.can_use('Dins Fire') or self.can_use('Fire Arrows')


    def has_fire_source_with_torch(self):
        return self.has_fire_source() or (self.is_child() and self.has_sticks())


    def guarantee_hint(self):
        if self.world.hints == 'mask':
            # has the mask of truth
            return self.has_mask_of_truth()
        elif self.world.hints == 'agony':
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
            return (self.has('Small Key (Gerudo Fortress)', 4) and
                    (self.can_use('Bow')
                        or self.can_use('Hookshot')
                        or self.can_use('Hover Boots')
                        or self.world.logic_gerudo_kitchen
                        or self.is_glitched))
        elif self.world.gerudo_fortress == 'fast':
            return (self.has('Small Key (Gerudo Fortress)', 1) and
                    (self.is_adult() or self.is_glitched))
        else:
            return self.is_adult() or self.is_glitched


    def can_shield(self):
        return ((self.is_adult() and (self.has('Buy Hylian Shield') or self.has('Mirror Shield')))
                or (self.is_child() and self.has('Buy Deku Shield')))


    def can_mega(self):
        return self.has_explosives() and self.can_shield()


    def can_isg(self):
        return self.can_shield() and (self.is_adult() or self.has_sticks() or self.has('Kokiri Sword'))


    def can_hover(self):
        return self.can_mega() and self.can_isg()


    def can_weirdshot(self):
        return self.can_mega() and self.can_use('Hookshot')


    def can_jumpslash(self):
        return self.is_adult() or (self.is_child() and (self.has_sticks or self.has('Kokiri Sword')))


    # Used for fall damage and other situations where damage is unavoidable
    def can_live_dmg(self, hearts):
        mult = self.world.damage_multiplier
        if hearts*4 >= 3:
            return mult != 'ohko' and mult != 'quadruple'
        elif hearts*4 < 3:
            return mult != 'ohko'
        else:
            return True


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

            # invalidate collected cache. unreachable regions are still unreachable
            for cache_type in self.region_cache:
                self.region_cache[cache_type] = {k: v for k, v in self.region_cache[cache_type].items() if not v}

            self.recursion_count = {k: 0 for k in self.recursion_count}


    def __getstate__(self):
        return self.__dict__.copy()


    def __setstate__(self, state):
        self.__dict__.update(state)


    @staticmethod
    def can_beat_game(state_list, scan_for_items=True):
        return Playthrough(state_list).can_beat_game(scan_for_items)


    @staticmethod
    def update_required_items(spoiler):
        worlds = spoiler.worlds
        state_list = [world.state for world in worlds]

        # get list of all of the progressive items that can appear in hints
        # all_locations: all progressive items. have to collect from these
        # item_locations: only the ones that should appear as "required"/WotH
        all_locations = [location for world in worlds for location in world.get_filled_locations()]
        # Set to test inclusion against
        item_locations = {location for location in all_locations if location.item.majoritem and not location.locked}

        # if the playthrough was generated, filter the list of locations to the
        # locations in the playthrough. The required locations is a subset of these
        # locations. Can't use the locations directly since they are location to the
        # copied spoiler world, so must compare via name and world id
        if spoiler.playthrough:
            translate = lambda loc: worlds[loc.world.id].get_location(loc.name)
            spoiler_locations = set(map(translate, itertools.chain.from_iterable(spoiler.playthrough.values())))
            item_locations &= spoiler_locations

        required_locations = []

        playthrough = Playthrough(state_list)
        for location in playthrough.iter_reachable_locations(all_locations):
            # Try to remove items one at a time and see if the game is still beatable
            if location in item_locations:
                old_item = location.item
                location.item = None
                # copies state! This is very important as we're in the middle of a playthrough
                # already, but beneficially, has playthrough it can start from
                if not playthrough.can_beat_game():
                    required_locations.append(location)
                location.item = old_item
            state_list[location.item.world.id].collect(location.item)

        # Filter the required location to only include location in the world
        required_locations_dict = {}
        for world in worlds:
            required_locations_dict[world.id] = list(filter(lambda location: location.world.id == world.id, required_locations))
        spoiler.required_locations = required_locations_dict
