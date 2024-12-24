from __future__ import annotations
from io import FileIO
import struct

# Container for storing Audiotable, Audiobank, Audiotable_index, Audiobank_index
class Audiobin:
    def __init__(self, _Audiobank: bytearray, _Audiobank_index: bytearray, _Audiotable: bytearray, _Audiotable_index: bytearray):
        self.Audiobank: bytearray = _Audiobank
        self.Audiobank_index: bytearray = _Audiobank_index
        self.Audiotable: bytearray = _Audiotable
        self.Audiotable_index: bytearray = _Audiotable_index

        num_banks = int.from_bytes(self.Audiobank_index[0:2], 'big')
        self.audiobanks: list[AudioBank] = []
        for i in range(0, num_banks):
            index = 0x10 + (0x10*i)
            curr_entry = self.Audiobank_index[index:index+0x10]
            audiobank: AudioBank = AudioBank(curr_entry, self.Audiobank, self.Audiotable, self.Audiotable_index)
            self.audiobanks.append(audiobank)

    def find_sample_in_audiobanks(self, sample_data: bytearray):
        for audiobank in self.audiobanks:
            for drum in audiobank.drums:
                if drum and drum.sample:
                    if drum.sample.data == sample_data:
                        return drum.sample
            for instrument in audiobank.instruments:
                if instrument:
                    if instrument.highNoteSample and instrument.highNoteSample.data == sample_data:
                        return instrument.highNoteSample
                    if instrument.lowNoteSample and instrument.lowNoteSample.data == sample_data:
                        return instrument.lowNoteSample
                    if instrument.normalNoteSample and instrument.normalNoteSample.data == sample_data:
                        return instrument.normalNoteSample
            for sfx in audiobank.SFX:
                if sfx and sfx.sample and sfx.sample.data:
                    if sfx.sample.data == sample_data:
                        return sfx.sample
        return None

class AdpcmLoop:
    def __init__(self, bankdata: bytearray, loop_addr: int):
        self.start = int.from_bytes(bankdata[loop_addr:loop_addr+4], 'big')
        self.end = int.from_bytes(bankdata[loop_addr+4:loop_addr+8], 'big')
        self.count = int.from_bytes(bankdata[loop_addr+8:loop_addr+12], 'big')
        self.origSpls = int.from_bytes(bankdata[loop_addr+12:loop_addr+16], 'big')
        self.state = []
        if self.count:
            for i in range(0,16):
                index = loop_addr + 0x10 + 2*i
                self.state.append(int.from_bytes(bankdata[index:index+2],'big'))

    def get_bytes(self):
        bytes = bytearray(0)
        bytes += self.start.to_bytes(4,'big')
        bytes += self.end.to_bytes(4, 'big')
        bytes += self.count.to_bytes(4, 'big')
        bytes += self.origSpls.to_bytes(4, 'big')
        for short in self.state:
            bytes += short.to_bytes(2, 'big')
        return bytes

class AdpcmBook:
    def __init__(self, bankdata: bytearray, book_addr: int):
        self.order = int.from_bytes(bankdata[book_addr:book_addr+4], 'big')
        self.npredictors = int.from_bytes(bankdata[book_addr+4:book_addr+8], 'big')
        self.book = []
        for i in range(0, 8 * self.order * self.npredictors):
            index = book_addr + 8 + 2*i
            self.book.append(int.from_bytes(bankdata[index:index+2], 'big'))

class Sample:
    def __init__(self, bankdata: bytearray, audiotable_file: bytearray, audiotable_index: bytearray, sample_offset: int, audiotable_id: int, parent):
        # Process the sample
        if sample_offset == 0:
            self.data = None
            return
        self.parent = parent
        self.bank_offset = sample_offset
        self.sample_header = bankdata[sample_offset:sample_offset + 0x10]
        self.codec = (self.sample_header[0] & 0xF0) >> 4
        self.medium = (self.sample_header[0] & 0x0C) >> 2
        self.size = int.from_bytes(self.sample_header[1:4], 'big')
        self.addr = int.from_bytes(self.sample_header[4:8], 'big', signed=True)
        if(sample_offset != 0):
            self.loop_addr = int.from_bytes(self.sample_header[8:12], 'big')
            self.book_addr = int.from_bytes(self.sample_header[12:16], 'big')
            self.loop = AdpcmLoop(bankdata, self.loop_addr)
            self.book = AdpcmBook(bankdata, self.book_addr)

        if self.addr == -1 : # If the offset is set to 0xFFFFFFFF then we need to get the sample data from ZSOUND files in the archive.
            self.data = None
            return
        # Read the audiotable pointer table entry
        if audiotable_file and audiotable_index:
            audiotable_index_offset = 0x10 + (audiotable_id * 0x10)
            audiotable_entry = audiotable_index[audiotable_index_offset:audiotable_index_offset + 0x10]
            audiotable_offset = int.from_bytes(audiotable_entry[0:4], 'big')
            sample_address = audiotable_offset + self.addr
            if sample_address < 0 or sample_address > len(audiotable_file): # If the calculated address falls outside of audiotable then we probably need to get the sample data from ZSOUND files in the archive
                self.data = None
                self.addr = -1
                return
            self.audiotable_addr = sample_address
            # Read the sample data
            self.data = audiotable_file[sample_address:sample_address+self.size]
        else:
            self.audiotable_addr = -1
            self.data = None
    
    def get_bytes(self) -> bytearray:
        bytes = bytearray()
        bytes += (((self.codec & 0x0F) << 4) | ((self.medium & 0x03) << 2)).to_bytes(1, 'big')
        bytes += self.size.to_bytes(3, 'big')
        bytes += self.addr.to_bytes(4, 'big')
        bytes += self.loop_addr.to_bytes(4, 'big')
        bytes += self.book_addr.to_bytes(4, 'big')
        return bytes

