from collections import Counter
import copy
import logging

from Item import ItemInfo
from RulesCommon import escape_name

Triforce_Piece = ItemInfo.solver_ids['Triforce_Piece']
Triforce = ItemInfo.solver_ids['Triforce']
Rutos_Letter = ItemInfo.solver_ids['Rutos_Letter']
Piece_of_Heart = ItemInfo.solver_ids['Piece_of_Heart']

class State(object):

    def __init__(self, parent):
        self.solv_items = [0] * len(ItemInfo.solver_ids)
        self.world = parent
        self.search = None
        self._won = self.won_triforce_hunt if self.world.settings.triforce_hunt else self.won_normal


    def copy(self, new_world=None):
        if not new_world:
            new_world = self.world
        new_state = State(new_world)
        for i, val in enumerate(self.solv_items):
            new_state.solv_items[i] = val
        return new_state


    def item_name(self, location):
        location = self.world.get_location(location)
        if location.item is None:
            return None
        return location.item.name


    def won(self):
        return self._won()


    def won_triforce_hunt(self):
        return self.has(Triforce_Piece, self.world.settings.triforce_goal_per_world)


    def won_normal(self):
        return self.has(Triforce)


    def has(self, item, count=1):
        return self.solv_items[item] >= count


    def has_any_of(self, items):
        for i in items:
            if self.solv_items[i]: return True
        return False


    def has_all_of(self, items):
        for i in items:
            if not self.solv_items[i]: return False
        return True


    def count_of(self, items):
        s = 0
        for i in items:
            s += self.solv_items[i]
        return s


    def item_count(self, item):
        return self.solv_items[item]


    def item_name_count(self, name):
        return self.solv_items[ItemInfo.solver_ids[escape_name(name)]]


    def has_bottle(self, **kwargs):
        # Extra Ruto's Letter are automatically emptied
        return self.has_any_of(ItemInfo.bottle_ids) or self.has(Rutos_Letter, 2)


    def has_hearts(self, count):
        # Warning: This is limited by World.max_progressions so it currently only works if hearts are required for LACS, bridge, or Ganon bk
        return self.heart_count() >= count


    def heart_count(self):
        # Warning: This is limited by World.max_progressions so it currently only works if hearts are required for LACS, bridge, or Ganon bk
        return (
            self.item_count(Piece_of_Heart) // 4 # aliases ensure Heart Container and Piece of Heart (Treasure Chest Game) are included in this
            + 3 # starting hearts
        )

    def has_medallions(self, count):
        return self.count_of(ItemInfo.medallion_ids) >= count


    def has_stones(self, count):
        return self.count_of(ItemInfo.stone_ids) >= count


    def has_dungeon_rewards(self, count):
        return (self.count_of(ItemInfo.medallion_ids) + self.count_of(ItemInfo.stone_ids)) >= count


    # TODO: Store the item's solver id in the goal
    def has_item_goal(self, item_goal):
        return self.solv_items[ItemInfo.solver_ids[escape_name(item_goal['name'])]] >= item_goal['minimum']


    def has_full_item_goal(self, category, goal, item_goal):
        local_goal = self.world.goal_categories[category.name].get_goal(goal.name)
        per_world_max_quantity = local_goal.get_item(item_goal['name'])['quantity']
        return self.solv_items[ItemInfo.solver_ids[escape_name(item_goal['name'])]] >= per_world_max_quantity


    def has_all_item_goals(self):
        for category in self.world.goal_categories.values():
            for goal in category.goals:
                if not all(map(lambda i: self.has_full_item_goal(category, goal, i), goal.items)):
                    return False
        return True


    def had_night_start(self):
        stod = self.world.settings.starting_tod
        # These are all not between 6:30 and 18:00
        if (stod == 'sunset' or         # 18
            stod == 'evening' or        # 21
            stod == 'midnight' or       # 00
            stod == 'witching-hour'):   # 03
            return True
        else:
            return False


    # Used for fall damage and other situations where damage is unavoidable
    def can_live_dmg(self, hearts):
        mult = self.world.settings.damage_multiplier
        if hearts*4 >= 3:
            return mult != 'ohko' and mult != 'quadruple'
        elif hearts*4 < 3:
            return mult != 'ohko'
        else:
            return True


    # Use the guarantee_hint rule defined in json.
    def guarantee_hint(self):
        return self.world.parser.parse_rule('guarantee_hint')(self)


    # Be careful using this function. It will not collect any
    # items that may be locked behind the item, only the item itself.
    def collect(self, item):
        if 'Small Key Ring' in item.name and self.world.settings.keyring_give_bk:
            dungeon_name = item.name[:-1].split(' (', 1)[1]
            if dungeon_name in ['Forest Temple', 'Fire Temple', 'Water Temple', 'Shadow Temple', 'Spirit Temple']:
                bk = f'Boss Key ({dungeon_name})'
                self.solv_items[ItemInfo.solver_ids[escape_name(bk)]] = 1
        if item.alias:
            self.solv_items[item.alias_id] += item.alias[1]
        if item.advancement:
            self.solv_items[item.solver_id] += 1


    # Be careful using this function. It will not uncollect any
    # items that may be locked behind the item, only the item itself.
    def remove(self, item):
        if 'Small Key Ring' in item.name and self.world.settings.keyring_give_bk:
            dungeon_name = item.name[:-1].split(' (', 1)[1]
            if dungeon_name in ['Forest Temple', 'Fire Temple', 'Water Temple', 'Shadow Temple', 'Spirit Temple']:
                bk = f'Boss Key ({dungeon_name})'
                self.solv_items[ItemInfo.solver_ids[escape_name(bk)]] = 0
        if item.alias and self.solv_items[item.alias_id] > 0:
            self.solv_items[item.alias_id] -= item.alias[1]
            if self.solv_items[item.alias_id] < 0:
                self.solv_items[item.alias_id] = 0
        if self.solv_items[item.solver_id] > 0:
            self.solv_items[item.solver_id] -= 1


    def region_has_shortcuts(self, region_name):
        return self.world.region_has_shortcuts(region_name)


    def __getstate__(self):
        return self.__dict__.copy()


    def __setstate__(self, state):
        self.__dict__.update(state)


    def get_prog_items(self):
        return {
            **{item.name: self.solv_items[item.solver_id]
                for item in ItemInfo.items.values()
                if item.junk is None and self.solv_items[item.solver_id]},
            **{event: self.solv_items[ItemInfo.solver_ids[event]]
                for event in self.world.event_items
                if self.solv_items[ItemInfo.solver_ids[event]]}
        }

