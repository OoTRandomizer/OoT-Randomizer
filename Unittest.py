# Run unittests with python -m unittest Unittest[.ClassName[.test_func]]
# With python3.10, you can instead run pytest Unittest.py
# See `python -m unittest -h` or `pytest -h` for more options.

from __future__ import annotations
import io
import json
import logging
import os
import random
import re
import unittest
from collections import Counter, defaultdict
from typing import Literal, Optional, Any, overload

from EntranceShuffle import EntranceShuffleError
from Fill import ShuffleError
from Hints import HintArea, build_misc_item_hints
from Item import ItemInfo
from ItemPool import remove_junk_items, remove_junk_ludicrous_items, ludicrous_items_base, ludicrous_items_extended, trade_items, ludicrous_exclusions
from LocationList import location_is_viewable
from Main import main, resolve_settings, build_world_graphs
from Messages import Message, read_messages, shuffle_messages
from Settings import Settings, get_preset_files
from Spoiler import Spoiler
from Rom import Rom
from Audiobank import *

test_dir = os.path.join(os.path.dirname(__file__), 'tests')
output_dir = os.path.join(test_dir, 'Output')
os.makedirs(output_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO, filename=os.path.join(output_dir, 'LAST_TEST_LOG'), filemode='w')

# items never required:
# refills, maps, compasses, capacity upgrades, masks (not listed in logic)
never_prefix = ['Bombs', 'Arrows', 'Rupee', 'Deku Seeds', 'Map', 'Compass']
never_suffix = ['Capacity']
never = {
    'Recovery Heart', 'Milk', 'Ice Trap',
    'Double Defense', 'Biggoron Sword', 'Giants Knife',
} | {name for name, item in ItemInfo.items.items() if item.priority
     or any(map(name.startswith, never_prefix)) or any(map(name.endswith, never_suffix))}

# items required at most once, specifically things with multiple possible names
# (except bottles)
once = {
    'Goron Tunic', 'Zora Tunic',
}

progressive = {name for name, item in ItemInfo.items.items() if item.special.get('progressive', None)}
bottles = {name for name, item in ItemInfo.items.items() if item.special.get('bottle', None) and name != 'Deliver Letter'}
junk = set(remove_junk_items)
shop_items = {i for i, nfo in ItemInfo.items.items() if nfo.type == 'Shop'}
ludicrous_junk = set(remove_junk_ludicrous_items)
ludicrous_set = set(ludicrous_items_base) | set(ludicrous_items_extended) | ludicrous_junk | set(trade_items) | set(bottles) | set(ludicrous_exclusions) | {'Bottle with Big Poe'} | shop_items


def make_settings_for_test(settings_dict: dict[str, Any], seed: Optional[str] = None, outfilename: str = '', strict: bool = True) -> Settings:
    # Some consistent settings for testability
    settings_dict.update({
        'create_patch_file': False,
        'create_compressed_rom': False,
        'create_wad_file': False,
        'create_uncompressed_rom': False,
        'count': 1,
        'create_spoiler': True,
        'output_file': os.path.join(test_dir, 'Output', outfilename),
    })
    if seed and 'seed' not in settings_dict:
        settings_dict['seed'] = seed
    return Settings(settings_dict, strict=strict)


def load_settings(settings_file: dict[str, Any] | str, seed: Optional[str] = None, filename: Optional[str] = None) -> Settings:
    if isinstance(settings_file, dict):  # Check if settings_file is a distribution file settings dict
        if filename is None:
            raise RuntimeError("Running test with in memory file but did not supply a filename for output file.")
        j = settings_file
        j.update({
            'enable_distribution_file': True,
            'distribution_file': os.path.join(test_dir, 'plando', filename + '.json')
        })
    else:
        sfile = os.path.join(test_dir, settings_file)
        filename = os.path.splitext(settings_file)[0]
        with open(sfile) as f:
            j = json.load(f)
    return make_settings_for_test(j, seed=seed, outfilename=filename)


def load_spoiler(json_file: str) -> Any:
    with open(json_file) as f:
        return json.load(f)


@overload
def generate_with_plandomizer(filename: str, live_copy: Literal[False] = False, max_attempts: int = 10) -> tuple[dict[str, Any], dict[str, Any]]:
    pass


@overload
def generate_with_plandomizer(filename: str, live_copy: Literal[True], max_attempts: int = 10) -> tuple[dict[str, Any], Spoiler]:
    pass


def generate_with_plandomizer(filename: str, live_copy: bool = False, max_attempts: int = 10) -> tuple[dict[str, Any], Spoiler | dict[str, Any]]:
    distribution_file = load_spoiler(os.path.join(test_dir, 'plando', filename + '.json'))
    try:
        settings = load_settings(distribution_file['settings'], seed='TESTTESTTEST', filename=filename)
    except KeyError:  # No settings dict in distribution file, create minimal consistent configuration
        settings = Settings({
            'enable_distribution_file': True,
            'distribution_file': os.path.join(test_dir, 'plando', filename + '.json'),
            'create_patch_file': False,
            'create_compressed_rom': False,
            'create_wad_file': False,
            'create_uncompressed_rom': False,
            'count': 1,
            'create_spoiler': True,
            'output_file': os.path.join(test_dir, 'Output', filename),
            'seed': 'TESTTESTTEST'
        })
    spoiler = main(settings, max_attempts=max_attempts)
    if not live_copy:
        spoiler = load_spoiler(f'{settings.output_file}_Spoiler.json')
    return distribution_file, spoiler


