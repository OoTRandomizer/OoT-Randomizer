import zlib

def make_title(replace, export):
    Original = open("titleoriginal.bin", "rb").read()
    New = open(replace, "rb").read()
    titleBytes = bytearray([a ^ b for a, b in zip(Original, New)])
    titleDiff = zlib.compress(titleBytes)
    with open(export, "wb") as new:
        new.write(titleDiff)

make_title("titleJP.bin", "JP.bin")
