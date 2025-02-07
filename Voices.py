from __future__ import annotations
from enum import Enum
from math import ceil
import random
import sys
from typing import BinaryIO
from Audiobank import *
from Rom import Rom
from Settings import Settings
from Utils import data_path
from bin.tools.adpcm.adpcm_encode import adpcm_encode
from bin.tools.ml64_unpak import ML64Unpack
import soundfile as sf
import os
import numpy as np
import json
import zipfile
import io

AUDIOSEQ_DMADATA_INDEX: int = 4

AUDIOBANK_INDEX_ADDR = 0x00B896A0
AUDIOBANK_FILE_ADDR = 0xD390
AUDIOBANK_FILE_LENGTH = 0x1CA50
AUDIOTABLE_FILE_ADDR = 0x79470
AUDIOTABLE_FILE_LENGTH = 0x460AD0
AUDIOTABLE_INDEX_ADDR = 0x00B8A1C0

SFX_TYPE_PLAY_ONE = 0x01
SFX_TYPE_CHOOSE_RAND = 0x02
SFX_TYPE_PLAY_ORDERED = 0x03

# Calculate the ticks variable to be used when overwriting
# SFX sequences
def calculate_ticks(numFrames, sampleRate) -> int:
    duration = float(numFrames) / float(sampleRate)
    # seconds = ticks / (120 * 48) * 60
    numTicks = int(duration * (120 * 48) / 60) + 1
    numTicks |= 0x8000 # for aseq VAR format
    return numTicks

# SFX patch functions
# Used to patch SFX that use multiple sequenced samples with a single audio file
# Return a list of tuples of the form (address, [patch_data])
# Where address is the offset into the SEQ0 file
# and patch_data is a list of bytes to patch at that address

def adult_sfx_patch_death(rom: Rom, numFrames: int, sampleRate: int) -> tuple[int, list[int]]:
    # increase length. Patch out the last 2 notes w/ 0xFF
    numTicks = calculate_ticks(numFrames, sampleRate)
    tick_bytes = numTicks.to_bytes(2, 'big')
    return [(0x6265, [0x4D] + list(tick_bytes) + [0x64] + [0xFF]*5)]

def adult_sfx_patch_sneeze(rom: Rom, numFrames: int, sampleRate: int) -> tuple[int, list[int]]:
    # Increase duration of first note and make it 100 volume. Patch out the last 2 notes
    numTicks = calculate_ticks(numFrames, sampleRate)
    tick_bytes = numTicks.to_bytes(2, 'big')
    return [
        (0x628D, [0x50] + list(tick_bytes) + [0x64] + [0xFF]*7)
    ]

def adult_sfx_patch_sweat(rom: Rom, numFrames: int, sampleRate: int) -> tuple[int, list[int]]:
    numTicks = calculate_ticks(numFrames, sampleRate)
    tick_bytes = numTicks.to_bytes(2, 'big')
    return [
        (0x629F, [0x53] + list(tick_bytes) + [0x64] +
        [0xFF]*7)
    ]

def adult_sfx_patch_stretch(rom: Rom, numFrames: int, sampleRate: int) -> tuple[int, list[int]]:
    numTicks = calculate_ticks(numFrames, sampleRate)
    tick_bytes = numTicks.to_bytes(2, 'big')
    return [
        (0x62BA, [0x56] + list(tick_bytes) + [0x64] + [0xFF]*7)
    ]

adult_sfx_id_map = {
    0x6800: { # Adult Link Attacks
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x00, 0x01, 0x02, 0x03]
    },
    0x6801: { # Adult Link Strong Attacks
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x04, 0x05]
    },
    0x6802: { # Adult Link Lashing Epona
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x15, 0x16]
    },
    0x6803: { # Adult Link Dangling Gasp/Grunt
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x06, 0x19]
    },
    0x6804: { # Adult Link Climbing Ledge after having fallen on it
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x07, 0x08]
    },
    0x6805: { # Adult Link Hurt
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x09, 0x0A, 0x0B]
    },
    0x6806: {  # Adult Link knock back landing
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x0C, 0x0D, 0x0E]
    },
    0x6807: { # Adult Link Gasp
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x11, 0x12]
    },
    0x6808: { # Adult Link Fall
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x0F, 0x10]
    },
    0x6809: { # Adult Link Pant
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x13, 0x17]
    },
    0x680A: { # Adult Link Refreshed
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x38]
    },
    0x680B: { # Adult Link Death Sequence
        'type': SFX_TYPE_PLAY_ORDERED,
        'sounds': [0x4D],
        'patch': adult_sfx_patch_death
    },
    0x680E: { # Adult Link Sneeze Idle Sequence
        'type': SFX_TYPE_PLAY_ORDERED,
        'sounds': [0x50],
        'patch': adult_sfx_patch_sneeze
    },
    0x680F: { # Adult Link Sweat Idle Sequence
        'type': SFX_TYPE_PLAY_ORDERED,
        'sounds': [0x53],
        'patch': adult_sfx_patch_sweat
    },
    0x6810: { # Adult Link Drink
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x37]
    },
    0x6811: { # Adult Link Stretch Idle Sequence
        'type': SFX_TYPE_PLAY_ORDERED,
        'sounds': [0x56],
        'patch': adult_sfx_patch_stretch
    },
    0x6814: { # Adult Link Jump/Climb
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x1A, 0x1B]
    },
    0x6816: { # Adult Link Surprised
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x86]
    },
    0x681A: { # Adult Link Fall Damage
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x18]
    },
    0x681C: { # Adult Link Dins Fire}
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x3D]
    },
}


