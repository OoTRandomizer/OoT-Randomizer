# Sequence Processing Functions in the form:
# def process_sequence_func(file_name: str, seq_type: str, include_custom_audiobanks: bool)
# return a Sequence object if it matches seq_type + include_custom_audiobank rule, return None otherwise

import io
import os
import zipfile
from Sequence import Sequence, SequenceGame
from Utils import data_path

def process_sequence_mmr_zseq(filepath: str, file_name: str, seq_type: str, include_custom_audiobanks: bool, groups) -> Sequence:
    split = file_name.split('.zseq')
    base = split[0]
    split = base.split('_')

    if len(split) != 3:
        raise Exception("Error while processing MMR .zseq " + file_name + ": Not enough parameters in the file name")

    cosmetic_name = split[0]
    instrument_set = split[1]
    categories = split[2]

    type_match = False
    mmrs_categories = categories.split('-')
    if seq_type.lower() == 'fanfare' and ('8' in mmrs_categories or '9' in mmrs_categories or '10' in mmrs_categories):
        type_match = True
    elif seq_type.lower() == 'bgm' and not ('8' in mmrs_categories or '9' in mmrs_categories or '10' in mmrs_categories):
        type_match = True

    if not type_match:
        return None

    seq_file = filepath
    seq = Sequence(filepath, cosmetic_name, seq_type=seq_type, seq_file = seq_file, instrument_set = instrument_set)
    seq.game = SequenceGame.MM
    seq.new_instrument_set = True
    return seq

def process_sequence_mmrs(filepath: str, file_name: str, seq_type: str, include_custom_audiobanks: bool, groups) -> Sequence:
    if not include_custom_audiobanks:
        return None

    with zipfile.ZipFile(filepath) as zip:
        seq_file = None
        zbank_file = None
        bankmeta_file = None
        for f in zip.namelist():
            # Uncomment if MMR ever decides to wisen up and use a common format
            #if f.endswith(".meta"):
            #    meta_file = f
            #    continue
            if f.endswith(".zseq") or f.endswith(".seq"):
                seq_file = f
                continue
            if f.endswith(".zbank"):
                zbank_file = f
                continue
            if f.endswith(".bankmeta"):
                bankmeta_file = f
                continue

        if not seq_file:
            raise FileNotFoundError(f'No .seq file in: "{file_name}". This should never happen')
        if zbank_file and not bankmeta_file:
            raise FileNotFoundError(f'Custom track "{file_name}" contains .zbank but no .bankmeta')
        type_match = False
        if 'categories.txt' in zip.namelist():
            mmrs_categories_txt = zip.read('categories.txt').decode()
            delimitingChar: str = ','
            if '-' in mmrs_categories_txt: # MMR is ridiculous...
                delimitingChar = '-'
            elif '\n' in mmrs_categories_txt:
                delimitingChar = '\n'
            mmrs_categories = mmrs_categories_txt.split(delimitingChar)
            if seq_type.lower() == 'fanfare' and ('8' in mmrs_categories or '9' in mmrs_categories or '10' in mmrs_categories):
                type_match = True
            elif seq_type.lower() == 'bgm' and not ('8' in mmrs_categories or '9' in mmrs_categories or '10' in mmrs_categories):
                type_match = True
        else:
            raise Exception("OWL LIED TO ME")

        if type_match:
            if zbank_file:
                instrument_set = '-'
            else:
                instrument_set = int(seq_file.split(".zseq")[0], 16) # Get the instrument set from the .zseq file name
            cosmetic_name, _ext = os.path.splitext(file_name)
            # Create new sequence
            seq = Sequence(filepath, cosmetic_name, seq_type=seq_type, seq_file = seq_file, instrument_set = instrument_set)
            if zbank_file:
                seq.zbank_file = zbank_file
                seq.bankmeta = bankmeta_file
            seq.zsounds = []

            seq.game = SequenceGame.MM
            seq.new_instrument_set = True # MM sequences always require new instrument set.
            # Make sure we have the MM audio binaries
            if not os.path.exists(os.path.join(data_path(), 'Music', 'MM.audiobin')):
                # Raise error. Maybe just skip and log a warning?
                raise FileNotFoundError(".MMRS sequence found but missing MM.audiobin")

            for f in zip.namelist():
                if f.lower().endswith(".zsound"):
                    split: str = f.split('.zsound')
                    split = split[0].split('_')
                    zsound = {
                        'type': None,
                        'index': None,
                        'alt': None,
                        'file': f,
                        'tempaddr': int(split[1], 16)
                    }
                    seq.zsounds.append(zsound)
            return seq
        return None

