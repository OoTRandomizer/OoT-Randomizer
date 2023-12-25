from __future__ import annotations
import copy
import json
import os
import platform
import subprocess
from collections.abc import Iterator, Sequence
from typing import Optional

from Models import restrictiveBytes
from Utils import is_bundled, subprocess_args, local_path, data_path, get_version_bytes
from crc import calculate_crc
from ntype import BigStream
from version import base_version, branch_identifier, supplementary_version

DMADATA_START: int = 0x7430  # NTSC 1.0/1.1: 0x7430, NTSC 1.2: 0x7960, Debug: 0x012F70


class Rom(BigStream):
    def __init__(self, file: Optional[str] = None) -> None:
        super().__init__(bytearray())

        self.original: Rom = self
        self.changed_address: dict[int, int] = {}
        self.changed_dma: dict[int, tuple[int, int, int]] = {}
        self.force_patch: list[int] = []
        self.dma: DMAIterator = DMAIterator(self, DMADATA_START)

        if file is None:
            return

        decompressed_file: str = local_path('ZOOTDEC.z64')

        os.chdir(local_path())

        with open(data_path('generated/symbols.json'), 'r') as stream:
            symbols = json.load(stream)
            self.symbols: dict[str, int] = {name: int(addr, 16) for name, addr in symbols.items()}

        if os.path.isfile(decompressed_file):
            # Try to read from previously decompressed rom if one exists.
            try:
                self.read_rom(decompressed_file)
            except (FileNotFoundError, RuntimeError):
                # Decompress the provided file.
                if not file:
                    raise FileNotFoundError('Must specify path to base ROM')
                self.read_rom(file, decompressed_file)
        elif file:
            self.read_rom(file, decompressed_file)
        else:
            raise FileNotFoundError('Must specify path to base ROM')

        # Add file to maximum size
        self.buffer.extend(bytearray([0x00] * (0x4000000 - len(self.buffer))))
        self.original = self.copy()

        # Add version number to header.
        self.write_version_bytes()

    def copy(self) -> Rom:
        new_rom: Rom = Rom()
        new_rom.buffer = copy.copy(self.buffer)
        new_rom.changed_address = copy.copy(self.changed_address)
        new_rom.changed_dma = copy.copy(self.changed_dma)
        new_rom.force_patch = copy.copy(self.force_patch)
        return new_rom

    def read_rom(self, input_file: str, output_file: Optional[str] = None, verify_crc: bool = True) -> None:
        try:
            with open(input_file, 'rb') as stream:
                self.buffer = bytearray(stream.read())
        except FileNotFoundError as ex:
            raise FileNotFoundError(f'Invalid path to Base ROM: "{input_file}"')

        # Validate ROM file
        if not verify_crc:
            return

        valid_crc = [
            [0xEC, 0x70, 0x11, 0xB7, 0x76, 0x16, 0xD7, 0x2B], # Compressed
            [0x70, 0xEC, 0xB7, 0x11, 0x16, 0x76, 0x2B, 0xD7], # Byteswap compressed
            [0x93, 0x52, 0x2E, 0x7B, 0xE5, 0x06, 0xD4, 0x27], # Decompressed
        ]

        file_name = os.path.splitext(input_file)
        rom_crc = list(self.buffer[0x10:0x18])
        if rom_crc not in valid_crc:
            # Bad CRC validation
            raise RuntimeError(f'ROM file {input_file} is not a valid OoT 1.0 US ROM.')
        elif len(self.buffer) < 0x2000000 or len(self.buffer) > 0x4000000 or file_name[1].lower() not in ('.z64', '.n64'):
            # ROM is too big, or too small, or a bad type
            raise RuntimeError(f'ROM file {input_file} is not a valid OoT 1.0 US ROM.')
        elif len(self.buffer) == 0x2000000:
            # If Input ROM is compressed, then Decompress it
            if output_file:
                self.decompress_rom(input_file, output_file, verify_crc)
            else:
                raise RuntimeError('ROM was unable to be decompressed. Please supply an already decompressed ROM.')
        else:
            # ROM file is a valid and already uncompressed
            pass

    def decompress_rom(self, input_file: str, output_file: str, verify_crc: bool = True) -> None:
        sub_dir = "./" if is_bundled() else "bin/Decompress/"

        if platform.system() == 'Windows':
            if platform.machine() == 'AMD64':
                subcall = [sub_dir + "Decompress.exe", input_file, output_file]
            elif platform.machine() == 'ARM64':
                subcall = [sub_dir + "Decompress_ARM64.exe", input_file, output_file]
            else:
                subcall = [sub_dir + "Decompress32.exe", input_file, output_file]
        elif platform.system() == 'Linux':
            if platform.machine() in ('arm64', 'aarch64', 'aarch64_be', 'armv8b', 'armv8l'):
                subcall = [sub_dir + "Decompress_ARM64", input_file, output_file]
            elif platform.machine() in ('arm', 'armv7l', 'armhf'):
                subcall = [sub_dir + "Decompress_ARM32", input_file, output_file]
            else:
                subcall = [sub_dir + "Decompress", input_file, output_file]
        elif platform.system() == 'Darwin':
            if platform.machine() == 'arm64':
                subcall = [sub_dir + "Decompress_ARM64.out", input_file, output_file]
            else:
                subcall = [sub_dir + "Decompress.out", input_file, output_file]
        else:
            raise RuntimeError('Unsupported operating system for decompression. Please supply an already decompressed ROM.')

        subprocess.call(subcall, **subprocess_args())
        self.read_rom(output_file, verify_crc=verify_crc)

    def write_byte(self, address: int, value: int) -> None:
        super().write_byte(address, value)
        self.changed_address[self.last_address-1] = value

    def write_bytes_restrictive(self, start: int, size: int, values: Sequence[int]) -> None:
        for i in range(size):
            address = start + i
            should_write = True
            for restrictiveBlock in restrictiveBytes:
                # If i is between the start of restrictive zone [0] and start + size [1]
                if restrictiveBlock[0] <= address < restrictiveBlock[0] + restrictiveBlock[1]:
                    should_write = False
                    break
            if should_write:
                self.write_byte(address, values[i])

    def write_bytes(self, address: int, values: Sequence[int]) -> None:
        super().write_bytes(address, values)
        self.changed_address.update(zip(range(address, address + len(values)), values))

    def restore(self) -> None:
        self.buffer = copy.copy(self.original.buffer)
        self.changed_address = {}
        self.changed_dma = {}
        self.force_patch = []
        self.last_address = 0
        self.write_version_bytes()

    def sym(self, symbol_name: str) -> int:
        return self.symbols[symbol_name]

    def write_to_file(self, file: str) -> None:
        self.verify_dmadata()
        self.update_header()
        with open(file, 'wb') as outfile:
            outfile.write(self.buffer)

    def update_header(self) -> None:
        crc = calculate_crc(self)
        self.write_bytes(0x10, crc)

    def write_version_bytes(self) -> None:
        version_bytes = get_version_bytes(base_version, branch_identifier, supplementary_version)
        self.write_bytes(0x19, version_bytes[:5])
        self.write_bytes(0x35, version_bytes[:3])
        self.force_patch.extend([0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x35, 0x36, 0x37])

    def read_version_bytes(self) -> bytearray:
        version_bytes = self.read_bytes(0x19, 5)
        secondary_version_bytes = self.read_bytes(0x35, 3)
        for i in range(3):
            if secondary_version_bytes[i] != version_bytes[i]:
                return secondary_version_bytes
        return version_bytes

    # dmadata/file management helper functions

    def verify_dmadata(self) -> None:
        overlapping_records = []
        dma_data = []

        for dma_entry in self.dma:
            this_start, this_end, this_size = dma_entry.as_tuple()

            if this_start == 0 and this_end == 0:
                break

            dma_data.append((this_start, this_end, this_size))

        dma_data.sort()

        for i in range(0, len(dma_data) - 1):
            this_start, this_end, this_size = dma_data[i]
            next_start, next_end, next_size = dma_data[i + 1]

            if this_end > next_start:
                overlapping_records.append(
                    f'0x{this_start:08X} - 0x{this_end:08X} (Size: 0x{this_size:04X})\n0x{next_start:08X} - 0x{next_end:08X} (Size: 0x{next_size:04X})'
                )

        if len(overlapping_records) > 0:
            raise Exception("Overlapping DMA Data Records!\n%s" %
                            '\n-------------------------------------\n'.join(overlapping_records))

    # update dmadata record with start vrom address "key"
    # if key is not found, then attempt to add a new dmadata entry
    def update_dmadata_record_by_key(self, key: Optional[int], start: int, end: int, from_file: Optional[int] = None) -> None:
        dma_entry = self.dma.get_dmadata_record_by_key(key)
        if dma_entry is None:
            raise Exception(f"dmadata update failed: key {key:{'x' if key else ''}} not found in dmadata and dma table is full.")

        if from_file is None:
            from_file = -1 if key is None else key
        dma_entry.update(start, end, from_file)

    # This will scan for any changes that have been made to the DMA table
    # By default, this assumes any changes here are new files, so this should only be called
    # after patching in the new files, but before vanilla files are repointed
    def scan_dmadata_update(self, preserve_from_file: bool = False, assume_move: bool = False) -> None:
        for dma_entry in self.dma:
            dma_start, dma_end, dma_size = dma_entry.as_tuple()
            old_dma_start, old_dma_end, old_dma_size = self.original.dma[dma_entry.index].as_tuple()
            if (dma_start == 0 and dma_end == 0) and (old_dma_start == 0 and old_dma_end == 0):
                break

            # If the entries do not match, the flag the changed entry
            if not (dma_start == old_dma_start and dma_end == old_dma_end):
                from_file = -1
                if preserve_from_file and dma_entry.index in self.changed_dma:
                    from_file = self.changed_dma[dma_entry.index][0]
                elif assume_move and dma_entry.index < 1496:
                    from_file = old_dma_start
                self.changed_dma[dma_entry.index] = (from_file, dma_start, dma_end - dma_start)

    # This will rescan the entire ROM, compare to original ROM, and repopulate changed_address.
    def rescan_changed_bytes(self) -> None:
        self.changed_address = {}
        size = len(self.buffer)
        original_size = len(self.original.buffer)
        for i, byte in enumerate(self.buffer):
            if i >= original_size:
                self.changed_address[i] = byte
                continue
            orig_byte = self.original.read_byte(i)
            if byte != orig_byte:
                self.changed_address[i] = byte
        if size < original_size:
            self.changed_address.update(zip(range(size, original_size-1), [0]*(original_size-size)))


