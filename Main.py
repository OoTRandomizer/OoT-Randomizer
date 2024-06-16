from __future__ import annotations
import copy
import hashlib
import logging
import os
import platform
import random
import shutil
import time
import zipfile
from typing import Optional


from Cosmetics import CosmeticsLog, patch_cosmetics
from EntranceShuffle import set_entrances
from Fill import distribute_items_restrictive, ShuffleError
from Goals import update_goal_items, replace_goal_names
from Hints import build_gossip_hints
from HintList import clear_hint_exclusion_cache, misc_item_hint_table, misc_location_hint_table
from ItemPool import generate_itempool
from MBSDIFFPatch import apply_ootr_3_web_patch
from Models import patch_model_adult, patch_model_child
from N64Patch import create_patch_file, apply_patch_file
from Patches import patch_rom
from Rom import Rom
from Rules import set_rules, set_shop_rules
from Settings import Settings
from SettingsList import logic_tricks
from Spoiler import Spoiler
from Utils import default_output_path, is_bundled, run_process, data_path
from World import World
from version import __version__


def main(settings: Settings, max_attempts: int = 10) -> Spoiler:
    clear_hint_exclusion_cache()
    logger = logging.getLogger('')
    start = time.process_time()

    rom = resolve_settings(settings)

    max_attempts = max(max_attempts, 1)
    spoiler = None
    for attempt in range(1, max_attempts + 1):
        try:
            spoiler = generate(settings)
            break
        except ShuffleError as e:
            logger.warning('Failed attempt %d of %d: %s', attempt, max_attempts, e)
            if attempt >= max_attempts:
                raise
            else:
                logger.info('Retrying...\n\n')
            settings.reset_distribution()
    if spoiler is None:
        raise RuntimeError("Generation failed.")
    patch_and_output(settings, spoiler, rom)
    logger.debug('Total Time: %s', time.process_time() - start)
    return spoiler


def resolve_settings(settings: Settings) -> Optional[Rom]:
    logger = logging.getLogger('')

    old_tricks = settings.allowed_tricks
    settings.load_distribution()

    # compare pointers to lists rather than contents, so even if the two are identical
    # we'll still log the error and note the dist file overrides completely.
    if old_tricks and old_tricks is not settings.allowed_tricks:
        logger.error('Tricks are set in two places! Using only the tricks from the distribution file.')

    for trick in logic_tricks.values():
        settings.settings_dict[trick['name']] = trick['name'] in settings.allowed_tricks

    # we load the rom before creating the seed so that errors get caught early
    outputting_specific_world = settings.create_uncompressed_rom or settings.create_compressed_rom or settings.create_wad_file
    using_rom = outputting_specific_world or settings.create_patch_file or settings.patch_without_output
    if not (using_rom or settings.patch_without_output) and not settings.create_spoiler:
        raise Exception('You must have at least one output type or spoiler log enabled to produce anything.')

    if using_rom:
        rom = Rom(settings.rom)
    else:
        rom = None

    if not settings.world_count:
        settings.world_count = 1
    elif settings.world_count < 1 or settings.world_count > 255:
        raise Exception('World Count must be between 1 and 255')

    # Bounds-check the player_num settings, in case something's gone wrong we want to know.
    if settings.player_num < 1:
        raise Exception(f'Invalid player num: {settings.player_num}; must be between (1, {settings.world_count})')
    if settings.player_num > settings.world_count:
        if outputting_specific_world:
            raise Exception(f'Player Num is {settings.player_num}; must be between (1, {settings.world_count})')
        settings.player_num = settings.world_count

    # Set to a custom hint distribution if plando is overriding the distro
    if len(settings.hint_dist_user) != 0:
        settings.hint_dist = 'custom'

    logger.info('OoT Randomizer Version %s  -  Seed: %s', __version__, settings.seed)
    settings.remove_disabled()
    logger.info('(Original) Settings string: %s\n', settings.settings_string)
    random.seed(settings.numeric_seed)
    settings.resolve_random_settings(cosmetic=False)
    logger.debug(settings.get_settings_display())
    return rom


