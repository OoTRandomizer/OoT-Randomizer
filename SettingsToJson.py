#!/usr/bin/env python3
from __future__ import annotations
import copy
import json
import sys
from typing import Any, Optional

from Hints import hint_dist_files
from SettingsList import SettingInfos, get_settings_from_section, get_settings_from_tab
from Utils import data_path


tab_keys: list[str] = ['text', 'app_type', 'footer']
section_keys: list[str] = ['text', 'app_type', 'is_colors', 'is_sfx', 'col_span', 'row_span', 'subheader']
setting_keys: list[str] = ['hide_when_disabled', 'min', 'max', 'size', 'max_length', 'file_types', 'no_line_break', 'function', 'option_remove', 'dynamic']
types_with_options: list[str] = ['Checkbutton', 'Radiobutton', 'Combobox', 'SearchBox', 'MultipleSelect']


def remove_trailing_lines(text: str) -> str:
    while text.endswith('<br>'):
        text = text[:-4]
    while text.startswith('<br>'):
        text = text[4:]
    return text


def deep_update(source: dict, new_dict: dict) -> dict:
    for k, v in new_dict.items():
        if isinstance(v, dict):
            source[k] = deep_update(source.get(k, { }), v)
        elif isinstance(v, list):
            source[k] = (source.get(k, []) + v)
        else:
            source[k] = v
    return source


def add_disable_option_to_json(disable_option: dict[str, Any], option_json: dict[str, Any]) -> None:
    if disable_option.get('settings') is not None:
        if 'controls_visibility_setting' not in option_json:
            option_json['controls_visibility_setting'] = ','.join(disable_option['settings'])
        else:
            option_json['controls_visibility_setting'] += ',' + ','.join(disable_option['settings'])
    if disable_option.get('sections') is not None:
        if 'controls_visibility_section' not in option_json:
            option_json['controls_visibility_section'] = ','.join(disable_option['sections'])
        else:
            option_json['controls_visibility_section'] += ',' + ','.join(disable_option['sections'])
    if disable_option.get('tabs') is not None:
        if 'controls_visibility_tab' not in option_json:
            option_json['controls_visibility_tab'] = ','.join(disable_option['tabs'])
        else:
            option_json['controls_visibility_tab'] += ',' + ','.join(disable_option['tabs'])


def get_setting_json(setting: str, web_version: bool, as_array: bool = False) -> Optional[dict[str, Any]]:
    try:
        setting_info = SettingInfos.setting_infos[setting]
    except KeyError:
        if as_array:
            return {'name': setting}
        else:
            return {}

    if setting_info.gui_text is None:
        return None

    setting_json: dict[str, Any] = {
        'options':       [],
        'default':       setting_info.default,
        'text':          setting_info.gui_text,
        'tooltip': remove_trailing_lines('<br>'.join(line.strip() for line in setting_info.gui_tooltip.split('\n'))),
        'type':          setting_info.gui_type,
        'shared':        setting_info.shared,
    }

    if as_array:
        setting_json['name'] = setting_info.name
    else:
        setting_json['current_value'] = setting_info.default

    setting_disable = {}
    if setting_info.disable is not None:
        setting_disable = copy.deepcopy(setting_info.disable)

    version_specific_keys = []

    for key, value in setting_info.gui_params.items():
        version_specific = False
        if key.startswith('web:'):
            if web_version:
                key = key[4:]
                version_specific_keys.append(key)
                version_specific = True
            else:
                continue
        if key.startswith('electron:'):
            if not web_version:
                key = key[9:]
                version_specific_keys.append(key)
                version_specific = True
            else:
                continue

        if key in setting_keys and (key not in version_specific_keys or version_specific):
            setting_json[key] = value
        if key == 'disable':
            for option, types in value.items():
                for s in types.get('settings', []):
                    if SettingInfos.setting_infos[s].shared:
                        raise ValueError(f'Cannot disable setting {s}. Disabling "shared" settings in the gui_params is forbidden. Use the non gui_param version of disable instead.')
                for section in types.get('sections', []):
                    for s in get_settings_from_section(section):
                        if SettingInfos.setting_infos[s].shared:
                            raise ValueError(f'Cannot disable setting {s} in {section}. Disabling "shared" settings in the gui_params is forbidden. Use the non gui_param version of disable instead.')
                for tab in types.get('tabs', []):
                    for s in get_settings_from_tab(tab):
                        if SettingInfos.setting_infos[s].shared:
                            raise ValueError(f'Cannot disable setting {s} in {tab}. Disabling "shared" settings in the gui_params is forbidden. Use the non gui_param version of disable instead.')
            deep_update(setting_disable, value)

    if setting_json['type'] in types_with_options:
        if as_array:
            setting_json['options'] = []
        else:
            setting_json['options'] = {}

        tags_list = []

        for option_name in setting_info.choice_list:
            if option_name in setting_json.get('option_remove', []):
                continue

            if as_array:
                option_json = {
                    'name':     option_name,
                    'text':     setting_info.choices[option_name],
                }
            else:
                option_json = {
                    'text':     setting_info.choices[option_name],
                }

            if option_name in setting_disable:
                add_disable_option_to_json(setting_disable[option_name], option_json)

            option_tooltip = setting_info.gui_params.get('choice_tooltip', {}).get(option_name, None)
            if option_tooltip is not None:
                option_json['tooltip'] = remove_trailing_lines(
                    '<br>'.join(line.strip() for line in option_tooltip.split('\n')))

            option_filter = setting_info.gui_params.get('filterdata', {}).get(option_name, None)
            if option_filter is not None:
                option_json['tags'] = option_filter
                for tag in option_filter:
                    if tag not in tags_list:
                        tags_list.append(tag)

            if as_array:
                setting_json['options'].append(option_json)
            else:
                setting_json['options'][option_name] = option_json

        # For disables with '!', add disable settings to all options other than the one marked.
        for option_name in setting_disable:
            if isinstance(option_name, str) and option_name[0] == '!':
                if as_array:
                    for option in setting_json['options']:
                        if option['name'] != option_name[1:]:
                            add_disable_option_to_json(setting_disable[option_name], option)
                else:
                    for name, option in setting_json['options'].items():
                        if name != option_name[1:]:
                            add_disable_option_to_json(setting_disable[option_name], option)

        if tags_list:
            tags_list.sort()
            setting_json['tags'] = ['(all)'] + tags_list
            setting_json['filter_by_tag'] = True

    return setting_json


