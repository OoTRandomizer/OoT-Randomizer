# Much of this is heavily inspired from and/or based on az64's / Deathbasket's MM randomizer
from __future__ import annotations
from enum import Enum
import io
import itertools
import os
import random
import zipfile
from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional, Any
from Audiobank import *
from MusicHelpers import process_sequence_mmr_zseq, process_sequence_mmrs, process_sequence_ootrs

from Rom import Rom
from Sequence import Sequence, SequenceGame
from Utils import compare_version, data_path

if TYPE_CHECKING:
    from Cosmetics import CosmeticsLog
    from Settings import Settings

AUDIOSEQ_DMADATA_INDEX: int = 4
AUDIOBANK_DMADATA_INDEX: int = 3
AUDIOTABLE_DMADATA_INDEX: int = 5

# Format: (Title, Sequence ID)
bgm_sequence_ids: tuple[tuple[str, int], ...] = (
    ("Hyrule Field", 0x02),
    ("Dodongos Cavern", 0x18),
    ("Kakariko Adult", 0x19),
    ("Battle", 0x1A),
    ("Boss Battle", 0x1B),
    ("Inside Deku Tree", 0x1C),
    ("Market", 0x1D),
    ("Title Theme", 0x1E),
    ("House", 0x1F),
    ("Jabu Jabu", 0x26),
    ("Kakariko Child", 0x27),
    ("Fairy Fountain", 0x28),
    ("Zelda Theme", 0x29),
    ("Fire Temple", 0x2A),
    ("Forest Temple", 0x2C),
    ("Castle Courtyard", 0x2D),
    ("Ganondorf Theme", 0x2E),
    ("Lon Lon Ranch", 0x2F),
    ("Goron City", 0x30),
    ("Miniboss Battle", 0x38),
    ("Temple of Time", 0x3A),
    ("Kokiri Forest", 0x3C),
    ("Lost Woods", 0x3E),
    ("Spirit Temple", 0x3F),
    ("Horse Race", 0x40),
    ("Ingo Theme", 0x42),
    ("Fairy Flying", 0x4A),
    ("Deku Tree", 0x4B),
    ("Windmill Hut", 0x4C),
    ("Shooting Gallery", 0x4E),
    ("Sheik Theme", 0x4F),
    ("Zoras Domain", 0x50),
    ("Shop", 0x55),
    ("Chamber of the Sages", 0x56),
    ("Ice Cavern", 0x58),
    ("Kaepora Gaebora", 0x5A),
    ("Shadow Temple", 0x5B),
    ("Water Temple", 0x5C),
    ("Gerudo Valley", 0x5F),
    ("Potion Shop", 0x60),
    ("Kotake and Koume", 0x61),
    ("Castle Escape", 0x62),
    ("Castle Underground", 0x63),
    ("Ganondorf Battle", 0x64),
    ("Ganon Battle", 0x65),
    ("Fire Boss", 0x6B),
    ("Mini-game", 0x6C),
)

fanfare_sequence_ids: tuple[tuple[str, int], ...] = (
    ("Game Over", 0x20),
    ("Boss Defeated", 0x21),
    ("Item Get", 0x22),
    ("Ganondorf Appears", 0x23),
    ("Heart Container Get", 0x24),
    ("Treasure Chest", 0x2B),
    ("Spirit Stone Get", 0x32),
    ("Heart Piece Get", 0x39),
    ("Escape from Ranch", 0x3B),
    ("Learn Song", 0x3D),
    ("Epona Race Goal", 0x41),
    ("Medallion Get", 0x43),
    ("Zelda Turns Around", 0x51),
    ("Master Sword", 0x53),
    ("Door of Time", 0x59),
    ("Ganons Rainbow Bridge", 0x5D),
)

ocarina_sequence_ids: tuple[tuple[str, int], ...] = (
    ("Prelude of Light", 0x25),
    ("Bolero of Fire", 0x33),
    ("Minuet of Forest", 0x34),
    ("Serenade of Water", 0x35),
    ("Requiem of Spirit", 0x36),
    ("Nocturne of Shadow", 0x37),
    ("Saria's Song", 0x44),
    ("Epona's Song", 0x45),
    ("Zelda's Lullaby", 0x46),
    ("Sun's Song", 0x47),
    ("Song of Time", 0x48),
    ("Song of Storms", 0x49),
)

credit_sequence_ids: tuple[tuple[str, int], ...] = (
    ("Zeldas Theme Orchestra", 0x52),
    ("Zeldas Ocarina Song", 0x66),
    ("Ending Credits Part 1", 0x67),
    ("Ending Credits Part 2", 0x68),
    ("Ending Credits Part 3", 0x69),
    ("Ending Credits Part 4", 0x6A),
)

fileselect_sequence_id: tuple[tuple[str, int], ...] = (
    ("File Select", 0x57),
)

# Represents actual sequence data, along with metadata for the sequence data block
class SequenceData:
    def __init__(self) -> None:
        self.address: int = -1
        self.size: int = -1
        self.data: bytearray = bytearray()


