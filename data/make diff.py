import zlib

def make_diff(original, replace, export):
    Original = open(original, "rb").read()
    New = open(replace, "rb").read()
    if b"\x00\x00\x00\x00" in New:
        New = New.replace(b"\x00\x00\x00\x00", b"\xFF\xFF\xFF\x00")
    titleBytes = bytearray([a ^ b for a, b in zip(Original, New)])
    titleDiff = zlib.compress(titleBytes)
    with open(export, "wb") as new:
        new.write(titleDiff)
