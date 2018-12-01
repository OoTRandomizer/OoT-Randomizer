import argparse
import re
import math
from Patches import get_tunic_color_options, get_navi_color_options, get_NaviSFX_options, get_HealthSFX_options
from LocationList import location_table

# holds the info for a single setting
class Setting_Info():

    def __init__(self, name, type, bitwidth=0, shared=False, args_params={}, gui_params=None):
        self.name = name # name of the setting, used as a key to retrieve the setting's value everywhere
        self.type = type # type of the setting's value, used to properly convert types in GUI code
        self.bitwidth = bitwidth # number of bits needed to store the setting, used in converting settings to a string
        self.shared = shared # whether or not the setting is one that should be shared, used in converting settings to a string
        self.args_params = args_params # parameters that should be pased to the command line argument parser's add_argument() function
        self.gui_params = gui_params # parameters that the gui uses to build the widget components

        # create the choices parameters from the gui options if applicable
        if gui_params and 'options' in gui_params and 'choices' not in args_params \
                and not ('type' in args_params and callable(args_params['type'])):
            if isinstance(gui_params['options'], list):
                self.args_params['choices'] = list(gui_params['options'])
            elif isinstance(gui_params['options'], dict):
                self.args_params['choices'] = list(gui_params['options'].values())


class Setting_Widget(Setting_Info):

    def __init__(self, name, type, choices, default, args_params={},
            gui_params=None, shared=False):

        assert 'default' not in args_params and 'default' not in gui_params, \
                'Setting {}: default shouldn\'t be defined in '\
                'args_params or in gui_params'.format(name)
        assert 'choices' not in args_params, \
                'Setting {}: choices shouldn\'t be defined in '\
                'args_params'.format(name)
        assert 'options' not in gui_params, \
                'Setting {}: options shouldn\'t be defined in '\
                'gui_params'.format(name)

        if 'type' not in args_params: args_params['type'] = type
        if 'type' not in gui_params:  gui_params['type']  = type

        args_params['choices'] = list(choices.keys())
        args_params['default'] = default
        gui_params['options']  = {v: k for k, v in choices.items()}
        gui_params['default']  = choices[default]

        super().__init__(name, type, self.calc_bitwidth(choices), shared, args_params, gui_params)


    def calc_bitwidth(self, choices):
        count = len(choices)
        if count > 0:
            return math.ceil(math.log(count, 2))
        return 0


class Checkbutton(Setting_Widget):

    def __init__(self, name, args_help, gui_text, gui_group=None,
            gui_tooltip=None, gui_dependency=None, default=False,
            shared=False):

        choices = {
                True:  'checked',
                False: 'unchecked',
                }
        gui_params = {
                'text':    gui_text,
                'widget': 'Checkbutton',
                }
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip
        if gui_dependency is not None: gui_params['dependency'] = gui_dependency
        args_params = {
                'help':    args_help,
                }

        super().__init__(name, bool, choices, default, args_params, gui_params,
                shared)
        self.args_params['type'] = Checkbutton.parse_bool


    def parse_bool(s):
      if s.lower() in ['yes', 'true', 't', 'y', '1']:
          return True
      elif s.lower() in ['no', 'false', 'f', 'n', '0']:
          return False
      else:
          raise argparse.ArgumentTypeError('Boolean value expected.')


class Combobox(Setting_Widget):

    def __init__(self, name, choices, default, args_help, gui_text=None,
            gui_group=None, gui_tooltip=None, gui_dependency=None,
            shared=False):

        type = str
        gui_params = {
                'widget': 'Combobox',
                }
        if gui_text       is not None: gui_params['text']       = gui_text
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip
        if gui_dependency is not None: gui_params['dependency'] = gui_dependency
        args_params = {
                'help':    args_help,
                }

        super().__init__(name, type, choices, default, args_params, gui_params,
                shared)


class Scale(Setting_Widget):

    def __init__(self, name, min, max, default, args_help, step=1,
            gui_text=None, gui_group=None, gui_tooltip=None,
            gui_dependency=None, shared=False):

        type = int
        choices = {}
        for i in range(min, max+1, step):
            choices = {**choices, str(i): i}
        gui_params = {
                'min':     min,
                'max':     max,
                'step':    step,
                'widget': 'Scale',
                }
        if gui_text       is not None: gui_params['text']       = gui_text
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip
        if gui_dependency is not None: gui_params['dependency'] = gui_dependency
        args_params = {
                'help':    args_help,
                }

        super().__init__(name, type, choices, default, args_params, gui_params,
                shared)


def parse_custom_tunic_color(s):
    return parse_color(s, get_tunic_color_options())

def parse_custom_navi_color(s):
    return parse_color(s, get_navi_color_options())

def parse_color(s, color_choices):
    if s == 'Custom Color':
        raise argparse.ArgumentTypeError('Specify custom color by using \'Custom (#xxxxxx)\'')
    elif re.match(r'^Custom \(#[A-Fa-f0-9]{6}\)$', s):
        return re.findall(r'[A-Fa-f0-9]{6}', s)[0]
    elif s in color_choices:
        return s
    else:
        raise argparse.ArgumentTypeError('Invalid color specified')


