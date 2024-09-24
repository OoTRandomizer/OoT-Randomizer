from __future__ import annotations
import difflib
import json
from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional, Any

import Colors
from Hints import hint_dist_list, hint_dist_tips, gossipLocations
from Item import ItemInfo
from Location import LocationIterator
from LocationList import location_table
from Models import get_model_choices
from SettingsListTricks import logic_tricks
from SettingTypes import SettingInfo, SettingInfoStr, SettingInfoList, SettingInfoDict, Textbox, Button, Checkbutton, \
    Combobox, Radiobutton, Fileinput, Directoryinput, Textinput, ComboboxInt, Scale, Numberinput, MultipleSelect, \
    SearchBox
import Sounds
import StartingItems
from Utils import data_path

if TYPE_CHECKING:
    from Entrance import Entrance


class SettingInfos:
    # Internal & Non-GUI Settings
    aliases = SettingInfoList(None, None, False)
    cosmetics_only = Checkbutton(None)
    check_version = Checkbutton(None)
    checked_version = SettingInfoStr(None, None)
    output_settings = Checkbutton(None)
    patch_without_output = Checkbutton(None)
    generating_patch_file = Checkbutton(None)
    output_file = SettingInfoStr(None, None)
    seed = SettingInfoStr(None, None)

    # GUI Only Buttons/Text

    output_types = Textbox(
        gui_text = "Output Types",
    )

    open_output_dir = Button(
        gui_text   = "Open Output Directory",
        gui_params = {
            'function':      "openOutputDir",
            'no_line_break': True,
        },
    )

    open_python_dir = Button(
        gui_text   = "Open App Directory",
        gui_params = {
            'function':      "openPythonDir",
        },
    )

    tricks_list_msg = Textbox(
        gui_text   = "Your current logic setting does not support the enabling of tricks.",
        gui_params = {
            "hide_when_disabled": True,
        },
    )

    model_unavailable_msg = Textbox(
        gui_text   = "Models can only be customized when patching.",
        gui_params = {
            "hide_when_disabled": True,
        },
    )

    sfx_link_unavailable_msg = Textbox(
        gui_text   = "Link's Voice can only be customized when patching.",
        gui_params = {
            "hide_when_disabled": True
        },
    )

    custom_music_unavailable_msg = Textbox(
        gui_text   = "Custom music can only be added when patching.",
        gui_params = {
            "hide_when_disabled": True,
        },
    )

    # Web Only Settings

    web_wad_file = Fileinput(
        gui_text    = "WAD File",
        gui_tooltip = "Your original OoT 1.2 NTSC-U / NTSC-J WAD file (.wad)",
        gui_params  = {
            "file_types": [
                {
                  "name": "WAD Files",
                  "extensions": ["wad"]
                },
                {
                  "name": "All Files",
                  "extensions": ["*"]
                },
            ],
            "hide_when_disabled": True,
        },
    )

    web_common_key_file = Fileinput(
        gui_text    = "Wii Common Key File",
        gui_tooltip = """\
            The Wii Common Key is a copyrighted 32 character string needed for WAD encryption.
            Google to find it! Do not ask on Discord!
        """,
        gui_params  = {
            "file_types": [
                {
                  "name": "BIN Files",
                  "extensions": ["bin"]
                },
                {
                  "name": "All Files",
                  "extensions": ["*"]
                },
            ],
            "hide_when_disabled": True,
        },
    )

    web_common_key_string = Textinput(
        gui_text    = "Alternatively Enter Wii Common Key",
        gui_tooltip = """\
            The Wii Common Key is a copyrighted 32 character string needed for WAD encryption.
            Google to find it! Do not ask on Discord!
        """,
        gui_params  = {
            "size":               "full",
            "max_length":         32,
            "hide_when_disabled": True,
        },
    )

    web_wad_channel_id = Textinput(
        gui_text    = "WAD Channel ID",
        default     = "NICE",
        gui_tooltip = """\
            4 characters, should end with E to ensure Dolphin compatibility.
            Note: If you have multiple OoTR WAD files with different Channel IDs installed, the game can crash on a soft reset. Use a Title Deleter to remove old WADs.
        """,
        gui_params  = {
            "size":               "small",
            "max_length":         4,
            "no_line_break":      True,
            "hide_when_disabled": True,
        },
    )

    web_wad_channel_title = Textinput(
        gui_text    = "WAD Channel Title",
        default     = "OoTRandomizer",
        gui_tooltip = "20 characters max",
        gui_params  = {
            "size":               "medium",
            "max_length":         20,
            "hide_when_disabled": True,
        },
    )

    web_wad_legacy_mode = Checkbutton(
        gui_text       = 'WAD Legacy Mode',
        default        = False,
        gui_tooltip    = "Enabling this will avoid any patching of the VC emulator in case your Wii does not have support for it. Recommended to be left unchecked.",
        gui_params  = {
            "no_line_break":      False,
            "hide_when_disabled": True,
        },
    )

    web_output_type = Radiobutton(
        gui_text   = "Output Type",
        choices    = {
            'z64': ".z64 (N64/Emulator)",
            'wad': ".wad (WiiVC)",
        },
        gui_params  = {
            "hide_when_disabled": True,
        },
        default    = "z64",
        disable    = {
            'z64': {
                'settings': [
                    'web_wad_file', 'web_common_key_file', 'web_common_key_string',
                    'web_wad_channel_id', 'web_wad_channel_title', 'web_wad_legacy_mode',
                ],
            },
        },
    )

    web_persist_in_cache = Checkbutton(
        gui_text       = 'Persist Files in Cache',
        default        = True,
    )

    # General Settings

    generate_from_file = Checkbutton(
        gui_text       = 'Generate From Patch File',
        default        = False,
        disable        = {
            True: {
                'tabs':     ['main_tab', 'detailed_tab', 'starting_tab', 'other_tab'],
                'sections': ['preset_section'],
                'settings': ['count', 'create_spoiler', 'world_count', 'enable_distribution_file', 'distribution_file', 'create_patch_file', 'show_seed_info', 'user_message'],
            },
            False: {
                'settings': ['repatch_cosmetics'],
            },
        },
        gui_params     = {
            'web:disable': {
                False: {
                    'settings': [
                        'rom', 'web_output_type', 'player_num',
                        'web_wad_file', 'web_common_key_file', 'web_common_key_string',
                        'web_wad_channel_id', 'web_wad_channel_title', 'web_wad_legacy_mode',
                        'model_adult', 'model_child', 'model_adult_filepicker', 'model_child_filepicker',
                        'sfx_link_adult', 'sfx_link_child', 'custom_music_directorypicker'
                    ],
                },
                True: {
                    'settings': [
                        'model_adult', 'model_child', 'model_unavailable_msg',
                        'sfx_link_unavailable_msg', 'custom_music_unavailable_msg'
                    ],
                },
            },
            'electron:disable': {
                False: {
                    'settings': [
                        'model_adult_filepicker', 'model_child_filepicker', 'model_unavailable_msg',
                        'sfx_link_unavailable_msg', 'custom_music_directorypicker', 'custom_music_unavailable_msg'
                    ],
                },
                True: {
                    'settings': [
                        'model_adult_filepicker', 'model_child_filepicker', 'model_unavailable_msg',
                        'sfx_link_unavailable_msg', 'custom_music_directorypicker', 'custom_music_unavailable_msg'
                    ],
                },
            },
        },
    )

    enable_distribution_file = Checkbutton(
        gui_text       = 'Enable Plandomizer (Advanced)',
        gui_tooltip    = '''\
            Optional. Use a plandomizer JSON file to get
            total control over the item placement.
        ''',
        gui_params     = {
            'no_line_break': True,
        },
        default        = False,
        disable        = {
            False: {'settings': ['distribution_file']},
        },
        shared         = False,
    )

    enable_cosmetic_file = Checkbutton(
        gui_text       = 'Enable Cosmetic Plandomizer (Advanced)',
        gui_tooltip    = '''\
            Optional. Use a cosmetic plandomizer JSON file to get
            more control over your cosmetic and sound settings.
        ''',
        default        = False,
        disable        = {
            False: {'settings': ['cosmetic_file']},
        },
        shared         = False,
    )

    distribution_file = Fileinput(
        gui_text    = "Plandomizer File",
        gui_tooltip = """\
            Optional. Place a plandomizer JSON file here
            to get total control over the item placement.
        """,
        gui_params = {
            "file_types": [
                {
                  "name": "JSON Files",
                  "extensions": ["json"]
                },
                {
                  "name": "All Files",
                  "extensions": ["*"]
                },
            ],
            "hide_when_disabled": True,
        },
    )

    cosmetic_file = Fileinput(
        gui_text    = "Cosmetic Plandomizer File",
        gui_tooltip = """\
            Optional. Use a cosmetic plandomizer JSON file to get
            more control over your cosmetic and sound settings.
        """,
        gui_params = {
            "file_types": [
                {
                  "name": "JSON Files",
                  "extensions": ["json"]
                },
                {
                  "name": "All Files",
                  "extensions": ["*"]
                },
            ],
            "hide_when_disabled": True,
        },
    )

    rom = Fileinput(
        gui_text   = "Base ROM",
        gui_params = {
            "file_types": [
                {
                  "name": "ROM Files",
                  "extensions": ["z64", "n64"]
                },
                {
                  "name": "All Files",
                  "extensions": ["*"]
                },
            ],
            "web:hide_when_disabled": True,
        },
    )

    output_dir = Directoryinput(
        gui_text   = "Output Directory",
    )

    show_seed_info = Checkbutton(
        gui_text       = 'Show Seed Info on File Screen',
        shared         = True,
        gui_tooltip    = '''\
            Display the version number, generation time, and user
            message on the file screen.
        ''',
        default        = True,
        disable        = {
            False: {'settings': ["user_message"]},
        },
        gui_params = {
            "hide_when_disabled": True,
        },
    )

    user_message = Textinput(
        gui_text       = "User-Configurable Message",
        shared         = True,
        gui_tooltip    = """\
            Add a custom message to the seed info.
        """,
        default        = "",
        gui_params     = {
            "size":               "full",
            "max_length":         42,
            "hide_when_disabled": True,
        },
    )

    patch_file = Fileinput(
        gui_text   = "Patch File",
        gui_params = {
            "file_types": [
                {
                  "name": "Patch File Archive",
                  "extensions": ["zpfz", "zpf", "patch"]
                },
                {
                  "name": "All Files",
                  "extensions": ["*"]
                },
            ],
        },
    )

    count = Numberinput(
        gui_text       = "Generation Count",
        shared         = False,
        default        = 1,
        minimum        = 1,
    )

    world_count = Numberinput(
        gui_text       = "Player Count",
        shared         = True,
        default        = 1,
        minimum        = 1,
        maximum        = 255,
        gui_params     = {
            'no_line_break':     True,
            'web:max':           15,
            'web:no_line_break': True,
        },
    )

    player_num = Numberinput(
        gui_text       = "Player ID",
        shared         = False,
        default        = 1,
        minimum        = 1,
        maximum        = 255,
    )

    repatch_cosmetics = Checkbutton(
        gui_text       = 'Override Original Cosmetics',
        default        = True,
        disable        = {
            False: {
                'tabs':     ['cosmetics_tab', 'sfx_tab'],
                'settings': ['create_cosmetics_log', 'enable_cosmetic_file', 'cosmetic_file'],
            },
        },
        shared         = False,
    )

    create_spoiler = Checkbutton(
        gui_text       = 'Create Spoiler Log',
        gui_tooltip    = '''\
                         Enabling this will change the seed.
                         Warning: Only disable this if you don't want any help in solving this seed!
                         ''',
        default        = True,
        gui_params     = {
            'no_line_break':     True,
            'web:no_line_break': False,
        },
        shared         = True,
    )

    create_cosmetics_log = Checkbutton(
        gui_text         = 'Create Cosmetics Log',
        gui_tooltip      = '''\
                 Cosmetics Logs are only output if one of the output types below are enabled.
                 ''',
        default          = True,
        disabled_default = False,
    )

    create_patch_file = Checkbutton(
        gui_text       = '.zpf (Patch File)',
        gui_tooltip    = '''\
            Patch files are used to send the patched data to other
            people without sending the ROM file.
        ''',
        shared         = False,
        gui_params     = {
            "no_line_break": True,
        },
    )

    create_compressed_rom = Checkbutton(
        gui_text       = '.z64 (N64/Emulator)',
        default        = True,
        gui_tooltip    = '''\
            A "compressed" .z64 ROM file for use on
            N64 emulators or with an N64 flash cart.
        ''',
        shared         = False,
        gui_params     = {
            "no_line_break": True,
        },
    )

    create_wad_file = Checkbutton(
        gui_text       = '.wad (Wii VC)',
        gui_tooltip    = '''\
            .wad files are used to play on Wii Virtual Console or Dolphin Emulator.
        ''',
        shared         = False,
        disable        = {
            False: {'settings': ['wad_file', 'wad_channel_title', 'wad_channel_id']},
        },
        gui_params     = {
            "no_line_break": True,
        },
    )

    create_uncompressed_rom = Checkbutton(
        gui_text       = 'Uncompressed ROM (Development)',
        gui_tooltip    = '''\
            Uncompressed ROMs may be helpful for developers
            but should not be used to play through a seed
            normally as it will very likely cause crashes.
            Use a compressed ROM instead.
        ''',
        shared         = False,
    )

    wad_file = Fileinput(
        gui_text    = "Base WAD File",
        gui_tooltip = "Your original OoT 1.2 NTSC-U / NTSC-J WAD file (.wad)",
        gui_params  = {
            "file_types": [
                {
                  "name": "WAD Files",
                  "extensions": ["wad"]
                },
                {
                  "name": "All Files",
                  "extensions": ["*"]
                },
            ],
            "hide_when_disabled": True,
        },
    )

    wad_channel_id = Textinput(
        gui_text    = "WAD Channel ID",
        default     = "NICE",
        gui_tooltip = """\
            4 characters, should end with E to ensure Dolphin compatibility.
            Note: If you have multiple OoTR WAD files with different Channel IDs installed, the game can crash on a soft reset. Use a Title Deleter to remove old WADs.
        """,
        gui_params  = {
            "size":               "small",
            "max_length":         4,
            "no_line_break":      True,
            "hide_when_disabled": True,
        },
    )

    wad_channel_title = Textinput(
        gui_text    = "WAD Channel Title",
        default     = "OoTRandomizer",
        gui_tooltip = "20 characters max",
        gui_params  = {
            "size":               "medium",
            "max_length":         20,
            "hide_when_disabled": True,
        },
    )

    presets = SettingInfoStr(
        gui_text       = "",
        gui_type       = "Presetinput",
        default        = "[New Preset]",
        gui_tooltip    = '''\
            Select a setting preset to apply.

            Default/Beginner is aimed at those familiar with the vanilla game who desire a similar progression.
            Uses base glitchless logic. No timesavers (See the tab "Other") are enabled in this preset
            and the world begins closed. Expect a long playthrough.

            Easy Mode is aimed at those who have perhaps seen a few randomizer runs previously and/or
            wish to dive right in. Uses base glitchless logic. Most timesavers (See the tab "Other")
            are enabled and the world is more open after leaving Kokiri Forest.

            Hell Mode is designed to be as frustrating an experience as possible, with every setting enabled
            to provide maximum randomness as well as things like one-hit-KO, one-bonk-KO and max ice traps.
            It still uses glitchless logic to ensure a beatable seed. However, be aware that all glitchless
            "tricks" are enabled which have the potential to require the player to perform difficult techniques.
            Expect a long and painful playthrough, even with good note-taking.

            The other presets are for racing and/or tournaments.

            After a preset is loaded, the settings can be viewed/changed in the other tabs before
            generating a seed.
            ''',
    )

    password_lock = Checkbutton(
        gui_text         = "Lock Seed Behind Password",
        gui_tooltip      = '''\
            Starting the seed will be locked behind a password provided in the spoiler log.
            The password is a sequence of 6 button presses (A and C).
        ''',
        shared           = True,
        gui_params       = {
            'optional': True,
        },
    )

    # Main Rules (and "Guarantee Reachable Locations")

    randomize_settings = Checkbutton(
        gui_text       = 'Randomize Main Rule Settings',
        gui_tooltip    = '''\
                         Randomizes all settings on the 'Main Rules' tab, except:

                         - Logic Rules
                         - (Random) Number of MQ Dungeons
                         - Pre-completed Dungeons
                         - Rainbow Bridge/Ganon Boss Key Requirements: Gold Skulltula Tokens
                         - Variable numbers of Spiritual Stones, Medallions, or Dungeons
                         for Rainbow Bridge and Ganon's Boss Key
                         (you will always be required to obtain all the relevant rewards)
                         - Scrub Shuffle will either be "Off" or "On (Affordable)"
                         ''',
        default        = False,
        disable        = {
            True: {
                'sections': ['shuffle_section'],
                'settings': [
                    'open_forest', 'open_kakariko', 'open_door_of_time', 'zora_fountain', 'gerudo_fortress', 'dungeon_shortcuts_choice',
                    'dungeon_shortcuts', 'trials_random', 'trials',
                    'starting_age', 'shuffle_interior_entrances', 'shuffle_hideout_entrances',
                    'shuffle_grotto_entrances', 'shuffle_dungeon_entrances',
                    'shuffle_bosses', 'shuffle_overworld_entrances', 'shuffle_gerudo_valley_river_exit', 'owl_drops', 'warp_songs', 'spawn_positions',
                    'triforce_hunt', 'triforce_count_per_world', 'triforce_goal_per_world', 'free_bombchu_drops', 'one_item_per_dungeon',
                    'shuffle_mapcompass', 'shuffle_smallkeys', 'shuffle_hideoutkeys', 'shuffle_tcgkeys', 'key_rings_choice', 'key_rings',
                    'shuffle_silver_rupees', 'silver_rupee_pouches_choice', 'silver_rupee_pouches', 'shuffle_bosskeys', 'enhance_map_compass',
                ],
            },
        },
        shared         = True,
    )

    logic_rules = Combobox(
        gui_text       = 'Logic Rules',
        default        = 'glitchless',
        choices        = {
            'glitchless': 'Glitchless',
            'glitched':   'Glitched',
            'none':       'No Logic',
        },
        gui_tooltip    = '''\
            Logic provides guiding sets of rules for world generation
            which the Randomizer uses to ensure the generated seeds
            are beatable.

            'Glitchless': No glitches are required, but may require
            some minor tricks. Add minor tricks to consider for logic
            in the 'Detailed Logic' tab.

            'Glitched': Movement-oriented glitches are likely required.
            No locations excluded.

            'No Logic': Maximize randomization, All locations are
            considered available. MAY BE IMPOSSIBLE TO BEAT.
        ''',
        disable        = {
            'glitchless': {'settings': ['tricks_list_msg']},
            'glitched':   {'settings': ['allowed_tricks', 'shuffle_interior_entrances', 'shuffle_hideout_entrances', 'shuffle_grotto_entrances',
                                         'shuffle_dungeon_entrances', 'shuffle_overworld_entrances', 'shuffle_gerudo_valley_river_exit', 'owl_drops',
                                         'warp_songs', 'spawn_positions', 'mq_dungeons_mode', 'mq_dungeons_specific',
                                         'mq_dungeons_count', 'shuffle_bosses', 'shuffle_ganon_tower', 'dungeon_shortcuts', 'deadly_bonks',
                                         'shuffle_freestanding_items', 'shuffle_pots', 'shuffle_crates', 'shuffle_beehives', 'shuffle_silver_rupees', 'shuffle_wonderitems']},
            'none':       {'settings': ['allowed_tricks', 'logic_no_night_tokens_without_suns_song', 'reachable_locations']},
        },
        shared         = True,
    )

    reachable_locations = Combobox(
        gui_text       = 'Guarantee Reachable Locations',
        default        = 'all',
        choices        = {
            'all':      'All',
            'goals':    'All Goals',
            'beatable': 'Required Only',
        },
        gui_tooltip    = '''\
            This determines which items and locations are guaranteed to be reachable.

            'All': The randomizer will guarantee that every item is obtainable and every location is reachable.

            'All Goals': The randomizer will guarantee that every goal item is obtainable, not just the amount required
            to beat the game, but otherwise behaves like 'Required Only'.
            Goal items are the items required for the rainbow bridge and/or Ganon's Boss Key, so for example if the bridge is
            set to 1 Medallion and Ganon's Boss Key to 1 Gold Skulltula Token, all 6 Medallions and all 100 Tokens will
            be obtainable. In Triforce Hunt, this will instead guarantee that all Triforce Pieces can be obtained. Hint
            distributions that define custom goals or remove the default goals will affect item placement as well.

            'Required Only': Only items and locations required to beat the game will be guaranteed reachable.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
        },
        shared         = True,
    )

    triforce_hunt = Checkbutton(
        gui_text       = 'Triforce Hunt',
        gui_tooltip    = '''\
            Pieces of the Triforce have been scattered around the world.
            Find some of them to beat the game.

            Game is saved on completion, and Ganon's Castle key is given
            if beating the game again is desired.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
        disable        = {
            True:  {'settings': ['shuffle_ganon_bosskey', 'ganon_bosskey_stones', 'ganon_bosskey_medallions', 'ganon_bosskey_rewards', 'ganon_bosskey_tokens', 'ganon_bosskey_hearts']},
            False: {'settings': ['triforce_count_per_world', 'triforce_goal_per_world']},
        },
    )

    triforce_count_per_world = Scale(
        gui_text       = 'Triforces Per World',
        default        = 30,
        minimum        = 1,
        maximum        = 999,
        shared         = True,
        gui_tooltip    = '''\
            Select the amount of Triforce Pieces placed in each world.
            Each world will have the same number of triforces.

            A good number to choose is 1.5 times the amount of
            Triforce Pieces required per world, for example 30
            Triforces placed with a goal of 20. Higher ratios will
            result in easier and shorter seeds, while a ratio closer
            to 1 will generally be longer and more difficult.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
            'web:max':            200,
            'electron:max':       200,
        },
    )

    triforce_goal_per_world = Scale(
        gui_text       = 'Required Triforces Per World',
        default        = 20,
        minimum        = 1,
        maximum        = 999,
        shared         = True,
        gui_tooltip    = '''\
            Select the amount of Triforce Pieces required to beat the game.

            In multiworld, the required amount will be per world collectively.
            For example, if this is set to 20 in a 2 player multiworld, players
            need 40 total, but one player could obtain 30 and the other 10.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
            'web:max':            100,
            'electron:max':       100,
        },
    )

    lacs_condition = Combobox(
        gui_text       = 'LACS Condition',
        default        = 'vanilla',
        choices        = {
            'vanilla':    "Vanilla",
            'stones':     "Stones",
            'medallions': "Medallions",
            'dungeons':   "Dungeon Rewards",
            'tokens':     "Tokens",
            'hearts':     "Hearts",
        },
        gui_tooltip    = '''\
            Sets the condition for the Light Arrow Cutscene
            check to give you the item from Zelda.

            'Vanilla': Shadow and Spirit Medallions.
            'Stones': A configurable amount of Spiritual Stones.
            'Medallions': A configurable amount of Medallions.
            'Dungeon Rewards': A configurable amount of Dungeon Rewards.
            'Tokens': A configurable amount of Gold Skulltula Tokens.
            'Hearts': A configurable amount of hearts.
        ''',
        shared         = True,
        disable        = {
            '!stones':     {'settings': ['lacs_stones']},
            '!medallions': {'settings': ['lacs_medallions']},
            '!dungeons':   {'settings': ['lacs_rewards']},
            '!tokens':     {'settings': ['lacs_tokens']},
            '!hearts':     {'settings': ['lacs_hearts']},
        },
        gui_params     = {
            'optional': True,
            'distribution': [
                ('vanilla',    1),
                ('medallions', 1),
                ('stones',     1),
                ('dungeons',   1),
            ],
        },
    )

    lacs_medallions = Scale(
        gui_text         = "Medallions Required for LACS",
        default          = 6,
        minimum          = 1,
        maximum          = 6,
        gui_tooltip      = '''\
            Select the amount of Medallions required to trigger the Light Arrow Cutscene.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            'optional':           True,
            "hide_when_disabled": True,
            'distribution':       [(6, 1)],
        },
    )

    lacs_stones = Scale(
        gui_text         = "Spiritual Stones Required for LACS",
        default          = 3,
        minimum          = 1,
        maximum          = 3,
        gui_tooltip      = '''\
            Select the amount of Spiritual Stones required to trigger the Light Arrow Cutscene.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            'optional':           True,
            "hide_when_disabled": True,
            'distribution':       [(3, 1)],
        },
    )

    lacs_rewards = Scale(
        gui_text         = "Dungeon Rewards Required for LACS",
        default          = 9,
        minimum          = 1,
        maximum          = 9,
        gui_tooltip      = '''\
            Select the amount of Dungeon Rewards (Medallions and Spiritual Stones)
            required to trigger the Light Arrow Cutscene.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            'optional':           True,
            "hide_when_disabled": True,
            'distribution':       [(9, 1)],
        },
    )

    lacs_tokens = Scale(
        gui_text         = "Gold Skulltula Tokens Required for LACS",
        default          = 100,
        minimum          = 1,
        maximum          = 999,
        gui_tooltip      = '''\
            Select the amount of Gold Skulltula Tokens
            required to trigger the Light Arrow Cutscene.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            'optional':           True,
            "hide_when_disabled": True,
            'web:max':            100,
            'electron:max':       100,
        },
    )

    lacs_hearts = Scale(
        gui_text         = "Hearts Required for LACS",
        default          = 20,
        minimum          = 4,
        maximum          = 20,
        gui_tooltip      = '''\
            Select the amount of hearts
            required to trigger the Light Arrow Cutscene.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            'optional':           True,
            "hide_when_disabled": True,
        },
    )

    bridge = Combobox(
        gui_text       = 'Rainbow Bridge Requirement',
        default        = 'medallions',
        choices        = {
            'open':       'Always Open',
            'vanilla':    'Vanilla Requirements',
            'stones':     'Spiritual Stones',
            'medallions': 'Medallions',
            'dungeons':   'Dungeon Rewards',
            'tokens':     'Gold Skulltula Tokens',
            'hearts':     'Hearts',
            'random':     'Random'
        },
        gui_tooltip    = '''\
            'Always Open': Rainbow Bridge is always present.
            'Vanilla Requirements': Spirit/Shadow Medallions and Light Arrows.
            'Spiritual Stones': A configurable amount of Spiritual Stones.
            'Medallions': A configurable amount of Medallions.
            'Dungeon Rewards': A configurable amount of Dungeon Rewards.
            'Gold Skulltula Tokens': A configurable amount of Gold Skulltula Tokens.
            'Hearts': A configurable amount of hearts.
            'Random': A random Rainbow Bridge requirement excluding Gold Skulltula Tokens.
        ''',
        shared         = True,
        disable        = {
            '!stones':     {'settings': ['bridge_stones']},
            '!medallions': {'settings': ['bridge_medallions']},
            '!dungeons':   {'settings': ['bridge_rewards']},
            '!tokens':     {'settings': ['bridge_tokens']},
            '!hearts':     {'settings': ['bridge_hearts']},
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('open',       1),
                ('vanilla',    1),
                ('stones',     1),
                ('medallions', 1),
                ('dungeons',   1),
            ],
        },
    )

    bridge_medallions = Scale(
        gui_text         = "Medallions Required for Bridge",
        default          = 6,
        minimum          = 1,
        maximum          = 6,
        gui_tooltip      = '''\
            Select the amount of Medallions required to spawn the rainbow bridge.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            "randomize_key":      "randomize_settings",
            "hide_when_disabled": True,
            'distribution':       [(6, 1)],
        },
    )

    bridge_stones = Scale(
        gui_text         = "Spiritual Stones Required for Bridge",
        default          = 3,
        minimum          = 1,
        maximum          = 3,
        gui_tooltip      = '''\
            Select the amount of Spiritual Stones required to spawn the rainbow bridge.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            "randomize_key":      "randomize_settings",
            "hide_when_disabled": True,
            'distribution':       [(3, 1)],
        },
    )

    bridge_rewards = Scale(
        gui_text         = "Dungeon Rewards Required for Bridge",
        default          = 9,
        minimum          = 1,
        maximum          = 9,
        gui_tooltip      = '''\
            Select the amount of Dungeon Rewards (Medallions and Spiritual Stones)
            required to spawn the rainbow bridge.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            "randomize_key":      "randomize_settings",
            "hide_when_disabled": True,
            'distribution':       [(9, 1)],
        },
    )

    bridge_tokens = Scale(
        gui_text         = "Skulltulas Required for Bridge",
        default          = 100,
        minimum          = 1,
        maximum          = 999,
        gui_tooltip      = '''\
            Select the amount of Gold Skulltula Tokens required to spawn the rainbow bridge.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            'hide_when_disabled': True,
            'web:max':            100,
            'electron:max':       100,
        },
    )

    bridge_hearts = Scale(
        gui_text       = "Hearts Required for Bridge",
        default        = 20,
        minimum        = 4,
        maximum        = 20,
        gui_tooltip    = '''\
            Select the amount of hearts required to spawn the rainbow bridge.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    trials_random = Checkbutton(
        gui_text       = "Random Number of Ganon's Trials",
        gui_tooltip    = '''\
            Sets a random number of trials to enter Ganon's Tower.
        ''',
        shared         = True,
        disable        = {
            True: {'settings': ['trials']}
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                (True, 1),
            ],
        },
    )

    trials = Scale(
        gui_text         = "Ganon's Trials Count",
        default          = 6,
        minimum          = 0,
        maximum          = 6,
        gui_tooltip      = '''\
            Trials are randomly selected. If hints are
            enabled, then there will be hints for which
            trials need to be completed.
        ''',
        shared           = True,
        disabled_default = 0,
    )

    shuffle_ganon_bosskey = Combobox(
        gui_text         = "Ganon's Boss Key",
        default          = 'dungeon',
        disabled_default = 'triforce',
        choices          = {
            'remove':          "Remove (Keysy)",
            'vanilla':         "Vanilla Location",
            'dungeon':         "Own Dungeon",
            'regional':        "Regional",
            'overworld':       "Overworld Only",
            'any_dungeon':     "Any Dungeon",
            'keysanity':       "Anywhere (Keysanity)",
            'on_lacs':         "Light Arrow Cutscene",
            'stones':          "Stones",
            'medallions':      "Medallions",
            'dungeons':        "Dungeon Rewards",
            'tokens':          "Tokens",
            'hearts':          "Hearts",
        },
        gui_tooltip      = '''\
            'Remove': Ganon's Castle Boss Key is removed
            and the boss door in Ganon's Tower starts unlocked.

            'Vanilla': Ganon's Castle Boss Key will appear in
            the vanilla location.

            'Own Dungeon': Ganon's Castle Boss Key can only appear
            inside Ganon's Castle.

            'Regional': Ganon's Castle Boss Key can only appear
            in Hyrule Field, Lon Lon Ranch, Market, Temple of Time, Hyrule Castle,
            (Outside) Ganon's Castle, and Inside Ganon's Castle.

            'Overworld Only': Ganon's Castle Boss Key can only appear
            outside of dungeons.

            'Any Dungeon': Ganon's Castle Boss Key can only appear
            inside of a dungeon, but not necessarily Ganon's Castle.

            'Anywhere': Ganon's Castle Boss Key can appear
            anywhere in the world.

            'Light Arrow Cutscene': Ganon's Castle Boss Key will
            appear on the Light Arrow Cutscene.

            'Stones': Ganon's Castle Boss Key will be awarded
            when reaching the target number of Spiritual Stones.

            'Medallions': Ganon's Castle Boss Key will be awarded
            when reaching the target number of Medallions.

            'Dungeon Rewards': Ganon's Castle Boss Key will be awarded
            when reaching the target number of Dungeon Rewards.

            'Tokens': Ganon's Castle Boss Key will be awarded
            when reaching the target number of Gold Skulltula Tokens.

            'Hearts': Ganon's Castle Boss Key will be awarded
            when reaching the target number of hearts.
        ''',
        shared           = True,
        disable          = {
            '!stones':      {'settings': ['ganon_bosskey_stones']},
            '!medallions':  {'settings': ['ganon_bosskey_medallions']},
            '!dungeons':    {'settings': ['ganon_bosskey_rewards']},
            '!tokens':      {'settings': ['ganon_bosskey_tokens']},
            '!hearts':      {'settings': ['ganon_bosskey_hearts']},
        },
        gui_params       = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                ('remove',          4),
                ('dungeon',         2),
                ('vanilla',         2),
                ('keysanity',       4),
                ('on_lacs',         1),
            ],
        },
    )

    ganon_bosskey_medallions = Scale(
        gui_text         = "Medallions Required for Ganon's BK",
        default          = 6,
        minimum          = 1,
        maximum          = 6,
        gui_tooltip      = '''\
            Select the amount of Medallions required to receive Ganon's Castle Boss Key.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            "randomize_key":      "randomize_settings",
            "hide_when_disabled": True,
            'distribution':       [(6, 1)],
        },
    )

    ganon_bosskey_stones = Scale(
        gui_text         = "Spiritual Stones Required for Ganon's BK",
        default          = 3,
        minimum          = 1,
        maximum          = 3,
        gui_tooltip      = '''\
            Select the amount of Spiritual Stones required to receive Ganon's Castle Boss Key.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            "randomize_key":      "randomize_settings",
            "hide_when_disabled": True,
            'distribution':       [(3, 1)],
        },
    )

    ganon_bosskey_rewards = Scale(
        gui_text         = "Dungeon Rewards Required for Ganon's BK",
        default          = 9,
        minimum          = 1,
        maximum          = 9,
        gui_tooltip      = '''\
            Select the amount of Dungeon Rewards (Medallions and Spiritual Stones)
            required to receive Ganon's Castle Boss Key.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            "randomize_key":      "randomize_settings",
            "hide_when_disabled": True,
            'distribution':       [(9, 1)],
        },
    )

    ganon_bosskey_tokens = Scale(
        gui_text         = "Gold Skulltula Tokens Required for Ganon's BK",
        default          = 100,
        minimum          = 1,
        maximum          = 999,
        gui_tooltip      = '''\
            Select the amount of Gold Skulltula Tokens
            required to receive Ganon's Castle Boss Key.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            "hide_when_disabled": True,
            'web:max':            100,
            'electron:max':       100,
        },
    )

    ganon_bosskey_hearts = Scale(
        gui_text         = "Hearts Required for Ganon's BK",
        default          = 20,
        minimum          = 4,
        maximum          = 20,
        gui_tooltip      = '''\
            Select the amount of hearts
            required to receive Ganon's Castle Boss Key.
        ''',
        shared           = True,
        disabled_default = 0,
        gui_params       = {
            "hide_when_disabled": True,
        },
    )

    shuffle_dungeon_rewards = Combobox(
        gui_text       = 'Shuffle Dungeon Rewards',
        default        = 'reward',
        choices        = {
            'vanilla':     'Vanilla Locations',
            'reward':      'Dungeon Reward Locations',
            'dungeon':     'Own Dungeon',
            'regional':    'Regional',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'anywhere':    'Anywhere',
        },
        gui_tooltip    = '''\
            This controls where Medallions and Spiritual Stones can
            appear.

            'Vanilla Locations': Medallions and Spiritual Stones will
            appear in their vanilla locations.

            'Dungeon Reward Locations': Medallions and Spiritual
            Stones will be awarded when stepping into the blue warps
            of boss rooms, but not necessarily the boss's vanilla
            reward. In Multiworld, dungeon rewards will only appear
            in their own world.

            If you use one of the following options, note that after
            receiving the last required medallion for the Burning
            Kakariko cutscene while already in Kakariko, the cutscene
            doesn't play until you leave and reenter Kakariko (or enter
            and exit a building).

            'Own Dungeon': Each dungeon reward appears in its respective
            dungeon, but not necessarily on the boss. If boss entrances
            are mixed, boss rooms that aren't in a dungeon can't have
            dungeon rewards. The Light Medallion appears in the Temple
            of Time, or may be a starting item if the "Free Reward from
            Rauru" setting is enabled.

            'Regional': Dungeon rewards can only appear in regions
            near the original dungeon (including the dungeon
            itself or other dungeons in the region).
            <a href="https://wiki.ootrandomizer.com/index.php?title=Hints#Hint_Regions" target="_blank">The Wiki has a list of corresponding regions here.</a>

            'Overworld Only': Dungeon rewards can only appear
            outside of dungeons.

            'Any Dungeon': Dungeon rewards can only appear
            inside of dungeons.

            'Anywhere': Dungeon rewards can appear anywhere
            in the world.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
        shared         = True,
    )

    shuffle_bosskeys = Combobox(
        gui_text       = 'Boss Keys',
        default        = 'dungeon',
        choices        = {
            'remove':      'Remove (Keysy)',
            'vanilla':     'Vanilla Locations',
            'dungeon':     'Own Dungeon',
            'regional':    'Regional',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'keysanity':   'Anywhere (Keysanity)',
        },
        gui_tooltip    = '''\
            'Remove': Boss Keys are removed. All locked
            doors in dungeons will be unlocked. An easier
            mode.

            'Vanilla': Boss Keys will appear in their
            vanilla locations.

            'Own Dungeon': Boss Keys can only appear in their
            respective dungeon.

            'Regional': Boss Keys can only appear in regions
            near the original dungeon (including the dungeon
            itself or other dungeons in the region).
            <a href="https://wiki.ootrandomizer.com/index.php?title=Hints#Hint_Regions" target="_blank">The Wiki has a list of corresponding regions here.</a>

            'Overworld Only': Boss Keys can only appear outside
            of dungeons. You may need to enter a dungeon without
            the boss key to get items required to find the key
            in the overworld.

            'Any Dungeon': Boss Keys can only appear inside
            of any dungeon, but won't necessarily be in the
            dungeon that the key is for. A difficult mode since
            it is more likely to need to enter a dungeon
            multiple times.

            'Anywhere': Boss Keys can appear
            anywhere in the world. A difficult mode since
            it is more likely to need to enter a dungeon
            multiple times.

            Try different combinations out, such as:
            'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
            for a milder Keysanity experience.

            Regardless of the selected option, boss keys from
            pre-completed dungeons won't be placed outside their
            respective dungeons and boss keys from other dungeons
            won't be placed inside pre-completed dungeons.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_smallkeys = Combobox(
        gui_text       = 'Small Keys',
        default        = 'dungeon',
        choices        = {
            'remove':      'Remove (Keysy)',
            'vanilla':     'Vanilla Locations',
            'dungeon':     'Own Dungeon',
            'regional':    'Regional',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'keysanity':   'Anywhere (Keysanity)',
        },
        gui_tooltip    = '''\
            'Remove': Small Keys are removed. All locked doors in dungeons
            will be unlocked. An easier mode.

            'Vanilla': Small Keys will appear in their vanilla locations. You start
            with 3 keys in Spirit Temple MQ because the vanilla key layout is
            not beatable in logic. You start with 2 keys in Vanilla/MQ Shadow
            Temple with its dungeon shortcut enabled to prevent softlocks.

            'Own Dungeon': Small Keys can only appear in their respective
            dungeon. If Fire Temple is not a Master Quest dungeon, the door to
            the Boss Key chest will be unlocked.

            'Regional': Small Keys can only appear
            in regions near the original dungeon (including
            the dungeon itself or other dungeons in the region).
            <a href="https://wiki.ootrandomizer.com/index.php?title=Hints#Hint_Regions" target="_blank">The Wiki has a list of corresponding regions here.</a>

            'Overworld Only': Small Keys can only appear outside
            of dungeons. You may need to enter a dungeon multiple
            times to gain items to access the overworld locations
            with the keys required to finish a dungeon.

            'Any Dungeon': Small Keys can only appear inside of any dungeon, but
            won't necessarily be in the dungeon that the key is for. A difficult mode
            since it is more likely to need to enter a dungeon multiple times.

            'Anywhere': Small Keys can appear anywhere in the world. A difficult
            mode since it is more likely to need to enter a dungeon multiple times.

            Try different combination out, such as:
            'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
            for a milder Keysanity experience.

            Regardless of the selected option, small keys from pre-completed dungeons
            won't be placed outside their respective dungeons and small keys from
            other dungeons won't be placed inside pre-completed dungeons.
        ''',
        disable        = {
            'any_dungeon': {'settings': ['one_item_per_dungeon']}
        },
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_hideoutkeys = Combobox(
        gui_text       = "Thieves' Hideout Keys",
        default        = 'vanilla',
        disabled_default = 'remove',
        choices        = {
            'vanilla':     "Vanilla Locations",
            'fortress':    "Gerudo Fortress Region",
            'regional':    "Regional",
            'overworld':   "Overworld Only",
            'any_dungeon': "Any Dungeon",
            'keysanity':   "Anywhere (Keysanity)",
        },
        gui_tooltip    = '''\
            "Vanilla": Thieves' Hideout Keys will appear in their
            vanilla location, dropping from fighting Gerudo guards
            that attack when trying to free the jailed carpenters.

            "Gerudo Fortress Region": Thieves' Hideout Keys can only
            appear in Gerudo Fortress or Thieves' Hideout.

            "Regional": Thieves' Hideout Keys can only appear in
            Gerudo Valley, Gerudo Fortress, Thieves' Hideout, Gerudo
            Training Ground, Haunted Wasteland, Desert Colossus, or
            Spirit Temple.

            "Overworld Only": Thieves' Hideout Keys can only appear
            outside of dungeons.

            "Any Dungeon": Thieves' Hideout Keys can only appear
            inside of dungeons.

            "Anywhere": Thieves' Hideout Keys can appear anywhere
            in the world.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'option_remove': ['fortress'],
        },
    )

    shuffle_tcgkeys = Combobox(
        gui_text       = 'Treasure Chest Game Keys',
        default        = 'vanilla',
        choices        = {
            'remove':      "Remove (Keysy)",
            'vanilla':     "Vanilla Locations",
            'regional':    "Regional",
            'overworld':   "Overworld Only",
            'any_dungeon': "Any Dungeon",
            'keysanity':   "Anywhere (Keysanity)",
        },
        gui_tooltip    = '''\
            'Remove': All Treasure Chest Game keys will be removed
            and all doors will remained unlocked.

            'Vanilla': Treasure Chest Game keys will have vanilla
            behavior (one random per room). The minigame will
            also have vanilla behavior.

            'Regional': Treasure Chest Game keys can only appear
            in Hyrule Field, Lon Lon Ranch, the Market, the Temple
            of Time, Hyrule Castle, outside Ganon's Castle, or
            inside Ganon's Castle.

            'Overworld Only': Treasure Chest Game keys can only appear
            outside of dungeons.

            'Any Dungeon': Treasure Chest Game keys can only appear
            inside of dungeons.

            'Anywhere': Treasure Chest Game keys can appear anywhere
            in the world.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    key_rings_choice = Combobox(
        gui_text       = 'Key Rings Mode',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'choice':    'Choose Dungeons',
            'all':       'All Dungeons',
            'random':    'Random Selection'
        },
        gui_tooltip     = '''\
            Selected dungeons will have all of their keys found
            at once in a ring rather than individually.

            For example, instead of shuffling 5 Forest Temple
            small keys into the pool, you will find a single
            key ring which will give you all 5 keys at once.

            Selecting key ring for dungeons will have no effect
            if Small Keys are set to Remove or Vanilla.

            Selecting key ring for Thieves' Hideout will have
            no effect if Thieves' Hideout keys are in vanilla
            locations or Gerudo's Fortress is set to Rescue
            One Carpenter.

            Similarly, selecting Treasure Chest Game will have
            no effect if the keys aren't shuffled. Treasure Chest
            Game will be considered when selecting 'All dungeons'
            or 'Random selection'.
        ''',
        shared         = True,
        disable={
            'off':    {'settings': ['key_rings', 'keyring_give_bk']},
            'all':    {'settings': ['key_rings']},
            'random': {'settings': ['key_rings']},
        },
    )

    key_rings = MultipleSelect(
        gui_text        = 'Key Rings',
        choices         = {
            'Thieves Hideout':        "Thieves' Hideout",
            'Treasure Chest Game':    "Treasure Chest Game",
            'Forest Temple':          "Forest Temple",
            'Fire Temple':            "Fire Temple",
            'Water Temple':           "Water Temple",
            'Shadow Temple':          "Shadow Temple",
            'Spirit Temple':          "Spirit Temple",
            'Bottom of the Well':     "Bottom of the Well",
            'Gerudo Training Ground': "Gerudo Training Ground",
            'Ganons Castle':          "Ganon's Castle"
        },
        default         = [],
        gui_params     = {
            "hide_when_disabled": True,
        },
        gui_tooltip    = '''\
            Select areas with keyring instead of multiple keys
        ''',
        shared          = True,
    )

    keyring_give_bk = Checkbutton(
        gui_text       = 'Key Rings give Boss Keys',
        gui_tooltip    = '''\
            Boss Keys will be included in the Key Ring for the specific dungeon.
            This does not apply to the Ganon's Castle Boss Key.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    shuffle_silver_rupees = Combobox(
        gui_text       = 'Shuffle Silver Rupees',
        default        = 'vanilla',
        choices        = {
            'remove':      'Remove',
            'vanilla':     'Vanilla Locations',
            'dungeon':     'Own Dungeon',
            'regional':    'Regional',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'anywhere':    'Anywhere',
        },
        gui_tooltip    = '''\
            Enabling this shuffles the Silver Rupee puzzles into to the
            item pool.

            Silver Rupees are grouped into sets of 5 (except for some
            Master Quest dungeons, which have sets of other amounts), each
            of which permanently unlocks something in a dungeon once all
            the rupees in that set are collected. Hints will only tell you
            the dungeon a Silver Rupee corresponds to, but upon collecting
            it, you will be told the exact room.
            The vanilla locations of Silver Rupees hold shuffled items.

            'Remove': Silver Rupees are removed and the puzzles are
            solved. This will add a small amount of money and
            refill items to the pool.

            'Vanilla': Silver Rupees will appear in their vanilla
            locations. You will have to collect all of a set in one go to
            to solve a puzzle.

            'Own Dungeon': Silver Rupees can only appear
            in their respective dungeon.

            'Regional': Silver Rupees can only appear in regions
            near the original dungeon (including the dungeon
            itself or other dungeons in the region).
            <a href="https://wiki.ootrandomizer.com/index.php?title=Hints#Hint_Regions" target="_blank">The Wiki has a list of corresponding regions here.</a>

            'Overworld Only': Silver Rupees can only appear
            outside of dungeons.

            'Any Dungeon': Silver Rupees can only appear in a
            dungeon, but not necessarily the dungeon they are for.

            'Anywhere': Silver Rupees can appear
            anywhere in the world.
        ''',
        shared         = True,
        disable        = {
            'remove':  {'settings': ['silver_rupee_pouches_choice', 'silver_rupee_pouches']},
            'vanilla': {'settings': ['silver_rupee_pouches_choice', 'silver_rupee_pouches']},
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    silver_rupee_pouches_choice = Combobox(
        gui_text       = 'Silver Rupee Pouches Mode',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'choice':    'Choose Puzzles',
            'all':       'All Puzzles',
            'random':    'Random Puzzles'
        },
        gui_tooltip     = '''\
            Selected silver rupee puzzles will have all of
            their silver rupees found at once in a pouch
            rather than individually.

            For example, instead of shuffling 5 silver
            rupees for the Fire Trial in Ganon's Castle
            into the pool, you will find a single pouch
            which will give you all 5 of them at once.
        ''',
        shared         = True,
        disable        = {
            'off':    {'settings': ['silver_rupee_pouches']},
            'all':    {'settings': ['silver_rupee_pouches']},
            'random': {'settings': ['silver_rupee_pouches']},
        },
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    silver_rupee_pouches = MultipleSelect(
        gui_text        = 'Silver Rupee Pouches',
        choices         = {
            'Dodongos Cavern Staircase': "Dodongo's Cavern Staircase",
            'Ice Cavern Spinning Scythe': "Ice Cavern Spinning Scythe",
            'Ice Cavern Push Block': "Ice Cavern Push Block",
            'Bottom of the Well Basement': "Bottom of the Well Basement",
            'Shadow Temple Scythe Shortcut': "Shadow Temple Scythe Shortcut",
            'Shadow Temple Invisible Blades': "Shadow Temple Invisible Blades",
            'Shadow Temple Huge Pit': "Shadow Temple Huge Pit",
            'Shadow Temple Invisible Spikes': "Shadow Temple Invisible Spikes",
            'Gerudo Training Ground Slopes': "Gerudo Training Ground Slopes",
            'Gerudo Training Ground Lava': "Gerudo Training Ground Lava",
            'Gerudo Training Ground Water': "Gerudo Training Ground Water",
            'Spirit Temple Child Early Torches': "Spirit Temple Child Early Torches",
            'Spirit Temple Adult Boulders': "Spirit Temple Adult Boulders",
            'Spirit Temple Lobby and Lower Adult': "Spirit Temple Lobby and Lower Adult",
            'Spirit Temple Sun Block': "Spirit Temple Sun Block",
            'Spirit Temple Adult Climb': "Spirit Temple Adult Climb",
            'Ganons Castle Spirit Trial': "Ganon's Castle Spirit Trial",
            'Ganons Castle Light Trial': "Ganon's Castle Light Trial",
            'Ganons Castle Fire Trial': "Ganon's Castle Fire Trial",
            'Ganons Castle Shadow Trial': "Ganon's Castle Shadow Trial",
            'Ganons Castle Water Trial': "Ganon's Castle Water Trial",
            'Ganons Castle Forest Trial': "Ganon's Castle Forest Trial",
        },
        gui_tooltip    = '''\
            Select puzzles with silver rupee pouches
            instead of individual silver rupees.
        ''',
        default         = [],
        gui_params     = {
            "hide_when_disabled": True,
        },
        shared          = True,
    )

    shuffle_mapcompass = Combobox(
        gui_text       = 'Maps & Compasses',
        default        = 'dungeon',
        choices        = {
            'remove':      'Remove',
            'startwith':   'Start With',
            'vanilla':     'Vanilla Locations',
            'dungeon':     'Own Dungeon',
            'regional':    'Regional',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'keysanity':   'Anywhere',
        },
        gui_tooltip    = '''\
            'Remove': Maps and Compasses are removed.
            This will add a small amount of money and refill items to the pool.

            'Start With': Maps and Compasses are given to you from the start.
            This will add a small amount of money and refill items to the pool.

            'Vanilla': Maps and Compasses will appear in their vanilla locations.

            'Own Dungeon': Maps and Compasses can only appear in their respective
            dungeon.

            'Regional': Maps and Compasses can only appear in regions near the
            original dungeon (including the dungeon itself or other dungeons in
            the region). <a href="https://wiki.ootrandomizer.com/index.php?title=Hints#Hint_Regions" target="_blank">The Wiki has a list of corresponding regions here.</a>

            'Overworld Only': Maps and Compasses can only appear
            outside of dungeons.

            'Any Dungeon': Maps and Compasses can only appear in a dungeon, but
            not necessarily the dungeon they are for.

            'Anywhere': Maps and Compasses can appear anywhere in the world.

            Setting 'Remove', 'Start With', 'Overworld', or 'Anywhere' will add 2
            more possible locations to each Dungeons. This makes dungeons more
            profitable, especially Ice Cavern, Water Temple, and Jabu Jabu's Belly.

            Regardless of the selected option, maps and compasses from pre-completed
            dungeons won't be placed outside their respective dungeons and maps and
            compasses from other dungeons won't be placed inside pre-completed dungeons.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    enhance_map_compass = Checkbutton(
        gui_text       = 'Maps and Compasses Give Information',
        gui_tooltip    = '''\
            Gives the Map and Compass extra functionality.
            Map will tell if a dungeon is vanilla or Master Quest.
            Compass will tell what medallion or stone is within.
            The Temple of Time Altar will no longer provide
            information on the location of medallions and stones.

            'Maps/Compasses: Remove': The dungeon information is
            not available anywhere in the game.

            'Maps/Compasses: Start With': The dungeon information
            is available immediately from the dungeon menu.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    open_forest = Combobox(
        gui_text       = 'Forest',
        default        = 'closed',
        choices        = {
            'open':        'Open Forest',
            'closed_deku': 'Closed Deku',
            'closed':      'Closed Forest',
            },
        gui_tooltip    = '''\
            'Open Forest': Mido no longer blocks the path to the
            Deku Tree, and the Kokiri boy no longer blocks the path
            out of the forest.

            'Closed Deku': The Kokiri boy no longer blocks the path
            out of the forest, but Mido still blocks the path to the
            Deku Tree, requiring Kokiri Sword and Deku Shield to access
            the Deku Tree.

            'Closed Forest': Beating Deku Tree is logically required
            to leave the forest area (Kokiri Forest/Lost Woods/Sacred Forest
            Meadow/Deku Tree), while the Kokiri Sword and a Deku Shield are
            required to access the Deku Tree. Items needed for this will be
            guaranteed inside the forest area. This setting is incompatible
            with starting as adult, and so Starting Age will be locked to Child.
            With either "Shuffle Interior Entrances" set to "All", "Shuffle
            Overworld Entrances" on, "Randomize Warp Song Destinations" on
            or "Randomize Overworld Spawns" on, Closed Forest will instead
            be treated as Closed Deku with starting age Child and WILL NOT
            guarantee that these items are available in the forest area.
        ''',
        shared         = True,
        disable        = {
            'closed': {'settings': ['starting_age']}
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                ('open',        1),
                ('closed_deku', 1),
                ('closed',      1),
            ],
        },
    )

    open_kakariko = Combobox(
        gui_text       = 'Kakariko Gate',
        default        = 'closed',
        choices        = {
            'open':   'Open Gate',
            'zelda':  "Zelda's Letter Opens Gate",
            'closed': 'Closed Gate',
            },
        gui_tooltip    = '''\
            This changes the behavior of the Kakariko Gate to
            Death Mountain Trail as child. The gate is always
            open as adult.

            "Open Gate": The gate is always open instead of
            needing Zelda's Letter. The Happy Mask Shop opens
            upon obtaining Zelda's Letter without needing to
            show it to the guard.

            "Zelda's Letter Opens Gate": The gate is closed at
            the start, but opens automatically along with the
            Happy Mask Shop upon obtaining Zelda's Letter.

            "Closed": The gate and the Happy Mask Shop both remain closed
            until showing Zelda's Letter to the guard in Kakariko.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    open_door_of_time = Checkbutton(
        gui_text       = 'Open Door of Time',
        gui_tooltip    = '''\
            The Door of Time starts opened instead of needing to
            play the Song of Time. If this is not set, only
            an Ocarina and Song of Time must be found to open
            the Door of Time.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    zora_fountain = Combobox(
        gui_text       = "Zora's Fountain",
        default        = 'closed',
        choices        = {
            'closed': 'Default Behavior (Closed)',
            'adult':  'Open For Adult',
            'open':   'Always Open',
        },
        gui_tooltip    = '''\
            'Default Behavior': King Zora obstructs the way to
            Zora's Fountain. Ruto's Letter must be shown as
            child in order to move him for both eras.

            'Open For Adult': King Zora is always moved in
            the adult era. This means Ruto's Letter is only
            required to access Zora's Fountain as child.

            'Always Open': King Zora starts as moved in
            both the child and adult eras. This also removes
            Ruto's Letter from the pool since it can't be used.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    gerudo_fortress = Combobox(
        gui_text       = "Gerudo's Fortress",
        default        = 'normal',
        choices        = {
            'normal': 'Default Behavior',
            'fast':   'Rescue One Carpenter',
            'open':   "Open Gerudo's Fortress",
        },
        gui_tooltip    = '''\
            'Rescue One Carpenter': Only the bottom left carpenter,
            in the cell with a single torch, must be rescued.
            This cell can be savewarped to from any room in the hideout.
            All but one of the Thieves' Hideout Keys are removed.

            'Open Gerudo's Fortress': The carpenters are rescued from
            the start of the game, and if 'Shuffle Gerudo Card' is disabled,
            the player starts with the Gerudo Card in the inventory
            allowing access to Gerudo Training Ground.
        ''',
        shared         = True,
        disable        = {
            'open': {'settings': ['shuffle_hideoutkeys']}
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    dungeon_shortcuts_choice = Combobox(
        gui_text       = 'Dungeon Boss Shortcuts Mode',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'choice':    'Specific Dungeons',
            'all':       'All Dungeons',
            'random':    'Random Dungeons'
        },
        gui_tooltip    = '''\
            Shortcuts to dungeon bosses are available
            without any requirements.
            Incompatible with glitched logic.

            Changes include (vanilla shown, MQ similar):
            <b>Deku Tree</b>: webs burned, block in the
            basement moved, 231 scrubs defeated
            <b>Dodongo's Cavern</b>: mud wall bombed,
            mouth opened and boss lobby floor bombed
            <b>Jabu Jabu</b>: pathway lowered
            <b>Forest Temple</b>: elevator raised and
            basement gates open
            <b>Fire Temple</b>: pillar knocked down
            <b>Water Temple</b>: no change, but see the
            note on "Shuffle Boss Entrances" below
            <b>Shadow Temple</b>: Truthspinner solved, boat
            block moved, and statue bridge moved. You start
            with 2 small keys if Shuffle Small Keys is set
            to Vanilla.
            <b>Spirit Temple</b>: lobby elevator activated,
            shortcut silver blocks moved, central room
            platform lowered, and statue face melted

            With "Shuffle Boss Entrances", the floor above
            King Dodongo's arena is opened based on the
            shortcut setting for the dungeon that contains
            the entrance to King Dodongo's boss room, not
            necessarily Dodongo's Cavern.

            Choose: Select dungeons with shortcuts
            All: Enable all dungeons shortcuts
            Random: Random dungeon shortcuts
        ''',
        shared         = True,
        disable        = {
            '!choice': {'settings': ['dungeon_shortcuts']},
        },
    )

    dungeon_shortcuts = MultipleSelect(
        gui_text        = 'Dungeon Boss Shortcuts',
        choices         = {
            'Deku Tree':        "Deku Tree",
            'Dodongos Cavern':  "Dodongo's Cavern",
            'Jabu Jabus Belly': "Jabu Jabu's Belly",
            'Forest Temple':    "Forest Temple",
            'Fire Temple':      "Fire Temple",
            'Water Temple':     "Water Temple",  # affects King Dodongo if he's in Water
            'Shadow Temple':    "Shadow Temple",
            'Spirit Temple':    "Spirit Temple",
        },
        default        = [],
        gui_params     = {
            "hide_when_disabled": True,
        },
        gui_tooltip    = '''\
            Select dungeons with shortcuts
        ''',
        shared          = True,
    )

    starting_age = Combobox(
        gui_text       = 'Starting Age',
        default        = 'child',
        choices        = {
            'child':  'Child',
            'adult':  'Adult',
            'random': 'Random',
        },
        gui_tooltip    = '''\
            Choose which age Link will start as.

            Starting as adult means you start with
            the master sword in your inventory.

            Only the child option is compatible with
            Closed Forest.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('random', 1),
            ],
        },
    )

    mq_dungeons_mode = Combobox(
        gui_text       = 'MQ Dungeon Mode',
        default        = 'vanilla',
        choices        = {
            'vanilla':    "Vanilla",
            'mq':         "Master Quest",
            'specific':   "Specific Dungeons",
            'count':      "Count",
            'random':     "Completely Random",
        },
        gui_tooltip    = '''\
            'Vanilla': All dungeons will be the original versions.
            'Master Quest': All dungeons will be the MQ versions.
            'Specific Dungeons': Choose which specific dungeons will be MQ versions.
            'Count': Choose how many MQ dungeons will be randomly chosen.
            'Completely Random': Each dungeon will vanilla or MQ at random.
        ''',
        shared         = True,
        disable        = {
            '!specific': {'settings': ['mq_dungeons_specific']},
            '!count':    {'settings': ['mq_dungeons_count']},
        },
        gui_params     = {
            'distribution': [
                ('random', 1),
            ],
        },
    )

    mq_dungeons_specific = MultipleSelect(
        gui_text        = 'MQ Dungeons',
        choices         = {
            'Deku Tree':              "Deku Tree",
            'Dodongos Cavern':        "Dodongo's Cavern",
            'Jabu Jabus Belly':       "Jabu Jabu's Belly",
            'Forest Temple':          "Forest Temple",
            'Fire Temple':            "Fire Temple",
            'Water Temple':           "Water Temple",
            'Shadow Temple':          "Shadow Temple",
            'Spirit Temple':          "Spirit Temple",
            'Bottom of the Well':     "Bottom of the Well",
            'Ice Cavern':             "Ice Cavern",
            'Gerudo Training Ground': "Gerudo Training Ground",
            'Ganons Castle':          "Ganon's Castle",
        },
        default         = [],
        gui_tooltip     = '''\
            Select the specific dungeons you would
            like the Master Quest version of.
            The unselected dungeons will be
            the original version.
        ''',
        shared          = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    mq_dungeons_count = Scale(
        gui_text       = "MQ Dungeon Count",
        default        = 0,
        minimum        = 0,
        maximum        = 12,
        gui_tooltip    = '''\
            Specify the number of Master Quest
            dungeons to appear in the game.
        ''',
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    empty_dungeons_mode = Combobox(
        gui_text       = 'Pre-completed Dungeons Mode',
        default        = 'none',
        choices        = {
            'none':       'Off',
            'specific':   'Specific Dungeons',
            'rewards':    'Specific Rewards',
            'count':      'Count',
        },
        gui_tooltip    = '''\
            Pre-completed dungeons are dungeons guaranteed to be barren and whose
            dungeon rewards are given for free to the player before the beginning
            of the game. This setting only applies to dungeons with dungeon rewards
            (blue warps).

            - 'None': No dungeon will be pre-completed. Some dungeons may still be
            randomly rolled with no major items, but their dungeon rewards won't
            be given for free.
            - 'Specific Dungeons': Choose which specific dungeons will be pre-completed.
            - 'Specific Rewards': Choose which specific dungeon rewards will be in pre-completed dungeons. Not compatible with shuffled dungeon rewards.
            - 'Count': Choose how many pre-completed dungeons will be randomly chosen.

            A same dungeon won't be both MQ and pre-completed unless it has been
            explicitly specified as such or unless it is the only way to fulfill both MQ and
            pre-completed selected settings.

            Pre-completed dungeons won't contain major items even if "Dungeons Have
            One Major Item" is on.

            Regardless of "Shuffle Dungeon Items" settings, dungeon items from
            pre-completed dungeons won't be placed outside their respective dungeons
            and dungeon items from other dungeons won't be placed inside pre-completed
            dungeons.

            If "Shuffle Songs" is set to "Dungeon rewards", then songs that would have
            been placed in pre-completed dungeons are given for free along with the
            free dungeon rewards.
        ''',
        shared         = True,
        disable        = {
            '!specific': {'settings': ['empty_dungeons_specific']},
            '!rewards':  {'settings': ['empty_dungeons_rewards']},
            '!count':    {'settings': ['empty_dungeons_count']},
            'rewards':   {'settings': ['shuffle_dungeon_rewards']},
        },
        gui_params     = {
            'distribution':  [
                ('none', 1)
            ],
        },
    )

    empty_dungeons_specific = MultipleSelect(
        gui_text        = 'Pre-completed Dungeons',
        choices         = {
            'Deku Tree':              "Deku Tree",
            'Dodongos Cavern':        "Dodongo's Cavern",
            'Jabu Jabus Belly':       "Jabu Jabu's Belly",
            'Forest Temple':          "Forest Temple",
            'Fire Temple':            "Fire Temple",
            'Water Temple':           "Water Temple",
            'Shadow Temple':          "Shadow Temple",
            'Spirit Temple':          "Spirit Temple"
        },
        default         = [],
        gui_tooltip     = '''\
            Select the specific dungeons you would
            like to be pre-completed.
        ''',
        shared          = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    empty_dungeons_rewards = MultipleSelect(
        gui_text        = 'Pre-completed Dungeon Rewards',
        choices         = {
            'Kokiri Emerald':   "Kokiri Emerald",
            'Goron Ruby':       "Goron Ruby",
            'Zora Sapphire':    "Zora Sapphire",
            'Light Medallion':  "Light Medallion",
            'Forest Medallion': "Forest Medallion",
            'Fire Medallion':   "Fire Medallion",
            'Water Medallion':  "Water Medallion",
            'Shadow Medallion': "Shadow Medallion",
            'Spirit Medallion': "Spirit Medallion",
        },
        default         = [],
        gui_tooltip     = '''\
            Select the specific dungeons rewards whose
            dungeons you would like to be pre-completed.
        ''',
        shared          = True,
        gui_params      = {
            "hide_when_disabled": True,
        },
    )

    empty_dungeons_count = Scale(
        gui_text       = "Pre-completed Dungeon Count",
        default        = 2,
        minimum        = 1,
        maximum        = 8,
        gui_tooltip    = '''\
            Specify the number of pre-completed
            dungeons to appear in the game.
        ''',
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    shuffle_interior_entrances = Combobox(
        gui_text       = 'Shuffle Interior Entrances',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'simple':    'Simple Interiors',
            'all':       'All Interiors',
        },
        gui_tooltip    = '''\
            'Simple Interiors':
            Shuffle the pool of interior entrances which contains most Houses
            and all Great Fairies.

            'All Interiors':
            Extended version of 'Simple Interiors' with some extra places:
            Windmill, Link's House, Temple of Time and Kakariko Potion Shop.

            When shuffling any interior entrances, trade quest timers are disabled
            and items never revert, even when dying or loading a save.
        ''',
        shared         = True,
        disable        = {
            'off': {'settings': ['shuffle_hideout_entrances']},
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('off',    2),
                ('simple', 1),
                ('all',    1),
            ],
        },
    )

    shuffle_hideout_entrances = Checkbutton(
        gui_text       = "Shuffle Thieves' Hideout Entrances",
        gui_tooltip    = '''\
            Shuffle the pool of entrances to Thieves' Hideout
            into the pool of interior entrances.

            Note that savewarping in any room of Thieves' Hideout
            always takes you to the first room (with 1 torch).

            There is an extra heart piece on the balcony above the jail in
            Gerudo's Fortress if accessed as child. This is not shuffled
            and not considered in logic.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_grotto_entrances = Checkbutton(
        gui_text       = 'Shuffle Grotto Entrances',
        gui_tooltip    = '''\
            Shuffle the pool of grotto entrances, including all graves,
            small Fairy Fountains and the Lost Woods Stage.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_dungeon_entrances = Combobox(
        gui_text       = 'Shuffle Dungeon Entrances',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'simple':    'Dungeon',
            'all':       'Dungeon and Ganon',
        },
        gui_tooltip    = '''\
            Shuffle the pool of dungeon entrances, including Bottom
            of the Well, Ice Cavern, and Gerudo Training Ground.

            Additionally, the entrances of Deku Tree, Fire Temple and
            Bottom of the Well are opened for both adult and child.

            With Dungeon and Ganon selected, all dungeons including Ganon's
            castle will be shuffled.

            Thieves' Hideout is controlled by a separate setting.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                ('off',    2),
                ('simple', 1),
                ('all',    1),
            ],
        },
    )

    shuffle_bosses = Combobox(
        gui_text       = 'Shuffle Boss Entrances',
        gui_tooltip    = '''\
            Shuffle dungeon boss rooms.  This affects the boss rooms of all stone and medallion dungeons.

            'Age-Restricted':
            Shuffle the locations of child boss rooms and adult boss rooms separately.

            'Full':
            Shuffle the locations of all boss rooms together.  Child may be expected to defeat Phantom Ganon and/or Bongo Bongo.
        ''',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'limited':   'Age-Restricted',
            'full':      'Full',
        },
        disable        = {
            'off' : {'settings': ['shuffle_ganon_tower']},
        },
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_ganon_tower = Checkbutton(
        gui_text       = "Shuffle Ganon's Tower Entrance",
        gui_tooltip    = '''\
            Shuffle the entrance from Ganon's Castle to
            Ganon's Tower, just behind the trials barrier,
            into the adult boss entrance pool if "Shuffle
            Boss Entrances" is set to "Age-Restricted", or
            the boss entrance pool if it's set to "Full".

            The entrance from Ganon's Tower to Ganondorf's
            boss room is never shuffled.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_overworld_entrances = Checkbutton(
        gui_text       = 'Shuffle Overworld Entrances',
        gui_tooltip    = '''\
            Shuffle the pool of Overworld entrances, which corresponds
            to almost all loading zones between Overworld areas.

            Some entrances are kept unshuffled to avoid issues:
            - Hyrule Castle Courtyard and Garden entrances
            - Both Market Back Alley entrances

            The entrance from Gerudo Valley to Lake Hylia is a one-way
            entrance and has its own setting below.

            Just like when shuffling interior entrances, shuffling overworld
            entrances disables trade timers and trade items never revert,
            even when dying or loading a save.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_gerudo_valley_river_exit = Checkbutton(
        gui_text       = 'Shuffle Gerudo Valley River Exit',
        gui_tooltip    = '''\
            Randomize where the the one-way entrance
            down the river in Gerudo Valley leads to.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    owl_drops = Checkbutton(
        gui_text       = 'Randomize Owl Drops',
        gui_tooltip    = '''\
            Randomize where Kaepora Gaebora (the Owl) drops you at
            when you talk to him at Lake Hylia or at the top of
            Death Mountain Trail.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    warp_songs = Checkbutton(
        gui_text       = 'Randomize Warp Song Destinations',
        gui_tooltip    = '''\
            Randomize where each of the 6 warp songs leads to.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    spawn_positions = MultipleSelect(
        gui_text       = 'Randomize Overworld Spawns',
        choices         = {
            'child': 'Child',
            'adult': 'Adult',
        },
        gui_tooltip    = '''\
            Randomize where you start when loading
            a save in the Overworld. This means you may not necessarily
            spawn inside Link's House or Temple of Time.

            'Child': Child overworld spawn will be randomized.

            'Adult': Adult overworld spawn will be randomized.

            Selecting both options will randomize both spawns.

            This stays consistent after saving and loading the game again.
        ''',
        default        = [],
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    free_bombchu_drops = Checkbutton(
        gui_text       = 'Add Bombchu Bag and Drops',
        gui_tooltip    = '''\
            Bombchus are properly considered in logic.

            The first Bombchu pack will always be a
            Bombchu Bag giving the same amount of Bombchus
            as would have been given by the item normally.
            For example, finding the Bombchus (5) item
            first will give the Bombchu Bag with 5
            Bombchus inside.

            Bombchu refills will drop from grass, pots,
            crates, and enemies after finding the bag.

            Bombchus can be purchased for 60/99/180
            rupees once the bag has been found.

            The Wasteland carpet merchant will not sell
            unshuffled Bombchus without finding a Bombchu
            Bag. If he is shuffled, he will sell his item
            without a Bombchu Bag.

            Bombchu Bowling opens with either Bomb Bag or
            Bombchu Bag. The Bombchu and Bomb prizes (3rd
            and 4th respectively) will change to a Purple
            Rupee if the corresponding bag has not yet been
            found.
        ''',
        default        = True,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    one_item_per_dungeon = Checkbutton(
        gui_text       = 'Dungeons Have One Major Item',
        gui_tooltip    = '''\
            Dungeons have exactly one major item.
            This naturally makes each dungeon similar in value
            rather than vary based on shuffled locations.

            Spirit Temple Colossus hands count as part
            of the dungeon. Spirit Temple has TWO items
            to match vanilla distribution.

            Boss Keys and Fortress Keys only count as
            major items if they are shuffled Anywhere
            (Keysanity) or in Any Dungeon, and Small
            Keys only count as major items if they are
            shuffled Anywhere (Keysanity). This setting
            is disabled if Small Keys are shuffled in
            Any Dungeon.

            GS Tokens only count as major items if the
            bridge or Ganon Boss Key requirements are
            set to "GS Tokens".

            Heart Containers and Pieces of Heart only
            count as major items if the bridge or Ganon
            Boss Key requirements are set to "Hearts".

            Bombchus only count as major items if they
            are considered in logic.

            Pre-completed dungeons (if any) won't have
            a major item.

            This setting has potential to conflict with
            other randomizer settings. Should seeds continuously
            fail to generate, consider turning this option off.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_song_items = Combobox(
        gui_text       = 'Shuffle Songs',
        default        = 'song',
        choices        = {
            'song':    'Song Locations',
            'dungeon': 'Dungeon Rewards',
            'any':     'Anywhere',
            },
        gui_tooltip    = '''\
            This restricts where song items can appear.

            'Song Locations': Song will only appear at locations that
            normally teach songs. In Multiworld, songs will only
            appear in their own world.

            'Dungeon Rewards': Songs appear at the end of dungeons.
            For major dungeons, they will be at the boss heart
            container location. The remaining 4 songs are placed at:

            - Zelda's Lullaby Location
            - Ice Cavern's Serenade of Water Location
            - Bottom of the Well's Lens of Truth Location
            - Gerudo Training Ground's Ice Arrow Location

            If some dungeons are pre-completed, songs that would have
            been located inside these dungeons are given for free along
            with the free dungeon rewards.

            'Anywhere': Songs can appear in any location.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('song',    2),
                ('dungeon', 1),
                ('any',     1),
            ],
        },
        shared         = True,
    )

    shopsanity = Combobox(
        gui_text       = 'Shopsanity',
        default        = 'off',
        choices        = {
            'off':    'Off',
            '0':      '0 Items Per Shop',
            '1':      '1 Item Per Shop',
            '2':      '2 Items Per Shop',
            '3':      '3 Items Per Shop',
            '4':      '4 Items Per Shop',
            'random': 'Random # of Items Per Shop',
        },
        disable        = {
            'off':  {'settings': ['shopsanity_prices']},
            '0':    {'settings': ['shopsanity_prices']},
        },
        gui_tooltip    = '''\
            Randomizes Shop contents.

            'X Items Per Shop': Each shop will have the
            specified number of items randomized and they
            will always appear on the left side
            (identified by the Special Deal! text).
            Remaining items will be shuffled between shops.

            'Random # of Items Per Shop': Each shop will
            have 0 to 4 Special Deals.

            The randomized items have no requirements
            except money, while the remaining items retain
            normal requirements. Tunics that aren't a
            Special Deal! will still require you to be an
            adult to purchase for example.

            Bombchu Special Deals will unlock the Bombchu
            slot in your inventory and allow purchase of
            Bombchu Refills if "Bombchus are considered in
            logic" is enabled. Otherwise, the Bomb Bag is
            required to purchase Bombchu Refills.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('off',    6),
                ('0',      1),
                ('1',      1),
                ('2',      1),
                ('3',      1),
                ('4',      1),
                ('random', 1),
            ],
        },
    )

    shopsanity_prices = Combobox(
        gui_text         = 'Shopsanity Prices',
        default          = 'random',
        choices          = {
            'random':          "Random",
            'random_starting': "Starting Wallet",
            'random_adult':    "Adult's Wallet",
            'random_giant':    "Giant's Wallet",
            'random_tycoon':   "Tycoon's Wallet",
            'affordable':      "Affordable",
        },
        gui_tooltip      = '''\
            Controls the randomization of prices for shopsanity items.
            For more control, utilize the plandomizer.

            'Random': The default randomization. Shop prices for
            shopsanity items will range between 0 to 300 rupees,
            with a bias towards values slightly below the middle of the
            range, in multiples of 5.

            'X Wallet': Shop prices for shopsanity items will range
            between 0 and the specified wallet's maximum capacity,
            in multiples of 5.

            'Affordable': Shop prices for shopsanity items will be
            fixed to 10 rupees.
        ''',
        disabled_default =  'random',
        shared           = True,
        gui_params       = {
            "hide_when_disabled": True,
        },
    )

    tokensanity = Combobox(
        gui_text       = 'Tokensanity',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'dungeons':  'Dungeons Only',
            'overworld': 'Overworld Only',
            'all':       'All Tokens',
            },
        gui_tooltip    = '''\
            Token reward from Gold Skulltulas are
            shuffled into the pool.

            'Dungeons Only': This only shuffles
            the GS locations that are within
            dungeons, increasing the value of
            most dungeons and making internal
            dungeon exploration more diverse.

            'Overworld Only': This only shuffles
            the GS locations that are outside
            of dungeons.

            'All Tokens': Effectively adds 100
            new locations for items to appear.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_scrubs = Combobox(
        gui_text       = 'Scrub Shuffle',
        default        = 'off',
        choices        = {
            'off':     'Off',
            'low':     'On (Affordable)',
            'regular': 'On (Expensive)',
            'random':  'On (Random Prices)',
        },
        gui_tooltip    = '''\
            'Off': Only the 3 Scrubs that give one-time
            items in the vanilla game (PoH, Deku Nut
            capacity, and Deku Stick capacity) will
            have random items.

            'Affordable': All Scrub prices will be
            reduced to 10 rupees each.

            'Expensive': All Scrub prices will be
            their vanilla prices. This will require
            spending over 1000 rupees on Scrubs.

            'Random Prices': All Scrub prices will be
            between 0-99 rupees. This will on average
            be very, very expensive overall.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('off', 1),
                ('low', 1),
            ],
        },
    )

    shuffle_child_trade = MultipleSelect(
        gui_text       = 'Shuffle Child Trade Sequence Items',
        default        = [],
        choices        = {
            'Weird Egg':     'Weird Egg',
            'Chicken':       'Chicken',
            'Zeldas Letter': "Zelda's Letter",
            'Keaton Mask':   'Keaton Mask',
            'Skull Mask':    'Skull Mask',
            'Spooky Mask':   'Spooky Mask',
            'Bunny Hood':    'Bunny Hood',
            'Goron Mask':    'Goron Mask',
            'Zora Mask':     'Zora Mask',
            'Gerudo Mask':   'Gerudo Mask',
            'Mask of Truth': 'Mask of Truth',
        },
        gui_tooltip    = '''\
            Select the items to shuffle in the child trade sequence.

            To skip Child Zelda, do not shuffle Zelda's Letter and
            add it as a starting item.
        ''',
        shared         = True,
    )

    shuffle_freestanding_items = Combobox(
        gui_text       = 'Shuffle Rupees & Hearts',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'all':       'All',
            'overworld': 'Overworld Only',
            'dungeons':  'Dungeons Only',
        },
        gui_tooltip    = '''\
            Shuffles freestanding rupees and recovery hearts, also shuffles:
                Shadow Temple Spinning Pot Drop
                All Goron Pot faces

            Off: No freestanding rupees/recovery hearts are shuffled.
            All: All Visible freestanding rupees/recovery hearts are shuffled.
            Overworld Only: Freestanding rupees/recovery hearts in the overworld are shuffled.
            Dungeons Only: Freestanding rupees/recovery hearts in dungeons are shuffled.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
        shared         = True,
    )

    shuffle_pots = Combobox(
        gui_text       = 'Shuffle Pots',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'all':       'All',
            'overworld': 'Overworld Only',
            'dungeons':  'Dungeons Only',
        },
        gui_tooltip    = '''\
            Shuffles pots, flying pots into the location pool.

            Off: Not shuffled.
            All: All pots/flying pots are shuffled.
            Overworld Only: Only overworld pots/flying pots are shuffled.
            Dungeons Only: Only dungeon pots/flying pots are shuffled.

            When this setting is enabled, the pots in Ganon's Tower will be
            accessible without Ganon's Boss Key. Proceeding up the tower out
            of the room with the pots will require Ganon's Boss Key.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
        shared         = True,
        disable        = {
            'off': {'settings': ['shuffle_empty_pots']},
        }
    )

    shuffle_empty_pots = Checkbutton(
        gui_text       = 'Include Empty Pots',
        default        = False,
        gui_tooltip    = '''\
            Enabling this will include empty pots into the location
            pool based on the Shuffle Pots setting chosen.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
        },
        shared         = True
    )

    shuffle_crates = Combobox(
        gui_text       = 'Shuffle Crates',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'all':       'All',
            'overworld': 'Overworld Only',
            'dungeons':  'Dungeons Only',
        },
        gui_tooltip    = '''\
            Shuffles large and small crates into the location pool.

            Off: Not shuffled.
            All: crates are shuffled.
            Overworld Only: Only overworld crates are shuffled.
            Dungeons Only: Only dungeon crates are shuffled.

            Note: Only crates which normally drop an item are shuffled. Empty crates are not included.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
        shared         = True,
        disable        = {
            'off': {'settings': ['shuffle_empty_crates']},
        }
    )

    shuffle_empty_crates = Checkbutton(
        gui_text       = 'Include Empty Crates',
        default        = False,
        gui_tooltip    = '''\
            Enabling this will include empty crates into the location
            pool based on the Shuffle Crates setting chosen.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
        },
        shared         = True
    )

    shuffle_cows = Checkbutton(
        gui_text       = 'Shuffle Cows',
        gui_tooltip    = '''\
            Enabling this will let cows give you items
            upon performing Epona's song in front of them.
            There are 9 cows, and an extra in MQ Jabu.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_beehives = Checkbutton(
        gui_text       = 'Shuffle Beehives',
        gui_tooltip    = '''\
            Enabling this will let beehives drop items.
            There are 32 Beehives located in:
                Generic Grottos (x2 per grotto)
                2 Scrub Grottos (x1 per grotto)
                3 Scrub Grottos (x1 per grotto)
                DMT Cow Grotto (x1)
                Zora's Domain (x3 child only)
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_wonderitems = Checkbutton(
        gui_text       = 'Shuffle Wonderitems',
        gui_tooltip    = '''\
            Enabling will shuffle drops from wonderitems.

            Wonderitems are invisible items in the game that will drop an
            item under a certain condition. These items will be marked in the game with a
            sparkle effect when shuffled so they can be easily found. There
            are 4 kinds of shuffled wonderitems.

            Proximity Drop (Yellow): Gives an item when Link touches it.

            Interact Switch (Red): Drops an item when hit with a certain damage type.
                             (Sword, bow, slingshot, or hookshot)

            Free Multitag (Blue): Gives an item when a certain set of tag points
                           are touched. The only free multitag is the stepping stones
                           in Kokiri Forest.

            Ordered Multitag (Cyan): Gives an item when a set of tag points are touched
                              in a specific order. The only ordered multitag is the
                              grass stepping stones in Kokiri Forest.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_kokiri_sword = Checkbutton(
        gui_text       = 'Shuffle Kokiri Sword',
        gui_tooltip    = '''\
            Enabling this shuffles the Kokiri Sword into the pool.

            This will require extensive use of sticks until the
            sword is found.
        ''',
        default        = True,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_ocarinas = Checkbutton(
        gui_text       = 'Shuffle Ocarinas',
        gui_tooltip    = '''\
            Enabling this shuffles the Fairy Ocarina and the Ocarina
            of Time into the pool.

            This will require finding an Ocarina before being able
            to play songs.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_gerudo_card = Checkbutton(
        gui_text       = "Shuffle Gerudo Card",
        gui_tooltip    = '''\
            Enabling this shuffles the Gerudo Card into the item pool.

            The Gerudo Card is required to enter the Gerudo Training Ground
            and prevents the guards from throwing you in jail.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_beans = Checkbutton(
        gui_text       = 'Shuffle Magic Beans',
        gui_tooltip    = '''\
            Enabling this adds a pack of 10 beans to the item pool
            and changes the Magic Bean Salesman to sell a random
            item once at the price of 60 Rupees.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_expensive_merchants = Checkbutton(
        gui_text       = 'Shuffle Expensive Merchants',
        gui_tooltip    = '''\
            Enabling this adds a Giant's Knife and a pack of Bombchus
            to the item pool and changes Medigoron, Granny's Potion Shop,
            and the Haunted Wasteland Carpet Salesman to sell a random
            item once at the same price as their vanilla items.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_frog_song_rupees = Checkbutton(
        gui_text       = 'Shuffle Frog Song Rupees',
        gui_tooltip    = '''\
            Enabling this adds 5 Purple Rupees to the item pool
            and shuffles the rewards from playing Zelda's Lullaby,
            Epona's Song, Saria's Song, Sun's Song, and Song of Time
            to the frogs in Zora's River.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_individual_ocarina_notes = Checkbutton(
        gui_text       = 'Shuffle Individual Ocarina Notes',
        gui_tooltip    = '''\
            Enabling this locks all Ocarina inputs, and adds 5
            new items to find that each unlock one of the 5
            Ocarina notes.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    )

    shuffle_loach_reward = Combobox(
        gui_text       = 'Shuffle Hyrule Loach Reward',
        gui_tooltip    = '''\
            Enabling this shuffles the reward for catching the
            Hyrule Loach at the fishing pond into the item pool

            Vanilla Behavior shuffles the reward for catching the loach
            but otherwise keeps all behavior the same as in
            the vanilla game. The loach will spawn every fourth play
            of the fishing minigame and the sinking lure will
            become available only after obtaining the fishing prize
            for link's current age.

            Easier Behavior shuffles the loach reward but also modifies
            some behavior in order to make the loach easier to catch.
            When enabled the loach will always spawn at the
            fishing pond, the sinking lure will be available
            immediately at all four possible positions, and
            the child/adult fishing prizes are still obtainable
            if you use the sinking lure.
        ''',
        default        = 'off',
        choices        = {
            'off':     'Off',
            'vanilla': 'Vanilla Behavior',
            'easy':    'Easier Behavior',
        },
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                ('off',          1),
                ('vanilla',      1),
                ('easy',         1),
            ],
        },
    )

    # Detailed Logic (except "Guarantee Reachable Locations")

    logic_no_night_tokens_without_suns_song = Checkbutton(
        gui_text       = "Nighttime Skulltulas Expect Sun's Song",
        gui_tooltip    = '''\
            GS Tokens that can only be obtained
            during the night expect you to have Sun's
            Song to collect them. This prevents needing
            to wait until night for some locations.
        ''',
        gui_params={
            "hide_when_disabled": True,
        },
        shared         = True,
    )

    disabled_locations = SearchBox(
        gui_text       = "Exclude Locations",
        shared         = True,
        choices        = [location.name for location in LocationIterator(lambda loc: loc.filter_tags is not None)],
        default        = [],
        gui_tooltip    = '''
            Locations in the left column may contain items
            required to complete the game.

            Locations in the right column will never have
            items that are required to complete the game,
            and will only contain junk.

            Most dungeon locations have a MQ alternative.
            If the location does not exist because of MQ
            then it will be ignored. So make sure to
            disable both versions if that is the intent.
        ''',
        gui_params     = {
            'filterdata': {location.name: location.filter_tags for location in LocationIterator(lambda loc: loc.filter_tags is not None)},
        }
    )

    allowed_tricks = SearchBox(
        gui_text       = "Enable Tricks",
        shared         = True,
        choices        = {
            val['name']: gui_text for gui_text, val in logic_tricks.items()
        },
        default        = [],
        gui_params     = {
            'choice_tooltip': {choice['name']: choice['tooltip'] for choice in logic_tricks.values()},
            'filterdata': {val['name']: val['tags'] for _, val in logic_tricks.items()},
            "hide_when_disabled": True,
        },
        gui_tooltip='''
            Tricks moved to the right column are in-logic
            and MAY be required to complete the game.

            Tricks in the left column are NEVER required.

            Tricks are only relevant for Glitchless logic.
        '''
    )

    # Starting Inventory

    starting_items = SettingInfoDict(None, None, True, {})

    starting_equipment = SearchBox(
        gui_text       = "Starting Equipment",
        shared         = True,
        choices        = {
            key: value.gui_text for key, value in StartingItems.equipment.items()
        },
        default        = [],
        gui_tooltip    = '''\
            Begin the game with the selected equipment.
        ''',
    )

    starting_songs = SearchBox(
        gui_text       = "Starting Songs",
        shared         = True,
        choices        = {
            key: value.gui_text for key, value in StartingItems.songs.items()
        },
        default        = [],
        gui_tooltip    = '''\
            Begin the game with the selected songs already learnt.
        ''',
    )

    starting_inventory = SearchBox(
        gui_text       = "Starting Items",
        shared         = True,
        choices        = {
            key: value.gui_text for key, value in StartingItems.inventory.items()
        },
        default        = [],
        gui_tooltip    = '''\
            Begin the game with the selected inventory items.
            Selecting multiple progressive items will give
            the appropriate number of upgrades.

            If playing with Open Zora's Fountain, the Ruto's Letter
            is converted to a regular Bottle.
        ''',
    )

    start_with_consumables = Checkbutton(
        gui_text       = 'Start with Consumables',
        gui_tooltip    = '''\
            Start the game with maxed out Deku Sticks and Deku Nuts.
        ''',
        shared         = True,
    )

    start_with_rupees = Checkbutton(
        gui_text       = 'Start with Max Rupees',
        gui_tooltip    = '''\
            Start the game with a full wallet.
            Wallet upgrades will also fill the wallet.
        ''',
        shared         = True,
    )

    starting_hearts = Scale(
        gui_text         = "Starting Hearts",
        default          = 3,
        minimum          = 3,
        maximum          = 20,
        gui_tooltip      = '''\
            Start the game with the selected number of hearts.
            Heart Containers and Pieces of Heart are removed
            from the item pool in equal proportion.
        ''',
        disabled_default = 1,
        shared           = True,
    )

    # Other

    skip_reward_from_rauru = Checkbutton(
        gui_text       = 'Free Reward from Rauru',
        gui_tooltip    = '''\
            The item given by Rauru beyond the Door of Time
            (the Light Medallion in the vanilla game) is
            given as a starting item instead.
        ''',
        shared         = True,
    )

    no_escape_sequence = Checkbutton(
        gui_text       = 'Skip Tower Escape Sequence',
        gui_tooltip    = '''\
            The tower escape sequence between
            Ganondorf and Ganon will be skipped.
        ''',
        shared         = True,
    )

    no_guard_stealth = Checkbutton(
        gui_text       = 'Skip Child Stealth',
        gui_tooltip    = '''\
            The crawlspace into Hyrule Castle goes
            straight to Zelda, skipping the guards.
        ''',
        shared         = True,
    )

    no_epona_race = Checkbutton(
        gui_text       = 'Skip Epona Race',
        gui_tooltip    = '''\
            Epona can be summoned with Epona's Song
            without needing to race Ingo.
        ''',
        shared         = True,
    )

    skip_some_minigame_phases = Checkbutton(
        gui_text       = 'Skip Some Minigame Phases',
        gui_tooltip    = '''\
            Awards all eligible prizes after the first attempt for
            Dampe Race and Gerudo Horseback Archery.

            Dampe will start with the second race so you can finish
            the race in under a minute and get both rewards at once.
            You still get the first reward from the chest even if you
            don't complete the race in under a minute.

            Both rewards at the Gerudo Horseback Archery will be
            available from the first time you play the minigame.
            This means you can get both rewards at once if you get
            1500 points in a single attempt.
        ''',
        shared         = True,
    )

    complete_mask_quest = Checkbutton(
        gui_text       = 'Complete Mask Quest',
        gui_tooltip    = '''\
            Once the Happy Mask Shop is opened,
            all masks will be available to be borrowed.
        ''',
        shared         = True,
    )

    useful_cutscenes = Checkbutton(
        gui_text       = 'Enable Specific Glitch-Useful Cutscenes',
        gui_tooltip    = '''\
            The cutscenes of the Poes in Forest Temple and Darunia in
            Fire Temple will not be skipped. These cutscenes are useful
            in glitched gameplay only and do not provide any timesave
            for glitchless playthroughs.
        ''',
        shared         = True,
    )

    fast_chests = Checkbutton(
        gui_text       = 'Fast Chest Cutscenes',
        gui_tooltip    = '''\
            All chest animations are fast. If disabled,
            the animation time is slow for major items.
        ''',
        default        = True,
        shared         = True,
    )

    free_scarecrow = Checkbutton(
        gui_text       = "Free Scarecrow's Song",
        gui_tooltip    = '''\
            Pulling out the Ocarina near a
            spot at which Pierre can spawn will
            do so, without needing the song.
        ''',
        shared         = True,
    )

    fast_bunny_hood = Checkbutton(
        gui_text       = 'Fast Bunny Hood',
        gui_tooltip    = '''\
            The Bunny Hood mask behaves like it does
            in Majora's Mask and makes you go 1.5× faster.
        ''',
        shared         = True,
    )

    auto_equip_masks = Checkbutton(
        gui_text       = 'Maintain Mask Equips through Scene Changes',
        gui_tooltip    = '''\
            Keep the currently equipped mask equipped after scene
            changes. Also persists through savewarps. If equip swap
            is used to wear a mask as adult and the ability to
            equip swap masks is lost, travelling through time will
            unequip the mask as adult.
        ''',
        default        = False,
        shared         = True,
    )

    plant_beans = Checkbutton(
        gui_text       = 'Plant Magic Beans',
        gui_tooltip    = '''\
            Enabling this plants all 10 magic beans in soft soil
            causing the bean plants to be available as adult. You
            can still get beans normally.
        ''',
        default        = False,
        shared         = True,
    )

    chicken_count_random = Checkbutton(
        gui_text       = 'Random Cucco Count',
        gui_tooltip    = '''\
            Anju will give a reward for collecting a random
            number of Cuccos.
        ''',
        disable        = {
            True: {'settings': ['chicken_count']},
        },
        shared         = True,
    )

    chicken_count = Scale(
        gui_text       = 'Cucco Count',
        default        = 7,
        minimum        = 0,
        maximum        = 7,
        gui_tooltip    = '''\
            Anju will give a reward for turning
            in the chosen number of Cuccos.
        ''',
        shared         = True,
        gui_params     = {
            'no_line_break': True,
        },
    )

    big_poe_count_random = Checkbutton(
        gui_text       = 'Random Big Poe Target Count',
        gui_tooltip    = '''\
            The Poe buyer will give a reward for turning
            in a random number of Big Poes.
        ''',
        disable        = {
            True: {'settings': ['big_poe_count']},
        },
        shared         = True,
    )

    big_poe_count = Scale(
        gui_text         = "Big Poe Target Count",
        default          = 10,
        minimum          = 1,
        maximum          = 10,
        gui_tooltip      = '''\
            The Poe buyer will give a reward for turning
            in the chosen number of Big Poes.
        ''',
        disabled_default = 1,
        shared           = True,
    )

    easier_fire_arrow_entry = Checkbutton(
        gui_text       = 'Easier Fire Arrow Entry',
        gui_tooltip    = '''\
            It is possible to open the Shadow Temple entrance
            by lighting the torches with Fire Arrows, but
            can be difficult to light all 24 torches in time.
            Enabling this setting allows you to reduce the
            number of torches that need to be lit to open
            the entrance, making it easier to perform
            Fire Arrow Entry.

            Note that this setting does not affect logic.
            Whether it's used or not, the trick "Shadow Temple
            Entry with Fire Arrows" must be enabled for it to be
            in logic.
        ''',
        disable        = {
            False: {'settings': ['fae_torch_count']},
        },
        shared         = True,
    )

    fae_torch_count = Scale(
        gui_text       = 'Fire Arrow Entry Torch Count',
        default        = 3,
        minimum        = 1,
        maximum        = 23,
        gui_tooltip    = '''\
            The entrance to Shadow Temple will open
            after the chosen number of torches are lit.
        ''',
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    ruto_already_f1_jabu = Checkbutton(
        gui_text       = 'Ruto Already at F1',
        gui_tooltip    = '''\
            Ruto in Jabu Jabu's Belly will already be at the top floor.
            Only applied in the original version of the dungeon, since
            in Master Quest you don't need to bring Ruto up.
        ''',
        default        = False,
        shared         = True,
    )

    ocarina_songs = Combobox(
        gui_text       = 'Randomize Ocarina Melodies',
        default        = 'off',
        choices        = {
            'off': 'Off',
            'frog': 'Frog Songs Only',
            'warp': 'Warp Songs Only',
            'all':  'All Songs',
        },
        gui_tooltip    = '''\
            Will need to memorize a new set of songs.
            Can be silly, but difficult. All songs are
            generally sensible, but warp songs are
            typically more difficult than frog songs.
            ''',
        shared         = True,
    )

    correct_chest_appearances = Combobox(
        gui_text       = 'Chest Appearance Matches Contents',
        default        = 'off',
        choices        = {
            'off': 'Off',
            'textures': 'Texture',
            'both':  'Both Size and Texture',
            'classic': 'Classic'
        },
        gui_tooltip    = '''\
            If "Texture" is enabled, chest texture will reflect its contents
            regardless of size.  Fancy chests will contain keys,
            Gilded chests will contain major items, shuffled
            tokens will be in Webbed chests, and Wooden chests
            will contain the rest.
            This allows skipping chests if they are wooden.
            However, skipping wooden chests will mean having
            low health, ammo, and rupees, so doing so is a risk.

            "Size and Texture" will change chests with major
            items and boss keys into big chests, and everything
            else into small chests.

            "Classic" is the behavior of CSMC in previous versions of the randomizer.
            This will change chests with major items and boss keys into big chests.
            Boss keys will remain in their fancy chest, while small key will be in a
            smaller version of the fancy chest.
        ''',
        shared         = True,
        disable        = {
            'off': {'settings': ['minor_items_as_major_chest', 'chest_textures_specific']},
            'classic': {'settings': ['chest_textures_specific']},
            '!textures': {'settings': ['soa_unlocks_chest_texture']},
        },
    )

    chest_textures_specific = MultipleSelect(
        gui_text        = 'Chest Textures',
        choices         = {
            'major':    "Major items",
            'bosskeys': "Boss keys",
            'keys':     "Small keys",
            'tokens':   "Gold Skulltula tokens",
            'hearts':   "Hearts",
        },
        default         = ['major', 'bosskeys','keys', 'tokens', 'hearts'],
        gui_tooltip     = '''\
            Select specific chest textures.
            Any unchecked option will make all items in the category
            appear in brown chests.
        ''',
        shared          = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    soa_unlocks_chest_texture = Checkbutton(
        gui_text       = 'Stone of Agony Unlocks Chest Textures',
        gui_tooltip    = '''\
            Textures for chests will only be correct
            when Stone of Agony is found.
        ''',
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    minor_items_as_major_chest = MultipleSelect(
        gui_text       = 'Minor Items in Big/Gold chests',
        choices        = {
            'bombchus': 'Bombchus',
            'shields':  'Deku & Hylian Shields',
            'capacity': 'Deku Stick & Nut Capacity',
        },
        gui_tooltip    = '''\
            Chests with Hylian or Deku Shields, Deku Stick
            or Nut Capacity, or Bombchus will appear in Big
            and/or Gold chests, depending on the Chest
            Appearance Matches Contents setting. Bombchus
            are always in big chests if Add Bombchu Bag and
            Drops is on.
        ''',
        shared         = True,
        default        = [],
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    invisible_chests = Checkbutton(
        gui_text       = 'Invisible Chests',
        gui_tooltip    = '''\
            Chests will only be visible with the
            Lens of Truth. Lens is not logically
            required for normally visible chests.
        ''',
        shared         = True,
    )

    correct_potcrate_appearances = Combobox(
        gui_text       = 'Pot, Crate, & Beehive Appearance Matches Contents',
        default        = 'textures_unchecked',
        choices        = {
            'off':                'Off',
            'textures_content':   'Texture (Match Content)',
            'textures_unchecked': 'Texture (Unchecked)',
        },
        gui_tooltip    = '''\
            If enabled, pot/crate textures, and beehive wiggling will reflect its contents.

            Off - Pots, crates, and beehives will appear as vanilla.

            Texture (Match Content) - Pot and crate textures will reflect the contents.
            Golden Pots/crates will contain major items.
            Pots/crates with keys on them will contain small keys.
            Pots/crates containing boss keys will use a variation of the boss key chest texture.
            Pots/crates with a spider web on them contain Gold Skulltula tokens.
            All other items will use the original texture.
            The texture will revert to the original texture once the item is collected.
            Beehives containing non-junk items will wiggle until collected.

            Texture (Unchecked) - All pots/crates containing shuffled items
            will appear with a golden texture. The texture will revert to the
            original texture once the item is collected.
            Beehives will wiggle until their item is collected.
        ''',
        shared         = True,
        disable        = {
            '!textures_content': {'settings': ['potcrate_textures_specific', 'soa_unlocks_potcrate_texture']},
        },
    )

    potcrate_textures_specific = MultipleSelect(
        gui_text        = 'Pot and Crate Textures',
        choices         = {
            'major':    "Major items",
            'bosskeys': "Boss keys",
            'keys':     "Small keys",
            'tokens':   "Gold Skulltula tokens",
            'hearts':   "Hearts",
        },
        default         = ['major', 'bosskeys', 'keys', 'tokens', 'hearts'],
        gui_tooltip     = '''\
            Select specific pots and crates textures.
            Any unchecked option will make all items in the category
            appear in regular pots/crates.
        ''',
        shared          = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    soa_unlocks_potcrate_texture = Checkbutton(
        gui_text       = 'Stone of Agony Unlocks Pot and Crate Textures',
        gui_tooltip    = '''\
            Textures for pots and crates will only be correct
            when Stone of Agony is found.
        ''',
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    )

    key_appearance_match_dungeon = Checkbutton(
        gui_text       = 'Key Appearance Matches Dungeon',
        gui_tooltip    = '''\
            Small keys and boss keys (not key rings)
            will use custom models to match their dungeon.
        ''',
        shared         = True,
    )

    clearer_hints = Checkbutton(
        gui_text       = 'Clearer Hints',
        gui_tooltip    = '''\
            The hints provided by Gossip Stones will
            be very direct if this option is enabled.
        ''',
        shared         = True,
        default        = True,
    )

    hints = Combobox(
        gui_text       = 'Gossip Stones',
        default        = 'always',
        choices        = {
            'none':   'No Hints',
            'mask':   'Hints; Need Mask of Truth',
            'agony':  'Hints; Need Stone of Agony',
            'always': 'Hints; Need Nothing',
        },
        gui_tooltip    = '''\
            Gossip Stones can be made to give hints
            about where items can be found.

            Different settings can be chosen to
            decide which item is needed to
            speak to Gossip Stones. Choosing to
            stick with the Mask of Truth will
            make the hints very difficult to
            obtain.

            Hints for 'on the way of the hero' are
            locations that contain items that are
            required to beat the game.
        ''',
        shared         = True,
    )

    hint_dist = Combobox(
        gui_text       = 'Hint Distribution',
        default        = 'balanced',
        choices        =hint_dist_list(),
        gui_tooltip    =hint_dist_tips(),
        gui_params     = {
            "dynamic": True,
        },
        shared         = True,
        disable        = {
            '!bingo' : {'settings': ['bingosync_url']},
        },
    )

    bingosync_url = Textinput(
        gui_text       = "Bingosync URL",
        shared         = False,
        gui_tooltip    = '''\
            Enter a URL to a Bingosync bingo board in
            order to have hints specific to items needed
            to beat the board. Goals which are completed simply
            by finding a specific item are not hinted
            (e.g. "Boomerang").
            In addition, overworld tokensanity will always
            hint the location of Sun's Song, and shopsanity
            will always hint the location of a wallet.

            Leaving this entry blank or providing an
            invalid URL will generate generic item hints
            designed to allow completion of most bingo goals.
            Non Bingosync bingo boards are not directly
            supported, and will also generate generic item hints.
        ''',
        disabled_default = None,
        gui_params       = {
            "size"               : "full",
            "hide_when_disabled" : True,
        },
    )

    item_hints = SettingInfoList(
        gui_type       = None,
        gui_text       = None,
        shared         = True,
        choices        = [name for name, item in ItemInfo.items.items() if item.type not in ('Drop', 'Event', 'Refill', 'Shop')]
    )

    hint_dist_user = SettingInfoDict(None, None, True, {})

    misc_hints = MultipleSelect(
        gui_text        = 'Misc. Hints',
        choices         = {
            'altar':       'Temple of Time Altar',
            'dampe_diary': "Dampé's Diary (Hookshot)",
            'ganondorf':   'Ganondorf (Light Arrows)',
            'warp_songs_and_owls':  'Warp Songs and Owls',
            '10_skulltulas':  'House of Skulltula: 10',
            '20_skulltulas':  'House of Skulltula: 20',
            '30_skulltulas':  'House of Skulltula: 30',
            '40_skulltulas':  'House of Skulltula: 40',
            '50_skulltulas':  'House of Skulltula: 50',
            'frogs2':         'Frogs Ocarina Game',
            'mask_shop':  'Shuffled Mask Shop',
            'unique_merchants':  'Unique Merchants',
        },
        gui_tooltip    = '''\
            This setting adds some hints at locations
            other than Gossip Stones:

            Reading the Temple of Time altar as child
            will tell you the locations of the
            Spiritual Stones (unless Maps and Compasses
            Give Information is enabled).

            Reading the Temple of Time altar as adult
            will tell you the locations of the Medallions
            (unless Maps and Compasses Give Information
            is enabled), as well as the conditions for
            building the Rainbow Bridge and getting the
            Boss Key for Ganon's Castle.

            Reading the diary of Dampé the gravekeeper
            as adult will tell you the location of one
            of the Hookshots.

            Talking to Ganondorf in his boss room will
            tell you the location of the Light Arrows.
            If this option is enabled and Ganondorf
            is reachable without Light Arrows, Gossip
            Stones will never hint the Light Arrows.

            Playing a warp song will tell you where
            it leads. (If warp song destinations
            are vanilla, this is always enabled.)
            The two Owls at Lake Hylia and Death Mountain
            that move you around will tell you where they go.

            Talking to a cursed House of Skulltula
            resident will tell you the reward they will
            give you for removing their curse.

            Placing yourself on the log at Zora River
            where you play the songs for the frogs will
            tell you what the reward is for playing all
            six non warp songs.

            If shuffled, right side items in the mask
            shop will be visible but not obtainable
            before completing the child trade quest.
            Mask of Truth's shelf slot is always visible.

            If Shuffle Expensive Merchants is enabled, the
            three characters that sell a new item will tell
            what the reward is for buying their item.
            If Shuffle Magic Beans is enabled, the Magic bean
            salesman will tell what the reward is for buying
            the 60 Rupees item.
        ''',
        shared         = True,
        default        = ['altar', 'ganondorf', 'warp_songs_and_owls'],
    )

    text_shuffle = Combobox(
        gui_text       = 'Text Shuffle',
        default        = 'none',
        choices        = {
            'none':         'No Text Shuffled',
            'except_hints': 'Shuffled except Important Text',
            'complete':     'All Text Shuffled',
        },
        gui_tooltip    = '''\
            Will make things confusing for comedic value.

            'Shuffled except Important Text': For when
            you want comedy but don't want to impact
            gameplay. Text that has an impact on gameplay
            is not shuffled. This includes all hint text,
            key text, Good Deal! items sold in shops, random
            price scrubs, chicken count and poe count.
        ''',
        shared         = True,
    )

    damage_multiplier = Combobox(
        gui_text       = 'Damage Multiplier',
        default        = 'normal',
        choices        = {
            'half':      'Half',
            'normal':    'Normal',
            'double':    'Double',
            'quadruple': 'Quadruple',
            'ohko':      'OHKO',
        },
        gui_tooltip    = '''\
            Changes the amount of damage taken.

            'OHKO': Link dies in one hit.
        ''',
        shared         = True,
    )

    deadly_bonks = Combobox(
        gui_text       = 'Bonks Do Damage',
        default        = 'none',
        choices        = {
            'none':      'No Damage',
            'half':      'Quarter Heart',
            'normal':    'Half Heart',
            'double':    'Whole Heart',
            'quadruple': 'Two Hearts',
            'ohko':      'One Bonk KO',
        },
        gui_tooltip    = '''\
            When rolling, hitting a wall or object
            will hurt Link. Damage is unaffected
            by the damage multiplier setting.
        ''',
        shared         = True,
    )

    no_collectible_hearts = Checkbutton(
        gui_text       = 'Hero Mode',
        gui_tooltip    = '''\
            No recovery hearts will drop from
            enemies or objects.
            (You might still find some freestanding
            or in chests depending on other settings.)
        ''',
        default        = False,
        shared         = True,
    )

    starting_tod = Combobox(
        gui_text       = 'Starting Time of Day',
        default        = 'default',
        choices        = {
            'default':       'Default (10:00)',
            'random':        'Random Choice',
            'sunrise':       'Sunrise (6:30)',
            'morning':       'Morning (9:00)',
            'noon':          'Noon (12:00)',
            'afternoon':     'Afternoon (15:00)',
            'sunset':        'Sunset (18:00)',
            'evening':       'Evening (21:00)',
            'midnight':      'Midnight (00:00)',
            'witching-hour': 'Witching Hour (03:00)',
        },
        gui_tooltip    = '''\
            Change up Link's sleep routine.

            Daytime officially starts at 6:30,
            nighttime at 18:00 (6:00 PM).
        ''',
        shared         = True,
    )

    blue_fire_arrows = Checkbutton(
        gui_text       = 'Blue Fire Arrows',
        gui_tooltip    = '''\
            Ice arrows gain the power of blue fire.
            They can be used to melt red ice
            and break the mud walls in Dodongo's Cavern.
        ''',
        default        = False,
        shared         = True,
    )

    fix_broken_drops = Checkbutton(
        gui_text       = 'Fix Broken Drops',
        gui_tooltip    = '''\
            Enabling this fixes drops that are broken in the vanilla game.

            There is a deku shield drop from a pot in the Spirit Temple child
            side Anubis room that does not appear in the vanilla game, and
            logic might require you to get a deku shield this way. There is a
            magic jar on top of the Gerudo Training Ground eye statue that does
            not always refill your magic in the vanilla game.
        ''',
        shared         = True,
    )

    item_pool_value = Combobox(
        gui_text       = 'Item Pool',
        default        = 'balanced',
        choices        = {
            'ludicrous': 'Ludicrous',
            'plentiful': 'Plentiful',
            'balanced':  'Balanced',
            'scarce':    'Scarce',
            'minimal':   'Minimal'
        },
        gui_tooltip    = '''\
            'Ludicrous': Every item in the game is a major
            item. Incompatible with one major item per dungeon.

            'Plentiful': One additional copy of each major
            item is added.

            'Balanced': Original item pool.

            'Scarce': An extra copy of major item upgrades
            that are not required to open location checks
            is removed (e.g. Bow upgrade, Magic upgrade).
            Heart Containers are removed as well. Number
            of Bombchu items is reduced.

            'Minimal': All major item upgrades not used to
            open location checks are removed. All health
            upgrades are removed. Only one Bombchu item is
            available.
        ''',
        shared         = True,
        disable        = {
            'ludicrous':  {'settings': ['one_item_per_dungeon']}
        }
    )

    junk_ice_traps = Combobox(
        gui_text       = 'Ice Traps',
        default        = 'normal',
        choices        = {
            'off':       'No Ice Traps',
            'normal':    'Normal Ice Traps',
            'on':        'Extra Ice Traps',
            'mayhem':    'Ice Trap Mayhem',
            'onslaught': 'Ice Trap Onslaught',
        },
        gui_tooltip    = '''\
            'Off': All Ice Traps are removed.

            'Normal': Only Ice Traps from the base item pool
            are placed.

            'Extra Ice Traps': Chance to add extra Ice Traps
            when junk items are added to the itempool.

            'Ice Trap Mayhem': All added junk items will
            be Ice Traps.

            'Ice Trap Onslaught': All junk items will be
            replaced by Ice Traps, even those in the
            base pool.
        ''',
        shared         = True,
    )

    ice_trap_appearance = Combobox(
        gui_text       = 'Ice Trap Appearance',
        default        = 'major_only',
        choices        = {
            'major_only': 'Major Items Only',
            'junk_only':  'Junk Items Only',
            'anything':   'Anything',
        },
        gui_tooltip    = '''\
            Changes the categories of items Ice Traps may
            appear as, both when freestanding and when in
            chests with Chest Size Matches Contents enabled.

            'Major Items Only': Ice Traps appear as Major
            Items (and in large chests if CSMC enabled).

            'Junk Items Only': Ice Traps appear as Junk
            Items (and in small chests if CSMC enabled).

            'Anything': Ice Traps may appear as anything.
        ''',
        shared         = True,
    )

    adult_trade_shuffle = Checkbutton(
        gui_text       = 'Shuffle All Selected Adult Trade Items',
        gui_tooltip    = '''\
            Enable to shuffle every selected Adult Trade Item.

            If disabled and at least one of "Shuffle Adult Trade
            Sequence Items" is selected, Anju will always give
            a shuffled item even if Pocket Egg has not been shuffled.
        ''',
        shared         = True,
        default        = False,
    )

    adult_trade_start = MultipleSelect(
        gui_text       = 'Shuffle Adult Trade Sequence Items',
        default        = ['Pocket Egg', 'Pocket Cucco', 'Cojiro', 'Odd Mushroom', 'Odd Potion', 'Poachers Saw',
                          'Broken Sword', 'Prescription', 'Eyeball Frog', 'Eyedrops', 'Claim Check'],
        choices        = {
            'Pocket Egg':   'Pocket Egg',
            'Pocket Cucco': 'Pocket Cucco',
            'Cojiro':       'Cojiro',
            'Odd Mushroom': 'Odd Mushroom',
            'Odd Potion':   'Odd Potion',
            'Poachers Saw': "Poacher's Saw",
            'Broken Sword': 'Broken Sword',
            'Prescription': 'Prescription',
            'Eyeball Frog': 'Eyeball Frog',
            'Eyedrops':     'Eyedrops',
            'Claim Check':  'Claim Check',
        },
        gui_tooltip    = '''\
            Select the Adult Trade Sequence items to shuffle.

            If "Shuffle All Selected Adult Trade Items" is
            enabled, every selected item will be shuffled.

            If "Shuffle All Selected Adult Trade Items" is
            disabled, only one of the selected items will be
            shuffled. If the Odd Mushroom, Eyeball Frog, or
            Eyedrops is removed from the player's inventory due
            to an expired timer or game reset, that item can
            be reacquired from its <i>non-shuffled</i> location.
        ''',
        shared         = True,
    )

    # Cosmetics

    default_targeting = Combobox(
        gui_text       = 'Default Targeting Option',
        shared         = False,
        cosmetic       = True,
        default        = 'hold',
        choices        = {
            'hold':   'Hold',
            'switch': 'Switch',
        },
    )

    display_dpad = Combobox(
        gui_text       = 'Display D-Pad HUD',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Shows an additional HUD element displaying
            current available options on the D-Pad.
        ''',
        default        = 'right',
        choices        = {
            'off':   'Off',
            'left':  'On the left',
            'right': 'On the right',
        },
    )

    dpad_dungeon_menu = Checkbutton(
        gui_text       = 'Display D-Pad Dungeon Info',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Shows separated menus on the pause screen for dungeon
            keys, rewards, and Vanilla/MQ info. If disabled, these
            menus are still available by holding the A button and
            one of the D-Pad directions on the pause screen.
        ''',
        default        = True,
    )

    correct_model_colors = Checkbutton(
        gui_text       = 'Item Model Colors Match Cosmetics',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            In-game models for items such as Heart Containers have
            colors matching the colors chosen for cosmetic settings.
            Heart and magic drop icons also have matching colors.

            Tunic colors are excluded from this to prevent not being
            able to discern freestanding Tunics from each other.
        ''',
        default        = True,
    )

    randomize_all_cosmetics = Checkbutton(
        gui_text       = 'Randomize All Cosmetics',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Randomize all cosmetics settings, except those in the "General Cosmetics" and the "Player Models" sections.
        ''',
        default        = False,
        disable        = {
            True: {'sections': ["equipment_color_section", "ui_color_section", "misc_color_section"]},
        }
    )

    uninvert_y_axis_in_first_person_camera = Checkbutton(
        gui_text       = 'Uninvert Y-Axis in First Person Camera',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Uninvert the Y axis in first person camera.
            Note that this can make some tricks or glitches
            harder to pull off.
        ''',
        default        = False,
    )

    input_viewer = Checkbutton(
        gui_text       = 'Input Viewer',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Show the controller inputs in form of icons at the bottom of the screen.
        ''',
        default        = False,
    )

    model_adult = Combobox(
        gui_text       = 'Adult Link Model',
        shared         = False,
        cosmetic       = True,
        choices        = get_model_choices(0),
        gui_tooltip    = '''\
            Link's model will be replaced by the model selected.
            To add more model options, save the .zobj file to
            data/Models/Adult.
            Cosmetics options might not be applied when a
            custom model is in use.
            Caution: Any changes to Link's skeleton have the potential
            to affect gameplay in significant ways and so are disallowed
            for all recorded Racetime races. A note will appear at the top
            of the pause screen if this is the case.
        ''',
        default        = 'Default',
        gui_params     = {
            "hide_when_disabled": True,
            "dynamic":            True,
        },
    )

    model_adult_filepicker = Fileinput(
        gui_text   = "Adult Link Model",
        gui_tooltip = '''\
            Link's model will be replaced by the model selected.
            Cosmetics options might not be applied when a
            custom model is in use.
            Caution: Any changes to Link's skeleton have the potential
            to affect gameplay in significant ways and so are disallowed
            for all recorded Racetime races. A note will appear at the top
            of the pause screen if this is the case.
        ''',
        gui_params = {
            "file_types": [
                {
                  "name": "Z64 Model Files",
                  "extensions": ["zobj"]
                },
                {
                  "name": "All Files",
                  "extensions": ["*"]
                },
            ],
            "hide_when_disabled": True,
        },
    )

    model_child = Combobox(
        gui_text       = 'Child Link Model',
        shared         = False,
        cosmetic       = True,
        choices        = get_model_choices(1),
        gui_tooltip    = '''\
            Link's model will be replaced by the model selected.
            To add more model options, save the .zobj file to
            data/Models/Child.
            Cosmetics options might not be applied when a
            custom model is in use.
            Caution: Any changes to Link's skeleton have the potential
            to affect gameplay in significant ways and so are disallowed
            for all recorded Racetime races. A note will appear at the top
            of the pause screen if this is the case.
        ''',
        default        = 'Default',
        gui_params     = {
            "hide_when_disabled": True,
            "dynamic":            True,
        },
    )

    model_child_filepicker = Fileinput(
        gui_text   = "Child Link Model",
        gui_tooltip = '''\
            Link's model will be replaced by the model selected.
            Cosmetics options might not be applied when a
            custom model is in use.
            Caution: Any changes to Link's skeleton have the potential
            to affect gameplay in significant ways and so are disallowed
            for all recorded Racetime races. A note will appear at the top
            of the pause screen if this is the case.
        ''',
        gui_params = {
            "file_types": [
                {
                  "name": "Z64 Model Files",
                  "extensions": ["zobj"]
                },
                {
                  "name": "All Files",
                  "extensions": ["*"]
                },
            ],
            "hide_when_disabled": True,
        },
    )

    kokiri_color = Combobox(
        gui_text       = "Kokiri Tunic",
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_tunic_color_options(),
        default        = 'Kokiri Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    goron_color = Combobox(
        gui_text       = "Goron Tunic",
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_tunic_color_options(),
        default        = 'Goron Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    zora_color = Combobox(
        gui_text       = "Zora Tunic",
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_tunic_color_options(),
        default        = 'Zora Blue',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    silver_gauntlets_color = Combobox(
        gui_text       = 'Silver Gauntlets Color',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_gauntlet_color_options(),
        default        = 'Silver',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    golden_gauntlets_color = Combobox(
        gui_text       = 'Golden Gauntlets Color',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_gauntlet_color_options(),
        default        = 'Gold',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    mirror_shield_frame_color = Combobox(
        gui_text       = 'Mirror Shield Frame Color',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_shield_frame_color_options(),
        default        = 'Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    heart_color = Combobox(
        gui_text       = 'Heart Color',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_heart_color_options(),
        default        = 'Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    magic_color = Combobox(
        gui_text       = 'Magic Color',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_magic_color_options(),
        default        = 'Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    a_button_color = Combobox(
        gui_text       = 'A Button Color',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_a_button_color_options(),
        default        = 'N64 Blue',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    b_button_color = Combobox(
        gui_text       = 'B Button Color',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_b_button_color_options(),
        default        = 'N64 Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    c_button_color = Combobox(
        gui_text       = 'C Button Color',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_c_button_color_options(),
        default        = 'Yellow',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    start_button_color = Combobox(
        gui_text       = 'Start Button Color',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_start_button_color_options(),
        default        = 'N64 Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    navi_color_default_inner = Combobox(
        gui_text       = "Navi Idle Inner",
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_navi_color_options(),
        default        = 'White',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break': True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    navi_color_default_outer = Combobox(
        gui_text       = "Outer",
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    navi_color_enemy_inner = Combobox(
        gui_text       = 'Navi Targeting Enemy Inner',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_navi_color_options(),
        default        = 'Yellow',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break':  True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    navi_color_enemy_outer = Combobox(
        gui_text       = 'Outer',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    navi_color_npc_inner = Combobox(
        gui_text       = 'Navi Targeting NPC Inner',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_navi_color_options(),
        default        = 'Light Blue',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break':  True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    navi_color_npc_outer = Combobox(
        gui_text       = 'Outer',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    navi_color_prop_inner = Combobox(
        gui_text       = 'Navi Targeting Prop Inner',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_navi_color_options(),
        default        = 'Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break': True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    navi_color_prop_outer = Combobox(
        gui_text       = 'Outer',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    bombchu_trail_color_inner = Combobox(
        gui_text       = 'Bombchu Trail Inner',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_bombchu_trail_color_options(),
        default        = 'Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break': True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    bombchu_trail_color_outer = Combobox(
        gui_text       = 'Outer',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_bombchu_trail_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    boomerang_trail_color_inner = Combobox(
        gui_text       = 'Boomerang Trail Inner',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_boomerang_trail_color_options(),
        default        = 'Yellow',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break': True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    boomerang_trail_color_outer = Combobox(
        gui_text       = 'Outer',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_boomerang_trail_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    sword_trail_color_inner = Combobox(
        gui_text       = 'Sword Trail Inner',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_sword_trail_color_options(),
        default        = 'White',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break': True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    sword_trail_color_outer = Combobox(
        gui_text       = 'Outer',
        shared         = False,
        cosmetic       = True,
        choices        = Colors.get_sword_trail_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                ('Completely Random', 1),
            ],
        },
    )

    sword_trail_duration = ComboboxInt(
        gui_text       = 'Sword Trail Duration',
        shared         = False,
        cosmetic       = True,
        choices        = {
            4: 'Default',
            10: 'Long',
            15: 'Very Long',
            20: 'Lightsaber',
        },
        default        = 4,
        gui_tooltip    = '''\
            Select the duration for sword trails.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution':  [
                (4, 1),
                (10, 1),
                (15, 1),
                (20, 1)
            ],
        },
    )

    # SFX

    randomize_all_sfx = Checkbutton(
        gui_text       = 'Randomize All Sound Effects',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Randomize all sound effects and music settings (ear safe), except the "Adult Voice" and "Child Voice" options and those in the "General" section.
        ''',
        default        = False,
        disable    = {
            True : {'sections' : [ "generalsfx_section", "UIsfx_section", "itemsfx_section" ],
            'settings' : ["sfx_navi_overworld", "sfx_navi_enemy", "sfx_horse_neigh", "sfx_cucco", "background_music", "fanfares", "ocarina_fanfares", "credits_music"]
            }
        }
    )

    disable_battle_music = Checkbutton(
        gui_text       = 'Disable Battle Music',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Disable standard battle music.
            This prevents background music from being
            interrupted by the battle theme when being
            near enemies.
        ''',
        default        = False,
    )

    speedup_music_for_last_triforce_piece = Checkbutton(
        gui_text       = 'Speed Up Music For Last Triforce Piece',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            In Triforce Hunt, the music will speed up slightly
            at one piece from the goal to make it more hype !
            Does not apply on the standard battle enemy music.
        ''',
        default        = False,
    )

    background_music = Combobox(
        gui_text       = 'Background Music',
        shared         = False,
        cosmetic       = True,
        default        = 'normal',
        choices        = {
            'normal':               'Normal',
            'off':                  'No Music',
            'random':               'Random',
            'random_custom_only':   'Random (Custom Only)',
        },
        gui_tooltip    = '''\
            'No Music': No background music is played.

            'Random': Area background music is randomized.
            Additional music can be loaded from data/Music/
        ''',
        gui_params  = {
            'randomize_key': 'randomize_all_sfx',
            'distribution':  [
                ('random', 1),
            ]
        },
    )

    display_custom_song_names = Combobox(
        gui_text       = 'Display Custom Music Names',
        shared         = False,
        cosmetic       = True,
        default        = 'off',
        choices        = {
            'off':   'Off',
            'top':   'At the top of the screen',
            'pause': 'In pause screen only',
        },
        gui_tooltip    = '''\
            'off': Not displayed.

            'At the top of the screen': The song name will be briefly
            displayed at the top of the screen at every scene transition,
            and permanently on the pause screen.

            'In pause screen only': The song name will be displayed only
            on the pause screen.
        ''',
    )

    fanfares = Combobox(
        gui_text       = 'Fanfares',
        shared         = False,
        cosmetic       = True,
        default        = 'normal',
        choices        = {
            'normal':               'Normal',
            'off':                  'No Fanfares',
            'random':               'Random',
            'random_custom_only':   'Random (Custom Only)',
        },
        disable        = {
            'normal': {'settings': ['ocarina_fanfares']},
        },
        gui_tooltip    = '''\
            'No Fanfares': No fanfares (short non-looping tracks) are played.

            'Random': Fanfares are randomized.
            Additional fanfares can be loaded from data/Music/
        ''',
        gui_params  = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random', 1),
            ]
        },
    )

    ocarina_fanfares = Checkbutton(
        gui_text       = 'Ocarina Songs as Fanfares',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Include the songs that play when an ocarina song
            is played as part of the fanfare pool when
            shuffling or disabling fanfares. Note that these
            are a bit longer than most fanfares.
        ''',
        gui_params  = {
            "hide_when_disabled": True,
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                (True, 1),
            ],
        },
        default        = False,
    )

    custom_music_directorypicker = Directoryinput(
        gui_text   = "Custom Music",
        shared     = False,
        cosmetic   = True,
        gui_tooltip = '''\
            Upload custom music files in OoTR's dedicated .ootrs format.
            You can upload individual files or directories consisting of multiple
            custom sequences. Implementation into the seed is controlled by
            the background_music setting.
            Note: Multiple directories at once can only be uploaded by dragging them
            onto the text field.
        ''',
        gui_params = {
            "file_types": [
                {
                  "name": "OoTR Sequence Files",
                  "extensions": ["ootrs"]
                }
            ],
            "hide_when_disabled": True,
        },
    )

    credits_music = Checkbutton(
        gui_text       = 'Credits music as BGM',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Include the songs that play when the credits
            roll as part of the music pool when
            shuffling music.
        ''',
        gui_params  = {
            "hide_when_disabled": False,
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                (True, 1),
            ],
        },
        default        = False,
    )

    sfx_ocarina = Combobox(
        gui_text       = 'Ocarina',
        shared         = False,
        cosmetic       = True,
        choices        = {
            'ocarina':       'Default',
            'random-choice': 'Random Choice',
            'flute':         'Flute',
            'harp':          'Harp',
            'whistle':       'Whistle',
            'malon':         'Malon',
            'grind-organ':   'Grind Organ',
        },
        default        = 'ocarina',
        gui_tooltip    = '''\
            Change the instrument used when playing the ocarina.
        ''',
        gui_params     = {
            'no_line_break' : True,
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-choice', 1),
            ]
        }
    )

    sfx_bombchu_move = Combobox(
        gui_text       = 'Bombchu',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.BOMBCHU_MOVE),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound bombchus make when moving.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution':  [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_hover_boots = Combobox(
        gui_text       = "Hover Boots",
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.BOOTS_HOVER),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of the hover boots when in air.
        ''',
        gui_params     = {
        'no_line_break' : True,
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_iron_boots = Combobox(
        gui_text       = "Iron Boots",
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.BOOTS_IRON),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of Iron boots.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_boomerang_throw = Combobox(
        gui_text       = 'Boomerang Throw',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.BOOMERANG_THROW),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of the Boomerang flying in the air.
        ''',
        gui_params     = {
            "no_line_break"      : True,
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_hookshot_chain = Combobox(
        gui_text       = 'Hookshot Chain',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.HOOKSHOT_CHAIN),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of the Hookshot extending.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_arrow_shot = Combobox(
        gui_text       = 'Arrow Shot',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.ARROW_SHOT),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of a regular arrow shot.
        ''',
        gui_params     = {
            "no_line_break"      : True,
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_slingshot_shot = Combobox(
        gui_text       = 'Slingshot Shot',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.SLINGSHOT_SHOT),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of a Slingshot shot.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_magic_arrow_shot = Combobox(
        gui_text       = 'Magic Arrow Shot',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.MAGIC_ARROW_SHOT),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of a Magic arrow shot.
        ''',
        gui_params     = {
            "no_line_break"      : True,
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_explosion = Combobox(
        gui_text       = 'Bomb Explosion',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.EXPLOSION),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of a bomb exploding.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ],
        },
    )

    sfx_link_adult = Combobox(
        gui_text       = 'Adult Voice',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_voice_sfx_choices(1),
        default        = 'Default',
        gui_tooltip    = '''\
            Change Link's adult voice.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
            "dynamic": True,
        },
    )

    sfx_link_child = Combobox(
        gui_text       = 'Child Voice',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_voice_sfx_choices(0),
        default        = 'Default',
        gui_tooltip    = '''\
            Change Link's child voice.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
            "dynamic": True,
        },
    )

    sfx_navi_overworld = Combobox(
        gui_text       = 'Navi Overworld',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.NAVI_OVERWORLD),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of Navi calling in the overworld.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_navi_enemy = Combobox(
        gui_text       = 'Navi Enemy',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.NAVI_ENEMY),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of Navi targetting an enemy.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_horse_neigh = Combobox(
        gui_text       = 'Horse',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.HORSE_NEIGH),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of Epona and other horses.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_cucco = Combobox(
        gui_text       = 'Cucco',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.CUCCO),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound of Cuccos.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_daybreak = Combobox(
        gui_text       = 'Daybreak',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.DAYBREAK),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound when morning comes.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_nightfall = Combobox(
        gui_text       = 'Nightfall',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.NIGHTFALL),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound when night falls.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_menu_cursor = Combobox(
        gui_text       = 'Menu Cursor',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.MENU_CURSOR),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound when the cursor move in the main menu.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_menu_select = Combobox(
        gui_text       = 'Menu Select',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.MENU_SELECT),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound when pressing A in the main menu.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_low_hp = Combobox(
        gui_text       = 'Low HP',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.HP_LOW),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound when being low on HP.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    slowdown_music_when_lowhp = Checkbutton(
        gui_text       = 'Slow Down Music When Low HP',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            The music will slow down slightly when being low on HP.
            Does not apply on the standard battle enemy music.
        ''',
        default        = False,
    )

    sfx_silver_rupee = Combobox(
        gui_text       = 'Silver Rupee Jingle',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.SILVER_RUPEE),
        default        = 'default',
        gui_tooltip    = '''\
            Change the jingle when getting a silver rupee.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    sfx_get_small_item = Combobox(
        gui_text       = 'Get Refill',
        shared         = False,
        cosmetic       = True,
        choices        = Sounds.get_setting_choices(Sounds.SoundHooks.GET_SMALL_ITEM),
        default        = 'default',
        gui_tooltip    = '''\
            Change the sound when you get a small refill (ammo or recovery heart).
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    )

    setting_infos: dict[str, SettingInfo] = {}
    setting_map: dict = {}

    def __init__(self) -> None:
        self.settings_dict: dict[str, Any] = {}


def get_settings_from_section(section_name: str) -> Iterable[str]:
    for tab in SettingInfos.setting_map['Tabs']:
        for section in tab['sections']:
            if section['name'] == section_name:
                for setting in section['settings']:
                    yield setting
                return


def get_settings_from_tab(tab_name: str) -> Iterable[str]:
    for tab in SettingInfos.setting_map['Tabs']:
        if tab['name'] == tab_name:
            for section in tab['sections']:
                for setting in section['settings']:
                    yield setting
            return


def is_mapped(setting_name: str) -> bool:
    for tab in SettingInfos.setting_map['Tabs']:
        for section in tab['sections']:
            if setting_name in section['settings']:
                return True
    return False


# When a string isn't found in the source list, attempt to get the closest match from the list
# ex. Given "Recovery Hart" returns "Did you mean 'Recovery Heart'?"
def build_close_match(name: str, value_type: str, source_list: Optional[list[str] | dict[str, list[Entrance]]] = None) -> str:
    source = []
    if value_type == 'item':
        source = ItemInfo.items.keys()
    elif value_type == 'location':
        source = location_table.keys()
    elif value_type == 'entrance':
        for pool in source_list.values():
            for entrance in pool:
                source.append(entrance.name)
    elif value_type == 'stone':
        source = [x.name for x in gossipLocations.values()]
    elif value_type == 'setting':
        source = SettingInfos.setting_infos.keys()
    elif value_type == 'choice':
        source = source_list
    # Ensure name and source are type string to prevent errors
    close_match = difflib.get_close_matches(str(name), map(str, source), 1)
    if len(close_match) > 0:
        return "Did you mean %r?" % (close_match[0])
    return ""  # No matches


def validate_settings(settings_dict: dict[str, Any], *, check_conflicts: bool = True) -> None:
    for setting, choice in settings_dict.items():
        # Ensure the supplied setting name is a real setting
        if setting not in SettingInfos.setting_infos:
            raise TypeError('%r is not a valid setting. %s' % (setting, build_close_match(setting, 'setting')))
        info = SettingInfos.setting_infos[setting]
        # Ensure the type of the supplied choice is correct
        if type(choice) != info.type:
            raise TypeError('Supplied choice %r for setting %r is of type %r, expecting %r' % (choice, setting, type(choice).__name__, info.type.__name__))
        # If setting is a list, must check each element
        if isinstance(choice, list):
            if not info.choice_list:
                continue
            for element in choice:
                if element not in info.choice_list:
                    raise ValueError('%r is not a valid choice for setting %r. %s' % (element, setting, build_close_match(element, 'choice', info.choice_list)))
        # Ignore dictionary settings such as hint_dist_user
        elif isinstance(choice, dict):
            continue
        # Ensure that the given choice is a valid choice for the setting
        elif info.choice_list and choice not in info.choice_list:
            raise ValueError('%r is not a valid choice for setting %r. %s' % (choice, setting, build_close_match(choice, 'choice', info.choice_list)))
        # Ensure no conflicting settings are specified
        if check_conflicts and info.disable is not None:
            for option, disabling in info.disable.items():
                negative = False
                if isinstance(option, str) and option[0] == '!':
                    negative = True
                    option = option[1:]
                if (choice == option) != negative:
                    for other_setting in disabling.get('settings', []):
                        validate_disabled_setting(settings_dict, setting, choice, other_setting)
                    for section in disabling.get('sections', []):
                        for other_setting in get_settings_from_section(section):
                            validate_disabled_setting(settings_dict, setting, choice, other_setting)
                    for tab in disabling.get('tabs', []):
                        for other_setting in get_settings_from_tab(tab):
                            validate_disabled_setting(settings_dict, setting, choice, other_setting)


def validate_disabled_setting(settings_dict: dict[str, Any], setting: str, choice, other_setting: str) -> None:
    if other_setting in settings_dict:
        if settings_dict[other_setting] != SettingInfos.setting_infos[other_setting].disabled_default:
            raise ValueError(f'The {other_setting!r} setting cannot be used since {setting!r} is set to {choice!r}')


class UnmappedSettingError(Exception):
    pass


SettingInfos.setting_infos = {n: s for n, s in SettingInfos.__dict__.items() if isinstance(s, SettingInfo)}
with open(data_path('settings_mapping.json')) as f:
    SettingInfos.setting_map = json.load(f)

for info in SettingInfos.setting_infos.values():
    if info.gui_text is not None and not info.gui_params.get('optional') and not is_mapped(info.name):
        raise UnmappedSettingError(f'{info.name} is defined but is not in the settings map. Add it to the settings_mapping or set the gui_text to None to suppress.')

    if info.disable is not None:
        for option, disabling in info.disable.items():
            negative = False
            if isinstance(option, str) and option[0] == '!':
                negative = True
                option = option[1:]
            for setting_name in disabling.get('settings', []):
                SettingInfos.setting_infos[setting_name].create_dependency(info, option, negative)
            for section in disabling.get('sections', []):
                for setting_name in get_settings_from_section(section):
                    SettingInfos.setting_infos[setting_name].create_dependency(info, option, negative)
            for tab in disabling.get('tabs', []):
                for setting_name in get_settings_from_tab(tab):
                    SettingInfos.setting_infos[setting_name].create_dependency(info, option, negative)
