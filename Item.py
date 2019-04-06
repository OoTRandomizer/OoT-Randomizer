from ItemList import item_table


class ItemInfo(object):
    items = {}

    def __init__(self, name=''):
        (type, progessive, itemID, special) = item_table[name]

        self.name = name
        self.advancement = (progessive == True)
        self.priority = (progessive == False)
        self.type = type
        self.special = special or {}
        self.index = itemID
        self.price = self.special.get('price')
        self.bottle = self.special.get('bottle', False)


    def isBottle(name):
        return ItemInfo.items[name].bottle


for item_name in item_table:
    ItemInfo.items[item_name] = ItemInfo(item_name)


class Item(object):

    def __init__(self, name='', world=None):
        self.name = name
        self.location = None
        self.info = ItemInfo.items[name]
        self.price = self.info.special.get('price')
        self.world = world
        self.looks_like_item = None


    @property
    def advancement(self):
        return self.info.advancement


    @property
    def priority(self):
        return self.info.priority


    @property
    def type(self):
        return self.info.type


    @property
    def special(self):
        return self.info.special


    @property
    def index(self):
        return self.info.index


    item_worlds_to_fix = {}

    def copy(self, new_world=None):
        if new_world is not None and self.world is not None and new_world.id != self.world.id:
            new_world = None

        new_item = Item(self.name, new_world)
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
        return self.smallkey or self.bosskey


    @property
    def smallkey(self):
        return self.type == 'SmallKey' or self.type == 'FortressSmallKey'


    @property
    def bosskey(self):
        return self.type == 'BossKey'


    @property
    def map(self):
        return self.type == 'Map'


    @property
    def compass(self):
        return self.type == 'Compass'


    @property
    def dungeonitem(self):
        return self.smallkey or self.bosskey or self.map or self.compass


    @property
    def majoritem(self):
        if self.type == 'Token':
            return self.world.bridge == 'tokens'

        if self.type == 'Event' or self.type == 'Shop' or not self.advancement:
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
        if item in ItemInfo.items:
            ret.append(Item(item, world))
        else:
            raise KeyError('Unknown Item: %s', item)

    if singleton:
        return ret[0]
    return ret


def IsItem(name):
    return name in item_table


def ItemIterator(predicate=lambda loc: True, world=None):
    for item_name in item_table:
        item = ItemFactory(item_name, world)
        if predicate(item):
            yield item