# Loads an audiobank and it's corresponding instrument/drum/sfxs
class AudioBank:

    # Constructor:
    # table_entry - 0x10 byte audiobank entry which contains info like the bank offset, size, number of instruments, etc.
    # audiobank_file - the Audiobank file as a byte array
    # audiotable_file - the Audiotable file as a byte array
    # audiotable_index - the Audiotable index (pointer table) which provides an offsets into the Audiotable file where a bank's instrument samples offsets are calculated from.
    def __init__(self, table_entry: bytearray, audiobank_file: bytearray, audiotable_file: bytearray, audiotable_index: bytearray) -> None:

        # Process bank entry
        self.bank_offset: int = int.from_bytes(table_entry[0:4], 'big') # Offset of the bank in the Audiobank file
        self.size: int = int.from_bytes(table_entry[4:8], 'big') # Size of the bank, in bytes
        self.load_location: int = table_entry[8] # ROM/RAM/DISK
        self.type: int = table_entry[9]
        self.audiotable_id: int = table_entry[10] # Read audiotable id from the table entry. Instrument data offsets are in relation to this
        self.unk: int = table_entry[11] # 0xFF
        self.num_instruments: int = table_entry[12]
        self.num_drums: int = table_entry[13]
        self.num_sfx: int = int.from_bytes(table_entry[14:16], 'big')
        self.bank_data = audiobank_file[self.bank_offset:self.bank_offset + self.size]
        self.original_data = self.bank_data.copy()
        self.original_table_entry = table_entry.copy()
        self.table_entry: bytearray = table_entry.copy()
        self.duplicate_banks: list[AudioBank] = []
        # Process the bank

        # Read drums
        self.drums: list[Drum] = []
        drum_offset = int.from_bytes(self.bank_data[0:4], 'big') # Get the drum pointer. This is the first uint32 in the bank. Points to a list of drum offsets of length num_drums
        for i in range(0, self.num_drums): # Read each drum
            offset = drum_offset + 4*i
            offset = int.from_bytes(self.bank_data[offset:offset+4], 'big')
            drum = Drum(i, self.bank_data, audiotable_file, audiotable_index, offset, self.audiotable_id) if offset != 0 else None
            self.drums.append(drum)

        # Read SFX
        self.SFX: list[SFX] = []
        sfx_offset = int.from_bytes(self.bank_data[4:8], 'big') # Get the SFX pointer. this is the second uint32 in the bank. Points to a list of Sound objects which are 8 bytes each (Sample offsets + tuning)
        for i in range(0, self.num_sfx): # Read each SFX
            offset = sfx_offset + 8*i
            sfx = SFX(i, self.bank_data, audiotable_file, audiotable_index, offset, self.audiotable_id) if offset != 0 else None
            self.SFX.append(sfx)

        self.instruments: list[Instrument] = []
        # Read the instruments
        for i in range(0, self.num_instruments):
            offset = 0x08 + 4*i
            instr_offset = int.from_bytes(self.bank_data[offset:offset+4], 'big')
            instrument: Instrument = Instrument(i, self.bank_data, audiotable_file, audiotable_index, instr_offset, self.audiotable_id) if instr_offset != 0 else None
            self.instruments.append(instrument)

    def __str__(self):
        return "Offset: " + hex(self.bank_offset) + ", " + "Len:" + hex(self.size)

    def get_all_samples(self) -> list[Sample]:
        all_sounds = self.drums + self.instruments + self.SFX
        all_samples: list[Sample] = []
        for sound in all_sounds:
            if type(sound) == Instrument:
                instrument: Instrument = sound
                if instrument.highNoteSample:
                    all_samples.append(instrument.highNoteSample)
                if instrument.lowNoteSample:
                    all_samples.append(instrument.lowNoteSample)
                if instrument.normalNoteSample:
                    all_samples.append(instrument.normalNoteSample)

            elif type(sound) == Drum:
                drum: Drum = sound
                if drum.sample:
                    all_samples.append(drum.sample)
            elif type(sound) == SFX:
                sfx: SFX = sound
                if sfx.sample:
                    all_samples.append(sfx.sample)
        return all_samples

    def build_entry(self, offset: int = 0) -> bytes:
        bank_entry: bytearray = bytearray(0)
        if offset == 0:
            bank_entry += self.bank_offset.to_bytes(4, 'big')
        else:
            bank_entry += offset.to_bytes(4, 'big')
        bank_entry += len(self.bank_data).to_bytes(4, 'big')
        bank_entry += self.table_entry[8:16]
        return bank_entry

