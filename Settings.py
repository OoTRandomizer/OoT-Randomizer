import argparse
import textwrap
import string
import re
import hashlib
import math
import sys
import json

from version import __version__
from Utils import random_choices, local_path
from SettingsList import setting_infos, get_setting_info

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
            if setting.type == list:
                val = ('\n' + (' ' * (padding + 2))).join(self.__dict__[setting.name])
            else:
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
                if 'choices' in setting.args_params:
                    try:
                        index = setting.args_params['choices'].index(value)
                    except ValueError:
                        index = setting.args_params['choices'].index(setting.args_params['default'])
                    # https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
                    i_bits = [1 if digit=='1' else 0 for digit in bin(index)[2:]]
                    i_bits.reverse()
                elif 'char_options' in setting.gui_params:
                    char_bitwidth = math.ceil(math.log(len(setting.gui_params['char_options']), 2))
                    for c in value.upper():
                        index = setting.gui_params['char_options'].index(c)
                        # https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
                        c_bits = [1 if digit=='1' else 0 for digit in bin(index)[2:]]
                        c_bits.reverse()
                        c_bits += [0] * ( char_bitwidth - len(c_bits) )
                        i_bits.extend(c_bits)
                else:
                    raise ValueError('Setting is string type, but missing parse parameters.')
            if setting.type == int:
                value = int(value)
                value = value - (setting.gui_params.get('min', 0))
                value = int(value / (setting.gui_params.get('step', 1)))
                value = min(value, (setting.gui_params.get('max', value)))
                # https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
                i_bits = [1 if digit=='1' else 0 for digit in bin(value)[2:]]
                i_bits.reverse()
            if setting.type == list:
                if 'choices' in setting.args_params:
                    if len(value) > len(setting.args_params['choices']) / 2:
                        value = [item for item in setting.args_params['choices'] if item not in value]
                        terminal = [1] * setting.bitwidth
                    else:
                        terminal = [0] * setting.bitwidth

                    for item in value:                       
                        try:
                            index = setting.args_params['choices'].index(item)
                        except ValueError:
                            continue

                        item_bits = [1 if digit=='1' else 0 for digit in bin(index+1)[2:]]
                        item_bits.reverse()
                        item_bits += [0] * ( setting.bitwidth - len(item_bits) )
                        i_bits.extend(item_bits)
                    i_bits.extend(terminal)
                else:
                    raise ValueError('Setting is list type, but missing parse parameters.')

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
                if 'choices' in setting.args_params:
                    index = 0
                    for b in range(setting.bitwidth):
                        index |= cur_bits[b] << b
                    value = setting.args_params['choices'][index]
                elif 'char_options' in setting.gui_params:
                    char_bitwidth = math.ceil(math.log(len(setting.gui_params['char_options']), 2))
                    value = ''
                    for i in range(0, setting.bitwidth, char_bitwidth):
                        char_bits = cur_bits[i:i+char_bitwidth]
                        index = 0
                        for b in range(char_bitwidth):
                            index |= char_bits[b] << b
                        value += setting.gui_params['char_options'][index]  
                else:
                    raise ValueError('Setting is string type, but missing parse parameters.')
            if setting.type == int:
                value = 0
                for b in range(setting.bitwidth):
                    value |= cur_bits[b] << b
                value = value * ('step' in setting.gui_params and setting.gui_params['step'] or 1)
                value = value + ('min' in setting.gui_params and setting.gui_params['min'] or 0)
            if setting.type == list:
                if 'choices' in setting.args_params:
                    value = []
                    max_index = (1 << setting.bitwidth) - 1
                    while True:
                        index = 0
                        for b in range(setting.bitwidth):
                            index |= cur_bits[b] << b

                        if index == 0:
                            break
                        if index == max_index:
                            value = [item for item in setting.args_params['choices'] if item not in value]
                            break

                        value.append(setting.args_params['choices'][index-1])
                        cur_bits = bits[:setting.bitwidth]
                        bits = bits[setting.bitwidth:]
                else:
                    raise ValueError('Setting is list type, but missing parse parameters.')

            self.__dict__[setting.name] = value

        self.settings_string = self.get_settings_string()
        self.numeric_seed = self.get_numeric_seed()

    def get_numeric_seed(self):
        # salt seed with the settings, and hash to get a numeric seed
        full_string = self.settings_string + __version__ + self.seed
        return int(hashlib.sha256(full_string.encode('utf-8')).hexdigest(), 16)

    def sanitize_seed(self):
        # leave only alphanumeric and some punctuation
        self.seed = re.sub(r'[^a-zA-Z0-9_-]', '', self.seed, re.UNICODE)

    def update_seed(self, seed):
        self.seed = seed
        self.sanitize_seed()
        self.numeric_seed = self.get_numeric_seed()

    def update(self):
        self.settings_string = self.get_settings_string()
        self.numeric_seed = self.get_numeric_seed()

    def check_dependency(self, setting_name):
        info = get_setting_info(setting_name)
        if info.gui_params is not None and 'dependency' in info.gui_params:
            return info.gui_params['dependency'](self) == None
        else:
            return True

    def remove_disabled(self):
        for info in setting_infos:
            if info.gui_params is not None and 'dependency' in info.gui_params:
                new_value = info.gui_params['dependency'](self)
                if new_value != None:
                    self.__dict__[info.name] = new_value
        self.settings_string = self.get_settings_string()

    # add the settings as fields, and calculate information based on them
    def __init__(self, settings_dict):
        self.__dict__.update(settings_dict)
        for info in setting_infos:
            if info.name not in self.__dict__:
                if info.type == bool:
                    if info.gui_params is not None and 'default' in info.gui_params:
                        self.__dict__[info.name] = True if info.gui_params['default'] == 'checked' else False
                    else:
                        self.__dict__[info.name] = False
                if info.type == str:
                    if 'default' in info.args_params:
                        self.__dict__[info.name] = info.args_params['default']
                    elif info.gui_params is not None and 'default' in info.gui_params:
                        if 'options' in info.gui_params and isinstance(info.gui_params['options'], dict):
                            self.__dict__[info.name] = info.gui_params['options'][info.gui_params['default']]
                        else:
                            self.__dict__[info.name] = info.gui_params['default']
                    else:
                        self.__dict__[info.name] = ""
                if info.type == int:
                    if 'default' in info.args_params:
                        self.__dict__[info.name] = info.args_params['default']
                    elif info.gui_params is not None and 'default' in info.gui_params:                      
                        self.__dict__[info.name] = info.gui_params['default']
                    else:
                        self.__dict__[info.name] = 1
                if info.type == list:
                    if 'default' in info.args_params:
                        self.__dict__[info.name] = list(info.args_params['default'])
                    elif info.gui_params is not None and 'default' in info.gui_params:
                        self.__dict__[info.name] = list(info.gui_params['default'])
                    else:
                        self.__dict__[info.name] = []
        self.settings_string = self.get_settings_string()
        if(self.seed is None):
            # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
            self.seed = ''.join(random_choices(string.ascii_uppercase + string.digits, k=10))
        self.sanitize_seed()
        self.numeric_seed = self.get_numeric_seed()


