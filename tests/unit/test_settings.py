import logging
import unittest
from pathlib import Path

import Settings
from Utils import local_path


class TestSettings(unittest.TestCase):
    def test_settings_init(self):
        test_settings = Settings.Settings({})
        self.assertEqual(
            test_settings.settings_string, test_settings.get_settings_string()
        )
        # How to test self.distribution: Distribution = Distribution(self)
        self.assertFalse(test_settings.numeric_seed is None)
        self.assertFalse(test_settings.custom_seed)

    def test_old_compress_setting_patch(self):
        test_settings = Settings.Settings({"compress_rom": "Patch"})

        self.assertTrue(test_settings.create_patch_file)
        self.assertFalse(test_settings.create_compressed_rom)
        self.assertFalse(test_settings.create_uncompressed_rom)
        self.assertRaises(
            AttributeError,
            lambda: "compress_rom" in test_settings.__getattribute__("compress_rom"),
        )

    def test_old_compress_setting_compressed(self):
        test_settings = Settings.Settings({"compress_rom": "True"})

        self.assertFalse(test_settings.create_patch_file)
        self.assertTrue(test_settings.create_compressed_rom)
        self.assertFalse(test_settings.create_uncompressed_rom)
        self.assertRaises(
            AttributeError,
            lambda: "compress_rom" in test_settings.__getattribute__("compress_rom"),
        )

    def test_old_compress_setting_uncompressed(self):
        test_settings = Settings.Settings({"compress_rom": "False"})

        self.assertFalse(test_settings.create_patch_file)
        self.assertFalse(test_settings.create_compressed_rom)
        self.assertTrue(test_settings.create_uncompressed_rom)
        self.assertRaises(
            AttributeError,
            lambda: "compress_rom" in test_settings.__getattribute__("compress_rom"),
        )

    def test_default_settings_strict(self):
        try:
            Settings.Settings({}, True)
        except (TypeError, ValueError, BaseException) as e:
            self.fail(f"Default settings no longer pass `validate_settings`\n{e}")

    def test_world_count_min(self):
        # TODO: The value checked in the assert should be constant to avoid needing to change this test for
        #       intentional changes.
        world_count_settings = Settings.Settings({"world_count": 0})
        self.assertEqual(world_count_settings.world_count, 1)

    def test_world_count_max(self):
        # TODO: The value checked in the assert should be constant to avoid needing to change this test for
        #       intentional changes.
        world_count_settings = Settings.Settings({"world_count": 256})
        self.assertEqual(world_count_settings.world_count, 255)

    def test_copy(self):
        distribution_file = local_path(
            Path("tests", "plando", "plando-beehives.json").__str__()
        )
        test_settings = Settings.Settings({})
        test_settings.enable_distribution_file = True
        test_settings.distribution_file = distribution_file
        test_settings.load_distribution()

        result_settings = test_settings.copy()

        for setting in test_settings.settings_dict:
            self.assertTrue(
                setting in result_settings.settings_dict,
                f"Setting {setting} was removed.",
            )
            self.assertEqual(
                test_settings.settings_dict[setting],
                result_settings.settings_dict[setting],
                f"{setting} was not copied. Was {test_settings.settings_dict[setting]} "
                + f"is now {result_settings.settings_dict[setting]}",
            )
            self.assertEqual(
                test_settings.__getattribute__(setting),
                result_settings.__getattribute__(setting),
            )

    # Settings.update() is already tested as part of init
    # Settings.get_settings_display() unsure if worth testing. Would probably be done via regex
    # Settings.get_settings_string() and Settings.update_with_settings_string()
    #   may be outside of my knowledge for testing

    def test_get_numeric_seed_is_consistent(self):
        test_settings = Settings.Settings({"seed": "unittest"})
        duplicate_seed = Settings.Settings({})
        duplicate_seed.seed = "unittest"

        self.assertEqual(
            test_settings.get_numeric_seed(),
            duplicate_seed.get_numeric_seed(),
            f"Using the same seed value resulted in different numeric seeds.",
        )

    def test_sanitize_seed(self):
        test_settings = Settings.Settings({})
        test_settings.seed = "unit!test"

        test_settings.sanitize_seed()

        self.assertEqual(test_settings.seed, "unittest")

    # Settings.update_seed implicitly tested in test_get_numeric_seed_consistent

    def test_load_distribution(self):
        test_settings = Settings.Settings({})
        old_seed = test_settings.numeric_seed

        test_settings.load_distribution()

        self.assertFalse(test_settings.enable_distribution_file)
        self.assertFalse(test_settings.distribution_file)
        self.assertEqual(
            old_seed,
            test_settings.numeric_seed,
            "Seed was updated even though no distribution file was loaded",
        )

    def test_load_distribution_file(self):
        distribution_file = local_path(
            Path("tests", "plando", "plando-beehives.json").__str__()
        )
        test_settings = Settings.Settings({})
        test_settings.enable_distribution_file = True
        test_settings.distribution_file = distribution_file
        old_seed = test_settings.numeric_seed

        test_settings.load_distribution()

        self.assertTrue(test_settings.shuffle_beehives)
        self.assertNotEqual(
            old_seed,
            test_settings.numeric_seed,
            "Seed was not updated after loading distribution file",
        )

    def test_load_distribution_invalid_file_disables_distribution_file(self):
        distribution_file = local_path(
            Path("tests", "bad file does not exist").__str__()
        )
        test_settings = Settings.Settings({})
        test_settings.enable_distribution_file = True
        test_settings.distribution_file = distribution_file
        old_seed = test_settings.numeric_seed

        test_settings.load_distribution()

        self.assertFalse(test_settings.enable_distribution_file)
        self.assertEqual(
            old_seed,
            test_settings.numeric_seed,
            "Seed was updated even though no distribution file was loaded",
        )

    def test_load_distribution_no_file_disables_distribution_file(self):
        test_settings = Settings.Settings({})
        test_settings.enable_distribution_file = True
        old_seed = test_settings.numeric_seed

        test_settings.load_distribution()

        self.assertFalse(test_settings.enable_distribution_file)
        self.assertEqual(
            old_seed,
            test_settings.numeric_seed,
            "Seed was updated even though no distribution file was loaded",
        )

    def test_load_distribution_file_not_enabled_stays_disabled(self):
        distribution_file = local_path(
            Path("tests", "plando", "plando-beehives.json").__str__()
        )
        test_settings = Settings.Settings({})
        test_settings.distribution_file = distribution_file
        old_seed = test_settings.numeric_seed

        test_settings.load_distribution()

        self.assertFalse(test_settings.enable_distribution_file)
        self.assertEqual(
            old_seed,
            test_settings.numeric_seed,
            "Seed was updated even though no distribution file was loaded",
        )

    def test_reset_distribution(self):
        disabled_location = "KF Midos Top Left Chest"
        test_settings = Settings.Settings({})
        test_settings.disabled_locations.append(disabled_location)

        test_settings.reset_distribution()

        self.assertIn(
            disabled_location, test_settings.distribution.world_dists[0].locations
        )
        # Perhaps LocationRecord should be iterable e.g. locations[disabled_location]
        self.assertEqual(
            "#Junk",
            test_settings.distribution.world_dists[0]
            .locations.get(disabled_location)
            .item,
        )

    # get_settings_display
    # get_settings_string
    # update_with_settings_string
    # check_dependency
    # get_dependency
    # remove_disabled
    # resolve_random_settings
    # to_json
    # to_json_cosmetics


if __name__ == "__main__":
    unittest.main()
