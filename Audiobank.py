from __future__ import annotations
from enum import IntEnum
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
            audiobank: AudioBank = AudioBank.from_rom_data(curr_entry, self.Audiobank, self.Audiotable, self.Audiotable_index)
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
    def __init__(self, start: int, end: int, count: int, origSpls: int, state: list[int]):
        self.start: int = start
        self.end: int = end
        self.count: int = count
        self.origSpls: int = origSpls
        self.state: list[int] = state

    def from_rom_data(bankdata: bytearray, loop_addr: int):
        start = int.from_bytes(bankdata[loop_addr:loop_addr+4], 'big')
        end = int.from_bytes(bankdata[loop_addr+4:loop_addr+8], 'big')
        count = int.from_bytes(bankdata[loop_addr+8:loop_addr+12], 'big')
        origSpls = int.from_bytes(bankdata[loop_addr+12:loop_addr+16], 'big')
        state: list[int] = []
        if count :
            for i in range(0,16):
                index = loop_addr + 0x10 + 2*i
                state.append(int.from_bytes(bankdata[index:index+2],'big'))
        return AdpcmLoop(start, end, count, origSpls, state)

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
    def __init__(self, order: int, npredictors: int, book: bytearray):
        self.bank_offset: int = -1
        self.order: int = order
        self.npredictors: int = npredictors
        self.book: bytearray = book

    def from_rom_data(bankdata: bytearray, book_addr: int, adpcmbookCache: dict[int, AdpcmBook]) -> AdpcmBook:
        if adpcmbookCache and book_addr in adpcmbookCache.keys():
            return adpcmbookCache[book_addr]

        order = int.from_bytes(bankdata[book_addr:book_addr+4], 'big')
        npredictors = int.from_bytes(bankdata[book_addr+4:book_addr+8], 'big')
        book: bytearray = bankdata[book_addr+8:book_addr+8+2*8*order*npredictors]
        newbook = AdpcmBook(order, npredictors, book)
        if adpcmbookCache is not None:
            adpcmbookCache[book_addr] = newbook
        return newbook

    def get_bytes(self) -> bytearray:
        bytes = bytearray(0)
        bytes += self.order.to_bytes(4, 'big')
        bytes += self.npredictors.to_bytes(4, 'big')
        bytes += self.book
        return bytes

class Envelope:
    def __init__(self, points: list[EnvelopePoint]):
        self.bank_offset = -1
        self.points = points

    def get_bytes(self):
        bytes = bytearray(0)
        for point in self.points:
            bytes += point.get_bytes()
        
        # Extend to 16 bytes for alignment purposes
        if len(bytes) % 16 != 0:
            bytes += bytearray(16 - len(bytes)%16)
        
        return bytes

class EnvelopePoint:
    def __init__(self, delay: int, arg: int):
        self.delay: int = delay
        self.arg: int = arg
        self.bank_offset = -1
    
    def get_bytes(self):
        bytes = bytearray(0)
        bytes += self.delay.to_bytes(2, 'big', signed=True)
        bytes += self.arg.to_bytes(2, 'big', signed=True)
        return bytes

    def from_rom_data(bankdata: bytearray, envelopepoint_offset: int, envelopeCache: dict[int, Envelope] = None) -> Envelope:
        if envelopeCache and envelopepoint_offset in envelopeCache.keys():
            return envelopeCache[envelopepoint_offset]

        points: list[EnvelopePoint] = []
        done: bool = False
        index = envelopepoint_offset
        while True:
            delay: int = int.from_bytes(bankdata[index:index+2], 'big', signed=True)
            arg: int = int.from_bytes(bankdata[index+2:index+4], 'big', signed=True)
            newPoint = EnvelopePoint(delay, arg)
            points.append(newPoint)
            if newPoint.delay == -1:
                break
            index += 4
        envelope: Envelope = Envelope(points)
        if envelopeCache is not None:
            envelopeCache[envelopepoint_offset] = envelope
        return envelope

