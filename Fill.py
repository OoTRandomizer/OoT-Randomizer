import random
import logging
from State import State
from Rules import set_shop_rules
from Location import DisableType
from ItemPool import songlist, get_junk_item
from Item import ItemFactory


class FillError(RuntimeError):
    pass


# Places all items into the world
def distribute_items_restrictive(window, worlds, fill_locations=None):
    song_locations = [world.get_location(location) for world in worlds for location in
        ['Song from Composer Grave', 'Impa at Castle', 'Song from Malon', 'Song from Saria',
        'Song from Ocarina of Time', 'Song at Windmill', 'Sheik Forest Song', 'Sheik at Temple',
        'Sheik in Crater', 'Sheik in Ice Cavern', 'Sheik in Kakariko', 'Sheik at Colossus']]

    shop_locations = [location for world in worlds for location in world.get_unfilled_locations() if location.type == 'Shop' and location.price == None]

    # If not passed in, then get a shuffled list of locations to fill in
    if not fill_locations:
        fill_locations = [location for world in worlds for location in world.get_unfilled_locations() \
            if location not in song_locations and \
               location not in shop_locations and \
               location.type != 'GossipStone']
    world_states = [world.state for world in worlds]

    window.locationcount = len(fill_locations) + len(song_locations) + len(shop_locations)
    window.fillcount = 0

    # Generate the itempools
    shopitempool = [item for world in worlds for item in world.itempool if item.type == 'Shop']
    songitempool = [item for world in worlds for item in world.itempool if item.type == 'Song']
    itempool =     [item for world in worlds for item in world.itempool if item.type != 'Shop' and item.type != 'Song']
    
    if worlds[0].shuffle_song_items:
        itempool.extend(songitempool)
        fill_locations.extend(song_locations)

    # add unrestricted dungeon items to main item pool
    itempool.extend([item for world in worlds for item in world.get_unrestricted_dungeon_items()])
    dungeon_items = [item for world in worlds for item in world.get_restricted_dungeon_items()]

    random.shuffle(itempool) # randomize item placement order. this ordering can greatly affect the location accessibility bias
    progitempool = [item for item in itempool if item.advancement]
    prioitempool = [item for item in itempool if not item.advancement and item.priority]
    restitempool = [item for item in itempool if not item.advancement and not item.priority]

    # set ice traps to have the appearance of other random items in the item pool
    ice_traps = [item for item in itempool if item.name == 'Ice Trap']
    fake_items = []
    while len(ice_traps) > len(fake_items):
        # if there are more ice traps than major items, then double up on major items
        fake_items.extend([item for item in itempool if item.majoritem])
    for random_item in random.sample(fake_items, len(ice_traps)):
        ice_trap = ice_traps.pop(0)
        ice_trap.looks_like_item = random_item

    # We place all the shop items first. Like songs, they have a more limited
    # set of locations that they can be placed in, so placing them first will
    # reduce the odds of creating unbeatable seeds. This also avoids needing
    # to create item rules for every location for whether they are a shop item
    # or not. This shouldn't have much affect on item bias.
    if shop_locations:
        fill_shops(window, worlds, shop_locations, shopitempool, itempool + songitempool + dungeon_items)
    # Update the shop item access rules
    for world in worlds:
        set_shop_rules(world)

    # If there are dungeon items that are restricted to their original dungeon,
    # we must place them first to make sure that there is always a location to
    # place them. This could probably be replaced for more intelligent item
    # placement, but will leave as is for now
    fill_dungeons_restrictive(window, worlds, fill_locations, dungeon_items, itempool + songitempool)

    # places the songs into the world
    # Currently places songs only at song locations. if there's an option
    # to allow at other locations then they should be in the main pool.
    # Placing songs on their own since they have a relatively high chance
    # of failing compared to other item type. So this way we only have retry
    # the song locations only.
    if not worlds[0].shuffle_song_items:
        fill_songs(window, worlds, song_locations, songitempool, progitempool)
        if worlds[0].start_with_fast_travel:
            fill_locations += [location for location in song_locations if location.item is None]

    # Put one item in every dungeon, needs to be done before other items are
    # placed to ensure there is a spot available for them
    if worlds[0].one_item_per_dungeon:
        fill_dungeon_unique_item(window, worlds, fill_locations, progitempool)

    # Place all progression items. This will include keys in keysanity.
    # Items in this group will check for reachability and will be placed
    # such that the game is guaranteed beatable.
    fill_restrictive(window, worlds, [world.state for world in worlds], fill_locations, progitempool)

    # Place all priority items.
    # These items are items that only check if the item is allowed to be
    # placed in the location, not checking reachability. This is important
    # for things like Ice Traps that can't be found at some locations
    fill_restrictive_fast(window, worlds, fill_locations, prioitempool)

    # Place the rest of the items.
    # No restrictions at all. Places them completely randomly. Since they
    # cannot affect the beatability, we don't need to check them
    fast_fill(window, fill_locations, restitempool)

    # Log unplaced item/location warnings
    for item in progitempool + prioitempool + restitempool:
        logging.getLogger('').error('Unplaced Items: %s [World %d]' % (item.name, item.world.id))
    for location in fill_locations:
        logging.getLogger('').error('Unfilled Locations: %s [World %d]' % (location.name, location.world.id))

    if progitempool + prioitempool + restitempool:
        raise FillError('Not all items are placed.')

    if fill_locations:
        raise FillError('Not all locations have an item.')

    if not State.can_beat_game(world_states, True):
        raise FillError('Cannot beat game!')

    # Get Light Arrow location for later usage.
    for world in worlds:
        for location in world.get_filled_locations():
            if location.item and location.item.name == 'Light Arrows':
                location.item.world.light_arrow_location = location


