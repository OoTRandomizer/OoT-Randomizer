# This script is called by GitHub Actions, see .github/workflows/python.yml
# To fix code style errors, run: python3 ./CI.py --fix --no_unit_tests

import argparse
import json
import os.path
import pathlib
import sys
import unittest
from io import StringIO
from typing import NoReturn


import Unittest as Tests
from SettingsList import SettingInfos, logic_tricks, validate_settings
from Utils import data_path


def error(msg: str, can_fix: bool) -> None:
    if not hasattr(error, "count"):
        error.count = 0
    print(msg, file=sys.stderr)
    error.count += 1
    if can_fix:
        error.can_fix = True
    else:
        error.cannot_fix = True


def run_unit_tests() -> None:
    # Run Unit Tests
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    suite = unittest.defaultTestLoader.loadTestsFromModule(Tests)
    result = runner.run(suite)
    print(f'Tests run: {result.testsRun}.')
    stream.seek(0)
    print(f'Test output:\n{stream.read()}')
    if not result.wasSuccessful():
        error('Unit Tests had an error, see output above.', False)


def check_presets_formatting(fix_errors: bool = False) -> None:
    # Check the code style of presets_default.json
    with open(data_path('presets_default.json'), encoding='utf-8') as f:
        presets = json.load(f)

    any_errors = False
    for preset_name, preset in presets.items():
        try:
            validate_settings(preset, check_conflicts=False)
        except Exception as e:
            error(f'Error in {preset_name} preset: {e}', False)
        for setting_name, setting in SettingInfos.setting_infos.items():
            if setting_name != 'starting_items' and setting.shared and setting_name not in preset:
                error(f'Missing setting {setting_name} in {preset_name} preset', False)
                any_errors = True
    if any_errors:
        return

    with open(data_path('presets_default.json'), encoding='utf-8') as f:
        presets_str = f.read()

    if presets_str != json.dumps(presets, indent=4) + '\n':
        error('presets not formatted correctly', True)
        if fix_errors:
            with open(data_path('presets_default.json'), 'w', encoding='utf-8', newline='') as file:
                json.dump(presets, file, indent=4)
                print(file=file)
        else:
            return

    presets = {
        preset_name: {
            # sort the settings within each preset
            setting_name: preset[setting_name]
            for setting_name, setting in SettingInfos.setting_infos.items()
            if setting_name != 'starting_items' and setting.shared and setting_name in preset
        }
        for preset_name, preset in presets.items()
    }

    if presets_str != json.dumps(presets, indent=4) + '\n':
        error('presets not sorted correctly', True)
        if fix_errors:
            with open(data_path('presets_default.json'), 'w', encoding='utf-8', newline='') as file:
                json.dump(presets, file, indent=4)
                print(file=file)


def check_hell_mode_tricks(fix_errors: bool = False) -> None:
    # Check for tricks missing from Hell Mode preset.
    with open(data_path('presets_default.json'), encoding='utf-8') as f:
        presets = json.load(f)

    for trick in logic_tricks.values():
        if trick['name'] not in presets['Hell Mode']['allowed_tricks']:
            error(f'Logic trick {trick["name"]!r} missing from Hell Mode preset.', True)

    if set(presets['Hell Mode']['allowed_tricks']) == {trick['name'] for trick in logic_tricks.values()}:
        if presets['Hell Mode']['allowed_tricks'] != [trick['name'] for trick in logic_tricks.values()]:
            error(f'Order of logic tricks in Hell Mode preset does not match definition order in SettingsList.py', True)

    if fix_errors:
        presets['Hell Mode']['allowed_tricks'] = [trick['name'] for trick in logic_tricks.values()]
        with open(data_path('presets_default.json'), 'w', encoding='utf-8', newline='') as file:
            json.dump(presets, file, indent=4)
            print(file=file)