class Sample:    
    def __init__(self):
        self.parents: list = []
        self.bank_offset = -1 # offset of the sample within the bank. -1 indicates the sample hasn't been placed yet
        self.original_offset = -1 
        self.codec: int = 0 # ADPCM is the only codec that seems to work
        self.medium: int = 0
        self.tag: bool = False
        self.book: AdpcmBook = None
        self.loop: AdpcmLoop = None
        self.data: bytearray = None
        self.size: int = 0
        self.placed_address: int = -1

    def from_rom_data(bankdata: bytearray, audiotable_file: bytearray, audiotable_index: bytearray, sample_offset: int, audiotable_id: int,parent, sampleCache: dict[int,Sample] = None, adpcmbookCache: dict[int,AdpcmBook] = None):
        # First check if this sample is already in the list of samples that we've processed
        if sampleCache and (sample_offset in sampleCache.keys()):
            sampleCache[sample_offset].parents.append(parent)
            return sampleCache[sample_offset]

        # Process the sample
        sample = Sample()
        sample.parents.append(parent)
        if sample_offset == 0:
            sample.data = None
            return sample
        sample.original_offset = sample_offset
        sample.sample_header = bankdata[sample_offset:sample_offset + 0x10]
        sample.codec = (sample.sample_header[0] & 0xF0) >> 4
        sample.medium = (sample.sample_header[0] & 0x0C) >> 2
        sample.size = int.from_bytes(sample.sample_header[1:4], 'big')
        sample.addr = int.from_bytes(sample.sample_header[4:8], 'big', signed=True) # Apparently can use negative audiotable offsets so treat this as signed
        if(sample_offset != 0):
            sample.loop_addr = int.from_bytes(sample.sample_header[8:12], 'big')
            sample.book_addr = int.from_bytes(sample.sample_header[12:16], 'big')
            sample.loop = AdpcmLoop.from_rom_data(bankdata, sample.loop_addr)
            sample.book = AdpcmBook.from_rom_data(bankdata, sample.book_addr, adpcmbookCache)

        if sample.addr == -1 : # If the offset is set to 0xFFFFFFFF then we need to get the sample data from ZSOUND files in the archive.
            sample.data = None
            return sample
        
        # Read the audiotable pointer table entry
        elif audiotable_file and audiotable_index:
            audiotable_index_offset = 0x10 + (audiotable_id * 0x10)
            audiotable_entry = audiotable_index[audiotable_index_offset:audiotable_index_offset + 0x10]
            audiotable_offset = int.from_bytes(audiotable_entry[0:4], 'big')
            sample_address = audiotable_offset + sample.addr
            if sample_address < 0 or sample_address > len(audiotable_file): # If the calculated address falls outside of audiotable then this is probably a tempaddress ZSOUND and we need to get the sample data from ZSOUND files in the archive
                sample.data = None
                sample.addr = int.from_bytes(sample.addr.to_bytes(4, 'big', signed=True), 'big', signed=False) # Convert back to unsigned int
                #sample.addr = -1
            else: # This is a sample in audiotable so read the sample
                sample.audiotable_addr = sample_address
                # Read the sample data
                sample.data = audiotable_file[sample_address:sample_address+sample.size]
        else: # Should probably never get to this case
            sample.audiotable_addr = -1
            sample.data = None
        
        # Add to the sample cache if one was provided
        if sampleCache is not None:
            sampleCache[sample_offset] = sample
        return sample
    
    def get_bytes(self) -> bytearray:
        bytes = bytearray()
        bytes += (((self.codec & 0x0F) << 4) | ((self.medium & 0x03) << 2)).to_bytes(1, 'big')
        bytes += self.size.to_bytes(3, 'big')
        bytes += self.placed_address.to_bytes(4, 'big')
        bytes += self.loop.bank_offset.to_bytes(4, 'big')
        bytes += self.book.bank_offset.to_bytes(4, 'big')
        return bytes

class AudioCacheLoadType(IntEnum):
    CACHE_LOAD_PERMANENT = 0
    CACHE_LOAD_PERSISTENT = 1
    CACHE_LOAD_TEMPORARY = 2
    CACHE_LOAD_EITHER = 3
    CACHE_LOD_EITHER_NOSYNC = 4