def process_sequences(rom: Rom, ids: Iterable[tuple[str, int]], seq_type: str = 'bgm', disabled_source_sequences: Optional[list[str]] = None,
                      disabled_target_sequences: Optional[dict[str, tuple[str, int]]] = None, include_custom: bool = True,
                      sequences: Optional[dict[str, Sequence]] = None, target_sequences: Optional[dict[str, Sequence]] = None,
                      groups: Optional[dict[str, list[str]]] = None, include_custom_audiobanks: bool = False,
                      log: CosmeticsLog = None) -> tuple[dict[str, Sequence], dict[str, Sequence], dict[str, list[str]]]:
    disabled_source_sequences = [] if disabled_source_sequences is None else disabled_source_sequences
    disabled_target_sequences = {} if disabled_target_sequences is None else disabled_target_sequences
    sequences = {} if sequences is None else sequences
    target_sequences = {} if target_sequences is None else target_sequences
    groups = {} if groups is None else groups

    # Process vanilla music data
    for bgm in ids:
        # Get sequence metadata
        name = bgm[0]
        cosmetic_name = name
        type = rom.read_int16(0xB89AE8 + (bgm[1] * 0x10))
        instrument_set = rom.read_byte(0xB89911 + 0xDD + (bgm[1] * 2))
        id = bgm[1]

        # Create new sequences
        seq = Sequence(name, cosmetic_name, seq_type, type, instrument_set, vanilla_id = id)
        target = Sequence(name, cosmetic_name, seq_type, type, instrument_set, replaces = id)

        # Special handling for file select/fairy fountain
        if seq.vanilla_id != 0x57 and cosmetic_name not in disabled_source_sequences:
            sequences[seq.cosmetic_name] = seq
        if cosmetic_name not in disabled_target_sequences:
            target_sequences[target.cosmetic_name] = target

    if not include_custom:
        return sequences, target_sequences, groups

    # If present, load the file containing custom music to exclude
    try:
        with open(os.path.join(data_path(), u'custom_music_exclusion.txt')) as excl_in:
            seq_exclusion_list = excl_in.readlines()
        seq_exclusion_list = [seq.rstrip() for seq in seq_exclusion_list if seq[0] != '#']
        seq_exclusion_list = [seq for seq in seq_exclusion_list if seq.endswith('.ootrs')]
    except FileNotFoundError:
        seq_exclusion_list = []

    # Process music data in data/Music/
    # Each sequence requires a valid .ootrs zip file
    # .ootrs files are just .zip files containing at minimum:
    #   .seq sequence file
    #   .meta metadata file
    # And optionally .zbank, .bankmeta, and .zsound files

    for dirpath, _, filenames in os.walk(os.path.join(data_path(), 'Music'), followlinks=True):
        for fname in filenames:
            # Skip if included in exclusion file
            if fname in seq_exclusion_list:
                continue

            filepath = os.path.join(dirpath, fname)
            seq = None
            try:
                if fname.lower().endswith('.ootrs'):
                    seq = process_sequence_ootrs(filepath, fname, seq_type, include_custom_audiobanks, groups)
                elif fname.lower().endswith('.zseq'):
                    seq = process_sequence_mmr_zseq(filepath, fname, seq_type, include_custom_audiobanks, groups)
                elif fname.lower().endswith('.mmrs'):
                    seq = process_sequence_mmrs(filepath, fname, seq_type, include_custom_audiobanks, groups)
                if seq:
                    sequences[seq.cosmetic_name] = seq
            except Exception as e:
                if log:
                    log.errors.append(f"Error processing custom sequence {fname} - {e}")
            continue

    return sequences, target_sequences, groups


def shuffle_music(log: CosmeticsLog, source_sequences: dict[str, Sequence], target_sequences: dict[str, Sequence],
                  music_mapping: dict[str, str], seq_type: str = "music") -> list[Sequence]:
    sequences = []
    favorites = log.src_dict.get('bgm_groups', {}).get('favorites', []).copy()

    if not source_sequences:
        raise Exception(f"Not enough custom {seq_type} ({len(source_sequences)}) to omit base Ocarina of Time sequences ({len(target_sequences)}).")

    # Shuffle the sequences
    sequence_ids = [name for name in source_sequences.keys() if name not in music_mapping.values()]
    random.shuffle(sequence_ids)
    sequence_ids.sort(key=lambda name: name not in favorites)
    del sequence_ids[len([name for name in target_sequences.keys() if name not in music_mapping]):]
    random.shuffle(sequence_ids)

    refill_needed = False
    for name, target_sequence in target_sequences.items():
        if target_sequence.cosmetic_name not in music_mapping:
            # If we've run out of sequences to place, refill sequence_ids
            if not sequence_ids:
                refill_needed = True
                sequence_ids = [name for name in source_sequences.keys()]
                random.shuffle(sequence_ids)
            sequence = source_sequences[sequence_ids.pop()].copy()
        else:
            sequence = source_sequences[music_mapping[target_sequence.cosmetic_name]].copy()
        sequences.append(sequence)
        sequence.replaces = target_sequence.replaces
        log.bgm[target_sequence.cosmetic_name] = sequence.cosmetic_name

    if refill_needed:
        log.errors.append(f"Not enough {seq_type} available to not have repeats. There were {len(source_sequences)} sequences available to fill {len(target_sequences)} target tracks.")
    return sequences