def child_sfx_patch_death(rom: Rom, numFrames: int, sampleRate: int):
    
    # Switch the first note to use 0x41 and increase length. Patch out the last 2 notes w/ 0xFF
    numTicks = calculate_ticks(numFrames, sampleRate)
    tick_bytes = numTicks.to_bytes(2, 'big')
    return [(0x642A, [0x41] + list(tick_bytes) + [0x64] + [0xFF]*5)]

def child_sfx_patch_sneeze(rom: Rom, numFrames: int, sampleRate: int):
    # Increase duration of first note and make it 100 volume. Patch out the last 3 notes
    numTicks = calculate_ticks(numFrames, sampleRate)
    tick_bytes = numTicks.to_bytes(2, 'big')
    return [
        (0x6457, [0x43] + list(tick_bytes) + [0x64] + [0xFF]*11)
    ]

def child_sfx_patch_sweat(rom: Rom, numFrames: int, sampleRate: int):
    # Patch out the last 2 notes and increase length of the first
    # Existing Code
    # .channel CHAN_6467
    # /* 0x6467 [0x88 0x64 0x6B          ] */ ldlayer     0, LAYER_646B
    # /* 0x646A [0xFF                    ] */ end
# 
    # .layer LAYER_646B
    # /* 0x646B [0xC2 0x01               ] */ transpose   1
    # /* 0x646D [0x47 0x80 0xD9 0x64     ] */ notedv      PITCH_E1, FRAMERATE_CONST(217, 260), 100
    # /* 0x6471 [0x48 0x62 0x64          ] */ notedv      PITCH_F1, FRAMERATE_CONST(98, 118), 100
    # /* 0x6474 [0x49 0x81 0x09 0x64     ] */ notedv      PITCH_GF1, 265, 100
    # /* 0x6478 [0xFF                    ] */ end
    numTicks = calculate_ticks(numFrames, sampleRate)
    tick_bytes = numTicks.to_bytes(2, 'big')
    return [
        (0x646D, [0x47] + list(tick_bytes) + [0x64] +
        [0xFF]*7)
    ]

def child_sfx_patch_stretch(rom: Rom, numFrames: int, sampleRate: int):
    # Existing Code
    #   .channel CHAN_6482
    #   /* 0x6482 [0x88 0x64 0x86          ] */ ldlayer     0, LAYER_6486
    #   /* 0x6485 [0xFF                    ] */ end
    #
    #   .layer LAYER_6486
    #   /* 0x6486 [0xC2 0x01               ] */ transpose   1
    #   /* 0x6488 [0x4A 0x41 0x64          ] */ notedv      PITCH_G1, FRAMERATE_CONST(65, 78), 100
    #   /* 0x648B [0x4B 0x81 0x0A 0x64     ] */ notedv      PITCH_AF1, FRAMERATE_CONST(266, 319), 100
    #   /* 0x648F [0x4C 0x53 0x64          ] */ notedv      PITCH_A1, 83, 100
    #   /* 0x6492 [0xFF                    ] */ end

    # Patch out the last 2 notes. Increase length of first note
    numTicks = calculate_ticks(numFrames, sampleRate)
    tick_bytes = numTicks.to_bytes(2, 'big')
    return [
        (0x6488, [0x4A] + list(tick_bytes) + [0x64] + [0xFF]*6)
    ]

