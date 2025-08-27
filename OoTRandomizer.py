#!/usr/bin/env python3
import sys
if sys.version_info < (3, 8):
    print("OoT Randomizer requires Python version 3.8 or newer and you are using %s" % '.'.join([str(i) for i in sys.version_info[0:3]]))
    sys.exit(1)

import datetime
import logging
import os
import time


def start() -> None:
    from Main import main, from_patch_file, cosmetic_patch, diff_roms
    from Settings import get_settings_from_command_line_args
    from Utils import check_version, VersionError, local_path
    settings, gui, args_loglevel, no_log_file, diff_rom = get_settings_from_command_line_args()

    # set up logger
    loglevel = {'error': logging.ERROR, 'info': logging.INFO, 'warning': logging.WARNING, 'debug': logging.DEBUG}[args_loglevel]
    logging.basicConfig(format='%(message)s', level=loglevel)

    logger = logging.getLogger('')

    if not no_log_file:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H-%M-%S')
        log_dir = local_path('Logs')
        os.makedirs(log_dir, exist_ok=True)
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
            from Gui import gui_main
            gui_main()
        elif diff_rom:
            diff_roms(settings, diff_rom)
        elif settings.cosmetics_only:
            cosmetic_patch(settings)
        elif settings.patch_file != '':
            from_patch_file(settings)
        elif settings.count is not None and settings.count > 1:
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
    start()
