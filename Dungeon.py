from __future__ import annotations
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from Hints import HintArea
    from Item import Item
    from Region import Region
    from World import World


class Dungeon:
    def __init__(self, world: World, name: str, hint: HintArea, regions: Optional[list[Region]] = None) -> None:
        self.world: World = world
        self.name: str = name
        self.hint: HintArea = hint
        self.regions: list[Region] = regions if regions is not None else []
        self.boss_key: list[Item] = []
        self.small_keys: list[Item] = []
        self.dungeon_items: list[Item] = []
        self.silver_rupees: list[Item] = []

        if regions is None:
            for region in world.regions:
                if region.dungeon_name != self.name:
                    continue
                region.dungeon = self
                self.regions.append(region)

    def copy(self, *, copy_dict: Optional[dict[int, Any]] = None) -> Dungeon:
        copy_dict = {} if copy_dict is None else copy_dict
        if (new_dungeon := copy_dict.get(id(self), None)) and isinstance(new_dungeon, Dungeon):
            return new_dungeon

        new_dungeon = Dungeon(world=self.world.copy(copy_dict=copy_dict), name=self.name, hint=self.hint, regions=[])
        copy_dict[id(self)] = new_dungeon

        new_dungeon.regions = [region.copy(copy_dict=copy_dict) for region in self.regions]
        new_dungeon.boss_key = [item.copy(copy_dict=copy_dict) for item in self.boss_key]
        new_dungeon.small_keys = [item.copy(copy_dict=copy_dict) for item in self.small_keys]
        new_dungeon.dungeon_items = [item.copy(copy_dict=copy_dict) for item in self.dungeon_items]
        new_dungeon.silver_rupees = [item.copy(copy_dict=copy_dict) for item in self.silver_rupees]

        return new_dungeon

    @property
    def shuffle_mapcompass(self) -> str:
        return self.world.settings.shuffle_mapcompass

    @property
    def shuffle_smallkeys(self) -> str:
        return self.world.settings.shuffle_smallkeys

    @property
    def shuffle_bosskeys(self) -> str:
        return self.world.settings.shuffle_bosskeys if self.name != 'Ganons Castle' else self.world.settings.shuffle_ganon_bosskey

    @property
    def shuffle_silver_rupees(self) -> str:
        return self.world.settings.shuffle_silver_rupees

    @property
    def empty(self) -> bool:
        return self.world.empty_dungeons[self.name].empty

    @property
    def keys(self) -> list[Item]:
        return self.small_keys + self.boss_key

    @property
    def all_items(self) -> list[Item]:
        return self.dungeon_items + self.keys + self.silver_rupees

    def item_name(self, text: str) -> str:
        return f"{text} ({self.name})"

    def get_silver_rupee_names(self) -> set[str]:
        from Item import ItemInfo
        return {name for name, item in ItemInfo.items.items() if item.type == 'SilverRupee' and self.name in name}

    def get_item_names(self) -> set[str]:
        return (self.get_silver_rupee_names() |
                {self.item_name(name) for name in ["Map", "Compass", "Small Key", "Boss Key", "Small Key Ring"]})

    def is_dungeon_item(self, item: Item) -> bool:
        return item.name in [dungeon_item.name for dungeon_item in self.all_items]

    def get_restricted_dungeon_items(self) -> Iterator[Item]:
        if self.shuffle_mapcompass == 'dungeon' or (self.empty and self.shuffle_mapcompass in ['any_dungeon', 'overworld', 'keysanity', 'regional']):
            yield from self.dungeon_items
        if self.shuffle_smallkeys == 'dungeon' or (self.empty and self.shuffle_smallkeys in ['any_dungeon', 'overworld', 'keysanity', 'regional']):
            yield from self.small_keys
        if self.shuffle_bosskeys == 'dungeon' or (self.empty and self.shuffle_bosskeys in ['any_dungeon', 'overworld', 'keysanity', 'regional']):
            yield from self.boss_key
        if self.shuffle_silver_rupees == 'dungeon' or (self.empty and self.shuffle_silver_rupees in ['any_dungeon', 'overworld', 'anywhere', 'regional']):
            yield from self.silver_rupees

    # get a list of items that don't have to be in their proper dungeon
    def get_unrestricted_dungeon_items(self) -> Iterator[Item]:
        if self.empty:
            return
        if self.shuffle_mapcompass in ['any_dungeon', 'overworld', 'keysanity', 'regional']:
            yield from self.dungeon_items
        if self.shuffle_smallkeys in ['any_dungeon', 'overworld', 'keysanity', 'regional']:
            yield from self.small_keys
        if self.shuffle_bosskeys in ['any_dungeon', 'overworld', 'keysanity', 'regional']:
            yield from self.boss_key
        if self.shuffle_silver_rupees in ['any_dungeon', 'overworld', 'anywhere', 'regional']:
            yield from self.silver_rupees

    def __str__(self) -> str:
        return str(self.__unicode__())

    def __unicode__(self) -> str:
        return '%s' % self.name