# Places restricted dungeon items into the worlds. To ensure there is room for them.
# they are placed first so it will assume all other items are reachable
def fill_dungeons_restrictive(window, worlds, shuffled_locations, dungeon_items, itempool):
    # List of states with all non-key items
    all_state_base_list = State.get_states_with_items([world.state for world in worlds], itempool)

    # shuffle this list to avoid placement bias
    random.shuffle(dungeon_items)

    # sort in the order Other, Small Key, Boss Key before placing dungeon items
    # python sort is stable, so the ordering is still random within groups
    # fill_restrictive processes the resulting list backwards so the Boss Keys will actually be placed first
    sort_order = {"BossKey": 3, "SmallKey": 2}
    dungeon_items.sort(key=lambda item: sort_order.get(item.type, 1))

    # place dungeon items
    fill_restrictive(window, worlds, all_state_base_list, shuffled_locations, dungeon_items)

    for world in worlds:
        world.state.clear_cached_unreachable()


# Places items into dungeon locations. This is used when there should be exactly
# one progression item per dungeon. This should be ran before all the progression
# items are places to ensure there is space to place them.
def fill_dungeon_unique_item(window, worlds, fill_locations, itempool):
    # We should make sure that we don't count event items, shop items,
    # token items, or dungeon items as a major item. itempool at this
    # point should only be able to have tokens of those restrictions
    # since the rest are already placed.
    major_items = [item for item in itempool if item.majoritem]
    minor_items = [item for item in itempool if not item.majoritem]

    dungeons = [dungeon for world in worlds for dungeon in world.dungeons]
    double_dungeons = []
    for dungeon in dungeons:
        # we will count spirit temple twice so that it gets 2 items to match vanilla
        if dungeon.name == 'Spirit Temple':
            double_dungeons.append(dungeon)
    dungeons.extend(double_dungeons)

    random.shuffle(dungeons)
    random.shuffle(itempool)

    all_other_item_state = State.get_states_with_items([world.state for world in worlds], minor_items)
    all_dungeon_locations = []

    # iterate of all the dungeons in a random order, placing the item there
    for dungeon in dungeons:
        dungeon_locations = [location for region in dungeon.regions for location in region.locations if location in fill_locations]
        if dungeon.name == 'Spirit Temple':
            # spirit temple is weird and includes a couple locations outside of the dungeon
            dungeon_locations.extend(filter(lambda location: location in fill_locations, [dungeon.world.get_location(location) for location in ['Mirror Shield Chest', 'Silver Gauntlets Chest']]))

        # cache this list to flag afterwards
        all_dungeon_locations.extend(dungeon_locations)

        # place 1 item into the dungeon
        fill_restrictive(window, worlds, all_other_item_state, dungeon_locations, major_items, 1)

        # update the location and item pool, removing any placed items and filled locations
        # the fact that you can remove items from a list you're iterating over is python magic
        for item in itempool:
            if item.location != None:
                fill_locations.remove(item.location)
                itempool.remove(item)

    # flag locations to not place further major items. it's important we do it on the
    # locations instead of the dungeon because some locations are not in the dungeon
    for location in all_dungeon_locations:
        location.minor_only = True

    logging.getLogger('').info("Unique dungeon items placed")


