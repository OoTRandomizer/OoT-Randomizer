#!/usr/bin/env python3
from __future__ import annotations

from Rom import Rom


# Read a ci4 texture from rom and convert to rgba16
# rom - Rom
# address - address of the ci4 texture in Rom
# length - size of the texture in PIXELS
# palette - 4-bit color palette to use (max of 16 colors)
def ci4_to_rgba16(rom: Rom, address: int, length: int, palette: list[int]) -> list[int]:
    new_pixels = []
    texture = rom.read_bytes(address, length // 2)
    for byte in texture:
        new_pixels.append(palette[(byte & 0xF0) >> 4])
        new_pixels.append(palette[byte & 0x0F])
    return new_pixels


# Convert an rgba16 texture to ci8
# rgba16_texture - texture to convert
# returns - tuple (ci8_texture, palette)
def rgba16_to_ci8(rgba16_texture: list[int]) -> tuple[list[int], list[int]]:
    ci8_texture = []
    palette = get_colors_from_rgba16(rgba16_texture)  # Get all the colors in the texture
    if len(palette) > 0x100:  # Make sure there are <= 256 colors. Could probably do some fancy stuff to convert, but nah.
        raise(Exception("RGB Texture exceeds maximum of 256 colors"))
    if len(palette) < 0x100:  # Pad the palette with 0x0001 #Pad the palette with 0001s to take up the full 256 colors
        for i in range(0, 0x100 - len(palette)):
            palette.append(0x0001)

    # Create the new ci8 texture (list of bytes) by locating the index of each color from the rgba16 texture in the color palette.
    for pixel in rgba16_texture:
        if pixel in palette:
            ci8_texture.append(palette.index(pixel))
    return ci8_texture, palette


# Load a palette (essentially just an rgba16 texture) from rom
def load_palette(rom: Rom, address: int, length: int) -> list[int]:
    palette = []
    for i in range(0, length):
        palette.append(rom.read_int16(address + 2 * i))
    return palette


# Get a list of unique colors (palette) from an rgba16 texture
def get_colors_from_rgba16(rgba16_texture: list[int]) -> list[int]:
    colors = []
    for pixel in rgba16_texture:
        if pixel not in colors:
            colors.append(pixel)
    return colors


# Apply a patch to a rgba16 texture. The patch texture is exclusive or'd with the original to produce the result
# rgba16_texture - Original texture
# rgba16_patch - Patch texture. If this parameter is not supplied, this function will simply return the original texture.
# returns - new texture = texture xor patch
def apply_rgba16_patch(rgba16_texture: list[int], rgba16_patch: list[int]) -> list[int]:
    if rgba16_patch is not None and (len(rgba16_texture) != len(rgba16_patch)):
        raise(Exception("OG Texture and Patch not the same length!"))

    new_texture = []
    if not rgba16_patch:
        for i in range(0, len(rgba16_texture)):
            new_texture.append(rgba16_texture[i])
        return new_texture
    for i in range(0, len(rgba16_texture)):
        new_texture.append(rgba16_texture[i] ^ rgba16_patch[i])
    return new_texture


# Save a rgba16 texture to a file
def save_rgba16_texture(rgba16_texture: list[int], filename: str) -> None:
    file = open(filename, 'wb')
    bytes = bytearray()
    for pixel in rgba16_texture:
        bytes.extend(pixel.to_bytes(2, 'big'))
    file.write(bytes)
    file.close()


# Save a ci8 texture to a file
def save_ci8_texture(ci8_texture: list[int], filename: str) -> None:
    file = open(filename, 'wb')
    bytes = bytearray()
    for pixel in ci8_texture:
        bytes.extend(pixel.to_bytes(1, 'big'))
    file.write(bytes)
    file.close()


# Read an rgba16 texture from ROM
# rom - Rom object to load the texture from
# base_texture_address - Address of the rbga16 texture in ROM
# size - Size of the texture in PIXELS
# returns - list of ints representing each 16-bit pixel
def load_rgba16_texture_from_rom(rom: Rom, base_texture_address: int, size: int) -> list[int]:
    texture = []
    for i in range(0, size):
        texture.append(int.from_bytes(rom.read_bytes(base_texture_address + 2 * i, 2), 'big'))
    return texture


# Load an rgba16 texture from a binary file.
# filename - path to the file
# size - number of 16-bit pixels in the texture.
def load_rgba16_texture(filename: str, size: int) -> list[int]:
    texture = []
    file = open(filename, 'rb')
    for i in range(0, size):
        texture.append(int.from_bytes(file.read(2), 'big'))

    file.close()
    return texture


# Create an new rgba16 texture byte array from a rgba16 binary file. Use this if you want to create complete new textures using no copyrighted content (or for testing).
# rom - Unused set to None
# base_texture_address - Unusued set to None
# base_palette_address - Unusued set to None
# size - Size of the texture in PIXELS
# patchfile - File containing the texture to load
# returns - bytearray containing the new texture
def rgba16_from_file(rom: Rom, base_texture_address: int, base_palette_address: int, size: int, patchfile: str) -> bytearray:
    new_texture = load_rgba16_texture(patchfile, size)
    bytes = bytearray()
    for pixel in new_texture:
        bytes.extend(int.to_bytes(pixel, 2, 'big'))
    return bytes


# Create a new rgba16 texture from a original rgba16 texture and a rgba16 patch file
# rom - Rom object to load the original texture from
# base_texture_address - Address of the original rbga16 texture in ROM
# base_palette_address - Unused. Set to None (this is only used for CI4 style textures)
# size - Size of the texture in PIXELS
# patchfile - file path of a rgba16 binary texture to patch
# returns - bytearray of the new texture
def rgba16_patch(rom: Rom, base_texture_address: int, base_palette_address: int, size: int, patchfile: str) -> bytearray:
    base_texture_rgba16 = load_rgba16_texture_from_rom(rom, base_texture_address, size)
    patch_rgba16 = None
    if patchfile:
        patch_rgba16 = load_rgba16_texture(patchfile, size)
    new_texture_rgba16 = apply_rgba16_patch(base_texture_rgba16, patch_rgba16)
    bytes = bytearray()
    for pixel in new_texture_rgba16:
        bytes.extend(int.to_bytes(pixel, 2, 'big'))
    return bytes


# Create a new ci8 texture from a ci4 texture/palette and a rgba16 patch file
# rom - Rom object to load the original textures from
# base_texture_address - Address of the original ci4 texture in ROM
# base_palette_address - Address of the ci4 palette in ROM
# size - Size of the texture in PIXELS
# patchfile - file path of a rgba16 binary texture to patch
# returns - bytearray of the new texture
def ci4_rgba16patch_to_ci8(rom: Rom, base_texture_address: int, base_palette_address: int, size: int, patchfile: str) -> bytearray:
    palette = load_palette(rom, base_palette_address, 16) # load the original palette from rom
    base_texture_rgba16 = ci4_to_rgba16(rom, base_texture_address, size, palette) # load the original texture from rom and convert to ci8
    patch_rgba16 = None
    if patchfile:
        patch_rgba16 = load_rgba16_texture(patchfile, size)
    new_texture_rgba16 = apply_rgba16_patch(base_texture_rgba16, patch_rgba16)
    ci8_texture, ci8_palette = rgba16_to_ci8(new_texture_rgba16)
    # merge the palette and the texture
    bytes = bytearray()
    for pixel in ci8_palette:
        bytes.extend(int.to_bytes(pixel, 2, 'big'))
    for pixel in ci8_texture:
        bytes.extend(int.to_bytes(pixel, 1, 'big'))
    return bytes


# Function to create rgba16 texture patches for crates
def build_crate_ci8_patches() -> None:
    # load crate textures from rom
    object_kibako2_addr = 0x018B6000
    SIZE_CI4_32X128 = 4096
    rom = Rom("ZOOTDEC.z64")
    crate_palette = load_palette(rom, object_kibako2_addr + 0x00, 16)
    crate_texture_rgba16 = ci4_to_rgba16(rom, object_kibako2_addr + 0x20, SIZE_CI4_32X128, crate_palette)

    # load new textures
    crate_texture_gold_rgba16 = load_rgba16_texture('crate_heart.bin', 0x1000)

    # create patches
    gold_patch = apply_rgba16_patch(crate_texture_rgba16, crate_texture_gold_rgba16)

    # save patches
    save_rgba16_texture(gold_patch, 'crate_heart_rgba16_patch.bin')

# Function to create rgba16 texture patches for pots.
def build_pot_patches() -> None:
    # load pot textures from rom
    object_tsubo_side_addr = 0x01738000
    SIZE_32X64 = 2048
    rom = Rom("ZOOTDEC.z64")

    pot_default_rgba16 = load_rgba16_texture_from_rom(rom, object_tsubo_side_addr, SIZE_32X64)
    pot_gold_rgba16 = load_rgba16_texture('pot_gold_rgba16.bin', SIZE_32X64)
    pot_key_rgba16 = load_rgba16_texture('pot_key_rgba16.bin', SIZE_32X64)
    pot_skull_rgba16 = load_rgba16_texture('pot_skull_rgba16.bin', SIZE_32X64)
    pot_bosskey_rgba16 = load_rgba16_texture('pot_bosskey_rgba16.bin', SIZE_32X64)

    # create patches
    gold_patch = apply_rgba16_patch(pot_default_rgba16, pot_gold_rgba16)
    key_patch = apply_rgba16_patch(pot_default_rgba16, pot_key_rgba16)
    skull_patch = apply_rgba16_patch(pot_default_rgba16, pot_skull_rgba16)
    bosskey_patch = apply_rgba16_patch(pot_default_rgba16, pot_bosskey_rgba16)

    # save patches
    save_rgba16_texture(gold_patch, 'pot_gold_rgba16_patch.bin')
    save_rgba16_texture(key_patch, 'pot_key_rgba16_patch.bin')
    save_rgba16_texture(skull_patch, 'pot_skull_rgba16_patch.bin')
    save_rgba16_texture(bosskey_patch, 'pot_bosskey_rgba16_patch.bin')


def build_smallcrate_patches() -> None:
    # load small crate texture from rom
    object_kibako_texture_addr = 0xF7ECA0

    SIZE_32X64 = 2048
    rom = Rom("ZOOTDEC.z64")

    # Load textures
    smallcrate_default_rgba16 = load_rgba16_texture_from_rom(rom, object_kibako_texture_addr, SIZE_32X64)
    smallcrate_gold_rgba16 = load_rgba16_texture('smallcrate_heart.bin', SIZE_32X64)

    save_rgba16_texture(smallcrate_default_rgba16, 'smallcrate_default_rgba16.bin')
    # Create patches
    gold_patch = apply_rgba16_patch(smallcrate_default_rgba16, smallcrate_gold_rgba16)

    # save patches
    save_rgba16_texture(gold_patch, 'smallcrate_heart_rgba16_patch.bin')

def build_chest_patches():
    # load front and base texture from rom
    front_texture_addr = 0xFEC798
    base_texture_addr = 0xFED798

    SIZE_32X64 = 2048
    SIZE_32X32 = 1024
    rom = Rom("ZOOTDEC.z64")

    # Load textures
    front_default_rgba16 = load_rgba16_texture_from_rom(rom, front_texture_addr, SIZE_32X64)
    base_default_rgba16 = load_rgba16_texture_from_rom(rom, base_texture_addr, SIZE_32X32)

    front_gilded_rgba16 = load_rgba16_texture('GILDED_CHEST_FRONT_TEXTURE.bin', SIZE_32X64)
    base_gilded_rgba16 = load_rgba16_texture('GILDED_CHEST_BASE_TEXTURE.bin', SIZE_32X32)
    front_silver_rgba16 = load_rgba16_texture('SILVER_CHEST_FRONT_TEXTURE.bin', SIZE_32X64)
    base_silver_rgba16 = load_rgba16_texture('SILVER_CHEST_BASE_TEXTURE.bin', SIZE_32X32)
    front_skull_rgba16 = load_rgba16_texture('SKULL_CHEST_FRONT_TEXTURE.bin', SIZE_32X64)
    base_skull_rgba16 = load_rgba16_texture('SKULL_CHEST_BASE_TEXTURE.bin', SIZE_32X32)

    save_rgba16_texture(front_default_rgba16, 'front_default_rgba16.bin')
    save_rgba16_texture(base_default_rgba16, 'base_default_rgba16.bin')

    # Create patches
    front_gilded_patch = apply_rgba16_patch(front_default_rgba16, front_gilded_rgba16)
    base_gilded_patch = apply_rgba16_patch(base_default_rgba16, base_gilded_rgba16)
    front_silver_patch = apply_rgba16_patch(front_default_rgba16, front_silver_rgba16)
    base_silver_patch = apply_rgba16_patch(base_default_rgba16, base_silver_rgba16)
    front_skull_patch = apply_rgba16_patch(front_default_rgba16, front_skull_rgba16)
    base_skull_patch = apply_rgba16_patch(base_default_rgba16, base_skull_rgba16)

    # save patches
    save_rgba16_texture(front_gilded_patch, 'chest_front_gilded_rgba16_patch.bin')
    save_rgba16_texture(base_gilded_patch, 'chest_base_gilded_rgba16_patch.bin')
    save_rgba16_texture(front_silver_patch, 'chest_front_silver_rgba16_patch.bin')
    save_rgba16_texture(base_silver_patch, 'chest_base_silver_rgba16_patch.bin')
    save_rgba16_texture(front_skull_patch, 'chest_front_skull_rgba16_patch.bin')
    save_rgba16_texture(base_skull_patch, 'chest_base_skull_rgba16_patch.bin')


#build_crate_ci8_patches()
#build_pot_patches()
#build_smallcrate_patches()
#build_chest_patches()