def generate(settings: Settings) -> Spoiler:
    worlds = build_world_graphs(settings)
    place_items(worlds)
    for world in worlds:
        world.distribution.configure_effective_starting_items(worlds, world)
    if worlds[0].enable_goal_hints:
        replace_goal_names(worlds)
    return make_spoiler(settings, worlds)


def build_world_graphs(settings: Settings) -> list[World]:
    logger = logging.getLogger('')
    worlds = []
    for i in range(0, settings.world_count):
        worlds.append(World(i, settings.copy()))

    savewarps_to_connect = []
    for id, world in enumerate(worlds):
        logger.info('Generating World %d.' % (id + 1))
        logger.info('Creating Overworld')

        # Load common json rule files (those used regardless of MQ status)
        if settings.logic_rules == 'glitched':
            path = 'Glitched World'
        else:
            path = 'World'
        path = data_path(path)

        for filename in ('Overworld.json', 'Bosses.json'):
            savewarps_to_connect += world.load_regions_from_json(os.path.join(path, filename))

        # Compile the json rules based on settings
        savewarps_to_connect += world.create_dungeons()
        world.create_internal_locations()

        if settings.shopsanity != 'off':
            world.random_shop_prices()
        world.set_scrub_prices()

        logger.info('Calculating Access Rules.')
        set_rules(world)

        logger.info('Generating Item Pool.')
        generate_itempool(world)
        set_shop_rules(world)
        world.set_drop_location_names()
        if world.settings.shuffle_dungeon_rewards in ('vanilla', 'reward'):
            world.fill_bosses()

        if settings.empty_dungeons_mode == 'rewards':
            world.set_empty_dungeon_rewards(settings.empty_dungeons_rewards)

    if settings.triforce_hunt:
        settings.distribution.configure_triforce_hunt(worlds)

    logger.info('Setting Entrances.')
    set_entrances(worlds, savewarps_to_connect)
    return worlds


def place_items(worlds: list[World]) -> None:
    logger = logging.getLogger('')
    logger.info('Fill the world.')
    distribute_items_restrictive(worlds)


def make_spoiler(settings: Settings, worlds: list[World]) -> Spoiler:
    logger = logging.getLogger('')
    spoiler = Spoiler(worlds)
    if settings.create_spoiler:
        logger.info('Calculating playthrough.')
        spoiler.create_playthrough()
    if settings.create_spoiler or settings.hints != 'none':
        logger.info('Calculating hint data.')
        update_goal_items(spoiler)
        build_gossip_hints(spoiler, worlds)
    elif any(world.dungeon_rewards_hinted for world in worlds) or any(hint_type in settings.misc_hints for hint_type in misc_item_hint_table) or any(hint_type in settings.misc_hints for hint_type in misc_location_hint_table):
        spoiler.find_misc_hint_items()
    spoiler.build_file_hash()
    return spoiler


def prepare_rom(spoiler: Spoiler, world: World, rom: Rom, settings: Settings, rng_state: Optional[tuple] = None, restore: bool = True) -> CosmeticsLog:
    if rng_state:
        random.setstate(rng_state)
        # Use different seeds for each world when patching.
        seed = int(random.getrandbits(256))
        for i in range(0, world.id):
            seed = int(random.getrandbits(256))
        random.seed(seed)

    if restore:
        rom.restore()
    patch_rom(spoiler, world, rom)
    cosmetics_log = patch_cosmetics(settings, rom)
    if not settings.generating_patch_file:
        if settings.model_adult != "Default" or len(settings.model_adult_filepicker) > 0:
            patch_model_adult(rom, settings, cosmetics_log)
        if settings.model_child != "Default" or len(settings.model_child_filepicker) > 0:
            patch_model_child(rom, settings, cosmetics_log)
    rom.update_header()
    return cosmetics_log


