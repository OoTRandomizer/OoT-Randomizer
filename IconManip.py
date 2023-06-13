from __future__ import annotations
import sys
from collections.abc import Sequence, MutableSequence
from typing import TYPE_CHECKING, Optional

from Utils import data_path

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    TypeAlias = str

if TYPE_CHECKING:
    from Rom import Rom

RGBValues: TypeAlias = "MutableSequence[MutableSequence[int]]"


# TODO
# Move the tunic to the generalized system

# Function for adding hue to a greyscaled icon
def add_hue(image: MutableSequence[int], color: Sequence[int], tiff: bool = False) -> MutableSequence[int]:
    start = 154 if tiff else 0
    for i in range(start, len(image), 4):
        try:
            for x in range(3):
                image[i+x] = int(((image[i+x]/255) * (color[x]/255)) * 255)
        except:
            pass
    return image


def add_rainbow(img: MutableSequence[int], width: int, tiff: bool = False) -> MutableSequence[int]:
    # Define the colors of the rainbow
    colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0),
              (0, 128, 0), (0, 0, 255), (75, 0, 130),
              (238, 130, 238)]
    start = 154 if tiff else 0
    for y in range(0, width):
        for x in range(0, width):
            try:
                color_index = int((x + y) / (width / len(colors)))
                color_start = colors[color_index % len(colors)]
                color_end = colors[(color_index + 1) % len(colors)]
                color = tuple(int(color_start[i] + (color_end[i] - color_start[i]) * ((x + y) % (width / len(colors))) / (width / len(colors))) for i in range(3))
                for c in range(3):
                    img[start + (y*width*4) + (x*4) + c] = int(((img[start + (y*width*4) + (x*4) + c]/255) * (color[c]/255)) * 255)
            except:
                pass
    return img


# Function for adding belt to tunic
def add_belt(tunic: MutableSequence[int], belt: MutableSequence[int], tiff: bool = False) -> MutableSequence[int]:
    start = 154 if tiff else 0
    for i in range(start, len(tunic), 4):
        try:
            if belt[i+3] != 0:
                alpha = belt[i+3] / 255
                for x in range(3):
                    tunic[i+x] = int((belt[i+x] * alpha) + (tunic[i+x] * (1 - alpha)))
        except:
            pass
    return tunic


# Function for putting tunic colors together
def generate_tunic_icon(color: Sequence[int]) -> MutableSequence[int]:
    with open(data_path('icons/grey.tiff'), 'rb') as grey_fil, open(data_path('icons/belt.tiff'), 'rb') as belt_fil:
        grey = list(grey_fil.read())
        belt = list(belt_fil.read())
        return add_belt(add_hue(grey, color, True), belt, True)[154:]


def generate_rainbow_tunic_icon() -> MutableSequence[int]:
    with open(data_path('icons/grey.tiff'), 'rb') as grey_fil, open(data_path('icons/belt.tiff'), 'rb') as belt_fil:
        grey = list(grey_fil.read())
        belt = list(belt_fil.read())
        return add_belt(add_rainbow(grey, 32, True), belt, True)[154:]

# END TODO


# Function to add extra data on top of icon
def add_extra_data(rgb_values: RGBValues, filename: str, intensity: float = 0.5) -> None:
    file_rgb = []
    with open(filename, "rb") as fil:
        data = fil.read()
        for i in range(0, len(data), 4):
            file_rgb.append([data[i + 0], data[i + 1], data[i + 2], data[i + 3]])
    for i in range(len(rgb_values)):
        alpha = file_rgb[i][3] / 255
        for x in range(3):
            rgb_values[i][x] = int((file_rgb[i][x] * alpha + intensity) + (rgb_values[i][x] * (1 - alpha - intensity)))


# Function for desaturating RGB values
def greyscale_rgb(rgb_values: RGBValues, intensity: int = 2) -> RGBValues:
    for rgb in rgb_values:
        rgb[0] = rgb[1] = rgb[2] = int((rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722) * intensity)
    return rgb_values


# Converts rgb5a1 values to RGBA lists
def rgb5a1_to_rgb(rgb5a1_bytes: bytes) -> RGBValues:
    pixels = []
    for i in range(0, len(rgb5a1_bytes), 2):
        bits = format(rgb5a1_bytes[i], '#010b')[2:] + format(rgb5a1_bytes[i + 1], '#010b')[2:]
        r = int(int(bits[0:5], 2) * (255/31))
        g = int(int(bits[5:10], 2) * (255/31))
        b = int(int(bits[10:15], 2) * (255/31))
        a = int(bits[15], 2) * 255
        pixels.append([r, g, b, a])
    return pixels


# Adds a hue to RGB values
def add_hue_to_rgb(rgb_values: RGBValues, color: Sequence[int]) -> RGBValues:
    for rgb in rgb_values:
        for i in range(3):
            rgb[i] = int(((rgb[i]/255) * (color[i]/255)) * 255)
    return rgb_values


# Convert RGB to RGB5a1 format
def rgb_to_rgb5a1(rgb_values: RGBValues) -> bytes:
    rgb5a1 = []
    for rgb in rgb_values:
        r = int(rgb[0] / (255/31))
        r = r if r <= 31 else 31
        r = r if r >= 0 else 0
        g = int(rgb[1] / (255/31))
        g = g if g <= 31 else 31
        g = g if g >= 0 else 0
        b = int(rgb[2] / (255/31))
        b = b if b <= 31 else 31
        b = b if b >= 0 else 0
        a = int(rgb[3] / 255)
        bits = format(r, '#07b')[2:] + format(g, '#07b')[2:] + format(b, '#07b')[2:] + format(a, '#03b')[2:]
        rgb5a1.append(int(bits[:8], 2))
        rgb5a1.append(int(bits[8:], 2))
    for i in rgb5a1:
        assert i <= 255, i
    return bytes(rgb5a1)


# Patch overworld icons
def patch_overworld_icon(rom: Rom, color: Optional[Sequence[int]], address: int, filename: Optional[str] = None) -> None:
    original = rom.original.read_bytes(address, 0x800)

    if color is None:
        rom.write_bytes(address, original)
        return

    rgb_bytes = rgb5a1_to_rgb(original)
    greyscaled = greyscale_rgb(rgb_bytes)
    rgb_bytes = add_hue_to_rgb(greyscaled, color)
    if filename is not None:
        add_extra_data(rgb_bytes, filename)
    rom.write_bytes(address, rgb_to_rgb5a1(rgb_bytes))