def get_actual_pool(spoiler: dict[str, Any]) -> dict[str, int]:
    """Retrieves the actual item pool based on items placed in the spoiler log.

    :param spoiler: Spoiler log output from generator
    :return: dict:
                key: Item name
                value: count in spoiler
    """
    actual_pool = {}
    for location, item in spoiler['locations'].items():
        if isinstance(item, dict):
            test_item = item['item']
        else:
            test_item = item
        try:
            actual_pool[test_item] += 1
        except KeyError:
            actual_pool[test_item] = 1
    return actual_pool


class TestPlandomizer(unittest.TestCase):
    def test_item_list(self):
        filenames = [
            "plando-list",
            "plando-item-list-implicit",
            "plando-item-list-explicit"
        ]
        for filename in filenames:
            with self.subTest(filename):
                distribution_file, spoiler = generate_with_plandomizer(filename)
                for location, item_value in distribution_file['locations'].items():
                    spoiler_value = spoiler['locations'][location]
                    if isinstance(item_value, dict):
                        item_list = item_value['item']
                    else:
                        item_list = item_value
                    if isinstance(spoiler_value, dict):
                        self.assertIn(spoiler_value['item'], item_list)
                    else:
                        self.assertIn(spoiler_value, item_list)

    def test_explicit_item_pool(self):
        with self.subTest("generate with defined item pool"):
            distribution_file, spoiler = generate_with_plandomizer("plando-explicit-item-pool")
            for item, value in distribution_file['item_pool'].items():
                self.assertEqual(value, spoiler['item_pool'][item])
            actual_pool = get_actual_pool(spoiler)
            for item in spoiler['item_pool']:
                self.assertEqual(actual_pool[item], spoiler['item_pool'][item])
        with self.subTest("even if item pool is large"):
            generate_with_plandomizer("plando-explicit-item-pool-3")
        with self.subTest("except when not enough junk can be added"):
            self.assertRaises(RuntimeError, generate_with_plandomizer, "plando-explicit-item-pool-2")

    def test_num_limited_items(self):
        filenames = [
            "plando-num-bottles-fountain-closed-bad",
            "plando-num-bottles-fountain-open-bad",
            "plando-num-adult-trade-item-bad",
            "plando-num-weird-egg-item-bad"
        ]
        for filename in filenames:
            with self.subTest(filename):
                self.assertRaises(RuntimeError, generate_with_plandomizer, filename)

    def test_excess_starting_items(self):
        distribution_file, spoiler = generate_with_plandomizer("plando-excess-starting-items")
        excess_item = list(distribution_file['settings']['starting_items'])[0]
        for location, item in spoiler['locations'].items():
            if isinstance(item, dict):
                test_item = spoiler['locations'][location]['item']
            else:
                test_item = spoiler['locations'][location]
            self.assertNotEqual(excess_item, test_item)
        self.assertNotIn(excess_item, spoiler['item_pool'])

    def test_rom_patching(self):
        # This makes sure there are no crashes while patching.
        if not os.path.isfile('./ZOOTDEC.z64'):
            self.skipTest("Base ROM file not available.")
        filename = "plando-ammo-max-out-of-bounds"
        logic_rules_settings = ['glitchless', 'glitched', 'none']
        for logic_rules_setting in logic_rules_settings:
            with self.subTest(f"Logic Rules: {logic_rules_setting}"):
                settings = Settings({
                    'enable_distribution_file': True,
                    'distribution_file': os.path.join(test_dir, 'plando', filename + '.json'),
                    'patch_without_output': True,
                    'create_patch_file': False,
                    'create_compressed_rom': False,
                    'create_wad_file': False,
                    'create_uncompressed_rom': False,
                    'count': 1,
                    'create_spoiler': True,
                    'create_cosmetics_log': False,
                    'output_file': os.path.join(test_dir, 'Output', filename),
                    'seed': 'TESTTESTTEST',
                    'logic_rules': logic_rules_setting
                })
                main(settings)  # Should not crash

    def test_ice_traps(self):
        filenames = [
            "plando-item-pool-matches-items-placed-after-starting-items-replaced",
            "plando-new-placed-ice-traps",
            "plando-placed-and-added-ice-traps",
            "non-standard-visible-ice-traps",
            "custom-ice-traps-percent-triforce-hunt",
            "custom-ice-traps-count",
            "custom-ice-traps-percent",
        ]
        for filename in filenames:
            with self.subTest(filename):
                distribution_file, spoiler = generate_with_plandomizer(filename)
                csmc = spoiler['settings'].get('correct_chest_appearances')
                fast_chests = spoiler['settings'].get('fast_chests')
                for location in spoiler['locations']:
                    if location_is_viewable(location, csmc, fast_chests):
                        item = spoiler['locations'][location]
                        if isinstance(item, dict):
                            if item['item'] == "Ice Trap":
                                self.assertIn("model", item)
                        else:
                            self.assertNotIn("Ice Trap", item)
                if filename == "plando-item-pool-matches-items-placed-after-starting-items-replaced":
                    with self.subTest("ice traps not junk with junk ice traps off"):
                        self.assertEqual(spoiler['item_pool']['Ice Trap'], 6)
                    with self.subTest("ice traps junk with junk ice traps on"):
                        # This distribution file should set all junk items to 1 except for ice traps so we will reuse it
                        _, spoiler = generate_with_plandomizer("plando-explicit-item-pool")
                        self.assertGreater(spoiler['item_pool']['Ice Trap'], 6)
                if filename == "non-standard-visible-ice-traps":
                    with self.subTest("ice trap models in non-standard visible locations"):
                        for location in distribution_file['locations']:
                            self.assertIn('model', spoiler['locations'][location])
                if filename == "custom-ice-traps-count":
                    self.assertEqual(spoiler['item_pool']['Ice Trap'], 50)
                if filename in  ["custom-ice-traps-percent", "custom-ice-traps-percent-triforce-hunt"]:
                    # Count up all the junk that is left
                    from ItemPool import junk_pool_base
                    junk = [item for item, weight in junk_pool_base] + ['Rupee (1)', 'Recovery Heart', 'Bombs (20)', 'Arrows (30)']
                    junk_count = 0
                    for item in spoiler['item_pool'].keys():
                        if item in junk:
                            junk_count += spoiler['item_pool'][item]
                    ice_trap_count = spoiler['item_pool']['Ice Trap']
                    # Check that 75% of the junk is ice traps, per the plando
                    self.assertEqual(int((junk_count + ice_trap_count) * .75), ice_trap_count)

    def test_should_not_throw_exception(self):
        filenames = [
            "plando-bottles-in-list",
            "plando-bottle-item-group",
            "plando-bottle-item-group-in-list",
            "plando-adult-trade-in-list",
            "plando-adult-trade-item-group",
            "plando-adult-trade-item-group-in-list",
            "plando-weird-egg-in-list",
            "plando-shop-items",
            "plando-list-case-sensitivity",
            "plando-num-adult-trade-item-good",
            "plando-num-weird-egg-item-good",
            "plando-num-bottles-fountain-closed-good",
            "plando-num-bottles-fountain-open-good",
            "plando-change-triforce-piece-count",
            "plando-use-normal-triforce-piece-count",
            "plando-egg-not-shuffled-one-pool",
            "plando-egg-not-shuffled-two-pool",
            "plando-egg-shuffled-one-pool",
            "plando-egg-shuffled-two-pool",
            "no-ice-trap-pending-junk",
            "disabled-song-location",
            "plando-keyrings-all-anydungeon-allmq",
            "plando-keyrings-all-anydungeon-halfmq",
            "plando-keyrings-all-anydungeon-nomq",
            "plando-keyrings-all-anywhere-allmq",
            "plando-keyrings-all-anywhere-halfmq",
            "plando-keyrings-all-anywhere-nomq",
            "plando-keyrings-all-dungeon-allmq",
            "plando-keyrings-all-dungeon-halfmq",
            "plando-keyrings-all-dungeon-nomq",
            "plando-mirrored-ice-traps",
            "plando-boss-shuffle-nomq",
            "plando-boss-shuffle-allmq",
            "plando-boss-shuffle-limited-dungeon-shuffle",
            "dual-hints",
            "negative-pattern-test",
            "dual-hints-custom-text",
            "dual-hints-with-upgrade",
            "plando-freestanding-nomq",
            "plando-freestanding-allmq",
            "plando-potscrates-nomq",
            "plando-potscrates-allmq",
            "plando-beehives",
            "plando-freestanding-pots-crates-beehives-triforcehunt",
        ]
        for filename in filenames:
            with self.subTest(filename):
                generate_with_plandomizer(filename)

    def test_boss_item_list(self):
        filenames = [
            "plando-boss-list-child",
            "plando-boss-list-adult",
            "plando-boss-list"]
        for filename in filenames:
            with self.subTest(filename):
                distribution_file, spoiler = generate_with_plandomizer(filename)
                for location, item_list in distribution_file['locations'].items():
                    self.assertIn(spoiler['locations'][location], item_list)

    def test_pool_accuracy(self):
        filenames = [
            "empty",
            "plando-list",
            "plando-item-pool-matches-items-placed-after-starting-items-replaced",
            "plando-change-triforce-piece-count",
            "plando-use-normal-triforce-piece-count",
            "plando-shop-items",
            "no-ice-trap-pending-junk",
        ]
        for filename in filenames:
            with self.subTest(filename + " pool accuracy"):
                distribution_file, spoiler = generate_with_plandomizer(filename)
                actual_pool = get_actual_pool(spoiler)
                for item in spoiler['item_pool']:
                    self.assertEqual(actual_pool[item], spoiler['item_pool'][item],
                    f"Pool item {item} count mismatch")
        filename = "plando-list-exhaustion"
        with self.subTest(filename + " pool accuracy"):
            distribution_file, spoiler = generate_with_plandomizer(filename)
            actual_pool = get_actual_pool(spoiler)
            for item in distribution_file['item_pool']:
                self.assertEqual(actual_pool[item], distribution_file['item_pool'][item])
        filename = "plando-item-pool-matches-items-placed-after-starting-items-replaced"
        with self.subTest("starting items not in actual_pool"):
            distribution_file, spoiler = generate_with_plandomizer(filename)
            actual_pool = get_actual_pool(spoiler)
            for item in distribution_file['settings']['starting_items']:
                self.assertNotIn(item, actual_pool)

    def test_ludicrous_pool_junk(self):
        filenames = [
            "plando-ludicrous-default",
            "plando-ludicrous-skip-child-zelda",
            "plando-ludicrous-max-locations",
            "plando-ludicrous-ice-traps",
            "plando-ludicrous-starting-bottles",
            "plando-ludicrous-starting-hearts",
            "plando-ludicrous-starting-all-items"
        ]
        for filename in filenames:
            with self.subTest(filename + " ludicrous junk"):
                distribution_file, spoiler = generate_with_plandomizer(filename)
                pool_set = {i for i, c in spoiler['item_pool'].items()}
                self.assertEqual(
                    set(),
                    pool_set - ludicrous_set,
                    'Ludicrous pool has regular junk items')
        filename = "plando-ludicrous-junk-locations"
        with self.subTest("location plando junk permission with ludicrous item pool"):
            distribution_file, spoiler = generate_with_plandomizer(filename)
            pool_set = {i for i, c in spoiler['item_pool'].items()}
            self.assertEqual(
                {'Rupees (5)'},
                pool_set - ludicrous_set,
                'Ludicrous pool missing forced location junk items')

    def test_weird_egg_in_pool(self):
        # Not shuffled, one in pool: Should remove from pool and not place anywhere
        not_shuffled_one = "plando-egg-not-shuffled-one-pool"
        distribution_file, spoiler = generate_with_plandomizer(not_shuffled_one)
        self.assertNotIn('Weird Egg', spoiler['item_pool'])
        # Not shuffled, two in pool: Should be the same outcome as previous case
        not_shuffled_two = "plando-egg-not-shuffled-two-pool"
        distribution_file, spoiler = generate_with_plandomizer(not_shuffled_two)
        self.assertNotIn('Weird Egg', spoiler['item_pool'])
        # Shuffled, one in pool: Valid config, shouldn't have to make any changes, will end with 1 in pool
        shuffled_one = "plando-egg-shuffled-one-pool"
        distribution_file, spoiler = generate_with_plandomizer(shuffled_one)
        self.assertEqual(spoiler['item_pool']['Weird Egg'], 1)
        # Shuffled, two in pool: Valid config, will end with 2 in pool
        shuffled_two = "plando-egg-shuffled-two-pool"
        distribution_file, spoiler = generate_with_plandomizer(shuffled_two)
        self.assertEqual(spoiler['item_pool']['Weird Egg'], 1)

    def test_key_rings(self):
        # Checking dungeon keys using forest temple
        # Testing Boss Keys, should not be any Forest BK
        # All other Boss Keys should exist, Fire Temple for example
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-bosskey-forest-anywhere-minimal")
        self.assertNotIn('Boss Key (Forest Temple)', spoiler['locations'].values())
        self.assertEqual(get_actual_pool(spoiler)['Boss Key (Fire Temple)'], 1)
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-bosskey-forest-anywhere-balanced")
        self.assertNotIn('Boss Key (Forest Temple)', spoiler['locations'].values())
        self.assertEqual(get_actual_pool(spoiler)['Boss Key (Fire Temple)'], 1)
        # Shuffle Keys set to Vanilla, Boss Keys should exist
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-bosskey-forest-vanilla-plentiful")
        self.assertEqual(get_actual_pool(spoiler)['Boss Key (Forest Temple)'], 1)

        # No key rings: Make sure boss key in plentiful
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-bosskey-none-anywhere-plentiful")
        self.assertEqual(get_actual_pool(spoiler)['Boss Key (Forest Temple)'], 1)

        # No key rings: Make sure boss key in ludicrous
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-bosskey-none-anywhere-ludicrous")
        self.assertEqual(get_actual_pool(spoiler)['Boss Key (Forest Temple)'], 1)

        # Minimal and balanced pools: Should be one key ring
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-forest-anywhere-minimal")
        self.assertNotIn('Small Key (Forest Temple)', spoiler['locations'].values())
        self.assertEqual(get_actual_pool(spoiler)['Small Key Ring (Forest Temple)'], 1)
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-forest-anywhere-balanced")
        self.assertNotIn('Small Key (Forest Temple)', spoiler['locations'].values())
        self.assertEqual(get_actual_pool(spoiler)['Small Key Ring (Forest Temple)'], 1)
        # Plentiful pool: Should be two key rings
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-forest-anywhere-plentiful")
        self.assertNotIn('Small Key (Forest Temple)', spoiler['locations'].values())
        self.assertEqual(get_actual_pool(spoiler)['Small Key Ring (Forest Temple)'], 2)
        # Ludicrous pool: Should be more than two key rings
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-forest-anywhere-ludicrous")
        self.assertNotIn('Small Key (Forest Temple)', spoiler['locations'].values())
        self.assertGreater(get_actual_pool(spoiler)['Small Key Ring (Forest Temple)'], 2)
        # Keysy: Should be no small keys or key rings (regardless of item pool)
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-forest-keysy-plentiful")
        self.assertNotIn('Small Key (Forest Temple)', spoiler['locations'].values())
        self.assertNotIn('Small Key Ring (Forest Temple)', spoiler['locations'].values())
        # Vanilla: Should be no keys of either type in vanilla (small keys will be placed but not listed in locations)
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-forest-vanilla-plentiful")
        self.assertNotIn('Small Key (Forest Temple)', spoiler['locations'].values())
        self.assertNotIn('Small Key Ring (Forest Temple)', spoiler['locations'].values())

        # Checking hideout keys
        # If fortress is fast or keys are vanilla, should be no key rings
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-hideout-default-vanilla")
        self.assertNotIn('Small Key (Thieves Hideout)', spoiler['locations'].values())
        self.assertNotIn('Small Key Ring (Thieves Hideout)', spoiler['locations'].values())
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-hideout-fast-vanilla")
        self.assertNotIn('Small Key (Thieves Hideout)', spoiler['locations'].values())
        self.assertNotIn('Small Key Ring (Thieves Hideout)', spoiler['locations'].values())
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-hideout-fast-anywhere-balanced")
        self.assertEqual(get_actual_pool(spoiler)['Small Key (Thieves Hideout)'], 1)
        self.assertNotIn('Small Key Ring (Thieves Hideout)', spoiler['locations'].values())
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-hideout-fast-anywhere-plentiful")
        self.assertEqual(get_actual_pool(spoiler)['Small Key (Thieves Hideout)'], 2)
        self.assertNotIn('Small Key Ring (Thieves Hideout)', spoiler['locations'].values())
        # If default behaviour (so 4 keys necessary) and keys not vanilla, should be 1 or 2 keyrings (balanced or plentiful)
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-hideout-default-anywhere-balanced")
        self.assertNotIn('Small Key (Thieves Hideout)', spoiler['locations'].values())
        self.assertEqual(get_actual_pool(spoiler)['Small Key Ring (Thieves Hideout)'], 1)
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-hideout-default-anywhere-plentiful")
        self.assertNotIn('Small Key (Thieves Hideout)', spoiler['locations'].values())
        self.assertEqual(get_actual_pool(spoiler)['Small Key Ring (Thieves Hideout)'], 2)
        # Should be neither if fortress is open, regardless of item pool
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-hideout-open-plentiful")
        self.assertNotIn('Small Key (Thieves Hideout)', spoiler['locations'].values())
        self.assertNotIn('Small Key Ring (Thieves Hideout)', spoiler['locations'].values())

        # No key rings: Make sure none in item pool on plentiful
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-none-anywhere-plentiful")
        self.assertEqual(get_actual_pool(spoiler)['Small Key (Forest Temple)'], 6)
        self.assertNotIn('Small Key Ring (Forest Temple)', spoiler['locations'].values())
        self.assertEqual(get_actual_pool(spoiler)['Small Key (Thieves Hideout)'], 5)
        self.assertNotIn('Small Key Ring (Thieves Hideout)', spoiler['locations'].values())

        # No key rings: Make sure none in item pool on ludicrous
        distribution_file, spoiler = generate_with_plandomizer("plando-keyrings-none-anywhere-ludicrous")
        self.assertGreater(get_actual_pool(spoiler)['Small Key (Forest Temple)'], 6)
        self.assertNotIn('Small Key Ring (Forest Temple)', spoiler['locations'].values())
        self.assertGreater(get_actual_pool(spoiler)['Small Key (Thieves Hideout)'], 5)
        self.assertNotIn('Small Key Ring (Thieves Hideout)', spoiler['locations'].values())

    def test_empty_dungeons(self):
        filenames = [
            "empty-dungeons-all-dungeon-er",
            "empty-dungeons-all-dungeon-item-any-dungeon",
            "empty-dungeons-all-dungeon-item-anywhere",
            "empty-dungeons-all-dungeon-item-remove",
            "empty-dungeons-all-mq-all",
            "empty-dungeons-all-mq-random",
            "empty-dungeons-all-plentiful",
            "empty-dungeons-all-songs-dungeon",
            "empty-dungeons-half-boss-shuffle",
            "empty-dungeons-half-dungeon-er",
            "empty-dungeons-half-dungeon-item-any-dungeon",
            "empty-dungeons-half-dungeon-item-anywhere",
            "empty-dungeons-half-dungeon-item-remove",
            "empty-dungeons-half-mq-all",
            "empty-dungeons-half-mq-random",
            "empty-dungeons-half-plentiful",
            "empty-dungeons-half-songs-dungeon"
        ]
        dungeons = {
            HintArea.DEKU_TREE: "Queen Gohma",
            HintArea.DODONGOS_CAVERN: "King Dodongo",
            HintArea.JABU_JABUS_BELLY: "Barinade",
            HintArea.FOREST_TEMPLE: "Phantom Ganon",
            HintArea.FIRE_TEMPLE: "Volvagia",
            HintArea.WATER_TEMPLE: "Morpha",
            HintArea.SHADOW_TEMPLE: "Bongo Bongo",
            HintArea.SPIRIT_TEMPLE: "Twinrova"
        }
        for filename in filenames:
            with self.subTest(filename):
                distribution_file, spoiler = generate_with_plandomizer(filename)
                # Proper rewards should be given on file select
                if spoiler['settings']['shuffle_bosses'] == 'off':
                    for dungeon, boss in dungeons.items():
                        if spoiler['empty_dungeons'][dungeon.dungeon_name]:
                            self.assertIn(boss, spoiler[':skipped_locations'])
                # Empty dungeons should be barren (except in settings where keys or tokens are major items)
                if spoiler['settings']['shuffle_smallkeys'] not in ['dungeon', 'vanilla']:
                    continue
                if spoiler['settings']['shuffle_bosskeys'] not in ['dungeon', 'vanilla']:
                    continue
                if spoiler['settings']['bridge'] == 'tokens' or spoiler['settings']['shuffle_ganon_bosskey'] == 'tokens':
                    continue
                if spoiler['settings']['shuffle_ganon_bosskey'] == 'on_lacs' and spoiler['settings']['lacs_condition'] == 'tokens':
                    continue
                for dungeon in dungeons:
                    if spoiler['empty_dungeons'][dungeon.dungeon_name]:
                        self.assertIn(str(dungeon), spoiler[':barren_regions'])

    def test_fix_broken_drops(self):
        # Setting off
        distribution_file, spoiler = generate_with_plandomizer("plando-fix-broken-drops-off")
        self.assertEqual(len([sphere for sphere in spoiler[':playthrough'].values() if 'Child Spirit Temple Beyond Metal Bridges Deku Shield Pot' in sphere]), 0)

        # No deku shield available, fail to generate
        self.assertRaises(ShuffleError, lambda : generate_with_plandomizer("plando-fix-broken-drops-bad", max_attempts=1))

        # Deku shield available only via spirit shield pot
        distribution_file, spoiler = generate_with_plandomizer("plando-fix-broken-drops-good")
        self.assertEqual(len([sphere for sphere in spoiler[':playthrough'].values() if 'Child Spirit Temple Beyond Metal Bridges Deku Shield Pot' in sphere]), 1)


