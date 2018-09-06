import argparse
import textwrap
import string
import re
import random
import hashlib

from Patches import get_tunic_color_options, get_navi_color_options
from version import __version__

class ArgumentDefaultsHelpFormatter(argparse.RawTextHelpFormatter):

    def _get_help_string(self, action):
        return textwrap.dedent(action.help)


# 32 characters
letters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
index_to_letter = { i: letters[i] for i in range(32) }
letter_to_index = { v: k for k, v in index_to_letter.items() }

def bit_string_to_text(bits):
    # pad the bits array to be multiple of 5
    if len(bits) % 5 > 0:
        bits += [0] * (5 - len(bits) % 5)
    # convert to characters
    result = ""
    for i in range(0, len(bits), 5):
        chunk = bits[i:i + 5]
        value = 0
        for b in range(5):
            value |= chunk[b] << b
        result += index_to_letter[value]
    return result

def text_to_bit_string(text):
    bits = []
    for c in text:
        index = letter_to_index[c]
        for b in range(5):
            bits += [ (index >> b) & 1 ]
    return bits

# holds the info for a single setting
class Setting_Info():

    def __init__(self, name, type, bitwidth=0, shared=False, args_params={}, gui_params=None):
        self.name = name # name of the setting, used as a key to retrieve the setting's value everywhere
        self.type = type # type of the setting's value, used to properly convert types in GUI code
        self.bitwidth = bitwidth # number of bits needed to store the setting, used in converting settings to a string
        self.shared = shared # whether or not the setting is one that should be shared, used in converting settings to a string
        self.args_params = args_params # parameters that should be pased to the command line argument parser's add_argument() function
        self.gui_params = gui_params # parameters that the gui uses to build the widget components

# holds the particular choices for a run's settings
class Settings():

    def get_settings_display(self):
        padding = 0
        for setting in filter(lambda s: s.shared, setting_infos):
            padding = max( len(setting.name), padding )
        padding += 2
        output = ''
        for setting in filter(lambda s: s.shared, setting_infos):
            name = setting.name + ': ' + ' ' * (padding - len(setting.name))
            val = str(self.__dict__[setting.name])
            output += name + val + '\n'
        return output

    def get_settings_string(self):
        bits = []
        for setting in filter(lambda s: s.shared and s.bitwidth > 0, setting_infos):
            value = self.__dict__[setting.name]
            i_bits = []
            if setting.type == bool:
                i_bits = [ 1 if value else 0 ]
            if setting.type == str:
                index = setting.args_params['choices'].index(value)
                # https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
                i_bits = [1 if digit=='1' else 0 for digit in bin(index)[2:]]
                i_bits.reverse()
            if setting.type == int:
                value = value - ('min' in setting.gui_params and setting.gui_params['min'] or 0)
                value = int(value / ('step' in setting.gui_params and setting.gui_params['step'] or 1))
                value = min(value, ('max' in setting.gui_params and setting.gui_params['max'] or value))
                # https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
                i_bits = [1 if digit=='1' else 0 for digit in bin(value)[2:]]
                i_bits.reverse()
            # pad it
            i_bits += [0] * ( setting.bitwidth - len(i_bits) )
            bits += i_bits
        return bit_string_to_text(bits)

    def update_with_settings_string(self, text):
        bits = text_to_bit_string(text)

        for setting in filter(lambda s: s.shared and s.bitwidth > 0, setting_infos):
            cur_bits = bits[:setting.bitwidth]
            bits = bits[setting.bitwidth:]
            value = None
            if setting.type == bool:
                value = True if cur_bits[0] == 1 else False
            if setting.type == str:
                index = 0
                for b in range(setting.bitwidth):
                    index |= cur_bits[b] << b
                value = setting.args_params['choices'][index]
            if setting.type == int:
                value = 0
                for b in range(setting.bitwidth):
                    value |= cur_bits[b] << b
                value = value * ('step' in setting.gui_params and setting.gui_params['step'] or 1)
                value = value + ('min' in setting.gui_params and setting.gui_params['min'] or 0)
            self.__dict__[setting.name] = value

        self.settings_string = self.get_settings_string()
        self.numeric_seed = self.get_numeric_seed()

    def get_numeric_seed(self):
        # salt seed with the settings, and hash to get a numeric seed
        full_string = self.settings_string + __version__ + self.seed
        return int(hashlib.sha256(full_string.encode('utf-8')).hexdigest(), 16)

    def sanatize_seed(self):
        # leave only alphanumeric and some punctuation
        self.seed = re.sub(r'[^a-zA-Z0-9_-]', '', self.seed, re.UNICODE)

    def update_seed(self, seed):
        self.seed = seed
        self.sanatize_seed()
        self.numeric_seed = self.get_numeric_seed()

    def update(self):
        self.settings_string = self.get_settings_string()
        self.numeric_seed = self.get_numeric_seed()

    # add the settings as fields, and calculate information based on them
    def __init__(self, settings_dict):
        self.__dict__.update(settings_dict)
        for info in setting_infos:
            if info.name not in self.__dict__:
                if info.type == bool:
                    self.__dict__[info.name] = True if info.gui_params['default'] == 'checked' else False
                if info.type == str:
                    if 'default' in info.args_params:
                        self.__dict__[info.name] = info.gui_params['default'] or info.args_params['default']
                    else:
                        self.__dict__[info.name] = ""
                if info.type == int:
                    self.__dict__[info.name] = info.gui_params['default'] or 1
        self.settings_string = self.get_settings_string()
        if(self.seed is None):
            # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
            self.seed = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.sanatize_seed()
        self.numeric_seed = self.get_numeric_seed()