# Places the shop items into the world at the Shop locations
def fill_shops(window, worlds, locations, shoppool, itempool, attempts=15):
    # get the shop locations for each world

    # look for preplaced items
    placed_prizes = [loc.item.name for loc in locations if loc.item is not None]
    unplaced_prizes = [item for item in shoppool if item.name not in placed_prizes]
    empty_shop_locations = [loc for loc in locations if loc.item is None]

    prizepool_dict = {world.id: [item for item in unplaced_prizes if item.world.id == world.id] for world in worlds}
    prize_locs_dict = {world.id: [loc for loc in empty_shop_locations if loc.world.id == world.id] for world in worlds}

    # Shop item being sent in to this method are tied to their own world.
    # Therefore, let's do this one world at a time. We do this to help
    # increase the chances of successfully placing songs
    for world in worlds:
        # List of states with all items
        unplaced_prizes = [item for item in unplaced_prizes if item not in prizepool_dict[world.id]]
        all_state_base_list = State.get_states_with_items([world.state for world in worlds], itempool + unplaced_prizes)

        world_attempts = attempts
        while world_attempts:
            world_attempts -= 1
            try:
                prizepool = list(prizepool_dict[world.id])
                prize_locs = list(prize_locs_dict[world.id])
                random.shuffle(prizepool)
                fill_restrictive(window, worlds, all_state_base_list, prize_locs, prizepool)
                
                logging.getLogger('').info("Shop items placed for world %s", (world.id+1))
            except FillError as e:
                logging.getLogger('').info("Failed to place shop items for world %s. Will retry %s more times", (world.id+1), world_attempts)
                for location in prize_locs_dict[world.id]:
                    location.item = None
                    if location.disabled == DisableType.DISABLED:
                        location.disabled = DisableType.PENDING
                logging.getLogger('').info('\t%s' % str(e))
                continue
            break
        else:
            raise FillError('Unable to place shop items in world %d' % (world.id+1))


# Places the songs into the world at the Song locations
def fill_songs(window, worlds, locations, songpool, itempool, attempts=15):
    # get the song locations for each world

    # look for preplaced items
    placed_prizes = [loc.item.name for loc in locations if loc.item is not None]
    unplaced_prizes = [song for song in songpool if song.name not in placed_prizes]
    empty_song_locations = [loc for loc in locations if loc.item is None]

    prizepool_dict = {world.id: [song for song in unplaced_prizes if song.world.id == world.id] for world in worlds}
    prize_locs_dict = {world.id: [loc for loc in empty_song_locations if loc.world.id == world.id] for world in worlds}

    # Songs being sent in to this method are tied to their own world.
    # Therefore, let's do this one world at a time. We do this to help
    # increase the chances of successfully placing songs
    for world in worlds:
        # List of states with all items
        unplaced_prizes = [song for song in unplaced_prizes if song not in prizepool_dict[world.id]]
        all_state_base_list = State.get_states_with_items([world.state for world in worlds], itempool + unplaced_prizes)

        world_attempts = attempts
        while world_attempts:
            world_attempts -= 1
            try:
                prizepool = list(prizepool_dict[world.id])
                prize_locs = list(prize_locs_dict[world.id])
                random.shuffle(prizepool)
                fill_restrictive(window, worlds, all_state_base_list, prize_locs, prizepool)
                
                logging.getLogger('').info("Songs placed for world %s", (world.id+1))
            except FillError as e:
                logging.getLogger('').info("Failed to place songs for world %s. Will retry %s more times", (world.id+1), world_attempts)
                for location in prize_locs_dict[world.id]:
                    location.item = None
                    if location.disabled == DisableType.DISABLED:
                        location.disabled = DisableType.PENDING
                logging.getLogger('').info('\t%s' % str(e))
                continue
            break
        else:
            raise FillError('Unable to place songs in world %d' % (world.id+1))


