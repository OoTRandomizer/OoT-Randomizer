# text details: https://wiki.cloudmodding.com/oot/Text_Format

from __future__ import annotations
import random
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Optional, Any, Dict, Tuple, List
from math import ceil
import json
import itertools

from ItemList import REWARD_COLORS
from HintList import misc_item_hint_table, misc_location_hint_table
from TextBox import line_wrap
from Utils import find_last, data_path
from Language import Language

if TYPE_CHECKING:
    from Rom import Rom
    from World import World

ENG_TEXT_START: int = 0x92D000
JPN_TEXT_START: int = 0x8EB000
ENG_TEXT_SIZE_LIMIT: int = 0x39000
JPN_TEXT_SIZE_LIMIT: int = 0x3B000

JPN_TABLE_START: int = 0xB808AC
ENG_TABLE_START: int = 0xB849EC
CREDITS_TABLE_START: int = 0xB88C0C

JPN_TABLE_SIZE: int = ENG_TABLE_START - JPN_TABLE_START
ENG_TABLE_SIZE: int = CREDITS_TABLE_START - ENG_TABLE_START

EXTENDED_TABLE_START: int = JPN_TABLE_START  # start writing entries to the jp table instead of english for more space
EXTENDED_TABLE_SIZE: int = JPN_TABLE_SIZE + ENG_TABLE_SIZE  # 0x8360 bytes, 4204 entries

EXTENDED_TEXT_START: int = JPN_TABLE_START  # start writing text to the jp table instead of english for more space
EXTENDED_TEXT_SIZE_LIMIT: int = JPN_TEXT_SIZE_LIMIT + ENG_TEXT_SIZE_LIMIT  # 0x74000 bytes

# name of type, followed by number of additional bytes to read, follwed by a function that prints the code
CONTROL_CODES: dict[int, tuple[str, int, Callable[[Any], str]]] = {
    0x00: ('pad', 0, lambda _: '<pad>' ),
    0x01: ('line-break', 0, lambda _: '\n' ),
    0x02: ('end', 0, lambda _: '' ),
    0x04: ('box-break', 0, lambda _: '\n▼\n' ),
    0x05: ('color', 1, lambda d: '<color ' + "{:02x}".format(d) + '>' ),
    0x06: ('gap', 1, lambda d: '<' + str(d) + 'px gap>' ),
    0x07: ('goto', 2, lambda d: '<goto ' + "{:04x}".format(d) + '>' ),
    0x08: ('instant', 0, lambda _: '<allow instant text>' ),
    0x09: ('un-instant', 0, lambda _: '<disallow instant text>' ),
    0x0A: ('keep-open', 0, lambda _: '<keep open>' ),
    0x0B: ('event', 0, lambda _: '<event>' ),
    0x0C: ('box-break-delay', 1, lambda d: '\n▼<wait ' + str(d) + ' frames>\n' ),
    0x0E: ('fade-out', 1, lambda d: '<fade after ' + str(d) + ' frames?>' ),
    0x0F: ('name', 0, lambda _: '<name>' ),
    0x10: ('ocarina', 0, lambda _: '<ocarina>' ),
    0x12: ('sound', 2, lambda d: '<play SFX ' + "{:04x}".format(d) + '>' ),
    0x13: ('icon', 1, lambda d: '<icon ' + "{:02x}".format(d) + '>' ),
    0x14: ('speed', 1, lambda d: '<delay each character by ' + str(d) + ' frames>' ),
    0x15: ('background', 3, lambda d: '<set background to ' + "{:06x}".format(d) + '>' ),
    0x16: ('marathon', 0, lambda _: '<marathon time>' ),
    0x17: ('race', 0, lambda _: '<race time>' ),
    0x18: ('points', 0, lambda _: '<points>' ),
    0x19: ('skulltula', 0, lambda _: '<skulltula count>' ),
    0x1A: ('unskippable', 0, lambda _: '<text is unskippable>' ),
    0x1B: ('two-choice', 0, lambda _: '<start two choice>' ),
    0x1C: ('three-choice', 0, lambda _: '<start three choice>' ),
    0x1D: ('fish', 0, lambda _: '<fish weight>' ),
    0x1E: ('high-score', 1, lambda d: '<high-score ' + "{:02x}".format(d) + '>' ),
    0x1F: ('time', 0, lambda _: '<current time>' ),
    0xF0: ('silver_rupee', 1, lambda d: '<silver rupee count ' + "{:02x}".format(d) + '>' ),
    0xF1: ('key_count', 1, lambda d: '<key count ' + "{:02x}".format(d) + '>' ),
    0xF2: ('outgoing_item_filename', 0, lambda _: '<outgoing item filename>' ),
    0xF3: ('farores_wind_destination', 0, lambda _: '<farores_wind_destination>' ),
}

CONTROL_CHARS_JP: dict[str, tuple[str, str|int, int, int]] = {
    '　': ('pad', '　', 0, 0x00),
    '&': ('line-break', 0x0A, 0, 0x01),
    '｝': ('end', '｝', 0, 0x02),
    '^': ('box-break', '▼', 0, 0x04),
    '#': ('color', 0x0B, 1, 0x05),
    '☞': ('gap', 0x86C7, 1, 0x06),
    '⇒': ('goto', '⇒', 2, 0x07),
    '♂': ('instant', '♂', 0, 0x08),
    '♀': ('un-instant', '♀', 0, 0x09),
    '☜': ('keep-open', 0x86C8, 0, 0x0A),
    '◆': ('event', '◆', 0, 0x0B),
    '▲': ('box-break-delay', '▲', 1, 0x0C),
    '◇': ('fade-out', '◇', 1, 0x0E),
    '@': ('name', 0x874F, 0, 0x0F),
    'Å': ('ocarina', 0x81F0, 0, 0x10),
    '♭': ('sound', '♭', 2, 0x12),
    '★': ('icon', '★', 1, 0x13),
    '☝': ('speed', 0x86C9, 1, 0x14),
    '〠': ('background', 0x86B3, 3, 0x15),
    '大⃝': ('marathon', 0x8791, 0, 0x16),
    '小⃝': ('race', 0x8792, 0, 0x17),
    '㊘': ('points', 0x879B, 0, 0x18),
    '♠': ('skulltula', 0x86A3, 0, 0x19),
    '☆': ('unskippable', '☆', 0, 0x1A),
    '⊂': ('two-choice', '⊂', 0, 0x1B),
    '∈': ('three-choice', '∈', 0, 0x1C),
    '♣': ('fish', 0x86A4, 0, 0x1D),
    '♤': ('highscore', 0x869F, 1, 0x1E),
    '■': ('time', '■', 0, 0x1F),
    '㍓': ('silver_rupee', 0x87F0, 1, 0xF0),
    '♧': ('key_count', 0x87F1, 1, 0xF1),
    '☼': ('outgoing_item_filename', 0x87F2, 0, 0xF2),
    '▷': ('farores_wind_destination', 0x87F3, 0, 0xF3),
}

CC_PARSE_JP: Dict[int, Tuple[str, int, Callable[[Any], str]]] = {}

for _k, (name_jp, byte, ext_len_jp, code) in CONTROL_CHARS_JP.items():
    byte_key = byte if isinstance(byte, int) else int.from_bytes(byte.encode("cp932"), 'big')
    try:
        print_fmt = CONTROL_CODES[code][2]
    except KeyError:
        raise ValueError(f"The Value respondes with {name_jp!r} doesn't exist in CONTROL_CODES[{code:#04x}]")
    CC_PARSE_JP[byte_key] = (name_jp, ext_len_jp, print_fmt, _k)


# Maps unicode characters to corresponding bytes in OOTR's character set.
CHARACTER_MAP: dict[str, int] = {
    'Ⓐ': 0x9F,
    'Ⓑ': 0xA0,
    'Ⓒ': 0xA1,
    'Ⓛ': 0xA2,
    'Ⓡ': 0xA3,
    'Ⓩ': 0xA4,
    '⯅': 0xA5,
    '⯆': 0xA6,
    '⯇': 0xA7,
    '⯈': 0xA8,
    chr(0xA9): 0xA9,  # Down arrow   -- not sure what best supports this
    chr(0xAA): 0xAA,  # Analog stick -- not sure what best supports this
}
# Support other ways of directly specifying controller inputs in OOTR's character set.
# (This is backwards-compatibility support for ShadowShine57's previous patch.)
CHARACTER_MAP.update(tuple((chr(v), v) for v in CHARACTER_MAP.values()))

