import copy
from collections import deque, defaultdict
import itertools


class Playthrough(object):

    def __init__(self, state_list, cached_spheres=None):
        self.state_list = state_list  # reference, not a copy
        # Each cached sphere is a dict with 5 values:
        #  child_regions, adult_regions: sets of Region, all the regions in that sphere
        #  child_queue, adult_queue: queue of Entrance, all the exits to try next sphere
        #  visited_locations: set of Locations visited in or before that sphere.
        self.cached_spheres = cached_spheres or []

        # Mapping from location to sphere index. 0-based.
        self.location_in_sphere = defaultdict(int)
        # Mapping from item to sphere index, if this is tracking items. 0-based.
        self.item_in_sphere = defaultdict(int)

        # Prefill sphere 0 if not already filled.
        if not self.cached_spheres:
            self.next_sphere()

        # Let the states reference this playthrough.
        for state in self.state_list:
            state.playthrough = self


    def copy(self):
        new_state_list = [state.copy() for state in self.state_list]
        # we only need to copy the top sphere since that's what we're starting with and we don't go back
        new_cache = [{k: copy.copy(v) for k,v in self.cached_spheres[-1].items()}]
        return Playthrough(new_state_list, new_cache)


    def collect_all(self, itempool):
        for item in itempool:
            self.item_in_sphere[item] = len(self.cached_spheres)
            self.state_list[item.world.id].collect(item)


    def collect(self, item):
        self.item_in_sphere[item] = len(self.cached_spheres)
        self.state_list[item.world.id].collect(item)


    @staticmethod
    def max_explore(state_list, itempool=None):
        p = Playthrough([s.copy() for s in state_list])
        if itempool:
            p.collect_all(itempool)
        p.collect_locations()
        return p

    # Truncates the sphere cache based on which sphere a location is in, and
    # drops the location from the appropriate visited set.
    # Doesn't forget which sphere locations are in as an optimization, so be careful
    # to only unvisit locations in descending sphere order, or locations that
    # have been revisited in the most recent iteration.
    # Locations never visited in this Playthrough are assumed to have been visited
    # in sphere 0, so unvisiting them will discard the entire cache.
    # Not safe to call during iteration.
    def unvisit(self, location):
        self.cached_spheres[self.location_in_sphere[location]+1:] = []
        self.cached_spheres[-1]['visited_locations'].discard(location)


    # Drops the item from its respective state, and truncates the sphere cache
    # based on which sphere an item was in.
    # Does *not* uncollect any other items in or above that sphere!
    # Doesn't forget which sphere items are in as an optimization, so be careful
    # to only uncollect items in descending sphere order, or only track collected
    # items in one sphere.
    # Items not collected in this Playthrough are assumed to have been collected
    # prior to sphere 0, so uncollecting them will discard the entire cache.
    # Not safe to call during iteration.
    def uncollect(self, item):
        self.state_list[item.world.id].remove(item)
        self.cached_spheres[self.item_in_sphere[item]:] = []

    # Resets the sphere cache to the first entry only.
    # Does not uncollect any items!
    # Not safe to call during iteration.
    def reset(self):
        self.cached_spheres[1:] = []
        self.cached_spheres[0]['visited_locations'].clear()
        self.location_in_sphere.clear()
        self.item_in_sphere.clear()


    # simplified exit.can_reach(state), with_age bypasses can_become_age
    # which we've already accounted for
    def validate_child(self, exit):
        return self.state_list[exit.parent_region.world.id].with_age(
                lambda state: exit.can_reach(state, noparent=True), 'child')

    def validate_adult(self, exit):
        return self.state_list[exit.parent_region.world.id].with_age(
                lambda state: exit.can_reach(state, noparent=True), 'adult')


    # Internal to the iteration. Modifies the exit_queue, region_set. 
    # Returns a queue of the exits whose access rule failed, 
    # as a cache for the exits to try on the next iteration.
    @staticmethod
    def _expand_regions(exit_queue, region_set, validate):
        new_exit = lambda exit: exit.connected_region != None and exit.connected_region not in region_set
        failed = []
        while exit_queue:
            exit = exit_queue.popleft()
            if new_exit(exit):
                if validate(exit):
                    region_set.add(exit.connected_region)
                    exit_queue.extend(filter(new_exit, exit.connected_region.exits))
                else:
                    failed.append(exit)
        return failed

    # Explores available exits, based on the most recent cache entry, and pushes
    # the result as a new entry in the cache.
    # Returns the set of regions accessible in the new sphere as child,
    # the set of regions accessible as adult, and the set of visited locations.
    # These are references to the new entry in the cache, so they can be modified
    # directly (likely only useful for visited_locations).
    def next_sphere(self):
        # Use cached regions and queues or initialize starting values.
        if self.cached_spheres:
            child_regions = copy.copy(self.cached_spheres[-1]['child_regions'])
            adult_regions = copy.copy(self.cached_spheres[-1]['adult_regions'])
            # queues of Entrance where the entrance is not yet validated
            child_queue = copy.copy(self.cached_spheres[-1]['child_queue'])
            adult_queue = copy.copy(self.cached_spheres[-1]['adult_queue'])
            # Locations already visited
            visited_locations = copy.copy(self.cached_spheres[-1]['visited_locations'])
        else:
            root_regions = [state.world.get_region('Root') for state in self.state_list]
            child_queue = deque(exit for region in root_regions for exit in region.exits)
            adult_queue = deque(exit for region in root_regions for exit in region.exits)
            child_regions = set(root_regions)
            adult_regions = set(root_regions)
            visited_locations = set()

        # Use the queue to iteratively add regions to the accessed set,
        # until we are stuck or out of regions.
        adult_failed = Playthrough._expand_regions(adult_queue, adult_regions, self.validate_adult)
        child_failed = Playthrough._expand_regions(child_queue, child_regions, self.validate_child)

        # Save the current data into the cache.
        new_child_exit = lambda exit: exit.connected_region not in child_regions
        new_adult_exit = lambda exit: exit.connected_region not in adult_regions

        self.cached_spheres.append({
            'child_regions': child_regions,
            'adult_regions': adult_regions,
            # Didn't change here, but this will be the editable layer of the cache.
            'visited_locations': visited_locations,
            # Exits that didn't pass validation (and still point to new places)
            # are the only exits we'll be interested in
            'child_queue': deque(filter(new_child_exit, child_failed)),
            'adult_queue': deque(filter(new_adult_exit, adult_failed)),
        })
        return child_regions, adult_regions, visited_locations

    # Yields every reachable location, by iteratively deepening explored sets of
    # regions (one as child, one as adult) and invoking access rules.
    # item_locations is a list of Location objects from state_list that the caller
    # has prefiltered (eg. by whether they contain advancement items).
    #
    # Inside the loop, the caller usually wants to collect items at these
    # locations to see if the game is beatable.
    # This function does not alter provided state.
    def iter_reachable_locations(self, item_locations):
        # tests reachability, skipping recursive can_reach region check
        def accessible(loc):
            return (loc not in visited_locations
                    and not loc.is_disabled()
                    # Check adult first; it's the most likely.
                    and (loc.parent_region in adult_regions
                         and self.state_list[loc.world.id].with_age(lambda state: loc.can_reach(state, noparent=True), 'adult')
                     or (loc.parent_region in child_regions
                         and self.state_list[loc.world.id].with_age(lambda state: loc.can_reach(state, noparent=True), 'child'))))


        had_reachable_locations = True
        # will loop as long as any visits were made, and at least once
        while had_reachable_locations:
            child_regions, adult_regions, visited_locations = self.next_sphere()

            # Get all locations in accessible_regions that aren't visited,
            # and check if they can be reached. Collect them.
            reachable_locations = filter(accessible, item_locations)
            had_reachable_locations = False
            for location in reachable_locations:
                had_reachable_locations = True
                # Mark it visited for this algorithm
                visited_locations.add(location)
                self.location_in_sphere[location] = len(self.cached_spheres) - 1
                yield location


    # This collects all item locations available in the state list given that
    # the states have collected items. The purpose is that it will search for
    # all new items that become accessible with a new item set.
    # This function modifies provided state.
    def collect_locations(self, item_locations=None):
        # Get all item locations in the worlds that have progression items
        item_locations = item_locations or [location for state in self.state_list for location in state.world.get_filled_locations() if location.item.advancement]
        for location in self.iter_reachable_locations(item_locations):
            # Collect the item for the state world it is for
            self.collect(location.item)

    # A shorthand way to iterate over locations without collecting items.
    def visit_locations(self, locations):
        for _ in self.iter_reachable_locations(locations):
            pass


    # This returns True if every state is beatable. It's important to ensure
    # all states beatable since items required in one world can be in another.
    # A state is beatable if it can ever collect the Triforce.
    # If scan_for_items is True, constructs and modifies a copy of the underlying
    # state to determine beatability; otherwise, only checks that the playthrough
    # has already acquired all the Triforces.
    def can_beat_game(self, scan_for_items=True):
        def won(state):
            return state.has('Triforce')

        if scan_for_items:
            # Check if already beaten
            if all(map(won, self.state_list)):
                return True

            # collect all available items
            # make a new playthrough since we might be iterating over one already
            playthrough = self.copy()
            playthrough.collect_locations()
        else:
            playthrough = self

        # if every state got the Triforce, then return True
        return all(map(won, playthrough.state_list))


    # Use the cache in the playthrough to determine region reachability.
    def can_reach(self, region, age=None):
        if age == 'adult':
            return region in self.cached_spheres[-1]['adult_regions']
        elif age == 'child':
            return region in self.cached_spheres[-1]['child_regions']
        elif age == 'both':
            return region in self.cached_spheres[-1]['adult_regions'] and region in self.cached_spheres[-1]['child_regions']
        else:
            # treat None as either
            return region in self.cached_spheres[-1]['adult_regions'] and region in self.cached_spheres[-1]['child_regions']

    # Use the cache in the playthrough to determine location reachability.
    # Only works for locations that had progression items...
    def visited(self, location):
        return location in self.cached_spheres[-1]['visited_locations']