# Loads an audiobank and it's corresponding instrument/drum/sfxs
class AudioBank:

    # Constructor:
    # table_entry - 0x10 byte audiobank entry which contains info like the bank offset, size, number of instruments, etc.
    # audiobank_file - the Audiobank file as a byte array
    # audiotable_file - the Audiotable file as a byte array
    # audiotable_index - the Audiotable index (pointer table) which provides an offsets into the Audiotable file where a bank's instrument samples offsets are calculated from.
    def __init__(self) -> None:
        self.drums: list[Drum] = []
        self.SFX: list[SFX] = []
        self.instruments: list[Instrument] = []
        self.medium: int = None # ROM/RAM/Disk
        self.cachePolicy: AudioCacheLoadType = None # 
        self.audiotable_id: int = 0
        self.placed_address: int = -1
        self.placed_data: bytearray = None
        self.original_data: bytearray = None
        self.original_table_entry: bytearray = None

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

    def from_rom_data(table_entry: bytearray, audiobank_file: bytearray, audiotable_file: bytearray, audiotable_index: bytearray) -> AudioBank:
        # Process bank entry
        bank: AudioBank = AudioBank()
        bank.original_table_entry = table_entry
        bank_offset: int = int.from_bytes(table_entry[0:4], 'big') # Offset of the bank in the Audiobank file
        size: int = int.from_bytes(table_entry[4:8], 'big') # Size of the bank, in bytes
        bank.medium = table_entry[8] # ROM/RAM/DISK
        bank.cachePolicy = AudioCacheLoadType(table_entry[9])
        bank.audiotable_id = table_entry[10] # Read audiotable id from the table entry. Instrument data offsets are in relation to this
        unk: int = table_entry[11] # 0xFF
        num_instruments: int = table_entry[12]
        num_drums: int = table_entry[13]
        num_sfx: int = int.from_bytes(table_entry[14:16], 'big')
        bank_data = audiobank_file[bank_offset:bank_offset + size]
        bank.original_data = bank_data
        # Process the bank

        # Keep track of the sample offsets that we load from so we can actually point to the same Sample object
        sampleCache: dict[int, Sample] = {}

        # Same with AdpcmBook stuff
        adpcmbookCache: dict[int, AdpcmBook] = {}

        # Same with EnvelopePoints
        envelopeCache: dict[int, EnvelopePoint] = {}

        # Read drums
        drum_offset = int.from_bytes(bank_data[0:4], 'big') # Get the drum pointer. This is the first uint32 in the bank. Points to a list of drum offsets of length num_drums
        for i in range(0, num_drums): # Read each drum
            offset = drum_offset + 4*i
            offset = int.from_bytes(bank_data[offset:offset+4], 'big')
            drum = Drum(i, bank_data, audiotable_file, audiotable_index, offset, bank.audiotable_id, sampleCache, adpcmbookCache, envelopeCache) if offset != 0 else None
            bank.drums.append(drum)

        # Read SFX
        sfx_offset = int.from_bytes(bank_data[4:8], 'big') # Get the SFX pointer. this is the second uint32 in the bank. Points to a list of Sound objects which are 8 bytes each (Sample offsets + tuning)
        for i in range(0, num_sfx): # Read each SFX
            offset = sfx_offset + 8*i
            sfx = SFX.from_rom_data(i, bank_data, audiotable_file, audiotable_index, offset, bank.audiotable_id, sampleCache, adpcmbookCache) if offset != 0 else None
            bank.SFX.append(sfx)

        # Read the instruments
        for i in range(0, num_instruments):
            offset = 0x08 + 4*i
            instr_offset = int.from_bytes(bank_data[offset:offset+4], 'big')
            instrument: Instrument = Instrument(i, bank_data, audiotable_file, audiotable_index, instr_offset, bank.audiotable_id, sampleCache, adpcmbookCache, envelopeCache) if instr_offset != 0 else None
            bank.instruments.append(instrument)

        return bank

    def print_bank(self) -> None:
        i = 0
        offsets = {}
        for instrument in self.instruments:
            if instrument:
                print(f"Instrument {i} ({hex(instrument.instrument_offset)}):\n\tLow Offset: {hex(instrument.lowNoteSampleOffset)}\n\tNormal Offset: {hex(instrument.normalNoteSampleOffset)}\n\tHigh Offset: {hex(instrument.highNoteSampleOffset)}")
                offsets[instrument.instrument_offset] = instrument
                offsets[instrument.AdsrEnvelopePointOffset] = instrument.envelope
                if instrument.lowNoteSample:
                    offsets[instrument.lowNoteSampleOffset] = instrument.lowNoteSample
                    offsets[instrument.lowNoteSample.book_addr] = instrument.lowNoteSample.book
                    offsets[instrument.lowNoteSample.loop_addr] = instrument.lowNoteSample.loop
                if instrument.normalNoteSample:
                    offsets[instrument.normalNoteSampleOffset] = instrument.normalNoteSample
                    offsets[instrument.normalNoteSample.book_addr] = instrument.normalNoteSample.book
                    offsets[instrument.normalNoteSample.loop_addr] = instrument.normalNoteSample.loop
                if instrument.highNoteSample:
                    offsets[instrument.highNoteSampleOffset] = instrument.highNoteSample
                    offsets[instrument.highNoteSample.book_addr] = instrument.highNoteSample.book
                    offsets[instrument.highNoteSample.loop_addr] = instrument.highNoteSample.loop
                
            i += 1

        i = 0
        for drum in self.drums:
            if drum:
                offsets[drum.drum_offset] = drum
                print(f"Drum {i} ({hex(drum.drum_offset)}): Sample Offset: {hex(drum.sampleOffset)}")
                offsets[drum.sampleOffset] = drum.sample
                offsets[drum.sample.book_addr] = drum.sample.book
                offsets[drum.sample.loop_addr] = drum.sample.loop
                offsets[drum.envelopePointOffset] = drum.envelope
            i += 1
        i = 0
        for sfx in self.SFX:
            if sfx:
                offsets[sfx.sfx_offset] = sfx
                print(f"SFX {i} ({hex(sfx.sfx_offset)}): Sample Offset: {hex(sfx.sampleOffset)}")
                offsets[sfx.sampleOffset] = sfx.sample
                if sfx.sampleOffset:
                    offsets[sfx.sample.book_addr] = sfx.sample.book
                    offsets[sfx.sample.loop_addr] = sfx.sample.loop
            i += 1
        
        for offset in sorted(offsets.keys()):
            print(f"{hex(offset)}: {type(offsets[offset])}")
        return offsets

    def build_entry(self, offset: int, length: int) -> bytes:
        bank_entry: bytearray = bytearray(0)
        bank_entry += offset.to_bytes(4, 'big')
        bank_entry += length.to_bytes(4, 'big')
        bank_entry += self.medium.to_bytes(1, 'big')
        bank_entry += self.cachePolicy.to_bytes(1, 'big')
        bank_entry += self.audiotable_id.to_bytes(1, 'big')
        bank_entry += (0xFF).to_bytes(1, 'big')
        bank_entry += len(self.instruments).to_bytes(1, 'big')
        bank_entry += len(self.drums).to_bytes(1, 'big')
        bank_entry += len(self.SFX).to_bytes(2, 'big')
        return bank_entry

