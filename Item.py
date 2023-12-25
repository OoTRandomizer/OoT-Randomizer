from __future__ import annotations
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Optional, Any, overload

from ItemList import item_table
from RulesCommon import allowed_globals, escape_name

if TYPE_CHECKING:
    from Location import Location
    from World import World


class ItemInfo:
    items: dict[str, ItemInfo] = {}
    events: dict[str, ItemInfo] = {}
    bottles: set[str] = set()
    medallions: set[str] = set()
    stones: set[str] = set()
    junk_weight: dict[str, int] = {}
    ocarina_buttons: set[str] = set()

    solver_ids: dict[str, int] = {}
    bottle_ids: set[int] = set()
    medallion_ids: set[int] = set()
    stone_ids: set[int] = set()
    ocarina_buttons_ids: set[int] = set()

    def __init__(self, name: str = '', event: bool = False) -> None:
        if event:
            item_type = 'Event'
            progressive = True
            item_id = None
            special = None
        else:
            (item_type, progressive, item_id, special) = item_table[name]

        self.name: str = name
        self.advancement: bool = (progressive is True)
        self.priority: bool = (progressive is False)
        self.type: str = item_type
        self.special: dict[str, Any] = special or {}
        self.index: Optional[int] = item_id
        self.price: Optional[int] = self.special.get('price', None)
        self.bottle: bool = self.special.get('bottle', False)
        self.medallion: bool = self.special.get('medallion', False)
        self.stone: bool = self.special.get('stone', False)
        self.alias: Optional[tuple[str, int]] = self.special.get('alias', None)
        self.junk: Optional[int] = self.special.get('junk', None)
        self.trade: bool = self.special.get('trade', False)
        self.ocarina_button: bool = self.special.get('ocarina_button', False)

        self.solver_id: Optional[int] = None
        if name and self.junk is None:
            esc = escape_name(name)
            if esc not in ItemInfo.solver_ids:
                allowed_globals[esc] = ItemInfo.solver_ids[esc] = len(ItemInfo.solver_ids)
            self.solver_id = ItemInfo.solver_ids[esc]


for item_name in item_table:
    iteminfo = ItemInfo.items[item_name] = ItemInfo(item_name)
    if iteminfo.bottle:
        ItemInfo.bottles.add(item_name)
        ItemInfo.bottle_ids.add(ItemInfo.solver_ids[escape_name(item_name)])
    if iteminfo.medallion:
        ItemInfo.medallions.add(item_name)
        ItemInfo.medallion_ids.add(ItemInfo.solver_ids[escape_name(item_name)])
    if iteminfo.stone:
        ItemInfo.stones.add(item_name)
        ItemInfo.stone_ids.add(ItemInfo.solver_ids[escape_name(item_name)])

    if iteminfo.junk is not None:
        ItemInfo.junk_weight[item_name] = iteminfo.junk

    if iteminfo.ocarina_button:
        ItemInfo.ocarina_buttons.add(item_name)
        ItemInfo.ocarina_buttons_ids.add(ItemInfo.solver_ids[escape_name(item_name)])

