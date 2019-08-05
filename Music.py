#Much of this is heavily inspired from and/or based on az64's / Deathbasket's MM randomizer

import random
import os


# Format: (Title, Sequence ID)
bgm_sequence_ids = [
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
    ("Mini-game", 0x6C)
]

fanfare_sequence_ids = [
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
    ("Door of Time", 0x59)
]

ocarina_sequence_ids = [
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
    ("Song of Storms", 0x49)
]

# Represents the information associated with a sequence, aside from the sequence data itself
class TableEntry(object):
    def __init__(self, name, cosmetic_name, type = 0x0202, instrument_set = 0x03, replaces = -1, vanilla_id = -1):
        self.name = name
        self.cosmetic_name = cosmetic_name
        self.replaces = replaces
        self.vanilla_id = vanilla_id
        self.type = type
        self.instrument_set = instrument_set


# Represents actual sequence data, along with metadata for the sequence data block
class Sequence(object):
    def __init__(self):
        self.address = -1
        self.size = -1
        self.data = []


def process_sequences(rom, sequences, target_sequences, ids, seq_type = 'bgm'):
    # Process vanilla music data
    for bgm in ids:
        # Get sequence metadata
        name = bgm[0]
        cosmetic_name = name
        type = rom.read_int16(0xB89AE8 + (bgm[1] * 0x10))
        instrument_set = rom.read_byte(0xB89911 + 0xDD + (bgm[1] * 2))
        id = bgm[1]

        # Create new sequences
        seq = TableEntry(name, cosmetic_name, type, instrument_set, vanilla_id = id)
        target = TableEntry(name, cosmetic_name, type, instrument_set, replaces = id)

        # Special handling for file select/fairy fountain
        if seq.vanilla_id != 0x57:
            sequences.append(seq)
        target_sequences.append(target)

    # Process music data in data/Music/
    # Each sequence requires a valid .seq sequence file and a .meta metadata file
    # Current .meta format: Cosmetic Name\nInstrument Set\nPool
    for f in os.listdir('data/Music'):
        fname = os.fsdecode(f)
        # Find meta file and check if corresponding seq file exists
        if fname.endswith('.meta') and os.path.isfile('data/Music/' + fname.split('.')[0] + '.seq'):
            # Read meta info
            try:
                with open('data/Music/' + fname, 'r') as stream:
                    lines = stream.readlines()
                # Strip newline(s) which doesn't like to work for some reason
                for line in lines:
                    line = line.rstrip()
            except FileNotFoundError as ex:
                raise FileNotFoundError('No meta file for: "' + fname + '". This should never happen')

            # Create new sequence, checking third line for correct type
            if (len(lines) > 2 and (lines[2].lower().rstrip() == seq_type.lower() or lines[2] == '')) or (len(lines) <= 2 and seq_type == 'bgm'):
                seq = TableEntry(fname.split('.')[0], lines[0], instrument_set = int(lines[1], 16))

                if seq.instrument_set < 0x00 or seq.instrument_set > 0x25:
                    raise Exception('Sequence instrument must be in range [0x00, 0x25]')

                sequences.append(seq)

    return sequences, target_sequences


def shuffle_music(sequences, target_sequences, log):
    # Shuffle the sequences
    random.shuffle(sequences)

    # Exclude unwanted sequences
    excluded_sequences = []
    if os.path.exists('data/Music/excluded.txt'):
        try:
            with open('data/Music/excluded.txt', 'r') as stream:
                excluded_sequences_raw = stream.readlines()
            for line in excluded_sequences_raw:
                excluded_sequences.append(line.rstrip())
        except FileNotFoundError as ex:
            raise FileNotFoundError('No exclusion file. This should never happen')

        # Find sequences that need to be removed
        excluded_list_elements = []
        for i in range(len(sequences)):
            if sequences[i].name in excluded_sequences:
                excluded_list_elements.insert(0, i)

        if len(sequences) == len(excluded_list_elements):
            raise RuntimeError(f'Too many sequences excluded. Remove sequences from exclude.txt or add more custom sequences.')

        # Remove the excluded sequences
        for i in range(len(excluded_list_elements)):
            new_choice = sequences[random.choice([i for i in range(len(sequences)) if i not in excluded_list_elements])]
            del(sequences[excluded_list_elements[i]])
            excluded_list_elements[i] = -1
            new_sequence = TableEntry(new_choice.name, new_choice.cosmetic_name, new_choice.type, new_choice.instrument_set, new_choice.replaces, new_choice.vanilla_id)
            sequences.append(new_sequence)

    for i in range(len(target_sequences)):
        sequences[i].replaces = target_sequences[i].replaces
        log[target_sequences[i].cosmetic_name] = sequences[i].cosmetic_name.rstrip()

    # Set sequences to only be the assigned sequences
    del sequences[len(target_sequences):]

    return sequences, log


