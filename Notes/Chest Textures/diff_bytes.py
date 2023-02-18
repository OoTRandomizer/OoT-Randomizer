# new texture, vanilla texture, num bytes
textures = [('silver_chest_front.bin', 'oot_chest_front.bin', 4096),
            ('silver_chest_base.bin', 'oot_chest_base.bin', 2048),
            ('gilded_chest_front.bin', 'oot_chest_front.bin', 4096),
            ('gilded_chest_base.bin', 'oot_chest_base.bin', 2048),
            ('skull_chest_front.bin', 'oot_chest_front.bin', 4096),
            ('skull_chest_base.bin', 'oot_chest_base.bin', 2048)]

for new_tex, vanilla_tex, numbytes in textures:
    with open(vanilla_tex, 'rb') as v:
        vb = v.read()
    with open(new_tex, 'rb') as n:
        nb = n.read()
    diff_tex = bytearray(numbytes)
    for index in range(len(vb)):
        diff_tex[index] = (nb[index] - vb[index]) & 0xFF
    with open(new_tex, 'wb') as nw:
        nw.write(diff_tex)