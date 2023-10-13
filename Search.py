from __future__ import annotations
import copy
import itertools
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from Region import Region, TimeOfDay
from State import State

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    TypeAlias = str

if TYPE_CHECKING:
    from Entrance import Entrance
    from Item import Item
    from Location import Location
    from Goals import GoalCategory

ValidGoals: TypeAlias = "dict[str, bool | dict[str, list[int] | dict[int, list[str]]]]"


@dataclass
class SearchCache:
    child_queue: list[Entrance] = field(default_factory=list)
    adult_queue: list[Entrance] = field(default_factory=list)
    visited_locations: set[Location] = field(default_factory=set)
    child_regions: dict[Region, int] = field(default_factory=dict)
    adult_regions: dict[Region, int] = field(default_factory=dict)

    def copy(self) -> SearchCache:
        new = type(self)()
        for name, value in self.__dict__.items():
            setattr(new, name, copy.copy(value))
        return new


class Search:
    def __init__(self, state_list: Iterable[State], initial_cache: Optional[SearchCache] = None) -> None:
        self.state_list: list[State] = [state.copy() for state in state_list]

        # Let the states reference this search.
        for state in self.state_list:
            state.search = self

        self._cache: SearchCache
        self.cached_spheres: list[SearchCache]
        if initial_cache:
            self._cache = initial_cache
            self.cached_spheres = [self._cache]
        else:
            root_regions = [state.world.get_region('Root') for state in self.state_list]
            # The cache is a dict with 5 values:
            #  child_regions, adult_regions: maps of Region -> tod, all the regions in that sphere
            #    values are lazily-determined tod flags (see TimeOfDay).
            #  child_queue, adult_queue: queue of Entrance, all the exits to try next sphere
            #  visited_locations: set of Locations visited in or before that sphere.
            self._cache = SearchCache(
                child_queue=list(exit for region in root_regions for exit in region.exits),
                adult_queue=list(exit for region in root_regions for exit in region.exits),
                visited_locations=set(),
                child_regions={region: TimeOfDay.NONE for region in root_regions},
                adult_regions={region: TimeOfDay.NONE for region in root_regions},
            )
            self.cached_spheres = [self._cache]
            self.next_sphere()

    def copy(self) -> Search:
        # we only need to copy the top sphere since that's what we're starting with and we don't go back
        # copy always makes a nonreversible instance
        return Search(self.state_list, initial_cache=self._cache.copy())

    def collect_all(self, itempool: Iterable[Item]) -> None:
        for item in itempool:
            if item.solver_id is not None and item.world is not None:
                self.state_list[item.world.id].collect(item)

    def collect(self, item: Item) -> None:
        if item.world is None:
            raise Exception(f"Item '{item.name}' cannot be collected as it does not have a world.")
        self.state_list[item.world.id].collect(item)

    @classmethod
    def max_explore(cls, state_list: Iterable[State], itempool: Optional[Iterable[Item]] = None) -> Search:
        p = cls(state_list)
        if itempool:
            p.collect_all(itempool)
        p.collect_locations()
        return p

    @classmethod
    def with_items(cls, state_list: Iterable[State], itempool: Optional[Iterable[Item]] = None) -> Search:
        p = cls(state_list)
        if itempool:
            p.collect_all(itempool)
        p.next_sphere()
        return p

    # Truncates the sphere cache based on which sphere a location is in, and
    # drops the location from the appropriate visited set.
    # Doesn't forget which sphere locations are in as an optimization, so be careful
    # to only unvisit locations in descending sphere order, or locations that
    # have been revisited in the most recent iteration.
    # Locations never visited in this Search are assumed to have been visited
    # in sphere 0, so unvisiting them will discard the entire cache.
    # Not safe to call during iteration.
    def unvisit(self, location: Location) -> None:
        raise Exception('Unimplemented for Search. Perhaps you want RewindableSearch.')

    # Drops the item from its respective state.
    # Has no effect on cache!
    def uncollect(self, item: Item) -> None:
        if item.world is None:
            raise Exception(f"Item '{item.name}' cannot be uncollected as it does not have a world.")
        self.state_list[item.world.id].remove(item)

    # Resets the sphere cache to the first entry only.
    # Does not uncollect any items!
    # Not safe to call during iteration.
    def reset(self) -> None:
        raise Exception('Unimplemented for Search. Perhaps you want RewindableSearch.')

    # Internal to the iteration. Modifies the exit_queue, regions.
    # Returns a queue of the exits whose access rule failed,
    # as a cache for the exits to try on the next iteration.
    def _expand_regions(self, exit_queue: list[Entrance], regions: dict[Region, int], age: Optional[str]) -> list[Entrance]:
        failed = []
        for exit in exit_queue:
            if exit.world and exit.connected_region and exit.connected_region not in regions:
                # Evaluate the access rule directly, without tod
                if exit.access_rule(self.state_list[exit.world.id], spot=exit, age=age):
                    # If it found a new tod, make sure we try other entrances again.
                    # Probably would take too long and not be worth it if we only grabbed the exits
                    # for the given world...
                    if exit.connected_region.provides_time and ~regions[exit.world.get_region('Root')] & exit.connected_region.provides_time:
                        exit_queue.extend(failed)
                        failed = []
                        regions[exit.world.get_region('Root')] |= exit.connected_region.provides_time
                    regions[exit.connected_region] = exit.connected_region.provides_time
                    exit_queue.extend(exit.connected_region.exits)
                else:
                    failed.append(exit)
        return failed

    def _expand_tod_regions(self, regions: dict[Region, int], goal_region: Region, age: Optional[str], tod: int) -> bool:
        # grab all the exits from the regions with the given tod in the same world as our goal.
        # we want those that go to existing regions without the tod, until we reach the goal.
        has_tod_world = lambda regtod: regtod[1] & tod and regtod[0].world == goal_region.world
        exit_queue = list(itertools.chain.from_iterable(region.exits for region, _ in filter(has_tod_world, regions.items())))
        for exit in exit_queue:
            # We don't look for new regions, just spreading the tod to our existing regions
            if exit.connected_region in regions and tod & ~regions[exit.connected_region]:
                # Evaluate the access rule directly
                if exit.access_rule(self.state_list[exit.world.id], spot=exit, age=age, tod=tod):
                    regions[exit.connected_region] |= tod
                    if exit.connected_region == goal_region:
                        return True
                    exit_queue.extend(exit.connected_region.exits)
        return False

    # Explores available exits, updating relevant entries in the cache in-place.
    # Returns the regions accessible in the new sphere as child,
    # the regions accessible as adult, and the set of visited locations.
    # These are references to the new entry in the cache, so they can be modified
    # directly.
    def next_sphere(self) -> tuple[dict[Region, int], dict[Region, int], set[Location]]:
        # Use the queue to iteratively add regions to the accessed set,
        # until we are stuck or out of regions.

        # Replace the queues (which have been modified) with just the
        # failed exits that we can retry next time.
        self._cache.adult_queue = self._expand_regions(self._cache.adult_queue, self._cache.adult_regions, 'adult')
        self._cache.child_queue = self._expand_regions(self._cache.child_queue, self._cache.child_regions, 'child')

        return self._cache.child_regions, self._cache.adult_regions, self._cache.visited_locations

    # Yields every reachable location, by iteratively deepening explored sets of regions
    # (one as child, one as adult) and invoking access rules.
    # item_locations is a list of Location objects from state_list that the caller
    # has prefiltered (eg. by whether they contain advancement items).
    #
    # Inside the loop, the caller usually wants to collect items at these
    # locations to see if the game is beatable. Collection should be done
    # using internal State (recommended to just call search.collect).
    def iter_reachable_locations(self, item_locations: Iterable[Location]) -> Iterable[Location]:
        had_reachable_locations = True
        # will loop as long as any visits were made, and at least once
        while had_reachable_locations:
            child_regions, adult_regions, visited_locations = self.next_sphere()

            # Get all locations in accessible_regions that aren't visited,
            # and check if they can be reached. Collect them.
            had_reachable_locations = False
            for loc in item_locations:
                if loc in visited_locations:
                    continue
                # Check adult first; it's the most likely.
                if (loc.parent_region in adult_regions
                        and loc.access_rule(self.state_list[loc.world.id], spot=loc, age='adult')):
                    had_reachable_locations = True
                    # Mark it visited for this algorithm
                    visited_locations.add(loc)
                    yield loc

                elif (loc.parent_region in child_regions
                      and loc.access_rule(self.state_list[loc.world.id], spot=loc, age='child')):
                    had_reachable_locations = True
                    # Mark it visited for this algorithm
                    visited_locations.add(loc)
                    yield loc

    # This collects all item locations available in the state list given that
    # the states have collected items. The purpose is that it will search for
    # all new items that become accessible with a new item set.
    def collect_locations(self, item_locations: Optional[Iterable[Location]] = None) -> None:
        item_locations = item_locations or self.progression_locations()
        for location in self.iter_reachable_locations(item_locations):
            # Collect the item for the state world it is for
            self.collect(location.item)

    # A shorthand way to iterate over locations without collecting items.
    def visit_locations(self, locations: Optional[Iterable[Location]] = None) -> None:
        locations = locations or self.progression_locations()
        for _ in self.iter_reachable_locations(locations):
            pass

    # Retrieve all item locations in the worlds that have progression items
    def progression_locations(self) -> list[Location]:
        return [location for state in self.state_list for location in state.world.get_locations() if location.item and location.item.advancement]

    # This returns True if every state is beatable. It's important to ensure
    # all states beatable since items required in one world can be in another.
    # A state is beatable if it can ever collect the Triforce.
    # If scan_for_items is True, constructs and modifies a copy of the underlying
    # state to determine beatability; otherwise, only checks that the search
    # has already acquired all the Triforces.
    #
    # The above comment was specifically for collecting the triforce. Other win
    # conditions are possible, such as in Triforce Hunt, where only the total
    # amount of an item across all worlds matter, not specifcally who has it
    #
    # predicate must be a function (state) -> bool, that will be applied to all states
    def can_beat_game(self, scan_for_items: bool = True, predicate: Callable[[State], bool] = State.won) -> bool:
        # Check if already beaten
        if all(map(predicate, self.state_list)):
            return True

        if scan_for_items:
            # collect all available items
            # make a new search since we might be iterating over one already
            search = self.copy()
            search.collect_locations()
            # if every state got the Triforce, then return True
            return all(map(predicate, search.state_list))
        else:
            return False

    def beatable_goals_fast(self, goal_categories: dict[str, GoalCategory], world_filter: Optional[int] = None) -> ValidGoals:
        valid_goals = self.test_category_goals(goal_categories, world_filter)
        if all(map(State.won, self.state_list)):
            valid_goals['way of the hero'] = True
        else:
            valid_goals['way of the hero'] = False
        return valid_goals

    def beatable_goals(self, goal_categories: dict[str, GoalCategory]) -> ValidGoals:
        # collect all available items
        # make a new search since we might be iterating over one already
        search = self.copy()
        search.collect_locations()
        valid_goals = search.test_category_goals(goal_categories)
        if all(map(State.won, search.state_list)):
            valid_goals['way of the hero'] = True
        else:
            valid_goals['way of the hero'] = False
        return valid_goals

    def test_category_goals(self, goal_categories: dict[str, GoalCategory], world_filter: Optional[int] = None) -> ValidGoals:
        valid_goals: ValidGoals = {}
        for category_name, category in goal_categories.items():
            valid_goals[category_name] = {}
            valid_goals[category_name]['stateReverse'] = {}
            for state in self.state_list:
                # Must explicitly test for None as the world filter can be 0
                # for the first world ID
                # Skips item search when an entrance lock is active to avoid
                # mixing accessible goals with/without the entrance lock in
                # multiworld
                if world_filter is not None and state.world.id != world_filter:
                    continue
                valid_goals[category_name]['stateReverse'][state.world.id] = []
                world_category = state.world.goal_categories.get(category_name, None)
                if world_category is None:
                    continue
                for goal in world_category.goals:
                    if goal.name not in valid_goals[category_name]:
                        valid_goals[category_name][goal.name] = []
                    # Check if already beaten
                    if all(map(lambda i: state.has_full_item_goal(world_category, goal, i), goal.items)):
                        valid_goals[category_name][goal.name].append(state.world.id)
                        # Reverse lookup for checking if the category is already beaten.
                        # Only used to check if starting items satisfy the category.
                        valid_goals[category_name]['stateReverse'][state.world.id].append(goal.name)
        return valid_goals

    def iter_pseudo_starting_locations(self) -> Iterable[Location]:
        for state in self.state_list:
            for location in state.world.distribution.skipped_locations:
                # We need to use the locations in the current world
                location = state.world.get_location(location.name)
                self._cache.visited_locations.add(location)
                yield location

    def collect_pseudo_starting_items(self) -> None:
        for location in self.iter_pseudo_starting_locations():
            if location.item and location.item.solver_id is not None:
                self.collect(location.item)

    # Use the cache in the search to determine region reachability.
    # Implicitly requires is_starting_age or Time_Travel.
    def can_reach(self, region: Region, age: Optional[str] = None, tod: int = TimeOfDay.NONE) -> bool:
        if age == 'adult':
            if tod:
                return region in self._cache.adult_regions and (self._cache.adult_regions[region] & tod or self._expand_tod_regions(self._cache.adult_regions, region, age, tod))
            else:
                return region in self._cache.adult_regions
        elif age == 'child':
            if tod:
                return region in self._cache.child_regions and (self._cache.child_regions[region] & tod or self._expand_tod_regions(self._cache.child_regions, region, age, tod))
            else:
                return region in self._cache.child_regions
        elif age == 'both':
            return self.can_reach(region, age='adult', tod=tod) and self.can_reach(region, age='child', tod=tod)
        else:
            # treat None as either
            return self.can_reach(region, age='adult', tod=tod) or self.can_reach(region, age='child', tod=tod)

    def can_reach_spot(self, state: State, location_name: str, age: Optional[str] = None, tod: int = TimeOfDay.NONE) -> bool:
        location = state.world.get_location(location_name)
        return self.spot_access(location, age, tod)

    # Use the cache in the search to determine location reachability.
    # Only works for locations that had progression items...
    def visited(self, location: Location) -> bool:
        return location in self._cache.visited_locations

    # Use the cache in the search to get all reachable regions.
    def reachable_regions(self, age: Optional[str] = None) -> set[Region]:
        if age == 'adult':
            return set(self._cache.adult_regions.keys())
        elif age == 'child':
            return set(self._cache.child_regions.keys())
        else:
            return set(self._cache.adult_regions.keys()).union(self._cache.child_regions.keys())

    # Returns whether the given age can access the spot at this age and tod,
    # by checking whether the search has reached the containing region, and evaluating the spot's access rule.
    def spot_access(self, spot: Location | Entrance, age: Optional[str] = None, tod: int = TimeOfDay.NONE) -> bool:
        if age == 'adult' or age == 'child':
            return (self.can_reach(spot.parent_region, age=age, tod=tod)
                    and spot.access_rule(self.state_list[spot.world.id], spot=spot, age=age, tod=tod))
        elif age == 'both':
            return (self.can_reach(spot.parent_region, age=age, tod=tod)
                    and spot.access_rule(self.state_list[spot.world.id], spot=spot, age='adult', tod=tod)
                    and spot.access_rule(self.state_list[spot.world.id], spot=spot, age='child', tod=tod))
        else:
            return (self.can_reach(spot.parent_region, age='adult', tod=tod)
                    and spot.access_rule(self.state_list[spot.world.id], spot=spot, age='adult', tod=tod)) or (
                            self.can_reach(spot.parent_region, age='child', tod=tod)
                            and spot.access_rule(self.state_list[spot.world.id], spot=spot, age='child', tod=tod))


class RewindableSearch(Search):
    def unvisit(self, location: Location) -> None:
        # A location being unvisited is either:
        # in the top two caches (if it's the first being unvisited for a sphere)
        # in the topmost cache only (otherwise)
        # After we unvisit every location in a sphere, the top two caches have identical visited locations.
        assert location in self.cached_spheres[-1].visited_locations
        if location in self.cached_spheres[-2].visited_locations:
            self.cached_spheres.pop()
            self._cache = self.cached_spheres[-1]
        self._cache.visited_locations.discard(location)

    def reset(self) -> None:
        self._cache = self.cached_spheres[0]
        self.cached_spheres[1:] = []

    # Adds a new layer to the sphere cache, as a copy of the previous.
    def checkpoint(self) -> None:
        # Save the current data into the cache.
        self.cached_spheres.append(self._cache.copy())
        self._cache = self.cached_spheres[-1]