def check_code_style(fix_errors: bool = False) -> None:
    # Check for code style errors
    repo_dir = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))

    def check_file_format(path: pathlib.Path, *, allow_trailing_spaces: bool = False):
        fixed = ''
        empty_lines = 0
        with path.open(encoding='utf-8', newline='') as file:
            path = path.relative_to(repo_dir)
            for i, line in enumerate(file, start=1):
                if not line.endswith('\n'):
                    error(f'Missing line break at end of {path}', True)
                    line += '\n'
                line = line.rstrip('\n')
                if line:
                    empty_lines = 0
                else:
                    empty_lines += 1
                if '\t' in line:
                    error(f'Hard tab on line {i} of {path}', True)
                    fixed_line = ''
                    for c in line:
                        if c == '\t':
                            fixed_line += ' ' * (4 - len(fixed_line) % 4)
                        else:
                            fixed_line += c
                    line = fixed_line
                if line.endswith(' ') and not allow_trailing_spaces:
                    error(f'Trailing whitespace on line {i} of {path}', True)
                    line = line.rstrip(' ')
                fixed += line + '\n'
        if empty_lines > 0:
            error(f'Multiple trailing newlines at end of {path}', True)
            fixed = fixed.rstrip('\n') + '\n'
        if fix_errors:
            with path.open('w', encoding='utf-8', newline='') as file:
                file.write(fixed)

    for path in repo_dir.iterdir():
        if path.suffix == '.py':
            check_file_format(path)
    for path in (repo_dir / 'ASM').iterdir():
        if path.suffix == '.py':
            check_file_format(path)
    for path in (repo_dir / 'ASM' / 'c').iterdir():
        if path.suffix in ('.c', '.h'):
            check_file_format(path)
    for path in (repo_dir / 'ASM' / 'src').iterdir():
        if path.suffix == '.asm':
            check_file_format(path)
    for subdir in ('Glitched World', 'Hints', 'World'):
        for path in (repo_dir / 'data' / subdir).iterdir():
            if path.suffix == '.json':
                check_file_format(path)
    for path in (repo_dir / 'Notes').iterdir():
        if path.suffix == '.md':
            # In Markdown, 2 trailing spaces indicate a hard line break.
            check_file_format(path, allow_trailing_spaces=True)
    check_file_format(repo_dir / 'data' / 'LogicHelpers.json')
    check_file_format(repo_dir / 'data' / 'presets_default.json')
    check_file_format(repo_dir / 'data' / 'settings_mapping.json')


def run_ci_checks() -> NoReturn:
    parser = argparse.ArgumentParser()
    parser.add_argument('--no_unit_tests', help="Skip unit tests", action='store_true')
    parser.add_argument('--only_unit_tests', help="Only run unit tests", action='store_true')
    parser.add_argument('--fix', help='Automatically apply fixes where possible', action='store_true')
    args = parser.parse_args()

    if not args.no_unit_tests:
        run_unit_tests()

    if not args.only_unit_tests:
        check_hell_mode_tricks(args.fix)
        check_code_style(args.fix)
        check_presets_formatting(args.fix)

    exit_ci(args.fix)


def exit_ci(fix_errors: bool = False) -> NoReturn:
    if hasattr(error, "count") and error.count:
        print(f'CI failed with {error.count} errors.', file=sys.stderr)
        if fix_errors:
            if getattr(error, 'cannot_fix', False):
                print('Some errors could not be fixed automatically.', file=sys.stderr)
                sys.exit(1)
            else:
                print('All errors fixed.', file=sys.stderr)
                sys.exit(0)
        else:
            if getattr(error, 'can_fix', False):
                if getattr(error, 'cannot_fix', False):
                    print('Run `CI.py --fix --no_unit_tests` to automatically fix some of these errors.', file=sys.stderr)
                else:
                    print('Run `CI.py --fix --no_unit_tests` to automatically fix these errors.', file=sys.stderr)
            sys.exit(1)
    else:
        print(f'CI checks successful.')
        sys.exit(0)


if __name__ == '__main__':
    run_ci_checks()
