# Originally written by mzxrules
from __future__ import annotations
from collections.abc import Sequence
from typing import Optional
import struct


class uint16:
    _struct = struct.Struct('>H')

    @staticmethod
    def write(buffer: bytearray, address: int, value: int) -> None:
        struct.pack_into('>H', buffer, address, value)

    @classmethod
    def read(cls, buffer: bytearray, address: int = 0) -> int:
        return cls._struct.unpack_from(buffer, address)[0]

    @staticmethod
    def bytes(value: int) -> bytearray:
        value = value & 0xFFFF
        return bytearray([(value >> 8) & 0xFF, value & 0xFF])

    @staticmethod
    def value(values: Sequence[int]) -> int:
        return ((values[0] & 0xFF) << 8) | (values[1] & 0xFF)


class uint32:
    _struct = struct.Struct('>I')

    @staticmethod
    def write(buffer: bytearray, address: int, value: int) -> None:
        struct.pack_into('>I', buffer, address, value)

    @classmethod
    def read(cls, buffer: bytearray, address: int = 0) -> int:
        return cls._struct.unpack_from(buffer, address)[0]

    @staticmethod
    def bytes(value: int) -> bytearray:
        value = value & 0xFFFFFFFF
        return bytearray([(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])

    @staticmethod
    def value(values: Sequence[int]) -> int:
        return ((values[0] & 0xFF) << 24) | ((values[1] & 0xFF) << 16) | ((values[2] & 0xFF) << 8) | (values[3] & 0xFF)


class int32:
    _struct = struct.Struct('>i')

    @staticmethod
    def write(buffer: bytearray, address: int, value: int) -> None:
        struct.pack_into('>i', buffer, address, value)

    @classmethod
    def read(cls, buffer: bytearray, address: int = 0) -> int:
        return cls._struct.unpack_from(buffer, address)[0]

    @staticmethod
    def bytes(value: int) -> bytearray:
        value = value & 0xFFFFFFFF
        return bytearray([(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])

    @staticmethod
    def value(values: Sequence[int]) -> int:
        value: int = ((values[0] & 0xFF) << 24) | ((values[1] & 0xFF) << 16) | ((values[2] & 0xFF) << 8) | (values[3] & 0xFF)
        if value >= 0x80000000:
            value ^= 0xFFFFFFFF
            value += 1
        return value


class uint24:
    @staticmethod
    def write(buffer: bytearray, address: int, value: int) -> None:
        byte_arr: bytes = bytes(value)
        buffer[address:address + 3] = byte_arr[0:3]

    @staticmethod
    def read(buffer: bytearray, address: int = 0) -> int:
        return (buffer[address+0] << 16) | (buffer[address+1] << 8) | buffer[address+2]

    @staticmethod
    def bytes(value: int) -> bytearray:
        value = value & 0xFFFFFF
        return bytearray([(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])

    @staticmethod
    def value(values: Sequence[int]) -> int:
        return ((values[0] & 0xFF) << 16) | ((values[1] & 0xFF) << 8) | (values[2] & 0xFF)


class BigStream:
    def __init__(self, buffer: bytearray) -> None:
        self.last_address: int = 0
        self.buffer: bytearray = buffer

    def seek_address(self, address: Optional[int] = None, delta: Optional[int] = None) -> None:
        if address is not None:
            self.last_address = address
        if delta is not None:
            self.last_address += delta

    def eof(self) -> bool:
        return self.last_address >= len(self.buffer)

    def read_byte(self, address: Optional[int] = None) -> int:
        if address is None:
            address = self.last_address
        self.last_address = address + 1
        return self.buffer[address]

    def read_bytes(self, address: Optional[int] = None, length: int = 1) -> bytearray:
        if address is None:
            address = self.last_address
        self.last_address = address + length
        return self.buffer[address: address + length]

    def read_int16(self, address: Optional[int] = None) -> int:
        if address is None:
            address = self.last_address
        return uint16.value(self.read_bytes(address, 2))

    def read_int24(self, address: Optional[int] = None) -> int:
        if address is None:
            address = self.last_address
        return uint24.value(self.read_bytes(address, 3))

    def read_int32(self, address: Optional[int] = None) -> int:
        if address is None:
            address = self.last_address
        return uint32.value(self.read_bytes(address, 4))

    def write_byte(self, address: Optional[int], value: int) -> None:
        if address is None:
            address = self.last_address
        self.buffer[address] = value
        self.last_address = address + 1

    def write_sbyte(self, address: Optional[int], value: int) -> None:
        if address is None:
            address = self.last_address
        self.write_bytes(address, struct.pack('b', value))

    def write_int16(self, address: Optional[int], value: int) -> None:
        if address is None:
            address = self.last_address
        self.write_bytes(address, uint16.bytes(value))

    def write_int24(self, address: Optional[int], value: int) -> None:
        if address is None:
            address = self.last_address
        self.write_bytes(address, uint24.bytes(value))

    def write_int32(self, address: Optional[int], value: int) -> None:
        if address is None:
            address = self.last_address
        self.write_bytes(address, uint32.bytes(value))

    def write_f32(self, address: Optional[int], value: float) -> None:
        if address is None:
            address = self.last_address
        self.write_bytes(address, struct.pack('>f', value))

    def write_bytes(self, address: Optional[int], values: Sequence[int]) -> None:
        if address is None:
            address = self.last_address
        self.last_address = address + len(values)
        self.buffer[address:address + len(values)] = values

    def write_int16s(self, address: Optional[int], values: Sequence[int]) -> None:
        if address is None:
            address = self.last_address

        i: int
        value: int
        for i, value in enumerate(values):
            self.write_int16(address + (i * 2), value)

    def write_int24s(self, address: Optional[int], values: Sequence[int]) -> None:
        if address is None:
            address = self.last_address

        i: int
        value: int
        for i, value in enumerate(values):
            self.write_int24(address + (i * 3), value)

    def write_int32s(self, address: Optional[int], values: Sequence[int]) -> None:
        if address is None:
            address = self.last_address

        i: int
        value: int
        for i, value in enumerate(values):
            self.write_int32(address + (i * 4), value)

    def append_byte(self, value: int) -> None:
        self.buffer.append(value)

    def append_sbyte(self, value: int) -> None:
        self.append_bytes(struct.pack('b', value))

    def append_int16(self, value: int) -> None:
        self.append_bytes(uint16.bytes(value))

    def append_int24(self, value: int) -> None:
        self.append_bytes(uint24.bytes(value))

    def append_int32(self, value: int) -> None:
        self.append_bytes(uint32.bytes(value))

    def append_f32(self, value: float) -> None:
        self.append_bytes(struct.pack('>f', value))

    def append_bytes(self, values: Sequence[int]) -> None:
        value: int
        for value in values:
            self.append_byte(value)

    def append_int16s(self, values: Sequence[int]) -> None:
        value: int
        for value in values:
            self.append_int16(value)

    def append_int24s(self, values: Sequence[int]) -> None:
        value: int
        for value in values:
            self.append_int24(value)

    def append_int32s(self, values: Sequence[int]) -> None:
        value: int
        for value in values:
            self.append_int32(value)