child_sfx_id_map = {
    0x6820: { # Child Link Attacks
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x1C, 0x1D, 0x1E, 0x1F]
    },
    0x6821: { # Child Link Strong Attacks
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x20, 0x21]
    },
    0x6823: { # Child Link Dangling Gasp/Grunt
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x22, 0x32]
    },
    0x6824: { # Child Link Climbing Ledge after having fallen on it
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x23, 0x24]
    },
    0x6825: { # Child Link Hurt
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x25, 0x26, 0x27]
    },
    0x6826: {  # Child Link knock back landing
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x28, 0x29, 0x2A]
    },
    0x6827: { # Child Link Gasp
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x2D, 0x2E]
    },
    0x6828: { # Child Link Fall
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x2B, 0x2C]
    },
    0x6829: { # Child Link Pant
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x2F, 0x30]
    },
    0x682A: { # Child Link Refreshed
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x34]
    },
    0x682B: { # Child Link Death Sequence
        'type': SFX_TYPE_PLAY_ORDERED,
        # 'sounds': [0x40, 0x41, 0x42], SFX 0x40 shares its sample with 0x14 so we're going to use 0x41 instead
        'sounds': [0x41],
        'patch': child_sfx_patch_death,
    },
    0x682D: { # Child Link Grabbed By Redead (Uses different sound unlike adult)
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x14]
    },
    0x682E: { # Child Link Sneeze Idle Sequence
        'type': SFX_TYPE_PLAY_ORDERED,
        'sounds': [0x43],
        'patch': child_sfx_patch_sneeze,
    },
    0x682F: { # Child Link Sweat Idle Sequence
        'type': SFX_TYPE_PLAY_ORDERED,
        'sounds': [0x47],
        'patch': child_sfx_patch_sweat,
    },
    0x6830: { # Child Link Drink
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x33]
    },
    0x6831: { # Child Link Stretch Idle Sequence
        'type': SFX_TYPE_PLAY_ORDERED,
        'sounds': [0x4A],
        'patch': child_sfx_patch_stretch
    },
    0x6833: { # Child Link Shiver
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x43]
    },
    0x6834: { # Child Link Jump/Climb
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x35, 0x36]
    },
    0x6836: { # Child Link Surprised
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x87]
    },
    0x683A: { # Child Link Fall Damage
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x31]
    },
    0x683C: { # Child Link Din's Fire
        'type': SFX_TYPE_CHOOSE_RAND,
        'sounds': [0x3F]
    }
}

child_link_sfx = [
    ("Child Link - Dying Gasp", 20),
    ("Child Link - Attack 1", 28),
    ("Child Link - Attack 2", 29),
    ("Child Link - Attack 3", 30),
    ("Child Link - Attack 4", 31),
    ("Child Link - Strong Attack 1", 32),
    ("Child Link - Strong Attack 2", 33),
    ("Child Link - Dangling Gasp 1", 34),
    ("Child Link - Danging Gasp 2", 50),
    ("Child Link - Sigh 1", 35),
    ("Child Link - Sigh 2", 36),
    ("Child Link - Hurt 1", 37),
    ("Child Link - Hurt 2", 38),
    ("Child Link - Hurt 3", 39),
    ("Child Link - Hurt 4", 40),
    ("Child Link - Hurt 5", 42),
    ("Child Link - Knocked Back", 41),
    ("Child Link - Falling 1", 43),
    ("Child Link - Falling 2", 44),
    ("Child Link - Gasp 1", 45),
    ("Child Link - Gasp 2", 46),
    ("Child Link - Gasp 3", 66),
    ("Child Link - Wheeze", 47),
    ("Child Link - Exhausted Panting", 48),
    ("Child Link - Painful Landing", 49),
    ("Child Link - Glug", 51),
    ("Child Link - Refreshed", 52),
    ("Child Link - Hup 1", 53),
    ("Child Link - Hup 2", 54),
    ("Child Link - Charge Up", 62),
    ("Child Link - Cast Spell", 63),
    ("Child Link - Dying Gasp", 64),
    ("Child Link - Strangled", 65),
    ("Child Link - Shiver", 67),
    ("Child Link - Sneeze", 69),
    ("Child Link - Grunt", 70),
    ("Child Link - Moans From Heat", 71),
    ("Child Link - Awakening Grunt", 72),
    ("Child Link - Wiping Off Sweat", 73),
    ("Child Link - Yawn Starts", 74),
    ("Child Link - Yawn and Stretch", 75),
    ("Child Link - Stretch Refreshingly", 76),
    ("Child Link - Dramatic Gasp", 135)
]

