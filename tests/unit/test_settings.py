from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

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

    def test_get_numeric_seed_is_consistent(self):
        test_settings = Settings.Settings({"seed": "unittest"})
        duplicate_seed = Settings.Settings({})
        duplicate_seed.seed = "unittest"

        self.assertEqual(
            test_settings.get_numeric_seed(),
            duplicate_seed.get_numeric_seed(),
            f"Using the same seed value resulted in different numeric seeds.",
        )

    def test_copy(self):
        distribution_file = local_path(
            Path("tests", "plando", "plando-beehives.json").__str__()
        )
        test_settings = Settings.Settings({})
        test_settings.enable_distribution_file = True
        test_settings.distribution_file = distribution_file
        test_settings.load_distribution()

        result_settings = test_settings.copy()

        self.assert_settings_objects_are_equal(
            result_settings, test_settings, False, {}
        )

    def test_update_with_default_settings_string(self):
        default_settings_string = "BSAWDNCAX2TB2XCHGA3UL62ANEBBABADFAAAAAAEAASAAAAAJAAAAAAAAAAAE2FKA6A86AAJNJACAAF2D"
        default_settings = Settings.Settings({})
        test_settings = Settings.Settings({})

        test_settings.update_with_settings_string(default_settings_string)

        self.assert_settings_objects_are_equal(
            default_settings, test_settings, True, {}
        )

    def test_update_with_modified_settings_string(self):
        modified_settings_string = "BSAWDNCAX2TB2XCHGA3UL62ANEBBABADFAAAAAAEAASAAAAAJASFAAAAAAAAAASAZEBSD2VDAATBBJAAWAR"
        default_settings = Settings.Settings({})
        test_settings = Settings.Settings({})

        test_settings.update_with_settings_string(modified_settings_string)

        self.assert_settings_objects_are_equal(
            default_settings,
            test_settings,
            True,
            {"disabled_locations": ["KF Midos Top Left Chest"]},
        )

    def test_get_setting_string_hell_mode(self):
        # Not sure that this test even does anything useful.
        hell_mode_setting_string = "BSANNNNAX2TBJYCHGA35L62AWPZFAGA2EAAKSBAEQ79N29ZE99BAA9HAAAAAA2FK26S6APAAJYDSW9"
        default_settings = Settings.Settings({})
        test_settings = Settings.Settings({})
        test_settings.update_with_settings_string(hell_mode_setting_string)

        result = test_settings.get_settings_string()

        self.assertNotEqual(default_settings.settings_string, result)
        self.assertEqual(test_settings.settings_string, result)

    def test_sanitize_seed(self):
        test_settings = Settings.Settings({})
        test_settings.seed = "unit!test"

        test_settings.sanitize_seed()

        self.assertEqual(test_settings.seed, "unittest")

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

    # Settings.update_seed implicitly tested in test_get_numeric_seed_consistent

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

        test_settings.disabled_locations.clear()  # BUG: Using mutable data that is evaluated once at definition time and used over and over.

    def test_check_dependency_randomized_setting(self):
        test_settings = Settings.Settings({"randomize_settings": True})

        result = test_settings.check_dependency(
            "bridge", True
        )  # check_random is always True when used

        self.assertFalse(result)

    def test_check_dependency_non_randomized_setting(self):
        test_settings = Settings.Settings({"randomize_settings": True})

        result = test_settings.check_dependency(
            "logic_rules", True
        )  # check_random is always True when used

        self.assertTrue(result)

    def test_check_dependency_randomizable_setting_not_randomized(self):
        test_settings = Settings.Settings({})

        result = test_settings.check_dependency("bridge", True)

        self.assertTrue(result)

    def test_get_dependency_randomized_setting(self):
        test_settings = Settings.Settings({"randomize_settings": True})

        result = test_settings.get_dependency("bridge", True)

        self.assertEqual(result, test_settings.settings_dict["bridge"])

    def test_get_dependency_setting_not_randomized(self):
        test_settings = Settings.Settings({"randomize_settings": True})

        result = test_settings.get_dependency("logic_rules", True)

        self.assertIsNone(result)

    def test_get_dependency_randomizable_setting_not_randomized(self):
        test_settings = Settings.Settings({})

        result = test_settings.get_dependency("logic_rules", True)

        self.assertIsNone(result)

    def test_get_dependency_no_dependency(self):
        test_settings = Settings.Settings({})

        result = test_settings.get_dependency("seed", True)

        self.assertIsNone(result)

    def test_remove_disabled(self):
        # Should probably be private
        test_settings = Settings.Settings({"starting_age": "adult"})

        test_settings.remove_disabled()

        self.assertEqual(test_settings.settings_dict["starting_age"], "child")

    # resolve_random_settings
    # Should probably be private

    def assert_settings_objects_are_equal(
        self,
        original_settings: Settings,
        modified_settings: Settings,
        skip_seed: bool,
        except_for: dict[str, Any],
    ):
        for setting in modified_settings.settings_dict:
            self.assertTrue(
                setting in original_settings.settings_dict,
                f"Setting {setting} was removed.",
            )

            if setting == "seed" and skip_seed:
                continue
            elif setting in except_for:
                self.assertEqual(
                    modified_settings.settings_dict[setting], except_for[setting]
                )
                continue

            self.assertEqual(
                modified_settings.settings_dict[setting],
                original_settings.settings_dict[setting],
                f"{setting} was not copied. Was"
                f" {modified_settings.settings_dict[setting]} "
                + f"is now {original_settings.settings_dict[setting]}",
            )
            self.assertEqual(
                modified_settings.__getattribute__(setting),
                original_settings.__getattribute__(setting),
            )


if __name__ == "__main__":
    unittest.main()
