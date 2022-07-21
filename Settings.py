import argparse
import hashlib
import json
import logging
import os
import re
import string
import sys
import textwrap

from version import __version__
from Utils import random_choices, local_path, data_path
from SettingsList import setting_infos, get_setting_info, validate_settings
from Plandomizer import Distribution
import StartingItems

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


def get_preset_files():
    return [data_path('presets_default.json')] + sorted(
            os.path.join(data_path('Presets'), fn)
            for fn in os.listdir(data_path('Presets'))
            if fn.endswith('.json'))


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
            if setting.name in ('starting_equipment', 'starting_items', 'starting_songs'):
                items = {'starting_equipment': StartingItems.equipment, 'starting_items': StartingItems.inventory, 'starting_songs': StartingItems.songs}[setting.name]
                value = []
                for entry in items.values():
                    if entry.itemname in self.starting_items:
                        count = self.starting_items[entry.itemname]
                        if not isinstance(count, int):
                            count = count.count
                        if count > entry.i:
                            value.append(entry.settingname)
            if setting.type == bool:
                i_bits = [ 1 if value else 0 ]
            elif setting.type == str:
                try:
                    index = setting.choice_list.index(value)
                except ValueError:
                    index = setting.choice_list.index(setting.default)
                # https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
                i_bits = [1 if digit=='1' else 0 for digit in bin(index)[2:]]
                i_bits.reverse()
            elif setting.type == int:
                value = int(value)
                value = value - (setting.gui_params.get('min', 0))
                value = int(value / (setting.gui_params.get('step', 1)))
                value = min(value, (setting.gui_params.get('max', value)))
                # https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
                i_bits = [1 if digit=='1' else 0 for digit in bin(value)[2:]]
                i_bits.reverse()
            elif setting.type == list:
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
            else:
                raise TypeError(f'Cannot encode type {setting.type} into settings string')

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
            elif setting.type == str:
                index = 0
                for b in range(setting.bitwidth):
                    index |= cur_bits[b] << b
                value = setting.choice_list[index]
            elif setting.type == int:
                value = 0
                for b in range(setting.bitwidth):
                    value |= cur_bits[b] << b
                value = value * setting.gui_params.get('step', 1)
                value = value + setting.gui_params.get('min', 0)
            elif setting.type == list:
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
            else:
                raise TypeError(f'Cannot decode type {setting.type} from settings string')

            self.__dict__[setting.name] = value

        self.distribution.reset() # convert starting_items
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
        if self.enable_distribution_file:
            if self.distribution_file:
                try:
                    self.distribution = Distribution.from_file(self, self.distribution_file)
                except FileNotFoundError:
                    logging.getLogger('').warning("Distribution file not found at %s" % (self.distribution_file))
                    self.enable_distribution_file = False
            else:
                logging.getLogger('').warning("Plandomizer enabled, but no distribution file provided.")
                self.enable_distribution_file = False
        elif self.distribution_file:
            logging.getLogger('').warning("Distribution file provided, but using it not enabled. "
                    "Did you mean to set enable_distribution_file?")
        else:
            self.distribution = Distribution(self)

        self.reset_distribution()

        self.numeric_seed = self.get_numeric_seed()


    def reset_distribution(self):
        self.distribution.reset()

        for location in self.disabled_locations:
            self.distribution.add_location(location, '#Junk')


    def check_dependency(self, setting_name, check_random=True):
        return self.get_dependency(setting_name, check_random) == None


    def get_dependency(self, setting_name, check_random=True):
        info = get_setting_info(setting_name)
        not_in_dist = '_settings' not in self.distribution.src_dict or info.name not in self.distribution.src_dict['_settings'].keys()
        if check_random and 'randomize_key' in info.gui_params and self.__dict__[info.gui_params['randomize_key']] and not_in_dist:
            return info.disabled_default
        elif info.dependency != None:
            return info.disabled_default if info.dependency(self) and not_in_dist else None
        else:
            return None


    def remove_disabled(self):
        for info in setting_infos:
            if info.dependency != None:
                new_value = self.get_dependency(info.name)
                if new_value != None:
                    self.__dict__[info.name] = new_value
                    self._disabled.add(info.name)

        self.settings_string = self.get_settings_string()
        self.numeric_seed = self.get_numeric_seed()


    def resolve_random_settings(self, cosmetic, randomize_key=None):
        sorted_infos = list(setting_infos)
        sort_key = lambda info: 0 if info.dependency is None else 1
        sorted_infos.sort(key=sort_key)
        randomize_keys_enabled = set()

        for info in sorted_infos:
            # only randomize cosmetics options or non-cosmetic
            if cosmetic == info.shared:
                continue

            if self.check_dependency(info.name, check_random=True):
                continue

            if 'randomize_key' not in info.gui_params:
                continue

            if randomize_key is not None and info.gui_params['randomize_key'] != randomize_key:
                continue

            # Make sure the setting is meant to be randomized and not specified in distribution
            # We that check it's not specified in the distribution so that plando can override randomized settings
            not_in_dist = '_settings' not in self.distribution.src_dict or info.name not in self.distribution.src_dict['_settings'].keys()
            if self.__dict__[info.gui_params['randomize_key']] and not_in_dist:
                randomize_keys_enabled.add(info.gui_params['randomize_key'])
                choices, weights = zip(*info.gui_params['distribution'])
                self.__dict__[info.name] = random_choices(choices, weights=weights)[0]

        # Second pass to make sure disabled settings are set properly.
        # Stupid hack: disable randomize keys, then re-enable.
        for randomize_keys in randomize_keys_enabled:
            self.__dict__[randomize_keys] = False
        for info in sorted_infos:
            if cosmetic == info.shared:
                continue
            dependency = self.get_dependency(info.name, check_random=False)
            if dependency is None:
                continue
            self.__dict__[info.name] = dependency
        for randomize_keys in randomize_keys_enabled:
            self.__dict__[randomize_keys] = True


    # add the settings as fields, and calculate information based on them
    def __init__(self, settings_dict, strict=False):
        if settings_dict.get('compress_rom', None):
            # Old compress_rom setting is set, so set the individual output settings using it.
            settings_dict['create_patch_file'] = settings_dict['compress_rom'] == 'Patch' or settings_dict.get('create_patch_file', False)
            settings_dict['create_compressed_rom'] = settings_dict['compress_rom'] == 'True' or settings_dict.get('create_compressed_rom', False)
            settings_dict['create_uncompressed_rom'] = settings_dict['compress_rom'] == 'False' or settings_dict.get('create_uncompressed_rom', False)
            del settings_dict['compress_rom']
        if strict:
            validate_settings(settings_dict)
        self.__dict__.update(settings_dict)
        for info in setting_infos:
            if info.name not in self.__dict__:
                self.__dict__[info.name] = info.default

        if self.world_count < 1:
            self.world_count = 1
        if self.world_count > 255:
            self.world_count = 255

        self._disabled = set()
        self.settings_string = self.get_settings_string()
        self.distribution = Distribution(self)
        self.update_seed(self.seed)
        self.custom_seed = False


    def to_json(self):
        return {
            setting.name: (
                {name: (
                    {name: record.to_json() for name, record in record.items()} if isinstance(record, dict) else record.to_json()
                ) for name, record in self.__dict__[setting.name].items()}
                if setting.name == 'starting_items' else
                self.__dict__[setting.name]
            )
            for setting in setting_infos
            if setting.shared and (
                setting.name not in self._disabled or
                # We want to still include settings disabled by randomized settings options if they're specified in distribution
                ('_settings' in self.distribution.src_dict and setting.name in self.distribution.src_dict['_settings'].keys())
            )
            # Don't want to include list starting equipment and songs, these are consolidated into starting_items
            and not (setting.name == "starting_equipment" or setting.name == "starting_songs")
        }

    def to_json_cosmetics(self):
        return {setting.name: self.__dict__[setting.name] for setting in setting_infos if setting.cosmetic}