adult_link_sfx = [
    ("Adult Link - Attack 1", 0x00),
    ("Adult Link - Attack 2", 0x01),
    ("Adult Link - Attack 3", 0x02),
    ("Adult Link - Attack 4", 0x03),
    ("Adult Link - Strong Attack 1", 0x04),
    ("Adult Link - Strong Attack 2", 0x05),
    ("Adult Link - Dangling Grunt", 0x06),
    ("Adult Link - Climb Edge", 0x07),
    ("Adult Link - Dangling Gasp 1", 0x08),
    ("Adult Link - Hurt 1", 0x09),
    ("Adult Link - Hurt 2", 0x0A),
    ("Adult Link - Hurt 3", 0x0B),
    ("Adult Link - Hurt 4", 0x0C),
    ("Adult Link - Knocked Back", 0x0D),
    ("Adult Link - Hurt 5", 0x0E),
    ("Adult Link - Falling 1", 0x0F),
    ("Adult Link - Falling 2", 0x10),
    ("Adult Link - Gasp 1", 0x11),
    ("Adult Link - Gasp 2", 0x12),
    ("Adult Link - Pant 1", 0x13),
    ("Adult Link - Spur Horse 1", 0x15),
    ("Adult Link - Spur Horse 2", 0x16),
    ("Adult Link - Pant 2", 0x17),
    ("Adult Link - Painful Landing", 0x18),
    ("Adult Link - Dangling Gasp 2", 0x19),
    ("Adult Link - Hup", 0x1A),
    ("Adult Link - Gasp 3", 0x1B),
    ("Adult Link - Glug", 0x37),
    ("Adult Link - Refreshed", 0x38),
    ("Adult Link - Lift", 0x3C),
    ("Adult Link - Cast Spell", 0x3D),
    ("Adult Link - Hurt 6", 0x4D),
    ("Adult Link - Choking", 0x4E),
    ("Adult Link - Gasping", 0x4F),
    ("Adult Link - Small Gasp", 0x50),
    ("Adult Link - Unsettled Moan", 0x51),
    ("Adult Link - Sneeze", 0x52),
    ("Adult Link - Sigh 1", 0x53),
    ("Adult Link - Sigh 2", 0x54),
    ("Adult Link - Sigh 3", 0x55),
    ("Adult Link - Stretch Start", 0x56),
    ("Adult Link - Stretching", 0x57),
    ("Adult Link - Finished Stretching", 0x58),
    ("Adult Link - Dramatic Gasp", 0x86)
]

class VOICE_PACK_AGE(Enum):
    CHILD = 0
    ADULT = 1

# pak_sfx_id - The SFX ID specified in the pack. We'll try to map paks that are created for a specific age to the selected age
# sfx_id_map - the sfx_id -> bank map to use selected by age
# pak_sounds - a dictionary mapping for the entire voice pack - sfx_id to a list of tuples containing the file's name and the raw data from the file
# age that this pak is for
def process_pak_sfx_by_id(pak_sfx_id: int, sfx_id_map, pak_sounds, age, settings: Settings) -> tuple[str, int, list[int], bytearray, int, int, function]:
    to_add = []

    # Check if the sfx_id is in the mapping for this age. 
    sfx_id = pak_sfx_id   
    if sfx_id in sfx_id_map.keys():
        pak_opts = pak_sounds[pak_sfx_id] # Options provided in the pack
        if not pak_opts:
            return []
        # Look up sfx_id in our mapping
        mapping = sfx_id_map[sfx_id]
        sfx_type = mapping['type']
        if sfx_type == SFX_TYPE_CHOOSE_RAND:
            # SFX that are selected at random by the SFX sequence, or only use a single sound
            rom_targets = mapping['sounds'] # Different sounds used by the vanilla sequence
            to_add = []
            if len(pak_opts) <= len(rom_targets):
                # We have <= than what the game expects, patch the ones we have and then randomly select among them to extend to the amount required
                i = 0
                # Add the ones we have
                for name, decompressed in pak_opts:
                    _file = io.BytesIO(decompressed)
                    soundData, numSampleFrames, sampleRate, book, loop = process_sound_file(name, _file, age, settings, trim=True)
                    _file.close()
                    to_add.append((name, 0, rom_targets[i], soundData, numSampleFrames, sampleRate, None))
                    i += 1
                # Randomly pick from the ones we've already added and duplicate them
                for j in range(i, len(rom_targets)):
                    added = to_add[random.randint(0, i-1)]
                    to_add.append((added[0], 0, rom_targets[j], added[3], added[4], added[5], None))
            else:
                # We have more than what the game expects, just take the first ones based on the length we expect
                for i in range(0, len(rom_targets)):
                    name, decompressed = pak_opts[i]
                    _file = io.BytesIO(decompressed)
                    soundData, numSampleFrames, sampleRate, book, loop = process_sound_file(name, _file, age, settings, trim=True)
                    _file.close()
                    to_add.append((name, 0, rom_targets[i], soundData, numSampleFrames, sampleRate, None))
                pass
        elif sfx_type == SFX_TYPE_PLAY_ORDERED:
            rom_targets = mapping['sounds']
            # These vanilla SFX are a combination of multiple sounds that are played as notes by the sequence player with delays in between
            # The delay values were taken from the sequence in "ticks" where delay (seconds) = ticks / (120 * 48) * 60
            # Delay is the duration to play the SFX + time to wait after
            # We should just play a single SFX because it seems like that was ML's intent
            # We'll need to patch the sequence to not call the other SFX and instead just end (0xFF)
            patch = mapping['patch']
            name, decompressed = pak_opts[0]
            _file = io.BytesIO(decompressed)
            soundData, numSampleFrames, sampleRate, book, loop = process_sound_file(name, _file, age, settings, trim=True)
            to_add.append((name, 0, rom_targets[0], soundData, numSampleFrames, sampleRate, patch))
            _file.close()
        else:
            raise Exception("Unsupported sfx type")
    return to_add

