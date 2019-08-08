import argparse
import textwrap
import string
import re
import hashlib
import math
import sys
import json
import logging

from version import __version__
from Utils import random_choices, local_path
from SettingsList import setting_infos, get_setting_info
from Plandomizer import Distribution

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
class Settings:

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
                try:
                    index = setting.choice_list.index(value)
                except ValueError:
                    index = setting.choice_list.index(setting.default)
                # https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
                i_bits = [1 if digit=='1' else 0 for digit in bin(index)[2:]]
                i_bits.reverse()
            if setting.type == int:
                value = int(value)
                value = value - (setting.gui_params.get('min', 0))
                value = int(value / (setting.gui_params.get('step', 1)))
                value = min(value, (setting.gui_params.get('max', value)))
                # https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
                i_bits = [1 if digit=='1' else 0 for digit in bin(value)[2:]]
                i_bits.reverse()
            if setting.type == list:
                if len(value) > len(setting.choice_list) / 2:
                    value = [item for item in setting.choice_list if item not in value]
                    terminal = [1] * setting.bitwidth
                else:
                    terminal = [0] * setting.bitwidth

                item_indexes = []
                for item in value:                       
                    try:
                        item_indexes.append(setting.choice_list.index(item))
                    except ValueError:
                        continue
                item_indexes.sort()
                for index in item_indexes:
                    item_bits = [1 if digit=='1' else 0 for digit in bin(index+1)[2:]]
                    item_bits.reverse()
                    item_bits += [0] * ( setting.bitwidth - len(item_bits) )
                    i_bits.extend(item_bits)
                i_bits.extend(terminal)

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
                value = setting.choice_list[index]
            if setting.type == int:
                value = 0
                for b in range(setting.bitwidth):
                    value |= cur_bits[b] << b
                value = value * setting.gui_params.get('step', 1)
                value = value + setting.gui_params.get('min', 0)
            if setting.type == list:
                value = []
                max_index = (1 << setting.bitwidth) - 1
                while True:
                    index = 0
                    for b in range(setting.bitwidth):
                        index |= cur_bits[b] << b

                    if index == 0:
                        break
                    if index == max_index:
                        value = [item for item in setting.choice_list if item not in value]
                        break

                    value.append(setting.choice_list[index-1])
                    cur_bits = bits[:setting.bitwidth]
                    bits = bits[setting.bitwidth:]

            self.__dict__[setting.name] = value

        self.settings_string = self.get_settings_string()
        self.numeric_seed = self.get_numeric_seed()


    def get_numeric_seed(self):
        # salt seed with the settings, and hash to get a numeric seed
        distribution = json.dumps(self.distribution.to_json(include_output=False), sort_keys=True)
        full_string = self.settings_string + distribution + __version__ + self.seed
        return int(hashlib.sha256(full_string.encode('utf-8')).hexdigest(), 16)


    def sanitize_seed(self):
        # leave only alphanumeric and some punctuation
        self.seed = re.sub(r'[^a-zA-Z0-9_-]', '', self.seed, re.UNICODE)


    def update_seed(self, seed):
        if seed is None or seed == '':
            # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
            self.seed = ''.join(random_choices(string.ascii_uppercase + string.digits, k=10))
        else:
            self.seed = seed
        self.sanitize_seed()
        self.numeric_seed = self.get_numeric_seed()


    def update(self):
        self.settings_string = self.get_settings_string()
        self.numeric_seed = self.get_numeric_seed()

    def load_distribution(self):
        if self.distribution_file is not None and self.distribution_file != '':
            try:
                self.distribution = Distribution.from_file(self, self.distribution_file)
            except FileNotFoundError:
                logging.getLogger('').warning("Distribution file not found at %s" % (self.distribution_file))
        else:
            self.distribution = Distribution(self)

        for location in self.disabled_locations:
            self.distribution.add_location(location, '#Junk')

        self.numeric_seed = self.get_numeric_seed()

    def check_dependency(self, setting_name, check_random=True):
        return self.get_dependency(setting_name, check_random) == None


    def get_dependency(self, setting_name, check_random=True):
        info = get_setting_info(setting_name)
        if check_random and 'randomize_key' in info.gui_params and self.__dict__[info.gui_params['randomize_key']]:
            return info.disabled_default
        elif info.dependency != None:
            return info.disabled_default if info.dependency(self) else None
        else:
            return None


    def remove_disabled(self):
        for info in setting_infos:
            if info.dependency != None:
                new_value = self.get_dependency(info.name)
                if new_value != None:
                    self.__dict__[info.name] = new_value

        self.settings_string = self.get_settings_string()
        self.numeric_seed = self.get_numeric_seed()


    def resolve_random_settings(self):
        sorted_infos = list(setting_infos)
        sort_key = lambda info: 0 if info.dependency is None else 1
        sorted_infos.sort(key=sort_key)

        for info in sorted_infos:
            if not self.check_dependency(info.name, check_random=False):
                continue

            if 'randomize_key' in info.gui_params and self.__dict__[info.gui_params['randomize_key']]:               
                choices, weights = zip(*info.gui_params['distribution'])
                self.__dict__[info.name] = random_choices(choices, weights=weights)[0]


    # add the settings as fields, and calculate information based on them
    def __init__(self, settings_dict):
        self.__dict__.update(settings_dict)
        for info in setting_infos:
            if info.name not in self.__dict__:
                self.__dict__[info.name] = info.default

        if self.world_count < 1:
            self.world_count = 1
        if self.world_count > 255:
            self.world_count = 255

        self.settings_string = self.get_settings_string()
        self.distribution = Distribution(self)
        self.update_seed(self.seed)


    def to_json(self):
        return {setting.name: self.__dict__[setting.name] for setting in setting_infos if setting.shared}


# gets the randomizer settings, whether to open the gui, and the logger level from command line arguments
def get_settings_from_command_line_args():
    parser = argparse.ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--gui', help='Launch the GUI', action='store_true')
    parser.add_argument('--loglevel', default='info', const='info', nargs='?', choices=['error', 'info', 'warning', 'debug'], help='Select level of logging for output.')
    parser.add_argument('--settings_string', help='Provide sharable settings using a settings string. This will override all flags that it specifies.')
    parser.add_argument('--convert_settings', help='Only convert the specified settings to a settings string. If a settings string is specified output the used settings instead.', action='store_true')
    parser.add_argument('--settings', help='Use the specified settings file to use for generation')
    parser.add_argument('--seed', help='Generate the specified seed.')
    parser.add_argument('--no_log', help='Suppresses the generation of a log file.', action='store_true')

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
            print(json.dumps(settings.to_json()))
        else:
            print(settings.get_settings_string())
        sys.exit(0)
        
    return settings, args.gui, args.loglevel, args.no_log