def rebuild_sequences(rom, sequences, log):
    # List of sequences (actual sequence data objects) containing the vanilla sequence data
    old_sequences = []

    for i in range(0x6E):
        # Create new sequence object, an entry for the audio sequence
        entry = Sequence()
        # Get the address for the entry's pointer table entry
        entry_address = 0xB89AE0 + (i * 0x10)
        # Extract the info from the pointer table entry
        entry.address = rom.read_int32(entry_address)
        entry.size = rom.read_int32(entry_address + 0x04)

        # If size > 0, read the sequence data from the rom into the sequence object
        if entry.size > 0:
            entry.data = rom.read_bytes(entry.address + 0x029DE0, entry.size)
        else:
            s = [seq for seq in sequences if seq.replaces == i]
            if s != [] and entry.address > 0 and entry.address < 128:
                s = s.pop()
                if s.replaces != 0x28:
                    s.replaces = entry.address
                else:
                    # Special handling for file select/fairy fountain
                    entry.data = old_sequences[0x57].data
                    entry.size = old_sequences[0x57].size

        old_sequences.append(entry)

    # List of sequences containing the new sequence data
    new_sequences = []
    address = 0
    # Byte array to hold the data for the whole audio sequence
    new_audio_sequence = []

    for i in range(0x6E):
        new_entry = Sequence()
        # If sequence size is 0, the address doesn't matter and it doesn't effect the current address
        if old_sequences[i].size == 0:
            new_entry.address = old_sequences[i].address
        # Continue from the end of the new sequence table
        else:
            new_entry.address = address

        s = [seq for seq in sequences if seq.replaces == i]
        if s != []:
            assert len(s) == 1
            s = s.pop()
            # If we are using a vanilla sequence, get its data from old_sequences
            if s.vanilla_id != -1:
                new_entry.size = old_sequences[s.vanilla_id].size
                new_entry.data = old_sequences[s.vanilla_id].data
            else:
                # Read sequence info
                try:
                    with open('data/Music/' + s.name + '.seq', 'rb') as stream:
                        new_entry.data = bytearray(stream.read())
                    new_entry.size = len(new_entry.data)
                    if new_entry.size <= 0x10:
                        raise Exception('Invalid sequence file "' + s.name + '.seq"')
                    new_entry.data[1] = 0x20
                except FileNotFoundError as ex:
                    raise FileNotFoundError('No sequence file for: "' + s.name + '"')
        else:
            new_entry.size = old_sequences[i].size
            new_entry.data = old_sequences[i].data

        new_sequences.append(new_entry)

        # Concatenate the full audio sequence and the new sequence data
        if new_entry.data != [] and new_entry.size > 0:
            new_audio_sequence.extend(new_entry.data)
            # Increment the current address by the size of the new sequence
            address += new_entry.size

    # Check if the new audio sequence is larger than the vanilla one
    if address > 0x04F690:
        # Zero out the old audio sequence
        rom.buffer[0x029DE0 : 0x029DE0 + 0x04F690] = [0] * 0x04F690

        # Append new audio sequence
        new_address = rom.free_space()
        rom.write_bytes(new_address, new_audio_sequence)

        #Update dmatable
        rom.update_dmadata_record(0x029DE0, new_address, new_address + address)

    else:
        # Write new audio sequence file
        rom.write_bytes(0x029DE0, new_audio_sequence)

    # Update pointer table
    for i in range(0x6E):
        rom.write_int32(0xB89AE0 + (i * 0x10), new_sequences[i].address)
        rom.write_int32(0xB89AE0 + (i * 0x10) + 0x04, new_sequences[i].size)
        s = [seq for seq in sequences if seq.replaces == i]
        if s != []:
            assert len(s) == 1
            s = s.pop()
            rom.write_int16(0xB89AE0 + (i * 0x10) + 0x08, s.type)

    # Update instrument sets
    for i in range(0x6E):
        base = 0xB89911 + 0xDD + (i * 2)
        j = -1
        if new_sequences[i].size == 0:
            try:
                j = [seq for seq in sequences if seq.replaces == new_sequences[i].address].pop()
            except:
                j = -1
        else:
            try:
                j = [seq for seq in sequences if seq.replaces == i].pop()
            except:
                j = -1
        if j != -1:
            rom.write_byte(base, j.instrument_set)

    return log