# gets the randomizer settings, whether to open the gui, and the logger level from command line arguments
def get_settings_from_command_line_args():
    parser = argparse.ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--gui', help='Launch the GUI', action='store_true')
    parser.add_argument('--loglevel', default='info', const='info', nargs='?', choices=['error', 'info', 'warning', 'debug'], help='Select level of logging for output.')
    parser.add_argument('--settings_string', help='Provide sharable settings using a settings string. This will override all flags that it specifies.')
    parser.add_argument('--convert_settings', help='Only convert the specified settings to a settings string. If a settings string is specified output the used settings instead.', action='store_true')
    parser.add_argument('--settings', help='Use the specified settings file to use for generation')
    parser.add_argument('--settings_preset', help="Use the given preset for base settings. Anything defined in the --settings file or the --settings_string will override the preset.")
    parser.add_argument('--seed', help='Generate the specified seed.')
    parser.add_argument('--no_log', help='Suppresses the generation of a log file.', action='store_true')
    parser.add_argument('--output_settings', help='Always outputs a settings.json file even when spoiler is enabled.', action='store_true')
    parser.add_argument('--diff_rom', help='Generates a ZPF patch from the specified ROM file.')

    args = parser.parse_args()
    settings_base = {}
    if args.settings_preset:
        presetsFiles = get_preset_files()
        for fn in presetsFiles:
            with open(fn, encoding='utf-8') as f:
                presets = json.load(f)
                if args.settings_preset in presets:
                    settings_base.update(presets[args.settings_preset])
                    break
        else:
            sys.stderr.write(f'ERROR:No preset found with name {args.settings_preset!r}\n')
            sys.exit(1)

    if args.settings == '-':
        settings_base.update(json.loads(sys.stdin.read()))
    elif args.settings or not settings_base:  # avoid implicitly using settings.sav with presets
        settingsFile = local_path(args.settings or 'settings.sav')

        try:
            with open(settingsFile, encoding='utf-8') as f:
                settings_base.update(json.load(f))
        except Exception as ex:
            if args.settings is not None:
                raise ex

    settings = Settings(settings_base)

    settings.output_settings = args.output_settings

    if args.settings_string is not None:
        settings.update_with_settings_string(args.settings_string)

    if args.seed is not None:
        settings.update_seed(args.seed)
        settings.custom_seed = True

    if args.convert_settings:
        if args.settings_string is not None:
            print(json.dumps(settings.to_json()))
        else:
            print(settings.get_settings_string())
        sys.exit(0)

    return settings, args.gui, args.loglevel, args.no_log, args.diff_rom
