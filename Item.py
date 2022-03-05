from ItemList import item_table


class ItemInfo(object):
    items = {}
    events = {}
    bottles = set()
    medallions = set()
    stones = set()
    junk = {}

    def __init__(self, name='', event=False):
        if event:
            type = 'Event'
            progressive = True
            itemID = None
            special = None
        else:
            (type, progressive, itemID, special) = item_table[name]

        self.name = name
        self.advancement = (progressive is True)
        self.priority = (progressive is False)
        self.type = type
        self.special = special or {}
        self.index = itemID
        self.price = self.special.get('price')
        self.bottle = self.special.get('bottle', False)
        self.medallion = self.special.get('medallion', False)
        self.stone = self.special.get('stone', False)
        self.alias = self.special.get('alias', None)
        self.junk = self.special.get('junk', None)


for item_name in item_table:
    ItemInfo.items[item_name] = ItemInfo(item_name)
    if ItemInfo.items[item_name].bottle:
        ItemInfo.bottles.add(item_name)
    if ItemInfo.items[item_name].medallion:
        ItemInfo.medallions.add(item_name)
    if ItemInfo.items[item_name].stone:
        ItemInfo.stones.add(item_name)
    if ItemInfo.items[item_name].junk is not None:
        ItemInfo.junk[item_name] = ItemInfo.items[item_name].junk


class Item(object):

    def __init__(self, name='', world=None, event=False):
        self.name = name
        self.location = None
        self.event = event
        if event:
            if name not in ItemInfo.events:
                ItemInfo.events[name] = ItemInfo(name, event=True)
            self.info = ItemInfo.events[name]
        else:
            self.info = ItemInfo.items[name]
        self.price = self.info.special.get('price')
        self.world = world
        self.looks_like_item = None
        self.advancement = self.info.advancement
        self.priority = self.info.priority
        self.type = self.info.type
        self.special = self.info.special
        self.index = self.info.index
        self.alias = self.info.alias


    item_worlds_to_fix = {}

    def copy(self, new_world=None):
        if new_world is not None and self.world is not None and new_world.id != self.world.id:
            new_world = None

        new_item = Item(self.name, new_world, self.event)
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
        return self.type == 'SmallKey' or self.type == 'HideoutSmallKey'


    @property
    def bosskey(self):
        return self.type == 'BossKey' or self.type == 'GanonBossKey'


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
    def unshuffled_dungeon_item(self):
        return ((self.type == 'SmallKey' and self.world.settings.shuffle_smallkeys in ['remove','vanilla','dungeon']) or
                (self.type == 'FortressSmallKey' and self.world.settings.shuffle_fortresskeys in ['vanilla']) or
                (self.bosskey and self.world.settings.shuffle_bosskeys in ['remove','vanilla','dungeon']) or
                ((self.map or self.compass) and (self.world.settings.shuffle_mapcompass in ['remove','startwith','vanilla','dungeon'])))

    @property
    def majoritem(self):
        if self.type == 'Token':
            return (self.world.settings.bridge == 'tokens' or self.world.settings.shuffle_ganon_bosskey == 'tokens' or
                (self.world.settings.shuffle_ganon_bosskey == 'on_lacs' and self.world.settings.lacs_condition == 'tokens'))

        if self.type in ('Drop', 'Event', 'Shop', 'DungeonReward') or not self.advancement:
            return False

        if self.name.startswith('Bombchus') and not self.world.settings.bombchus_in_logic:
            return False

        if self.map or self.compass:
            return False
        if self.type == 'SmallKey' and self.world.settings.shuffle_smallkeys in ['dungeon', 'vanilla']:
            return False
        if self.type == 'HideoutSmallKey' and self.world.settings.shuffle_hideoutkeys == 'vanilla':
            return False
        if self.type == 'BossKey' and self.world.settings.shuffle_bosskeys in ['dungeon', 'vanilla']:
            return False
        if self.type == 'GanonBossKey' and self.world.settings.shuffle_ganon_bosskey in ['dungeon', 'vanilla']:
            return False

        return True


    @property
    def goalitem(self):
        return self.name in self.world.goal_items


    def __str__(self):
        return str(self.__unicode__())


    def __unicode__(self):
        return '%s' % self.name


def ItemFactory(items, world=None, event=False):
    if isinstance(items, str):
        if not event and items not in ItemInfo.items:
            raise KeyError('Unknown Item: %s' % items)
        return Item(items, world, event)

    ret = []
    for item in items:
        if not event and item not in ItemInfo.items:
            raise KeyError('Unknown Item: %s' % item)
        ret.append(Item(item, world, event))

    return ret


def MakeEventItem(name, location, item=None):
    if item is None:
        item = ItemFactory(name, location.world, event=True)
    location.world.push_item(location, item)
    location.locked = True
    if name not in item_table:
        location.internal = True
    location.world.event_items.add(name)
    return item


def IsItem(name):
    return name in item_table


def ItemIterator(predicate=lambda loc: True, world=None):
    for item_name in item_table:
        item = ItemFactory(item_name, world)
        if predicate(item):
            yield item
