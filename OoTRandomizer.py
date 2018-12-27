#!/usr/bin/env python3
import argparse
import os
import logging
import random
import textwrap
import sys

from Gui import guiMain
from Main import main, from_patch_file, cosmetic_patch
from Utils import is_bundled, close_console, check_version, VersionError, check_python_version
from Settings import get_settings_from_command_line_args


class ArgumentDefaultsHelpFormatter(argparse.RawTextHelpFormatter):

    def _get_help_string(self, action):
        return textwrap.dedent(action.help)


def start():

    settings, gui, args_loglevel = get_settings_from_command_line_args()

    if is_bundled() and len(sys.argv) == 1:
        # for the bundled builds, if we have no arguments, the user
        # probably wants the gui. Users of the bundled build who want the command line
        # interface shouuld specify at least one option, possibly setting a value to a
        # default if they like all the defaults
        close_console()
        guiMain()
        sys.exit(0)

    # ToDo: Validate files further than mere existance
    if not os.path.isfile(settings.rom):
        input('Could not find valid base rom for patching at expected path %s. Please run with -h to see help for further information. \nPress Enter to exit.' % settings.rom)
        sys.exit(1)

    # set up logger
    loglevel = {'error': logging.ERROR, 'info': logging.INFO, 'warning': logging.WARNING, 'debug': logging.DEBUG}[args_loglevel]
    logging.basicConfig(format='%(message)s', level=loglevel)

    logger = logging.getLogger('')
    if not settings.check_version:
        try:
            version_error = check_version(settings.checked_version)
        except VersionError as e:
            logger.warning(str(e))

    if gui:
        guiMain(settings)
    elif settings.cosmetics_only:
        cosmetic_patch(settings)
    elif settings.patch_file != '':
        from_patch_file(settings)
    elif settings.count is not None:
        orig_seed = settings.seed
        for i in range(settings.count):
            settings.update_seed(orig_seed + '-' + str(i))
            main(settings)
    else:
        main(settings)

if __name__ == '__main__':
    check_python_version()
    start()
