from __future__ import annotations
import logging
import random
from collections import OrderedDict
from itertools import chain
from typing import TYPE_CHECKING, Any

from Item import Item
from LocationList import location_sort_order
from Search import Search, RewindableSearch

if TYPE_CHECKING:
    from Dungeon import Dungeon
    from Entrance import Entrance
    from Goals import GoalCategory
    from Hints import GossipText
    from Location import Location
    from Region import Region
    from Settings import Settings
    from World import World

HASH_ICONS: list[str] = [
    'Deku Stick',
    'Deku Nut',
    'Bow',
    'Slingshot',
    'Fairy Ocarina',
    'Bombchu',
    'Longshot',
    'Boomerang',
    'Lens of Truth',
    'Beans',
    'Megaton Hammer',
    'Bottled Fish',
    'Bottled Milk',
    'Mask of Truth',
    'SOLD OUT',
    'Cucco',
    'Mushroom',
    'Saw',
    'Frog',
    'Master Sword',
    'Mirror Shield',
    'Kokiri Tunic',
    'Hover Boots',
    'Silver Gauntlets',
    'Gold Scale',
    'Stone of Agony',
    'Skull Token',
    'Heart Container',
    'Boss Key',
    'Compass',
    'Map',
    'Big Magic',
]

PASSWORD_NOTES: list[str] = [
    'A',
    'C down',
    'C right',
    'C left',
    'C up',
]