# Characters 0x20 thru 0x7D map perfectly.  range() excludes the last element.
CHARACTER_MAP.update((chr(c), c) for c in range(0x20, 0x7e))

# Other characters, source: https://wiki.cloudmodding.com/oot/Text_Format
CHARACTER_MAP.update((c, ix) for ix, c in enumerate(
        (
            '\u203e'             # 0x7f
            'ÀîÂÄÇÈÉÊËÏÔÖÙÛÜß'   # 0x80 .. #0x8f
            'àáâäçèéêëïôöùûü'    # 0x90 .. #0x9e
        ),
        start=0x7f
))

SPECIAL_CHARACTERS: dict[int, str] = {
    0x9F: '[A]',
    0xA0: '[B]',
    0xA1: '[C]',
    0xA2: '[L]',
    0xA3: '[R]',
    0xA4: '[Z]',
    0xA5: '[C Up]',
    0xA6: '[C Down]',
    0xA7: '[C Left]',
    0xA8: '[C Right]',
    0xA9: '[Triangle]',
    0xAA: '[Control Stick]',
}

SCJP: dict[int, str] = {k + 0x8300: v for k, v in SPECIAL_CHARACTERS.items()}

REVERSE_MAP: list[str] = list(chr(x) for x in range(256))

for char, byte in CHARACTER_MAP.items():
    SPECIAL_CHARACTERS.setdefault(byte, char)
    REVERSE_MAP[byte] = char

try:
    CHARACTER_MAP_JP, REVERSE_MAP_JP = json.load(open(data_path('generated/jp_char_map.otrx'), mode="r+"))
except:
    CHARACTER_MAP_JP: Dict[str, int] = {}
    for cp in range(0x110000):
        ch = chr(cp)
        if cp in CC_PARSE_JP.keys():
            continue
        try:
            b = ch.encode("cp932")
        except UnicodeEncodeError:
            continue                       # skip characters not in the JP font

        if len(b) == 1:                    # single-byte (same as US ASCII & half-width kana)
            code = b[0]
        else:                              # two-byte sequence: high byte first
            code = (b[0] << 8) | b[1]
        CHARACTER_MAP_JP[ch] = code

    # 2. add the controller glyphs explicitly (Greek Α … Μ)
    for sjis_code, token in SCJP.items():
        glyph = bytes([(sjis_code >> 8) & 0xFF, sjis_code & 0xFF]).decode("cp932")
        CHARACTER_MAP_JP[glyph] = sjis_code

    REVERSE_MAP_JP: List[str] = ["\uFFFD"] * 0x10000     # default U+FFFD for gaps

    #  regular characters …
    for ch, code in CHARACTER_MAP_JP.items():
        if code < 0x10000:
            REVERSE_MAP_JP[code] = ch

    #  … then override with tokens for special controller inputs
    for code, token in SCJP.items():
        if code < 0x10000:
            REVERSE_MAP_JP[code] = token
    json.dump([CHARACTER_MAP_JP, REVERSE_MAP_JP], open(data_path('generated/jp_char_map.otrx'), mode="w"))

# [0x0500,0x0560] (inclusive) are reserved for plandomakers
GOSSIP_STONE_MESSAGES: list[int] = list(range(0x0401, 0x04FF))  # ids of the actual hints
GOSSIP_STONE_MESSAGES += [0x2053, 0x2054]  # shared initial stone messages
TEMPLE_HINTS_MESSAGES: list[int] = [0x7057, 0x707A]  # dungeon reward hints from the temple of time pedestal
GS_TOKEN_MESSAGES: list[int] = [0x00B4, 0x00B5]  # Get Gold Skulltula Token messages
ERROR_MESSAGE: int = 0x0001
IMPORTANT_ITEM_MESSAGES_IDS = [
    6, 28, 29, 30, 42, 97, 98, 99, 100, 101,
    124, 125, 126, 127, 135, 136, 137, 138,
    139, 140, 142, 143, 146, 147, 148, 149,
    155, 159, 160, 161, 162, 163, 165, 166,
    169, 243, 36891, 36892, 36893, 36894,
    36895, 36896, 36897, 36898, 36899, 36900,
    36901, 36902, 36903, 36904, 36905, 36906,
    36907, 36908, 36909, 36910, 36911, 36912,
    36913, 36914, 36915, 36916, 36917, 36918,
    36919, 36920, 36921, 36922, 36923, 36924,
    36925, 36926, 36927, 36928, 36929, 36930,
    36931, 36932, 36933, 36934, 36937, 36941,
    36942, 36943, 36944, 36945, 36946, 36947,
    36950, 36952, 36955, 36956, 36957, 36960,
    36961, 36962, 36963, 36965, 36966, 36967,
    36968, 36969, 36970, 36971, 36973, 36975,
    36976, 36977, 36980, 36981, 36982, 36983,
    36984, 36985, 36986, 36987, 36988, 36989,
    36990, 36991, 36992, 36993, 36994, 36995,
    36996, 36997, 36998, 36999, 37000, 37001, 37002
    ]

new_messages = [] # Used to keep track of new/updated messages to prevent duplicates. Clear it at the start of patches


COLOR_MAP: dict[str, list[str, str]] = {
    'White':      ['\x40', "00"],
    'Red':        ['\x41', "01"],
    'Green':      ['\x42', "02"],
    'Blue':       ['\x43', "03"],
    'Light Blue': ['\x44', "04"],
    'Pink':       ['\x45', "05"],
    'Yellow':     ['\x46', "06"],
    'Black':      ['\x47', "07"],
}


# convert byte array to an integer
def bytes_to_int(data: bytes, signed: bool = False) -> int:
    return int.from_bytes(data, byteorder='big', signed=signed)


# convert int to an array of bytes of the given width
def int_to_bytes(num: int, width: int, signed: bool = False) -> bytes:
    return int.to_bytes(num, width, byteorder='big', signed=signed)


def display_code_list(codes: list[TextCode]) -> str:
    message = ""
    for code in codes:
        message += str(code)
    return message

def encode_text_string_jp(text: str) -> list[int]:
    result = []
    c = ""
    q = 0
    it=iter(text)
    for ch in it:
        if q != 0:
            c += ch
            q -= 1
            if len(c) == 4 or (q == 0 and c != ""):
                result.append(int(f"{c}", 16))
                c = ""
            continue
        if ch in CONTROL_CHARS_JP.keys():
            _, h, q, _ = CONTROL_CHARS_JP[ch]
            if q % 2 == 1:
                c += "0C" if ch == "#" else "00"
            q *= 2
            if type(h) == int:
                result.append(h)
            else:
                result.append(int.from_bytes(h.encode("cp932"), "big"))
            continue
        mapped = CHARACTER_MAP_JP.get(ch)
        if mapped:
            result.append(mapped)
            continue
        else:
            result.append(int.from_bytes(ch.encode("cp932"), "big"))
    return result

def encode_text_string(text: str) -> list[int]:
    result = []
    it = iter(text)
    for ch in it:
        n = ord(ch)
        mapped = CHARACTER_MAP.get(ch)
        if mapped:
            result.append(mapped)
            continue
        if n in CONTROL_CODES:
            result.append(n)
            for _ in range(CONTROL_CODES[n][1]):
                result.append(ord(next(it)))
            continue
        if n in CHARACTER_MAP.values(): # Character has already been translated
            result.append(n)
            continue
        raise ValueError(f"While encoding {text!r}: Unable to translate unicode character {ch!r} ({n}).  (Already decoded: {result!r})")
    return result

def bytearray_to_list(text: bytearray, lang: int):
    l = list(text)
    if lang:
        return l
    else:
        return [hi * 0x100 + lo for hi, lo in zip(l[::2], l[1::2])]

def form_list(text: list[int], lang: int):
    if lang: return text
    else:
        if all([t<256*256 for t in text]):
            return text
        return [hi * 0x100 + lo for hi, lo in zip(text[::2], text[1::2])]