def compress_rom(input_file: str, output_file: str, delete_input: bool = False) -> None:
    logger = logging.getLogger('')
    compressor_path = "./" if is_bundled() else "bin/Compress/"
    if platform.system() == 'Windows':
        if platform.machine() == 'AMD64':
            compressor_path += "Compress.exe"
        elif platform.machine() == 'ARM64':
            compressor_path += "Compress_ARM64.exe"
        else:
            compressor_path += "Compress32.exe"
    elif platform.system() == 'Linux':
        if platform.machine() in ('arm64', 'aarch64', 'aarch64_be', 'armv8b', 'armv8l'):
            compressor_path += "Compress_ARM64"
        elif platform.machine() in ('arm', 'armv7l', 'armhf'):
            compressor_path += "Compress_ARM32"
        else:
            compressor_path += "Compress"
    elif platform.system() == 'Darwin':
        if platform.machine() == 'arm64':
            compressor_path += "Compress_ARM64.out"
        else:
            compressor_path += "Compress.out"
    else:
        logger.info("OS not supported for ROM compression.")
        raise Exception("This operating system does not support ROM compression. You may only output patch files or uncompressed ROMs.")

    run_process(logger, [compressor_path, input_file, output_file])
    if delete_input:
        os.remove(input_file)


def generate_wad(wad_file: str, rom_file: str, output_file: str, channel_title: str, channel_id: str, delete_input: bool = False) -> None:
    logger = logging.getLogger('')
    if wad_file == "" or wad_file is None:
        raise Exception("Unspecified base WAD file.")
    if not os.path.isfile(wad_file):
        raise Exception("Cannot open base WAD file.")

    gzinject_path = "./" if is_bundled() else "bin/gzinject/"
    gzinject_patch_path = gzinject_path + "ootr.gzi"
    if platform.system() == 'Windows':
        if platform.machine() == 'AMD64':
            gzinject_path += "gzinject.exe"
        elif platform.machine() == 'ARM64':
            gzinject_path += "gzinject_ARM64.exe"
        else:
            gzinject_path += "gzinject32.exe"
    elif platform.system() == 'Linux':
        if platform.machine() in ('arm64', 'aarch64', 'aarch64_be', 'armv8b', 'armv8l'):
            gzinject_path += "gzinject_ARM64"
        elif platform.machine() in ('arm', 'armv7l', 'armhf'):
            gzinject_path += "gzinject_ARM32"
        else:
            gzinject_path += "gzinject"
    elif platform.system() == 'Darwin':
        if platform.machine() == 'arm64':
            gzinject_path += "gzinject_ARM64.out"
        else:
            gzinject_path += "gzinject.out"
    else:
        logger.info("OS not supported for WAD generation.")
        raise Exception("This operating system does not support outputting .wad files.")

    run_process(logger, [gzinject_path, "-a", "genkey"], b'45e')
    run_process(logger, [gzinject_path, "-a", "inject", "--rom", rom_file, "--wad", wad_file,
                         "-o", output_file, "-i", channel_id, "-t", channel_title,
                         "-p", gzinject_patch_path, "--cleanup"])
    os.remove("common-key.bin")
    if delete_input:
        os.remove(rom_file)