# gets the randomizer settings, whether to open the gui, and the logger level from command line arguments
def get_settings_from_command_line_args():
    parser = argparse.ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--gui', help='Launch the GUI', action='store_true')
    parser.add_argument('--loglevel', default='info', const='info', nargs='?', choices=['error', 'info', 'warning', 'debug'], help='Select level of logging for output.')
    parser.add_argument('--settings_string', help='Provide sharable settings using a settings string. This will override all flags that it specifies.')
    parser.add_argument('--convert_settings', help='Only convert the specified settings to a settings string. If a settings string is specified output the used settings instead.', action='store_true')
    parser.add_argument('--settings', help='Use the specified settings file to use for generation')
    parser.add_argument('--seed', help='Generate the specified seed.')

    args = parser.parse_args()

    if args.settings is None:
        settingsFile = local_path('settings.sav')
    else:
        settingsFile = local_path(args.settings)

    try:
        with open(settingsFile) as f:
            settings = Settings(json.load(f))
    except Exception as ex:
        if args.settings is None:
            settings = Settings({})
        else:
            raise ex

    if args.settings_string is not None:
        settings.update_with_settings_string(args.settings_string)

    if args.seed is not None:
        settings.update_seed(args.seed)

    if args.convert_settings:
        if args.settings_string is not None:
            print(settings.get_settings_display())
        else:
            print(settings.get_settings_string())
        sys.exit(0)
        
    return settings, args.gui, args.loglevel
