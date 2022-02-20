from collections import Counter
import copy

from Item import ItemInfo
from Region import Region, TimeOfDay



class State(object):

    def __init__(self, parent):
        self.prog_items = Counter()
        self.world = parent
        self.search = None
        self._won = self.won_triforce_hunt if self.world.settings.triforce_hunt else self.won_normal


    ## Ensure that this will always have a value
    @property
    def is_glitched(self):
        return self.world.settings.logic_rules != 'glitchless'


    def copy(self, new_world=None):
        if not new_world:
            new_world = self.world
        new_state = State(new_world)
        new_state.prog_items = copy.copy(self.prog_items)
        return new_state


    def item_name(self, location):
        location = self.world.get_location(location)
        if location.item is None:
            return None
        return location.item.name


    def won(self):
        return self._won()


    def won_triforce_hunt(self):
        return self.has('Triforce Piece', self.world.settings.triforce_goal_per_world)


    def won_normal(self):
        return self.has('Triforce')


    def has(self, item, count=1):
        return self.prog_items[item] >= count


    def has_any_of(self, items):
        return any(map(self.prog_items.__contains__, items))


    def has_all_of(self, items):
        return all(map(self.prog_items.__contains__, items))


    def count_of(self, items):
        return len(list(filter(self.prog_items.__contains__, items)))


    def item_count(self, item):
        return self.prog_items[item]


    def has_bottle(self, **kwargs):
        # Extra Ruto's Letter are automatically emptied
        return self.has_any_of(ItemInfo.bottles) or self.has('Rutos Letter', 2)


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

    def has_medallions(self, count):
        return self.count_of(ItemInfo.medallions) >= count


    def has_stones(self, count):
        return self.count_of(ItemInfo.stones) >= count


    def has_dungeon_rewards(self, count):
        return (self.count_of(ItemInfo.medallions) + self.count_of(ItemInfo.stones)) >= count


    def has_item_goal(self, item_goal):
        return self.prog_items[item_goal['name']] >= item_goal['minimum']


    def has_full_item_goal(self, category, goal, item_goal):
        local_goal = self.world.goal_categories[category.name].get_goal(goal.name)
        per_world_max_quantity = local_goal.get_item(item_goal['name'])['quantity']
        return self.prog_items[item_goal['name']] >= per_world_max_quantity


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
        if item.alias:
            self.prog_items[item.alias[0]] += item.alias[1]
        if item.advancement:
            self.prog_items[item.name] += 1


    # Be careful using this function. It will not uncollect any
    # items that may be locked behind the item, only the item itself.
    def remove(self, item):
        if item.alias and self.prog_items[item.alias[0]] > 0:
            self.prog_items[item.alias[0]] -= item.alias[1]
            if self.prog_items[item.alias[0]] <= 0:
                del self.prog_items[item.alias[0]]
        if self.prog_items[item.name] > 0:
            self.prog_items[item.name] -= 1
            if self.prog_items[item.name] <= 0:
                del self.prog_items[item.name]


    def __getstate__(self):
        return self.__dict__.copy()


    def __setstate__(self, state):
        self.__dict__.update(state)