class DMAEntry:
    def __init__(self, rom: Rom, index: int) -> None:
        self.rom = rom
        self.index = index
        if self.index < 0 or self.index > self.rom.dma.dma_entries:
            raise ValueError(f"DMAEntry: Index out of range: {self.index}")

    @property
    def start(self) -> int:
        return self.rom.read_int32(self.rom.dma.dma_start + (self.index * 0x10))

    @property
    def end(self) -> int:
        return self.rom.read_int32(self.rom.dma.dma_start + (self.index * 0x10) + 0x04)

    @property
    def size(self) -> int:
        return self.end - self.start

    def as_tuple(self) -> tuple[int, int, int]:
        start, end = self.start, self.end
        return start, end, end - start

    def file_bytes(self) -> bytearray:
        start, end, size = self.as_tuple()
        return self.rom.read_bytes(start, size)

    def update(self, start: int, end: int, from_file: Optional[int] = None):
        if from_file is None:
            if self.index in self.rom.changed_dma:
                from_file = self.rom.changed_dma[self.index][0]
            elif self.start and self.end:
                from_file = self.start
            else:
                from_file = -1
        self.rom.write_int32s(self.rom.dma.dma_start + (self.index * 0x10), [start, end, start, 0])
        self.rom.changed_dma[self.index] = (from_file, start, end - start)