def rebuild_sequences(rom: Rom, sequences: list[Sequence], log: CosmeticsLog, symbols: dict[str, int]) -> None:
    CUSTOM_BANKS_SUPPORTED = "CFG_AUDIOBANK_TABLE_EXTENDED_ADDR" in symbols.keys()
    audioseq_dma_entry = rom.dma[AUDIOSEQ_DMADATA_INDEX]
    audioseq_start, audioseq_end, audioseq_size = audioseq_dma_entry.as_tuple()

    replacement_dict = {seq.replaces: seq for seq in sequences}
    # List of sequences (actual sequence data objects) containing the vanilla sequence data
    old_sequences = []
    bgmlist = [sequence_id for title, sequence_id in bgm_sequence_ids]
    fanfarelist = [sequence_id for title, sequence_id in fanfare_sequence_ids]
    ocarinalist = [sequence_id for title, sequence_id in ocarina_sequence_ids]
    creditlist = [sequence_id for title, sequence_id in credit_sequence_ids]
    fileselectlist = [sequence_id for title, sequence_id in fileselect_sequence_id]

    for i in range(0x6E):
        # Create new sequence object, an entry for the audio sequence
        entry = SequenceData()
        # Get the address for the entry's pointer table entry
        entry_address = 0xB89AE0 + (i * 0x10)
        # Extract the info from the pointer table entry
        entry.address = rom.read_int32(entry_address)
        entry.size = rom.read_int32(entry_address + 0x04)

        # If size > 0, read the sequence data from the rom into the sequence object
        if entry.size > 0:
            entry.data = rom.read_bytes(entry.address + audioseq_start, entry.size)
        else:
            seq = replacement_dict.get(i, None)
            if seq and 0 < entry.address < 128:
                if seq.replaces != 0x28:
                    seq.replaces = entry.address
                else:
                    # Special handling for file select/fairy fountain
                    entry.data = old_sequences[0x57].data
                    entry.size = old_sequences[0x57].size

        old_sequences.append(entry)

    # List of sequences containing the new sequence data
    new_sequences: list[SequenceData] = []
    address = 0
    # Byte array to hold the data for the whole audio sequence
    new_audio_sequence = []

    for i in range(0x6E):
        new_entry = SequenceData()
        # If sequence size is 0, the address doesn't matter and it doesn't effect the current address
        if old_sequences[i].size == 0:
            new_entry.address = old_sequences[i].address
        # Continue from the end of the new sequence table
        else:
            new_entry.address = address

        seq = replacement_dict.get(i, None)
        if seq:
            # If we are using a vanilla sequence, get its data from old_sequences
            if seq.vanilla_id != -1:
                new_entry.size = old_sequences[seq.vanilla_id].size
                new_entry.data = old_sequences[seq.vanilla_id].data
            else:
                # Read sequence info
                try:
                    if seq.name.endswith('.zseq'):
                        with open(seq.name, 'rb') as stream:
                            new_entry.data = bytearray(stream.read())
                            new_entry.size = len(new_entry.data)
                    else:
                        with zipfile.ZipFile(seq.name) as zip:
                            with zip.open(seq.seq_file, 'r') as stream:
                                new_entry.data = bytearray(stream.read())
                                new_entry.size = len(new_entry.data)
                    # Align sequences to 0x10
                    if new_entry.size % 0x10 != 0:
                        new_entry.data.extend(bytearray(0x10 - (new_entry.size % 0x10)))
                        new_entry.size += 0x10 - (new_entry.size % 0x10)
                    if new_entry.size <= 0x10:
                        raise Exception(f'Invalid sequence file "{seq.name}.seq"')
                    new_entry.data[1] = 0x20
                except FileNotFoundError as ex:
                    raise FileNotFoundError(f'No sequence file for: "{seq.name}"')
        else:
            new_entry.size = old_sequences[i].size
            new_entry.data = old_sequences[i].data

        # Check if we have already added this sequence. This happens if we have less available sequences than total sequences
        for new_seq in new_sequences:
            if (new_entry.size == new_seq.size) and (new_entry.data == new_seq.data):
                new_entry.address = new_seq.address # Use the address of the sequence that has already been added
                new_entry.data = [] # Clear the data so it doesn't get added again.
                break

        new_sequences.append(new_entry)

        # Concatenate the full audio sequence and the new sequence data
        if new_entry.data != [] and new_entry.size > 0:
            new_audio_sequence.extend(new_entry.data)
            # Increment the current address by the size of the new sequence
            address += new_entry.size

    new_address = audioseq_start
    # Check if the new audio sequence is larger than the vanilla one
    if address > audioseq_size:
        # Zero out the old audio sequence
        rom.buffer[audioseq_start:audioseq_end] = [0] * audioseq_size

        # Find free space and update dmatable
        new_address = rom.dma.free_space(address)
        audioseq_dma_entry.update(new_address, new_address + address)

    # Write new audio sequence file
    rom.write_bytes(new_address, new_audio_sequence)

    # If custom banks are supported, we're going to make copies of the banks to be used for fanfares
    # In that case, need to update the fanfare sequence's bank to point to the new one
    fanfare_bank_shift = 0x26 if CUSTOM_BANKS_SUPPORTED else 0

    # Update pointer table
    for i in range(0x6E):
        rom.write_int32(0xB89AE0 + (i * 0x10), new_sequences[i].address)
        rom.write_int32(0xB89AE0 + (i * 0x10) + 0x04, new_sequences[i].size)
        seq = replacement_dict.get(i, None)

    # Update instrument sets for bgm sequences
    for i in bgmlist:
        base = 0xB89911 + 0xDD + (i * 2)
        j = replacement_dict.get(i if new_sequences[i].size else new_sequences[i].address, None)
        if j:
            rom.write_byte(base, j.instrument_set)
    # Update instrument sets for fanfare sequences
    for i in fanfarelist:
        base = 0xB89911 + 0xDD + (i * 2)
        j = replacement_dict.get(i if new_sequences[i].size else new_sequences[i].address, None)
        if j:
            rom.write_byte(base, j.instrument_set + fanfare_bank_shift)
    #Update instrument sets for ocarina fanfare sequences
    for i in ocarinalist:
        base = 0xB89911 + 0xDD + (i * 2)
        j = replacement_dict.get(i if new_sequences[i].size else new_sequences[i].address, None)
        if j:
            rom.write_byte(base, j.instrument_set + fanfare_bank_shift)
    #Update instrument sets for credits sequences
    for i in creditlist:
        base = 0xB89911 + 0xDD + (i * 2)
        j = replacement_dict.get(i if new_sequences[i].size else new_sequences[i].address, None)
        if j:
            rom.write_byte(base, j.instrument_set)
    #Update instrument set for file select sequence
    for i in fileselectlist:
        base = 0xB89911 + 0xDD + (i * 2)
        j = replacement_dict.get(i if new_sequences[i].size else new_sequences[i].address, None)
        if j:
            rom.write_byte(base, j.instrument_set)

    # Patch new instrument sets (banks) and add new instrument sounds
    # Only if we were passed CFG_AUDIOBANK_TABLE_EXTENDED_ADDR via symbols which means we're on the right version.
    if not CUSTOM_BANKS_SUPPORTED:
        return

    # Builds new audio bank entrys for fanfares to prevent fanfares killing bgm in areas like Goron City
    bank_index_base = (rom.read_int32(symbols['CFG_AUDIOBANK_TABLE_EXTENDED_ADDR']) - 0x80400000) + 0x3480000
    # Build new fanfare banks by copying each entry in audiobank_index
    for i in range(0, 0x26):
        bank_entry = rom.read_bytes(bank_index_base + 0x10 + 0x10 * i, 0x10) # Get the vanilla entry
        bank_entry[9] = 1 # Update the cache type to 1
        rom.write_bytes(bank_index_base + 0x270 + 0x10 * i, bank_entry) # Write the new entry at the end of the bank table.
    rom.write_byte(bank_index_base + 0x01, 0x4C) # Updates AudioBank Index Header if no custom banks are present as this would be 0x26 which would crash the game if a fanfare was played

    added_banks: list[AudioBank] = [] # Store copies of all the banks we've added
    added_samples: list[Sample] = []  # Store copies of all the samples we've added
    new_bank_index = 0x4C
    instr_data = bytearray(0)  # Store all the new instrument data that will be added to the end of audiotable

    audiobank_dma_entry = rom.dma[AUDIOBANK_DMADATA_INDEX]
    audiotable_dma_entry = rom.dma[AUDIOTABLE_DMADATA_INDEX]
    audiobank_start, audiobank_end, audiobank_size = audiobank_dma_entry.as_tuple()
    audiotable_start, audiotable_end, audiotable_size = audiotable_dma_entry.as_tuple()

    instr_offset_in_file = audiotable_size
    bank_table_base = 0

    # Load OOT Audiobin
    AUDIOBANK_INDEX_ADDR = 0x00B896A0
    AUDIOBANK_ADDR = 0xD390
    AUDIOTABLE_INDEX_ADDR = 0xB8A1C0
    AUDIOTABLE_ADDR = 0x79470

    audiobank_index = rom.read_bytes(AUDIOBANK_INDEX_ADDR, 0x2A0)
    audiobank = rom.read_bytes(AUDIOBANK_ADDR, 0x1CA50)
    audiotable_index = rom.read_bytes(AUDIOTABLE_INDEX_ADDR, 0x80) # Read audiotable index into bytearray
    audiotable = rom.read_bytes(AUDIOTABLE_ADDR, 0x460AD0) # Read audiotable (samples) into bytearray

    oot_audiobin: Audiobin = Audiobin(audiobank, audiobank_index, audiotable, audiotable_index)

    # Load MM Audiobin if needed
    mm_audiobin: Audiobin = None
    for i in range(0x6E): # Loop through all the replacement sequences
        j = replacement_dict.get(i if new_sequences[i].size else new_sequences[i].address, None)
        if j and j.game == SequenceGame.MM: # we have at least one MM sequence so load the audiobin
            with zipfile.ZipFile(os.path.join(data_path(), 'Music', 'MM.audiobin')) as mm_audiobin_zip:
                mm_audiobank = bytearray(mm_audiobin_zip.read("Audiobank"))
                mm_audiobank_index = bytearray(mm_audiobin_zip.read("Audiobank_index"))
                mm_audiotable = bytearray(mm_audiobin_zip.read("Audiotable"))
                mm_audiotable_index = bytearray(mm_audiobin_zip.read("Audiotable_index"))
                mm_audiobin = Audiobin(mm_audiobank, mm_audiobank_index, mm_audiotable, mm_audiotable_index)
            break

    for i in range(0x6E):
        bank_table_base = (rom.read_int32(symbols['CFG_AUDIOBANK_TABLE_EXTENDED_ADDR']) - 0x80400000) + 0x3480000
        seq_bank_base = 0xB89911 + 0xDD + (i * 2)
        j = replacement_dict.get(i if new_sequences[i].size else new_sequences[i].address, None)
        if j is not None and j.new_instrument_set:
            # Open the .ootrs/.mmrs file
            newbank: AudioBank = None
            vanilla_mm_bank: AudioBank = None
            bankdata = None
            bank_entry = None
            audiobin = oot_audiobin if j.game == SequenceGame.OOT else mm_audiobin # Load the correct audiobin

            # Handle MMR .zseq files. These use vanilla MM banks so just build the bank using the data from the MM audiobin. We'll update it with OOT data later
            if j.name.lower().endswith('.zseq'):
                # Get the entry from Audiobank_index
                offset = 0x10 + j.instrument_set*0x10
                bank_entry = audiobin.Audiobank_index[offset:offset+0x10]
                # Get the bank
                vanilla_mm_bank = AudioBank(bank_entry, audiobin.Audiobank, audiobin.Audiotable, audiobin.Audiotable_index)
                vanilla_mm_bank.table_entry[0x0A] = 1
                bankdata = vanilla_mm_bank.bank_data
            else: # MMRS or OOTRs with custom banks
                with zipfile.ZipFile(j.name) as zip:
                    # Check if we have a zbank file because MMR sequences might not.
                    if j.zbank_file:
                        bankdata = bytearray(zip.read(j.zbank_file)) # Load the .zbank file
                        bank_meta = bytearray(zip.open(j.bankmeta, 'r').read())
                        bank_entry = bytearray(4) + len(bankdata).to_bytes(4, 'big') + bank_meta
                    elif j.game == SequenceGame.MM: # MM sequence without a zbank:
                        offset = 0x10 + j.instrument_set*0x10
                        bank_entry = audiobin.Audiobank_index[offset:offset+0x10]
                        # Get the bank
                        vanilla_mm_bank = AudioBank(bank_entry, audiobin.Audiobank, audiobin.Audiotable, audiobin.Audiotable_index)
                        vanilla_mm_bank.table_entry[0x0A] = 1
                        bankdata = vanilla_mm_bank.bank_data
                    else: # Probably should never get here
                        raise Exception("No bank data available for custom music: " + j.cosmetic_name)

            # Update the bank's cache type based on bgm/fanfare
            bank_entry[9] = 1 if j.seq_type == 'fanfare' else 2
            # Check if we have already added this bank
            for added_bank in added_banks:
                if added_bank.original_data == bankdata:
                    newbank = added_bank
                    if added_bank.table_entry[8:16] != bank_entry[8:16]: # We've already added this bank but it has different metadata
                        found: bool = False
                        for bank in added_bank.duplicate_banks:
                            if bank.table_entry[8:16] == bank_entry[8:16]:
                                found = True
                                newbank = bank
                                break
                        if not found:
                            dupe_bank = AudioBank(bank_entry, bytearray(0), None, None)
                            dupe_bank.bank_index = new_bank_index
                            new_bank_index += 1
                            newbank.duplicate_banks.append(dupe_bank) # Make a new bank with just the meta and add it as a duplicate so it can be added separately but point to the same data.
                            newbank = dupe_bank
                    break

            if not newbank:
                if vanilla_mm_bank:
                    newbank = vanilla_mm_bank
                else:
                    newbank = AudioBank(bank_entry, bankdata, audiobin.Audiotable, audiobin.Audiotable_index)
                newbank.bank_index = new_bank_index

                zsound_samples: list[Sample] = []
                # Handle new zsounds
                tempbank = AudioBank(bank_entry, bankdata, None, None)
                if j.name.lower().endswith('.ootrs') or j.name.lower().endswith('.mmrs'):
                    with zipfile.ZipFile(j.name) as zip:
                        for zsound in j.zsounds:
                            if zsound['tempaddr']: # Old style/MMR zsound that uses the stupid temp address thing
                                for sample in tempbank.get_all_samples():
                                    if sample.addr == zsound['tempaddr']:
                                        parent = sample.parent
                                        if type(parent) == Instrument:
                                            if parent.highNoteSample and parent.highNoteSample.addr == sample.addr:
                                                sample = newbank.instruments[parent.inst_id].highNoteSample
                                            elif parent.normalNoteSample and parent.normalNoteSample.addr == sample.addr:
                                                sample = newbank.instruments[parent.inst_id].normalNoteSample
                                            elif parent.lowNoteSample and parent.lowNoteSample.addr == sample.addr:
                                                sample = newbank.instruments[parent.inst_id].lowNoteSample
                                        if type(parent) == Drum:
                                            sample = newbank.drums[parent.drum_id].sample
                                        if type(parent) == SFX:
                                            sample = newbank.SFX[parent.sfx_id].sample
                                        sample.data = zip.read(zsound['file'])
                                        sample.addr = -1 # Set the sample address to -1 so that we know it's from a zsound
                                        zsound_samples.append(sample)
                                        break
                                pass
                            else:
                                curr_sample_data = zip.read(zsound['file'])
                                already_added = False
                                sample: Sample = None

                                # Get the sample reference from the new bank
                                if zsound['type'] == 'DRUM':
                                    sample = newbank.drums[zsound['index']].sample
                                if zsound['type'] == 'SFX':
                                    sample = newbank.SFX[zsound['index']].sample
                                if zsound['type'] == 'INST':
                                    if zsound['alt'] == 'LOW':
                                        sample = newbank.instruments[zsound['index']].lowNoteSample
                                    elif zsound['alt'] == 'NORM':
                                        sample = newbank.instruments[zsound['index']].normalNoteSample
                                    elif zsound['alt'] == 'HIGH':
                                        sample = newbank.instruments[zsound['index']].highNoteSample
                                sample.data = curr_sample_data
                                sample.addr = -1 # Set the sample address to -1 so that we know it's from a zsound
                                zsound_samples.append(sample)

                # For MM, update the bank's samples with OOT addresses if they exist:
                mm_samples_to_add: list[Sample] = []
                # Cross reference MM instrument data against OOT and update accordingly
                if j.game == SequenceGame.MM:
                    all_samples = newbank.get_all_samples()
                    all_samples = [sample for sample in all_samples if sample.addr != -1] # Skip samples that are new ZSOUNDS because we'll handle them later
                    for sample in all_samples:
                        match = oot_audiobin.find_sample_in_audiobanks(sample.data)
                        if match: # Found a matching sample in OOT. Just update the bank with the corresponding sample address
                            # Update the sample's offset in the new bank
                            newbank.bank_data[sample.bank_offset+4:sample.bank_offset+8] = match.audiotable_addr.to_bytes(4, 'big')
                        else: # Didn't find a matching sample, Will have to add it later
                            mm_samples_to_add.append(sample)
                    i = 0
                    while i < len(zsound_samples):
                        match = oot_audiobin.find_sample_in_audiobanks(zsound_samples[i].data)
                        if match: # Found a matching sample in OOT. Just update the bank with the corresponding sample address and remove if from zsound list
                            # Update the sample's offset in the new bank
                            newbank.bank_data[zsound_samples[i].bank_offset+4:zsound_samples[i].bank_offset+8] = match.audiotable_addr.to_bytes(4, 'big')
                            zsound_samples.pop(i)
                            continue
                        i += 1

                # Create a list of all samples that need to be added.
                # This includes new samples, and samples from MM that don't exist in OOT
                for sample_to_add in zsound_samples + mm_samples_to_add:
                    # Check if we've already added this sample's data
                    already_added = False
                    for added_sample in added_samples:
                        if sample_to_add.data == added_sample.data:
                            # Already added this sample, just update the bank
                            newbank.bank_data[sample_to_add.bank_offset+4:sample_to_add.bank_offset+8] = added_sample.audiotable_addr.to_bytes(4, 'big')
                            already_added = True
                            break
                    if not already_added:
                        instr_data += sample_to_add.data
                         # Pad instrument data to 0x10
                        sample_to_add.audiotable_addr = instr_offset_in_file
                        instr_offset_in_file += len(sample_to_add.data)
                        if len(instr_data) % 0x10 != 0:
                            padding_length = 0x10 - (len(instr_data) % 0x10)
                            instr_data += (bytearray(padding_length))
                            instr_offset_in_file += padding_length
                        # Update the sample address in the bank data
                        newbank.bank_data[sample_to_add.bank_offset+4:sample_to_add.bank_offset+8] = sample_to_add.audiotable_addr.to_bytes(4, 'big')
                        added_samples.append(sample_to_add)

                added_banks.append(newbank)
                new_bank_index += 1

            # Update the sequence's bank (instrument set)
            rom.write_byte(seq_bank_base, newbank.bank_index)


    # Patch the new instrument data into the ROM in a new file.
    # If there is any instrument data to add, move the entire audiotable file to a new location in the ROM.
    if len(instr_data) > 0:
        # Read the original audiotable data
        audiotable_data = rom.read_bytes(audiotable_start, audiotable_size)
        # Zeroize existing file
        rom.write_bytes(audiotable_start, [0] * audiotable_size)
        # Add the new data
        audiotable_data += instr_data
        # Get new address for the file
        new_audiotable_start = rom.dma.free_space(len(audiotable_data))
        # Write the file to the new address
        rom.write_bytes(new_audiotable_start, audiotable_data)
        # Update DMA
        audiotable_dma_entry.update(new_audiotable_start, new_audiotable_start + len(audiotable_data))
        log.instr_dma_index = audiotable_dma_entry.index

    # Add new audio banks
    new_bank_data = bytearray(0)
    # Read the original audiobank data
    audiobank_data = rom.read_bytes(audiobank_start, audiobank_size)
    new_bank_offset = len(audiobank_data)
    for bank in added_banks:
        # Sample pointers should already be correct now
        # bank.update_zsound_pointers()
        bank.offset = new_bank_offset
        #absolute_offset = new_audio_banks_addr + new_bank_offset
        bank_entry = bank.build_entry(new_bank_offset)
        rom.write_bytes(bank_table_base + 0x10 + bank.bank_index * 0x10, bank_entry)
        for dupe_bank in bank.duplicate_banks:
            bank_entry = bytearray(dupe_bank.build_entry(new_bank_offset))
            bank_entry[4:8] = bank.size.to_bytes(4, 'big')
            rom.write_bytes(bank_table_base + 0x10 + dupe_bank.bank_index * 0x10, bank_entry)
        new_bank_data += bank.bank_data
        new_bank_offset += len(bank.bank_data)

    # If there is any audiobank data to add, move the entire audiobank file to a new place in ROM. Update the existing dmadata record
    if len(new_bank_data) > 0:
        # Zeroize existing file
        rom.write_bytes(audiobank_start, [0] * audiobank_size)
        # Add the new data
        audiobank_data += new_bank_data
        # Get new address for the file
        new_audio_banks_addr = rom.dma.free_space(len(audiobank_data))
        # Write the file to the new address
        rom.write_bytes(new_audio_banks_addr, audiobank_data)
        # Update DMA
        audiobank_dma_entry.update(new_audio_banks_addr, new_audio_banks_addr + len(audiobank_data))
        log.bank_dma_index = audiobank_dma_entry.index
        # Update size of bank table in the Audiobank table header.
        rom.write_bytes(bank_table_base, new_bank_index.to_bytes(2, 'big'))

    # Update the init heap size. This size is normally hardcoded based on the number of audio banks.
    init_heap_size = rom.read_int32(0xB80118)
    init_heap_size += (new_bank_index - 0x26)*0x20
    rom.write_int32(0xB80118, init_heap_size)
    log.added_banks = added_banks


