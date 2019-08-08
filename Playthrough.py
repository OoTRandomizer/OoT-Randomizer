import copy
from collections import defaultdict
import itertools


class Playthrough(object):

    def __init__(self, state_list, cached_spheres=None):
        self.state_list = [state.copy() for state in state_list]
        # Each cached sphere is a dict with 5 values:
        #  child_regions, adult_regions: sets of Region, all the regions in that sphere
        #  child_queue, adult_queue: queue of Entrance, all the exits to try next sphere
        #  visited_locations: set of Locations visited in or before that sphere.
        self.cached_spheres = cached_spheres or []

        # Mapping from location to sphere index. 0-based.
        self.location_in_sphere = defaultdict(int)
        # Mapping from item to sphere index, if this is tracking items. 0-based.
        self.item_in_sphere = defaultdict(int)

        # Let the states reference this playthrough.
        for state in self.state_list:
            state.playthrough = self

        # Prefill sphere 0 if not already filled.
        if not self.cached_spheres:
            self.next_sphere()


    def copy(self):
        # we only need to copy the top sphere since that's what we're starting with and we don't go back
        new_cache = [{k: copy.copy(v) for k,v in self.cached_spheres[-1].items()}]
        return Playthrough(self.state_list, new_cache)


    def collect_all(self, itempool):
        for item in itempool:
            self.item_in_sphere[item] = len(self.cached_spheres)
            self.state_list[item.world.id].collect(item)


    def collect(self, item):
        self.item_in_sphere[item] = len(self.cached_spheres)
        self.state_list[item.world.id].collect(item)


    @staticmethod
    def max_explore(state_list, itempool=None):
        p = Playthrough(state_list)
        if itempool:
            p.collect_all(itempool)
        p.collect_locations()
        return p

    @staticmethod
    def with_items(state_list, itempool=None):
        p = Playthrough(state_list)
        if itempool:
            p.collect_all(itempool)
        p.next_sphere()
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
        if self.cached_spheres:
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


    # simplified exit.can_reach(state), bypasses can_become_age
    # which we've already accounted for
    def validate_child(self, exit):
        return self.state_list[exit.parent_region.world.id].with_age(
                exit.can_reach_simple, adult=False)

    def validate_adult(self, exit):
        return self.state_list[exit.parent_region.world.id].with_age(
                exit.can_reach_simple, adult=True)


    # Internal to the iteration. Modifies the exit_queue, region_set. 
    # Returns a queue of the exits whose access rule failed, 
    # as a cache for the exits to try on the next iteration.
    @staticmethod
    def _expand_regions(exit_queue, region_set, validate):
        failed = []
        for exit in exit_queue:
            if exit.connected_region and exit.connected_region not in region_set:
                if validate(exit):
                    region_set.add(exit.connected_region)
                    exit_queue.extend(exit.connected_region.exits)
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
            child_queue = list(exit for region in root_regions for exit in region.exits)
            adult_queue = list(exit for region in root_regions for exit in region.exits)
            child_regions = set(root_regions)
            adult_regions = set(root_regions)
            visited_locations = set()

        # Use the queue to iteratively add regions to the accessed set,
        # until we are stuck or out of regions.
        adult_failed = Playthrough._expand_regions(adult_queue, adult_regions, self.validate_adult)
        child_failed = Playthrough._expand_regions(child_queue, child_regions, self.validate_child)

        # Save the current data into the cache.
        self.cached_spheres.append({
            'child_regions': child_regions,
            'adult_regions': adult_regions,
            # Didn't change here, but this will be the editable layer of the cache.
            'visited_locations': visited_locations,
            # Exits that didn't pass validation
            # are the only exits we'll be interested in
            'child_queue': child_failed,
            'adult_queue': adult_failed,
        })
        return child_regions, adult_regions, visited_locations

    # Yields every reachable location, by iteratively deepening explored sets of
    # regions (one as child, one as adult) and invoking access rules.
    # item_locations is a list of Location objects from state_list that the caller
    # has prefiltered (eg. by whether they contain advancement items).
    #
    # Inside the loop, the caller usually wants to collect items at these
    # locations to see if the game is beatable. Collection should be done
    # using internal State (recommended to just call playthrough.collect).
    def iter_reachable_locations(self, item_locations):
        # tests reachability, skipping recursive can_reach region check
        def accessible(loc):
            return (loc not in visited_locations
                    # Check adult first; it's the most likely.
                    and (loc.parent_region in adult_regions
                         and self.state_list[loc.world.id].with_age(loc.can_reach_simple, adult=True)
                     or (loc.parent_region in child_regions
                         and self.state_list[loc.world.id].with_age(loc.can_reach_simple, adult=False))))


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
    def collect_locations(self, item_locations=None):
        item_locations = item_locations or self.progression_locations()
        for location in self.iter_reachable_locations(item_locations):
            # Collect the item for the state world it is for
            self.collect(location.item)

    # A shorthand way to iterate over locations without collecting items.
    def visit_locations(self, locations=None):
        locations = locations or self.progression_locations()
        for _ in self.iter_reachable_locations(locations):
            pass

    # Retrieve all item locations in the worlds that have progression items
    def progression_locations(self):
        return [location for state in self.state_list for location in state.world.get_filled_locations() if location.item.advancement]


    # This returns True if every state is beatable. It's important to ensure
    # all states beatable since items required in one world can be in another.
    # A state is beatable if it can ever collect the Triforce.
    # If scan_for_items is True, constructs and modifies a copy of the underlying
    # state to determine beatability; otherwise, only checks that the playthrough
    # has already acquired all the Triforces.
    def can_beat_game(self, scan_for_items=True):
        def won(state):
            return state.has('Triforce')

        # Check if already beaten
        if all(map(won, self.state_list)):
            return True

        if scan_for_items:
            # collect all available items
            # make a new playthrough since we might be iterating over one already
            playthrough = self.copy()
            playthrough.collect_locations()
            # if every state got the Triforce, then return True
            return all(map(won, playthrough.state_list))
        else:
            return False


    # Use the cache in the playthrough to determine region reachability.
    def can_reach(self, region, age=None):
        if not self.cached_spheres: return False
        if age == 'adult':
            return region in self.cached_spheres[-1]['adult_regions']
        elif age == 'child':
            return region in self.cached_spheres[-1]['child_regions']
        elif age == 'both':
            return region in self.cached_spheres[-1]['adult_regions'] and region in self.cached_spheres[-1]['child_regions']
        else:
            # treat None as either
            return region in self.cached_spheres[-1]['adult_regions'] or region in self.cached_spheres[-1]['child_regions']

    # Use the cache in the playthrough to determine location reachability.
    # Only works for locations that had progression items...
    def visited(self, location):
        return location in self.cached_spheres[-1]['visited_locations']

    # Use the cache in the playthrough to get all reachable regions.
    def reachable_regions(self, age=None):
        if age == 'adult':
            return self.cached_spheres[-1]['adult_regions']
        elif age == 'child':
            return self.cached_spheres[-1]['child_regions']
        else:
            return self.cached_spheres[-1]['adult_regions'] + self.cached_spheres[-1]['child_regions']
