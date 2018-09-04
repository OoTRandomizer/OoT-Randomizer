class LocalRom(object):
    def __init__(self, settings, patch=True):
        self.last_address = None

        file = settings.rom
        decomp_file = 'ZOOTDEC.z64'

        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        #os.chdir(output_path(os.path.dirname(os.path.realpath(__file__))))

        try:
            # Read decompressed file if it exists
            with open(decomp_file, 'rb') as stream:
                self.buffer = read_rom(stream)
            # This is mainly for validation testing, but just in case...
            self.decompress_rom_file(decomp_file, decomp_file)
        except Exception as ex:
            # No decompressed file, instead read Input ROM
            with open(file, 'rb') as stream:
                self.buffer = read_rom(stream)
            self.decompress_rom_file(file, decomp_file)

        # Add file to maximum size
        self.buffer.extend(bytearray([0x00] * (0x4000000 - len(self.buffer))))

    def decompress_rom_file(self, file, decomp_file):
        validCRC = [
            [0xEC, 0x70, 0x11, 0xB7, 0x76, 0x16, 0xD7, 0x2B], # Compressed
            [0x70, 0xEC, 0xB7, 0x11, 0x16, 0x76, 0x2B, 0xD7], # Byteswap compressed
            [0x93, 0x52, 0x2E, 0x7B, 0xE5, 0x06, 0xD4, 0x27], # Decompressed
        ]

        # Validate ROM file
        file_name = os.path.splitext(file)
        romCRC = list(self.buffer[0x10:0x18])
        if romCRC not in validCRC:
            # Bad CRC validation
            raise RuntimeError('ROM file %s is not a valid OoT 1.0 US ROM.' % file)
        elif len(self.buffer) < 0x2000000 or len(self.buffer) > (0x4000000) or file_name[1] not in ['.z64', '.n64']:
            # ROM is too big, or too small, or not a bad type
            raise RuntimeError('ROM file %s is not a valid OoT 1.0 US ROM.' % file)
        elif len(self.buffer) == 0x2000000:
            # If Input ROM is compressed, then Decompress it
            if platform.system() == 'Windows':
                if 8 * struct.calcsize("P") == 64:
                    subprocess.call(["Decompress\\Decompress.exe", file, decomp_file])
                else:
                    subprocess.call(["Decompress\\Decompress32.exe", file, decomp_file])
                with open(decomp_file, 'rb') as stream:
                    self.buffer = read_rom(stream)
            elif platform.system() == 'Linux':
                subprocess.call(["Decompress/Decompress", file])
                with open(("ZOOTDEC.z64"), 'rb') as stream:
                    self.buffer = read_rom(stream)
            elif platform.system() == 'Darwin':
                subprocess.call(["Decompress/Decompress.out", file])
                with open(("ZOOTDEC.z64"), 'rb') as stream:
                    self.buffer = read_rom(stream)
            else:
                raise RuntimeError('Unsupported operating system for decompression. Please supply an already decompressed ROM.')
        else:
            # ROM file is a valid and already uncompressed
            pass


    def read_byte(self, address):
        return self.buffer[address]

    def read_bytes(self, address, len):
        return self.buffer[address : address + len]

    def read_int16(self, address):
        return bytes_as_int16(self.read_bytes(address, 2))

    def read_int24(self, address):
        return bytes_as_int24(self.read_bytes(address, 3))

    def read_int32(self, address):
        return bytes_as_int32(self.read_bytes(address, 4))

    def write_byte(self, address, value):
        if address == None:
            address = self.last_address
        self.buffer[address] = value
        self.last_address = address + 1

    def write_int16(self, address, value):
        if address == None:
            address = self.last_address
        self.write_bytes(address, int16_as_bytes(value))

    def write_int24(self, address, value):
        if address == None:
            address = self.last_address
        self.write_bytes(address, int24_as_bytes(value))

    def write_int32(self, address, value):
        if address == None:
            address = self.last_address
        self.write_bytes(address, int32_as_bytes(value))

    def write_bytes(self, startaddress, values):
        if startaddress == None:
            startaddress = self.last_address
        for i, value in enumerate(values):
            self.write_byte(startaddress + i, value)

    def write_int16s(self, startaddress, values):
        if startaddress == None:
            startaddress = self.last_address
        for i, value in enumerate(values):
            self.write_int16(startaddress + (i * 2), value)

    def write_int24s(self, startaddress, values):
        if startaddress == None:
            startaddress = self.last_address
        for i, value in enumerate(values):
            self.write_int24(startaddress + (i * 3), value)

    def write_int32s(self, startaddress, values):
        if startaddress == None:
            startaddress = self.last_address
        for i, value in enumerate(values):
            self.write_int32(startaddress + (i * 4), value)

    def write_to_file(self, file):
        self.update_crc()
        with open(file, 'wb') as outfile:
            outfile.write(self.buffer)

    def update_crc(self):
        t1 = t2 = t3 = t4 = t5 = t6 = 0xDF26F436
        u32 = 0xFFFFFFFF

        cur = 0x1000
        while cur < 0x00101000:
            d = self.read_int32(cur)

            if ((t6 + d) & u32) < t6:
                t4 += 1 

            t6 = (t6+d) & u32
            t3 ^= d
            shift = d & 0x1F
            r = ((d << shift) | (d >> (32 - shift))) & u32
            t5 = (t5 + r) & u32

            if t2 > d:
                t2 ^= r
            else:
                t2 ^= t6 ^ d

            data2 = self.read_int32(0x750 + (cur & 0xFF))
            t1 += data2 ^ d
            t1 &= u32

            cur += 4

        crc0 = t6 ^ t4 ^ t3
        crc1 = t5 ^ t2 ^ t1

        # Finally write the crc back to the rom
        self.write_int32s(0x10, [crc0, crc1])


def read_rom(stream):
    "Reads rom into bytearray"
    buffer = bytearray(stream.read())
    return buffer


def int16_as_bytes(value):
    value = value & 0xFFFF
    return [(value >> 8) & 0xFF, value & 0xFF]

def int24_as_bytes(value):
    value = value & 0xFFFFFFFF
    return [(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF]

def int32_as_bytes(value):
    value = value & 0xFFFFFFFF
    return [(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF]

def bytes_as_int16(values):
    return (values[0] << 8) | values[1]

def bytes_as_int24(values):
    return (values[0] << 16) | (values[1] << 8) | values[2]

def bytes_as_int32(values):
    return (values[0] << 24) | (values[1] << 16) | (values[2] << 8) | values[3]