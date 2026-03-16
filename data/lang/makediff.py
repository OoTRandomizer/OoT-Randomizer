"""
Make a diff between two files.
For the file names, please refer to data/bin_patch.json
"""

import zlib
import json

def make_diff(original, replace, export):
    Original = open(original, "rb").read()
    New = open(replace, "rb").read()
    f = json.load(open("data/bin_patch.json"))
    s, e = [int(x, 16) for x in f[export]]
    seg = bytearray([o ^ n for o, n in zip(Original[s:e], New[s:e])])
    diff = zlib.compress(seg)
    with open(export, "wb") as f:
        f.write(diff)

def get_ia4(frm, export, start=0, size=0):
    with open(frm, "rb") as f:
        orig = f.read()
    end=start+size
    w=orig[start:end]
    with open(export,"wb") as f:
        f.write(w)

##get_ia4("baserom-decomp.z64","blue_fire_arrow_item_name_jap.ia4",0x883000,0x400)

# make_diff("baserom-decomp.z64","editedrom-decomp.z64","title.bin",0x01795300,0x017B4440)

# diff_list = [
#     "title.bin",
#     "EXTitleCard.bin",
#     "Gameover.bin",
#     "TitleCardEN.bin",
#     "ItemNameEN.bin",
#     "MapName.bin",
#     "ActionEN.bin",
#     "PlaceName.bin",
#     "FileSelEN.bin"
# ]
# for file in diff_list:
#     make_diff("data/lang/baserom.z64", "data/lang/german_edit.z64", file)
    
get_ia4("/Users/lyonniki/Desktop/oot/build/ntsc-1.0/oot-ntsc-1.0.z64", "blue_fire_arrow_item_name_eng.ia4", 0x8A1C00, 0x400)