def parse_control_codes(text: list[int] | bytearray | str, lang: int) -> list[TextCode]:
    if isinstance(text, list):
        text_bytes = form_list(text, lang)
    elif isinstance(text, bytearray):
        text_bytes = bytearray_to_list(text, lang)
    else:
        text_bytes = encode_text_string(text) if lang else encode_text_string_jp(text)

    text_codes = []
    index = 0
    while index < len(text_bytes):
        next_char = text_bytes[index]
        data = 0
        index += 1
        if lang:
            if next_char in CONTROL_CODES:
                extra_bytes = CONTROL_CODES[next_char][1]
                if extra_bytes > 0:
                    data = bytes_to_int(text_bytes[index: index + extra_bytes])
                    index += extra_bytes
        else:
            if next_char in CC_PARSE_JP:
                extra_bytes = ceil(CC_PARSE_JP[next_char][1]/2)
                if extra_bytes > 0:
                    dt = []
                    for x in text_bytes[index: index + extra_bytes]:
                        dt += [x >> 8 & 0xFF, x & 0xFF]
                    data = bytes_to_int(dt)
                    index += extra_bytes
        text_code = TextCode(next_char, data, lang)
        text_codes.append(text_code)
        if text_code.code == [0x8170, 0x02][lang]:  # message end code
            break
    return text_codes



# holds a single character or control code of a string
class TextCode:
    def __init__(self, code: int, data: int, lang: str|int) -> None:
        self.code: int = code
        self.lang: int = 0 if lang in ["jp", 0] else 1
        self.get_control_codes()
        if code in self.CC:
            self.type = self.CC[code][0]
        else:
            self.type = 'character'
        self.data: int = data

    def get_control_codes(self):
        if self.lang:
            self.CC=CONTROL_CODES
            self.SP=SPECIAL_CHARACTERS
            self.RM=REVERSE_MAP
        else:
            self.CC=CC_PARSE_JP
            self.SP=SCJP
            self.RM=REVERSE_MAP_JP

    def display(self) -> str:
        if self.code in self.CC:
            sub=self.data
            if self.CC[self.code][0] == "color" and not self.lang:
                sub -= 0x0C00
            return self.CC[self.code][2](sub)
        elif self.code in self.SP:
            return self.SP[self.code]
        elif self.code >= 0x7F and self.lang:
            return '?'
        else:
            if self.code == 0x86D3:
                return '?'
            return chr(self.code) if self.lang else int_to_bytes(self.code, 2).decode("cp932")

    def get_python_string(self) -> str:
        if self.code in self.CC:
            ret = ''
            data = self.data
            for _ in range(0, self.CC[self.code][1]):
                ret = f'\\x{data & 0xFF:02X}{ret}' if self.lang else f'\\x{data & 0xFFFF:04X}{ret}'
                data >>= 16 // (self.lang+1)
            ret = f'\\x{self.code:02X}{ret}' if self.lang else f'\\x{self.code:04X}{ret}'
            return ret
        elif self.code in self.SP:
            return f'\\x{self.code:02X}' if self.lang else f'\\x{self.code:04X}'
        elif self.code >= 0x7F and self.lang:
            return '?'
        else:
            return chr(self.code) if self.lang else int_to_bytes(self.code, 2).decode("cp932")

    def get_string(self) -> str:
        if self.code in self.CC:
            ret = ''
            subdata = self.data
            if self.lang:
                for _ in range(0, self.CC[self.code][1]):
                    ret = chr(subdata & 0xFF) + ret
                    subdata >>= 16 // (self.lang+1)
                ret = chr(self.code) + ret
                return ret
            else:
                name, ext_len, _, literal=self.CC[self.code]
                if name == "color":
                    subdata -= 0x0C00
                width = ext_len * 2
                return literal+f"{subdata:0{width}X}" if ext_len!=0 else literal
        else:
            # raise ValueError(repr(REVERSE_MAP))
            return self.RM[self.code]

    def size(self) -> int:
        if self.lang:
            size = 1
            if self.code in self.CC:
                size += self.CC[self.code][1]
        else:
            size = 2
            if self.code in self.CC:
                size += ceil(self.CC[self.code][1]/2)*2
        return size

    # writes the code to the given offset, and returns the offset of the next byte
    def write(self, rom: Rom, text_start: int, offset: int) -> int:
        rom.write_bytes(text_start + offset, list(map(int, int_to_bytes(self.code, 2 - self.lang))))

        extra_bytes = 0
        if self.code in self.CC:
            extra_bytes = self.CC[self.code][1] if self.lang else ceil(self.CC[self.code][1] / 2) * 2
            bytes_to_write = int_to_bytes(self.data, extra_bytes)
            rom.write_bytes(text_start + offset + (2 - self.lang), bytes_to_write)

        return offset + (2 - self.lang) + extra_bytes

    __str__ = __repr__ = display