class Drum:
    def __init__(self, drum_id: int, bankdata: bytearray, audiotable_file: bytearray, audiotable_index: bytearray, drum_offset: int, audiotable_id: int, sampleCache: dict[int,Sample], adpcmbookCache: dict[int,AdpcmBook], envelopePoints: dict[int,EnvelopePoint]) -> None:
        self.drum_id = drum_id
        self.drum_offset: int = drum_offset
        self.releaseRate = bankdata[drum_offset]
        self.pan = bankdata[drum_offset + 1]
        self.sampleOffset = int.from_bytes(bankdata[drum_offset + 4:drum_offset+8], 'big')
        self.sampleTuning = struct.unpack(">f", bankdata[drum_offset + 8:drum_offset+12])[0]
        self.envelopePointOffset = int.from_bytes(bankdata[drum_offset+12:drum_offset+16], 'big')
        self.envelope: Envelope = EnvelopePoint.from_rom_data(bankdata, self.envelopePointOffset, envelopePoints)
        self.sample: Sample = Sample.from_rom_data(bankdata, audiotable_file, audiotable_index, self.sampleOffset, audiotable_id, self, sampleCache, adpcmbookCache)

    def get_bytes(self):
        bytes = bytearray(0)
        bytes += self.releaseRate.to_bytes(1, 'big')
        bytes += self.pan.to_bytes(1, 'big')
        bytes += bytearray(2)
        bytes += self.sample.bank_offset.to_bytes(4, 'big')
        bytes += struct.pack(">f", self.sampleTuning)
        bytes += self.envelope.bank_offset.to_bytes(4, 'big')
        return bytes

class SFX:
    def __init__(self, sfx_id, tuning: float, sample: Sample) -> None:
        self.sfx_id = sfx_id
        self.sampleOffset: int = -1
        self.sampleTuning: float = tuning
        self.sample: Sample = sample

    def from_rom_data(sfx_id: int, bankdata: bytearray, audiotable_file: bytearray, audiotable_index: bytearray, sfx_offset: int, audiotable_id: int, sampleCache: dict[int,Sample], adpcmbookCache: dict[int,AdpcmBook]) -> Sample:
        sampleOffset = int.from_bytes(bankdata[sfx_offset:sfx_offset+4], 'big')
        #sampleTuning = int.from_bytes(bankdata[sfx_offset+4:sfx_offset+8], 'big')
        sampleTuning = struct.unpack(">f", bankdata[sfx_offset+4:sfx_offset+8])[0]
        if sampleOffset == 0:
            return None
        sfx: SFX = SFX(sfx_id, sampleTuning, None)
        sfx.sfx_offset = sfx_offset
        sfx.sampleOffset = sampleOffset
        sample = Sample.from_rom_data(bankdata, audiotable_file, audiotable_index, sampleOffset, audiotable_id, sfx, sampleCache, adpcmbookCache)
        sfx.sample = sample
        return sfx

    def get_bytes(self):
        bytes = bytearray(0)
        bytes += self.sample.bank_offset.to_bytes(4,'big')
        bytes += struct.pack(">f", self.sampleTuning)
        return bytes

