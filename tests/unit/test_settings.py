import unittest
from pathlib import Path

import Main
import Settings
from Plandomizer import Distribution


class TestResolveSettings(unittest.TestCase):
    def test_settings_init(self):
        test_settings = Settings.Settings({})
        self.assertEqual(test_settings.settings_string, test_settings.get_settings_string())
        # How to test self.distribution: Distribution = Distribution(self)
        self.assertFalse(test_settings.numeric_seed is None)
        self.assertFalse(test_settings.custom_seed)

    def test_world_count_min(self):
        # TODO: The value checked in the assert should be constant to avoid needing to change this test for
        #       intentional changes.
        world_count_settings = Settings.Settings({'world_count': 0})
        self.assertEqual(world_count_settings.world_count, 1)

    def test_world_count_max(self):
        # TODO: The value checked in the assert should be constant to avoid needing to change this test for
        #       intentional changes.
        world_count_settings = Settings.Settings({'world_count': 256})
        self.assertEqual(world_count_settings.world_count, 255)

    def test_reset_distribution(self):
        disabled_location = "KF Midos Top Left Chest"
        test_settings = Settings.Settings({
            'disabled_locations': [disabled_location]
        })

        test_settings.reset_distribution()

        self.assertIn(disabled_location, test_settings.distribution.world_dists[0].locations)
        # Perhaps LocationRecord should be iterable e.g. locations[disabled_location]
        self.assertEqual('#Junk', test_settings.distribution.world_dists[0].locations.get(disabled_location).item)

    def test_load_distribution(self):
        distribution_file = Path(__file__, '..', '..', 'plando', 'plando-beehives.json')
        test_settings = Settings.Settings({
            'enable_distribution_file': True,
            'distribution_file': distribution_file.resolve()
        })
        old_seed = test_settings.numeric_seed

        test_settings.load_distribution()

        self.assertTrue(test_settings.shuffle_beehives)
        # Numeric seed is updated in many of these functions.
        self.assertNotEqual(old_seed, test_settings.numeric_seed,
                            "Seed was not updated after loading distribution file")

    def test_copy(self):
        distribution_file = Path(__file__, '..', '..', 'plando', 'plando-beehives.json')
        test_settings = Settings.Settings({
            'enable_distribution_file': True,
            'distribution_file': distribution_file.resolve()
        })
        test_settings.load_distribution()

        result_settings = test_settings.copy()

        for setting in test_settings.settings_dict:
            self.assertTrue(setting in result_settings.settings_dict, f"Setting {setting} was removed.")
            self.assertEqual(test_settings.settings_dict[setting], result_settings.settings_dict[setting],
                             f"{setting} was not copied. Was {test_settings.settings_dict[setting]} "
                             + f"is now {result_settings.settings_dict[setting]}")
            self.assertEqual(test_settings.__getattribute__(setting), result_settings.__getattribute__(setting))


if __name__ == '__main__':
    unittest.main()
