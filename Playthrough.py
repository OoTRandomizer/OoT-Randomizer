import copy
from collections import deque, defaultdict
import itertools


class Playthrough(object):

    def __init__(self, state_list):
        self.state_list = state_list  # reference, not a copy
        # Each cached sphere is a dict with 4 values:
        #  child_regions, adult_regions: sets of Region, all the regions in that sphere
        #  child_queue, adult_queue: queue of Entrance, all the exits to try next sphere
        self.cached_spheres = []

        # Mapping from location to sphere index. 0-based.
        self.location_in_sphere = defaultdict(int)

    # Truncates the sphere cache based on which sphere a location is in.
    # Doesn't forget which sphere locations are in as an optimization, so be careful
    # to only uncollect locations in descending sphere order, or locations that
    # have been revisited in the most recent iteration.
    # Locations never visited in this Playthrough are assumed to be in sphere 0, so
    # uncollecting them will discard everything above sphere 0.
    # Not safe to call during iteration.
    def uncollect(self, location):
        self.cached_spheres[self.location_in_sphere[location]+1:] = []

    # Internal to the iteration. Modifies the exit_queue, region_set,
    # and may modify those for cross_age. Returns a queue of the exits
    # whose access rule failed, as a cache for the exits to try on the next iteration.
    @staticmethod
    def _expand_regions(exit_queue, region_set, validate,
                        cross_age_queue, cross_age_set):
        new_exit = lambda exit: exit.connected_region != None and exit.connected_region not in region_set
        failed = []
        while exit_queue:
            exit = exit_queue.popleft()
            if new_exit(exit):
                if validate(exit):
                    region_set.add(exit.connected_region)
                    exit_queue.extend(filter(new_exit, exit.connected_region.exits))
                    # This will put all accessible cross-age regions into the current sphere,
                    # but for child->adult, the state will not yet have Master Sword,
                    # so adult locations will not yet be accessible.
                    if exit.connected_region.name == 'Beyond Door of Time':
                        cross_age_set.add(exit.connected_region)
                        cross_age_queue.extend(exit.connected_region.exits)
                        # Adult savewarp point is Temple of Time, which is
                        # always accessible from BDoT, so we can skip adding it specially
                        # Child savewarp point is Links House, which is
                        # always accessible from BDoT -> ToT -> CT -> HF -> LWB -> KF, so we can skip adding it specially
                else:
                    failed.append(exit)
        return failed


    # Yields every reachable location, by iteratively deepening explored sets of
    # regions (one as child, one as adult) and invoking access rules without
    # calling a recursive form of can_reach.
    # item_locations is a list of Location objects from state_list that the caller
    # has prefiltered (eg. by whether they contain advancement items).
    #
    # Inside the loop, the caller usually wants to collect items at these
    # locations to see if the game is beatable.
    # This function does not alter provided state.
    def iter_reachable_locations(self, item_locations):
        # Set keeps track of collected locations, not for iteration.
        collected_set = set(itertools.chain.from_iterable(
            map(state.world.get_location, state.collected_locations)
            for id, state in enumerate(self.state_list)))

        new_child_exit = lambda exit: exit.connected_region not in child_regions
        new_adult_exit = lambda exit: exit.connected_region not in adult_regions

        # simplified exit.can_reach(state), with_age bypasses can_become_age
        # which we've already accounted for
        validate_child = lambda exit: self.state_list[exit.parent_region.world.id].with_age(lambda state: exit.can_reach(state, noparent=True), 'child')
        validate_adult = lambda exit: self.state_list[exit.parent_region.world.id].with_age(lambda state: exit.can_reach(state, noparent=True), 'adult')

        accessible = lambda loc: (
            loc not in collected_set
            and not loc.is_disabled()
            # Check adult first; it's the most likely.
            and (loc.parent_region in adult_regions
                 and self.state_list[loc.world.id].with_age(lambda state: loc.can_reach(state, noparent=True), 'adult')
                 or (loc.parent_region in child_regions
                     and self.state_list[loc.world.id].with_age(lambda state: loc.can_reach(state, noparent=True), 'child'))))

        had_reachable_locations = True
        # will loop as long as any collections were made, and at least once
        while had_reachable_locations:
            # 0. Use cached regions and queues or initialize starting values.
            if self.cached_spheres:
                child_regions = copy.copy(self.cached_spheres[-1]['child_regions'])
                adult_regions = copy.copy(self.cached_spheres[-1]['adult_regions'])
                # queues of Entrance where the entrance is not yet validated
                child_queue = copy.copy(self.cached_spheres[-1]['child_queue'])
                adult_queue = copy.copy(self.cached_spheres[-1]['adult_queue'])
            else:
                child_starting_regions = [
                        state.world.get_region('Links House') for state in self.state_list
                        if state.world.starting_age == 'child']
                adult_starting_regions = [
                        state.world.get_region('Temple of Time') for state in self.state_list
                        if state.world.starting_age == 'adult']
                child_queue = deque(exit for region in child_starting_regions for exit in region.exits)
                adult_queue = deque(exit for region in adult_starting_regions for exit in region.exits)
                child_regions = set(child_starting_regions)
                adult_regions = set(adult_starting_regions)

            # 1. Use the queue to iteratively add regions to the accessed set,
            #    until we are stuck or out of regions.
            adult_failed = Playthrough._expand_regions(
                    adult_queue, adult_regions, validate_adult,
                    child_queue, child_regions)
            child_failed = Playthrough._expand_regions(
                    child_queue, child_regions, validate_child,
                    adult_queue, adult_regions)
            # If child reached BDoT, we'll have added BDoT for adult.
            # We always have to expand again before checking locations,
            # since we could have collected all in child before running this.
            if adult_queue:
                adult_failed.extend(Playthrough._expand_regions(
                        adult_queue, adult_regions, validate_adult,
                        child_failed, child_regions))

            # 2. Get all locations in accessible_regions that aren't collected,
            #    and check if they can be reached. Collect them.
            reachable_locations = filter(accessible, item_locations)
            had_reachable_locations = False
            for location in reachable_locations:
                had_reachable_locations = True
                yield location
                # Mark it collected for this algorithm
                collected_set.add(location)
                self.location_in_sphere[location] = len(self.cached_spheres)
            # 3. Save the current data into the cache.
            self.cached_spheres.append({
                'child_regions': child_regions,
                'adult_regions': adult_regions,
                # Exits that didn't pass validation (and still point to new places)
                # are the only exits we'll be interested in
                'child_queue': deque(filter(new_child_exit, child_failed)),
                'adult_queue': deque(filter(new_adult_exit, adult_failed)),
            })

    # This collects all item locations available in the state list given that
    # the states have collected items. The purpose is that it will search for
    # all new items that become accessible with a new item set.
    # This function modifies provided state.
    def collect_locations(self):
        # Get all item locations in the worlds
        item_locations = [location for state in self.state_list for location in state.world.get_filled_locations() if location.item.advancement]
        collected_locations = [s.collected_locations for s in self.state_list]
        for location in self.iter_reachable_locations(item_locations):
            # Mark the location collected in the state world it exists in
            collected_locations[location.world.id][location.name] = True
            # Collect the item for the state world it is for
            self.state_list[location.item.world.id].collect(location.item)

    # This returns True if every state is beatable. It's important to ensure
    # all states beatable since items required in one world can be in another.
    def can_beat_game(self, scan_for_items=True):
        if scan_for_items:
            # Check if already beaten
            game_beaten = True
            for state in self.state_list:
                if not state.has('Triforce'):
                    game_beaten = False
                    break
            if game_beaten:
                return True

            # collect all available items
            # make a new playthrough since we might be iterating over one already
            playthrough = Playthrough([state.copy() for state in self.state_list])
            # we only need to copy the top sphere since that's what we're starting with and we don't go back
            if self.cached_spheres:
                playthrough.cached_spheres = [{k: copy.copy(v) for k,v in self.cached_spheres[-1].items()}]
            playthrough.collect_locations()
        else:
            playthrough = self

        # if the every state got the Triforce, then return True
        for state in playthrough.state_list:
            if not state.has('Triforce'):
                return False
        return True

