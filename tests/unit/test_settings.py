import unittest

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


if __name__ == '__main__':
    unittest.main()