def patch_and_output(settings: Settings, spoiler: Spoiler, rom: Optional[Rom]) -> None:
    logger = logging.getLogger('')
    worlds = spoiler.worlds
    cosmetics_log = None

    settings_string_hash = hashlib.sha1(settings.settings_string.encode('utf-8')).hexdigest().upper()[:5]
    if settings.output_file:
        output_filename_base = settings.output_file
    else:
        output_filename_base = f"OoT_{settings_string_hash}_{settings.seed}"
        if settings.world_count > 1:
            output_filename_base += f"_W{settings.world_count}"

    output_dir = default_output_path(settings.output_dir)

    compressed_rom = settings.create_compressed_rom or settings.create_wad_file
    uncompressed_rom = compressed_rom or settings.create_uncompressed_rom
    generate_rom = uncompressed_rom or settings.create_patch_file or settings.patch_without_output
    separate_cosmetics = settings.create_patch_file and uncompressed_rom

    if generate_rom and rom is not None:
        rng_state = random.getstate()
        file_list = []
        restore_rom = False
        for world in worlds:
            # If we aren't creating a patch file and this world isn't the one being outputted, move to the next world.
            if not (settings.create_patch_file or world.id == settings.player_num - 1):
                continue

            if settings.world_count > 1:
                logger.info(f"Patching ROM: Player {world.id + 1}")
                player_filename_suffix = f"P{world.id + 1}"
            else:
                logger.info('Patching ROM')
                player_filename_suffix = ""

            settings.generating_patch_file = settings.create_patch_file
            patch_cosmetics_log = prepare_rom(spoiler, world, rom, settings, rng_state, restore_rom)
            restore_rom = True

            if settings.create_patch_file:
                patch_filename = f"{output_filename_base}{player_filename_suffix}.zpf"
                logger.info(f"Creating Patch File: {patch_filename}")
                output_path = os.path.join(output_dir, patch_filename)
                file_list.append(patch_filename)
                create_patch_file(rom, output_path)

                # Cosmetics Log for patch file only.
                if settings.create_cosmetics_log and patch_cosmetics_log:
                    if separate_cosmetics:
                        cosmetics_log_filename = f"{output_filename_base}{player_filename_suffix}.zpf_Cosmetics.json"
                    else:
                        cosmetics_log_filename = f"{output_filename_base}{player_filename_suffix}_Cosmetics.json"
                    logger.info(f"Creating Cosmetics Log: {cosmetics_log_filename}")
                    patch_cosmetics_log.to_file(os.path.join(output_dir, cosmetics_log_filename))
                    file_list.append(cosmetics_log_filename)

            # If we aren't outputting an uncompressed ROM, move to the next world.
            if not uncompressed_rom or world.id != settings.player_num - 1:
                continue

            uncompressed_filename = f"{output_filename_base}{player_filename_suffix}_uncompressed.z64"
            uncompressed_path = os.path.join(output_dir, uncompressed_filename)
            logger.info(f"Saving Uncompressed ROM: {uncompressed_filename}")
            if separate_cosmetics:
                settings.generating_patch_file = False
                cosmetics_log = prepare_rom(spoiler, world, rom, settings, rng_state, restore_rom)
            else:
                cosmetics_log = patch_cosmetics_log
            rom.write_to_file(uncompressed_path)
            logger.info("Created uncompressed ROM at: %s" % uncompressed_path)

            # If we aren't compressing the ROM, we're done with this world.
            if not compressed_rom:
                continue

            compressed_filename = f"{output_filename_base}{player_filename_suffix}.z64"
            compressed_path = os.path.join(output_dir, compressed_filename)
            logger.info(f"Compressing ROM: {compressed_filename}")
            compress_rom(uncompressed_path, compressed_path, not settings.create_uncompressed_rom)
            logger.info("Created compressed ROM at: %s" % compressed_path)

            # If we aren't generating a WAD, we're done with this world.
            if not settings.create_wad_file:
                continue

            wad_filename = f"{output_filename_base}{player_filename_suffix}.wad"
            wad_path = os.path.join(output_dir, wad_filename)
            logger.info(f"Generating WAD file: {wad_filename}")
            channel_title = settings.wad_channel_title if settings.wad_channel_title != "" and settings.wad_channel_title is not None else "OoTRandomizer"
            channel_id = settings.wad_channel_id if settings.wad_channel_id != "" and settings.wad_channel_id is not None else "OOTE"
            generate_wad(settings.wad_file, compressed_path, wad_path, channel_title, channel_id, not settings.create_compressed_rom)
            logger.info("Created WAD file at: %s" % wad_path)

        # World loop over, make the patch archive if applicable.
        if settings.world_count > 1 and settings.create_patch_file:
            patch_archive_filename = f"{output_filename_base}.zpfz"
            patch_archive_path = os.path.join(output_dir, patch_archive_filename)
            logger.info(f"Creating Patch Archive: {patch_archive_filename}")
            with zipfile.ZipFile(patch_archive_path, mode="w") as patch_archive:
                for file in file_list:
                    file_path = os.path.join(output_dir, file)
                    patch_archive.write(file_path, file.replace(output_filename_base, '').replace('.zpf_Cosmetics', '_Cosmetics'), compress_type=zipfile.ZIP_DEFLATED)
            for file in file_list:
                os.remove(os.path.join(output_dir, file))
            logger.info("Created patch file archive at: %s" % patch_archive_path)

    if not settings.create_spoiler or settings.output_settings:
        settings.distribution.update_spoiler(spoiler, False)
        settings_path = os.path.join(output_dir, '%s_Settings.json' % output_filename_base)
        settings.distribution.to_file(settings_path, False)
        logger.info("Created settings log at: %s" % ('%s_Settings.json' % output_filename_base))
    if settings.create_spoiler:
        settings.distribution.update_spoiler(spoiler, True)
        spoiler_path = os.path.join(output_dir, '%s_Spoiler.json' % output_filename_base)
        settings.distribution.to_file(spoiler_path, True)
        logger.info("Created spoiler log at: %s" % ('%s_Spoiler.json' % output_filename_base))

    if settings.create_cosmetics_log and cosmetics_log:
        if settings.world_count > 1 and not settings.output_file:
            filename = "%sP%d_Cosmetics.json" % (output_filename_base, settings.player_num)
        else:
            filename = '%s_Cosmetics.json' % output_filename_base
        cosmetic_path = os.path.join(output_dir, filename)
        cosmetics_log.to_file(cosmetic_path)
        logger.info("Created cosmetic log at: %s" % cosmetic_path)

    if settings.enable_distribution_file:
        try:
            filename = os.path.join(output_dir, '%s_Distribution.json' % output_filename_base)
            shutil.copyfile(settings.distribution_file, filename)
            logger.info("Copied distribution file to: %s" % filename)
        except:
            logger.info('Distribution file copy failed.')

    if cosmetics_log and cosmetics_log.errors:
        logger.info('Success: Rom patched successfully. Some cosmetics could not be applied.')
    else:
        logger.info('Success: Rom patched successfully')


