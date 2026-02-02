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
        self.reward: list[Item] = []

        if regions is None:
            for region in world.regions:
                if region.dungeon_name != self.name:
                    continue
                region.dungeon = self
                self.regions.append(region)

    def copy(self) -> Dungeon:
        new_dungeon = Dungeon(world=self.world, name=self.name, hint=self.hint, regions=[])

        new_dungeon.regions = [region for region in self.regions]
        new_dungeon.boss_key = [item for item in self.boss_key]
        new_dungeon.small_keys = [item for item in self.small_keys]
        new_dungeon.dungeon_items = [item for item in self.dungeon_items]
        new_dungeon.silver_rupees = [item for item in self.silver_rupees]
        new_dungeon.reward = [item for item in self.reward]

        return new_dungeon

    @staticmethod
    def from_vanilla_reward(item: Item) -> Dungeon:
        dungeons = [dungeon for dungeon in item.world.dungeons if dungeon.vanilla_reward == item.name]
        if dungeons:
            return dungeons[0]

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
    def shuffle_dungeon_rewards(self) -> str:
        return self.world.settings.shuffle_dungeon_rewards

    @property
    def precompleted(self) -> bool:
        return self.world.precompleted_dungeons.get(self.name, False)

    @property
    def keys(self) -> list[Item]:
        return self.small_keys + self.boss_key

    @property
    def all_items(self) -> list[Item]:
        return self.dungeon_items + self.keys + self.silver_rupees + self.reward

    @property
    def vanilla_boss_name(self) -> Optional[str]:
        return {
            'Deku Tree': 'Queen Gohma',
            'Dodongos Cavern': 'King Dodongo',
            'Jabu Jabus Belly': 'Barinade',
            'Forest Temple': 'Phantom Ganon',
            'Fire Temple': 'Volvagia',
            'Water Temple': 'Morpha',
            'Shadow Temple': 'Bongo Bongo',
            'Spirit Temple': 'Twinrova',
        }.get(self.name)


    @property
    def vanilla_reward(self) -> Optional[str]:
        if self.vanilla_boss_name is not None:
            return self.world.get_location(self.vanilla_boss_name).vanilla_item

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
        if self.shuffle_mapcompass == 'dungeon' or (self.precompleted and self.shuffle_mapcompass in ('any_dungeon', 'overworld', 'keysanity', 'regional')):
            yield from self.dungeon_items
        if self.shuffle_smallkeys == 'dungeon' or (self.precompleted and self.shuffle_smallkeys in ('any_dungeon', 'overworld', 'keysanity', 'regional')):
            yield from self.small_keys
        if self.shuffle_bosskeys == 'dungeon' or (self.precompleted and self.shuffle_bosskeys in ('any_dungeon', 'overworld', 'keysanity', 'regional')):
            yield from self.boss_key
        if self.shuffle_silver_rupees == 'dungeon' or (self.precompleted and self.shuffle_silver_rupees in ('any_dungeon', 'overworld', 'anywhere', 'regional')):
            yield from self.silver_rupees
        if self.shuffle_dungeon_rewards in ('vanilla', 'dungeon'): # we don't lock rewards inside pre-completed dungeons since they're still useful outside
            yield from self.reward

    # get a list of items that don't have to be in their proper dungeon
    def get_unrestricted_dungeon_items(self) -> Iterator[Item]:
        if self.precompleted:
            return
        if self.shuffle_mapcompass in ('any_dungeon', 'overworld', 'keysanity', 'regional'):
            yield from self.dungeon_items
        if self.shuffle_smallkeys in ('any_dungeon', 'overworld', 'keysanity', 'regional'):
            yield from self.small_keys
        if self.shuffle_bosskeys in ('any_dungeon', 'overworld', 'keysanity', 'regional'):
            yield from self.boss_key
        if self.shuffle_silver_rupees in ('any_dungeon', 'overworld', 'anywhere', 'regional'):
            yield from self.silver_rupees
        if self.shuffle_dungeon_rewards in ('any_dungeon', 'overworld', 'anywhere', 'regional'):
            yield from self.reward

    def __str__(self) -> str:
        return self.name
