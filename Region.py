from __future__ import annotations
from enum import Enum, unique
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from Dungeon import Dungeon
    from Entrance import Entrance
    from Hints import HintArea
    from Item import Item
    from Location import Location
    from World import World


@unique
class RegionType(Enum):
    Overworld = 1
    Interior = 2
    Dungeon = 3
    Grotto = 4

    @property
    def is_indoors(self) -> bool:
        """Shorthand for checking if Interior or Dungeon"""
        return self in (RegionType.Interior, RegionType.Dungeon, RegionType.Grotto)


# Pretends to be an enum, but when the values are raw ints, it's much faster
class TimeOfDay:
    NONE: int = 0
    DAY: int = 1
    DAMPE: int = 2
    ALL: int = DAY | DAMPE


class Region:
    def __init__(self, world: World, name: str, region_type: RegionType = RegionType.Overworld) -> None:
        self.world: World = world
        self.name: str = name
        self.type: RegionType = region_type
        self.entrances: list[Entrance] = []
        self.exits: list[Entrance] = []
        self.locations: list[Location] = []
        self.dungeon: Optional[Dungeon] = None
        self.dungeon_name: Optional[str] = None
        self.hint_name: Optional[str] = None
        self.alt_hint_name: Optional[str] = None
        self.price: Optional[int] = None
        self.time_passes: bool = False
        self.provides_time: int = TimeOfDay.NONE
        self.scene: Optional[str] = None
        self.is_boss_room: bool = False
        self.savewarp: Optional[Entrance] = None

    def copy(self) -> Region:
        new_region = Region(world=self.world, name=self.name, region_type=self.type)

        new_region.exits = [entrance for entrance in self.exits]
        new_region.locations = [location for location in self.locations]

        # Why does this not work properly?
        # new_region.entrances = [entrance.copy(copy_dict=copy_dict) for entrance in self.entrances]

        new_region.dungeon = self.dungeon
        new_region.dungeon_name = self.dungeon_name
        new_region.hint_name = self.hint_name
        new_region.alt_hint_name = self.alt_hint_name
        new_region.price = self.price
        new_region.time_passes = self.time_passes
        new_region.provides_time = self.provides_time
        new_region.scene = self.scene
        new_region.is_boss_room = self.is_boss_room
        new_region.savewarp = self.savewarp

        return new_region

    @property
    def hint(self) -> Optional[HintArea]:
        from Hints import HintArea

        if self.hint_name is not None:
            return HintArea[self.hint_name]
        if self.dungeon:
            return self.dungeon.hint

    @property
    def alt_hint(self) -> Optional[HintArea]:
        from Hints import HintArea

        if self.alt_hint_name is not None:
            return HintArea[self.alt_hint_name]

    def can_fill(self, item: Item, manual: bool = False) -> bool:
        from Hints import HintArea

        if not manual and self.world.settings.empty_dungeons_mode != 'none' and item.dungeonitem:
            # An empty dungeon can only store its own dungeon items
            if self.dungeon and self.dungeon.world.empty_dungeons[self.dungeon.name].empty:
                return self.dungeon.is_dungeon_item(item) and item.world.id == self.world.id
            # Items from empty dungeons can only be in their own dungeons
            for dungeon in item.world.dungeons:
                if item.world.empty_dungeons[dungeon.name].empty and dungeon.is_dungeon_item(item):
                    return False

        is_self_dungeon_restricted = False
        is_self_region_restricted = None
        is_hint_color_restricted = None
        is_dungeon_restricted = False
        is_overworld_restricted = False

        if item.type in ('Map', 'Compass', 'SmallKey', 'HideoutSmallKey', 'TCGSmallKey', 'BossKey', 'GanonBossKey', 'SilverRupee'):
            shuffle_setting = (
                self.world.settings.shuffle_mapcompass if item.type in ('Map', 'Compass') else
                self.world.settings.shuffle_smallkeys if item.type == 'SmallKey' else
                self.world.settings.shuffle_hideoutkeys if item.type == 'HideoutSmallKey' else
                self.world.settings.shuffle_tcgkeys if item.type == 'TCGSmallKey' else
                self.world.settings.shuffle_bosskeys if item.type == 'BossKey' else
                self.world.settings.shuffle_ganon_bosskey if item.type == 'GanonBossKey' else
                self.world.settings.shuffle_silver_rupees if item.type == 'SilverRupee' else
                None
            )

            is_self_dungeon_restricted = shuffle_setting in ('dungeon', 'vanilla') and item.type not in ('HideoutSmallKey', 'TCGSmallKey')
            is_self_region_restricted = [HintArea.GERUDO_FORTRESS, HintArea.THIEVES_HIDEOUT] if shuffle_setting == 'fortress' else None
            is_hint_color_restricted = [HintArea.for_dungeon(item.name).color] if shuffle_setting == 'regional' else None
            is_dungeon_restricted = shuffle_setting == 'any_dungeon'
            is_overworld_restricted = shuffle_setting == 'overworld'

        if is_self_dungeon_restricted and not manual:
            hint_area = HintArea.at(self)
            return hint_area.is_dungeon and hint_area.is_dungeon_item(item) and item.world.id == self.world.id

        if is_self_region_restricted and not manual:
            return HintArea.at(self) in is_self_region_restricted and item.world.id == self.world.id

        if is_hint_color_restricted and not manual:
            return HintArea.at(self).color in is_hint_color_restricted

        if is_dungeon_restricted and not manual:
            return HintArea.at(self).is_dungeon

        if is_overworld_restricted and not manual:
            return not HintArea.at(self).is_dungeon

        if item.name == 'Triforce Piece':
            return item.world.id == self.world.id

        return True

    def get_scene(self) -> Optional[str]:
        if self.scene:
            return self.scene
        elif self.dungeon:
            return self.dungeon.name
        else:
            return None

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.world.__repr__()} {self.name}"