# holds a single message, and all its data
class Message:
    def __init__(self, raw_text: list[int] | bytearray | str, index: int, id: int, opts: int, offset: int, length: int, lang: str) -> None:
        self.lang: int = 0 if lang == "jp" else 1
        if isinstance(raw_text, str):
            raw_text = encode_text_string(raw_text) if self.lang else encode_text_string_jp(raw_text)
        elif not isinstance(raw_text, bytearray):
            raw_text = bytearray(raw_text)

        self.raw_text: bytearray = raw_text

        self.index: int = index
        self.id: int = id
        self.opts: int = opts  # Textbox type and y position
        self.box_type: int = (self.opts & 0xF0) >> 4
        self.position: int = (self.opts & 0x0F)
        self.offset: int = offset
        self.length: int = length

        self.has_goto: bool = False
        self.has_keep_open: bool = False
        self.has_event: bool = False
        self.has_fade: bool = False
        self.has_ocarina: bool = False
        self.has_two_choice: bool = False
        self.has_three_choice: bool = False
        self.ending: Optional[TextCode] = None

        self.text_codes: list[TextCode] = []
        self.text: str = ''
        self.unpadded_length: int = 0
        self.parse_text()

    def display(self) -> str:
        meta_data = [
            "#" + str(self.index),
            "ID: 0x" + "{:04x}".format(self.id),
            "Offset: 0x" + "{:06x}".format(self.offset),
            "Length: 0x" + "{:04x}".format(self.unpadded_length) + "/0x" + "{:04x}".format(self.length),
            "Box Type: " + str(self.box_type),
            "Postion: " + str(self.position)
        ]
        return ', '.join(meta_data) + '\n' + self.text

    def get_python_string(self) -> str:
        ret = ''
        for code in self.text_codes:
            ret = ret + code.get_python_string()
        return ret

    def get_string(self) -> str:
        ret = ''
        for code in self.text_codes:
            ret = ret + code.get_string()
        return ret

    # check if this is an unused message that just contains it's own id as text
    def is_id_message(self) -> bool:
        if (self.lang and self.unpadded_length != 5) or self.id == 0xFFFC:
            return False
        i = 0
        start_i = 0
        while i - start_i < 4:
            try:
                code = self.text_codes[i].code
            except IndexError:
                return False
            if self.lang:
                if not (
                        code in range(ord('0'), ord('9')+1)
                        or code in range(ord('A'), ord('F')+1)
                        or code in range(ord('a'), ord('f')+1)
                ):
                    return False
            else:
                # In Japanese, some id messages use control codes as well for the dev's tests
                if code in CC_PARSE_JP.keys():
                    start_i += 1
                    i += 1
                    continue
                if not (
                        code in range(0x824F, 0x8258+1) # ０ - ９
                        or code in range(0x8260, 0x8265+1) # Ａ - Ｆ
                        or code in range(0x8281, 0x8286+1) # ａ - ｆ
                ):
                    return False
            i += 1
        return True

    def parse_text(self) -> None:
        self.text_codes = parse_control_codes(self.raw_text, self.lang)

        index = 0
        for text_code in self.text_codes:
            index += text_code.size()
            if text_code.code == [0x8170, 0x02][self.lang]:  # message end code
                break
            if text_code.code == [0x81CB, 0x07][self.lang]:  # goto
                self.has_goto = True
                self.ending = text_code
            if text_code.code == [0x86C8, 0x0A][self.lang]:  # keep-open
                self.has_keep_open = True
                self.ending = text_code
            if text_code.code == [0x819F, 0x0B][self.lang]:  # event
                self.has_event = True
                self.ending = text_code
            if text_code.code == [0x819E, 0x0E][self.lang]:  # fade out
                self.has_fade = True
                self.ending = text_code
            if text_code.code == [0x81F0, 0x10][self.lang]:  # ocarina
                self.has_ocarina = True
                self.ending = text_code
            if text_code.code == [0x81BC, 0x1B][self.lang]:  # two choice
                self.has_two_choice = True
            if text_code.code == [0x81B8, 0x1C][self.lang]:  # three choice
                self.has_three_choice = True
        self.text = display_code_list(self.text_codes)
        self.unpadded_length = index

    def is_basic(self) -> bool:
        return not (self.has_goto or self.has_keep_open or self.has_event or self.has_fade or self.has_ocarina or self.has_two_choice or self.has_three_choice)

    # computes the size of a message, including padding
    def size(self) -> int:
        size = 0

        for code in self.text_codes:
            size += code.size()

        size = (size + 3) & -4 # align to nearest 4 bytes

        return size

    # applies whatever transformations we want to the dialogs
    def transform(self, replace_ending: bool = False, ending: Optional[TextCode] = None,
                always_allow_skip: bool = True, speed_up_text: bool = True) -> None:
        ending_codes = [[0x8170, 0x81CB, 0x86C8, 0x819F, 0x819E, 0x81F0],
                        [0x02,   0x07,   0x0A,   0x0B,   0x0E,   0x10]][self.lang]
        box_breaks   = [[0x81A5, 0x81A3], [0x04, 0x0C]][self.lang]
        slows_text   = [[0x8189, 0x818A, 0x86C9], [0x08, 0x09, 0x14]][self.lang]
        slow_icons   = [0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x04, 0x02]

        end_code          = [0x8170, 0x02][self.lang]
        jp_goto           = 0x81CB  # JP only
        color_code        = [0x0B, 0x05][self.lang]
        icon_code         = [0x819A, 0x13][self.lang]
        space_or_pad_code = [0x8140, 0x20][self.lang]  # fullwidth space / ASCII space

        def tc(code: int, data: int = 0) -> TextCode:
            return TextCode(code, data, self.lang)

        instant_allow_code   = [0x8189, 0x08][self.lang]  # ♂ allow instant text
        instant_disallow_code = [0x818A, 0x09][self.lang]  # ♀ disallow instant text
        instant_text_code   = tc(instant_allow_code, 0)
        uninstant_text_code = tc(instant_disallow_code, 0)

        default_color = [0x0C00, 0x40][self.lang]

        ignores: list[int] = []
        if always_allow_skip:
            ignores += [[0x8199, 0x1A][self.lang]]
        # ignore anything that slows down text
        if speed_up_text:
            ignores += slows_text  # includes existing speed codes too

        # If we are replacing the ending, strip the trailing ending sequence from the *source* message first.
        # This prevents cases like "... <disallow><goto> <disallow><keep open>" where the original trailing goto
        # survives and the new ending is merely appended.
        src_codes = self.text_codes
        if replace_ending and src_codes:
            ending_set = set(ending_codes) - {end_code}
            peel_set = {space_or_pad_code, color_code, instant_allow_code, instant_disallow_code} | ending_set

            tmp = list(src_codes)

            # drop trailing end marker(s) if present
            while tmp and tmp[-1].code == end_code:
                tmp.pop()

            # drop trailing "formatting/instant/ending" cluster
            while tmp and tmp[-1].code in peel_set:
                tmp.pop()

            src_codes = tmp

        out: list[TextCode] = []

        # instant state tracking (so we can avoid useless duplicates except when we *must* re-assert)
        last_instant: Optional[bool] = None  # True=allow, False=disallow

        def emit_instant(allow: bool, force: bool = False) -> None:
            nonlocal last_instant
            if (not force) and (last_instant is not None) and (last_instant == allow):
                return
            out.append(tc(instant_allow_code if allow else instant_disallow_code, 0))
            last_instant = allow

        # current color tracking
        current_color = default_color

        # start: allow instant
        if speed_up_text:
            emit_instant(True, force=True)

        # --- main rewrite ---
        for code in src_codes:
            if code.code == end_code:
                break
            if code.code in ignores:
                continue

            # colors: only drop exact duplicates (do NOT drop tail #00 by "empty all()" logic)
            if code.code == color_code:
                if code.data == current_color:
                    continue
                out.append(code)
                current_color = code.data
                continue

            # JP goto: must be preceded by disallow when speed-up is enabled
            if speed_up_text and (not self.lang) and code.code == jp_goto:
                emit_instant(False)
                out.append(code)
                continue

            # box breaks: remove delay, then re-assert instant (force)
            if speed_up_text and code.code in box_breaks:
                # special cases for text that needs to remain on a timer
                if (self.id == 0x605A or  # twinrova transformation
                    self.id == 0x706C or  # rauru ending text
                    self.id == 0x70DD or  # ganondorf ending text
                    self.id in (0x706F, 0x7091, 0x7092, 0x7093, 0x7094, 0x7095, 0x7070)  # zelda ending text
                ):
                    out.append(code)
                    emit_instant(True, force=True)
                else:
                    out.append(tc([0x81A5, 0x04][self.lang], 0))  # un-delayed break
                    emit_instant(True, force=True)
                continue

            # slow icons: must re-assert instant *after* the icon (force)
            if speed_up_text and code.code == icon_code and code.data in slow_icons:
                out.append(code)
                emit_instant(True, force=True)
                continue

            out.append(code)

        # write/replace ending
        if replace_ending:
            # write ending if provided
            if ending is not None:
                ending = tc(ending.code, ending.data)  # clone

                # Rule: if speed-up is enabled, disallow must be placed immediately before ending
                if speed_up_text:
                    emit_instant(False)

                out.append(ending)

                # Rule: final color must be #00 if non-default is active
                if current_color != default_color:
                    out.append(tc(color_code, default_color))
                    current_color = default_color

            else:
                # no special ending: still enforce "disallow near the end" when speeding up
                if speed_up_text:
                    emit_instant(False)

                # enforce final color reset if needed
                if current_color != default_color:
                    out.append(tc(color_code, default_color))
                    current_color = default_color

            # always terminate
            out.append(tc(end_code, 0))

        self.text_codes = out

    # writes a Message back into the rom, using the given index and offset to update the table
    # returns the offset of the next message
    def write(self, rom: Rom, index: int, text_start: int, offset: int, bank: int) -> int:
        # construct the table entry
        id_bytes = int_to_bytes(self.id, 2)
        offset_bytes = int_to_bytes(offset, 3)
        entry = id_bytes + bytes([self.opts, 0x00, bank]) + offset_bytes
        # write it back
        entry_offset = EXTENDED_TABLE_START + 8 * index
        rom.write_bytes(entry_offset, entry)

        for code in self.text_codes:
            offset = code.write(rom, text_start, offset)

        while offset % 4 > 0:
            offset = TextCode(0x00, 0, self.lang).write(rom, text_start, offset) # pad to 4 byte align

        return offset

    # read a single message from rom
    @classmethod
    def from_rom(cls, rom: Rom, index: int, eng: bool = True) -> Message:
        if eng:
            table_start = ENG_TABLE_START
            text_start = ENG_TEXT_START
            lang = "en"
        else:
            table_start = JPN_TABLE_START
            text_start = JPN_TEXT_START
            lang = "jp"
        entry_offset = table_start + 8 * index
        entry = rom.read_bytes(entry_offset, 8)
        next = rom.read_bytes(entry_offset + 8, 8)

        id = bytes_to_int(entry[0:2])
        opts = entry[2]
        offset = bytes_to_int(entry[5:8])
        length = bytes_to_int(next[5:8]) - offset

        raw_text = rom.read_bytes(text_start + offset, length)

        return cls(raw_text, index, id, opts, offset, length, lang)

    @classmethod
    def from_string(cls, text: str, lang: str, id: int = 0, opts: int = 0x00) -> Message:
        bytes = text
        if not text.endswith('｝' if lang == 'jp' else '\x02'):
            bytes += '｝' if lang == 'jp' else '\x02'
        length = len(bytes) + 1
        if lang != "en":
            length *= 2
        return cls(bytes, 0, id, opts, 0, length, lang)

    @classmethod
    def from_bytearray(cls, text: bytearray, lang: str, id: int = 0, opts: int = 0x00) -> Message:
        lang_int = 0 if lang == "jp" else 1
        bytes = bytearray_to_list(text, lang_int)
        if bytes[-1] != [0x8170, 0x02][lang_int]:
            bytes += [0x8170, 0x02][lang_int]
        length = len(bytes) + 1
        if lang != "en":
            length *= 2
        return cls(bytes, 0, id, opts, 0, length, lang)

    __str__ = __repr__ = display


