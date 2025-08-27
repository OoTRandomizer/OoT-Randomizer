#!/usr/bin/env python3
import sys
if sys.version_info < (3, 9):
    print("OoT Randomizer requires Python version 3.9 or newer and you are using %s" % '.'.join([str(i) for i in sys.version_info[0:3]]))
    # raw_input was renamed to input in 3.0, handle both 2.x and 3.x by trying the rename for 2.x
    try:
        input = raw_input
    except NameError:
        pass
    input("Press enter to exit...")
    sys.exit(1)

import os
import platform
import shutil
import subprocess
import venv
import webbrowser

from SettingsToJson import create_settings_list_json
from Utils import local_path, data_path, compare_version, VersionError


VENV_DIR = os.path.join(os.path.dirname(__file__), ".venv")
PYTHON_BIN = os.path.abspath(os.path.join(VENV_DIR, "bin", "python3"))
if platform.system() == 'Windows':
    PYTHON_BIN = os.path.abspath(os.path.join(VENV_DIR, "Scripts", "python"))
REQUIREMENTS = os.path.join(os.path.dirname(__file__), "requirements.txt")


def ensure_venv():
    # If venv doesn’t exist, create it
    if not os.path.exists(PYTHON_BIN):
        print("Creating virtual environment...")
        venv.create(VENV_DIR, with_pip=True)
        subprocess.check_call([PYTHON_BIN, "-m", "pip", "install", "-r", REQUIREMENTS])

    # If we're not already running inside the venv, restart with it
    if sys.executable != PYTHON_BIN:
        print('Re-launching in virtual environment')
        subprocess.check_call([PYTHON_BIN] + sys.argv)
        sys.exit(0)


def gui_main() -> None:
    # Make sure we're running in a virtual environment with
    # required dependencies. Install and relaunch if we are not.
    ensure_venv()

    try:
        version_check("Node", "14.15.0", "https://nodejs.org/en/download/")
        version_check("NPM", "6.12.0", "https://nodejs.org/en/download/")
    except VersionError as ex:
        print(ex.args[0])
        webbrowser.open(ex.args[1])
        return

    web_version = '--web' in sys.argv
    if '--skip-settingslist' not in sys.argv:
        create_settings_list_json(data_path('generated/settings_list.json'), web_version)

    if web_version:
        args = ["node", "run.js", "web"]
    else:
        args = ["node", "run.js", "release", "python", sys.executable]
    subprocess.run(args, shell=False, cwd=local_path("GUI"), check=True)


def version_check(name: str, version: str, url: str) -> None:
    try:
        process = subprocess.Popen([shutil.which(name.lower()), "--version"], stdout=subprocess.PIPE)
    except Exception as ex:
        raise VersionError('{name} is not installed. Please install {name} {version} or later'.format(name=name, version=version), url)

    while True:
        line = str(process.stdout.readline().strip(), 'UTF-8')
        if line == '':
            break
        if compare_version(line, version) < 0:
            raise VersionError('{name} {version} or later is required but you are using {line}'.format(name=name, version=version, line=line), url)
        print('Using {name} {line}'.format(name=name, line=line))


if __name__ == '__main__':
    gui_main()
