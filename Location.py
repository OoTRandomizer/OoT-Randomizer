from __future__ import annotations
import logging
from collections.abc import Callable, Iterable
from enum import Enum
from typing import TYPE_CHECKING, Optional, Any, overload

from HintList import misc_item_hint_table, misc_location_hint_table
from LocationList import location_table, location_is_viewable, LocationAddress, LocationDefault, LocationFilterTags

if TYPE_CHECKING:
    from Dungeon import Dungeon
    from Item import Item
    from Region import Region
    from RulesCommon import AccessRule
    from State import State
    from World import World


class DisableType(Enum):
    ENABLED = 0
    PENDING = 1
    DISABLED = 2


class Location:
    def __init__(self, name: str = '', address: LocationAddress = None, address2: LocationAddress = None, default: LocationDefault = None,
                 location_type: str = 'Chest', scene: Optional[int] = None, parent: Optional[Region] = None,
                 filter_tags: LocationFilterTags = None, internal: bool = False, vanilla_item: Optional[str] = None) -> None:
        self.name: str = name
        self.parent_region: Optional[Region] = parent
        self.item: Optional[Item] = None
        self.vanilla_item: Optional[str] = vanilla_item
        self.address: LocationAddress = address
        self.address2: LocationAddress = address2
        self.default: LocationDefault = default
        self.type: str = location_type
        self.scene: Optional[int] = scene
        self.internal: bool = internal
        self.access_rule: AccessRule = lambda state, **kwargs: True
        self.access_rules: list[AccessRule] = []
        self.item_rule: Callable[[Location, Item], bool] = lambda location, item: True
        self.locked: bool = False
        self.price: Optional[int] = None
        self.minor_only: bool = False
        self.world: Optional[World] = None
        self.disabled: DisableType = DisableType.ENABLED
        self.always: bool = False
        self.never: bool = False
        self.filter_tags: Optional[tuple[str, ...]] = (filter_tags,) if isinstance(filter_tags, str) else filter_tags
        self.rule_string: Optional[str] = None

    def copy(self) -> Location:
        new_location = Location(name=self.name, address=self.address, address2=self.address2, default=self.default,
                                location_type=self.type, scene=self.scene, parent=self.parent_region,
                                filter_tags=self.filter_tags, internal=self.internal, vanilla_item=self.vanilla_item)

        new_location.world = self.world
        new_location.item = self.item
        new_location.access_rule = self.access_rule
        new_location.access_rules = list(self.access_rules)
        new_location.item_rule = self.item_rule
        new_location.locked = self.locked
        new_location.minor_only = self.minor_only
        new_location.disabled = self.disabled
        new_location.always = self.always
        new_location.never = self.never

        return new_location

    @property
    def dungeon(self) -> Optional[Dungeon]:
        return self.parent_region.dungeon if self.parent_region is not None else None

    def add_rule(self, lambda_rule: AccessRule) -> None:
        if self.always:
            self.set_rule(lambda_rule)
            self.always = False
            return
        if self.never:
            return
        self.access_rules.append(lambda_rule)
        self.access_rule = self._run_rules

    def _run_rules(self, state, **kwargs):
        for rule in self.access_rules:
            if not rule(state, **kwargs):
                return False
        return True

    def set_rule(self, lambda_rule: AccessRule) -> None:
        self.access_rule = lambda_rule
        self.access_rules = [lambda_rule]

    def can_fill(self, state: State, item: Item, check_access: bool = True) -> bool:
        if state.search is None:
            return False
        if self.minor_only and item.majoritem:
            return False
        return (
            not self.is_disabled and
            self.can_fill_fast(item) and
            (not check_access or state.search.spot_access(self, 'either'))
        )

    def can_fill_fast(self, item: Item, manual: bool = False) -> bool:
        if self.parent_region is None:
            return False
        return self.parent_region.can_fill(item, manual) and self.item_rule(self, item)

    @property
    def is_disabled(self) -> bool:
        return ((self.disabled == DisableType.DISABLED) or
                (self.disabled == DisableType.PENDING and self.locked))

    # Can the player see what's placed at this location without collecting it?
    # Used to reduce JSON spoiler noise
    def has_preview(self) -> bool:
        if self.world is None:
            return False
        return location_is_viewable(self.name, self.world.settings.correct_chest_appearances, self.world.settings.fast_chests)

    def has_item(self) -> bool:
        return self.item is not None

    def has_no_item(self) -> bool:
        return self.item is None

    def has_progression_item(self) -> bool:
        return self.item is not None and self.item.advancement

    def maybe_set_misc_hints(self) -> None:
        if self.item is None or self.item.world is None or self.world is None:
            return
        if self.item.world.dungeon_rewards_hinted and self.item.name in self.item.world.rewardlist:
            if self.item.name not in self.item.world.hinted_dungeon_reward_locations:
                self.item.world.hinted_dungeon_reward_locations[self.item.name] = self
                logging.getLogger('').debug(f'{self.item.name} [{self.item.world.id}] set to [{self.name}]')
        for hint_type in misc_item_hint_table:
            item = self.item.world.misc_hint_items[hint_type]
            if hint_type not in self.item.world.misc_hint_item_locations and self.item.name == item:
                self.item.world.misc_hint_item_locations[hint_type] = self
                logging.getLogger('').debug(f'{item} [{self.item.world.id}] set to [{self.name}]')
        for hint_type in misc_location_hint_table:
            the_location = self.world.misc_hint_locations[hint_type]
            if hint_type not in self.world.misc_hint_location_items and self.name == the_location:
                self.world.misc_hint_location_items[hint_type] = self.item
                logging.getLogger('').debug(f'{the_location} [{self.world.id}] set to [{self.item.name}]')

    def __str__(self) -> str:
        return str(self.__unicode__())

    def __unicode__(self) -> str:
        return '%s' % self.name


@overload
def LocationFactory(locations: str) -> Location:
    pass


@overload
def LocationFactory(locations: list[str]) -> list[Location]:
    pass


def LocationFactory(locations: str | list[str]) -> Location | list[Location]:
    ret = []
    singleton = False
    if isinstance(locations, str):
        locations = [locations]
        singleton = True
    for location in locations:
        if location in location_table:
            match_location = location
        else:
            match_location = next(filter(lambda k: k.lower() == location.lower(), location_table), None)
        if match_location:
            type, scene, default, addresses, vanilla_item, filter_tags = location_table[match_location]
            if addresses is None:
                addresses = (None, None)
            address, address2 = addresses
            ret.append(Location(match_location, address, address2, default, type, scene, None, filter_tags, False, vanilla_item))
        else:
            raise KeyError('Unknown Location: %s', location)

    if singleton:
        return ret[0]
    return ret


def LocationIterator(predicate: Callable[[Location], bool] = lambda loc: True) -> Iterable[Location]:
    for location_name in location_table:
        location = LocationFactory(location_name)
        if predicate(location):
            yield location


def is_location(name: str) -> bool:
    return name in location_table