# wrapper for updating the text of a message, given its message id
# if the id does not exist in the list, then it will add it
# Checks if the message being updated is a newly added message in order to prevent duplicates.
# Use allow_duplicates=True if the same message is purposely updated multiple times
def update_message_by_id(messages: list[Message], id: int, text: bytearray | str, lang: Language, opts: Optional[int] = None, allow_duplicates: bool = False, force_left: bool = False):
    # Check is we have previously added/modified this message.
    if id in new_messages and not allow_duplicates:
        raise Exception(f'Attempting to add duplicate message {hex(id)}')

    new_messages.append(id)
    # get the message index
    index = next( (m.index for m in messages if m.id == id), -1)

    # align the text when the proposed align text by the language isn't "Left"
    if lang.lang_property["align_text"] != "Left" and not force_left:
        text = line_wrap(text, lang.base, align=lang.lang_property["align_text"])

    # update if it was found
    if index >= 0:
        update_message_by_index(messages, index, text, lang, opts)
    else:
        add_message(messages, text, lang, id, opts)


# Gets the message by its ID. Returns None if the index does not exist
def get_message_by_id(messages: list[Message], id: int) -> Optional[Message]:
    # get the message index
    index = next( (m.index for m in messages if m.id == id), -1)
    if index >= 0:
        return messages[index]
    else:
        return None


# wrapper for updating the text of a message, given its index in the list
def update_message_by_index(messages: list[Message], index: int, text: bytearray | str, lang: Language, opts: Optional[int] = None) -> None:
    if opts is None:
        opts = messages[index].opts

    if isinstance(text, bytearray):
        messages[index] = Message.from_bytearray(text, lang.base, messages[index].id, opts)
    else:
        messages[index] = Message.from_string(text, lang.base, messages[index].id, opts)
    messages[index].index = index


# wrapper for adding a string message to a list of messages
def add_message(messages: list[Message], text: bytearray | str, lang: Language, id: int = 0, opts: int = 0x00) -> None:
    if isinstance(text, bytearray):
        messages.append(Message.from_bytearray(text, lang.base, id, opts))
    else:
        messages.append(Message.from_string(text, lang.base, id, opts))
    messages[-1].index = len(messages) - 1


# holds a row in the shop item table (which contains pointers to the description and purchase messages)
class ShopItem:
    # read a single message
    def __init__(self, rom: Rom, shop_table_address: int, index: int) -> None:
        entry_offset = shop_table_address + 0x20 * index
        entry = rom.read_bytes(entry_offset, 0x20)

        self.index: int = index
        self.object: int = bytes_to_int(entry[0x00:0x02])
        self.model: int = bytes_to_int(entry[0x02:0x04])
        self.func1: int = bytes_to_int(entry[0x04:0x08])
        self.price: int = bytes_to_int(entry[0x08:0x0A])
        self.pieces: int = bytes_to_int(entry[0x0A:0x0C])
        self.description_message: int = bytes_to_int(entry[0x0C:0x0E])
        self.purchase_message: int = bytes_to_int(entry[0x0E:0x10])
        # 0x10-0x11 is always 0000 padded apparently
        self.get_item_id: int = bytes_to_int(entry[0x12:0x14])
        self.func2: int = bytes_to_int(entry[0x14:0x18])
        self.func3: int = bytes_to_int(entry[0x18:0x1C])
        self.func4: int = bytes_to_int(entry[0x1C:0x20])

    def display(self) -> str:
        meta_data = [
            "#" + str(self.index),
            "Item: 0x" + "{:04x}".format(self.get_item_id),
            "Price: " + str(self.price),
            "Amount: " + str(self.pieces),
            "Object: 0x" + "{:04x}".format(self.object),
            "Model: 0x" + "{:04x}".format(self.model),
            "Description: 0x" + "{:04x}".format(self.description_message),
            "Purchase: 0x" + "{:04x}".format(self.purchase_message),
        ]
        func_data = [
            "func1: 0x" + "{:08x}".format(self.func1),
            "func2: 0x" + "{:08x}".format(self.func2),
            "func3: 0x" + "{:08x}".format(self.func3),
            "func4: 0x" + "{:08x}".format(self.func4),
        ]
        return ', '.join(meta_data) + '\n' + ', '.join(func_data)

    # write the shop item back
    def write(self, rom: Rom, shop_table_address: int, index: int) -> None:
        entry_offset = shop_table_address + 0x20 * index

        data = []
        data += int_to_bytes(self.object, 2)
        data += int_to_bytes(self.model, 2)
        data += int_to_bytes(self.func1, 4)
        data += int_to_bytes(self.price, 2, signed=True)
        data += int_to_bytes(self.pieces, 2)
        data += int_to_bytes(self.description_message, 2)
        data += int_to_bytes(self.purchase_message, 2)
        data += [0x00, 0x00]
        data += int_to_bytes(self.get_item_id, 2)
        data += int_to_bytes(self.func2, 4)
        data += int_to_bytes(self.func3, 4)
        data += int_to_bytes(self.func4, 4)

        rom.write_bytes(entry_offset, data)

    __str__ = __repr__ = display


# reads each of the shop items
def read_shop_items(rom: Rom, shop_table_address: int) -> list[ShopItem]:
    shop_items = []

    for index in range(0, 100):
        shop_items.append(ShopItem(rom, shop_table_address, index))

    return shop_items


# writes each of the shop item back into rom
def write_shop_items(rom: Rom, shop_table_address: int, shop_items: Iterable[ShopItem]) -> None:
    for s in shop_items:
        s.write(rom, shop_table_address, s.index)


# these are unused shop items, and contain text ids that are used elsewhere, and should not be moved
SHOP_ITEM_EXCEPTIONS: list[int] = [0x0A, 0x0B, 0x11, 0x12, 0x13, 0x14, 0x29]


# returns a set of all message ids used for shop items
def get_shop_message_id_set(shop_items: Iterable[ShopItem]) -> set[int]:
    ids = set()
    for shop in shop_items:
        if shop.index not in SHOP_ITEM_EXCEPTIONS:
            ids.add(shop.description_message)
            ids.add(shop.purchase_message)
    return ids


# remove all messages that easy to tell are unused to create space in the message index table
def remove_unused_messages(messages: list[Message]) -> None:
    messages[:] = [m for m in messages if not m.is_id_message()]
    for index, m in enumerate(messages):
        m.index = index


# takes all messages used for shop items, and moves messages from the 00xx range into the unused 80xx range
def move_shop_item_messages(messages: list[Message], shop_items: Iterable[ShopItem]) -> None:
    # checks if a message id is in the item message range
    def is_in_item_range(id: int) -> bool:
        bytes = int_to_bytes(id, 2)
        return bytes[0] == 0x00

    # get the ids we want to move
    ids = set( id for id in get_shop_message_id_set(shop_items) if is_in_item_range(id) )
    # update them in the message list
    for id in ids:
        # should be a singleton list, but in case something funky is going on, handle it as a list regardless
        relevant_messages = [message for message in messages if message.id == id]
        if len(relevant_messages) >= 2:
            raise(TypeError("duplicate id in move_shop_item_messages"))

        for message in relevant_messages:
            if message.id in new_messages: # Check if this was a message we've modified and update its ID in that table.
                index = new_messages.index(message.id)
                new_messages[index] |= 0x8000
            message.id |= 0x8000
    # update them in the shop item list
    for shop in shop_items:
        if is_in_item_range(shop.description_message):
            shop.description_message |= 0x8000
        if is_in_item_range(shop.purchase_message):
            shop.purchase_message |= 0x8000


def make_player_message(text: str, lang: Language) -> str:
    pronoun_mapping = lang.pronoun_mapping
    verb_mapping = lang.verb_mapping
    new_text = text
    # Replace the first instance of a 'You' with the player name
    if lang.search is not None:
        if lang.base != "jp":
            lower_text = text.lower()
            you_index = lower_text.find(lang.search)
        if you_index != -1:
            for find_text, replace_text in pronoun_mapping.items():
                # if the index do not match, then it is not the first 'You'
                if text.find(find_text) == you_index:
                    new_text = new_text.replace(find_text, replace_text, 1)
                    break

    # because names are longer, we shorten the verbs to they fit in the textboxes better
    for find_text, replace_text in verb_mapping.items():
        new_text = new_text.replace(find_text, replace_text)
    wrapped_text = line_wrap(new_text, lang.base, False, False, False)
    if wrapped_text != new_text:
        new_text = line_wrap(new_text, lang.base, True, False, False)

    return new_text