def rebuild_pointers_table(rom: Rom, sequences: list[Sequence], log: CosmeticsLog, symbols: dict[str, int]) -> None:
    for sequence in [s for s in sequences if s.vanilla_id and s.replaces]:
        bgm_sequence = rom.original.read_bytes(0xB89AE0 + (sequence.vanilla_id * 0x10), 0x10)
        bgm_instrument = rom.original.read_int16(0xB89910 + 0xDD + (sequence.vanilla_id * 2))
        rom.write_bytes(0xB89AE0 + (sequence.replaces * 0x10), bgm_sequence)
        rom.write_int16(0xB89910 + 0xDD + (sequence.replaces * 2), bgm_instrument)

    # Write Fairy Fountain instrument to File Select (uses same track but different instrument set pointer for some reason)
    rom.write_int16(0xB89910 + 0xDD + (0x57 * 2), rom.read_int16(0xB89910 + 0xDD + (0x28 * 2)))


def randomize_music(rom: Rom, settings: Settings, log: CosmeticsLog, symbols: dict[str, int]) -> None:
    shuffled_sequences = shuffled_fanfare_sequences = []
    sequences = fanfare_sequences = target_sequences = target_fanfare_sequences = bgm_groups = fanfare_groups = {}
    disabled_source_sequences = log.src_dict.get('bgm_groups', {}).get('exclude', []).copy()
    disabled_target_sequences = {}
    available_sequences = log.src_dict.get('sequences_available', {}) if not settings.generating_patch_file else {}
    music_mapping = log.src_dict.get('bgm', {}).copy()
    bgm_ids = {bgm[0]: bgm for bgm in bgm_sequence_ids}
    ff_ids = {bgm[0]: bgm for bgm in fanfare_sequence_ids}
    ocarina_ids = {bgm[0]: bgm for bgm in ocarina_sequence_ids}
    credits_ids = {bgm[0]: bgm for bgm in credit_sequence_ids}

    # If generating a patch file, disallow custom sequences.
    custom_sequences_enabled = not settings.generating_patch_file
    custom_audiobanks_enabled = True
    if not custom_sequences_enabled and (settings.background_music == 'random_custom_only' or settings.fanfares == 'random_custom_only'):
        log.errors.append("Custom music is disabled when creating patch files. Only randomizing vanilla music.")

    # If generating from patch, do a version check to make sure custom sequences are supported.
    if settings.patch_file != '':
        rom_version_bytes = rom.read_version_bytes()
        rom_version = f'{rom_version_bytes[0]}.{rom_version_bytes[1]}.{rom_version_bytes[2]}'
        if compare_version(rom_version, '7.1.123') < 0: # Check if custom sequences with custom banks are supported
            custom_audiobanks_enabled = False
        if compare_version(rom_version, '4.11.13') < 0:
            log.errors.append("Custom music is not supported by this patch version. Only randomizing vanilla music.")
            custom_sequences_enabled = False

    # If "sequences_available" is in the cosmetics plando, don't bother trying to scan for custom sequences.
    if available_sequences:
        custom_sequences_enabled = False

    # Check if we have mapped music for BGM, Fanfares, Ocarina Songs or Credits Sequences
    bgm_mapped = any(name in music_mapping for name in bgm_ids)
    ff_mapped = any(name in music_mapping for name in ff_ids)
    ocarina_mapped = any(name in music_mapping for name in ocarina_ids)
    credits_mapped = any(name in music_mapping for name in credits_ids)

    # Flag sequence locations that are set to off for disabling.
    disabled_ids = []
    if settings.background_music == 'off':
        disabled_ids += [music_id for music_id in bgm_ids.values()]
    if settings.fanfares == 'off':
        disabled_ids += [music_id for music_id in ff_ids.values()]
        if settings.ocarina_fanfares:
            disabled_ids += [music_id for music_id in ocarina_ids.values()]
    for bgm in itertools.chain(bgm_ids.values(), ff_ids.values(), ocarina_ids.values()):
        if music_mapping.get(bgm[0], '') == "None":
            disabled_target_sequences[bgm[0]] = bgm
            del music_mapping[bgm[0]]
    for bgm in disabled_ids:
        if bgm[0] not in music_mapping:
            disabled_target_sequences[bgm[0]] = bgm

    # Map music to itself if music is set to normal.
    normal_ids = []
    if settings.background_music == 'normal' and bgm_mapped:
        normal_ids += [music_id for music_id in bgm_ids.values()]
    if settings.fanfares == 'normal' and (ff_mapped or ocarina_mapped):
        normal_ids += [music_id for music_id in ff_ids.values()]
    if settings.fanfares == 'normal' and ocarina_mapped:
        normal_ids += [music_id for music_id in ocarina_ids.values()]
    if settings.credits_music == 'false' and credits_mapped:
        normal_ids += [music_id for music_id in credits_ids.values()]
    for bgm in normal_ids:
        if bgm[0] not in music_mapping:
            music_mapping[bgm[0]] = bgm[0]

    # Include ocarina songs in fanfare pool if checked
    if settings.ocarina_fanfares or ocarina_mapped:
        ff_ids.update(ocarina_ids)

    # Include credits sequences in music pool if checked
    if settings.credits_music or credits_mapped:
        bgm_ids.update(credits_ids)

    # Grab our lists of sequences.
    if settings.background_music in ['random', 'random_custom_only'] or bgm_mapped:
        sequences, target_sequences, bgm_groups = process_sequences(rom, bgm_ids.values(), 'bgm', disabled_source_sequences, disabled_target_sequences, custom_sequences_enabled, include_custom_audiobanks=custom_audiobanks_enabled, log=log)
        if settings.background_music == 'random_custom_only':
            sequences = {name: seq for name, seq in sequences.items() if name not in bgm_ids or name in music_mapping.values()}
        if available_sequences:
            for sequence_name in available_sequences.get("bgm", []):
                sequences[sequence_name] = Sequence(sequence_name, sequence_name, 'bgm')

    if settings.fanfares in ['random', 'random_custom_only'] or ff_mapped or ocarina_mapped:
        fanfare_sequences, target_fanfare_sequences, fanfare_groups = process_sequences(rom, ff_ids.values(), 'fanfare', disabled_source_sequences, disabled_target_sequences, custom_sequences_enabled, include_custom_audiobanks=custom_audiobanks_enabled, log=log)
        if settings.fanfares == 'random_custom_only':
            fanfare_sequences = {name: seq for name, seq in fanfare_sequences.items() if name not in ff_ids or name in music_mapping.values()}
        if available_sequences:
            for sequence_name in available_sequences.get("fanfare", []):
                fanfare_sequences[sequence_name] = Sequence(sequence_name, sequence_name, 'fanfare')

    # Handle groups.
    plando_groups = {n: s for n, s in log.src_dict.get('bgm_groups', {}).get('groups', {}).items()}
    bgm_groups_full = chain_groups([(n, s) for n, s in itertools.chain(bgm_groups.items(), plando_groups.items())], sequences)
    ff_groups_full = chain_groups([(n, s) for n, s in itertools.chain(fanfare_groups.items(), plando_groups.items())], fanfare_sequences)
    bgm_groups = {n: s.copy() for n, s in bgm_groups_full.items()}
    ff_groups = {n: s.copy() for n, s in ff_groups_full.items()}
    for target, mapping in music_mapping.copy().items():
        if target in bgm_ids:
            groups_full_alias = bgm_groups_full
            groups_alias = bgm_groups
            sequences_alias = sequences
        elif target in ff_ids:
            groups_full_alias = ff_groups_full
            groups_alias = ff_groups
            sequences_alias = fanfare_sequences
        else:
            log.errors.append(f'Target sequence "{target}" from plando file is invalid.')
            del music_mapping[target]
            continue

        source = mapping
        if isinstance(mapping, list):
            # Try to find a valid source in the defined list
            while len(mapping) > 0:
                random.shuffle(mapping)
                source = music_mapping[target] = mapping.pop()

                if source.startswith('#'):
                    group_name = source[1:]
                    group = groups_alias.get(group_name, None)

                    # Check if group exists.
                    if group is not None:
                        # Check if we need to refill this group from the source dictionary.
                        if not group:
                            groups_alias[group_name] = groups_full_alias.get(group_name, []).copy()
                            group = groups_alias[group_name]

                        if group:
                            random.shuffle(group)
                            source = music_mapping[target] = group.pop()
                            if source in sequences_alias:
                                break

                    log.errors.append(f"Warning: Group '{source}' linked to '{target}' does not have a valid custom sequence. Ignoring!")
                else:
                    break

            if len(mapping) == 0 and source not in sequences_alias:
                del music_mapping[target]
                log.errors.append(f"Target Sequence '{target}' does not have a valid 'bgm_groups' entry.")
                continue

        elif mapping.startswith('#'):
            group_name = source[1:]
            group = groups_alias.get(group_name, None)

            # Check if group exists.
            if group is not None:
                # Check if we need to refill this group from the source dictionary.
                if not group:
                    groups_alias[group_name] = groups_full_alias.get(group_name, []).copy()
                    group = groups_alias[group_name]

                if group:
                    random.shuffle(group)
                    source = music_mapping[target] = group.pop()

        # Check if mapped sequence exists.
        if source not in sequences_alias:
            del music_mapping[target]
            log.errors.append(f"Sequence '{source}' mapped to '{target}' was not found.")

    # Shuffle the sequences.
    if sequences and target_sequences:
        shuffled_sequences = shuffle_music(log, sequences, target_sequences, music_mapping)
    if fanfare_sequences and target_fanfare_sequences:
        shuffled_fanfare_sequences = shuffle_music(log, fanfare_sequences, target_fanfare_sequences, music_mapping, "fanfares")

    # Ensure disabled sequences are flagged in cosmetics log
    for name in disabled_target_sequences:
        log.bgm[name] = "None"

    # If "sequences_available" is in the cosmetic plando, just skip the actual patching portion and leave that to the web patcher
    if available_sequences:
        return

    # Patch the randomized sequences into the ROM.
    patch_music = rebuild_sequences if custom_sequences_enabled else rebuild_pointers_table
    patch_music(rom, shuffled_sequences + shuffled_fanfare_sequences, log, symbols)

    if disabled_target_sequences:
        disable_music(rom, log, disabled_target_sequences.values())