class TestHints(unittest.TestCase):
    def test_skip_zelda(self):
        # Song from Impa would be WotH, but instead of relying on random chance to get HC WotH,
        # just exclude all other locations to see if HC is barren.
        _, spoiler = generate_with_plandomizer("skip-zelda")
        woth = spoiler[':barren_regions']
        self.assertIn('Hyrule Castle', woth)

    def test_ganondorf(self):
        if not os.path.isfile('./ZOOTDEC.z64'):
            self.skipTest("Base ROM file not available.")
        filenames = [
            "light-arrows-1",
            "light-arrows-2",
            "light-arrows-3",
        ]
        # Ganondorf should never hint LAs locked behind LAs
        for filename in filenames:
            with self.subTest(filename):
                _, spoiler = generate_with_plandomizer(filename, live_copy=True)
                self.assertIsNotNone(spoiler.worlds[0].misc_hint_item_locations["ganondorf"])
                self.assertNotEqual('Ganons Tower Boss Key Chest', spoiler.worlds[0].misc_hint_item_locations["ganondorf"].name)

    # Test that every goal in every goal category is hinted at least once
    # if the bridge and Ganon's Boss Key conditions are for the same type
    # of win condition, such as 4 medallion bridge and 6 medallion GBK.
    def test_one_hint_per_goal(self):
        # To ensure there are no empty goals, one required item per dungeon is plando'd
        # in song of storms grottos for bridge goals, and in light trial for Ganon's Boss
        # Key goals. Careful placement with minimal item pool guarantees every goal will
        # have more hintable items than there are goals in the category. This prevents
        # goals from being skipped because all items for it were already hinted.
        filenames = [
            "one-hint-per-goal-medallions",
            "one-hint-per-goal-stones",
            "one-hint-per-goal-dungeons",
            "one-hint-per-goal-skulls",
            "one-hint-per-goal-hearts",
            "one-hint-per-goal-triforce-hunt"
        ]
        for filename in filenames:
            with self.subTest(filename):
                _, spoiler = generate_with_plandomizer(filename)
                goals = list(goal_name for goal in list(spoiler[':goal_locations'].values()) for goal_name in list(goal.keys()))
                # If the hint distro in the plando removes goal hints in the future, alert that the test is broken
                # A custom distro is used to prevent this, but just in case...
                self.assertGreater(len(goals), 0)
                found_goals = []
                for g in range(len(goals)):
                    # Triforce Hunt, Skull, and Heart goals all add total available collectables
                    # in parentheses to the path name. Remove for the hint text search.
                    try:
                        goals[g] = goals[g][:goals[g].index(' (')]
                    except:
                        pass
                    # We need at least one hint per goal, but it doesn't matter if there are duplicates
                    # of a goal hint or more than one hint for the goal.
                    for hint in spoiler['gossip_stones'].values():
                        if goals[g].lower() in hint['text'].replace('#','').lower() or goals[g].lower() == "path of the hero":
                            found_goals.append(goals[g])
                            break
                self.assertEqual(found_goals, goals)
        # 1 stone bridge / 3 stone gbk
        # 5 med bridge / 6 med bridge
        # 5 dungeon bridge / 9 dungeon gbk
        # 99 skull bridge / 100 skull gbk
        # 19 heart bridge / 20 heart gbk
        # TH

    # Test that Ganondorf hints light arrows in the pots within Ganon's Tower as "those pots over there"
    # This seems to break every time the hint system changes slightly.
    def test_those_pots_over_there(self):
        filename = "those_pots_over_there"
        # Ganondorf should say "those pots over there" when light arrows are in a pot below
        _, spoiler = generate_with_plandomizer(filename, live_copy=True)
        world = spoiler.worlds[0]
        location = spoiler.worlds[0].misc_hint_item_locations["ganondorf"]
        area = HintArea.at(location, use_alt_hint=True).text(world.settings.clearer_hints, world=None if not location.world or location.world.id == world.id else location.world.id + 1)
        self.assertEqual(area, "#Ganondorf's Chamber#")
        # Build a test message with the same ID as the ganondorf hint (0x70CC)
        messages = [Message("Test", 0, 0x70CC, 0, 0, 0)]
        build_misc_item_hints(spoiler.worlds[0], messages, allow_duplicates=True)
        for message in messages:
            if message.id == 0x70CC: # Ganondorf hint message
                self.assertTrue("thosepotsoverthere" in message.text.replace('\n', '').replace(' ', ''))

    def test_blue_fire_arrows(self):
        # Blue Fire Arrows should be WotH and in the item pool
        _, spoiler = generate_with_plandomizer("plando-blue-fire-arrows-hints")
        woth = [x['item'] if isinstance(x, dict) else x for x in spoiler[':woth_locations'].values()]
        self.assertIn('Blue Fire Arrows', woth)


