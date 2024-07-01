import zlib, sys
from pathlib import Path

class ML64Pak:
    def __init__(self, pak_data: bytearray):
        self.pak_data = pak_data

    def decompress(self, directory):
        
        # Process the .pak file

        # Starts with a ModLoader64 Header?
        # 0x0F long
        # Last 2 bytes: xx yy
        # xx = the number of items
        # yy = ???

        # Then each item is of the form:
        # DEFL xxxx yyyy zzzz
        # DEFL - deflate command. Means the data is compressed using DEFLATE algorithm. zlib.decompress and handle it
        # xxxx - file offset to the name of the compressed data file. Strings are terminated with 0xFF instead of 0x00 wtf
        # yyyy - file offset to the start of the data
        # zzzz - file offset to the end of the data

        header = self.pak_data[0:16]

        num_items = header[14]

        # read each item
        for i in range(0, num_items):
            item_offset = 0x10 + (i * 0x10)
            item = self.pak_data[item_offset:item_offset + 0x10]
            print(item)
            # Make sure it's a DEFL
            command = item[0:4].decode()
            print(command)
            if command != "DEFL":
                raise Exception(f"Unknown command encountered {command}")
            name_offset = int.from_bytes(item[4:8], 'big')
            file_start = int.from_bytes(item[8:12], 'big')
            file_end = int.from_bytes(item[12:16], 'big')

            # read the name
            file_name = ""
            char = self.pak_data[name_offset]
            while char != 0xFF:
                file_name += chr(char)
                name_offset += 1
                char = self.pak_data[name_offset]
            
            print(file_name)

            # Read the data
            file_compressed = self.pak_data[file_start:file_end+1]

            decompressed = zlib.decompress(file_compressed)

            file = Path(directory, file_name)
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("toto")

            # Open a new file
            f = open(file, 'wb')
            f.write(decompressed)
            f.close()

#ex: python3 ML64Unpack.py LuigiSmashUltimateVoice.pak ../../../data/Voices/cache

if __name__ == "__main__":
    # Read arguments
    # 1 - input file
    # 2 - output directory root
    pak_file = sys.argv[1]
    out_dir = sys.argv[2]
    # Read the .pak file from the stdin
    with open(pak_file, 'rb') as f:
        pak_data = f.read()

        pak = ML64Pak(pak_data)
        pak.decompress(out_dir)