class Drum:
    def __init__(self, drum_id: int, bankdata: bytearray, audiotable_file: bytearray, audiotable_index: bytearray, drum_offset: int, audiotable_id: int) -> None:
        self.drum_id = drum_id
        self.releaseRate = bankdata[drum_offset]
        self.pan = bankdata[drum_offset + 1]
        self.sampleOffset = int.from_bytes(bankdata[drum_offset + 4:drum_offset+8], 'big')
        self.sampleTuning = int.from_bytes(bankdata[drum_offset + 8:drum_offset+12], 'big')
        self.envelopePointOffset = int.from_bytes(bankdata[drum_offset+12:drum_offset+16], 'big')
        self.sample: Sample = Sample(bankdata, audiotable_file, audiotable_index, self.sampleOffset, audiotable_id, self)

class SFX:
    def __init__(self, sfx_id: int, bankdata: bytearray, audiotable_file: bytearray, audiotable_index: bytearray, sfx_offset: int, audiotable_id: int) -> None:
        self.sfx_id = sfx_id
        self.sfx_offset = sfx_offset
        self.sampleOffset = int.from_bytes(bankdata[sfx_offset:sfx_offset+4], 'big')
        self.sampleTuning = int.from_bytes(bankdata[sfx_offset+4:sfx_offset+8], 'big')
        self.sample: Sample = Sample(bankdata, audiotable_file, audiotable_index, self.sampleOffset, audiotable_id, self)
    
    def get_bytes(self):
        bytes = bytearray(0)
        bytes += self.sampleOffset.to_bytes(4,'big')
        bytes += struct.pack(">f", self.sampleTuning)
        return bytes

class Instrument:
    def __init__(self, inst_id: int, bankdata: bytearray, audiotable_file: bytearray, audiotable_index: bytearray, instr_offset: int, audiotable_id: int) -> None:
        self.inst_id = inst_id
        self.instrument_offset = instr_offset
        self.normalRangeLo = bankdata[instr_offset + 1]
        self.normalRangeHi = bankdata[instr_offset + 2]
        self.releaseRate = bankdata[instr_offset + 3]
        self.AdsrEnvelopePointOffset = int.from_bytes(bankdata[instr_offset + 4:instr_offset+8], 'big')
        self.lowNoteSampleOffset = int.from_bytes(bankdata[instr_offset + 8:instr_offset+12], 'big')
        self.lowNoteTuning = int.from_bytes(bankdata[instr_offset + 12: instr_offset + 16], 'big')
        self.normalNoteSampleOffset = int.from_bytes(bankdata[instr_offset + 16:instr_offset+20], 'big')
        self.normalNoteTuning = int.from_bytes(bankdata[instr_offset + 20:instr_offset + 24], 'big')
        self.highNoteSampleOffset = int.from_bytes(bankdata[instr_offset + 24:instr_offset+28], 'big')
        self.highNoteSampleTuning = int.from_bytes(bankdata[instr_offset + 28:instr_offset+32], 'big')
        self.lowNoteSample: Sample = Sample(bankdata, audiotable_file, audiotable_index, self.lowNoteSampleOffset, audiotable_id, self) if self.lowNoteSampleOffset != 0 else None
        self.normalNoteSample: Sample = Sample(bankdata, audiotable_file, audiotable_index, self.normalNoteSampleOffset, audiotable_id, self) if self.normalNoteSampleOffset != 0 else None
        self.highNoteSample: Sample = Sample(bankdata, audiotable_file, audiotable_index, self.highNoteSampleOffset, audiotable_id, self) if self.highNoteSampleOffset != 0 else None