# reduce item message sizes and add new item messages
# make sure to call this AFTER move_shop_item_messages()
def update_item_messages(messages: list[Message], world: World) -> None:
    lang = world.language
    if lang.PLAIN_TEXTS != []:
        for plain_text in lang.PLAIN_TEXTS:
            id, text, opt = plain_text["id"], plain_text["text"], plain_text["box_type"]
            update_message_by_id(messages, id, text, lang, opt, force_left=True)

    new_item_messages = lang.ITEM_MESSAGES + lang.IMPORTANT_ITEM_MESSAGES
    for item_message in new_item_messages:
        id, text = item_message["id"], item_message["text"]
        if world.settings.world_count > 1:
            update_message_by_id(messages, id, make_player_message(text, lang), lang, 0x23)
        else:
            update_message_by_id(messages, id, text, lang, 0x23)

    for misc_text in lang.MISC_MESSAGES:
        id, text, opt = misc_text["id"], misc_text["text"], misc_text["box_type"]
        update_message_by_id(messages, id, text, lang, opt)

# run all keysanity related patching to add messages for dungeon specific items
def add_item_messages(messages: list[Message], shop_items: Iterable[ShopItem], world: World) -> None:
    move_shop_item_messages(messages, shop_items)
    update_item_messages(messages, world)


# reads each of the game's messages into a list of Message objects
def read_messages(rom: Rom, lang: Language) -> list[Message]:
    table_offset = JPN_TABLE_START if lang.base == "jp" else ENG_TABLE_START
    index = 0
    messages = []
    while True:
        entry = rom.read_bytes(table_offset, 8)
        id = bytes_to_int(entry[0:2])

        if id == 0xFFFD:
            table_offset += 8
            continue # this is only here to give an ending offset
        if id == 0xFFFF:
            break # this marks the end of the table
        if lang.base == "jp" and id == 0xFFFC: break

        messages.append(Message.from_rom(rom, index, eng = lang.base != "jp"))

        index += 1
        table_offset += 8

    # Also grab 0xFFFC entry from JP table.
    messages.append(read_fffc_message(rom))
    return messages


# The JP text table is the only source for ID 0xFFFC, which is used by the
# title and file select screens. Preserve this table entry and text data when
# overwriting the JP data. The regular read_messages function only reads English
# data.
def read_fffc_message(rom: Rom) -> Message:
    table_offset = JPN_TABLE_START
    index = 0
    while True:
        entry = rom.read_bytes(table_offset, 8)
        id = bytes_to_int(entry[0:2])

        if id == 0xFFFC:
            message = Message.from_rom(rom, index, eng=False)
            break

        index += 1
        table_offset += 8

    return message