def disable_music(rom: Rom, log: CosmeticsLog, ids: Iterable[tuple[str, int]]) -> None:
    # First track is no music
    blank_track = rom.read_bytes(0xB89AE0 + (0 * 0x10), 0x10)
    for bgm in ids:
        rom.write_bytes(0xB89AE0 + (bgm[1] * 0x10), blank_track)


def restore_music(rom: Rom) -> None:
    # Restore all music from original
    for bgm in bgm_sequence_ids + fanfare_sequence_ids + ocarina_sequence_ids:
        bgm_sequence = rom.original.read_bytes(0xB89AE0 + (bgm[1] * 0x10), 0x10)
        rom.write_bytes(0xB89AE0 + (bgm[1] * 0x10), bgm_sequence)
        bgm_instrument = rom.original.read_int16(0xB89910 + 0xDD + (bgm[1] * 2))
        rom.write_int16(0xB89910 + 0xDD + (bgm[1] * 2), bgm_instrument)

    # restore file select instrument
    bgm_instrument = rom.original.read_int16(0xB89910 + 0xDD + (0x57 * 2))
    rom.write_int16(0xB89910 + 0xDD + (0x57 * 2), bgm_instrument)

    # Rebuild audioseq
    orig_start, orig_end, orig_size = rom.original.dma[AUDIOSEQ_DMADATA_INDEX].as_tuple()
    rom.write_bytes(orig_start, rom.original.read_bytes(orig_start, orig_size))

    # If Audioseq was relocated
    dma_entry = rom.dma[AUDIOSEQ_DMADATA_INDEX]
    start, end, size = dma_entry.as_tuple()
    if start != orig_start:
        # Zero out old audioseq
        rom.write_bytes(start, [0] * size)
        dma_entry.update(orig_start, orig_end, start)


def chain_groups(group_list: list[tuple[str, list[str] | str]], sequences: dict[str, Sequence]) -> dict[str, list[str]]:
    result = {}
    for group_name, sequence_names in group_list:
        if isinstance(sequence_names, list):
            result.setdefault(group_name, []).extend(ns for ns in sequence_names if ns in sequences)
        elif sequence_names in sequences:
            result.setdefault(group_name, []).append(sequence_names)
    return result