class TestEntranceRandomizer(unittest.TestCase):
    def test_spawn_point_invalid_areas(self):
        # With special interior, overworld, and warp song ER off, random spawns
        # require itemless access to Kokiri Forest or Kakariko Village. This imposes
        # a world state such that the Prelude and Serenade warp pads are also reachable
        # with no items, and Prelude and Serenade should be foolish. If this behaviour
        # is changed, this unit test serves as a reminder to revisit warp song
        # foolishness.
        # Currently only tests glitchless as glitched logic does not support ER yet.
        # Assumes the player starts with an ocarina to use a warp song from Sheik at
        # Colossus or Ice Cavern.
        filenames = [
            "plando-er-colossus-spawn-validity",
        ]
        for filename in filenames:
            distribution_file = load_spoiler(os.path.join(test_dir, 'plando', filename + '.json'))
            settings = load_settings(distribution_file['settings'], seed='TESTTESTTEST', filename=filename)
            resolve_settings(settings)
            # Test for an entrance shuffle error during world validation.
            # If the test succeeds, this confirms Serenade and Prelude can be foolish.
            with self.assertRaises(EntranceShuffleError):
                build_world_graphs(settings)


class TestValidSpoilers(unittest.TestCase):
    # Normalizes spoiler dict for single world or multiple worlds
    # Single world worlds_dict is a map of key -> value
    # Multi world worlds_dict is a map of "World x" -> {map of key -> value} (with x the player/world number)
    # Always returns a map of playernum -> {map of key -> value}
    def normalize_worlds_dict(self, worlds_dict):
        if 'World 1' not in worlds_dict:
            worlds_dict = {'World 1': worlds_dict}
        return {int(key.split()[1]): content for key, content in worlds_dict.items()}

    # Collect all the locations and items from the woth or playthrough.
    # locmaps is a map of key -> {map of loc -> item}
    # woth: key is "World x". modify 1p games to {"World 1": woth} first
    # playthrough: key is sphere index (unimportantish), loc has [Wx]
    def loc_item_collection(self, locmaps):
        # playernum -> location set
        locations = defaultdict(set)
        # playernum -> item -> count
        items = defaultdict(Counter)
        # location name -> item set
        locitems = defaultdict(set)
        for key, locmap in locmaps.items():
            p = 0
            if key.startswith('World'):
                p = int(key.split()[1])
            for loc, item_json in locmap.items():
                w = loc.split()[-1]
                if w[:2] == '[W':
                    p = int(w[2:-1])
                    loc = loc[:loc.rindex(' ')]
                elif p == 0:
                    # Assume single-player playthrough
                    p = 1
                locations[p].add(loc)
                if isinstance(item_json, dict):
                    item = item_json['item']
                    item_p = item_json.get('player', p)
                else:
                    item = item_json
                    item_p = p
                items[item_p][item] += 1
                locitems[loc].add(item)
        return locations, items, locitems

    def required_checks(self, spoiler, locations, items, locitems):
        # Checks to make against woth/playthrough:
        expected_none = {p: set() for p in items}
        # No 'never' items
        self.assertEqual(
            expected_none,
            {p: never & c.keys() for p, c in items.items()},
            'Non-required items deemed required')
        # No disabled locations
        disables = set(spoiler['settings'].get('disabled_locations', []))
        self.assertEqual(
            {p: set() for p in locations},  # keys might differ bt locations/items
            {p: disables & c for p, c in locations.items()},
            'Disabled locations deemed required')
        # No more than one of any 'once' item
        multi = {p: {it for it, ct in c.items() if ct > 1}
                 for p, c in items.items()}
        bottles_collected = {p: bottles & c.keys() for p, c in items.items()}
        self.assertEqual(
            expected_none,
            {p: once & multi[p] for p in items},
            'Collected unexpected items more than once')
        for p in items:
            if 'Rutos Letter' in multi[p]:
                multi[p].remove('Rutos Letter')
                bottles_collected[p].add('Rutos Letter')
        # Any item more than once is special['progressive']
        self.assertEqual(
            expected_none,
            {p: multi[p] - progressive for p in items},
            'Collected unexpected items more than once')
        # At most one bottle
        self.assertEqual(
            {p: 1 for p in items},
            {p: max(1, len(bottles & c.keys())) for p, c in items.items()},
            'Collected too many bottles')

    def verify_woth(self, spoiler):
        woth = spoiler[':woth_locations']
        if 'World 1' not in woth:
            woth = {'World 1': woth}
        self.required_checks(spoiler, *self.loc_item_collection(woth))

    def verify_playthrough(self, spoiler):
        pl = spoiler[':playthrough']
        locations, items, locitems = self.loc_item_collection(pl)
        self.required_checks(spoiler, locations, items, locitems)
        # Everybody reached the win condition in the playthrough
        if spoiler['settings'].get('triforce_hunt', False) or spoiler['randomized_settings'].get('triforce_hunt', False):
            item_pool = self.normalize_worlds_dict(spoiler['item_pool'])
            # playthrough assumes each player gets exactly the goal
            req = spoiler['settings'].get('triforce_goal_per_world', None) or spoiler['randomized_settings'].get('triforce_goal_per_world', None)
            self.assertEqual(
                {p: req or item_pool[p]['Triforce Piece']
                    for p in items},
                {p: c['Triforce Piece'] for p, c in items.items()},
                'Playthrough missing some (or having extra) Triforce Pieces')
        else:
            self.assertEqual(
                {p: 1 for p in items},
                {p: c['Triforce'] for p, c in items.items()},
                'Playthrough missing some (or having extra) Triforces')

    def verify_disables(self, spoiler):
        locmap = spoiler['locations']
        if 'World 1' not in locmap:
            locmap = {'World 1': locmap}
        disables = set(spoiler['settings'].get('disabled_locations', []))
        dmap = {k: {loc: v[loc] for loc in disables if loc in v}
                for k, v in locmap.items()}
        locations, items, locitems = self.loc_item_collection(dmap)
        if spoiler['settings'].get('item_pool_value') == 'ludicrous':
            junk_set = ludicrous_junk
        else:
            junk_set = junk

        # Only junk at disabled locations
        self.assertEqual(
            {loc: set() for loc in locitems},
            {loc: items - junk_set for loc, items in locitems.items()},
            'Disabled locations have non-junk')

    def test_testcases(self):
        test_files = [filename
                      for filename in os.listdir(test_dir)
                      if filename.endswith('.sav')]
        for filename in test_files:
            with self.subTest(filename=filename):
                settings = load_settings(filename, seed='TESTTESTTEST')
                main(settings)
                # settings.output_file contains the first part of the filename
                spoiler = load_spoiler('%s_Spoiler.json' % settings.output_file)
                self.verify_woth(spoiler)
                self.verify_playthrough(spoiler)
                self.verify_disables(spoiler)

    def test_presets(self):
        presetsFiles = get_preset_files()
        for fn in presetsFiles:
            with open(fn, encoding='utf-8') as f:
                presets = json.load(f)
            for name, settings_dict in presets.items():
                ofile = 'preset_' + re.sub(r'[^a-zA-Z0-9_-]+', '_', name)
                with self.subTest(name, filename=ofile):
                    settings = make_settings_for_test(
                            settings_dict, seed='TESTTESTTEST', outfilename=ofile, strict=False)
                    main(settings)
                    spoiler = load_spoiler('%s_Spoiler.json' % settings.output_file)
                    self.verify_woth(spoiler)
                    self.verify_playthrough(spoiler)
                    self.verify_disables(spoiler)

    # remove this to run the fuzzer
    @unittest.skip("generally slow and failures can be ignored")
    def test_fuzzer(self):
        random.seed()
        fuzz_settings = [Settings({
            'randomize_settings': True,
            'create_patch_file': False,
            'create_compressed_rom': False,
            'create_wad_file': False,
            'create_uncompressed_rom': False,
            'create_spoiler': True,
            'output_file': os.path.join(output_dir, 'fuzz-%d' % i),
        }) for i in range(10)]
        out_keys = ['randomize_settings', 'create_patch_file', 'create_compressed_rom', 'create_wad_file',
                    'create_uncompressed_rom', 'patch_without_output', 'create_spoiler', 'output_file', 'seed']
        for settings in fuzz_settings:
            output_file = '%s_Spoiler.json' % settings.output_file
            settings_file = '%s_%s_Settings.json' % (settings.output_file, settings.seed)
            with self.subTest(out=output_file, settings=settings_file):
                try:
                    main(settings, max_attempts=2)
                    spoiler = load_spoiler(output_file)
                    self.verify_woth(spoiler)
                    self.verify_playthrough(spoiler)
                    self.verify_disables(spoiler)
                except Exception as e:
                    # output the settings file in case of any failure
                    with open(settings_file, 'w') as f:
                        d = {k: settings.settings_dict[k] for k in out_keys}
                        json.dump(d, f, indent=0)
                    logging.getLogger('').exception(f'Failed to generate with these settings:\n{settings.get_settings_display()}\n')
                    raise


