from ItemList import item_table

class Item(object):

    def __init__(self, name='', advancement=False, priority=False, type=None, index=None, special=None, world=None):
        self.name = name
        self.advancement = advancement
        self.priority = priority
        self.type = type
        self.special = special or {}
        self.index = index
        self.location = None
        self.price = self.special.get('price')
        self.world = world
        self.looks_like_item = None


    item_worlds_to_fix = {}

    def copy(self, new_world=None):
        if new_world is not None and self.world is not None and new_world.id != self.world.id:
            new_world = None

        new_item = Item(self.name, self.advancement, self.priority, self.type, self.index, self.special)
        new_item.world = new_world
        new_item.price = self.price

        if new_world is None and self.world is not None:
            Item.item_worlds_to_fix[new_item] = self.world.id

        return new_item

    @classmethod
    def fix_worlds_after_copy(cls, worlds):
        items_fixed = []
        for item, world_id in cls.item_worlds_to_fix.items():
            item.world = worlds[world_id]
            items_fixed.append(item)
        for item in items_fixed:
            del cls.item_worlds_to_fix[item]

    @property
    def key(self):
        return self.type == 'SmallKey' or self.type == 'BossKey'


    @property
    def smallkey(self):
        return self.type == 'SmallKey'


    @property
    def bosskey(self):
        return self.type == 'BossKey'


    @property
    def crystal(self):
        return self.type == 'Crystal'


    @property
    def map(self):
        return self.type == 'Map'


    @property
    def compass(self):
        return self.type == 'Compass'


    @property
    def dungeonitem(self):
        return self.type == 'SmallKey' or self.type == 'BossKey' or self.type == 'Map' or self.type == 'Compass'


    @property
    def majoritem(self):
        if self.type == 'Token' or self.type == 'Event' or self.type == 'Shop' or not self.advancement:
            return False

        if self.name.startswith('Bombchus') and not self.world.bombchus_in_logic:
            return False

        if self.map or self.compass:
            return False
        if self.smallkey and self.world.shuffle_smallkeys == 'dungeon':
            return False
        if self.bosskey and self.world.shuffle_bosskeys == 'dungeon':
            return False

        return True


    def __str__(self):
        return str(self.__unicode__())


    def __unicode__(self):
        return '%s' % self.name


def ItemFactory(items, world=None):
    ret = []
    singleton = False
    if isinstance(items, str):
        items = [items]
        singleton = True
    for item in items:
        if item in item_table:
            (type, progessive, itemID, special) = item_table[item]
            advancement = (progessive == True)
            priority    = (progessive == False)
            new_item = Item(item, advancement, priority, type, itemID, special)

            if world:
                new_item.world = world
            ret.append(new_item)
        else:
            raise KeyError('Unknown Item: %s', item)

    if singleton:
        return ret[0]
    return ret