def process_sequence_ootrs(filepath: str, file_name: str, seq_type: str, include_custom_audiobanks: bool, groups) -> Sequence:
    with zipfile.ZipFile(filepath) as zip:
        # Make sure meta file and seq file exists
        meta_file = None
        seq_file = None
        zbank_file = None
        bankmeta_file = None
        for f in zip.namelist():
            if '/' in f: # Only read files in the root of the archive
                continue
            if f.endswith(".meta"):
                meta_file = f
                continue
            if f.endswith(".seq") or f.endswith(".zseq"):
                seq_file = f
                continue
            if f.endswith(".zbank"):
                if not include_custom_audiobanks: # Check if we are excluding sequences with custom banks
                    return None
                zbank_file = f
                continue
            if f.endswith(".bankmeta"):
                bankmeta_file = f
                continue

        if not meta_file:
            raise FileNotFoundError(f'No .meta file in: "{file_name}". This should never happen')
        if not seq_file:
            raise FileNotFoundError(f'No .seq file in: "{file_name}". This should never happen')
        if zbank_file and not bankmeta_file:
            raise FileNotFoundError(f'Custom track "{file_name}" contains .zbank but no .bankmeta')

        instrument_set = '-'
        cosmetic_name = filepath
        type_match = False

        # Read meta info
        with zip.open(meta_file, 'r') as stream:
            lines = io.TextIOWrapper(stream).readlines() # Use TextIOWrapper in order to get text instead of binary from the seq.
        # Strip newline(s)
        lines = [line.rstrip() for line in lines]
        cosmetic_name = lines[0]
        instrument_set = lines[1]
        if len(lines) < 3 and seq_type == 'bgm':
            type_match = True
        elif len(lines) >= 3 and lines[2].lower() == seq_type.lower():
            type_match = True

        if len(lines) >= 4:
            seq_groups = lines[3].split(',')
            for group in seq_groups:
                group = group.strip()
                if group not in groups:
                    groups[group] = []
                groups[group].append(cosmetic_name)

        if type_match:
            # Create new sequence
            seq = Sequence(filepath, cosmetic_name, seq_type=seq_type, seq_file = seq_file, instrument_set = instrument_set)
            if zbank_file:
                seq.zbank_file = zbank_file
                seq.bankmeta = bankmeta_file
            seq.zsounds = []

            if seq.instrument_set < 0x00 or seq.instrument_set > 0x25:
                raise Exception(f'{seq.name}: OOT Sequence instrument set must be in range [0x00, 0x25]')
            if seq.cosmetic_name == "None":
                raise Exception(f'{seq.name}: Sequences should not be named "None" as that is used for disabled music.')

            try:
                # Process ZSOUND lines. Make these lines in the format of ZSOUND:file_path:temp_addr
                for line in lines:
                    tokens = line.split(":")
                    if tokens[0] == "ZSOUND":
                        zsound = {
                            'type': tokens[1],
                            'index': int(tokens[2]),
                            'alt': tokens[3],
                            'file': tokens[4],
                            'tempaddr': None
                        }
                        seq.zsounds.append(zsound)
            except:
                seq.zsounds.clear()
                # Error occurred using the new way, try the old way
                for line in lines:
                    tokens = line.split(":")
                    if tokens[0] == "ZSOUND":
                        zsound = {
                            'type': None,
                            'index': None,
                            'alt': None,
                            'file': tokens[1],
                            'tempaddr': int(tokens[2], 16)
                        }
                        seq.zsounds.append(zsound)
            return seq
        return None