class TestTextShuffle(unittest.TestCase):
    def test_text_shuffle(self):
        if not os.path.isfile('./ZOOTDEC.z64'):
            self.skipTest("Base ROM file not available.")
        rom = Rom("./ZOOTDEC.z64")
        messages = read_messages(rom)
        shuffle_messages(messages)
        shuffle_messages(messages, False)

class TestSceneFlags(unittest.TestCase):
    def test_build_room_xflags(self):
        from SceneFlags import build_room_xflags, encode_room_xflags
        # Using Goron city child room 3 (main room with the goron pot)
        room_locations = [
            (41, 1), # Goron Pot Drop 1
            (41, 2), # Goron Pot Drop 2
            (41, 3), # Goron Pot Drop 3
            (41, 4), # Goron Pot Drop 4
            (41, 5), # Goron Pot Drop 5
            (41, 6), # Goron Pot Drop 6
            (41, 7), # Goron Pot Drop 7
            (41, 8), # Goron Pot Drop 8
            (42, 0), # Pot 1
            (43, 0), # Pot 2
            (44, 0), # Pot 3
            (45, 0), # Pot 4
            (46, 0), # Pot 5
        ]
        test_encoded = [0, 41, 1, 1, 9, 1, 1, 4]

        flags, bits = build_room_xflags(room_locations)
        diff, encoded = encode_room_xflags(flags)
        self.assertListEqual(test_encoded, encoded)