def get_section_json(section: dict[str, Any], web_version: bool, as_array: bool = False) -> dict[str, Any]:
    if as_array:
        section_json = {
            'name'     : section['name'],
            'settings' : []
        }
    else:
        section_json = {
            'settings' : {}
        }

    for key, value in section.items():
        if key in section_keys:
            section_json[key] = value

    for setting in section['settings']:
        setting_json = get_setting_json(setting, web_version, as_array)
        if as_array:
            section_json['settings'].append(setting_json)
        else:
            section_json['settings'][setting] = setting_json

    return section_json


def get_tab_json(tab: dict[str, Any], web_version: bool, as_array: bool = False) -> dict[str, Any]:
    if as_array:
        tab_json = {
            'name'     : tab['name'],
            'sections' : []
        }
    else:
        tab_json = {
            'sections' : {}
        }

    for key, value in tab.items():
        if key in tab_keys:
            tab_json[key] = value

    for section in tab['sections']:
        section_json = get_section_json(section, web_version, as_array)
        if section.get('exclude_from_web', False) and web_version:
            continue
        elif section.get('exclude_from_electron', False) and not web_version:
            continue

        if as_array:
            tab_json['sections'].append(section_json)
        else:
            tab_json['sections'][section['name']] = section_json

    return tab_json


def create_settings_list_json(path: str, web_version: bool = False) -> None:
    output_json = {
        'settingsObj'   : {},
        'settingsArray' : [],
        'cosmeticsObj'  : {},
        'cosmeticsArray': [],
        'distroArray'   : [],
    }

    for tab in SettingInfos.setting_map['Tabs']:
        if tab.get('exclude_from_web', False) and web_version:
            continue
        elif tab.get('exclude_from_electron', False) and not web_version:
            continue

        tab_json_object = get_tab_json(tab, web_version, as_array=False)
        tab_json_array = get_tab_json(tab, web_version, as_array=True)

        output_json['settingsObj'][tab['name']] = tab_json_object
        output_json['settingsArray'].append(tab_json_array)
        if tab.get('is_cosmetics', False):
            output_json['cosmeticsObj'][tab['name']] = tab_json_object
            output_json['cosmeticsArray'].append(tab_json_array)

    for d in hint_dist_files():
        with open(d, 'r') as dist_file:
            dist = json.load(dist_file)
        if ('distribution' in dist and
           'goal' in dist['distribution'] and
           (dist['distribution']['goal']['fixed'] != 0 or
                dist['distribution']['goal']['weight'] != 0)):
            output_json['distroArray'].append(dist['name'])

    with open(path, 'w') as f:
        json.dump(output_json, f)


def get_setting_details(setting_key: str, web_version: bool) -> None:
    setting_json_object = get_setting_json(setting_key, web_version, as_array=False)
    setting_json_array = get_setting_json(setting_key, web_version, as_array=True)

    setting_output = {"object": setting_json_object, "array": setting_json_array}
    print(json.dumps(setting_output))


def main() -> None:
    args = sys.argv[1:]
    web_version = '--web' in args

    if '--setting' in args:
        arg_index = args.index('--setting') + 1
        if len(args) < arg_index:
            raise Exception("Usage: SettingsToJson.py --setting <setting_key>")
        return get_setting_details(args[arg_index], web_version)

    create_settings_list_json(data_path('generated/settings_list.json'), web_version)


if __name__ == '__main__':
    main()
