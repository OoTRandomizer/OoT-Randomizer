#!/usr/bin/env python3
import platform
import sys
if sys.version_info < (3, 8):
    print("OoT Randomizer requires Python version 3.8 or newer and you are using %s" % '.'.join([str(i) for i in sys.version_info[0:3]]))
    # raw_input was renamed to input in 3.0, handle both 2.x and 3.x by trying the rename for 2.x
    try:
        input = raw_input
    except NameError:
        pass
    input("Press enter to exit...")
    sys.exit(1)

import shutil
import subprocess
import webbrowser
import os
import venv


from SettingsToJson import create_settings_list_json
from Utils import local_path, data_path, compare_version, VersionError


def gui_main() -> None:

    python_path = sys.executable
    # Get python virtual environment
    # Make it if it doesn't exist

    print("Checking for python virtual environment")
    try:
        if os.path.exists(".venv"):
            print("Found python virtual environment")
            # Looks like venv exists so just set the python path
            pass
        else:
            # Virtual environment doesn't exist so create it
            print("No virtual environment found. Creating...")
            venv.create(".venv", system_site_packages=False, clear=True, symlinks=False, with_pip=True)
        if platform.system() == "Windows":
            subdir = "Scripts"
            exename = "python.exe"
        else:
            subdir = "bin"
            exename = "python3"
        args = [os.path.join(".venv", subdir, "pip"), "install", "-r", "requirements.txt"]
        print("Installing any missing packages")
        subprocess.run(args, check=True)
        # Get platform dependent path to python
        python_path = os.path.abspath(os.path.join(os.curdir, ".venv", subdir, exename))
    except Exception as err:
        print(f"Could not create python virtual environment, defaulting to global python interpreter {python_path}")

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
        args = ["node", "run.js", "release", "python", python_path]
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