# Places items in the itempool into locations.
# worlds is a list of worlds and is redundant of the worlds in the base_state_list
# base_state_list is a list of world states prior to placing items in the item pool
# items and locations have pointers to the world that they belong to
#
# The algorithm places items in the world in reverse.
# This means we first assume we have every item in the item pool and
# remove an item and try to place it somewhere that is still reachable
# This method helps distribution of items locked behind many requirements
#
# count is the number of items to place. If count is negative, then it will place
# every item. Raises an error if specified count of items are not placed.
#
# This function will modify the location and itempool arguments. placed items and
# filled locations will be removed. If this returns and error, then the state of
# those two lists cannot be guaranteed.
def fill_restrictive(window, worlds, base_state_list, locations, itempool, count=-1):
    unplaced_items = []

    # loop until there are no items or locations
    while itempool and locations:
        # if remaining count is 0, return. Negative means unbounded.
        if count == 0:
            break

        # get and item and remove it from the itempool
        item_to_place = itempool.pop()
        random.shuffle(locations)

        # generate the max states that include every remaining item
        # this will allow us to place this item in a reachable location
        maximum_exploration_state_list = State.get_states_with_items(base_state_list, itempool + unplaced_items)

        # perform_access_check checks location reachability
        perform_access_check = True
        if worlds[0].check_beatable_only:
            # if any world can not longer be beatable with the remaining items
            # then we must check for reachability no matter what.
            # This way the reachability test is monotonic. If we were to later
            # stop checking, then we could place an item needed in one world
            # in an unreachable place in another world
            perform_access_check = not State.can_beat_game(maximum_exploration_state_list)

        # find a location that the item can be places. It must be a valid location
        # in the world we are placing it (possibly checking for reachability)
        spot_to_fill = None
        for location in locations:
            if location.can_fill(maximum_exploration_state_list[location.world.id], item_to_place, perform_access_check):
                # for multiworld, make it so that the location is also reachable
                # in the world the item is for. This is to prevent early restrictions
                # in one world being placed late in another world. If this is not
                # done then one player may be waiting a long time for other players.
                if location.world.id != item_to_place.world.id:
                    try:
                        source_location = item_to_place.world.get_location(location.name)
                        if not source_location.can_fill(maximum_exploration_state_list[item_to_place.world.id], item_to_place, perform_access_check):
                            # location wasn't reachable in item's world, so skip it
                            continue
                    except KeyError:
                        # This location doesn't exist in the other world, let's look elsewhere.
                        # Check access to whatever parent region exists in the other world.
                        can_reach = True
                        parent_region = location.parent_region
                        while parent_region:
                            try:
                                source_region = item_to_place.world.get_region(parent_region.name)
                                can_reach = source_region.can_reach(maximum_exploration_state_list[item_to_place.world.id])
                                break
                            except KeyError:
                                parent_region = parent_region.entrances[0].parent_region
                        if not can_reach:
                            continue

                if location.disabled == DisableType.PENDING:
                    if not State.can_beat_game(maximum_exploration_state_list):
                        continue
                    location.disabled = DisableType.DISABLED

                # location is reachable (and reachable in item's world), so place item here
                spot_to_fill = location
                break

        # if we failed to find a suitable location
        if spot_to_fill is None:
            # if we specify a count, then we only want to place a subset, so a miss might be ok
            if count > 0:
                # don't decrement count, we didn't place anything
                unplaced_items.append(item_to_place)
                continue
            else:
                # we expect all items to be placed
                raise FillError('Game unbeatable: No more spots to place %s [World %d]' % (item_to_place, item_to_place.world.id))

        # Place the item in the world and continue
        spot_to_fill.world.push_item(spot_to_fill, item_to_place)
        locations.remove(spot_to_fill)
        window.fillcount += 1
        window.update_progress(5 + ((window.fillcount / window.locationcount) * 30))

        # decrement count
        count -= 1

    # assert that the specified number of items were placed
    if count > 0:
        raise FillError('Could not place the specified number of item. %d remaining to be placed.' % count)
    # re-add unplaced items that were skipped
    itempool.extend(unplaced_items)


# This places items in the itempool into the locations
# It does not check for reachability, only that the item is
# allowed in the location
def fill_restrictive_fast(window, worlds, locations, itempool):
    while itempool and locations:
        item_to_place = itempool.pop()
        random.shuffle(locations)

        # get location that allows this item
        spot_to_fill = None
        for location in locations:
            if location.can_fill_fast(item_to_place):
                spot_to_fill = location
                break

        # if we failed to find a suitable location, then stop placing items
        # we don't need to check beatability since world must be beatable
        # at this point
        if spot_to_fill is None:
            if not worlds[0].check_beatable_only:
                logging.getLogger('').debug('Not all items placed. Game beatable anyway.')
            break

        # Place the item in the world and continue
        spot_to_fill.world.push_item(spot_to_fill, item_to_place)
        locations.remove(spot_to_fill)
        window.fillcount += 1
        window.update_progress(5 + ((window.fillcount / window.locationcount) * 30))


# this places item in item_pool completely randomly into
# fill_locations. There is no checks for validity since
# there should be none for these remaining items
def fast_fill(window, locations, itempool):
    random.shuffle(locations)
    while itempool and locations:
        spot_to_fill = locations.pop()
        item_to_place = itempool.pop()
        spot_to_fill.world.push_item(spot_to_fill, item_to_place)
        window.fillcount += 1
        window.update_progress(5 + ((window.fillcount / window.locationcount) * 30))
