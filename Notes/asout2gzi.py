import struct
import string
from pathlib import Path
import sys
import glob

outname = "wadpatch.gzi"

outputstr = "0000 00000000 00000001\n# crash screen and start-up progress payload for NACE\n# debug font address at offset 0x05F4 is for OoT US 1.0\n"

asmreadoffset = 0
asmdatasize = 0
readpos = 0

try:
    with open("WAD_crashscreen_patch.out", 'rb') as elf_stream:
        data = elf_stream.read()
except FileNotFoundError as ex:
        raise FileNotFoundError(f'Could not find the ASM binary file.')
        
elf_stream.close()

elf_sectionstart = struct.unpack_from('>I', data, 0x20)
elf_sectioncount = struct.unpack_from('>H', data, 0x30)

for i in range(elf_sectioncount[0]):
    section = struct.unpack_from('>IIIIII', data, (elf_sectionstart[0] + (i * 0x28)))
    sh_flags = section[2] & 0x04
    if sh_flags == 0x04:
        asmreadoffset = section[4]
        asmdatasize = section[5]
        break
    
if asmdatasize == 0:
    raise RuntimeError("I thought I could lazily find the .text section, but guess not.")
    
# Turn every non-zero 4-byte word into a command line. 
# If you want to overwrite something in the file with zeros, you'll have to do that manually.
# or do something more elaborate with the elf file. We're not writing zeros over non-zeros, so what this achieves is fine for now.
while readpos < asmdatasize:
    text = struct.unpack_from('>I', data, (asmreadoffset + readpos))
    word = text[0]
    if word != 0:
        bfill = hex(word)
        bfill = bfill.removeprefix('0x')
        bfill = bfill.zfill(8)
        offsetfill = hex(readpos)
        offsetfill = offsetfill.removeprefix('0x')
        offsetfill = offsetfill.zfill(8)
        outputstr = outputstr + ("0304 " + offsetfill + " " + bfill + '\n')
    readpos += 4

print(outputstr)
outfile = open(outname, 'w')
outfile.write(outputstr)
outfile.close()
