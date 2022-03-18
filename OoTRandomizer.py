#!/usr/bin/env python3
import argparse
import os
import logging
import textwrap
import time
import datetime
import sys

from Gui import guiMain
from Main import main, from_patch_file, cosmetic_patch, diff_roms
from Utils import check_version, VersionError, check_python_version, local_path
from Settings import get_settings_from_command_line_args


class ArgumentDefaultsHelpFormatter(argparse.RawTextHelpFormatter):

    def _get_help_string(self, action):
        return textwrap.dedent(action.help)


def start():

    settings, gui, args_loglevel, no_log_file, diff_rom = get_settings_from_command_line_args()

    # set up logger
    loglevel = {'error': logging.ERROR, 'info': logging.INFO, 'warning': logging.WARNING, 'debug': logging.DEBUG}[args_loglevel]
    logging.basicConfig(format='%(message)s', level=loglevel)

    logger = logging.getLogger('')

    if not no_log_file:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H-%M-%S')
        log_dir = local_path('Logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_path = os.path.join(log_dir, '%s.log' % st)
        log_file = logging.FileHandler(log_path)
        log_file.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(log_file)

    if not settings.check_version:
        try:
            check_version(settings.checked_version)
        except VersionError as e:
            logger.warning(str(e))

    try:
        if gui:
            guiMain()
        elif diff_rom:
            diff_roms(settings, diff_rom)
        elif settings.cosmetics_only:
            cosmetic_patch(settings)
        elif settings.patch_file != '':
            from_patch_file(settings)
        elif settings.count != None and settings.count > 1:
            orig_seed = settings.seed
            for i in range(settings.count):
                settings.update_seed(orig_seed + '-' + str(i))
                main(settings)
        else:
            main(settings)
    except Exception as ex:
        logger.exception(ex)
        sys.exit(1)


if __name__ == '__main__':
    check_python_version()
    start()