class Instrument:
    def __init__(self, inst_id: int, bankdata: bytearray, audiotable_file: bytearray, audiotable_index: bytearray, instr_offset: int, audiotable_id: int, sampleCache: dict[int,Sample], adpcmbookCache: dict[int,AdpcmBook], envelopeCache: dict[int,EnvelopePoint]) -> None:
        self.inst_id = inst_id
        self.instrument_offset = instr_offset
        self.normalRangeLo = bankdata[instr_offset + 1]
        self.normalRangeHi = bankdata[instr_offset + 2]
        self.releaseRate = bankdata[instr_offset + 3]
        self.AdsrEnvelopePointOffset = int.from_bytes(bankdata[instr_offset + 4:instr_offset+8], 'big')
        self.envelope: Envelope = EnvelopePoint.from_rom_data(bankdata, self.AdsrEnvelopePointOffset, envelopeCache)
        self.lowNoteSampleOffset = int.from_bytes(bankdata[instr_offset + 8:instr_offset+12], 'big')
        self.lowNoteTuning = struct.unpack(">f", bankdata[instr_offset+12:instr_offset+16])[0]
        self.normalNoteSampleOffset = int.from_bytes(bankdata[instr_offset + 16:instr_offset+20], 'big')
        self.normalNoteTuning = struct.unpack(">f", bankdata[instr_offset+20:instr_offset+24])[0]
        self.highNoteSampleOffset = int.from_bytes(bankdata[instr_offset + 24:instr_offset+28], 'big')
        self.highNoteSampleTuning = struct.unpack(">f", bankdata[instr_offset+28:instr_offset+32])[0]
        self.lowNoteSample: Sample = Sample.from_rom_data(bankdata, audiotable_file, audiotable_index, self.lowNoteSampleOffset, audiotable_id, self, sampleCache, adpcmbookCache) if self.lowNoteSampleOffset != 0 else None
        self.normalNoteSample: Sample = Sample.from_rom_data(bankdata, audiotable_file, audiotable_index, self.normalNoteSampleOffset, audiotable_id, self, sampleCache, adpcmbookCache) if self.normalNoteSampleOffset != 0 else None
        self.highNoteSample: Sample = Sample.from_rom_data(bankdata, audiotable_file, audiotable_index, self.highNoteSampleOffset, audiotable_id, self, sampleCache, adpcmbookCache) if self.highNoteSampleOffset != 0 else None
        self.tag: bool = False

    def get_bytes(self):
        bytes = bytearray(1)
        bytes += self.normalRangeLo.to_bytes(1, 'big')
        bytes += self.normalRangeHi.to_bytes(1, 'big')
        bytes += self.releaseRate.to_bytes(1, 'big')
        bytes += self.envelope.bank_offset.to_bytes(4, 'big')
        
        if self.lowNoteSample:
            bytes += self.lowNoteSample.bank_offset.to_bytes(4, 'big')
            bytes += struct.pack(">f", self.lowNoteTuning)
        else:
            bytes += bytearray(8)
        
        if self.normalNoteSample:
            bytes += self.normalNoteSample.bank_offset.to_bytes(4, 'big')
            bytes += struct.pack(">f", self.normalNoteTuning)
        else:
            bytes += bytearray(8)
        
        if self.highNoteSample:
            bytes += self.highNoteSample.bank_offset.to_bytes(4, 'big')
            bytes += struct.pack(">f", self.highNoteSampleTuning)
        else:
            bytes += bytearray(8)
        return bytes
    
    def equals(self, other: Instrument):
        match = True
        if self.lowNoteSample:
            match = match and self.lowNoteSample.data == other.lowNoteSample.data
            match = match and self.lowNoteSample.book.book == other.lowNoteSample.book.book
            match = match and self.lowNoteSample.loop.state == other.lowNoteSample.loop.state
        if self.normalNoteSample:
            match = match and (self.normalNoteSample.data == other.normalNoteSample.data)
            match = match and self.normalNoteSample.book.book == other.normalNoteSample.book.book
            match = match and self.normalNoteSample.loop.state == other.normalNoteSample.loop.state
        if self.highNoteSample:
            match = match and (self.highNoteSample.data == other.highNoteSample.data)
            match = match and self.highNoteSample.book.book == other.highNoteSample.book.book
            match = match and self.highNoteSample.loop.state == other.highNoteSample.loop.state
        
        return match