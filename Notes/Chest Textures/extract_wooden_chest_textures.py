with open('../../ZOOTDEC.z64', 'rb') as rom:
    rom.seek(0xFEC798, 0)
    front = rom.read(4096)
    base = rom.read(2048)
    with open('oot_chest_front.bin', 'wb') as front_file:
        front_file.write(front)
    with open('oot_chest_base.bin', 'wb') as base_file:
        base_file.write(base)