class Item:
    def __init__(self, name: str = '', world: Optional[World] = None, event: bool = False) -> None:
        self.name: str = name
        self.location: Optional[Location] = None
        self.event: bool = event
        if event:
            if name not in ItemInfo.events:
                ItemInfo.events[name] = ItemInfo(name, event=True)
        self.info: ItemInfo = ItemInfo.events[name] if event else ItemInfo.items[name]
        self.price: Optional[int] = self.info.special.get('price', None)
        self.world: Optional[World] = world
        self.looks_like_item: Optional[Item] = None
        self.advancement: bool = self.info.advancement
        self.priority: bool = self.info.priority
        self.type: str = self.info.type
        self.special: dict = self.info.special
        self.index: Optional[int] = self.info.index
        self.alias: Optional[tuple[str, int]] = self.info.alias

        self.solver_id: Optional[int] = self.info.solver_id
        # Do not alias to junk--it has no solver id!
        self.alias_id: Optional[int] = ItemInfo.solver_ids[escape_name(self.alias[0])] if self.alias else None

    def copy(self) -> Item:
        new_item = Item(name=self.name, world=self.world, event=self.event)

        new_item.location = self.location
        new_item.price = self.price
        new_item.looks_like_item = self.looks_like_item

        return new_item

    @property
    def key(self) -> bool:
        return self.smallkey or self.bosskey

    @property
    def smallkey(self) -> bool:
        return self.type == 'SmallKey' or self.type == 'HideoutSmallKey' or  self.type == 'TCGSmallKey'

    @property
    def bosskey(self) -> bool:
        return self.type == 'BossKey' or self.type == 'GanonBossKey'

    @property
    def map(self) -> bool:
        return self.type == 'Map'

    @property
    def compass(self) -> bool:
        return self.type == 'Compass'

    @property
    def dungeonitem(self) -> bool:
        return self.smallkey or self.bosskey or self.map or self.compass or self.type == 'SilverRupee'

    @property
    def unshuffled_dungeon_item(self) -> bool:
        if self.world is None:
            return False
        return ((self.type == 'SmallKey' and self.world.settings.shuffle_smallkeys in ('remove', 'vanilla', 'dungeon')) or
                (self.type == 'HideoutSmallKey' and self.world.settings.shuffle_hideoutkeys == 'vanilla') or
                (self.type == 'TCGSmallKey' and self.world.settings.shuffle_tcgkeys in ('remove', 'vanilla')) or
                (self.type == 'BossKey' and self.world.settings.shuffle_bosskeys in ('remove', 'vanilla', 'dungeon')) or
                (self.type == 'GanonBossKey' and self.world.settings.shuffle_ganon_bosskey in ('remove', 'vanilla', 'dungeon')) or
                ((self.map or self.compass) and (self.world.settings.shuffle_mapcompass in ('remove', 'startwith', 'vanilla', 'dungeon'))) or
                (self.type == 'SilverRupee' and self.world.settings.shuffle_silver_rupees in ('remove','vanilla','dungeon')))

    @property
    def majoritem(self) -> bool:
        if self.world is None:
            return False
        if self.type == 'Token':
            return (self.world.settings.bridge == 'tokens' or self.world.settings.shuffle_ganon_bosskey == 'tokens' or
                (self.world.settings.shuffle_ganon_bosskey == 'on_lacs' and self.world.settings.lacs_condition == 'tokens'))

        if self.type in ('Drop', 'Event', 'Shop', 'DungeonReward') or not self.advancement:
            return False

        if self.name.startswith('Bombchus') and not self.world.settings.free_bombchu_drops:
            return False

        if self.name == 'Heart Container' or self.name.startswith('Piece of Heart'):
            return (self.world.settings.bridge == 'hearts' or self.world.settings.shuffle_ganon_bosskey == 'hearts' or
                (self.world.settings.shuffle_ganon_bosskey == 'on_lacs' and self.world.settings.lacs_condition == 'hearts'))

        if self.map or self.compass:
            return False
        if self.type == 'SmallKey' and self.world.settings.shuffle_smallkeys in ('dungeon', 'vanilla'):
            return False
        if self.type == 'HideoutSmallKey' and self.world.settings.shuffle_hideoutkeys == 'vanilla':
            return False
        if self.type == 'TCGSmallKey' and self.world.settings.shuffle_tcgkeys == 'vanilla':
            return False
        if self.type == 'BossKey' and self.world.settings.shuffle_bosskeys in ('dungeon', 'vanilla'):
            return False
        if self.type == 'GanonBossKey' and self.world.settings.shuffle_ganon_bosskey in ('dungeon', 'vanilla'):
            return False
        if self.type == 'SilverRupee' and self.world.settings.shuffle_silver_rupees in ('dungeon', 'vanilla'):
            return False

        return True

    @property
    def goalitem(self) -> bool:
        if self.world is None:
            return False
        return self.name in self.world.goal_items

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.world.__repr__()} {self.name}"


@overload
def ItemFactory(items: str, world: Optional[World] = None, event: bool = False) -> Item:
    pass


@overload
def ItemFactory(items: Iterable[str], world: Optional[World] = None, event: bool = False) -> list[Item]:
    pass


def ItemFactory(items: str | Iterable[str], world: Optional[World] = None, event: bool = False) -> Item | list[Item]:
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


def make_event_item(name: str, location: Location, item: Optional[Item] = None) -> Item:
    if location.world is None:
        raise Exception(f"`make_event_item` called with location '{location.name}' that doesn't have a world.")
    if item is None:
        item = Item(name, location.world, event=True)
    location.world.push_item(location, item)
    location.locked = True
    if name not in item_table:
        location.internal = True
    location.world.event_items.add(name)
    return item


def is_item(name: str) -> bool:
    return name in item_table


def ItemIterator(predicate: Callable[[Item], bool] = lambda item: True, world: Optional[World] = None) -> Iterable[Item]:
    for item_name in item_table:
        item = ItemFactory(item_name, world)
        if predicate(item):
            yield item