# write the messages back
def repack_messages(rom: Rom, messages: list[Message], lang: str, permutation: Optional[list[int]] = None,
                    always_allow_skip: bool = True, speed_up_text: bool = True) -> None:
    rom.update_dmadata_record_by_key(ENG_TEXT_START, ENG_TEXT_START, ENG_TEXT_START + ENG_TEXT_SIZE_LIMIT)
    rom.update_dmadata_record_by_key(JPN_TEXT_START, JPN_TEXT_START, JPN_TEXT_START + JPN_TEXT_SIZE_LIMIT)

    if permutation is None:
        permutation = range(len(messages))

    # repack messages
    offset = 0
    text_start = JPN_TEXT_START
    text_size_limit = EXTENDED_TEXT_SIZE_LIMIT
    text_bank = 0x08 # start with the Japanese text bank
    jp_bytes = 0
    # An extra dummy message is inserted after exhausting the JP text file.
    # Written message IDs are independent of the python list index, but the
    # index has to be maintained for old/new lookups. This wouldn't be an
    # issue if text shuffle didn't exist.
    jp_index_offset = 0

    for old_index, new_index in enumerate(permutation):
        old_message = messages[old_index]
        new_message = messages[new_index]
        remember_id = new_message.id
        new_message.id = old_message.id

        # modify message, making it represent how we want it to be written
        if new_message.id != 0xFFFC:
            new_message.transform(True, old_message.ending, always_allow_skip, speed_up_text)

        # check if there is space to write the message
        message_size = new_message.size()
        if message_size + offset > JPN_TEXT_SIZE_LIMIT and text_start == JPN_TEXT_START:
            # Add a dummy entry to the table for the last entry in the
            # JP file. This is used by the game to calculate message
            # length. Since the next entry in the English table has an
            # offset of zero, which would lead to a negative length.
            # 0xFFFD is used as the text ID for this in vanilla.
            # Text IDs need to be in order across the table for the
            # split to work.
            entry = bytes([0xFF, 0xFD, 0x00, 0x00, text_bank]) + int_to_bytes(offset, 3)
            entry_offset = EXTENDED_TABLE_START + 8 * old_index
            rom.write_bytes(entry_offset, entry)
            # if there is no room then switch to the English text bank
            text_bank = 0x07
            text_start = ENG_TEXT_START
            jp_bytes = offset
            jp_index_offset = 1
            offset = 0

        # Special handling for text ID 0xFFFC, which has hard-coded offsets to
        # the JP file in function Font_LoadOrderedFont in z_kanfont.c
        if new_message.id == 0xFFFC:
            # hard-coded offset including segment
            rom.write_int16(0xAD1CE2, (text_bank << 8) + ((offset & 0xFFFF0000) >> 16) + (1 if offset & 0xFFFF > 0x8000 else 0))
            rom.write_int16(0xAD1CE6, offset & 0XFFFF)
            # hard-coded message length, represented by offset of end of message
            rom.write_int16(0xAD1D16, (text_bank << 8) + (((offset + new_message.size()) & 0xFFFF0000) >> 16) + (1 if (offset + new_message.size()) & 0xFFFF > 0x8000 else 0))
            rom.write_int16(0xAD1D1E, (offset + new_message.size()) & 0XFFFF)
            # hard-coded segment, default JP file (0x08)
            rom.write_int16(0xAD1D12, (text_bank << 8))
            # hard-coded text file start address in rom, default JP
            rom.write_int16(0xAD1D22, ((text_start & 0xFFFF0000) >> 16) + (1 if text_start & 0xFFFF > 0x8000 else 0))
            rom.write_int16(0xAD1D2E, text_start & 0XFFFF)

        # actually write the message
        offset = new_message.write(rom, old_index + jp_index_offset, text_start, offset, text_bank)

        new_message.id = remember_id

    # raise an exception if too much is written
    # we raise it at the end so that we know how much overflow there is
    if jp_bytes + offset > text_size_limit:
        raise(TypeError("Message Text table is too large: 0x" + "{:x}".format(jp_bytes + offset) + " written / 0x" + "{:x}".format(EXTENDED_TEXT_SIZE_LIMIT) + " allowed."))

    # end the table, accounting for additional entry for file split
    table_index = len(messages) + (1 if text_bank == 0x07 else 0)
    entry = bytes([0xFF, 0xFD, 0x00, 0x00, text_bank]) + int_to_bytes(offset, 3)
    entry_offset = EXTENDED_TABLE_START + 8 * table_index
    rom.write_bytes(entry_offset, entry)
    table_index += 1
    entry_offset = EXTENDED_TABLE_START + 8 * table_index
    if 8 * (table_index + 1) > EXTENDED_TABLE_SIZE:
        raise(TypeError("Message ID table is too large: 0x" + "{:x}".format(8 * (table_index + 1)) + " written / 0x" + "{:x}".format(EXTENDED_TABLE_SIZE) + " allowed."))
    rom.write_bytes(entry_offset, [0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

# shuffles the messages in the game, making sure to keep various message types in their own group
def shuffle_messages(messages: list[Message], except_hints: bool = True) -> list[int]:
    if not hasattr(shuffle_messages, "shop_item_messages"):
        shuffle_messages.shop_item_messages = []
    if not hasattr(shuffle_messages, "scrubs_message_ids"):
        shuffle_messages.scrubs_message_ids = []

    hint_ids = (
        GOSSIP_STONE_MESSAGES + TEMPLE_HINTS_MESSAGES +
        [data['id'] for data in misc_item_hint_table.values()] +
        [data['id'] for data in misc_location_hint_table.values()] +
        [message_id for message_id in IMPORTANT_ITEM_MESSAGES_IDS] + shuffle_messages.shop_item_messages +
        shuffle_messages.scrubs_message_ids +
        [0x5036, 0x70F5] # Chicken count and poe count respectively
    )

    permutation = [i for i, _ in enumerate(messages)]

    def is_exempt(m: Message) -> bool:
        hint_ids = (
            GOSSIP_STONE_MESSAGES + TEMPLE_HINTS_MESSAGES +
            [data['id'] for data in misc_item_hint_table.values()] +
            [data['id'] for data in misc_location_hint_table.values()] +
            [message_id for message_id in IMPORTANT_ITEM_MESSAGES_IDS] +
            shuffle_messages.shop_item_messages +
            shuffle_messages.scrubs_message_ids +
            [0x5036, 0x70F5] # Chicken count and poe count respectively
        )
        shuffle_exempt = [
            0x045C,         # Adult shooting gallery helping message when the player wins without having a bow
            0x208D,         # "One more lap!" for Cow in House race.
            0xFFFC,         # Character data from JP table used on title and file select screens
        ]
        is_hint = (except_hints and m.id in hint_ids)
        is_error_message = (m.id == ERROR_MESSAGE)
        is_shuffle_exempt = (m.id in shuffle_exempt)
        return is_hint or is_error_message or m.is_id_message() or is_shuffle_exempt

    have_goto         = list(filter(lambda m: not is_exempt(m) and m.has_goto,         messages))
    have_keep_open    = list(filter(lambda m: not is_exempt(m) and m.has_keep_open,    messages))
    have_event        = list(filter(lambda m: not is_exempt(m) and m.has_event,        messages))
    have_fade         = list(filter(lambda m: not is_exempt(m) and m.has_fade,         messages))
    have_ocarina      = list(filter(lambda m: not is_exempt(m) and m.has_ocarina,      messages))
    have_two_choice   = list(filter(lambda m: not is_exempt(m) and m.has_two_choice,   messages))
    have_three_choice = list(filter(lambda m: not is_exempt(m) and m.has_three_choice, messages))
    basic_messages    = list(filter(lambda m: not is_exempt(m) and m.is_basic(),       messages))

    def shuffle_group(group: list[Message]) -> None:
        group_permutation = [i for i, _ in enumerate(group)]
        random.shuffle(group_permutation)

        for index_from, index_to in enumerate(group_permutation):
            permutation[group[index_to].index] = group[index_from].index

    # need to use 'list' to force 'map' to actually run through
    list( map( shuffle_group, [
        have_goto + have_keep_open + have_event + have_fade + basic_messages,
        have_ocarina,
        have_two_choice,
        have_three_choice,
    ]))

    return permutation


# Update warp song text boxes for ER
def update_warp_song_text(messages: list[Message], world: World) -> None:
    from Hints import HintArea
    lang = world.language
    lang_num = 1 if lang.base == "jp" else 0
    msg_list = {
        0x088D: 'Minuet of Forest Warp -> Sacred Forest Meadow',
        0x088E: 'Bolero of Fire Warp -> DMC Central Local',
        0x088F: 'Serenade of Water Warp -> Lake Hylia',
        0x0890: 'Requiem of Spirit Warp -> Desert Colossus',
        0x0891: 'Nocturne of Shadow Warp -> Graveyard Warp Pad Region',
        0x0892: 'Prelude of Light Warp -> Temple of Time',
    }
    owl_messages = {
        0x3063: 'DMT Owl Flight -> Kak Impas Rooftop',
        0x4004: 'LH Owl Flight -> Hyrule Field',
    }

    for id, entr in msg_list.items():
        if 'warp_songs_and_owls' in world.settings.misc_hints or not world.settings.warp_songs:
            destination = world.get_entrance(entr).connected_region
            destination_name = HintArea.at(destination)
            color = COLOR_MAP[destination_name.color][lang_num]
            if destination_name.preposition(lang, True) is not None:
                destination_name = lang.format_from_id("PATCH_TEXTS.warp_to", {"destination_name": destination_name.display_name(lang)})
        else:
            destination_name = lang.PATCH_TEXTS["warp_mysterious"]
            color = COLOR_MAP['White'][lang_num]

        new_msg = lang.format_from_id("PATCH_TEXTS.warp_msg", {"destination_name": destination_name, "color": color})
        update_message_by_id(messages, id, new_msg, world.language)

    if world.settings.owl_drops:
        for id, entr in owl_messages.items():
            if 'warp_songs_and_owls' in world.settings.misc_hints:
                destination = world.get_entrance(entr).connected_region
                destination_name = HintArea.at(destination)
                color = COLOR_MAP[destination_name.color][lang_num]
                if destination_name.preposition(lang, True) is not None:
                    destination_name = lang.format_from_id("PATCH_TEXTS.warp_to", {"destination_name": destination_name.display_name(lang)})
            else:
                destination_name = lang.PATCH_TEXTS["warp_mysterious"]
                color = COLOR_MAP['White'][lang_num]

            new_msg = lang.format_from_id("PATCH_TEXTS.warp_owl", {"destination_name": destination_name, "color": color})
            update_message_by_id(messages, id, new_msg, world.language)

def update_map_compass_messages(messages: list[Message], world: World):
    from Hints import GossipText, HintArea
    if world.settings.enhance_map_compass and world.settings.shuffle_mapcompass != 'remove' and world.settings.world_count == 1:
        dungeon_id_list = {
                #                      compass map
                'Deku Tree':          (0x62,   0x88, "Deku Tree Before Boss -> Queen Gohma Boss Room"),
                'Dodongos Cavern':    (0x63,   0x89, "Dodongos Cavern Before Boss -> King Dodongo Boss Room"),
                'Jabu Jabus Belly':   (0x64,   0x8a, "Jabu Jabus Belly Before Boss -> Barinade Boss Room"),
                'Forest Temple':      (0x65,   0x8b, "Forest Temple Before Boss -> Phantom Ganon Boss Room"),
                'Fire Temple':        (0x7c,   0x8c, "Fire Temple Before Boss -> Volvagia Boss Room"),
                'Water Temple':       (0x7d,   0x8e, "Water Temple Before Boss -> Morpha Boss Room"),
                'Spirit Temple':      (0x7e,   0x8f, "Spirit Temple Before Boss -> Twinrova Boss Room"),
                'Shadow Temple':      (0x7f,   0xa3, "Shadow Temple Before Boss -> Bongo Bongo Boss Room"),
                'Bottom of the Well': (0xa2,   0xa5),
                'Ice Cavern':         (0x87,   0x92),
            }
        lang = world.language
        dungeon_list = {dungeon: (value["name"], value["gender"]) for dungeon, value in lang.dungeon_list.items() if value["has_map"]}
        dungeon_textbox_list = {dungeon: (value["name"], value["gender"]) for dungeon, value in lang.dungeon_list.items()}
        dungeon_entrances_list = {
            "Deku Tree": "KF Outside Deku Tree -> Deku Tree Lobby",
            "Dodongos Cavern": "Death Mountain -> Dodongos Cavern Beginning",
            "Jabu Jabus Belly": "Zoras Fountain -> Jabu Jabus Belly Beginning",
            "Forest Temple": "SFM Forest Temple Entrance Ledge -> Forest Temple Lobby",
            "Fire Temple": "DMC Fire Temple Entrance -> Fire Temple Lower",
            "Water Temple": "Lake Hylia -> Water Temple Lobby",
            "Shadow Temple": "Graveyard Warp Pad Region -> Shadow Temple Entryway",
            "Spirit Temple": "Desert Colossus -> Spirit Temple Lobby",
            "Bottom of the Well": "Kakariko Village -> Bottom of the Well",
            "Ice Cavern": "ZF Ice Ledge -> Ice Cavern Beginning",
            "Gerudo Training Ground": "Gerudo Fortress -> Gerudo Training Ground Lobby",
            "Ganons Castle": "Ganons Castle Ledge -> Ganons Castle Lobby",
        }

        dungeon_entrances = {}
        if 'map_dungeon_location' in world.settings.enhance_map_compass and world.settings.shuffle_dungeon_entrances != 'off':
            for original_location, dungeon_entrance in dungeon_entrances_list.items():
                connected_region = world.get_entrance(dungeon_entrance).connected_region
                dungeon_entrances[original_location] = connected_region.name

        boss_textboxes = lang.boss_textboxes

        for dungeon in world.dungeons:
            if dungeon.name in ('Gerudo Training Ground', 'Ganons Castle'):
                pass
            elif dungeon.name in ('Bottom of the Well', 'Ice Cavern'):
                dungeon_name, gender = dungeon_list[dungeon.name]
                compass_id, map_id = dungeon_id_list[dungeon.name]
                if 'map_dungeon_location' in world.settings.enhance_map_compass and world.settings.shuffle_dungeon_entrances != 'off':
                    dungeon_index = [i for i, c in dungeon_entrances.items() if dungeon.name in c]
                    if dungeon.name not in ('Dodongos Cavern', 'Jabu Jabus Belly'):
                        for prefix in lang.hintPrefixes:
                            if dungeon_name.startswith(prefix):
                                dungeon_name = dungeon_name.replace(prefix, '', 1)
                                break
                    dungeon_location = dungeon_textbox_list[dungeon_index[0]]
                    if 'map_mq' in world.settings.enhance_map_compass and (world.settings.mq_dungeons_mode == 'random' or world.settings.mq_dungeons_count != 0 and world.settings.mq_dungeons_count != 12):
                        map_message = lang.format_from_id(
                            "PATCH_TEXTS.map_location_mq",
                            {
                                "dungeon_name": dungeon_name,
                                "dungeon_state": lang.PATCH_TEXTS['masterful'] if world.dungeon_mq[dungeon.name] else lang.PATCH_TEXTS['ordinary'],
                                "gender": gender,
                                "dungeon_location": dungeon_location[0],
                                "location_gender": dungeon_location[1],
                            }
                        )
                    else:
                        map_message = lang.format_from_id(
                            "PATCH_TEXTS.map_location",
                            {
                                "dungeon_name": dungeon_name,
                                "gender": gender,
                                "dungeon_location": dungeon_location[0],
                                "location_gender": dungeon_location[1],
                            }
                        )
                    update_message_by_id(messages, map_id, map_message, lang, allow_duplicates=True, force_left=True)
                else:
                    if 'map_mq' in world.settings.enhance_map_compass:
                        map_message = lang.format_from_id(
                            "PATCH_TEXTS.map",
                            {
                                "dungeon_name": dungeon_name,
                                "dungeon_state": lang.PATCH_TEXTS["masterful"] if world.dungeon_mq[dungeon.name] else lang.PATCH_TEXTS["ordinary"],
                                "gender": gender
                            })

                        if world.settings.mq_dungeons_mode == 'random' or world.settings.mq_dungeons_count != 0 and world.settings.mq_dungeons_count != 12:
                            update_message_by_id(messages, map_id, map_message, lang, allow_duplicates=True, force_left=True)
            else:
                dungeon_name, gender = dungeon_list[dungeon.name]
                compass_id, map_id, boss_entrance = dungeon_id_list[dungeon.name]
                if 'compass_reward' in world.settings.enhance_map_compass:
                    if world.settings.shuffle_dungeon_rewards != 'dungeon':
                        if world.entrance_rando_reward_hints:
                            vanilla_reward = world.get_location(dungeon.vanilla_boss_name).vanilla_item
                            vanilla_reward_location = world.hinted_dungeon_reward_locations[vanilla_reward]
                            if vanilla_reward_location is None:
                                area = HintArea.ROOT
                            else:
                                area = HintArea.at(vanilla_reward_location)
                            area = GossipText(area.text(lang, world.settings.clearer_hints, preposition=True, use_2nd_person=True), lang, [area.color], prefix='', capitalize=False)
                            if 'compass_boss_location' in world.settings.enhance_map_compass and world.settings.shuffle_bosses != 'off':
                                boss_room = world.get_entrance(boss_entrance).connected_region.name
                                compass_message = lang.format_from_id(
                                    "PATCH_TEXTS.compass_boss_area",
                                    {
                                        "dungeon_name": dungeon_name,
                                        "area": area,
                                        "boss_name": boss_textboxes[boss_room],
                                        "vanilla_reward": world.language.hintTable[vanilla_reward]["clear_hint"],
                                        "gender": gender
                                    }
                                )
                            else:
                                compass_message = lang.format_from_id(
                                    "PATCH_TEXTS.compass_area",
                                    {
                                        "dungeon_name": dungeon_name,
                                        "area": area,
                                        "vanilla_reward": world.language.hintTable[vanilla_reward]["clear_hint"],
                                        "gender": gender
                                    }
                                )
                        else:
                            boss_location = next(filter(lambda loc: loc.type == 'Boss', world.get_entrance(f'{dungeon} Before Boss -> {dungeon.vanilla_boss_name} Boss Room').connected_region.locations))
                            dungeon_reward = boss_location.item.name
                            if 'compass_boss_location' in world.settings.enhance_map_compass and world.settings.shuffle_bosses != 'off':
                                boss_room = world.get_entrance(boss_entrance).connected_region.name
                                compass_message = lang.format_from_id(
                                    "PATCH_TEXTS.compass_boss_reward",
                                    {
                                        "dungeon_name": dungeon_name,
                                        "color": COLOR_MAP[REWARD_COLORS[dungeon_reward]][1 if lang.base == "jp" else 0],
                                        "boss_name": boss_textboxes[boss_room],
                                        "dungeon_reward": world.language.hintTable[dungeon_reward]["clear_hint"],
                                        "gender": gender
                                    }
                                )
                            else:
                                compass_message = lang.format_from_id(
                                    "PATCH_TEXTS.compass",
                                    {
                                        "dungeon_name": dungeon_name,
                                        "color": COLOR_MAP[REWARD_COLORS[dungeon_reward]][1 if lang.base == "jp" else 0],
                                        "dungeon_reward": world.language.hintTable[dungeon_reward]["clear_hint"],
                                        "gender": gender
                                    }
                                )
                        update_message_by_id(messages, compass_id, compass_message, lang, allow_duplicates=True, force_left=True)
                    else:
                        if 'compass_boss_location' in world.settings.enhance_map_compass and world.settings.shuffle_bosses != 'off':
                            boss_room = world.get_entrance(boss_entrance).connected_region.name
                            compass_message = lang.format_from_id(
                                "PATCH_TEXTS.compass_boss",
                                {
                                    "dungeon_name": dungeon_name,
                                    "boss_name": boss_textboxes[boss_room],
                                    "gender": gender
                                }
                            )
                            update_message_by_id(messages, compass_id, compass_message, lang, allow_duplicates=True, force_left=True)
                else:
                    if 'compass_boss_location' in world.settings.enhance_map_compass and world.settings.shuffle_bosses != 'off':
                        boss_room = world.get_entrance(boss_entrance).connected_region.name
                        compass_message = lang.format_from_id(
                            "PATCH_TEXTS.compass_boss",
                            {
                                "dungeon_name": dungeon_name,
                                "boss_name": boss_textboxes[boss_room],
                                "gender": gender
                            }
                        )
                        update_message_by_id(messages, compass_id, compass_message, lang, allow_duplicates=True, force_left=True)
                if 'map_dungeon_location' in world.settings.enhance_map_compass and world.settings.shuffle_dungeon_entrances != 'off':
                    dungeon_index = [i for i, c in dungeon_entrances.items() if dungeon.name in c]
                    for prefix in lang.hintPrefixes:
                        if dungeon_name.startswith(prefix):
                            dungeon_name = dungeon_name.replace(prefix, '', 1)
                            break
                    dungeon_location = dungeon_textbox_list[dungeon_index[0]]
                    if 'map_mq' in world.settings.enhance_map_compass and (world.settings.mq_dungeons_mode == 'random' or world.settings.mq_dungeons_count != 0 and world.settings.mq_dungeons_count != 12):
                        map_message = lang.format_from_id(
                            "PATCH_TEXTS.map_location_mq",
                            {
                                "dungeon_name": dungeon_name,
                                "dungeon_state": lang.PATCH_TEXTS['masterful'] if world.dungeon_mq[dungeon.name] else lang.PATCH_TEXTS['ordinary'],
                                "gender": gender,
                                "dungeon_location": dungeon_location[0],
                                "location_gender": dungeon_location[1],
                            }
                        )
                    else:
                        map_message = lang.format_from_id(
                            "PATCH_TEXTS.map_location",
                            {
                                "dungeon_name": dungeon_name,
                                "gender": gender,
                                "dungeon_location": dungeon_location[0],
                                "location_gender": dungeon_location[1],
                            }
                        )
                    update_message_by_id(messages, map_id, map_message, lang, allow_duplicates=True, force_left=True)
                else:
                    if 'map_mq' in world.settings.enhance_map_compass and (world.settings.mq_dungeons_mode == 'random' or world.settings.mq_dungeons_count != 0 and world.settings.mq_dungeons_count != 12):
                        map_message = lang.format_from_id(
                            "PATCH_TEXTS.map",
                            {
                                "dungeon_name": dungeon_name,
                                "dungeon_state": lang.PATCH_TEXTS["masterful"] if world.dungeon_mq[dungeon.name] else lang.PATCH_TEXTS["ordinary"],
                                "gender": gender
                            })
                        update_message_by_id(messages, map_id, map_message, lang, allow_duplicates=True, force_left=True)