class DMAIterator:
    def __init__(self, rom: Rom, dma_start: int) -> None:
        self.rom: Rom = rom
        self.dma_start: int = dma_start
        self.dma_index: int = 0
        self.dma_end: int = 0
        self._dma_entries: int = 0

    @property
    def dma_entries(self) -> int:
        if not self._dma_entries:
            self._calculate_dma_entries()
        return self._dma_entries

    def _calculate_dma_entries(self) -> None:
        i = start = -1
        while start != self.dma_start:
            i += 1
            if i > 2000:
                dma_bytes = self.rom.read_bytes(self.rom.dma.dma_start, 160).hex(' ', 4)
                raise Exception(f"DMA entry for DMA table not found. Attempted to find DMA entry starting at {self.dma_start}. First 160 bytes of DMA table: {dma_bytes}")
            start = self.rom.read_int32(self.rom.dma.dma_start + (i * 0x10))
        self.dma_index = i
        self.dma_end = self.rom.read_int32(self.dma_start + (self.dma_index * 0x10) + 0x04)
        self._dma_entries = (self.dma_end - self.dma_start) >> 4

    def __getitem__(self, item: int) -> DMAEntry:
        if not isinstance(item, int):
            raise ValueError("DMAIterator only supports integer keys.")
        if item < 0:
            item = self.dma_entries + item
        if item > self.dma_entries:
            raise ValueError(f"Attempted to get DMA entry exceeding the table size: {item}")

        return DMAEntry(self.rom, item)

    def __iter__(self) -> Iterator[DMAEntry]:
        for item in range(0, self.dma_entries):
            yield self[item]

    # Gets a dmadata entry by the file start position.
    def get_dmadata_record_by_key(self, key: Optional[int]) -> DMAEntry:
        for dma_entry in self:
            if key is None and dma_entry.end == 0 and dma_entry.start == 0:
                return dma_entry
            elif dma_entry.start == key:
                return dma_entry
        raise Exception(f"`get_dmadata_record_by_key`: DMA Start '{key}' not found in the DMA Table.")

    # Gets the last used byte of rom defined in the DMA table
    def end_of_data(self) -> int:
        max_end = 0
        for dma_entry in self:
            max_end = max(max_end, dma_entry.end)

        max_end = ((max_end + 0x0F) >> 4) << 4
        return max_end

    # Finds the smallest suitable place between current files. If size is None, find the largest span of free space.
    def free_space(self, size: Optional[int] = None) -> int:
        free_space = []  # List of tuples containing size of free space and start of free space.

        # Get DMA entries in tuple form and then sort them.
        files = sorted([dma_entry.as_tuple() for dma_entry in self])

        # Find free space between files.
        for i in range(len(files)):
            end_current = ((files[i][1] + 0x0F) >> 4) << 4
            start_next = ((files[i+1][0] + 0x0F) >> 4) << 4 if i+1 < len(files) else len(self.rom.buffer)
            if end_current < start_next:
                free_space.append((start_next - end_current, end_current))

        free_space.sort()
        if not free_space:
            raise Exception(f"No free space in ROM. This should never happen. DMA entries: {self.dma_entries}")

        if size is None:
            # Return the largest free space.
            return free_space[-1][1]
        else:
            # Return the smallest area of free space that fits size.
            try:
                return next(filter(lambda f: f[0] >= size, free_space))[1]
            except StopIteration:
                raise Exception(f"Not enough free space in ROM to fit a file of size {size}. Largest region of free space available: {free_space[-1][0]}.")