def patch_voice_pack(rom: Rom, age: VOICE_PACK_AGE, voice_pack: str, settings: Settings) -> None:
    # Don't allow custom voice packs when generating patch files
    if settings.generating_patch_file:
        return
    
    # Build voice pack path
    voice_pack_dir = os.path.join(data_path(), "Voices", "Child" if age == VOICE_PACK_AGE.CHILD else "Adult", voice_pack)

    sfx_list: list[tuple[str,int]] = child_link_sfx if age == VOICE_PACK_AGE.CHILD else adult_link_sfx
    sfx_id_map = child_sfx_id_map if age == VOICE_PACK_AGE.CHILD else adult_sfx_id_map

    # List all files in the directory
    files : list[str] = os.listdir(voice_pack_dir)

    sfxs = []
    inst_patch = []
    for filename in files:
        # ML64 .pak file
        # ML64 packs use SFX ID. SFX ID's are processed by the SFX sequence player so the mapping to the bank index isn't straightfoward
        # Some SFX will randomly select from multiple samples. ML64 doesn't necessarily respect how many random samples the sequence expects because it seems to run outside of the sequence player
        # Some SFX will play multiple samples in order but ML64 packs will include a single sample
        # Some SFX in the vanilla game re-use samples but ML64 packs won't follow this
        # Let's try to come up with a clever way to patch these
        # 1) Figure out what sort of SFX this is
        # Generally falls into one of 3 categories based on how the SFX works in the vanilla SFX seqence
        #     - Play 1 specific sound 
        #     - Randomly select from multiple sounds
        #     - Plays multiple sounds
        if filename.endswith(".pak"):
            # Read the .pak file
            with open(os.path.join(voice_pack_dir, filename), 'rb') as f:
                pak_bytes = f.read()
            pak = ML64Unpack.ML64Pak(pak_bytes)
            pak_sounds = pak.read_all_sounds()
            for pak_sfx_id in pak_sounds.keys():
                sfxs.extend(process_pak_sfx_by_id(pak_sfx_id, sfx_id_map, pak_sounds, age, settings))

        # New ZOOTR voice pack file
        # Support mapping sounds either via SFX_ID like ML64 does
        # Or directly via bank index
        elif filename.endswith("zip"):
            zf: zipfile.ZipFile = zipfile.ZipFile(os.path.join(voice_pack_dir, filename))
            for file in zf.filelist:
                # Find the voice map file in the archive
                if file.filename == "voice_map.json":
                    with zf.open(file) as f:
                        # Read the voice map
                        json_string = f.read().decode()
                        # Allow comments in the json so strip them out
                        json_lines = json_string.splitlines()
                        json_string = ""
                        for line in json_lines:
                            if "#" in line:
                                json_string += line[0:line.index("#")]
                            else:
                                json_string += line
                        voice_map = json.loads(json_string)
                    # Loop through the voice map
                    # Check for SFX mapped and handle it like we do for ML64
                    if "sfx" in voice_map.keys():
                        for sfx_id_str in voice_map["sfx"]:
                            if sfx_id_str.startswith("0x"):
                                sfx_id = int(sfx_id_str,16)
                            else:
                                sfx_id = int(sfx_id_str)
                            pak_sounds = {
                                sfx_id: []
                            }
                            # Read the files for this SFX ID
                            for sample_file in voice_map["sfx"][sfx_id_str]: # Iterate through list containing the files to be mapped for this SFX
                                # read the file data
                                sample_bytes = zf.read(sample_file)
                                pak_sounds[sfx_id].append((sample_file, sample_bytes))
                            sfxs.extend(process_pak_sfx_by_id(sfx_id, sfx_id_map, pak_sounds, age, settings))
                            
                    # Check for direct_bank mapped
                    if "direct_bank" in voice_map.keys():
                        for bank_str in voice_map["direct_bank"].keys():
                            bank = int(bank_str, 16)
                            for index_str in voice_map["direct_bank"][bank_str].keys():
                                index = int(index_str, 16)
                                sample_file = voice_map["direct_bank"][bank_str][index_str]
                                with zf.open(sample_file) as f:
                                    # Read and process the file
                                    soundData, numSampleFrames, sampleRate, book, loop = process_sound_file(sample_file, f, age, settings)
                                    sfxs.append((sample_file, bank, index, soundData, numSampleFrames, sampleRate, None))
                    if "direct_bank_inst" in voice_map.keys():
                        for bank_str in voice_map["direct_bank_inst"].keys():
                            bank_index = int(bank_str, 16)
                            bank = rom.audiobanks[bank_index]
                            for index_str in voice_map["direct_bank_inst"][bank_str].keys():
                                index = int(index_str, 16)
                                instrument = bank.instruments[index]
                                instrument.tag = True
                                instrument_json: dict = voice_map["direct_bank_inst"][bank_str][index_str]
                                if "lowNote" in instrument_json.keys():
                                    with zf.open(instrument_json["lowNote"]) as f:
                                        soundData, numSampleFrames, sampleRate, book, loop = process_sound_file(f.name, f, age, settings)
                                        # Pad the data to 16 bytes
                                        soundData += bytearray((16 - (len(soundData)%16))%16)
                                        tuning = sampleRate / 32000
                                        tuning = tuning * instrument_json["lowTuning"]
                                        lowSample = Sample()
                                        lowSample.tag = True
                                        instrument.lowNoteTuning = float(tuning)
                                        lowSample.loop = loop
                                        lowSample.book = book
                                        lowSample.data = soundData
                                        # Update sample data length = length
                                        lowSample.size = len(soundData)
                                        instrument.lowNoteSample = lowSample
                                        points = [
                                            EnvelopePoint(1, 32700),
                                            EnvelopePoint(10000, 0),
                                            EnvelopePoint(-1, 0)
                                        ]
                                        
                                        envelope = Envelope(points)
                                        instrument.envelope = envelope
                                if "normalNote" in instrument_json.keys():
                                    with zf.open(instrument_json["normalNote"]) as f:
                                        soundData, numSampleFrames, sampleRate, book, loop = process_sound_file(f.name, f, age, settings)
                                        # Pad the data to 16 bytes
                                        soundData += bytearray((16 - (len(soundData)%16))%16)
                                        tuning = sampleRate / 32000
                                        tuning = tuning * instrument_json["normalTuning"]
                                        normalSample = Sample()
                                        normalSample.tag = True
                                        instrument.normalNoteTuning = float(tuning)
                                        normalSample.loop = loop
                                        normalSample.book = book
                                        normalSample.data = soundData
                                        # Update sample data length = length
                                        normalSample.size = len(soundData)
                                        instrument.normalNoteSample = normalSample
                                        points = [
                                            EnvelopePoint(1, 32700),
                                            EnvelopePoint(10000, 0),
                                            EnvelopePoint(-1, 0)
                                        ]
                                        
                                        envelope = Envelope(points)
                                        instrument.envelope = envelope
                                if "highNote" in instrument_json.keys():
                                    with zf.open(instrument_json["highNote"]) as f:
                                        soundData, numSampleFrames, sampleRate, book, loop = process_sound_file(f.name, f, age, settings)
                                        # Pad the data to 16 bytes
                                        soundData += bytearray((16 - (len(soundData)%16))%16)
                                        tuning = sampleRate / 32000
                                        tuning = tuning * instrument_json["highTuning"]
                                        highSample = Sample()
                                        highSample.tag = True
                                        instrument.highNoteSampleTuning = float(tuning)
                                        highSample.loop = loop
                                        highSample.book = book
                                        highSample.data = soundData
                                        # Update sample data length = length
                                        highSample.size = len(soundData)
                                        instrument.highNoteSample = highSample
                                        points = [
                                            EnvelopePoint(1, 32700),
                                            EnvelopePoint(10000, 0),
                                            EnvelopePoint(-1, 0)
                                        ]
                                        
                                        envelope = Envelope(points)
                                        instrument.envelope = envelope
                                if "normalRangeLow" in instrument_json.keys():
                                    instrument.normalRangeLo = instrument_json["normalRangeLow"]
                                if "normalRangeHigh" in instrument_json.keys():
                                    instrument.normalRangeHi = instrument_json["normalRangeHigh"]
            zf.close()

    # Patch each sfx that we have
    for _, bank_index, sfx_id, soundData, numSampleFrames, sampleRate, patch in sfxs:
        # Calculate the tuning as sampling rate / 32000.
        tuning = sampleRate / 32000

        # Pad the data to 16 bytes
        soundData += bytearray((16 - (len(soundData)%16))%16)

        bank = rom.audiobanks[bank_index]

        # Sort-of problem. We need to update audiotable in multiple different spots. 
        # So instead of making the new file, maybe just add a new variable to Rom called new_audiotable_data and write it all at the end.
        # Update sample address to point to new data in audiotable.
        sfx: SFX = bank.SFX[sfx_id]


        sfx.sample.data = soundData
        # Update the sfx tuning
        sfx.sampleTuning = float(tuning)

        # Update loop end as numSampleFrames
        sfx.sample.loop.end = numSampleFrames
        # Update sample data length = length
        sfx.sample.size = len(soundData)

        dma_entry = rom.dma[AUDIOSEQ_DMADATA_INDEX]
        # Need to read the Audioseq table to find the start of sequence 0
        seq0_table_entry = rom.read_bytes(0xB89AE0, 0x10)
        seq0_offset = int.from_bytes(seq0_table_entry[0:4], 'big')

        if patch:
            patches = patch(rom, numSampleFrames, sampleRate)
            for addr, patch_bytes in patches:
                rom.write_bytes(dma_entry.start + seq0_offset + addr, patch_bytes)
    return