def from_patch_file(settings: Settings) -> None:
    start = time.process_time()
    logger = logging.getLogger('')

    compressed_rom = settings.create_compressed_rom or settings.create_wad_file
    uncompressed_rom = compressed_rom or settings.create_uncompressed_rom

    # we load the rom before creating the seed so that error get caught early
    if not uncompressed_rom:
        raise Exception('You must select a valid Output Type when patching from a patch file.')

    rom = Rom(settings.rom)
    logger.info('Patching ROM.')

    filename_split = os.path.basename(settings.patch_file).rpartition('.')

    if settings.output_file:
        output_filename_base = settings.output_file
    else:
        output_filename_base = filename_split[0]

    extension = filename_split[-1]

    output_dir = default_output_path(settings.output_dir)
    output_path = os.path.join(output_dir, output_filename_base)

    logger.info('Patching ROM')
    if extension == 'patch':
        apply_ootr_3_web_patch(settings, rom)
        create_patch_file(rom, output_path + '.zpf')
    else:
        subfile = None
        if extension == 'zpfz':
            subfile = f"P{settings.player_num}.zpf"
            if not settings.output_file:
                output_path += f"P{settings.player_num}"
        apply_patch_file(rom, settings, subfile)
    cosmetics_log = None
    if settings.repatch_cosmetics:
        cosmetics_log = patch_cosmetics(settings, rom)
        if settings.model_adult != "Default" or len(settings.model_adult_filepicker) > 0:
            patch_model_adult(rom, settings, cosmetics_log)
        if settings.model_child != "Default" or len(settings.model_child_filepicker) > 0:
            patch_model_child(rom, settings, cosmetics_log)

    logger.info('Saving Uncompressed ROM')
    uncompressed_path = output_path + '_uncompressed.z64'
    rom.write_to_file(uncompressed_path)
    logger.info("Created uncompressed rom at: %s" % uncompressed_path)

    if compressed_rom:
        logger.info('Compressing ROM')
        compressed_path = output_path + '.z64'
        compress_rom(uncompressed_path, compressed_path, not settings.create_uncompressed_rom)
        logger.info("Created compressed rom at: %s" % compressed_path)

        if settings.create_wad_file:
            wad_path = output_path + '.wad'
            channel_title = settings.wad_channel_title if settings.wad_channel_title != "" and settings.wad_channel_title is not None else "OoTRandomizer"
            channel_id = settings.wad_channel_id if settings.wad_channel_id != "" and settings.wad_channel_id is not None else "OOTE"
            generate_wad(settings.wad_file, compressed_path, wad_path, channel_title, channel_id,
                         not settings.create_compressed_rom)
            logger.info("Created WAD file at: %s" % wad_path)

    if settings.create_cosmetics_log and cosmetics_log:
        if settings.world_count > 1 and not settings.output_file:
            filename = "%sP%d_Cosmetics.json" % (output_filename_base, settings.player_num)
        else:
            filename = '%s_Cosmetics.json' % output_filename_base
        cosmetic_path = os.path.join(output_dir, filename)
        cosmetics_log.to_file(cosmetic_path)
        logger.info("Created cosmetic log at: %s" % cosmetic_path)

    if cosmetics_log and cosmetics_log.errors:
        logger.info('Success: Rom patched successfully. Some cosmetics could not be applied.')
    else:
        logger.info('Success: Rom patched successfully')

    logger.debug('Total Time: %s', time.process_time() - start)


