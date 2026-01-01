import zlib

def make_diff(original, replace, export, start=0, end=None):
    Original = open(original, "rb").read()
    New = open(replace, "rb").read()
    s = start
    e = len(orig) if end is None else end
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

make_diff("baserom-decomp.z64","editedrom-decomp.z64","title.bin",0x01795300,0x017B4440)