# Processes a single sound file into ADPCM data ready to be patched into the ROM
# file_name: the name of the file, used to determine how to process it
# file: a file-like object that will be read to process the file
# returns: tuple of the form (soundData, numSampleFrames, sampleRate)
def process_sound_file(file_name: str, file: BinaryIO, age: VOICE_PACK_AGE, settings: Settings, trim: bool = False) -> tuple[bytearray, int, int]:
    # Check if this is a file format that sf supports
    filename, ext = os.path.splitext(file_name)
    if ext.strip('.').upper() in sf.available_formats():
        soundData, numSampleFrames, sampleRate, book, loop = process_soundfile_file(file, age, settings, trim)
    elif ext == ".aifc":
        soundData, numSampleFrames, sampleRate, book, loop = process_aifc_file(file)
    elif ext == ".bin":
        soundData, numSampleFrames, sampleRate, book, loop = process_bin_file(file)
    else:
        raise Exception(f"Unsupported file format {ext} in custom voice pack.")

    return soundData, numSampleFrames, sampleRate, book, loop


# Read an audio file using the soundfile python library
def process_soundfile_file(f: BinaryIO, age: VOICE_PACK_AGE, settings: Settings, trim=False) -> tuple[bytes, int, int, AdpcmBook, AdpcmLoop]:
        data, sampleRate = sf.read(f)
        if data.ndim == 2 and data.shape[1] == 2:
            # Convert stereo to mono by averaging the two channels
            data = np.mean(data, axis=1)
        data = data / max(abs(data.max()), abs(data.min())) # Normalize track
        data = (data*32768).astype('>i2') # Convert to 16 bit big endian integers
        if trim: # Trim data - primarily used because ML64 sucks
            try:
                trim_index = list(map(lambda i: i > 0, data)).index(True)
                data = data[trim_index:]
            except ValueError as e:
                pass
        frames = data.tobytes()
        numSampleFrames = len(data)
        soundData = adpcm_encode(frames, len(data)) # Encode the raw samples
        return soundData, numSampleFrames, sampleRate, None, None