class TestCustomAudio(unittest.TestCase):
    def test_audiobank(self):
        AUDIOBANK_POINTER_TABLE = 0x00B896A0
        AUDIOBANK_ADDR = 0xD390
        AUDIOTABLE_INDEX_ADDR = 0xB8A1C0
        AUDIOTABLE_ADDR = 0x79470

        if not os.path.isfile('./ZOOTDEC.z64'):
            self.skipTest("Base ROM file not available.")

        rom: Rom = Rom("ZOOTDEC.z64")
        audiobank_file = rom.read_bytes(AUDIOBANK_ADDR, 0x1CA50)
        audiotable_index = rom.read_bytes(AUDIOTABLE_INDEX_ADDR, 0x80) # Read audiotable index into bytearray
        audiotable_file = rom.read_bytes(AUDIOTABLE_ADDR, 0x460AD0) # Read audiotable (samples) into bytearray
        rom_bytes: bytearray = rom.buffer
        audiobank_table_header = rom.read_bytes(AUDIOBANK_POINTER_TABLE, 0x10)
        num_banks = int.from_bytes(audiobank_table_header[0:2], 'big')
        audiobanks: list[AudioBank] = []
        for i in range(0, num_banks):
            curr_entry = rom.read_bytes(AUDIOBANK_POINTER_TABLE + 0x10 + (0x10 * i), 0x10)
            audiobank: AudioBank = AudioBank(curr_entry, audiobank_file, audiotable_file, audiotable_index)
            audiobanks.append(audiobank)
        self.assertEqual(num_banks, 0x26)
        self.assertEqual(audiobanks[0x25].bank_offset, 0x19110)
        self.assertEqual(audiobanks[0x25].size, 0x3940)
