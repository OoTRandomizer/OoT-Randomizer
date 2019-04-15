# Run unittests with python -m unittest Unittest[.ClassName[.test_func]]

from collections import Counter, defaultdict
import json
import logging
import os
import unittest

from ItemList import item_table
from Main import main
from Settings import Settings

test_dir = os.path.join(os.path.dirname(__file__), 'tests')
output_dir = os.path.join(test_dir, 'Output')
os.makedirs(output_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO, filename=os.path.join(output_dir, 'LAST_TEST_LOG'), filemode='w')

# items never required:
# refills, maps, compasses, capacity upgrades, masks (not listed in logic)
never_prefix = ['Bombs', 'Arrows', 'Rupee', 'Deku Seeds', 'Map', 'Compass']
never_suffix = ['Mask', 'Capacity']
never = {
    'Bunny Hood', 'Mask of Truth', 'Recovery Heart', 'Milk', 'Ice Arrows', 'Ice Trap',
    'Double Defense', 'Serenade of Water', 'Prelude of Light', 'Biggoron Sword',
} | {item for item, (t, adv, _, special) in item_table.items() if adv is False
     or any(map(item.startswith, never_prefix)) or any(map(item.endswith, never_suffix))}

# items required at most once, specifically things with multiple possible names
# (except bottles)
once = {
    'Deku Nut', 'Deku Stick', 'Deku Shield', 'Hylian Shield',
    'Goron Tunic', 'Zora Tunic',
}

progressive = {
    item for item, (_, _, _, special) in item_table.items()
    if special and 'progressive' in special
}

bottles = {
    item for item, (_, _, _, special) in item_table.items()
    if special and 'bottle' in special and item != 'Deliver Letter'
}


def load_settings(settings_file):
    sfile = os.path.join(test_dir, settings_file)
    ofile = os.path.join(test_dir, 'Output', os.path.splitext(settings_file)[0])
    with open(sfile) as f:
        j = json.load(f)
    # Some consistent settings for testability
    j.update({
        'compress_rom': "None",
        'count': 1,
        'create_spoiler': True,
        'output_file': ofile,
    })
    return Settings(j)


def load_spoiler(json_file):
    with open(json_file) as f:
        return json.load(f)


class TestValidSpoilers(unittest.TestCase):

    # Collect all the locations and items from the woth or playthrough.
    # locmaps is a map of key -> {map of loc -> item}
    # woth: key is "World x". modify 1p games to {"World 1": woth} first
    # playthrough: key is sphere index (unimportantish), loc has [Wx]
    def loc_item_collection(self, locmaps):
        # map from playernum to list/Counter
        locations = defaultdict(list)
        items = defaultdict(Counter)
        for key, locmap in locmaps.items():
            p = 0
            if key.startswith('World'):
                p = int(key.split()[1])
            for loc, item_json in locmap.items():
                w = loc.split()[-1]
                if w[:2] == '[W':
                    p = int(w[2:-1])
                    loc = loc[:loc.rindex(' ')]
                else:
                    # Assume single-player playthrough
                    p = 1
                locations[p].append(loc)
                if isinstance(item_json, dict):
                    item = item_json['item']
                    item_p = item_json.get('player', p)
                else:
                    item = item_json
                    item_p = p
                # Canonicalize some stuff
                if not item.endswith('Capacity'):
                    for n in once:
                        if n in item:
                            item = n
                            break
                items[item_p][item] += 1
        # Checks to make against woth/playthrough:
        expected_none = {p: set() for p in items}
        # No 'never' items
        self.assertEqual(
            expected_none,
            {p: never & c.keys() for p, c in items.items()},
            'Non-required items deemed required')
        # No more than one of any 'once' item
        multi = {p: {it for it, ct in c.items() if ct > 1}
                 for p, c in items.items()}
        self.assertEqual(
            expected_none,
            {p: once & multi[p] for p in items},
            'Collected unexpected items more than once')
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
        return locations, items

    def verify_woth(self, spoiler):
        woth = spoiler[':woth_locations']
        if 'World 1' not in woth:
            woth = {'World 1': woth}
        locations, items = self.loc_item_collection(woth)

    def verify_playthrough(self, spoiler):
        pl = spoiler[':playthrough']
        locations, items = self.loc_item_collection(pl)
        # Everybody finished
        self.assertEqual(
            {p: 1 for p in items},
            {p: c['Triforce'] for p, c in items.items()},
            'Playthrough missing some (or having extra) Triforces')

    def test_spoiler(self):
        test_files = [filename
                      for filename in os.listdir(test_dir)
                      if filename.endswith('.sav')]
        for filename in test_files:
            with self.subTest(filename=filename):
                settings = load_settings(filename)
                main(settings)
                # settings.output_file contains the first part of the filename
                spoiler = load_spoiler('%s_Spoiler.json' % settings.output_file)
                self.verify_woth(spoiler)
                self.verify_playthrough(spoiler)

    def test_fuzzer(self):
        fuzz_settings = [Settings({
            'randomize_settings': True,
            'compress_rom': "None",
            'count': 1,
            'create_spoiler': True,
            'output_file': os.path.join(output_dir, 'fuzz-%d' % i),
        }) for i in range(10)]
        out_keys = ['randomize_settings', 'compress_rom', 'count',
                    'create_spoiler', 'output_file', 'seed', 'numeric_seed']
        for settings in fuzz_settings:
            output_file = '%s_Spoiler.json' % settings.output_file
            settings_file = '%s_%s_Settings.json' % (settings.output_file, settings.seed)
            with self.subTest(out=output_file, settings=settings_file):
                try:
                    main(settings)
                    spoiler = load_spoiler(output_file)
                    self.verify_woth(spoiler)
                    self.verify_playthrough(spoiler)
                except Exception as e:
                    # output the settings file in case of any failure
                    with open(settings_file, 'w') as f:
                        json.dump(settings.to_json(), f, indent=0)
                    raise