def cosmetic_patch(settings: Settings) -> None:
    start = time.process_time()
    logger = logging.getLogger('')

    if settings.patch_file == '':
        raise Exception('Cosmetic Only must have a patch file supplied.')

    rom = Rom(settings.rom)

    logger.info('Patching ROM.')

    filename_split = os.path.basename(settings.patch_file).rpartition('.')

    if settings.output_file:
        outfilebase = settings.output_file
    else:
        outfilebase = filename_split[0]

    extension = filename_split[-1]

    output_dir = default_output_path(settings.output_dir)
    output_path = os.path.join(output_dir, outfilebase)

    logger.info('Patching ROM')
    if extension == 'zpf':
        subfile = None
    else:
        subfile = 'P%d.zpf' % (settings.player_num)
    apply_patch_file(rom, settings, subfile)

    # clear changes from the base patch file
    patched_base_rom = copy.copy(rom.buffer)
    rom.changed_address = {}
    rom.changed_dma = {}
    rom.force_patch = []

    patchfilename = '%s_Cosmetic.zpf' % output_path
    cosmetics_log = patch_cosmetics(settings, rom)

    # base the new patch file on the base patch file
    rom.original.buffer = patched_base_rom
    rom.update_header()
    create_patch_file(rom, patchfilename)
    logger.info("Created patchfile at: %s" % patchfilename)

    if settings.create_cosmetics_log and cosmetics_log:
        if settings.world_count > 1 and not settings.output_file:
            filename = "%sP%d_Cosmetics.json" % (outfilebase, settings.player_num)
        else:
            filename = '%s_Cosmetics.json' % outfilebase
        cosmetic_path = os.path.join(output_dir, filename)
        cosmetics_log.to_file(cosmetic_path)
        logger.info("Created cosmetic log at: %s" % cosmetic_path)

    if cosmetics_log and cosmetics_log.errors:
        logger.info('Success: Rom patched successfully. Some cosmetics could not be applied.')
    else:
        logger.info('Success: Rom patched successfully')

    logger.debug('Total Time: %s', time.process_time() - start)


def diff_roms(settings: Settings, diff_rom_file: str) -> None:
    start = time.process_time()
    logger = logging.getLogger('')

    logger.info('Loading base ROM.')
    rom = Rom(settings.rom)
    rom.force_patch = []

    filename_split = os.path.basename(diff_rom_file).rpartition('.')
    output_filename_base = settings.output_file if settings.output_file else filename_split[0]
    output_dir = default_output_path(settings.output_dir)
    output_path = os.path.join(output_dir, output_filename_base)

    logger.info('Loading patched ROM.')
    rom.read_rom(diff_rom_file, f"{output_path}_decomp.z64", verify_crc=False)
    try:
        os.remove(f"{output_path}_decomp.z64")
    except FileNotFoundError:
        pass

    logger.info('Searching for changes.')
    rom.rescan_changed_bytes()
    rom.scan_dmadata_update(assume_move=True)

    logger.info('Creating patch file.')
    create_patch_file(rom, f"{output_path}.zpf")
    logger.info(f"Created patchfile at: {output_path}.zpf")
    logger.info('Done. Enjoy.')
    logger.debug('Total Time: %s', time.process_time() - start)
