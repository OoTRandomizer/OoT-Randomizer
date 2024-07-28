import os
import unittest

import Main
import Settings


class TestResolveSettings(unittest.TestCase):
    def setUp(self):
        self.default_settings = Settings.Settings(
            {'show_seed_info': True, 'user_message': '', 'world_count': 1, 'create_spoiler': True,
             'password_lock': False, 'randomize_settings': False, 'logic_rules': 'glitchless',
             'reachable_locations': 'all', 'triforce_hunt': False, 'triforce_count_per_world': 30,
             'triforce_goal_per_world': 20, 'lacs_condition': 'vanilla', 'lacs_medallions': 6, 'lacs_stones': 3,
             'lacs_rewards': 9, 'lacs_tokens': 100, 'lacs_hearts': 20, 'bridge': 'medallions', 'bridge_medallions': 6,
             'bridge_stones': 3, 'bridge_rewards': 9, 'bridge_tokens': 100, 'bridge_hearts': 20, 'trials_random': False,
             'trials': 6, 'shuffle_ganon_bosskey': 'dungeon', 'ganon_bosskey_medallions': 6, 'ganon_bosskey_stones': 3,
             'ganon_bosskey_rewards': 9, 'ganon_bosskey_tokens': 100, 'ganon_bosskey_hearts': 20,
             'shuffle_dungeon_rewards': 'reward', 'shuffle_bosskeys': 'dungeon', 'shuffle_smallkeys': 'dungeon',
             'shuffle_hideoutkeys': 'vanilla', 'shuffle_tcgkeys': 'vanilla', 'key_rings_choice': 'off', 'key_rings': [],
             'keyring_give_bk': False, 'shuffle_silver_rupees': 'vanilla', 'silver_rupee_pouches_choice': 'off',
             'silver_rupee_pouches': [], 'shuffle_mapcompass': 'dungeon', 'enhance_map_compass': False,
             'open_forest': 'closed', 'open_kakariko': 'closed', 'open_door_of_time': False, 'zora_fountain': 'closed',
             'gerudo_fortress': 'normal', 'dungeon_shortcuts_choice': 'off', 'dungeon_shortcuts': [],
             'starting_age': 'child', 'mq_dungeons_mode': 'vanilla', 'mq_dungeons_specific': [], 'mq_dungeons_count': 0,
             'empty_dungeons_mode': 'none', 'empty_dungeons_specific': [], 'empty_dungeons_rewards': [],
             'empty_dungeons_count': 2, 'shuffle_interior_entrances': 'off', 'shuffle_hideout_entrances': False,
             'shuffle_grotto_entrances': False, 'shuffle_dungeon_entrances': 'off', 'shuffle_bosses': 'off',
             'shuffle_overworld_entrances': False, 'shuffle_gerudo_valley_river_exit': False, 'owl_drops': False,
             'warp_songs': False, 'spawn_positions': [], 'free_bombchu_drops': True, 'one_item_per_dungeon': False,
             'shuffle_song_items': 'song', 'shopsanity': 'off', 'shopsanity_prices': 'random', 'tokensanity': 'off',
             'shuffle_scrubs': 'off', 'shuffle_child_trade': [], 'shuffle_freestanding_items': 'off',
             'shuffle_pots': 'off', 'shuffle_empty_pots': False, 'shuffle_crates': 'off', 'shuffle_empty_crates': False,
             'shuffle_cows': False, 'shuffle_beehives': False, 'shuffle_wonderitems': False,
             'shuffle_kokiri_sword': True, 'shuffle_ocarinas': False, 'shuffle_gerudo_card': False,
             'shuffle_beans': False, 'shuffle_expensive_merchants': False, 'shuffle_frog_song_rupees': False,
             'shuffle_individual_ocarina_notes': False, 'shuffle_loach_reward': 'off',
             'logic_no_night_tokens_without_suns_song': False, 'disabled_locations': [], 'allowed_tricks': [],
             'starting_items': {}, 'start_with_consumables': False, 'start_with_rupees': False, 'starting_hearts': 3,
             'skip_reward_from_rauru': False, 'no_escape_sequence': False, 'no_guard_stealth': False,
             'no_epona_race': False, 'skip_some_minigame_phases': False, 'complete_mask_quest': False,
             'useful_cutscenes': False, 'fast_chests': True, 'free_scarecrow': False, 'fast_bunny_hood': False,
             'auto_equip_masks': False, 'plant_beans': False, 'chicken_count_random': False, 'chicken_count': 7,
             'big_poe_count_random': False, 'big_poe_count': 10, 'easier_fire_arrow_entry': False, 'fae_torch_count': 3,
             'ruto_already_f1_jabu': False, 'ocarina_songs': 'off', 'correct_chest_appearances': 'off',
             'chest_textures_specific': ['major', 'bosskeys', 'keys', 'tokens', 'hearts'],
             'soa_unlocks_chest_texture': False, 'minor_items_as_major_chest': [], 'invisible_chests': False,
             'correct_potcrate_appearances': 'textures_unchecked',
             'potcrate_textures_specific': ['major', 'bosskeys', 'keys', 'tokens', 'hearts'],
             'soa_unlocks_potcrate_texture': False, 'key_appearance_match_dungeon': False, 'clearer_hints': True,
             'hints': 'always', 'hint_dist': 'balanced', 'item_hints': [], 'hint_dist_user': {},
             'misc_hints': ['altar', 'ganondorf', 'warp_songs_and_owls'], 'text_shuffle': 'none',
             'damage_multiplier': 'normal', 'deadly_bonks': 'none', 'no_collectible_hearts': False,
             'starting_tod': 'default', 'blue_fire_arrows': False, 'fix_broken_drops': False,
             'item_pool_value': 'balanced', 'junk_ice_traps': 'normal', 'ice_trap_appearance': 'major_only',
             'adult_trade_shuffle': False,
             'adult_trade_start': ['Pocket Egg', 'Pocket Cucco', 'Cojiro', 'Odd Mushroom', 'Odd Potion', 'Poachers Saw',
                                   'Broken Sword', 'Prescription', 'Eyeball Frog', 'Eyedrops', 'Claim Check']})

    def test_default_settings(self):
        can_use_rom = os.path.isfile('./ZOOTDEC.z64')
        if not can_use_rom:
            test_settings = Settings.Settings({
                # Don't require a ROM
                'create_compressed_rom': False,
            })
        else:
            test_settings = Settings.Settings({})

        # TODO: The actual changing of settings is a side effect. Should be explicit.
        Main.resolve_settings(test_settings)

        for setting in self.default_settings.settings_dict:
            self.assertTrue(setting in test_settings.settings_dict, f"Setting {setting} was removed.")
            if setting == 'seed':
                continue
            elif setting == 'create_compressed_rom' and not can_use_rom:
                self.assertTrue(self.default_settings.create_compressed_rom,
                                f"Default for {setting} changed. Should be {True}")
            elif setting in ['lacs_medallions', 'lacs_stones', 'lacs_rewards', 'lacs_tokens', 'lacs_hearts',
                             'bridge_stones', 'bridge_rewards', 'bridge_tokens', 'bridge_hearts',
                             'ganon_bosskey_medallions', 'ganon_bosskey_stones', 'ganon_bosskey_rewards',
                             'ganon_bosskey_tokens', 'ganon_bosskey_hearts']:
                self.assertFalse(test_settings.settings_dict[setting] == self.default_settings.settings_dict[setting],
                                 f"Default for {setting} changed. Was {self.default_settings.settings_dict[setting]} "
                                 + f"is now {test_settings.settings_dict[setting]}")
                self.assertEqual(test_settings.settings_dict[setting], 0,
                                 f"{setting} is no longer disabled after resolving settings.")
            else:
                self.assertEqual(test_settings.settings_dict[setting], self.default_settings.settings_dict[setting],
                                 f"Default for {setting} changed. Was {self.default_settings.settings_dict[setting]} "
                                 + f"is now {test_settings.settings_dict[setting]}")
                self.assertEqual(test_settings.__getattribute__(setting), self.default_settings.__getattribute__(setting))

        for setting in test_settings.settings_dict:
            if setting == 'create_compressed_rom' and not can_use_rom:
                continue
            self.assertTrue(setting in test_settings.settings_dict,
                            f"Setting {setting} was added. Add it to this test.")


if __name__ == '__main__':
    unittest.main()