# Used for patching SFX AIFC files that have already been stripped into raw binary ready to patch into the ROM
# Assume a vanilla sampling rate of 20000
def process_bin_file(f: BinaryIO) -> tuple[bytes, int, int, AdpcmBook, AdpcmLoop]:
    soundData = f.read()
    numSampleFrames = int(len(soundData) * 16 / 9)
    sampleRate = 20000
    return (soundData, numSampleFrames, sampleRate, None, None)

# Pretty basic aifc file parser. Extracts the already encoded .aifc data metadata from the file
def process_aifc_file(f: BinaryIO) -> tuple[bytes, int, int]:
    # Open the .aifc file
    index = 0
    # Read data from the .aifc file
    
    # Read the "FORM" Chunk
    f.read(4) # "FORM"
    size = int.from_bytes(f.read(4), 'big')
    form_type = str(f.read(4), encoding='utf-8')
    if form_type != "AIFC":
        raise Exception("Not an AIFC file")
    # Read the rest of the chunks
    done = False
    chunks = {}
    chkID = "FORM"
    chunks["APPL"] = []
    while chkID != '':
        chkID = str(f.read(4), encoding='utf-8')
        size = int.from_bytes(f.read(4), 'big')
        data = f.read(size)
        chunk = {
            'size': size,
            'data': data
        }
        if chkID in chunks.keys():
            if type(chunks[chkID]) != list:
                chunks[chkID] = [chunks[chkID]]
            chunks[chkID].append(chunk)
        else:
            chunks[chkID] = chunk
    
    # Process the chunks
    
    # COMM Chunk: Sampling rate, compression type, number of channels
    #define CommonID 'COMM' /* ckID for Common Chunk */
    # typedef struct {
    #   ID ckID; /*  'COMM'  */
    #   long kDataSize;
    #   short numChannels; /* # audio channels */
    #   unsigned long numSampleFrames; /* # sample frames = samples/channel */
    #   short sampleSize; /* # bits/sample */
    #   extended sampleRate; /* sample_frames/sec */
    #   ID compressionType; /* compression type ID code */
    #   pstring compressionName; /* human-readable compression type name */
    # } CommonChunk;
    comm = chunks['COMM']
    data = comm['data']
    numChannels = int.from_bytes(data[0:2], 'big')
    numSampleFrames = int.from_bytes(data[2:6], 'big')
    sampleSize = int.from_bytes(data[6:8], 'big')
    sampleRateBytes = bytearray(data[8:18])
    sampleRateInt = int.from_bytes(sampleRateBytes, 'big')
    
    # Need to process the sample rate. it's an 80-bit extended floating point value stored in 10 bytes which nothing natively supports
    exp_int = int.from_bytes(sampleRateBytes[0:2], 'big') - 16383
    frac_int = int.from_bytes(sampleRateBytes[2:10], 'big')
    sampleRate = frac_int >> (64 - exp_int - 1)
    compressionType = str(data[18:22],encoding='utf-8')
    compressionNameLen = data[22]
    compressionName = str(data[23:23 + compressionNameLen], encoding='utf-8')
    
    # Make sure it's the correct compression type
    #if compressionType != "ADP9":
    #    raise Exception("Unknown compression format. Must be 'ADP9'. Did you use vadpcm_enc?")

    # Make sure it's the correct sample size
    if sampleSize != 16:
        raise Exception("Unsupported sample size. Must be 16 bit samples")
    # Compressed sample data
    # SSND Chunk contains the sample data
    ssnd = chunks['SSND']
    data = ssnd['data']
    ssndOffset = int.from_bytes(data[0:4], 'big')
    ssndBlockSize = int.from_bytes(data[4:8], 'big')
    
    # Pull out the APDCM Code Book from the first APPL chunk
    appl = chunks['APPL'][0]['data']
    # stoc + 0x0B + VADPCMCODES
    appl = appl[0x10:]
    version = int.from_bytes(appl[0:2], 'big')
    order = int.from_bytes(appl[2:4], 'big')
    nEntries = int.from_bytes(appl[4:6], 'big')
    tableData: list[int] = []
    for i in range(0, 16 * nEntries):
        index = 6 + order*i
        tableData.append(int.from_bytes(appl[index:index+order], 'big', signed=True))
    tableBytes = bytearray(0)
    for bookPoint in tableData:
        tableBytes += bookPoint.to_bytes(2, 'big', signed = True)

    # Pull out the loop crap from the other appl chunk
    loop = None
    if len(chunks['APPL']) > 1:
        appl = chunks['APPL'][1]['data']
        # stoc + 0x0B + VADPCMLOOPS
        appl = appl[0x14:]
        loop_start = int.from_bytes(appl[0:4], 'big')
        loop_end = int.from_bytes(appl[4:8], 'big')
        loop_count = int.from_bytes(appl[8:12], 'big')
        loop_state = []
        for i in range(0, 16):
            index = 12 + 2*i
            loop_state.append(int.from_bytes(appl[index:index+2], 'big'))
        loop = AdpcmLoop(loop_start, loop_end, loop_count, 0, loop_state)
    if ssndOffset != 0 or ssndBlockSize != 0:
        raise Exception("Unsupported SSND offset/block size")
    # Read the sample data. it's numSampleFrames * 9 / 8 / 2
    dataLen = int(ceil(numSampleFrames * 9 / 8 / 2))
    soundData = data[8:8 + dataLen]
    return soundData, numSampleFrames, sampleRate, AdpcmBook(order, nEntries, tableBytes), loop