def shuffle_pointers_table(rom, ids, log):
    # Read in all the Music data
    bgm_data = []
    for bgm in ids:
        bgm_sequence = rom.read_bytes(0xB89AE0 + (bgm[1] * 0x10), 0x10)
        bgm_instrument = rom.read_int16(0xB89910 + 0xDD + (bgm[1] * 2))
        bgm_data.append((bgm[0], bgm_sequence, bgm_instrument))

    # shuffle data
    random.shuffle(bgm_data)

    # Write Music data back in random ordering
    for bgm in ids:
        bgm_name, bgm_sequence, bgm_instrument = bgm_data.pop()
        rom.write_bytes(0xB89AE0 + (bgm[1] * 0x10), bgm_sequence)
        rom.write_int16(0xB89910 + 0xDD + (bgm[1] * 2), bgm_instrument)
        log[bgm[0]] = bgm_name

    # Write Fairy Fountain instrument to File Select (uses same track but different instrument set pointer for some reason)
    rom.write_int16(0xB89910 + 0xDD + (0x57 * 2), rom.read_int16(0xB89910 + 0xDD + (0x28 * 2)))
    return log


def randomize_music(rom, settings):
    log = {}
    sequences = []
    target_sequences = []
    fanfare_sequences = []
    fanfare_target_sequences = []

    # Include ocarina songs in fanfare pool if checked
    ff_ids = fanfare_sequence_ids
    if settings.ocarina_fanfares:
        ff_ids += ocarina_sequence_ids

    # If not creating patch file, shuffle audio sequences. Otherwise, shuffle pointer table
    if settings.compress_rom != 'Patch':
        if settings.background_music == 'random':
            sequences, target_sequences = process_sequences(rom, sequences, target_sequences, bgm_sequence_ids)
            sequences, log = shuffle_music(sequences, target_sequences, log)

        if settings.fanfares == 'random':
            fanfare_sequences, fanfare_target_sequences = process_sequences(rom, fanfare_sequences, fanfare_target_sequences, ff_ids, 'fanfare')
            fanfare_sequences, log = shuffle_music(fanfare_sequences, fanfare_target_sequences, log)

        log = rebuild_sequences(rom, sequences + fanfare_sequences, log)

        if settings.background_music == 'off':
            disable_music(rom, bgm_sequence_ids)
        if settings.fanfares == 'off':
            disable_music(rom, ff_ids)

    else:
        if settings.background_music == 'random':
            log = shuffle_pointers_table(rom, bgm_sequence_ids, log)
        elif settings.background_music == 'off':
            disable_music(rom, bgm_sequence_ids)

        if settings.fanfares == 'random':
            log = shuffle_pointers_table(rom, ff_ids, log)
        elif settings.fanfares == 'off':
            disable_music(rom, ff_ids)

    return log


def disable_music(rom, ids):
    # First track is no music
    blank_track = rom.read_bytes(0xB89AE0 + (0 * 0x10), 0x10)
    for bgm in ids:
        rom.write_bytes(0xB89AE0 + (bgm[1] * 0x10), blank_track)


def restore_music(rom):
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
    orig_start, orig_end, orig_size = rom.original._get_dmadata_record(0x7470)
    rom.write_bytes(orig_start, rom.original.read_bytes(orig_start, orig_size))

    # If Audioseq was relocated
    start, end, size = rom._get_dmadata_record(0x7470)
    if start != 0x029DE0:
        # Zero out old audioseq
        rom.write_bytes(start, [0] * size)
        rom.update_dmadata_record(start, orig_start, orig_end)