def parse_custom_tunic_color(s):
    if s == 'Custom Color':
        raise argparse.ArgumentTypeError('Specify custom color by using \'Custom (#xxxxxx)\'')
    elif re.match(r'^Custom \(#[A-Fa-f0-9]{6}\)$', s):
        return re.findall(r'[A-Fa-f0-9]{6}', s)[0]
    elif s in get_tunic_color_options():
        return s
    else:
        raise argparse.ArgumentTypeError('Invalid color specified')

def parse_custom_navi_color(s):
    if s == 'Custom Color':
        raise argparse.ArgumentTypeError('Specify custom color by using \'Custom (#xxxxxx)\'')
    elif re.match(r'^Custom \(#[A-Fa-f0-9]{6}\)$', s):
        return re.findall(r'[A-Fa-f0-9]{6}', s)[0]
    elif s in get_navi_color_options():
        return s
    else:
        raise argparse.ArgumentTypeError('Invalid color specified')

# a list of the possible settings
setting_infos = [
    Setting_Info('checked_version', str, 0, False, {
            'default': '',
            'help': 'Supress version warnings if checked_version is less than __version__.'}),
    Setting_Info('rom', str, 0, False, {
            'default': 'ZOOTDEC.z64',
            'help': 'Path to an OoT 1.0 rom to use as a base.'}),
    Setting_Info('output_dir', str, 0, False, {
            'default': '',
            'help': 'Path to output directory for rom generation.'}),
    Setting_Info('seed', str, 0, False, {
            'help': 'Define seed number to generate.'}),
    Setting_Info('count', int, 0, False, {
            'help': '''\
                    Use to batch generate multiple seeds with same settings.
                    If --seed is provided, it will be used for the first seed, then
                    used to derive the next seed (i.e. generating 10 seeds with
                    --seed given will produce the same 10 (different) roms each
                    time).
                    ''',
            'type': int}),
    Setting_Info('world_count', int, 0, False, {
            'default': 1,
            'help': '''\
                    Use to create a multi-world generation for co-op seeds.
                    World count is the number of players. Warning: Increasing
                    the world count will drastically increase generation time.
                    ''',
            'type': int}),
    Setting_Info('player_num', int, 0, False, {
            'default': 1,
            'help': '''\
                    Use to select world to generate when there are multiple worlds.
                    ''',
            'type': int}),
    Setting_Info('create_spoiler', bool, 1, True, 
        {
            'help': 'Output a Spoiler File',
            'action': 'store_true'
        }, 
        {
            'text': 'Create Spoiler Log',
            'group': 'rom_tab',
            'widget': 'Checkbutton',
            'default': 'checked',
            'dependency': lambda guivar: guivar['compress_rom'].get() != 'No ROM Output',
            'tooltip':'''\
                      Enabling this will change the seed.
                      '''
        }),
    Setting_Info('compress_rom', str, 2, False, 
        {
            'default': 'True',
            'const': 'True',
            'nargs': '?',
            'choices': ['True', 'False', 'None'],
            'help': '''\
                    Create a compressed version of the output rom file.
                    True: Compresses. Improves stability. Will take longer to generate
                    False: Uncompressed. Unstable. Faster generation
                    None: No ROM Output. Creates spoiler log only
                    ''',
        },
        {
            'text': 'Compress Rom',
            'group': 'rom_tab',
            'widget': 'Radiobutton',
            'default': 'Compressed [Stable]',
            'horizontal': True,
            'options': {
                'Compressed [Stable]': 'True',
                'Uncompressed [Crashes]': 'False',
                'No ROM Output': 'None',
            },
            'tooltip':'''\
                      The first time compressed generation will take a while 
                      but subsequent generations will be quick. It is highly 
                      recommended to compress or the game will crash 
                      frequently.
                      '''
        }),
    Setting_Info('open_forest', bool, 1, True, 
        {
            'help': '''\
                    Mido no longer blocks the path to the Deku Tree and
                    the Kokiri boy no longer blocks the path out of the forest.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Open Forest',
            'group': 'open',
            'widget': 'Checkbutton',
            'default': 'checked',
            'tooltip':'''\
                      The Deku Tree can be beaten without leaving the Forest
                      areas. This means that the Kokiri Sword and Slingshot
                      are always available somewhere in the forest.
                      '''
        }),
    Setting_Info('open_kakariko', bool, 1, True, 
        {
            'help': '''\
                    The gate in Kakariko Village to Death Mountain Trail
                    is always open, instead of needing Zelda's Letter.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Open Kakariko Gate',
            'group': 'open',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      The gate in Kakariko Village to Death Mountain Trail
                      is always open, instead of needing Zelda's Letter.

                      Recommend if Weird Egg is not shuffled.

                      Either way, the gate is always open as adult.
                      '''
        }),
    Setting_Info('open_door_of_time', bool, 1, True, 
        {
            'help': '''
                    The Door of Time is open from the beginning of the game.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Open Door of Time',
            'group': 'open',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      The Door of Time starts opened instead of needing to
                      play the Song of Time. Setting closed will mean there
                      is a child section before becoming adult, so there is
                      more structure.
                      '''
        }),
    Setting_Info('gerudo_fortress', str, 2, True, 
        {
            'default': 'normal',
            'const': 'normal',
            'nargs': '?',
            'choices': ['normal', 'fast', 'open'],
            'help': '''Select how much of Gerudo Fortress is required. (default: %(default)s)
                       Normal: Free all four carpenters to get the Gerudo Card.
                       Fast:   Free only the carpenter closest to Link's prison to get the Gerudo Card.
                       Open:   Start with the Gerudo Card and all it's benefits.
                    '''
        },
        {
            'text': 'Gerudo Fortress',
            'group': 'open',
            'widget': 'Combobox',
            'default': 'Default Behavior',
            'options': {
                'Default Behavior': 'normal',
                'Rescue one carpenter': 'fast',
                'Start with Gerudo Card': 'open',
            },
            'tooltip':'''\
                      'Rescure one carpenter': The carpenter rescue sequence 
                      is much faster and doesn't affect logic much.

                      'Start with Gerudo Card': skips the rescue entirely, 
                      so Epona and Longshot are not required to enter GTG.
                      '''
        }),
    Setting_Info('bridge', str, 2, True, 
        {
            'default': 'medallions',
            'const': 'medallions',
            'nargs': '?',
            'choices': ['medallions', 'vanilla', 'dungeons', 'open'],
            'help': '''\
                    Select requirement to spawn the Rainbow Bridge to reach Ganon's Castle. (default: %(default)s)
                    Medallions:    Collect all six medallions to create the bridge.
                    Vanilla:       Collect only the Shadow and Spirit Medallions and then view the Light Arrow cutscene.
                    All Dungeons:  Collect all spiritual stones and all medallions to create the bridge.
                    Open:          The bridge will spawn without an item requirement.
                    '''
        },
        {
            'text': 'Rainbow Bridge Requirement',
            'group': 'open',
            'widget': 'Combobox',
            'default': 'All medallions',
            'options': {
                'All dungeons': 'dungeons',
                'All medallions': 'medallions',
                'Vanilla requirements': 'vanilla',
                'Always open': 'open',
            },
            'tooltip':'''\
                      'All dungeons': All Medallions and Stones

                      'All medallions': Medallions but no Stones

                      'Vanilla requirements': Spirit and Shadow 
                      Medallion and the Light Arrows

                      'Always open': Nothing
                      '''
        }),
    Setting_Info('bombchus_in_logic', bool, 1, True, 
        {
            'help': '''\
                    Bombchus will be considered in logic. This has a few effects:
                    -Back alley shop will open once you've found Bombchus
                    -It will sell an affordable pack (5 for 60), and never sell out
                    -Bombchu Bowling will open once you've found Bombchus
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Bombchus are considered in logic',
            'group': 'logic',
            'widget': 'Checkbutton',
            'default': 'checked',
            'tooltip':'''\
                      Bombchus are properly considered in logic.

                      The first bombchu pack will always be 20.
                      Subsequent packs will be 5 or 10 based on
                      how many you have. 

                      Bombchus can be purchased for 60/99/180 
                      rupees once they are been found.

                      Bombchu Bowling opens with bombchus.
                      '''
        }),
    Setting_Info('trials_random', bool, 1, True, 
        {
            'help': '''\
                    Sets the number of trials must be cleared to enter 
                    Ganon's Tower to a random value.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Random Number of Ganon\'s Trials',
            'group': 'open',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Sets a random number of trials to
                      enter Ganon's Tower.
                      '''
        }),
    Setting_Info('trials', int, 3, True, 
        {
            'default': 6,
            'const': 6,
            'nargs': '?',
            'choices': [0, 1, 2, 3, 4, 5, 6],
            'help': '''\
                    Select how many trials must be cleared to enter Ganon's Tower.
                    The trials you must complete will be selected randomly.
                    ''',
            'type': int                    
        },
        {
            'group': 'open',
            'widget': 'Scale',
            'default': 6,
            'min': 0,
            'max': 6,
            'random': True,
            'tooltip':'''\
                      Trials are randomly selected. If hints are
                      enabled, then there will be hints for which
                      trials need to be completed.
                      ''',
            'dependency': lambda guivar: not guivar['trials_random'].get(),
        }),
    Setting_Info('no_escape_sequence', bool, 1, True, 
        {
            'help': '''\
                    The tower collapse escape sequence between Ganondorf and Ganon will be skipped.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Skip Tower Collapse Escape Sequence',
            'group': 'convenience',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      The tower collapse escape sequence between 
                      Ganondorf and Ganon will be skipped.
                      '''
        }),
    Setting_Info('no_guard_stealth', bool, 1, True, 
        {
            'help': '''\
                    The crawlspace into Hyrule Castle will take you straight to Zelda.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Skip Interior Castle Guard Stealth Sequence',
            'group': 'convenience',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      The crawlspace into Hyrule Castle goes
                      straight to Zelda, skipping the guards.
                      '''
        }),
    Setting_Info('no_epona_race', bool, 1, True, 
        {
            'help': '''\
                    Having Epona's song will allow you to summon epona without racing Ingo.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Skip Epona Race',
            'group': 'convenience',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Epona can be summoned with Epona's Song
                      without needing to race Ingo.
                      '''
        }),
    Setting_Info('fast_chests', bool, 1, True, 
        {
            'help': '''\
                    Makes all chests open without the large chest opening cutscene
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Fast Chest Cutscenes',
            'group': 'convenience',
            'widget': 'Checkbutton',
            'default': 'checked',
            'tooltip':'''\
                      All chest animations are fast. If disabled,
                      the animation time is slow for major items.
                      '''
        }),
    Setting_Info('big_poe_count_random', bool, 1, True, 
        {
            'help': '''\
                    Sets a random number of Big Poes to receive an item from the buyer.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Random Big Poe Target Count',
            'group': 'convenience',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      The Poe buyer will give a reward for turning 
                      in a random number of Big Poes.
                      '''
        }),
    Setting_Info('big_poe_count', int, 4, True, 
        {
            'default': 10,
            'const': 10,
            'nargs': '?',
            'choices': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'help': '''\
                    Select the number of Big Poes to receive an item from the buyer.
                    ''',
            'type': int,
        },
        {
            'group': 'convenience',
            'widget': 'Scale',
            'default': 10,
            'min': 1,
            'max': 10,
            'tooltip':'''\
                      The Poe buyer will give a reward for turning 
                      in the chosen number of Big Poes.
                      ''',
            'dependency': lambda guivar: not guivar['big_poe_count_random'].get(),
        }),
    Setting_Info('free_scarecrow', bool, 1, True, 
        {
            'help': '''\
                    Start with the scarecrow song. You do not need
                    to play it as child or adult at the scarecrow
                    patch to be able to summon Pierre.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Start with Scarecrow Song',
            'group': 'convenience',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Skips needing to go to Lake Hylia as both
                      child and adult to learn Scarecrow Song.
                      '''
        }),
    Setting_Info('scarecrow_song', str, 0, False, 
        {
            'default': 'DAAAAAAA',
            'const': 'DAAAAAAA',
            'nargs': '?',
            'help': '''\
                    The song started with if 'free_scarecrow' is True
                    ''',
        },
        {
            'group': 'convenience',
            'widget': 'Entry',
            'default': 'DAAAAAAA',
            'dependency': lambda guivar: guivar['free_scarecrow'].get(),
            'tooltip':'''\
                      Song must be 8 notes long and have at least 
                      two different notes.
                      Valid notes are: 
                      'A': A Button 
                      'D': C-Down
                      'U': C-Up
                      'L': C-Left 
                      'R': C-Right
                      '''
        }),
    Setting_Info('unlocked_ganondorf', bool, 1, True, 
        {
            'help': '''\
                    The Boss Key door in Ganon's Tower will start unlocked.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Remove Ganon\'s Boss Door Lock',
            'group': 'open',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Best when used when reducing the number of 
                      Trials to less than 6 to prevent needing
                      to do them all anyways looking for the key.
                      '''
        }),
    Setting_Info('all_reachable', bool, 1, True, 
        {
            'help': '''\
                    When disabled, only check if the game is beatable with 
                    placement. Do not ensure all locations are reachable. 
                    This only has an effect on the restrictive algorithm 
                    currently.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'All Locations Reachable',
            'group': 'logic',
            'widget': 'Checkbutton',
            'default': 'checked',
            'tooltip':'''\
                      Chests that lock themselves can still exists.
                      When disabled, some locations and item might 
                      not be reachable.
                      '''
        }), 
    Setting_Info('shuffle_kokiri_sword', bool, 1, True, 
        {
            'help': '''\
                    Shuffles the Kokiri Sword into the pool.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Shuffle Kokiri Sword',
            'group': 'logic',
            'widget': 'Checkbutton',
            'default': 'checked',
            'tooltip':'''\
                      Disabling this will make the Kokiri Sword
                      always available at the start.
                      '''
        }),
    Setting_Info('shuffle_weird_egg', bool, 1, True, 
        {
            'help': '''\
                    Shuffles the Weird Egg item from Malon into the pool.
                    This means that you need to find the egg before going Zelda.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Shuffle Weird Egg',
            'group': 'logic',
            'widget': 'Checkbutton',
            'default': 'checked',
            'tooltip':'''\
                      You need to find the egg before going Zelda.
                      This means the Weird Egg locks the items from
                      Impa, Saria, Malon, and Talon.
                      '''
        }),
    Setting_Info('shuffle_ocarinas', bool, 1, True, 
        {
            'help': '''\
                    Shuffles the Fairy Ocarina and the Ocarina of Time into the pool.
                    This means that you need to find the ocarina before playing songs. 
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Shuffle Ocarinas',
            'group': 'logic',
            'widget': 'Checkbutton',
            'default': 'checked',
            'tooltip':'''\
                      The Fairy Ocarina and Ocarina of Time are
                      randomized. One will be required before 
                      songs can be played. 

                      This is good in combination with Closed 
                      Door of Time for a more interesting child 
                      section.
                      '''
        }),
    Setting_Info('shuffle_song_items', bool, 1, True, 
        {
            'help': '''\
                    Shuffles the songs with with rest of the item pool so that
                    song can appear at other locations, and items can appear at
                    the song locations.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Shuffle Songs with Items',
            'group': 'logic',
            'widget': 'Checkbutton',
            'default': 'checked',
            'tooltip':'''\
                      Songs can appear anywhere not just Vanilla
                      song locations. This significantly reduces
                      song placement bias and makes the songs more
                      evenly distributed.
                      '''
        }),
    Setting_Info('shuffle_gerudo_card', bool, 1, True, 
        {
            'help': '''\
                    Shuffles the Gerudo Card into the item pool.
                    The Gerudo Card does not stop guards from throwing you in jail.
                    It only grants access to Training Grounds, AFTER all carpenters have been rescued.
                    This option does nothing if "gerudo_fortress" is "open".
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Shuffle Gerudo Card',
            'group': 'logic',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'dependency': lambda guivar: guivar['gerudo_fortress'].get() != 'Start with Gerudo Card',
            'tooltip':'''\
                      Gerudo Membership Card is required to
                      enter Gerudo Training Grounds. It is
                      effectively the Boss Key of Gerudo Fortress.

                      Plays spiritually best with Keysanity.
                      '''
        }),
    Setting_Info('shuffle_dungeon_items', str, 2, True,
        {
        'default': 'mapcompass',
        'const': 'mapcompass',
        'nargs': '?',
        'choices': ['off', 'mapcompass', 'keysanity'],
        'help': '''\
                    Dungeon items can appear outside of their
                    respective dungeon.
                    off:            Dungeon items will be in their dungeons
                    mapcompass:     Maps and Compasses can appear anywhere
                    keysanity:      Dungeon items can appear anywhere
                    '''
        },
        {
            'text': 'Shuffle Dungeon Items',
            'group': 'logic',
            'widget': 'Combobox',
            'default': 'Maps and Compasses',
            'options': {
                'Off': 'off',
                'Maps and Compasses': 'mapcompass',
                'Full Keysanity': 'keysanity'
            },
            'tooltip':'''\
                      Dungeon items can appear anywhere instead 
                      of just being restricted to their own dungeon.

                      'Maps and Compasses': Dungeons will have
                      2 more possible item locations. This helps
                      make some dungeons more profitable, such as
                      Ice Cavern and Jabu Jabu's Belly.

                      'Full Keysanity': Maps, Compasses, and Keys
                      can appear anywhere. A difficult mode, since 
                      it is more likely to need to enter a dungeon
                      multiple times.
                      '''
        }),
    Setting_Info('tokensanity', str, 2, True, 
        {
            'default': 'off',
            'const': 'off',
            'nargs': '?',
            'choices': ['off', 'dungeons', 'all'],
            'help': '''\
                    Gold Skulltula Tokens will be shuffled into the pool,
                    and Gold Skulltula locations can have any item.
                    off:        Don't use this feature
                    dungeons:   Only dungeon skulltulas will be shuffled
                    all:        All skulltulas will be shuffled
                    '''
        },
        {
            'text': 'Tokensanity',
            'group': 'logic',
            'widget': 'Combobox',
            'default': 'Off',
            'options': {
                'Off': 'off',
                'Dungeons Only': 'dungeons',
                'All Tokens': 'all',
            },
            'tooltip':'''\
                      Token reward from Gold Skulltulas are 
                      shuffled into the pool.

                      'Dungeon Only': This helps make some 
                      dungeons more profitable, such as 
                      Ice Cavern and Jabu Jabu's Belly.
                      Some GS locations in dungeons have
                      interesting requirements to reach.
                      This is a recommended option.

                      'All Tokens': Effectively adds 100
                      new locations for items to appear.
                      '''
        }),
    Setting_Info('quest', str, 2, True, 
        {
            'default': 'vanilla',
            'const': 'vanilla',
            'nargs': '?',
            'choices': ['vanilla', 'master', 'mixed'],
            'help': '''\
                    Select requirement to spawn the Rainbow Bridge to reach Ganon's Castle. (default: %(default)s)
                    Vanilla:       Dungeons will be the original Ocarina of Time dungeons.
                    Master:        Dungeons will be in the form of the Master Quest.
                    Mixed:         Each dungeon will randomly be either standard or Master Quest.
                    '''
        },
        {
            'text': 'Dungeon Quest',
            'group': 'logic',
            'widget': 'Combobox',
            'default': 'Vanilla',
            'options': {
                'Vanilla (recommended)': 'vanilla',
                'Master Quest (beta)': 'master',
                'Mixed (beta)': 'mixed',
            },
            'tooltip':'''\
                      'Vanilla': Dungeons will be in their
                      default OoT form (recommended).

                      'Master Quest': Dungeons will be in the
                      form found in OoT: Master Quest (beta).

                      'Mixed': Each dungeon will have a
                      random chance to be in either form (beta).
                      '''
        }),
    Setting_Info('logic_skulltulas', int, 3, True, 
        {
            'default': 50,
            'const': 50,
            'nargs': '?',
            'choices': [0, 10, 20, 30, 40, 50],
            'help': '''\
                    Choose the maximum number of gold skulltula tokens you will be expected to collect.
                    ''',
            'type': int
        },
        {
            'text': 'Maximum expected skulltula tokens',
            'group': 'rewards',
            'widget': 'Scale',
            'default': 50,
            'min': 0,
            'max': 50,
            'step': 10,
            'tooltip':'''\
                      Skulltula Token rewards are time consuming.
                      '''
        }),
    Setting_Info('logic_no_night_tokens_without_suns_song', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to collect nighttime-only skulltulas
                    unless you have Sun's Song
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No Nighttime Skulltulas without Sun\'s Song',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Skulltula Tokens that can only be obtained
                      during the night expect you to have Sun's
                      Song to collect them. This prevents needing
                      to wait until night for some locations.
                      '''
        }),
    Setting_Info('logic_no_big_poes', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to collect 10 big poes.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No Big Poes',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Big Poes reward is time consuming
                      '''
        }),
    Setting_Info('logic_no_child_fishing', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to obtain the child fishing reward.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No Child Fishing',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Fishing does not work correctly on
                      some emulators.
                      '''
        }),
    Setting_Info('logic_no_adult_fishing', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to obtain the adult fishing reward.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No Adult Fishing',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Fishing does not work correctly on
                      some emulators.
                      '''
        }),
    Setting_Info('logic_no_trade_skull_mask', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to show the skull mask at the forest stage.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No Skull Mask reward',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Mask trade quest is time consuming.
                      '''
        }),
    Setting_Info('logic_no_trade_mask_of_truth', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to show the mask of truth at the forest stage.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No Mask of Truth reward',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Completing mask trade quest is very
                      time consuming and requires all 3
                      Spiritual Stones.
                      '''
        }),
    Setting_Info('logic_no_trade_biggoron', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to trade for biggoron's reward.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No Biggoron reward',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Adult trade sequence is time consuming.
                      '''
        }),
    Setting_Info('logic_no_1500_archery', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to win the 1500 point horseback archery reward.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No 1500 Horseback Archery',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Some find this too difficult on emulator.
                      Also it is doing the same thing twice.
                      '''
        }),
    Setting_Info('logic_no_memory_game', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to play the memory game in lost woods with the skull kids.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No Lost Woods Memory Game',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Memory game is time consuming.
                      '''
        }),
    Setting_Info('logic_no_second_dampe_race', bool, 1, True, 
        {
            'help': '''\
                    You will not be expected to race Dampe a second time.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'No Racing Dampe a second time',
            'group': 'rewards',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Racing twice is repetitive.
                      '''
        }),
    Setting_Info('logic_man_on_roof', bool, 1, True, 
        {
            'help': '''\
                    The man on the roof will not require the hookshot in logic.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Man on Roof without Hookshot',
            'group': 'tricks',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Can be reached by side-hopping off of
                      the watchtower.
                      '''
        }),
    Setting_Info('logic_child_deadhand', bool, 1, True, 
        {
            'help': '''\
                    Deadhand in the Bottom of the Well will not require the Kokiri sword in logic.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Child Deadhand without Kokiri Sword',
            'group': 'tricks',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Requires 9 sticks or 5 jump slashes.
                      '''
        }),
    Setting_Info('logic_dc_jump', bool, 1, True, 
        {
            'help': '''\
                    Jumping towards the bomb bag chest in Dodongo's Cavern as an adult
                    will not require hover boots in logic.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Dodongo\'s Cavern spike trap room jump without Hover Boots',
            'group': 'tricks',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Jump is adult only.
                      '''
        }),
    Setting_Info('logic_windmill_hp', bool, 1, True, 
        {
            'help': '''\
                    Getting the heart piece in the windmill as an adult will require nothing in logic.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Windmill HP as adult with nothing',
            'group': 'tricks',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Can jump up to the spinning platform from
                      below as adult.
                      '''
        }),
    Setting_Info('logic_crater_bean_hp_with_hovers', bool, 1, True, 
        {
            'help': '''\
                    The Heart Piece in Death Mountain Crater than normally requires the bean to reach
                    will optionally require the Hover Boots in logic.
                    ''',
            'action': 'store_true'
        },
        {
            'text': "Crater's bean HP with Hover Boots",
            'group': 'tricks',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Hover from the top of the crater.
                      '''
        }),
    Setting_Info('logic_zora_with_cucco', bool, 1, True, 
        {
            'help': '''\
                    Zora's Domain can be entered with a Cucco as child in logic.
                    ''',
            'action': 'store_true'
        },
        {
            'text': "Zora's Domain entry with Cucco",
            'group': 'tricks',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Can fly behind the waterfall with 
                      a cucco as child.
                      '''
        }),
    Setting_Info('logic_zora_with_hovers', bool, 1, True, 
        {
            'help': '''\
                    Zora's Domain can be entered with Hover Boots as Adult in logic.
                    ''',
            'action': 'store_true'
        },
        {
            'text': "Zora's Domain entry with Hover Boots",
            'group': 'tricks',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Can hover behind the waterfall as adult.
                      '''
        }),
    Setting_Info('logic_fewer_tunic_requirements', bool, 1, True, 
        {
            'help': '''\
                    Allows the following possible without Goron or Zora Tunic:
                    Enter Water Temple
                    Enter Fire Temple
                    Zoras Fountain Bottom Freestanding PoH
                    Gerudo Training Grounds Underwater Silver Rupee Chest
                    ''',
            'action': 'store_true'
        },
        {
            'text': "Fewer Tunic Requirements",
            'group': 'tricks',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Allows the following possible without Tunics:
                      - Enter Water Temple. The key below the center
                      pillar still requires Zora Tunic.
                      - Enter Fire Temple. Only the first floor is
                      accessible, and not Volvagia.
                      - Zoras Fountain Bottom Freestanding PoH.
                      Might not have enough health to resurface.
                      - Gerudo Training Grounds Underwater 
                      Silver Rupee Chest. Will need to make multiple
                      trips.
                      '''
        }),
    Setting_Info('logic_lens', str, 2, True, 
        {
            'default': 'all',
            'const': 'always',
            'nargs': '?',
            'choices': ['chest', 'chest-wasteland', 'all'],
            'help': '''\
                    Choose what expects the Lens of Truth:
                    all:              All lens spots expect the lens (except those that did not in the original game)
                    chest-wasteland:  Only wasteland and chest minigame expect the lens
                    chest:            Only the chest minigame expects the lens
                    '''
        },
        {
            'text': 'Lens of Truth',
            'group': 'tricks',
            'widget': 'Combobox',
            'default': 'Required everywhere',
            'options': {
                'Required everywhere': 'all',
                'Wasteland and Chest Minigame': 'chest-wasteland',
                'Only Chest Minigame': 'chest',
            },
            'tooltip':'''\
                      'Required everywhere': every invisible or 
                      fake object will expect you to have the
                      Lens of Truth and Magic. The exception is
                      passing through the first wall in Bottom of
                      the Well, since that is required in Vanilla.

                      'Wasteland': The lens is needed to follow
                      the ghost guide across the Desert Wasteland.
                      '''
        }),
    Setting_Info('ocarina_songs', bool, 1, True, 
        {
            'help': '''\
                    Randomizes the notes need to play for each ocarina song.
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Randomize ocarina song notes',
            'group': 'other',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Will need to memorize a new set of songs.
                      Can be silly, but difficult. Song are
                      generally sensible, and warp songs are
                      typically more difficult.
                      '''
        }),
        Setting_Info('check_version', bool, 0, False, 
        {
            'help': '''\
                    Checks if you are on the latest version
                    ''',
            'action': 'store_true'
        }),
    Setting_Info('correct_chest_sizes', bool, 1, True, 
        {
            'help': '''\
                    Updates the chest sizes to match their contents.
                    Small Chest = Useless Item
                    Big Chest = Progression Item
                    Boss Chest = Dungeon Item
                    ''',
            'action': 'store_true'
        },
        {
            'text': 'Chests size matches contents',
            'group': 'other',
            'widget': 'Checkbutton',
            'default': 'unchecked',
            'tooltip':'''\
                      Chests will be large if they contain a major 
                      item and small if not. Allows skipping 
                      chests if they are small. However skipping
                      small chests will mean having low health,
                      ammo, and rupees, so doing so is a risk.
                      '''
        }),
    Setting_Info('hints', str, 2, True, 
        {
            'default': 'none',
            'const': 'always',
            'nargs': '?',
            'choices': ['none', 'mask', 'agony', 'always'],
            'help': '''\
                    Choose how Gossip Stones behave
                    none:   Default behavior
                    mask:   Have useful hints that are read with the Mask of Truth (untested)
                    agony:  Have useful hints that are read with Stone of Agony
                    always: Have useful hints which can always be read
                    '''
        },
        {
            'text': 'Gossip Stones',
            'group': 'other',
            'widget': 'Combobox',
            'default': 'Hints; Need Nothing',
            'options': {
                'No Hints': 'none',
                'Hints; Need Mask of Truth': 'mask',
                'Hints; Need Stone of Agony': 'agony',
                'Hints; Need Nothing': 'always',
            },
            'tooltip':'''\
                      Hints allow for more dynamic routing.
                      Spending time to gain knowledge of the
                      world can give better routing plans
                      and potentially save time.

                      Hints for 'on the way of the hero' are
                      locations that contain items that are
                      required to beat the game.

                      It is recommended to play with
                      'Hints; Need Nothing'. Requiring the
                      Stone of Agony generally requires
                      backtracking to locations for the hints,
                      which make them often not worthwhile.
                      '''
        }),
    Setting_Info('text_shuffle', str, 2, True, 
        {
            'default': 'none',
            'const': 'none',
            'nargs': '?',
            'choices': ['none', 'except_hints', 'complete'],
            'help': '''\
                    Choose how to shuffle the game's messages.
                    none:          Default behavior
                    except_hints:  All text except Gossip Stone hints and Dungeon reward hints is shuffled.
                    complete:      All text is shuffled
                    '''
        },
        {
            'text': 'Text Shuffle',
            'group': 'other',
            'widget': 'Combobox',
            'default': 'No text shuffled',
            'options': {
                'No text shuffled': 'none',
                'Shuffled except Hints and Keys': 'except_hints',
                'All text shuffled': 'complete',
            },
            'tooltip':'''\
                      Will make things confusing for comedic value.

                      'Shuffled except Hints and Keys': Key texts
                      not shuffled because in keysanity it is
                      impossible to tell what dungeon it is for
                      without the correct text.
                      '''
        }),
    Setting_Info('difficulty', str, 2, True, 
        {
            'default': 'normal',
            'const': 'normal',
            'nargs': '?',
            'choices': ['normal', 'hard', 'very_hard', 'ohko'],
            'help': '''\
                    Choose how hard the game will be.
                    normal:         Default items
                    hard:           Double defense, double magic, and all 8 heart containers are removed
                    very_hard:      Double defense, double magic, Nayru's Love, and all health upgrades are removed
                    ohko:           Same as very hard, and Link will die in one hit.
                    '''
        },
        {
            'text': 'Difficulty',
            'group': 'other',
            'widget': 'Combobox',
            'default': 'Normal',
            'options': {
                'Normal': 'normal',
                'Hard': 'hard',
                'Very Hard': 'very_hard',
                'OHKO': 'ohko'
            },
            'tooltip':'''\
                      Makes health less available

                      'Hard': Heart Containers, Double Magic,
                      and Double Defense are removed.

                      'Very Hard': Heart Containers, Heart,
                      Pieces, Double Magic, Double Defense, 
                      and Nayru's Love are removed.

                      'OHKO': Link dies in one hit.
                      '''
        }),
    Setting_Info('default_targeting', str, 1, False, 
        {
            'default': 'hold',
            'const': 'always',
            'nargs': '?',
            'choices': ['hold', 'switch'],
            'help': '''\
                    Choose what the default targeting is.
                    '''
        },
        {
            'text': 'Default Targeting Option',
            'group': 'rom_tab',
            'widget': 'Combobox',
            'default': 'Hold',
            'options': {
                'Hold': 'hold',
                'Switch': 'switch',
            }
        }),
    Setting_Info('background_music', str, 2, False,
        {
            'default': 'normal',
            'const': 'normal',
            'nargs': '?',
            'choices': ['normal', 'off', 'random'],
            'help': '''\
                    Sets the background music behavior
                    normal:      Areas play their normal background music
                    off:         No background music
                    random:      Areas play random background music
                    '''
        },
        {
            'text': 'Background Music',
            'group': 'cosmetics',
            'widget': 'Combobox',
            'default': 'Normal',
            'options': {
                'Normal': 'normal',
                'No Music': 'off',
                'Random': 'random',
            },
            'tooltip': '''\
                       'No Music': No background is played.
                       Useful for playing your own music
                       over the game.

                       'Random': Area background music is
                       randomized.
                       '''
        }),

    Setting_Info('kokiricolor', str, 0, False, 
        {
            'default': 'Kokiri Green',
            'const': 'Kokiri Green',
            'nargs': '?',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Kokiri Tunic. (default: %(default)s)
                    
                    '''
        },
        {
            'text': 'Kokiri Tunic Color',
            'group': 'tuniccolor',
            'widget': 'Combobox',
            'default': 'Kokiri Green',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random 
                      color from this list of colors.
                      'Comepletely Random': Choose a random 
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('goroncolor', str, 0, False, 
        {
            'default': 'Goron Red',
            'const': 'Goron Red',
            'nargs': '?',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Goron Tunic. (default: %(default)s)
                    Color:              Make the Goron Tunic this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Comepletely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Goron Tunic Color',
            'group': 'tuniccolor',
            'widget': 'Combobox',
            'default': 'Goron Red',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random 
                      color from this list of colors.
                      'Comepletely Random': Choose a random 
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('zoracolor', str, 0, False, 
        {
            'default': 'Zora Blue',
            'const': 'Zora Blue',
            'nargs': '?',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Zora Tunic. (default: %(default)s)
                    Color:              Make the Zora Tunic this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Comepletely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Zora Tunic Color',
            'group': 'tuniccolor',
            'widget': 'Combobox',
            'default': 'Zora Blue',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random 
                      color from this list of colors.
                      'Comepletely Random': Choose a random 
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navicolordefault', str, 0, False, 
        {
            'default': 'White',
            'const': 'White',
            'nargs': '?',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is idle. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Chocie:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Idle',
            'group': 'navicolor',
            'widget': 'Combobox',
            'default': 'White',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random 
                      color from this list of colors.
                      'Comepletely Random': Choose a random 
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navicolorenemy', str, 0, False, 
        {
            'default': 'Yellow',
            'const': 'Yellow',
            'nargs': '?',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is targeting an enemy. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Chocie:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Targeting Enemy',
            'group': 'navicolor',
            'widget': 'Combobox',
            'default': 'Yellow',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random 
                      color from this list of colors.
                      'Comepletely Random': Choose a random 
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navicolornpc', str, 0, False, 
        {
            'default': 'Light Blue',
            'const': 'Light Blue',
            'nargs': '?',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is targeting an NPC. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Chocie:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Targeting NPC',
            'group': 'navicolor',
            'widget': 'Combobox',
            'default': 'Light Blue',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random 
                      color from this list of colors.
                      'Comepletely Random': Choose a random 
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navicolorprop', str, 0, False, 
        {
            'default': 'Green',
            'const': 'Green',
            'nargs': '?',
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
            'group': 'navicolor',
            'widget': 'Combobox',
            'default': 'Green',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random 
                      color from this list of colors.
                      'Comepletely Random': Choose a random 
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navisfxoverworld', str, 0, False, 
        {
            'default': 'Default',
            'const': 'Default',
            'nargs': '?',
            'choices': ['Default', 'Notification', 'Rupee', 'Timer', 'Tamborine', 'Recovery Heart', 'Carrot Refill', 'Navi - Hey!', 'Navi - Random', 'Zelda - Gasp', 'Cluck', 'Mweep!', 'Random', 'None'],
            'help': '''\
                    Select the sound effect that plays when Navi has a hint. (default: %(default)s)
                    Sound:         Replace the sound effect with the chosen sound.
                    Random Chocie: Replace the sound effect with a random sound from this list.
                    None:          Eliminate Navi hint sounds.
                    '''
        },
        {
            'text': 'Navi Hint',
            'group': 'navihint',
            'widget': 'Combobox',
            'default': 'Default',
            'options': [
                'Random Choice', 
                'Default', 
                'Notification', 
                'Rupee', 
                'Timer', 
                'Tamborine', 
                'Recovery Heart', 
                'Carrot Refill', 
                'Navi - Hey!',
                'Navi - Random',
                'Zelda - Gasp', 
                'Cluck', 
                'Mweep!', 
                'None',
            ]
        }),
        Setting_Info('navisfxenemytarget', str, 0, False, 
        {
            'default': 'Default',
            'const': 'Default',
            'nargs': '?',
            'choices': ['Default', 'Notification', 'Rupee', 'Timer', 'Tamborine', 'Recovery Heart', 'Carrot Refill', 'Navi - Hey!', 'Navi - Random', 'Zelda - Gasp', 'Cluck', 'Mweep!', 'Random', 'None'],
            'help': '''\
                    Select the sound effect that plays when targeting an enemy. (default: %(default)s)
                    Sound:         Replace the sound effect with the chosen sound.
                    Random Chocie: Replace the sound effect with a random sound from this list.
                    None:          Eliminate Navi hint sounds.
                    '''
        },
        {
            'text': 'Navi Enemy Target',
            'group': 'navihint',
            'widget': 'Combobox',
            'default': 'Default',
            'options': [
                'Random Choice', 
                'Default', 
                'Notification', 
                'Rupee', 
                'Timer', 
                'Tamborine', 
                'Recovery Heart', 
                'Carrot Refill', 
                'Navi - Hey!',
                'Navi - Random',
                'Zelda - Gasp', 
                'Cluck', 
                'Mweep!', 
                'None',
            ]
        }),
    Setting_Info('healthSFX', str, 0, False, 
        {
            'default': 'Default',
            'const': 'Default',
            'nargs': '?',
            'choices': ['Default', 'Softer Beep', 'Rupee', 'Timer', 'Tamborine', 'Recovery Heart', 'Carrot Refill', 'Navi - Hey!', 'Zelda - Gasp', 'Cluck', 'Mweep!', 'Random', 'None'],
            'help': '''\
                    Select the sound effect that loops at low health. (default: %(default)s)
                    Sound:         Replace the sound effect with the chosen sound.
                    Random Chocie: Replace the sound effect with a random sound from this list.
                    None:          Eliminate heart beeps.
                    '''
        },
        {
            'text': 'Low Health SFX',
            'group': 'lowhp',
            'widget': 'Combobox',
            'default': 'Default',
            'options': [
                'Random Choice', 
                'Default', 
                'Softer Beep', 
                'Rupee', 
                'Timer', 
                'Tamborine', 
                'Recovery Heart', 
                'Carrot Refill', 
                'Navi - Hey!', 
                'Zelda - Gasp', 
                'Cluck', 
                'Mweep!', 
                'None',
            ],
            'tooltip':'''\
                      'Random Choice': Choose a random 
                      sound from this list of colors.
                      'Default': Beep. Beep. Beep.
                      '''
        }),
]

# gets the randomizer settings, whether to open the gui, and the logger level from command line arguments
def get_settings_from_command_line_args():
    parser = argparse.ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    for info in setting_infos:
        parser.add_argument("--" + info.name, **info.args_params)

    parser.add_argument('--gui', help='Launch the GUI', action='store_true')
    parser.add_argument('--loglevel', default='info', const='info', nargs='?', choices=['error', 'info', 'warning', 'debug'], help='Select level of logging for output.')
    parser.add_argument('--settings_string', help='Provide sharable settings using a settings string. This will override all flags that it specifies.')

    args = parser.parse_args()

    result = {}
    for info in setting_infos:
        result[info.name] = vars(args)[info.name]
    settings = Settings(result)

    if args.settings_string is not None:
        settings.update_with_settings_string(args.settings_string)

    return settings, args.gui, args.loglevel