# a list of the possible settings
setting_infos = [
    Setting_Info('check_version', bool, 0, False,
    {
        'help': '''\
                Checks if you are on the latest version
                ''',
        'action': 'store_true'
    }),
    Setting_Info('checked_version', str, 0, False, {
            'default': '',
            'help': 'Supress version warnings if checked_version is less than __version__.'}),
    Setting_Info('rom', str, 0, False, {
            'default': '',
            'help': 'Path to an OoT 1.0 rom to use as a base.'}),
    Setting_Info('output_dir', str, 0, False, {
            'default': '',
            'help': 'Path to output directory for rom generation.'}),
    Setting_Info('seed', str, 0, False, {
            'help': 'Define seed number to generate.'}),
    Setting_Info('patch_file', str, 0, False, {
            'default': '',
            'help': 'Path to a patch file.'}),
    Setting_Info('count', int, 0, False, {
            'help': '''\
                    Use to batch generate multiple seeds with same settings.
                    If --seed is provided, it will be used for the first seed, then
                    used to derive the next seed (i.e. generating 10 seeds with
                    --seed given will produce the same 10 (different) roms each
                    time).
                    ''',
            'type': int}),
    Setting_Info('world_count', int, 5, True, {
            'default': 1,
            'help': '''\
                    Use to create a multi-world generation for co-op seeds.
                    World count is the number of players. Warning: Increasing
                    the world count will drastically increase generation time.
                    ''',
            'type': int}, {}),
    Setting_Info('player_num', int, 0, False, 
        {
            'default': 1,
            'help': '''\
                    Use to select world to generate when there are multiple worlds.
                    ''',
            'type': int
        },
        {
            'dependency': lambda state: state['compress_rom'] not in ['No Output', 'Patch File'],
        }),
    Checkbutton(
            name           = 'create_spoiler',
            args_help      = '''\
                             Output a Spoiler File
                             ''',
            gui_text       = 'Create Spoiler Log',
            gui_group      = 'rom_tab',
            gui_tooltip    = '''\
                             Enabling this will change the seed.
                             ''',
            default        = True,
            shared         = True,
            ),
    Setting_Widget(
        name='compress_rom',
        type=str,
        default='True',
        choices={
            'True': 'Compressed [Stable]',
            'False': 'Uncompressed [Crashes]',
            'Patch': 'Patch File',
            'None': 'No Output',
        },
        args_params={
            'help': '''\
                    Create a compressed version of the output ROM file.
                    True: Compresses. Improves stability. Will take longer to generate
                    False: Uncompressed. Unstable. Faster generation
                    Patch: Patch file. No ROM, but used to send the patch data
                    None: No ROM Output. Creates spoiler log only
                    ''',
        },
        gui_params={
            'text': 'Output Type',
            'group': 'rom_tab',
            'widget': 'Radiobutton',
            'horizontal': True,
            'tooltip':'''\
                      The first time compressed generation will take a while,
                      but subsequent generations will be quick. It is highly
                      recommended to compress or the game will crash
                      frequently except on real N64 hardware.

                      Patch files are used to send the patched data to other
                      people without sending the ROM file.
                      '''
        },
        shared=False,
    ),
    Checkbutton(
            name           = 'open_forest',
            args_help      = '''\
                             Mido no longer blocks the path to the Deku Tree, and
                             the Kokiri boy no longer blocks the path out of the forest.
                             ''',
            gui_text       = 'Open Forest',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             Mido no longer blocks the path to the Deku Tree,
                             and the Kokiri boy no longer blocks the path out
                             of the forest.

                             When this option is off, the Kokiri Sword and
                             Slingshot are always available somewhere
                             in the forest.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'open_kakariko',
            args_help      = '''\
                             The gate in Kakariko Village to Death Mountain Trail
                             is always open instead of needing Zelda's Letter.
                             ''',
            gui_text       = 'Open Kakariko Gate',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             The gate in Kakariko Village to Death Mountain Trail
                             is always open instead of needing Zelda's Letter.

                             Either way, the gate is always open as an adult.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'open_door_of_time',
            args_help      = '''\
                             The Door of Time is open from the beginning of the game.
                             ''',
            gui_text       = 'Open Door of Time',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             The Door of Time starts opened instead of needing to
                             play the Song of Time. If this is not set, only
                             an Ocarina and Song of Time must be found to open
                             the Door of Time.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'gerudo_fortress',
            default        = 'normal',
            choices        = {
                'normal': 'Default Behavior',
                'fast':   'Rescue One Carpenter',
                'open':   'Start with Gerudo Card',
                },
            args_help      = '''\
                             Select how much of Gerudo Fortress is required. (default: %(default)s)
                             Normal: Free all four carpenters to get the Gerudo Card.
                             Fast:   Free only the carpenter closest to Link's prison to get the Gerudo Card.
                             Open:   Start with the Gerudo Card and all its benefits.
                             ''',
            gui_text       = 'Gerudo Fortress',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             'Rescue One Carpenter': Only the bottom left
                             carpenter must be rescued.
                             
                             'Start with Gerudo Card': The carpenters are rescued from
                             the start of the game, and the player starts with the Gerudo
                             Card in the inventory allowing access to Gerudo Training Grounds.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'bridge',
            default        = 'medallions',
            choices        = {
                'dungeons':   'All Dungeons',
                'medallions': 'All Medallions',
                'vanilla':    'Vanilla Requirements',
                'open':       'Always Open',
                },
            args_help      = '''\
                             Select requirement to spawn the Rainbow Bridge to reach Ganon's Castle. (default: %(default)s)
                             Medallions:    Collect all six medallions to create the bridge.
                             Vanilla:       Collect only the Shadow and Spirit Medallions and possess the Light Arrows.
                             All Dungeons:  Collect all spiritual stones and all medallions to create the bridge.
                             Open:          The bridge will spawn without an item requirement.
                             ''',
            gui_text       = 'Rainbow Bridge Requirement',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             'All Dungeons': All Medallions and Stones
        
                             'All Medallions': All 6 Medallions only
        
                             'Vanilla Requirements': Spirit and Shadow
                             Medallions and the Light Arrows
        
                             'Always Open': Rainbow Bridge is always present
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'logic_rules',
            default        = 'glitchless',
            choices        = {
                'glitchless': 'Glitchless',
                'none':       'No Logic',
                },
            args_help      = '''\
                             Sets the rules the logic uses to determine accessibility:
                             glitchless:  No glitches are required, but may require some minor tricks
                             none:        All locations are considered available. May not be beatable.
                             ''',
            gui_text       = 'Logic Rules',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Sets the rules the logic uses
                             to determine accessibility.
        
                             'Glitchless': No glitches are
                             required, but may require some
                             minor tricks
        
                             'No Logic': All locations are
                             considered available. May not
                             be beatable.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'all_reachable',
            args_help      = '''\
                             When disabled, only check if the game is beatable with
                             placement. Do not ensure all locations are reachable.
                             ''',
            gui_text       = 'All Locations Reachable',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             When this option is enabled, the randomizer will
                             guarantee that every item is obtainable and every
                             location is reachable.
        
                             When disabled, only required items and locations
                             to beat the game will be guaranteed reachable.
        
                             Even when enabled, some locations may still be able
                             to hold the keys needed to reach them.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'bombchus_in_logic',
            args_help      = '''\
                             Bombchus will be considered in logic. This has a few effects:
                             -Back Alley shop will open once you've found Bombchus.
                             -It will sell an affordable pack (5 for 60) and never sell out.
                             -Bombchus refills cannot be bought until Bombchus have been obtained.
                             ''',
            gui_text       = 'Bombchus Are Considered in Logic',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Bombchus are properly considered in logic.
        
                             The first Bombchu pack will always be 20.
                             Subsequent packs will be 5 or 10 based on
                             how many you have.
        
                             Bombchus can be purchased for 60/99/180
                             rupees once they have been found.
        
                             Bombchu Bowling opens with Bombchus.
                             Bombchus are available at Kokiri Shop
                             and the Bazaar. Bombchu refills cannot
                             be bought until Bombchus have been
                             obtained.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'one_item_per_dungeon',
            args_help      = '''\
                             Each dungeon will have exactly one major item.
                             Does not include dungeon items or GS Tokens.
                             ''',
            gui_text       = 'Dungeons Have One Major Item',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Dungeons have exactly one major
                             item. This naturally makes each
                             dungeon similar in value instead
                             of valued based on chest count.
        
                             Spirit Temple Colossus hands count
                             as part of the dungeon. Spirit
                             Temple has TWO items to match
                             vanilla distribution.
        
                             Dungeon items and GS Tokens do
                             not count as major items.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'trials_random',
            args_help      = '''\
                             Sets the number of trials must be cleared to enter
                             Ganon's Tower to a random value.
                             ''',
            gui_text       = 'Random Number of Ganon\'s Trials',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             Sets a random number of trials to
                             enter Ganon's Tower.
                             ''',
            shared         = True,
            ),
    Scale(
            name           = 'trials',
            default        = '6',
            min            = 0,
            max            = 6,
            args_help      = '''\
                             Select how many trials must be cleared to enter Ganon's Tower.
                             The trials you must complete will be selected randomly.
                             ''',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             Trials are randomly selected. If hints are
                             enabled, then there will be hints for which
                             trials need to be completed.
                             ''',
            gui_dependency = lambda state: not state['trials_random'],
            shared         = True,
            ),
    Checkbutton(
            name           = 'no_escape_sequence',
            args_help      = '''\
                             The tower collapse escape sequence between Ganondorf and Ganon will be skipped.
                             ''',
            gui_text       = 'Skip Tower Collapse Escape Sequence',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             The tower collapse escape sequence between
                             Ganondorf and Ganon will be skipped.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'no_guard_stealth',
            args_help      = '''\
                             The crawlspace into Hyrule Castle will take you straight to Zelda.
                             ''',
            gui_text       = 'Skip Interior Castle Guard Stealth Sequence',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             The crawlspace into Hyrule Castle goes
                             straight to Zelda, skipping the guards.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'no_epona_race',
            args_help      = '''\
                             Having Epona's Song will allow you to summon Epona without racing Ingo.
                             ''',
            gui_text       = 'Skip Epona Race',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Epona can be summoned with Epona's Song
                             without needing to race Ingo.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'fast_chests',
            args_help      = '''\
                             Makes all chests open without the large chest opening cutscene.
                             ''',
            gui_text       = 'Fast Chest Cutscenes',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             All chest animations are fast. If disabled,
                             the animation time is slow for major items.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'big_poe_count_random',
            args_help      = '''\
                             Sets a random number of Big Poes to receive an item from the buyer.
                             ''',
            gui_text       = 'Random Big Poe Target Count',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             The Poe buyer will give a reward for turning
                             in a random number of Big Poes.
                             ''',
            shared         = True,
            ),
    Scale(
            name           = 'big_poe_count',
            default        = '10',
            min            = 1,
            max            = 10,
            args_help      = '''\
                             Select the number of Big Poes to receive an item from the buyer.
                             ''',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             The Poe buyer will give a reward for turning
                             in the chosen number of Big Poes.
                             ''',
            gui_dependency = lambda state: not state['big_poe_count_random'],
            shared         = True,
            ),
    Checkbutton(
            name           = 'free_scarecrow',
            args_help      = '''\
                             Scarecrow song is not needed to summon Pierre.
                             ''',
            gui_text       = 'Free Scarecrow\'s Song',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Pulling out the Ocarina near
                             Pierre will summon him without
                             learning the song.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_kokiri_sword',
            args_help      = '''\
                             Shuffles the Kokiri Sword into the pool.
                             ''',
            gui_text       = 'Shuffle Kokiri Sword',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             Disabling this will make the Kokiri Sword
                             always available at the start.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_weird_egg',
            args_help      = '''\
                             Shuffles the Weird Egg item from Malon into the pool.
                             This means that you need to find the egg before going Zelda.
                             ''',
            gui_text       = 'Shuffle Weird Egg',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             You need to find the egg before going Zelda.
                             This means the Weird Egg locks the rewards from
                             Impa, Saria, Malon, and Talon as well as the
                             Happy Mask sidequest.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_ocarinas',
            args_help      = '''\
                             Shuffles the Fairy Ocarina and the Ocarina of Time into the pool.
                             This means that you need to find an ocarina before playing songs.
                             ''',
            gui_text       = 'Shuffle Ocarinas',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             The Fairy Ocarina and Ocarina of Time are
                             randomized. One will be required before
                             songs can be played.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_song_items',
            args_help      = '''\
                             Shuffles the songs with with rest of the item pool so that
                             songs can appear at other locations and items can appear at
                             the song locations.
                             ''',
            gui_text       = 'Shuffle Songs with Items',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             Songs can appear anywhere as normal items.
        
                             If this option is not set, songs will still
                             be shuffled but will be limited to the
                             locations that has songs in the original game.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_gerudo_card',
            args_help      = '''\
                             Shuffles the Gerudo Card into the item pool.
                             The Gerudo Card does not stop guards from throwing you in jail.
                             It only grants access to Gerudo Training Grounds after all carpenters
                             have been rescued. This option does nothing if "gerudo_fortress" is "open".
                             ''',
            gui_text       = 'Shuffle Gerudo Card',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             Gerudo Card is required to enter
                             Gerudo Training Grounds.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'shuffle_scrubs',
            default        = 'off',
            choices        = {
                'off':     'Off',
                'low':     'On (Affordable)',
                'regular': 'On (Expensive)',
                'random':  'On (Random Prices)',
                },
            args_help      = '''\
                             Deku Scrub Salesmen are randomized:
                             off:        Only the 3 Scrubs that give one-time items
                                         in the vanilla game will have random items.
                             low:        All Scrubs will have random items and their
                                         prices will be reduced to 10 rupees each.
                             regular:    All Scrubs will have random items and each
                                         of them will demand their vanilla prices.
                             random:     All Scrubs will have random items and their
                                         price will also be random between 10-99 rupees.
                             ''',
            gui_text       = 'Scrub Shuffle',
            gui_group      = 'logic',
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
        
                             The texts of the Scrubs are not updated.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'shopsanity',
            default        = 'off',
            choices        = {
                'off':    'Off',
                '0':      'Shuffled Shops (0 Items)',
                '1':      'Shuffled Shops (1 Items)',
                '2':      'Shuffled Shops (2 Items)',
                '3':      'Shuffled Shops (3 Items)',
                '4':      'Shuffled Shops (4 Items)',
                'random': 'Shuffled Shops (Random)',
                },
            args_help      = '''\
                             Shop contents are randomized. Non-shop items
                             are one time purchases. This setting also
                             changes the item pool to introduce a new Wallet
                             upgrade and more money.
                             off:        Normal Shops*
                             0-4:        Shop contents are shuffled and N non-shop
                                         items are added to every shop. So more
                                         possible item locations.
                             random:     Shop contents are shuffles and each shop
                                         will have a random number of non-shop items
                             ''',
            gui_text       = 'Shopsanity',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             Shop contents are randomized.
                             (X Items): Shops have X random non-shop (Special
                             Deal!) items. They will always be on the left
                             side, and some of the lower value shop items
                             will be replaced to make room for these.
        
                             (Random): Each shop will have a random number
                             of non-shop items up to a maximum of 4.
        
                             The non-shop items have no requirements except
                             money, while the normal shop items (such as
                             200/300 rupee tunics) have normal vanilla
                             requirements. This means that, for example,
                             as a child you cannot buy 200/300 rupee
                             tunics, but you can buy non-shop tunics.
        
                             Non-shop Bombchus will unlock the chu slot
                             in your inventory, which, if Bombchus are in
                             logic, is needed to buy Bombchu refills.
                             Otherwise, the Bomb Bag is required.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'shuffle_mapcompass',
            default        = 'dungeon',
            choices        = {
                'remove':    'Maps/Compasses: Remove',
                'startwith': 'Maps/Compasses: Start With',
                'dungeon':   'Maps/Compasses: Dungeon Only',
                'keysanity': 'Maps/Compasses: Anywhere'
                },
            args_help      = '''\
                             Sets the Map and Compass placement rules
                             remove:      Maps and Compasses are removed from the world.
                             startwith:   Start with all Maps and Compasses.
                             dungeon:     Maps and Compasses are put in their dungeon.
                             keysanity:   Maps and Compasses can appear anywhere.
                             ''',
            gui_text       = 'Shuffle Dungeon Items',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             'Remove': Maps and Compasses are removed.
                             This will add a small amount of money and
                             refill items to the pool.
        
                             'Start With': Maps and Compasses are given to
                             you from the start. This will add a small
                             amount of money and refill items to the pool.
        
                             'Dungeon': Maps and Compasses can only appear
                             in their respective dungeon.
        
                             'Anywhere': Maps and Compasses can appear
                             anywhere in the world.
        
                             Setting 'Remove', 'Start With, or 'Anywhere' will
                             add 2 more possible locations to each Dungeons.
                             This makes dungeons more profitable, especially
                             Ice Cavern, Water Temple, and Jabu Jabu's Belly.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'shuffle_smallkeys',
            default        = 'dungeon',
            choices        = {
                'remove':    'Small Keys: Remove (Keysy)',
                'dungeon':   'Small Keys: Dungeon Only',
                'keysanity': 'Small Keys: Anywhere (Keysanity)'
                },
            args_help      = '''\
                             Sets the Small Keys placement rules
                             remove:      Small Keys are removed from the world.
                             dungeon:     Small Keys are put in their dungeon.
                             keysanity:   Small Keys can appear anywhere.
                             ''',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             'Remove': Small Keys are removed. All locked
                             doors in dungeons will be unlocked. An easier
                             mode.
        
                             'Dungeon': Small Keys can only appear in their
                             respective dungeon. If Fire Temple is not a
                             Master Quest dungeon, the door to the Boss Key
                             chest will be unlocked
        
                             'Anywhere': Small Keys can appear
                             anywhere in the world. A difficult mode since
                             it is more likely to need to enter a dungeon
                             multiple times.
        
                             Try different combination out, such as:
                             'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
                             for a milder Keysanity experience.
                             ''',
            ),
    Combobox(
            name           = 'shuffle_bosskeys',
            default        = 'dungeon',
            choices        = {
                'remove':    'Boss Keys: Remove (Keysy)',
                'dungeon':   'Boss Keys: Dungeon Only',
                'keysanity': 'Boss Keys: Anywhere (Keysanity)',
                },
            args_help      = '''\
                             Sets the Boss Keys placement rules
                             remove:      Boss Keys are removed from the world.
                             dungeon:     Boss Keys are put in their dungeon.
                             keysanity:   Boss Keys can appear anywhere.
                             ''',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             'Remove': Boss Keys are removed. All locked
                             doors in dungeons will be unlocked. An easier
                             mode.
        
                             'Dungeon': Boss Keys can only appear in their
                             respective dungeon.
        
                             'Anywhere': Boss Keys can appear
                             anywhere in the world. A difficult mode since
                             it is more likely to need to enter a dungeon
                             multiple times.
        
                             Try different combination out, such as:
                             'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
                             for a milder Keysanity experience.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'enhance_map_compass',
            args_help      = '''\
                             Gives the Map and Compass extra functionality.
                             Map will tell if a dungeon is vanilla or Master Quest.
                             Compass will tell what medallion or stone is within.
                             The Temple of Time Altar will no longer provide any
                             information. If the maps and compasses are removed then
                             the information will be unavailable.
                             ''',
            gui_text       = 'Maps and Compasses Give Information',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                           Gives the Map and Compass extra functionality.
                           Map will tell if a dungeon is vanilla or Master Quest.
                           Compass will tell what medallion or stone is within.
                           The Temple of Time Altar will no longer provide any
                           information.
        
                           'Maps/Compasses: Remove': The dungeon information is
                           not available anywhere in the game.
        
                           'Maps/Compasses: Start With': The dungeon information
                           is available immediately from the dungeon menu.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'unlocked_ganondorf',
            args_help      = '''\
                             The Boss Key door in Ganon's Tower will start unlocked.
                             ''',
            gui_text       = 'Remove Ganon\'s Boss Door Lock',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             The Boss Key door in Ganon's Tower
                             will start unlocked. This is intended
                             to be used with reduced trial
                             requirements to make it more likely
                             that skipped trials can be avoided.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'tokensanity',
            default        = 'off',
            choices        = {
                'off':      'Off',
                'dungeons': 'Dungeons Only',
                'all':      'All Tokens',
                },
            args_help      = '''\
                             Gold Skulltula Tokens will be shuffled into the pool,
                             and Gold Skulltula locations can have any item.
                             off:        Don't use this feature
                             dungeons:   Only dungeon Skulltulas will be shuffled
                             all:        All Gold Skulltulas will be shuffled
                             ''',
            gui_text       = 'Tokensanity',
            gui_group      = 'logic',
            gui_tooltip    = '''\
                             Token reward from Gold Skulltulas are
                             shuffled into the pool.
        
                             'Dungeons Only': This only shuffles
                             the GS locations that are within
                             dungeons, increasing the value of
                             most dungeons and making internal
                             dungeon exploration more diverse.
        
                             'All Tokens': Effectively adds 100
                             new locations for items to appear.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'mq_dungeons_random',
            args_help      = '''\
                             If set, a uniformly random number of dungeons will have Master Quest designs.
                             ''',
            gui_text       = 'Random Number of MQ Dungeons',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             If set, a random number of dungeons
                             will have Master Quest designs.
                             ''',
            shared         = True,
            ),
    Scale(
            name           = 'mq_dungeons',
            default        = '0',
            min            = 0,
            max            = 12,
            args_help      = '''\
                             Select a number (0-12) of Master Quest dungeons to appear in the game.
                             0:  (default) All dungeon will have their original designs.
                             ...
                             6:  50/50 split; Half of all dungeons will be from Master Quest.
                             ...
                             12: All dungeons will have Master Quest redesigns.
                             ''',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Select a number of Master Quest
                             dungeons to appear in the game.

                             0: All dungeon will have their
                             original designs. (default)

                             6: Half of all dungeons will
                             be from Master Quest.

                             12: All dungeons will have
                             Master Quest redesigns.
                             ''',
            gui_dependency = lambda state: not state['mq_dungeons_random'],
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_no_night_tokens_without_suns_song',
            args_help      = '''\
                             You will not be expected to collect nighttime-only skulltulas
                             unless you have Sun's Song
                             ''',
            gui_text       = 'No Nighttime Skulltulas without Sun\'s Song',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             GS Tokens that can only be obtained
                             during the night expect you to have Sun's
                             Song to collect them. This prevents needing
                             to wait until night for some locations.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'logic_earliest_adult_trade',
            default        = 'pocket_egg',
            choices        = {
                'pocket_egg':   'Earliest: Pocket Egg',
                'pocket_cucco': 'Earliest: Pocket Cucco',
                'cojiro':       'Earliest: Cojiro',
                'odd_mushroom': 'Earliest: Odd Mushroom',
                'poachers_saw': "Earliest: Poacher's Saw",
                'broken_sword': 'Earliest: Broken Sword',
                'prescription': 'Earliest: Prescription',
                'eyeball_frog': 'Earliest: Eyeball Frog',
                'eyedrops':     'Earliest: Eyedrops',
                'claim_check':  'Earliest: Claim Check',
                },
            args_help      = '''\
                             Select the earliest item that can appear in the adult trade sequence:
                             'pocket_egg'
                             'pocket_cucco'
                             'cojiro'
                             'odd_mushroom'
                             'poachers_saw'
                             'broken_sword'
                             'prescription'
                             'eyeball_frog'
                             'eyedrops'
                             'claim_check'
                             ''',
            gui_text       = 'Adult Trade Sequence',
            gui_group      = 'rewards',
            gui_tooltip    = '''\
                             Select the earliest item that can appear in the adult trade sequence.
                             ''',
            shared         = True,
            ),
    Setting_Info('disabled_locations', list, math.ceil(math.log(len(location_table) + 2, 2)), True,
        {
            'default': [],
            'help': '''\
                    Choose a list of locations that will never be required to beat the game.
                    '''
        },
        {
            'options': list(location_table.keys()),
        }),      
    Combobox(
            name           = 'logic_latest_adult_trade',
            default        = 'claim_check',
            choices        = {
                'pocket_egg':   'Latest: Pocket Egg',
                'pocket_cucco': 'Latest: Pocket Cucco',
                'cojiro':       'Latest: Cojiro',
                'odd_mushroom': 'Latest: Odd Mushroom',
                'poachers_saw': "Latest: Poacher's Saw",
                'broken_sword': 'Latest: Broken Sword',
                'prescription': 'Latest: Prescription',
                'eyeball_frog': 'Latest: Eyeball Frog',
                'eyedrops':     'Latest: Eyedrops',
                'claim_check':  'Latest: Claim Check',
                },
            args_help      = '''\
                             Select the latest item that can appear in the adult trade sequence:
                             'pocket_egg'
                             'pocket_cucco'
                             'cojiro'
                             'odd_mushroom'
                             'poachers_saw'
                             'broken_sword'
                             'prescription'
                             'eyeball_frog'
                             'eyedrops'
                             'claim_check'
                             ''',
            gui_group      = 'rewards',
            gui_tooltip    = '''\
                             Select the latest item that can appear in the adult trade sequence.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_tricks',
            args_help      = '''\
                             Enable various advanced tricks that do not require glitches.
                             ''',
            gui_text       = 'Various Advanced Tricks',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Enables a large number of minor
                             tricks that do not require glitches.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_man_on_roof',
            args_help      = '''\
                             The man on the roof will not require the Hookshot in logic.
                             ''',
            gui_text       = 'Man on Roof without Hookshot',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Can be reached by side-hopping off
                             the watchtower.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_child_deadhand',
            args_help      = '''\
                             Deadhand in the Bottom of the Well will not require the Kokiri sword in logic.
                             ''',
            gui_text       = 'Child Deadhand without Kokiri Sword',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Requires 9 sticks or 5 jump slashes.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_dc_jump',
            args_help      = '''\
                             Jumping towards the Bomb Bag chest in Dodongo's Cavern as an adult
                             will not require Hover Boots in logic.
                             ''',
            gui_text       = 'Dodongo\'s Cavern Spike Trap Room Jump without Hover Boots',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Jump is adult only.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_windmill_poh',
            args_help      = '''\
                    Getting the Piece of Heart in the windmill as an adult will require nothing in logic.
                             ''',
            gui_text       = 'Windmill PoH as Adult with Nothing',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Can jump up to the spinning platform from
                             below as adult.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_crater_bean_poh_with_hovers',
            args_help      = '''\
                             The Piece of Heart in Death Mountain Crater that normally requires the bean to
                             reach will optionally require the Hover Boots in logic.
                             ''',
            gui_text       = 'Crater\'s Bean PoH with Hover Boots',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Hover from the base of the bridge
                             near Goron City and walk up the
                             very steep slope.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_zora_with_cucco',
            args_help      = '''\
                             Zora's Domain can be entered with a Cucco as child in logic.
                             ''',
            gui_text       = 'Zora\'s Domain Entry with Cucco',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Can fly behind the waterfall with
                             a cucco as child.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_zora_with_hovers',
            args_help      = '''\
                             Zora's Domain can be entered with Hover Boots as Adult in logic.
                             ''',
            gui_text       = 'Zora\'s Domain Entry with Hover Boots',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Can hover behind the waterfall as adult.
                             This is very difficult.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_fewer_tunic_requirements',
            args_help      = '''\
                             Allows the following possible without Goron or Zora Tunic:
                             Enter Water Temple
                             Enter Fire Temple
                             Zoras Fountain Bottom Freestanding PoH
                             Gerudo Training Grounds Underwater Silver Rupee Chest
                             ''',
            gui_text       = 'Fewer Tunic Requirements',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Allows the following possible without Tunics:
                             - Enter Water Temple. The key below the center
                             pillar still requires Zora Tunic.
                             - Enter Fire Temple. Only the first floor is
                             accessible, and not Volvagia.
                             - Zora's Fountain Bottom Freestanding PoH.
                             Might not have enough health to resurface.
                             - Gerudo Training Grounds Underwater
                             Silver Rupee Chest. May need to make multiple
                             trips.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_morpha_with_scale',
            args_help      = '''\
                             Allows entering Water Temple and beating
                             Morpha with Gold Scale instead of Iron Boots.
                             Only applicable for keysanity and keysy.
                             ''',
            gui_text       = 'Morpha with Gold Scale',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             Allows entering Water Temple and beating
                             Morpha with Gold Scale instead of Iron Boots.
                             Only applicable for keysanity and keysy due
                             to the logic always seeing every chest in
                             Water Temple that could contain the Boss Key
                             as requiring Iron Boots.
                             ''',
            default        = False,
            shared         = True,
            ),
    Combobox(
            name           = 'logic_lens',
            default        = 'all',
            choices        = {
                'all':             'Required Everywhere',
                'chest-wasteland': 'Wasteland and Chest Minigame',
                'chest':           'Only Chest Minigame',
                },
            args_help      = '''\
                             Choose what expects the Lens of Truth:
                             all:              All lens spots expect the lens (except those that did not in the original game)
                             chest-wasteland:  Only wasteland and chest minigame expect the lens
                             chest:            Only the chest minigame expects the lens
                             ''',
            gui_text       = 'Lens of Truth',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             'Required everywhere': every invisible or
                             fake object will expect you to have the
                             Lens of Truth and Magic. The exception is
                             passing through the first wall in Bottom of
                             the Well, since that is required in vanilla.
        
                             'Wasteland': The lens is needed to follow
                             the ghost guide across the Haunted Wasteland.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'ocarina_songs',
            args_help      = '''\
                             Randomizes the notes needed to play each ocarina song.
                             ''',
            gui_text       = 'Randomize Ocarina Song Notes',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Will need to memorize a new set of songs.
                             Can be silly, but difficult. Songs are
                             generally sensible, and warp songs are
                             typically more difficult.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'correct_chest_sizes',
            args_help      = '''\
                             Updates the chest sizes to match their contents.
                             Small Chest = Non-required Item
                             Big Chest = Progression Item
                             ''',
            gui_text       = 'Chest Size Matches Contents',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Chests will be large if they contain a major
                             item and small if they don't. This allows skipping
                             chests if they are small. However, skipping
                             small chests will mean having low health,
                             ammo, and rupees, so doing so is a risk.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'clearer_hints',
            args_help      = '''\
                             The hints provided by Gossip Stones are
                             very direct.
                             ''',
            gui_text       = 'Clearer Hints',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             The hints provided by Gossip Stones will
                             be very direct if this option is enabled.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'hints',
            default        = 'agony',
            choices        = {
                'none':   'No Hints',
                'mask':   'Hints; Need Mask of Truth',
                'agony':  'Hints; Need Stone of Agony',
                'always': 'Hints; Need Nothing',
                },
            args_help      = '''\
                             Choose how Gossip Stones behave
                             none:   Default behavior
                             mask:   Have useful hints that are read with the Mask of Truth.
                             agony:  Have useful hints that are read with Stone of Agony.
                             always: Have useful hints which can always be read.
                             ''',
            gui_text       = 'Gossip Stones',
            gui_group      = 'other',
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
            ),
    Combobox(
            name           = 'hint_dist',
            default        = 'balanced',
            choices        = {
                'useless':     'Useless',
                'balanced':    'Balanced',
                'strong':      'Strong',
                'very_strong': 'Very Strong',
                },
            args_help      = '''\
                             Choose how Gossip Stones hints are distributed
                             useless: Nothing but junk hints.
                             balanced: Use a balanced distribution of hint types
                             strong: Use a strong distribution of hint types
                             very_strong: Use a very strong distribution of hint types
                             ''',
            gui_text       = 'Hint Distribution',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Useless has nothing but junk
                             hints.
                             Strong distribution has some
                             duplicate hints and no junk
                             hints.
                             Very Strong distribution has
                             only very useful hints.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'text_shuffle',
            default        = 'none',
            choices        = {
                'none':         'No Text Shuffled',
                'except_hints': 'Shuffled except Hints and Keys',
                'complete':     'All Text Shuffled',
                },
            args_help      = '''\
                             Choose how to shuffle the game's messages.
                             none:          Default behavior
                             except_hints:  All non-useful text is shuffled.
                             complete:      All text is shuffled.
                             ''',
            gui_text       = 'Text Shuffle',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Will make things confusing for comedic value.
        
                             'Shuffled except Hints and Keys': Key texts
                             are not shuffled because in keysanity it is
                             inconvenient to figure out which keys are which
                             without the correct text. Similarly, non-shop
                             items sold in shops will also retain standard
                             text for the purpose of accurate price checks.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'item_pool_value',
            default        = 'balanced',
            choices        = {
                'plentiful': 'Plentiful',
                'balanced':  'Balanced',
                'scarce':    'Scarce',
                'minimal':   'Minimal'
                },
            args_help      = '''\
                             Change the item pool for an added challenge.
                             plentiful:      Duplicates most of the major items, making it easier to find progression.
                             balanced:       Default items
                             scarce:         Double defense, double magic, and all 8 heart containers are removed. Ammo
                                             for each type can only be expanded once and you can only find three Bombchu packs.
                             minimal:        Double defense, double magic, Nayru's Love, and all health upgrades are removed.
                                             No ammo expansions are available and you can only find one Bombchu pack.
                             ''',
            gui_text       = 'Item Pool Value',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Changes the amount of bonus items that
                             are available in the game.
        
                             'Plentiful': Extra major items are added.
        
                             'Balanced': Original item pool.
        
                             'Scarce': Some excess items are removed,
                             including health upgrades.
        
                             'Minimal': Most excess items are removed.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'damage_multiplier',
            default        = 'normal',
            choices        = {
                'half':      'Half',
                'normal':    'Normal',
                'double':    'Double',
                'quadruple': 'Quadruple',
                'ohko':      'OHKO',
                },
            args_help      = '''\
                             Change the amount of damage taken.
                             half:           Half damage taken.
                             normal:         Normal damage taken.
                             double:         Double damage taken.
                             quadruple:      Quadruple damage taken.
                             ohko:           Link will die in one hit.
                             ''',
            gui_text       = 'Damage Multiplier',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Changes the amount of damage taken.
        
                             'OHKO': Link dies in one hit.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'default_targeting',
            default        = 'hold',
            choices        = {
                'hold':   'Hold',
                'switch': 'Switch',
                },
            args_help      = '''\
                             Choose what the default Z-targeting is.
                             ''',
            gui_text       = 'Default Targeting Option',
            gui_group      = 'cosmetics',
            ),
    Combobox(
            name           = 'background_music',
            default        = 'normal',
            choices        = {
                'normal': 'Normal',
                'off':    'No Music',
                'random': 'Random',
                },
            args_help      = '''\
                             Sets the background music behavior
                             normal:      Areas play their normal background music
                             off:         No background music
                             random:      Areas play random background music
                             ''',
            gui_text       = 'Background Music',
            gui_group      = 'cosmetics',
            gui_tooltip    = '''\
                              'No Music': No background music.
                              is played.
        
                              'Random': Area background music is
                              randomized.
                             ''',
            ),

    Setting_Info('kokiri_color', str, 0, False,
        {
            'default': 'Kokiri Green',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Kokiri Tunic. (default: %(default)s)
                    Color:              Make the Kokiri Tunic this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Kokiri Tunic Color',
            'group': 'tunic_color',
            'widget': 'Combobox',
            'default': 'Kokiri Green',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('goron_color', str, 0, False,
        {
            'default': 'Goron Red',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Goron Tunic. (default: %(default)s)
                    Color:              Make the Goron Tunic this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Goron Tunic Color',
            'group': 'tunic_color',
            'widget': 'Combobox',
            'default': 'Goron Red',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('zora_color', str, 0, False,
        {
            'default': 'Zora Blue',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Zora Tunic. (default: %(default)s)
                    Color:              Make the Zora Tunic this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Zora Tunic Color',
            'group': 'tunic_color',
            'widget': 'Combobox',
            'default': 'Zora Blue',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navi_color_default', str, 0, False,
        {
            'default': 'White',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is idle. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Idle',
            'group': 'navi_color',
            'widget': 'Combobox',
            'default': 'White',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navi_color_enemy', str, 0, False,
        {
            'default': 'Yellow',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is targeting an enemy. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Targeting Enemy',
            'group': 'navi_color',
            'widget': 'Combobox',
            'default': 'Yellow',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navi_color_npc', str, 0, False,
        {
            'default': 'Light Blue',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is targeting an NPC. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Targeting NPC',
            'group': 'navi_color',
            'widget': 'Combobox',
            'default': 'Light Blue',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navi_color_prop', str, 0, False,
        {
            'default': 'Green',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is targeting a prop. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Targeting Prop',
            'group': 'navi_color',
            'widget': 'Combobox',
            'default': 'Green',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navisfxoverworld', str, 0, False,
        {
            'default': 'Default',
            'help': '''\
                    Select the sound effect that plays when Navi has a hint. (default: %(default)s)
                    Sound:         Replace the sound effect with the chosen sound.
                    Random Choice: Replace the sound effect with a random sound from this list.
                    None:          Eliminate Navi hint sounds.
                    '''
        },
        {
            'text': 'Navi Hint',
            'group': 'navihint',
            'widget': 'Combobox',
            'default': 'Default',
            'options': get_NaviSFX_options(),
        }),
        Setting_Info('navisfxenemytarget', str, 0, False,
        {
            'default': 'Default',
            'help': '''\
                    Select the sound effect that plays when targeting an enemy. (default: %(default)s)
                    Sound:         Replace the sound effect with the chosen sound.
                    Random Choice: Replace the sound effect with a random sound from this list.
                    None:          Eliminate Navi hint sounds.
                    '''
        },
        {
            'text': 'Navi Enemy Target',
            'group': 'navihint',
            'widget': 'Combobox',
            'default': 'Default',
            'options': get_NaviSFX_options(),
        }),
    Setting_Info('healthSFX', str, 0, False,
        {
            'default': 'Default',
            'help': '''\
                    Select the sound effect that loops at low health. (default: %(default)s)
                    Sound:         Replace the sound effect with the chosen sound.
                    Random Choice: Replace the sound effect with a random sound from this list.
                    None:          Eliminate heart beeps.
                    '''
        },
        {
            'text': 'Low Health SFX',
            'group': 'lowhp',
            'widget': 'Combobox',
            'default': 'Default',
            'options': get_HealthSFX_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      sound from this list.
                      'Default': Beep. Beep. Beep.
                      '''
        }),
]
