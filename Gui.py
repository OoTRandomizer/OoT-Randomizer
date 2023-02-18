#!/usr/bin/env python3
import os
import sys

min_python_version = [3,6,0]
for i,v in enumerate(min_python_version):
    if sys.version_info[i] < v:
        print("Randomizer requires at least version 3.6 and you are using %s" % '.'.join([str(i) for i in sys.version_info[0:3]]))
        # raw_input was renamed to input in 3.0, handle both 2.x and 3.x by trying the rename for 2.x
        try:
            input = raw_input
        except NameError:
            pass
        input("Press enter to exit...")
        sys.exit(1)
    if sys.version_info[i] > v:
        break

import subprocess
import shutil
import webbrowser
from Utils import local_path, data_path, check_python_version, compare_version, VersionError
from SettingsToJson import CreateJSON

def guiMain():
    try:
        version_check("Node", "14.15.0", "https://nodejs.org/en/download/")
        version_check("NPM", "6.12.0", "https://nodejs.org/en/download/")
    except VersionError as ex:
        print(ex.args[0])
        webbrowser.open(ex.args[1])
        return

    web_version = '--web' in sys.argv
    if '--skip-settingslist' not in sys.argv:
        CreateJSON(data_path('generated/settings_list.json'), web_version)

    if web_version:
        args = ["node", "run.js", "web"]
    else:
        args = ["node", "run.js", "release", "python", sys.executable]
    subprocess.run(args,shell=False,cwd=local_path("GUI"),check=True)

def version_check(name, version, URL):
    try:
        process = subprocess.Popen([shutil.which(name.lower()), "--version"], stdout=subprocess.PIPE)
    except Exception as ex:
        raise VersionError('{name} is not installed. Please install {name} {version} or later'.format(name=name, version=version), URL)

    while True:
        line = str(process.stdout.readline().strip(), 'UTF-8')
        if line == '':
            break
        if compare_version(line, version) < 0:
            raise VersionError('{name} {version} or later is required but you are using {line}'.format(name=name, version=version, line=line), URL)
        print('Using {name} {line}'.format(name=name, line=line))

if __name__ == '__main__':
    guiMain()