class Spoiler:
    def __init__(self, worlds: list[World]) -> None:
        self.worlds: list[World] = worlds
        self.settings: Settings = worlds[0].settings
        self.playthrough: dict[str, list[Location]] = {}
        self.entrance_playthrough: dict[str, list[Entrance]] = {}
        self.full_playthrough: dict[str, int] = {}
        self.max_sphere: int = 0
        self.locations: dict[int, dict[str, Item]] = {}
        self.entrances: dict[int, list[Entrance]] = {}
        self.required_locations: dict[int, list[Location]] = {}
        self.goal_locations: dict[int, dict[str, dict[str, dict[int, list[Location]]]]] = {}
        self.goal_categories: dict[int, dict[str, GoalCategory]] = {}
        self.hints: dict[int, dict[int, GossipText]] = {world.id: {} for world in worlds}
        self.file_hash: list[int] = []
        self.password: list[int] = []

    def build_file_hash(self) -> None:
        dist_file_hash = self.settings.distribution.file_hash
        for i in range(5):
            self.file_hash.append(random.randint(0, 31) if dist_file_hash[i] is None else HASH_ICONS.index(dist_file_hash[i]))

    def build_password(self, password: bool = False) -> None:
        dist_password = self.settings.distribution.password
        for i in range(6):
            if password:
                self.password.append(random.randint(1, 5) if dist_password[i] is None else PASSWORD_NOTES.index(dist_password[i]) + 1)
            else:
                self.password.append(0)

    def parse_data(self) -> None:
        for (sphere_nr, sphere) in self.playthrough.items():
            sorted_sphere = [location for location in sphere]
            sort_order = {"Song": 0, "Boss": -1}
            sorted_sphere.sort(key=lambda item: (item.world.id * 10) + sort_order.get(item.type, 1))
            self.playthrough[sphere_nr] = sorted_sphere

        self.locations = {}
        for world in self.worlds:
            spoiler_locations = sorted(
                    [location for location in world.get_locations() if not location.locked and not location.type.startswith('Hint')],
                    key=lambda x: location_sort_order.get(x.name, 100000))
            self.locations[world.id] = OrderedDict([(str(location), location.item) for location in spoiler_locations if location.item is not None])

        entrance_sort_order = {
            "Spawn": 0,
            "WarpSong": 1,
            "OwlDrop": 2,
            "OverworldOneWay": 3,
            "Overworld": 4,
            "DungeonSpecial": 5,
            "Dungeon": 5,
            "ChildBoss": 6,
            "AdultBoss": 6,
            "Hideout": 7,
            "SpecialInterior": 7,
            "Interior": 7,
            "Grotto": 8,
            "Grave": 8,
        }
        for (sphere_nr, sphere) in self.entrance_playthrough.items():
            sorted_sphere = [entrance for entrance in sphere]
            sorted_sphere.sort(key=lambda entrance: entrance_sort_order.get(entrance.type, -1))
            sorted_sphere.sort(key=lambda entrance: entrance.name)
            sorted_sphere.sort(key=lambda entrance: entrance.world.id)
            self.entrance_playthrough[sphere_nr] = sorted_sphere

        self.entrances = {}
        for world in self.worlds:
            spoiler_entrances = [entrance for entrance in world.get_shuffled_entrances() if entrance.primary or entrance.type == 'Overworld']
            spoiler_entrances.sort(key=lambda entrance: entrance.name)
            spoiler_entrances.sort(key=lambda entrance: entrance_sort_order.get(entrance.type, -1))
            self.entrances[world.id] = spoiler_entrances

    def copy_worlds(self) -> list[World]:
        copier = Copier(self)
        worlds = copier.copy()
        return worlds

    def find_misc_hint_items(self) -> None:
        search = Search([world.state for world in self.worlds])
        all_locations = [location for world in self.worlds for location in world.get_filled_locations()]
        for location in search.iter_reachable_locations(all_locations[:]):
            # include locations that are reachable but not part of the spoiler log playthrough in misc. item hints
            location.maybe_set_misc_hints()
            all_locations.remove(location)
            if location.item and location.item.solver_id is not None:
                search.collect(location.item)
        for location in all_locations:
            # finally, collect unreachable locations for misc. item hints
            location.maybe_set_misc_hints()

    def create_playthrough(self) -> None:
        logger = logging.getLogger('')
        if self.worlds[0].check_beatable_only and not Search([world.state for world in self.worlds]).can_beat_game():
            raise RuntimeError('Game unbeatable after placing all items.')

        # create a copy as we will modify it
        worlds = self.copy_worlds()

        # if we only check for beatable, we can do this sanity check first before writing down spheres
        if worlds[0].check_beatable_only and not Search([world.state for world in worlds]).can_beat_game():
            raise RuntimeError('Uncopied world beatable but copied world is not.')

        search = RewindableSearch([world.state for world in worlds])
        logger.debug('Initial search: %s', search.state_list[0].get_prog_items())
        # Get all item locations in the worlds
        item_locations = search.progression_locations()
        # Omit certain items from the playthrough
        internal_locations = {location for location in item_locations if location.internal}
        # Generate a list of spheres by iterating over reachable locations without collecting as we go.
        # Collecting every item in one sphere means that every item
        # in the next sphere is collectable. Will contain every reachable item this way.
        logger.debug('Building up collection spheres.')
        collection_spheres = []
        entrance_spheres = []
        remaining_entrances = set(entrance for world in worlds for entrance in world.get_shuffled_entrances())

        search.checkpoint()
        search.collect_pseudo_starting_items()
        logger.debug('With pseudo starting items: %s', search.state_list[0].get_prog_items())

        while True:
            search.checkpoint()
            # Not collecting while the generator runs means we only get one sphere at a time
            # Otherwise, an item we collect could influence later item collection in the same sphere
            collected = list(search.iter_reachable_locations(item_locations))
            if not collected:
                break
            random.shuffle(collected)
            # Gather the new entrances before collecting items.
            collection_spheres.append(collected)
            accessed_entrances = set(filter(search.spot_access, remaining_entrances))
            entrance_spheres.append(list(accessed_entrances))
            remaining_entrances -= accessed_entrances
            for location in collected:
                # Collect the item for the state world it is for
                search.state_list[location.item.world.id].collect(location.item)
                location.maybe_set_misc_hints()
        logger.info('Collected %d spheres', len(collection_spheres))
        self.full_playthrough = dict((location.name, i + 1) for i, sphere in enumerate(collection_spheres) for location in sphere)
        self.max_sphere = len(collection_spheres)

        # Reduce each sphere in reverse order, by checking if the game is beatable
        # when we remove the item. We do this to make sure that progressive items
        # like bow and slingshot appear as early as possible rather than as late as possible.
        required_locations = []
        for sphere in reversed(collection_spheres):
            random.shuffle(sphere)
            for location in sphere:
                # we remove the item at location and check if the game is still beatable in case the item could be required
                old_item = location.item

                # Uncollect the item and location.
                search.state_list[old_item.world.id].remove(old_item)
                search.unvisit(location)

                # Generic events might show up or not, as usual, but since we don't
                # show them in the final output, might as well skip over them. We'll
                # still need them in the final pass, so make sure to include them.
                if location.internal:
                    required_locations.append(location)
                    continue

                location.item = None

                # An item can only be required if it isn't already obtained or if it's progressive
                if search.state_list[old_item.world.id].item_count(old_item.solver_id) < old_item.world.max_progressions[old_item.name]:
                    # Test whether the game is still beatable from here.
                    logger.debug('Checking if %s is required to beat the game.', old_item.name)
                    if not search.can_beat_game():
                        # still required, so reset the item
                        location.item = old_item
                        required_locations.append(location)

        # Reduce each entrance sphere in reverse order, by checking if the game is beatable when we disconnect the entrance.
        required_entrances = []
        for sphere in reversed(entrance_spheres):
            random.shuffle(sphere)
            for entrance in sphere:
                # we disconnect the entrance and check if the game is still beatable
                old_connected_region = entrance.disconnect()

                # we use a new search to ensure the disconnected entrance is no longer used
                sub_search = Search([world.state for world in worlds])

                # Test whether the game is still beatable from here.
                logger.debug('Checking if reaching %s, through %s, is required to beat the game.', old_connected_region.name, entrance.name)
                if not sub_search.can_beat_game():
                    # still required, so reconnect the entrance
                    entrance.connect(old_connected_region)
                    required_entrances.append(entrance)

        # Regenerate the spheres as we might not reach places the same way anymore.
        search.reset() # search state has no items, okay to reuse sphere 0 cache
        collection_spheres = [list(
            filter(lambda loc: loc.item.advancement and loc.item.world.max_progressions[loc.item.name] > 0,
                   search.iter_pseudo_starting_locations()))]
        entrance_spheres = []
        remaining_entrances = set(required_entrances)
        collected = set()
        while True:
            # Not collecting while the generator runs means we only get one sphere at a time
            # Otherwise, an item we collect could influence later item collection in the same sphere
            collected.update(search.iter_reachable_locations(required_locations))
            if not collected:
                break
            internal = collected & internal_locations
            if internal:
                # collect only the internal events but don't record them in a sphere
                for location in internal:
                    search.state_list[location.item.world.id].collect(location.item)
                # Remaining locations need to be saved to be collected later
                collected -= internal
                continue
            # Gather the new entrances before collecting items.
            collection_spheres.append(list(collected))
            accessed_entrances = set(filter(search.spot_access, remaining_entrances))
            entrance_spheres.append(accessed_entrances)
            remaining_entrances -= accessed_entrances
            for location in collected:
                # Collect the item for the state world it is for
                search.state_list[location.item.world.id].collect(location.item)
            collected.clear()
        logger.info('Collected %d final spheres', len(collection_spheres))

        if not search.can_beat_game(False):
            logger.error('Playthrough could not beat the game!')
            # Add temporary debugging info or breakpoint here if this happens

        # Then we can finally output our playthrough
        self.playthrough = OrderedDict((str(i), {location: location.item for location in sphere}) for i, sphere in enumerate(collection_spheres))
        # Copy our misc. hint items, since we set them in the world copy
        for w, sw in zip(worlds, self.worlds):
            # But the actual location saved here may be in a different world
            for item_name, item_location in w.hinted_dungeon_reward_locations.items():
                sw.hinted_dungeon_reward_locations[item_name] = self.worlds[item_location.world.id].get_location(item_location.name)
            for hint_type, item_location in w.misc_hint_item_locations.items():
                sw.misc_hint_item_locations[hint_type] = self.worlds[item_location.world.id].get_location(item_location.name)

        if worlds[0].entrance_shuffle:
            self.entrance_playthrough = OrderedDict((str(i + 1), list(sphere)) for i, sphere in enumerate(entrance_spheres))


class Copier:
    def __init__(self, spoiler: Spoiler) -> None:
        self.spoiler: Spoiler = spoiler
        self.worlds: dict[int, World] = {}
        self.dungeons: dict[int, Dungeon] = {}
        self.regions: dict[int, Region] = {}
        self.entrances: dict[int, Entrance] = {}
        self.locations: dict[int, Location] = {}
        self.items: dict[int, Item] = {}

    def copy(self) -> list[World]:
        if self.worlds:
            return list(self.worlds.values())

        # Make copies.
        for world in self.spoiler.worlds:
            self.worlds[id(world)] = world.copy()
            for dungeon in world.dungeons:
                self.dungeons[id(dungeon)] = dungeon.copy()
                for item in chain(dungeon.boss_key, dungeon.small_keys, dungeon.dungeon_items, dungeon.silver_rupees, dungeon.reward):
                    if id(item) in self.items:
                        continue
                    self.items[id(item)] = item.copy()
            for region in world.regions:
                self.regions[id(region)] = region.copy()
                for entrance in chain(region.entrances, region.exits, [region.savewarp] if region.savewarp else []):
                    if id(entrance) in self.entrances:
                        continue
                    self.entrances[id(entrance)] = entrance.copy()
                for location in region.locations:
                    if id(location) in self.locations:
                        continue
                    self.locations[id(location)] = location.copy()
                    if location.item and id(location.item) not in self.items:
                        self.items[id(location.item)] = location.item.copy()
            for item in world.itempool:
                if id(item) in self.items:
                    continue
                self.items[id(item)] = item.copy()

        # Update references.
        for world in self.worlds.values():
            world.dungeons = [self.dungeons.get(id(dungeon), dungeon) for dungeon in world.dungeons]
            world.regions = [self.regions.get(id(region), region) for region in world.regions]
            world.itempool = [self.items.get(id(item), item) for item in world.itempool]

        for dungeon in self.dungeons.values():
            dungeon.world = self.worlds.get(id(dungeon.world), dungeon.world)
            dungeon.regions = [self.regions.get(id(region), region) for region in dungeon.regions]
            dungeon.boss_key = [self.items.get(id(item), item) for item in dungeon.boss_key]
            dungeon.small_keys = [self.items.get(id(item), item) for item in dungeon.small_keys]
            dungeon.dungeon_items = [self.items.get(id(item), item) for item in dungeon.dungeon_items]
            dungeon.silver_rupees = [self.items.get(id(item), item) for item in dungeon.silver_rupees]
            dungeon.reward = [self.items.get(id(item), item) for item in dungeon.reward]

        for region in self.regions.values():
            region.world = self.worlds.get(id(region.world), region.world)
            region.entrances = [self.entrances.get(id(entrance), entrance) for entrance in region.entrances]
            region.exits = [self.entrances.get(id(entrance), entrance) for entrance in region.exits]
            region.locations = [self.locations.get(id(location), location) for location in region.locations]
            region.dungeon = self.dungeons.get(id(region.dungeon), region.dungeon)
            region.savewarp = self.entrances.get(id(region.savewarp), region.savewarp)

        for entrance in self.entrances.values():
            entrance.world = self.worlds.get(id(entrance.world), entrance.world)
            entrance.parent_region = self.regions.get(id(entrance.parent_region), entrance.parent_region)
            entrance.connected_region = self.regions.get(id(entrance.connected_region), entrance.connected_region)
            entrance.reverse = self.entrances.get(id(entrance.reverse), entrance.reverse)
            entrance.replaces = self.entrances.get(id(entrance.replaces), entrance.replaces)
            entrance.assumed = self.entrances.get(id(entrance.assumed), entrance.assumed)

        for location in self.locations.values():
            location.world = self.worlds.get(id(location.world), location.world)
            location.parent_region = self.regions.get(id(location.parent_region), location.parent_region)
            location.item = self.items.get(id(location.item), location.item)

        for item in self.items.values():
            item.world = self.worlds.get(id(item.world), item.world)
            item.location = self.locations.get(id(item.location), item.location)
            item.looks_like_item = self.items.get(id(item.looks_like_item), item.looks_like_item)

        for world in self.worlds.values():
            world.initialize_entrances()

        return list(self.worlds.values())
