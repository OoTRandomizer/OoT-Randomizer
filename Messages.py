# text details: https://wiki.cloudmodding.com/oot/Text_Format

import logging
import random
import os
from TextBox import line_wrap, linewrapJP
from Utils import local_path
TEXT_START = 0x92D000
TEXT_START_JP = 0x8EB000
ENG_TEXT_SIZE_LIMIT = 0x39000
JPN_TEXT_SIZE_LIMIT = 0x3A150

JPN_TABLE_START = 0xB808AC
ENG_TABLE_START = 0xB849EC
CREDITS_TABLE_START = 0xB88C0C

JPN_TABLE_SIZE = ENG_TABLE_START - JPN_TABLE_START
ENG_TABLE_SIZE = CREDITS_TABLE_START - ENG_TABLE_START

EXTENDED_TABLE_START = JPN_TABLE_START # start writing entries to the jp table instead of english for more space
EXTENDED_TABLE_SIZE = JPN_TABLE_SIZE + ENG_TABLE_SIZE # 0x8360 bytes, 4204 entries

temporal = local_path("temporal.py")
# name of type, followed by number of additional bytes to read, follwed by a function that prints the code
CONTROL_CODES = {
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
}

# Maps unicode characters to corresponding bytes in OOTR's character set.
CHARACTER_MAP = {
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

SPECIAL_CHARACTERS = {
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

REVERSE_MAP = list(chr(x) for x in range(256))

for char, byte in CHARACTER_MAP.items():
    SPECIAL_CHARACTERS.setdefault(byte, char)
    REVERSE_MAP[byte] = char

CONTROL_CHARS_JP = {
   'LINE_BREAK':   ['&', '\x00\x0A', "\x01"],
   'BOX_BREAK':    ['^', '▼', "\x04"],
   'COLOR':        ['#', '\x00\x0B\x0C', "\x05"],
   'ENDMARK':      ['|', '｝', "\x02"],
   'ICON':         ['~', '★\x00', "\x13"],
   'INSTANTSTART': ['<', '♂', "\x08"],
   'INSTANTEND':   ['>', '♀', "\x09"],
   'SOUND':        ['$', '♭', "\x12"],
   'DELAY_BOX':    ['[', '▲\x00', "\x0C"],
   'PREVENT':      [']', '☆', "\x1A"],
   'EVENT':        ['{', '◆', "\x0B"],
   'PRINT_T':      ['@T', '■', "\x1F"],
   'THREE_C':      [':3', '∈', "\x1C"],
   'TWO_C':        [':2', '⊂', "\x1B"],
   'GO_MESSAGE':   ['}', '⇒', "\x07"],
   'FADE_OUT':     ['*F', '◇\x00', "\x0E"],
}

CONTROL_CHARS_JP_1 = {
   'LINE_BREAK':   ['&&', '\x00\x0A', "\x01"],
   'BOX_BREAK':    ['^^', '▼', "\x04"],
   'COLOR':        ['##', '\x00\x0B\x0C', "\x05"],
   'ENDMARK':      ['||', '｝', "\x02"],
   'ICON':         ['~~', '★\x00', "\x13"],
   'INSTANTSTART': ['<<', '♂', "\x08"],
   'INSTANTEND':   ['>>', '♀', "\x09"],
   'SOUND':        ['$$', '♭', "\x12"],
   'DELAY_BOX':    ['[[', '▲\x00', "\x0C"],
   'PREVENT':      [']]', '☆', "\x1A"],
   'EVENT':        ['{{', '◆', "\x0B"],
   'PRINT_T':      ['@T', '■', "\x1F"],
   'THREE_C':      [':3', '∈', "\x1C"],
   'TWO_C':        [':2', '⊂', "\x1B"],
   'GO_MESSAGE':   ['}}', '⇒', "\x07"],
   'FADE_OUT':     ['*F', '◇\x00', "\x0E"],
}

IGNORE_CHARS = {
    'NAME':         [r'\x40\x4e', r'\x87\x4f', '@N', "\x0F"],
    'PRINT_M':      [r'\x40\x4d', r'\x87\x91', '@M', "\x16"],
    'PRINT_R':      [r'\x40\x52', r'\x87\x92', '@R', "\x17"],
    'PRINT_G':      [r'\x40\x47', r'\x86\xa3', '@G', "\x19"],
    'PRINT_P':      [r'\x40\x50', r'\x87\x9b', '@P', "\x18"],
    'PRINT_H':      [r'\x40\x48', r'\x86\x9f\x00', '@H', "\x1E"],
    'PRINT_L':      [r'\x40\x4c', r'\x86\xa4', '@L', "\x1D"],
    'SETBACK':      [r'\x40\x42', r'\x86\xb3\x00', '@B', "\x15"],
    'SETSPEED':     [r'\x2b\x53', r'\x86\xc9\x00', '+S', "\x14"],
    'SHIFT_TEXT':   [r'\x2b\x54', r'\x86\xc7\x00', '+T', "\x06"],
    'OCARINA':      [r'\x3a\x4f', r'\x81\xf0', ':O', "\x10"],
    'KEEP_OPEN':    [r'\x2a\x4f', r'\x86\xc8', '*O', "\x0A"],
}

IGNORE_CHARS_1 = {
    'NAME':         [r'\x40\x4e', r'\x87\x4f', '@N', "\x0F"],
    'PRINT_M':      [r'\x40\x4d', r'\x87\x91', '@M', "\x16"],
    'PRINT_R':      [r'\x40\x52', r'\x87\x92', '@R', "\x17"],
    'PRINT_G':      [r'\x40\x47', r'\x86\xa3', '@G', "\x19"],
    'PRINT_P':      [r'\x40\x50', r'\x87\x9b', '@P', "\x18"],
    'PRINT_H':      [r'\x40\x48', r'\x86\x9f\x00', '@H', "\x1E"],
    'PRINT_L':      [r'\x40\x4c', r'\x86\xa4', '@L', "\x1D"],
    'SETBACK':      [r'\x40\x42', r'\x86\xb3\x00', '@B', "\x15"],
    'SETSPEED':     [r'\x2b\x53', r'\x86\xc9\x00', '+S', "\x14"],
    'SHIFT_TEXT':   [r'\x2b\x54', r'\x86\xc7\x00', '+T', "\x06"],
    'OCARINA':      [r'\x3a\x4f', r'\x81\xf0', ':O', "\x10"],
    'KEEP_OPEN':    [r'\x2a\x4f', r'\x86\xc8', '*O', "\x0A"],
    'AKINDO':       [r'\x81\xf3', r'\x81\xf3\x38\x82', '$', "AKINDO"],
}

NUMBERS = {
    '0':    [r'\x30', "0"],
    '1':    [r'\x31', '1'],
    '2':    [r'\x32', '2'],
    '3':    [r'\x33', '3'],
    '4':    [r'\x34', '4'],
    '5':    [r'\x35', '5'],
    '6':    [r'\x36', '6'],
    '7':    [r'\x37', '7'],
    '8':    [r'\x38', '8'],
    '9':    [r'\x39', '9'],
    'A':    [r'\x41', 'a'],
    'B':    [r'\x42', 'b'],
    'C':    [r'\x43', 'c'],
    'D':    [r'\x44', 'd'],
    'E':    [r'\x45', 'e'],
    'F':    [r'\x46', 'f'],
    'a':    [r'\x61', 'a'],
    'b':    [r'\x62', 'b'],
    'c':    [r'\x63', 'c'],
    'd':    [r'\x64', 'd'],
    'e':    [r'\x65', 'e'],
    'f':    [r'\x66', 'f'],
}

def parsejp(text, mode = 0):
    tag = ""
    ending = "None"
    if (r"\x81\xcb" in text) is True:
        tag += "g"
        ending = "goto"
    if (r"\x86\xc8" in text) is True:
        tag += "k"
        ending = "keep_open"
    if (r"\x81\x9f" in text) is True:
        tag += "e"
        ending = "event"
    if (r"\x81\x9e" in text) is True:
        tag += "f"
        ending = "fade"
    if (r"\x81\xf0" in text) is True:
        tag += "o"
        ending = "ocarina"
    if (r"\x81\xbc" in text) is True:
        tag += "2"
    if (r"\x81\xb8" in text) is True:
        tag += "3"

    if mode == 0:
        return tag
    if mode == 1:
        return ending

GOSSIP_STONE_MESSAGES = list( range(0x0401, 0x04FF) ) # ids of the actual hints
GOSSIP_STONE_MESSAGES += [0x2053, 0x2054] # shared initial stone messages
TEMPLE_HINTS_MESSAGES = [0x7057, 0x707A] # dungeon reward hints from the temple of time pedestal
LIGHT_ARROW_HINT = [0x70CC] # ganondorf's light arrow hint line
GS_TOKEN_MESSAGES = [0x00B4, 0x00B5] # Get Gold Skulltula Token messages
ERROR_MESSAGE = 0x0001
REJECT = [0x00f8,0x0109,0x010a,0x010b,0x010d,0x010e,0x010f,0x0110,0x0111,0x0112,0x0113,0x0117,0x0118,0x011a,0x011b,0x011c,0x011d,0x011e,0x0120,0x0121,0x0122,0x0123,0x0125,0x0127,0x012c,0x012d,0x012e,0x0130,0x0134,0x0135,0x0136,0x0138,0x013b,0x013c,0x013e,0x013f,0x014f,0x0159,0x015d,0x015e,0x016e,0x016f,0x0182,0x0185,0x0187,0x0188,0x018a,0x018b,0x018e,0x0193,0x0196,0x0199,0x019a,0x019b,0x019c,0x019d,0x019e,0x019f,0x01a0,0x01a1,0x01a2,0x01a4,0x01a6,0x01a8,0x01aa,0x032c,0x0346,0x0347,0x060b,0x062c,0x0638,0x063c,0x064a,0x064b,0x403c,0x403d,0x4040,0x4044,0x506f,0x601c,0x6073,0x7068,0x7069,0x706a,0x706b]
MASK_MESSAGES = list( range(0x7100, 0x711F) )
MASK_MESSAGES += list( range(0x7124, 0x71AC) )

# messages for shorter item messages
# ids are in the space freed up by move_shop_item_messages()
ITEM_MESSAGES = {
    0x0001:    ("\x08\x06\x30\x05\x41TEXT ID ERROR!\x05\x40", "<<+T\x30##\x01テキストエラー！##\x00"),
    0x9001:    ("\x08\x13\x2DYou borrowed a \x05\x41Pocket Egg\x05\x40!\x01A Pocket Cucco will hatch from\x01it overnight. Be sure to give it\x01back.", "<<~~\x2D##\x01タマゴ##\x00をお借りした。"),
    0x0002:    ("\x08\x13\x2FYou returned the Pocket Cucco\x01and got \x05\x41Cojiro\x05\x40 in return!\x01Unlike other Cuccos, Cojiro\x01rarely crows.", "<<~~\x2Fてのりコッコをお返しして&&##\x01コジロー##\x00を入手！"),
    0x0003:    ("\x08\x13\x30You got an \x05\x41Odd Mushroom\x05\x40!\x01It is sure to spoil quickly! Take\x01it to the Kakariko Potion Shop.", "<<~~\x30##\x01あやしいキノコ##\x00を入手。"),
    0x0004:    ("\x08\x13\x31You received an \x05\x41Odd Potion\x05\x40!\x01It may be useful for something...\x01Hurry to the Lost Woods!", "<<~~\x31##\x01あやしいクスリ##\x00を入手！"),
    0x0005:    ("\x08\x13\x32You returned the Odd Potion \x01and got the \x05\x41Poacher's Saw\x05\x40!\x01The young punk guy must have\x01left this.", "<<~~\x32あやしいクスリを返して&&##\x01密猟者のノコギリ##\x00を入手！"),
    0x0007:    ("\x08\x13\x48You got a \x01\x05\x41Deku Seeds Bullet Bag\x05\x40.\x01This bag can hold up to \x05\x4640\x05\x40\x01slingshot bullets.", "<<~~\x48##\x01デクのタネブクロ##\x00だ！&&##\x06４０コ##\x00まで入れられる！"),
    0x0008:    ("\x08\x13\x33You traded the Poacher's Saw \x01for a \x05\x41Broken Goron's Sword\x05\x40!\x01Visit Biggoron to get it repaired!", "<<~~\x33密猟者のノコギリをわたして&&##\x01折れたゴロン刀##\x00を入手！"),
    0x0009:    ("\x08\x13\x34You checked in the Broken \x01Goron's Sword and received a \x01\x05\x41Prescription\x05\x40!\x01Go see King Zora!", "<<~~\x34折れたゴロン刀をあずけて&&##\x01処方せん##\x00を入手！"),
    0x000A:    ("\x08\x13\x37The Biggoron's Sword...\x01You got a \x05\x41Claim Check \x05\x40for it!\x01You can't wait for the sword!", "<<~~\x37剛剣ダイゴロン刀！！&&…の##\x01ひきかえ券##\x00を入手。"),
    0x000B:    ("\x08\x13\x2EYou got a \x05\x41Pocket Cucco, \x05\x40one\x01of Anju's prized hens! It fits \x01in your pocket.", "<<~~\x2E##\x01てのりコッコ##\x00を入手！"),
    0x000C:    ("\x08\x13\x3DYou got the \x05\x41Biggoron's Sword\x05\x40!\x01This blade was forged by a \x01master smith and won't break!", "<<~~\x3D巨人のナイフと　交換で&&##\x01剛剣ダイゴロン刀##\x00を入手！"),
    0x000D:    ("\x08\x13\x35You used the Prescription and\x01received an \x05\x41Eyeball Frog\x05\x40!\x01Be quick and deliver it to Lake \x01Hylia!", "<<~~\x35処方せんを渡して&&##\x01メダマガエル##\x00を入手！"),
    0x000E:    ("\x08\x13\x36You traded the Eyeball Frog \x01for the \x05\x41World's Finest Eye Drops\x05\x40!\x01Hurry! Take them to Biggoron!", "<<~~\x36メダマガエルを渡して&&##\x01特製本生目薬##\x00を入手！"),
    0x0010:    ("\x08\x13\x25You borrowed a \x05\x41Skull Mask\x05\x40.\x01You feel like a monster while you\x01wear this mask!", "<<~~\x25##\x01ドクロのお面##\x00を借りた！&&魔物の気分が味わえる。"),
    0x0011:    ("\x08\x13\x26You borrowed a \x05\x41Spooky Mask\x05\x40.\x01You can scare many people\x01with this mask!", "<<~~\x26##\x01こわそなお面##\x00を借りた！&&いろんな人をおどかそう。"),
    0x0012:    ("\x08\x13\x24You borrowed a \x05\x41Keaton Mask\x05\x40.\x01You'll be a popular guy with\x01this mask on!", "<<~~\x24##\x01キータンのお面##\x00を借りた！&&これでキミも人気者。"),
    0x0013:    ("\x08\x13\x27You borrowed a \x05\x41Bunny Hood\x05\x40.\x01The hood's long ears are so\x01cute!", "<<~~\x27##\x01ウサギずきん##\x00を借りた！&&長いお耳が魅力てき！"),
    0x0014:    ("\x08\x13\x28You borrowed a \x05\x41Goron Mask\x05\x40.\x01It will make your head look\x01big, though.", "<<~~\x28##\x01ゴロンのお面##\x01を借りた！&&ちょっとカオがデカいです。"),
    0x0015:    ("\x08\x13\x29You borrowed a \x05\x41Zora Mask\x05\x40.\x01With this mask, you can\x01become one of the Zoras!", "<<~~\x29##\x01ゾーラのお面##\x01を借りた！&&これでアナタも　ゾーラ族。"),
    0x0016:    ("\x08\x13\x2AYou borrowed a \x05\x41Gerudo Mask\x05\x40.\x01This mask will make you look\x01like...a girl?", "<<~~\x2A##\x01ゲルドのお面##\x01を借りた！&&これでアナタも　オネエさん？"),
    0x0017:    ("\x08\x13\x2BYou borrowed a \x05\x41Mask of Truth\x05\x40.\x01Show it to many people!", "<<~~\x2B##\x01まことの仮面##\x00を借りた！&&いろんな人に　見せてみよう。"),
    0x0030:    ("\x08\x13\x06You found the \x05\x41Fairy Slingshot\x05\x40!", "<<~~\x06##\x01妖精のパチンコ##\x00を入手！"),
    0x0031:    ("\x08\x13\x03You found the \x05\x41Fairy Bow\x05\x40!", "<<~~\x03##\x01妖精の弓##\x00を入手！"),
    0x0032:    ("\x08\x13\x02You got \x05\x41Bombs\x05\x40!\x01If you see something\x01suspicious, bomb it!", "<<~~\x02##\x01バクダン##\x00を入手！"),
    0x0033:    ("\x08\x13\x09You got \x05\x41Bombchus\x05\x40!", "<<~~\x09##\x01ボムチュウ##\x00を入手！"),
    0x0034:    ("\x08\x13\x01You got a \x05\x41Deku Nut\x05\x40!", "<<~~\x01##\x01デクの実##\x00を入手！"),
    0x0035:    ("\x08\x13\x0EYou found the \x05\x41Boomerang\x05\x40!", "<<~~\x0E##\x01ブーメラン##\x00を入手！"),
    0x0036:    ("\x08\x13\x0AYou found the \x05\x41Hookshot\x05\x40!\x01It's a spring-loaded chain that\x01you can cast out to hook things.", "<<~~\x0A##\x01フックショット##\x00を入手！"),
    0x0037:    ("\x08\x13\x00You got a \x05\x41Deku Stick\x05\x40!", "<<~~\x00##\x01デクの棒##\x00を入手！"),
    0x0038:    ("\x08\x13\x11You found the \x05\x41Megaton Hammer\x05\x40!\x01It's so heavy, you need to\x01use two hands to swing it!", "<<~~\x11##\x01メガトンハンマー##\x00を入手！&&威力はデカいが両手持ち！"),
    0x0039:    ("\x08\x13\x0FYou found the \x05\x41Lens of Truth\x05\x40!\x01Mysterious things are hidden\x01everywhere!", "<<~~\x0F##\x01まことのメガネ##\x00を入手！&&フシギな物が見えかくれ。"),
    0x003A:    ("\x08\x13\x08You found the \x05\x41Ocarina of Time\x05\x40!\x01It glows with a mystical light...", "<<~~\x08##\x01時のオカリナ##\x00を入手！&&神秘的な光を放っている…"),
    0x003C:    ("\x08\x13\x67You received the \x05\x41Fire\x01Medallion\x05\x40!\x01Darunia awakens as a Sage and\x01adds his power to yours!", "<<~~\x67##\x01炎のメダル##\x00を入手！&&ダルニアは　賢者として目覚め&&勇者に力が　宿った！"),
    0x003D:    ("\x08\x13\x68You received the \x05\x43Water\x01Medallion\x05\x40!\x01Ruto awakens as a Sage and\x01adds her power to yours!", "<<~~\x68##\x03水のメダル##\x00を入手！&&ルトは　賢者として目覚め&&勇者に力が　宿った！"),
    0x003E:    ("\x08\x13\x66You received the \x05\x42Forest\x01Medallion\x05\x40!\x01Saria awakens as a Sage and\x01adds her power to yours!", "<<~~\x66##\x02森のメダル##\x00を入手！&&サリアは　賢者として目覚め&&勇者に力が　宿った！"),
    0x003F:    ("\x08\x13\x69You received the \x05\x46Spirit\x01Medallion\x05\x40!\x01Nabooru awakens as a Sage and\x01adds her power to yours!", "<<~~\x69##\x06魂のメダル##\x00を入手！&&ナボールは　賢者として目覚め&&勇者に力が　宿った！"),
    0x0040:    ("\x08\x13\x6BYou received the \x05\x44Light\x01Medallion\x05\x40!\x01Rauru the Sage adds his power\x01to yours!", "<<~~\x6B##\x04光のメダル##\x00を入手！&&ラウルは　賢者として目覚め&&勇者に力が　宿った！"),
    0x0041:    ("\x08\x13\x6AYou received the \x05\x45Shadow\x01Medallion\x05\x40!\x01Impa awakens as a Sage and\x01adds her power to yours!", "<<~~\x6A##\x05闇のメダル##\x00を入手！&&インパは　賢者として目覚め&&勇者に力が　宿った！"),
    0x0042:    ("\x08\x13\x14You got an \x05\x41Empty Bottle\x05\x40!\x01You can put something in this\x01bottle.", "<<~~\x14##\x01あきビン##\x00を入手！&&なにかとべんり！"),
    0x0043:    ("\x08\x13\x15You got a \x05\x41Red Potion\x05\x40!\x01It will restore your health", "<<~~\x15##\x01赤いクスリ##\x00を入手！&&体力を回復するぞ！"),
    0x0044:    ("\x08\x13\x16You got a \x05\x42Green Potion\x05\x40!\x01It will restore your magic.", "<<~~\x16##\x02緑のクスリ##\x00を入手！&&魔力を回復するぞ！"),
    0x0045:    ("\x08\x13\x17You got a \x05\x43Blue Potion\x05\x40!\x01It will recover your health\x01and magic.", "<<~~\x17##\x03青いクスリ##\x00を入手！&&体力、魔力も全復活！"),
    0x0046:    ("\x08\x13\x18You caught a \x05\x41Fairy\x05\x40 in a bottle!\x01It will revive you\x01the moment you run out of life \x01energy.", "<<~~\x18##\x01妖精##\x00をビンにつめた！"),
    0x0047:    ("\x08\x13\x19You got a \x05\x41Fish\x05\x40!\x01It looks so fresh and\x01delicious!", "<<~~\x19##\x01サカナ##\x00をビンにつめた！"),
    0x0048:    ("\x08\x13\x10You got a \x05\x41Magic Bean\x05\x40!\x01Find a suitable spot for a garden\x01and plant it.", "<<~~\x10##\x01魔法のマメ\x00を入手！&&いい場所さがして　まこう！"),
    0x9048:    ("\x08\x13\x10You got a \x05\x41Pack of Magic Beans\x05\x40!\x01Find suitable spots for a garden\x01and plant them.", "<<~~\x10##\x01マメ袋\x00を入手！&&いい場所さがして　まこう！"),
    0x004A:    ("\x08\x13\x07You received the \x05\x41Fairy Ocarina\x05\x40!\x01This is a memento from Saria.", "<<~~\x07##\x01妖精のオカリナ##\x00を入手！&&サリアとの思い出の品だ。"),
    0x004B:    ("\x08\x13\x3DYou got the \x05\x42Giant's Knife\x05\x40!\x01Hold it with both hands to\x01attack! It's so long, you\x01can't use it with a \x05\x44shield\x05\x40.", "<<~~\x3D##\x02巨人のナイフ##\x00を入手！&&両手で持って斬る。&&##\x04盾##\x00と同時に使えない。"),
    0x004C:    ("\x08\x13\x3EYou got a \x05\x44Deku Shield\x05\x40!", "<<~~\x3E##\x04デクの盾##\x00を入手！"),
    0x004D:    ("\x08\x13\x3FYou got a \x05\x44Hylian Shield\x05\x40!", "<<~~\x3F##\x04ハイリアの盾##\x00を入手！"),
    0x004E:    ("\x08\x13\x40You found the \x05\x44Mirror Shield\x05\x40!\x01The shield's polished surface can\x01reflect light or energy.", "<<~~\x40##\x04ミラーシールド##\x00を入手！&&鏡の盾は、光をはじく。"),
    0x004F:    ("\x08\x13\x0BYou found the \x05\x41Longshot\x05\x40!\x01It's an upgraded Hookshot.\x01It extends \x05\x41twice\x05\x40 as far!", "<<~~\x0B##\x01ロングフック##\x00を入手！&&長さが##\x01２倍##\x00になった！"),
    0x0050:    ("\x08\x13\x42You got a \x05\x41Goron Tunic\x05\x40!\x01Going to a hot place? No worry!", "<<~~\x42##\x01ゴロンの服##\x00を入手！"),
    0x0051:    ("\x08\x13\x43You got a \x05\x43Zora Tunic\x05\x40!\x01Wear it, and you won't drown\x01underwater.", "<<~~\x43##\x03ゾーラの服##\x00を入手！"),
    0x0052:    ("\x08You got a \x05\x42Magic Jar\x05\x40!\x01Your Magic Meter is filled!", "<<##\x02魔法のツボ##\x00を入手！&&魔力が回復する！"),
    0x0053:    ("\x08\x13\x45You got the \x05\x41Iron Boots\x05\x40!\x01So heavy, you can't run.\x01So heavy, you can't float.", "<<~~\x45##\x01ヘビィブーツ##\x00を入手！"),
    0x0054:    ("\x08\x13\x46You got the \x05\x41Hover Boots\x05\x40!\x01With these mysterious boots\x01you can hover above the ground.", "<<~~\x46##\x01ホバーブーツ##\x00を入手！"),
    0x0055:    ("\x08You got a \x05\x45Recovery Heart\x05\x40!\x01Your life energy is recovered!", "<<##\x05回復のハート##\x00を入手！&&体力が回復する！"),
    0x0056:    ("\x08\x13\x4BYou upgraded your quiver to a\x01\x05\x41Big Quiver\x05\x40!\x01Now you can carry more arrows-\x01\x05\x4640 \x05\x40in total!", "<<~~\x4B##\x01大きな矢立て##\x00を入手！&&##\x06４０本##\x00も入る！"),
    0x0057:    ("\x08\x13\x4CYou upgraded your quiver to\x01the \x05\x41Biggest Quiver\x05\x40!\x01Now you can carry to a\x01maximum of \x05\x4650\x05\x40 arrows!", "<<~~\x4C##\x01最大の矢立て##\x00を入手！&&##\x06５０本##\x00も入る！"),
    0x0058:    ("\x08\x13\x4DYou found a \x05\x41Bomb Bag\x05\x40!\x01You found \x05\x4120 Bombs\x05\x40 inside!", "<<~~\x4D##\x01ボム袋##\x00を入手！&&##\x01バクダン２０コ##\x00入り！"),
    0x0059:    ("\x08\x13\x4EYou got a \x05\x41Big Bomb Bag\x05\x40!\x01Now you can carry more \x01Bombs, up to a maximum of \x05\x4630\x05\x40!", "<<~~\x4E##\x01大きなボム袋##\x00を入手！&&##\x06３０コ##\x00も入る！"),
    0x005A:    ("\x08\x13\x4FYou got the \x01\x05\x41Biggest Bomb Bag\x05\x40!\x01Now, you can carry up to \x01\x05\x4640\x05\x40 Bombs!", "<<~~\x4F##\x01最大のボム袋##\x00を入手！&&##\x06４０コ##\x00も入る！"),
    0x005B:    ("\x08\x13\x51You found the \x05\x43Silver Gauntlets\x05\x40!\x01You feel the power to lift\x01big things with it!", "<<~~\x51##\x03銀のグローブ##\x00を入手！&&そうびすれば　力があふれる。"),
    0x005C:    ("\x08\x13\x52You found the \x05\x43Golden Gauntlets\x05\x40!\x01You can feel even more power\x01coursing through your arms!", "<<~~\x52##\x03金のグローブ##\x00を入手！&&両腕にさらに　力がみなぎる！"),
    0x005D:    ("\x08\x13\x1CYou put a \x05\x44Blue Fire\x05\x40\x01into the bottle!\x01This is a cool flame you can\x01use on red ice.", "<<~~\x1C##\x04青い炎##\x00をビンにつめた！"),
    0x005E:    ("\x08\x13\x56You got an \x05\x43Adult's Wallet\x05\x40!\x01Now you can hold\x01up to \x05\x46200\x05\x40 \x05\x46Rupees\x05\x40.", "<<~~\x56##\x03大人のサイフ##\x00を入手！&&##\x06２００ルピー##\x00まで持てるゾ！"),
    0x005F:    ("\x08\x13\x57You got a \x05\x43Giant's Wallet\x05\x40!\x01Now you can hold\x01up to \x05\x46500\x05\x40 \x05\x46Rupees\x05\x40.", "<<~~\x57##\x03巨人のサイフ##\x00を入手！&&##\x06５００ルピー##\x00まで持てるゾ！"),
    0x0060:    ("\x08\x13\x77You found a \x05\x41Small Key\x05\x40!\x01This key will open a locked \x01door. You can use it only\x01in this dungeon.", "<<~~\x77##\x01小さなカギ##\x00を入手！&&カギ付ドアを開くカギ。&&ここでしか使えません。"),
    0x0066:    ("\x08\x13\x76You found the \x05\x41Dungeon Map\x05\x40!\x01It's the map to this dungeon.", "<<~~\x76##\x01ダンジョン地図##\x00を入手！&&ここの地図のようだ。"),
    0x0067:    ("\x08\x13\x75You found the \x05\x41Compass\x05\x40!\x01Now you can see the locations\x01of many hidden things in the\x01dungeon!", "<<~~\x75##\x01コンパス##\x00を入手！&&ここの物の場所が分かった！"),
    0x0068:    ("\x08\x13\x6FYou obtained the \x05\x41Stone of Agony\x05\x40!\x01If you equip a \x05\x44Rumble Pak\x05\x40, it\x01will react to nearby...secrets.", "<<~~\x6F##\x01もだえ石##\x00を入手！&&秘密があると震えるゾ。"),
    0x0069:    ("\x08\x13\x23You received \x05\x41Zelda's Letter\x05\x40!\x01Wow! This letter has Princess\x01Zelda's autograph!", "<<~~\\x23##\x01ゼルダの手紙##\x00を入手！&&ゼルダ姫直筆サイン入り！"),
    0x006C:    ("\x08\x13\x49Your \x05\x41Deku Seeds Bullet Bag \x01\x05\x40has become bigger!\x01This bag can hold \x05\x4650\x05\x41 \x05\x40bullets!", "<<~~\x49##\x01タネブクロ##\x00が大きくなった！&&##\x06５０コ##\x00まで入るぞ！"),
    0x006F:    ("\x08You got a \x05\x42Green Rupee\x05\x40!\x01That's \x05\x42one Rupee\x05\x40!", "<<##\x02緑ルピー##\x00を入手！&&##\x02１ルピー##\x00だ。"),
    0x0070:    ("\x08\x13\x04You got the \x05\x41Fire Arrow\x05\x40!\x01If you hit your target,\x01it will catch fire.", "<<~~\x04##\x01炎の矢##\x00を入手！&&命中すれば　火ダルマだ！！"),
    0x0071:    ("\x08\x13\x0CYou got the \x05\x43Ice Arrow\x05\x40!\x01If you hit your target,\x01it will freeze.", "<<~~\x0C##\x03氷の矢##\x00を入手！&&命中すれば　凍りつく！！"),
    0x0072:    ("\x08\x13\x12You got the \x05\x44Light Arrow\x05\x40!\x01The light of justice\x01will smite evil!", "<<~~\x12##\x04光の矢##\x00を入手！&&聖なる光が　悪を射る！！"),
    0x0073:    ("\x08\x06\x28You have learned the\x01\x06\x2F\x05\x42Minuet of Forest\x05\x40!", "<<##\x02森のメヌエット##\x00をおぼえた！"),
    0x0074:    ("\x08\x06\x28You have learned the\x01\x06\x37\x05\x41Bolero of Fire\x05\x40!", "<<##\x01炎のボレロ##\x00をおぼえた！"),
    0x0075:    ("\x08\x06\x28You have learned the\x01\x06\x29\x05\x43Serenade of Water\x05\x40!", "<<##\x03水のセレナーデ##\x00をおぼえた！"),
    0x0076:    ("\x08\x06\x28You have learned the\x01\x06\x2D\x05\x46Requiem of Spirit\x05\x40!", "<<##\x06魂のレクイエム##\x00をおぼえた！"),
    0x0077:    ("\x08\x06\x28You have learned the\x01\x06\x28\x05\x45Nocturne of Shadow\x05\x40!", "<<##\x05闇のノクターン##\x00をおぼえた！"),
    0x0078:    ("\x08\x06\x28You have learned the\x01\x06\x32\x05\x44Prelude of Light\x05\x40!", "<<##\x04光のプレリュード##\x00をおぼえた！"),
    0x0079:    ("\x08\x13\x50You got the \x05\x41Goron's Bracelet\x05\x40!\x01Now you can pull up Bomb\x01Flowers.", "<<~~\x50##\x01ゴロンのうでわ##\x00を入手！&&バクダン花を引き抜ける。"),
    0x007A:    ("\x08\x13\x1DYou put a \x05\x41Bug \x05\x40in the bottle!\x01This kind of bug prefers to\x01live in small holes in the ground.", "<<~~\x1D##\x01ムシ##\x00をビンに入れた！&&小さな穴にもぐりこみます。"),
    0x007B:    ("\x08\x13\x70You obtained the \x05\x41Gerudo's \x01Membership Card\x05\x40!\x01You can get into the Gerudo's\x01training ground.", "<<~~\x70##\x01ゲルドの会員証##\x00を入手！&&ゲルドの修練場に入れます。"),
    0x0080:    ("\x08\x13\x6CYou got the \x05\x42Kokiri's Emerald\x05\x40!\x01This is the Spiritual Stone of \x01Forest passed down by the\x01Great Deku Tree.", "<<~~\x6C##\x02コキリのヒスイ##\x00を入手！&&デクの樹サマから託された、&&森の精霊石。"),
    0x0081:    ("\x08\x13\x6DYou obtained the \x05\x41Goron's Ruby\x05\x40!\x01This is the Spiritual Stone of \x01Fire passed down by the Gorons!", "<<~~\x6D##\x01ゴロンのルビー##\x00を入手！&&ゴロン族に伝わる、炎の精霊石。"),
    0x0082:    ("\x08\x13\x6EYou obtained \x05\x43Zora's Sapphire\x05\x40!\x01This is the Spiritual Stone of\x01Water passed down by the\x01Zoras!", "<<~~\x6E##\x03ゾーラのサファイア##\x00を入手！&&ゾーラ族に伝わる、水の精霊石。"),
    0x0090:    ("\x08\x13\x00Now you can pick up \x01many \x05\x41Deku Sticks\x05\x40!\x01You can carry up to \x05\x4620\x05\x40 of them!", "<<~~\x00##\x01デクの棒##\x00を##\x06２０本##\x00まで&&持てるようになった！"),
    0x0091:    ("\x08\x13\x00You can now pick up \x01even more \x05\x41Deku Sticks\x05\x40!\x01You can carry up to \x05\x4630\x05\x40 of them!", "<<~~\x00##\x01デクの棒##\x00を##\x06３０本##\x00まで&&持てるようになった！"),
    0x0097:    ("\x08\x13\x20You caught a \x05\x41Poe \x05\x40in a bottle!\x01Something good might happen!", "<<~~\x20##\x01ポウ##\x00をビンにつめた！"),
    0x0098:    ("\x08\x13\x1AYou got \x05\x41Lon Lon Milk\x05\x40!\x01This milk is very nutritious!\x01There are two drinks in it.", "<<~~\x1A##\x01ロンロン牛乳##\x00をビンにつめた！&&２回飲めるゾ！"),
    0x0099:    ("\x08\x13\x1BYou found \x05\x41Ruto's Letter\x05\x40 in a\x01bottle! Show it to King Zora.", "<<~~\x1B##\x01ルトの手紙##\x00を入手！"),
    0x9099:    ("\x08\x13\x1BYou found \x05\x41a letter in a bottle\x05\x40!\x01You remove the letter from the\x01bottle, freeing it for other uses.", "<<~~\x1B##\x01あきビン##\x00を入手！&&なにかとべんり！"),
    0x009A:    ("\x08\x13\x21You got a \x05\x41Weird Egg\x05\x40!\x01Feels like there's something\x01moving inside!", "<<~~\x21##\x01ふしぎなタマゴ##\x00を入手！"),
    0x00A4:    ("\x08\x13\x3BYou got the \x05\x42Kokiri Sword\x05\x40!\x01This is a hidden treasure of\x01the Kokiri.", "<<~~\x3B##\x02コキリの剣##\x00を入手した！"),
    0x00A7:    ("\x08\x13\x01Now you can carry\x01many \x05\x41Deku Nuts\x05\x40!\x01You can hold up to \x05\x4630\x05\x40 nuts!", "<<~~\x01##\x01デクの実##\x00を##\x06３０コ##\x00まで&&持てるようになった！"),
    0x00A8:    ("\x08\x13\x01You can now carry even\x01more \x05\x41Deku Nuts\x05\x40! You can carry\x01up to \x05\x4640\x05\x41 \x05\x40nuts!", "<<~~\x01##\x01デクの実##\x00を##\x06４０コ##\x00まで&&持てるようになった！"),
    0x00AD:    ("\x08\x13\x05You got \x05\x41Din's Fire\x05\x40!\x01Its fireball engulfs everything!", "<<~~\x05##\x01ディンの炎##\x00を入手！"),
    0x00AE:    ("\x08\x13\x0DYou got \x05\x42Farore's Wind\x05\x40!\x01This is warp magic you can use!", "<<~~\x0D##\x02フロルの風##\x00を入手！"),
    0x00AF:    ("\x08\x13\x13You got \x05\x43Nayru's Love\x05\x40!\x01Cast this to create a powerful\x01protective barrier.", "<<~~\x13##\x03ネールの愛##\x00を入手！"),
    0x00B4:    ("\x08You got a \x05\x41Gold Skulltula Token\x05\x40!\x01You've collected \x05\x41\x19\x05\x40 tokens in total.", "<<##\x01スタルチュラトークン##\x00を入手！&&これで##\x01@Gコ##\x00だ！"),
    0x00B5:    ("\x08You destroyed a \x05\x41Gold Skulltula\x05\x40.\x01You got a token proving you \x01destroyed it!", "<<##\x01黄金のスタルチュラ##\x00を倒した！&&倒した「しるし」を入手！"),
    0x00C2:    ("\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Collect four pieces total to get\x01another Heart Container.", "<<~~\x73##\x01ハートの欠片##\x00を入手！&&４つで１つの器。"),
    0x00C3:    ("\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01So far, you've collected two \x01pieces.", "<<~~\x73##\x01ハートの欠片##\x00を入手！&&これで２コ目。"),
    0x00C4:    ("\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Now you've collected three \x01pieces!", "<<~~\x73##\x01ハートの欠片##\x00を入手！&&これで３コ目。"),
    0x00C5:    ("\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01You've completed another Heart\x01Container!", "<<~~\x73##\x01ハートの欠片##\x00を入手！&&かけら４コで器が完成！！"),
    0x00C6:    ("\x08\x13\x72You got a \x05\x41Heart Container\x05\x40!\x01Your maximum life energy is \x01increased by one heart.", "<<~~\x72##\x01ハートの器##\x00を入手！&&ライフの上限１ＵＰ！"),
    0x00C7:    ("\x08\x13\x74You got the \x05\x41Boss Key\x05\x40!\x01Now you can get inside the \x01chamber where the Boss lurks.", "<<~~\x74##\x01ボスキー##\x00を入手！&&ダンジョンのボスの部屋へ&&入れるようになった！"),
    0x9002:    ("\x08You are a \x05\x43FOOL\x05\x40!", "<<Ｙｏｕ　ａｒｅ　ａ　##\x03ＦＯＯＬ##\x00！"),
    0x00CC:    ("\x08You got a \x05\x43Blue Rupee\x05\x40!\x01That's \x05\x43five Rupees\x05\x40!", "<<##\x03青ルピー##\x00を入手！&&##\x03５ルピー##\x00だ。"),
    0x00CD:    ("\x08\x13\x53You got the \x05\x43Silver Scale\x05\x40!\x01You can dive deeper than you\x01could before.", "<<~~\x53##\x03銀のウロコ##\x00を入手！"),
    0x00CE:    ("\x08\x13\x54You got the \x05\x43Golden Scale\x05\x40!\x01Now you can dive much\x01deeper than you could before!", "<<~~\x54##\x03金のウロコ##\x00を入手！"),
    0x00D1:    ("\x08\x06\x14You've learned \x05\x42Saria's Song\x05\x40!", "<<##\x02サリアの歌##\x00をおぼえた！"),
    0x00D2:    ("\x08\x06\x11You've learned \x05\x41Epona's Song\x05\x40!", "<<##\x01エポナの歌##\x00をおぼえた！"),
    0x00D3:    ("\x08\x06\x0BYou've learned the \x05\x46Sun's Song\x05\x40!", "<<##\x06太陽の歌##\x00をおぼえた！"),
    0x00D4:    ("\x08\x06\x15You've learned \x05\x43Zelda's Lullaby\x05\x40!", "<<##\x03ゼルダの子守歌##\x00をおぼえた！"),
    0x00D5:    ("\x08\x06\x05You've learned the \x05\x44Song of Time\x05\x40!", "<<##\x04時の歌##\x00をおぼえた！"),
    0x00D6:    ("\x08You've learned the \x05\x45Song of Storms\x05\x40!", "<<##\x05嵐の歌##\x00をおぼえた！"),
    0x00DC:    ("\x08\x13\x58You got \x05\x41Deku Seeds\x05\x40!\x01Use these as bullets\x01for your Slingshot.", "<<~~\x58##\x01デクのタネ##\x00を入手！&&パチンコのタマに使えるゾ！"),
    0x00DD:    ("\x08You mastered the secret sword\x01technique of the \x05\x41Spin Attack\x05\x40!", "<<秘技##\x01回転斬り##\x00をおぼえた！！"),
    0x00E4:    ("\x08You can now use \x05\x42Magic\x05\x40!", "<<##\x02魔力##\x00を入手！！"),
    0x00E5:    ("\x08Your \x05\x44defensive power\x05\x40 is enhanced!", "<<##\x04防御力##\x00が強化された！"),
    0x00E6:    ("\x08You got a \x05\x46bundle of arrows\x05\x40!", "<<##\x06矢の束##\x00を入手！"),
    0x00E8:    ("\x08Your magic power has been \x01enhanced! Now you have twice\x01as much \x05\x41Magic Power\x05\x40!", "<<魔力が強化された！&&これまでの　##\x01２倍の魔法##\x00が&&使えるようになった。"),
    0x00E9:    ("\x08Your defensive power has been \x01enhanced! Damage inflicted by \x01enemies will be \x05\x41reduced by half\x05\x40.", "<<防御力が強化された！&&敵から受けるダメージが&&今までの##\x01半分##\x00になった。"),
    0x00F0:    ("\x08You got a \x05\x41Red Rupee\x05\x40!\x01That's \x05\x41twenty Rupees\x05\x40!", "<<##\x01赤ルピー##\x00を入手！&&##\x01２０ルピー##\x00だ。"),
    0x00F1:    ("\x08You got a \x05\x45Purple Rupee\x05\x40!\x01That's \x05\x45fifty Rupees\x05\x40!", "<<##\x05紫ルピー##\x00を入手！&&##\x05５０ルピー##\x00だ。"),
    0x00F2:    ("\x08You got a \x05\x46Huge Rupee\x05\x40!\x01This Rupee is worth a whopping\x01\x05\x46two hundred Rupees\x05\x40!", "<<##\x06金ルピー##\x00を入手！&&##\x06２００ルピー##\x00だ。"),
    0x00F9:    ("\x08\x13\x1EYou put a \x05\x41Big Poe \x05\x40in a bottle!\x01Let's sell it at the \x05\x41Ghost Shop\x05\x40!\x01Something good might happen!", "<<~~\x1E##\x01ビッグポウ##\x00をビンにつめた！&&##\x01ゴーストショップ##\x00で　売ろう！"),
    0x9003:    ("\x08You found a piece of the \x05\x41Triforce\x05\x40!", "<<##\x01トライフォースの欠片##\x00を入手！"),
}

KEYSANITY_MESSAGES = {
    0x001C:    ("\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09", "~~\x74<<##\x01炎の神殿##\x00の##\x01ボスキー##\x00を&&入手！>>"),
    0x0006:    ("\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09", "~~\x74<<##\x02森の神殿##\x00の##\x01ボスキー##\x00を&&入手！>>"),
    0x001D:    ("\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09", "~~\x74<<##\x03水の神殿##\x00の##\x01ボスキー##\x00を&&入手！>>"),
    0x001E:    ("\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09", "~~\x74<<##\x06魂の神殿##\x00の##\x01ボスキー##\x00を&&入手！>>"),
    0x002A:    ("\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09", "~~\x74<<##\x05闇の神殿##\x00の##\x01ボスキー##\x00を&&入手！>>"),
    0x0061:    ("\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for \x05\x41Ganon's Castle\x05\x40!\x09", "~~\x74<<##\x01ガノン城##\x00の##\x01ボスキー##\x00を&&入手！>>"),
    0x0062:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x42Deku Tree\x05\x40!\x09", "~~\x75<<##\x02デクの樹##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x0063:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for \x05\x41Dodongo's Cavern\x05\x40!\x09", "~~\x75<<##\x01ドドンゴ##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x0064:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for \x05\x43Jabu Jabu's Belly\x05\x40!\x09", "~~\x75<<##\x03ジャブジャブ##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x0065:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09", "~~\x75<<##\x02森の神殿##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x007C:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09", "~~\x75<<##\x01炎の神殿##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x007D:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09", "~~\x75<<##\x03水の神殿##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x007E:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09", "~~\x75<<##\x06魂の神殿##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x007F:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09", "~~\x75<<##\x05闇の神殿##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x0087:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x44Ice Cavern\x05\x40!\x09", "~~\x75<<##\x04氷の洞窟##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x0088:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x42Deku Tree\x05\x40!\x09", "~~\x76<<##\x02デクの樹##\x00の##\x01地図##\x00を&&入手！>>"),
    0x0089:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for \x05\x41Dodongo's Cavern\x05\x40!\x09", "~~\x76<<##\x01ドドンゴ##\x00の##\x01地図##\x00を&&入手！>>"),
    0x008A:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for \x05\x43Jabu Jabu's Belly\x05\x40!\x09", "~~\x76<<##\x03ジャブジャブ##\x00の##\x01地図##\x00を&&入手！>>"),
    0x008B:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09", "~~\x76<<##\x02森の神殿##\x00の##\x01地図##\x00を&&入手！>>"),
    0x008C:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09", "~~\x76<<##\x01炎の神殿##\x00の##\x01地図##\x00を&&入手！>>"),
    0x008E:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09", "~~\x76<<##\x03水の神殿##\x00の##\x01地図##\x00を&&入手！>>"),
    0x008F:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09", "~~\x76<<##\x06魂の神殿##\x00の##\x01地図##\x00を&&入手！>>"),
    0x0092:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x44Ice Cavern\x05\x40!\x09", "~~\x76<<##\x04氷の洞窟##\x00の##\x01地図##\x00を&&入手！>>"),
    0x0093:    ("\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09", "~~\x77<<##\x02森の神殿##\x00の##\x01カギ##\x00を&&入手！>>"),
    0x0094:    ("\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09", "~~\x77<<##\x01炎の神殿##\x00の##\x01カギ##\x00を&&入手！>>"),
    0x0095:    ("\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09", "~~\x77<<##\x03水の神殿##\x00の##\x01カギ##\x00を&&入手！>>"),
    0x009B:    ("\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x45Bottom of the Well\x05\x40!\x09", "~~\x77<<##\x05井戸の下##\x00の##\x01カギ##\x00を&&入手！>>"),
    0x009F:    ("\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x46Gerudo Training\x01Ground\x05\x40!\x09", "~~\x77<<##\x06修練場##\x00の##\x01カギ##\x00を&&入手！>>"),
    0x00A0:    ("\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x46Thieves' Hideout\x05\x40!\x09", "~~\x77<<##\x06盗賊団##\x00の##\x01カギ##\x00を&&入手！>>"),
    0x00A1:    ("\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for \x05\x41Ganon's Castle\x05\x40!\x09", "~~\x77<<##\x01ガノン城##\x00の##\x01カギ##\x00を&&入手！>>"),
    0x00A2:    ("\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x45Bottom of the Well\x05\x40!\x09", "~~\x75<<##\x05井戸の下##\x00の##\x01コンパス##\x00を&&入手！>>"),
    0x00A3:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09", "~~\x76<<##\x05闇の神殿##\x00の##\x01地図##\x00を&&入手！>>"),
    0x00A5:    ("\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x45Bottom of the Well\x05\x40!\x09", "~~\x76<<##\x05井戸の下##\x00の##\x01地図##\x00を&&入手！>>"),
    0x00A6:    ("\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09", "~~\x77<<##\x06魂の神殿##\x00の##\x01カギ##\x00を&&入手！>>"),
    0x00A9:    ("\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09", "~~\x77<<##\x05闇の神殿##\x00の##\x01カギ##\x00を&&入手！>>"),
}

NAVI_MESSAGES = {
    0x0100: ("<#\x04？#\x00",0x03),
    0x0101: ("<#\x04この#\x00クモの巣#\x04の下！&覗けるよ！#\x00",0x03),
    0x0102: ("<#\x04このツタなら登れそう！#\x00",0x03),
    0x0103: ("<扉#\x04は前に立って&開けられるヨ#\x00",0x03),
    0x0104: ("<#\x04古い#\x00ハシゴ#\x04みたい#\x00",0x03),
    0x0105: ("<時の扉#\x04と同じ模様ね#\x00",0x03),
    0x0106: ("<#\x04さっきまで火がついてたみたい#\x00",0x03),
    0x0107: ("<#\x04この先は#\x00カニ歩き#\x04で&慎重に…#\x00",0x03),
    0x0108: ("<#\x04この#\x00ブロック#\x04動かせるよ#\x00",0x03),
    0x010C: ("<#\x04水で深くもぐれるよ#\x00",0x03),
    0x0114: ("<#\x04全部に火をつける方法って&ないかしら？#\x00",0x03),
    0x0115: ("<#\x04足元には気をつけて！#\x00",0x03),
    0x0116: ("<#\x04これですぐに上がれるね#\x00",0x03),
    0x0119: ("<#\x04曲がり角では#\x00カニ歩き#\x04&これ大事#\x00",0x03),
    0x011F: ("<#\x04？#\x00",0x03),
    0x0124: ("<#\x04この女神の顔…#\x00",0x03),
    0x0126: ("<「真実の目を求めよ」#\x04だってサ#\x00",0x03),
    0x0128: ("<#\x01聖者の足#\x00持つ者&風に身をまかせよ&#\x04だってサ#\x00",0x03),
    0x0129: ("<「頭上注意！」#\x04だってサ#\x00",0x03),
    0x012A: ("<「足元注意！」#\x04だってサ#\x00",0x03),
    0x012B: ("<#\x04ここから水が流れこんでるのね#\x00",0x03),
    0x012F: ("<#\x04この#\x02緑色の#\x04電気が流れてる！#\x00",0x03),
    0x0131: ("<#\x04この#\x01赤いの#\x04電気が流れてる！#\x00",0x03),
    0x0132: ("<#\x04この#\x03青いの#\x04電気が流れてる！#\x00",0x03),
    0x0133: ("<#\x04このスイッチ…&まだ押せないみたい#\x00",0x03),
    0x0137: ("<#\x01赤いの#\x04消えてる！#\x00",0x03),
    0x0139: ("<#\x04向こうに何かあるヨ！#\x00",0x03),
    0x013A: ("<#\x04台上に何かあるみたい#\x00",0x03),
    0x013D: ("<#\x04どれが本物？#\x00",0x03),
    0x0140: ("<#\x04一緒に来て！#\x00",0x03),
    0x0141: ("<#\x04中へ入りましょ！#\x00",0x03),
    0x0142: ("<#\x04お姫様に会うのよね？#\x00",0x03),
    0x0143: ("<#\x04牧場の子のお父さん&どこなのかな？#\x00",0x03),
    0x0144: ("<お姫様#\x04どこにいるの？#\x00",0x03),
    0x0145: ("<サリア#\x04は何て&言うかしら？#\x00",0x03),
    0x0146: ("<#\x04精霊石は&どこにあるの？#\x00",0x03),
    0x0147: ("<#\x04中へ入りましょ！#\x00",0x03),
    0x0148: ("<「残像剣を求めよ」#\x04だってサ#\x00",0x03),
    0x0149: ("<#\x04精霊石は&どこにあるの？#\x00",0x03),
    0x014A: ("<ルト姫#\x04はお腹の中みたいね#\x00",0x03),
    0x014B: ("<ハイラル城#\x04へ戻ろう！#\x00",0x03),
    0x014C: ("<#\x04投げこんだのは何かしら？#\x00",0x03),
    0x014D: ("<時の神殿#\x04行ってみる？#\x00",0x03),
    0x014E: ("<カカリコ村#\x04行ってみる？#\x00",0x03),
    0x0150: ("<コキリの森#\x04行ってみる？#\x00",0x03),
    0x0151: ("<火口#\x04行ってみる？#\x00",0x03),
    0x0152: ("<ゾーラの里#\x04行ってみる？#\x00",0x03),
    0x0153: ("<ヘビィブーツ#\x04すごく重そう#\x00",0x03),
    0x0154: ("<#\x04後ろ歩きは便利だヨ！#\x00",0x03),
    0x0155: ("<井戸#\x04行ってみる？#\x00",0x03),
    0x0156: ("<魂の神殿#\x04行ってみる？#\x00",0x03),
    0x0157: ("<#\x04オカリナは吹いた？#\x00",0x03),
    0x0158: ("<砂漠#\x04行ってみる？#\x00",0x03),
    0x015A: ("<グローブ#\x04があれば&重いものも持てるヨ！#\x00",0x03),
    0x015B: ("<#\x04?#\x00",0x03),
    0x015C: ("<ガノン城#\x04行ってみる？#\x00",0x03),
    0x015F: ("<#\x04がんばって！#\x00",0x03),
    0x0160: ("<普通にお話ししましょ！",0x03),
    0x0161: ("<私の歌が聞こえたら&森は近いヨ！",0x03),
    0x0162: ("<ウフフ！",0x03),
    0x0163: ("<精霊石を集めてるの？",0x03),
    0x0164: ("<精霊石を集めてるの？",0x03),
    0x0165: ("<嫌な胸騒ぎがする…",0x03),
    0x0166: ("<オカリナ上手くなった？",0x03),
    0x0167: ("<「#\x04闇は、嵐によって　開く#\x00」&…だって",0x03),
    0x0168: ("<「#\x04幼き者　砂漠へ行け#\x00」&…だって",0x03),
    0x0169: ("<全部の神殿見つけた？",0x03),
    0x016A: ("<無事だったのネ！",0x03),
    0x016B: ("<#\x02森の賢者#\x00なんて&なりたくなかった…",0x03),
    0x016C: ("<がんばって！",0x03),
    0x016D: ("<ハイラルの平和は&あなたにかかっているわ！",0x03),
    0x0180: ("<「銀ルピー集めろ！」#\x04…だってサ#\x00",0x03),
    0x0181: ("<「冥土への渡し船」#\x04…だってサ#\x00",0x03),
    0x0183: ("<#\x04いつ沈むか分かんないヨ#\x00",0x03),
    0x0184: ("<#\x04どうにか渡れないかな？#\x00",0x03),
    0x0186: ("<赤い氷#\x04なんて変わってるね#\x00",0x03),
    0x0189: ("<青い炎#\x04なんて変わってるね#\x00",0x03),
    0x018C: ("<燭台の火#\x04がなくなってる#\x00",0x03),
    0x018D: ("<燭台の火#\x04が点いたワ！#\x00",0x03),
    0x018F: ("<矢印#\x04が描いてあるよ？#\x00",0x03),
    0x0190: ("<#\x04ねじれてるよぉ～っ！#\x00",0x03),
    0x0191: ("<影#\x04に気をつけて！#\x00",0x03),
    0x0192: ("<箱#\x04があるよ。#\x00",0x03),
    0x0194: ("<燭台#\x04があるヨ#\x00",0x03),
    0x0195: ("<燭台の火#\x04が点いたワ！#\x00",0x03),
    0x0197: ("<スイッチ#\x04凍ってる#\x00",0x03),
    0x0198: ("<天井#\x04に気をつけて！#\x00",0x03),
    0x01A3: ("<ゴロン族の声#\x04がするよ！#\x00",0x03),
    0x01A5: ("<#\x04ここから下が覗けるよ！#\x00",0x03),
    0x01A7: ("<#\x04この#\x00石像#\x04って…#\x00",0x03),
    0x01A9: ("<#\x04このスイッチ錆びてるみたい#\x00",0x03),
    0x01AB: ("<#\x04気をつけて！#\x00",0x03),
    0x0600: ("<#\x01？#\x00",0x20),
    0x0601: ("<ゴーマ&目#\x04を狙って！#\x00",0x20),
    0x0602: ("<ゴーマの卵&#\x04壊して！#\x00",0x20),
    0x0603: ("<幼生ゴーマ&#\x04姿勢に注意！#\x00",0x20),
    0x0604: ("<スタルチュラ&お腹#\x04が弱点！#\x00",0x20),
    0x0605: ("<大スタルチュラ&お腹#\x04が弱点！#\x00",0x20),
    0x0606: ("<テールパサラン&尾#\x04を狙って！#\x00",0x20),
    0x0607: ("<デクババ&デクの棒#\x04になるヨ！#\x00",0x20),
    0x0608: ("<大デクババ&デクの棒#\x04になるヨ！#\x00",0x20),
    0x0609: ("<デクババ&デクの実#\x04になるヨ！#\x00",0x20),
    0x060A: ("<デクナッツ&#\x04木の実を跳ね返せ！#\x00",0x20),
    0x060C: ("<キングドドンゴ&#\x04ショックを与えて！#\x00",0x20),
    0x060D: ("<ドドンゴ&#\x04炎に注意！#\x00",0x20),
    0x060E: ("<ベビードドンゴ&#\x04バクハツするよ！#\x00",0x20),
    0x060F: ("<リザルフォス&#\x04盾を使って！#\x00",0x20),
    0x0610: ("<ダイナフォス&#\x04盾を使って！#\x00",0x20),
    0x0611: ("<ファイアキース&#\x04突っ込む前に倒して！#\x00",0x20),
    0x0612: ("<キース&#\x04接近したらＺ注目！#\x00",0x20),
    0x0613: ("<アモス&#\x04動きをとめて！#\x00",0x20),
    0x0614: ("<バリネード&#\x04本体を狙うの！#\x00",0x20),
    0x0615: ("<触手&#\x04特別な武器が必要#\x00",0x20),
    0x0616: ("<シャボム&#\x04剣を弾くよ！#\x00",0x20),
    0x0617: ("<ビリ&#\x04痺れるヨ！#\x00",0x20),
    0x0618: ("<バリ&#\x04痺れるヨ！#\x00",0x20),
    0x0619: ("<スティンガ&#\x04突っ込む前に倒して！#\x00",0x20),
    0x061A: ("<ファントムガノン&#\x04本物は飛び出すよ！#\x00",0x20),
    0x061B: ("<スタルフォス&#\x04隙を見て攻撃！#\x00",0x20),
    0x061C: ("<青バブル&#\x04炎は盾で防ぐのよ！#\x00",0x20),
    0x061D: ("<白バブル&#\x04停止した時を狙って！#\x00",0x20),
    0x061E: ("<緑バブル&#\x04炎が消えた時をねらうの！#\x00",0x20),
    0x061F: ("<スタルウォール&#\x04触らないで！#\x00",0x20),
    0x0620: ("<スタルチュラ&#\x04倒せばしるしがもらえるよ#\x00",0x20),
    0x0621: ("<ヴァルバジア&#\x04わからないよ…#\x00",0x20),
    0x0622: ("<フレアダンサー&炎の衣#\x04を消すの！#\x00",0x20),
    0x0623: ("<トーチスラグ&#\x04火が消えたら倒しましょ！#\x00",0x20),
    0x0624: ("<赤バブル&#\x04盾で防ぐのよ！#\x00",0x20),
    0x0625: ("<モーファ&核細胞#\x04を引き抜いて攻撃よ！#\x00",0x20),
    0x0626: ("<ダークリンク&#\x04自分に勝つのよ！#\x00",0x20),
    0x0627: ("<シェルブレード&貝柱#\x04が弱点よ！#\x00",0x20),
    0x0628: ("<スパイク&#\x04針を引込めた時を狙って！#\x00",0x20),
    0x0629: ("<ボンゴボンゴ&氷の矢#\x04を撃ってみて！#\x00",0x20),
    0x062A: ("<リーデット&太陽の歌#\x04が弱点！#\x00",0x20),
    0x062B: ("<ファントムガノン&#\x04本物は飛び出すよ！#\x00",0x20),
    0x062D: ("<ギブド&太陽の歌#\x04が弱点！#\x00",0x20),
    0x062E: ("<デドハンドの手&連打#\x04で逃げて！#\x00",0x20),
    0x062F: ("<デドハンド&#\x04頭を狙って！#\x00",0x20),
    0x0630: ("<フォールマスター&影#\x04に気をつけて！#\x00",0x20),
    0x0631: ("<フロアマスター&#\x04分裂した時を狙って！#\x00",0x20),
    0x0632: ("<コウメ&低温#\x04に弱いみたい#\x00",0x20),
    0x0633: ("<コタケ&高温#\x04に弱いみたい#\x00",0x20),
    0x0634: ("<アイアンナック&#\x04斧攻撃に注意#\x00",0x20),
    0x0635: ("<アイアンナック&#\x04斧攻撃に注意#\x00",0x20),
    0x0636: ("<スタルキッド&#\x04大人は嫌いみたい#\x00",0x20),
    0x0637: ("<ライクライク&#\x04食われないようにして！#\x00",0x20),
    0x0639: ("<ビーモス&ケムリ#\x04が目に染みるみたい…#\x00",0x20),
    0x063A: ("<アヌビス&#\x01炎#\x04が弱点！#\x00",0x20),
    0x063B: ("<フリザド&#\x04凍る息に注意！#\x00",0x20),
    0x063D: ("<ガノン&光の矢#\x04が弱点！#\x00",0x20),
    0x063E: ("<ガノン&光の矢#\x04が弱点！#\x00",0x20),
    0x063F: ("<スタルキッド&#\x04きっかけ次第で仲良くなれる？#\x00",0x20),
    0x0640: ("<スタルキッド&#\x04顔が寂しくて悩んでるみたい…#\x00",0x20),
    0x0641: ("<スタルキッド&#\x04ドクロ顔に満足そう！#\x00",0x20),
    0x0642: ("<オクタロック&#\x04石を跳ね返せ！#\x00",0x20),
    0x0643: ("<ポウ&Ｚ#\x04で姿を隠すよ#\x00",0x20),
    0x0644: ("<ポウ&Ｚ#\x04で姿を隠すよ#\x00",0x20),
    0x0645: ("<赤テクタイト&Ｚ#\x04で動きを固めて！#\x00",0x20),
    0x0646: ("<青テクタイト&#\x04陸地へ誘き出そう！#\x00",0x20),
    0x0647: ("<リーバ&#\x04逃げて！#\x00",0x20),
    0x0648: ("<ピーハット&根#\x04が弱点！#\x00",0x20),
    0x0649: ("<幼生ピーハット&盾#\x04で防いで！#\x00",0x20),
    0x064C: ("<ウルフォス&背中#\x04が弱点！#\x00",0x20),
    0x064D: ("<オコリナッツ&#\x04種を跳ね返せ！#\x00",0x20),
    0x064E: ("<アキンドナッツ&#\x04種を跳ね返せ！#\x00",0x20),
    0x064F: ("<ダンペイ&#\x04追っかけよう！#\x00",0x20),
    0x0650: ("<メグ&本物#\x04を探して！#\x00",0x20),
    0x0651: ("<ジョオ&#\x04現われた時を狙って！#\x00",0x20),
    0x0652: ("<ベス&#\x04現われた時を狙って！#\x00",0x20),
    0x0653: ("<エイミー&#\x04現われた時を狙って！#\x00",0x20),
    0x0654: ("<盗賊&背中#\x04が弱点！#\x00",0x20),
    0x0655: ("<スタルベビー&#\x04斬りまくろう！#\x00",0x20),
    0x0656: ("<アイスキース&#\x04突っ込む前に倒して！#\x00",0x20),
    0x0657: ("<ホワイトウルフォス&背中#\x04が弱点！#\x00",0x20),
    0x0658: ("<グエー&#\x04突っ込む前に倒して！#\x00",0x20),
    0x0659: ("<ダイオクタ&#\x04後ろへ回り込んで！#\x00",0x20),
    0x065A: ("<ビッグポウ&#\x04素早いヨ！#\x00",0x20),
    0x065B: ("<ツインローバ&魔法攻撃#\x04を逆利用して！#\x00",0x20),
    0x065C: ("<ポウ&#\x04中々根性のあるポウよ！#\x00",0x20),
}

SHOP_MESSAGES = {
    0x80B2: "<#\x01デクの実（５コ）１５ルピー#\x00&投げると　目つぶしになる。>*O",
    0x807F: "<デクの実（５コ）１５ルピー&:2#\x02かう&やめとく#\x00>",
    0x80C1: "<#\x01矢（３０本）６０ルピー#\x00&弓がない人には　売れません。>*O",
    0x809B: "<矢（３０本）６０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80B0: "<#\x01矢（５０本）９０ルピー#\x00&弓がない人には　売れません。>*O",
    0x807D: "<矢（５０本）９０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80A3: "<#\x01バクダン（５コ）２５ルピー#\x00&ボム袋がないと　買えません。>*O",
    0x808B: "<バクダン（５コ）２５ルピー&:2#\x02かう&やめとく#\x00>",
    0x80A2: "<#\x01デクの実（１０コ）３０ルピー#\x00&投げると　目つぶしになる。>*O",
    0x8087: "<デクの実（１０コ）３０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80A1: "<#\x01デクの棒（１本）１０ルピー#\x00&武器にもなるが、折れます。>*O",
    0x8088: "<デクの棒（１本）１０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80B1: "<#\x01バクダン（１０コ）５０ルピー#\x00&ボム袋がないと　買えません。>*O",
    0x807C: "<バクダン（１０コ）５０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80B3: "<#\x01サカナ　２００ルピー#\x00&ビンに入れて　保存できる。>*O",
    0x807E: "<サカナ　２００ルピー&:2#\x02かう&やめとく#\x00>",
    0x80A5: "<#\x01赤いクスリ　３０ルピー#\x00&飲むと　体力が　回復する。>*O",
    0x808E: "<赤いクスリ　３０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80A6: "<#\x01緑のクスリ　３０ルピー#\x00&飲むと　魔法の力が　回復する。>*O",
    0x808F: "<緑のクスリ　３０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80A9: "<#\x01ハイリアの盾　８０ルピー#\x00&炎攻撃を防ぐ。>*O",
    0x8092: "<ハイリアの盾　８０ルピー&:2#\x02かう&やめとく#\x00>",
    0x809F: "<#\x01デクの盾　４０ルピー#\x00&火がつくと　燃えてしまう。>*O",
    0x8089: "<デクの盾　４０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80AA: "<#\x01ゴロンの服　２００ルピー#\x00&大人専用の　耐火服。>*O",
    0x8093: "<ゴロンの服　２００ルピー&:2#\x02かう&やめとく#\x00>",
    0x80AB: "<#\x01ゾーラの服　３００ルピー#\x00&大人専用の　潜水服。>*O",
    0x8094: "<ゾーラの服　３００ルピー&:2#\x02かう&やめとく#\x00>",
    0x80AC: "<#\x01回復のハート　１０ルピー#\x00&ハート１つ分、体力回復。>*O",
    0x8095: "<回復のハート　１０ルピー&:2#\x02かう&やめとく#\x00>",
    0x8061: "<#\x01ボムチュウ（２０コ）１８０ルピー#\x00&自分で走る　新型バクダン。>*O",
    0x802A: "<ボムチュウ（２０コ）１８０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80DF: "<#\x01デクのタネ（３０コ）３０ルピー#\x00&パチンコがないと　買えません。>*O",
    0x80DE: "<デクのタネ（３０コ）３０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80B9: "<#\x01青い炎　３００ルピー#\x00&あきビンがないと　買えません。>*O",
    0x80B8: "<青い炎　３００ルピー&:2#\x02かう&やめとく#\x00>",
    0x80BB: "<#\x01ムシ　５０ルピー#\x00&あきビンがないと　買えません。>*O",
    0x80BA: "<ムシ　５０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80B7: "<#\x01妖精の魂　５０ルピー#\x00&あきビンがないと　買えません。>*O",
    0x80B6: "<妖精の魂　５０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80A0: "<#\x01矢（１０本）２０ルピー#\x00&弓がない人には　売れません。>>*O",
    0x808A: "<矢（１０本）２０ルピー&:2#\x02かう&やめとく#\x00>",
    0x801C: "<#\x01バクダン（２０コ）３０ルピー#\x00&ボム袋がないと　買えません。>*O",
    0x8006: "<バクダン（２０コ）３０ルピー&:2#\x02かう&やめとく#\x00>",
    0x801D: "<#\x01バクダン（３０コ）１２０ルピー#\x00&ボム袋がないと　買えません。>*O",
    0x801E: "<１２０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80CB: "<#\x01バクダン（５コ）３５ルピー#\x00&ボム袋がないと　買えません。>*O",
    0x80CA: "<バクダン（５コ）３５ルピー&:2#\x02かう&やめとく#\x00>",
    0x8064: "<#\x01赤いクスリ　４０ルピー#\x00&飲むと　体力が　回復する。>*O",
    0x8062: "<赤いクスリ　４０ルピー&:2#\x02かう&やめとく#\x00>",
    0x8065: "<#\x01赤いクスリ　５０ルピー#\x00&飲むと　体力が　回復する。>*O",
    0x8063: "<赤いクスリ　５０ルピー&:2#\x02かう&やめとく#\x00>",
    0x80BD: "<#\x01売り切れ#\x00>*O",
}

COLOR_MAP = {
    'White':      '\x40',
    'Red':        '\x41',
    'Green':      '\x42',
    'Blue':       '\x43',
    'Light Blue': '\x44',
    'Pink':       '\x45',
    'Yellow':     '\x46',
    'Black':      '\x47',
}

COLOR_MAP_JP = {
    'White':      '\x00',
    'Red':        '\x01',
    'Green':      '\x02',
    'Blue':       '\x03',
    'Light Blue': '\x04',
    'Pink':       '\x05',
    'Yellow':     '\x06',
    'Black':      '\x07',
}

MISC_MESSAGES = {
    0x000F:    (None, "<<##\x01大当たり～っ！！{{", 0x03, "center"),
    0x0084:    (None, "<<まいど、どうも！*O", 0x03, "center"),
    0x0085:    (None, "<<ルピーが足りません*O", 0x03, "center"),
    0x0086:    (None, "<<今は買えません*O", 0x03, "center"),
    0x0205:    (None, "<<##\x01ダンペイさん##\x00は&&おネムの　時間だ！", 0x22, "center"),
    0x0206:    (None, "<<##\x01ダンペイさん##\x00は&&おネムの　時間だ！", 0x22, "center"),
    0x0207:    (None, "<<##\x04しあわせのお面屋##\x00&&ぜひ　ご利用下さい。　　　店主", 0x22, "center"),
    0x0227:    (None, "<<だれ！？&&裏口から　入ろうとしてる&&ワルい子は！", 0x02, "center"),
    0x022C:    (None, "<<この地に眠る魂&&ハイラル王家に&&忠誠を誓いし者の魂なり", 0x22, "center"),
    0x0311:    (None, "<<命知らずな方は　ぜひとも&&当店に　お立ち寄りください&&じゅうたん商人", 0x10, "center"),
    0x0329:    (None, "<<##\x04的当て屋　　１回　２０ルピー##\x00", 0x13, "center"),
    0x0337:    (None, "<<##\x05Ｚの穴##\x00", 0x10, "center"),
    0x0340:    (None, "<<注目する相手が　いない時は&&Ｚで　前を見ることができます", 0x10, "center"),
    0x0341:    (None, "<<飛びたい方向に　おもいきって&&走れば　勝手に飛べます", 0x10, "center"),
    0x0343:    (None, "<<##\x01となりの石##\x00は　注目できます", 0x10, "center"),
    0x0344:    (None, "<<##\x02森のステージ##\x00&&ごうか賞品アリ", 0x10, "center"),
    0x1007:    (None, "<<オイラと　れんしゅうしようゼ～！", 0x00, "center"),
    0x100A:    (None, "<<オイラ、サリアんちの&&草かり　やらされてんだヨ。&&ミドのアニキの　命令なんだ～っ！}}\x10\x0B", 0x00, "center"),
    0x100D:    (None, "<<妖精は　人や　物に　向かって&&飛んで行くヨ！", 0x03, "center"),
    0x1015:    (None, "<<リンクよ…&&今、ここで　お前の勇気を&&ためさせてほしい。", 0x03, "center"),
    0x1016:    (None, "<<覚悟は　あるかな…？>>:2##\x02&&はい&&いいえ##\x00", 0x03, "left"),
    0x101C:    (None, "<<ボクに　ソレ　ゆずれよ。>>&&:2##\x02はい&&いやだ##\x00", 0x00, "left"),
    0x1036:    (None, "<<画面右上に　表示される&&３つの　黄色いアイコンは&&##\x06Ｃアイコン##\x00だヨ。", 0x03, "center"),
    0x104D:    (None, "<<$$\x38\x80ピッ！！", 0x03, "center"),
    0x1052:    (None, "<<おニイちゃん、&&デクの盾は　使えないヨ。", 0x00, "center"),
    0x1055:    (None, "<<フーン…　おニイちゃん…&&森に　はいっても　ヘーキなんダ。}}\x10\x56", 0x00, "center"),
    0x1058:    (None, "<<おニイちゃん、旅のヒト？}}\x10\x59", 0x00, "center"),
    0x105B:    (None, "<<おニイちゃん、&&@Nってコ&&知らない？}}\x10\x5C", 0x00, "center"),
    0x105D:    (None, "<<おっきくなって　強くなって…&&デクナッツとか　やっつけたいな。&&でも…}}\x10\x5E", 0x00, "center"),
    0x1060:    (None, "<<なんだ、オマエ！？", 0x00, "center"),
    0x1062:    (None, "<<ボク、##\x01デクの樹のこども##\x00　デス！", 0x00, "center"),
    0x1070:    (None, "<<@Nが　帰ってきたら&&サリアが　ずっと　待ってたこと…&&ぜったい　おしえてやる！}}\x10\x71", 0x00, "center"),
    0x109A:    (None, "<<…なんだっけ", 0x03, "center"),
    0x10A8:    (None, "<<ここで　あの曲　ふくと&&妖精たちと　お話しできるのよ。}}\\x10\\xA9", 0x03, "center"),
    0x10AB:    (None, "<<そんなこと　言わないで　やろ～よ！", 0x03, "center"),
    0x10B0:    (None, "<<サリアのコトなら&&ミドが　知ってるかもネ。", 0x00, "center"),
    0x10B8:    (None, "<<返して！:2##\x02&&はい&&いいえ##\x00", 0x00, "left"),
    0x10C1:    (None, "<<この　迷いの森を　ぬけると&&そこは　##\x02森の聖域##\x00。", 0x03, "center"),
    0x10C9:    (None, "<<もしものコトも　あるし、&&武器は　あったほうが　いいわネ。}}\x10\x32", 0x00, "center"),
    0x10D0:    (None, "<<なに～っ！？&&デクの樹サマに　呼ばれたって？}}\\x10\\xD1", 0x00, "center"),
    0x10D2:    (None, "<<なんだ、##\x04デクの盾##\x00つけてるじゃん。&&そ…　それ、「##\x02コキリの剣##\x00」？&&ちっくしょーっ！！}}\\x10\\xD3", 0x00, "center"),
    0x10D3:    (None, "<<でもヨ、そんなモン　持ってたって&&ヨワいやつは　ヨワいんだかんナ！}}\x10\x32", 0x00, "center"),
    0x10D6:    (None, "<<それから　ついでに…&&イジワルして…&&ゴメン！　って…サ。", 0x00, "center"),
    0x10D8:    (None, "<<見て、イイけしきでしょ？", 0x00, "center"),
    0x200D:    (None, "<<ぼーやにゃ　世話になったから、&&ウチのじまんの##\x01これ##\x00　やるだーよ。", 0x03, "center"),
    0x202E:    (None, "$$\x48\x07<<もらった分から&&お面の代金　##\x01５０ルピー##\x00だけを　&&お面屋に　納めに　戻ろう。", 0x23, "center"),
    0x2032:    (None, "<<そうかい。", 0x00, "center"),
    0x2039:    (None, "<<金のないヤツとは　勝負できね～な！", 0x00, "center"),
    0x2040:    (None, "<<あ～あ　雇われ人は　辛いよな。", 0x00, "center"),
    0x2042:    (None, "<<マロンはネ、とーさん　まってるの。&&とーさん、お城に牛乳届けに&&入ったまま　出てこないんダ…", 0x00, "center"),
    0x2046:    (None, "<<怠け者のタロンのオヤジより&&この##\x01インゴー様##\x00の方が　牧場の&&オーナーにゃ相応しいよナ。", 0x00, "center"),
    0x2057:    (None, "<<ＺＺＺＺＺＺＺＺ…", 0x00, "center"),
    0x207E:    (None, "<<この##\x01スーパーコッコ##\x00　３羽を&&普通のコッコの中に　投げこむだ。^^<<ぜんぶ　見つけたら　ぼうやの勝ち！&&##\x01イイもの##\x00　やるだーよ。^^<<１０ルピーもらうけど、やる？>>&&:2##\x02はい&&いいえ##\x00", 0x00, "left"),
    0x207F:    (None, "<<この##\x01スーパーコッコ##\x00　３羽を&&普通のコッコの中に　投げこむだ。^^<<ぜんぶ　見つけたら　ぼうやの勝ち！&&##\x01イイもの##\x00　やるだーよ。^^<<１０ルピーもらうけど、やる？>>&&:2##\x02はい&&いいえ##\x00", 0x00, "left"),
    0x2084:    (None, "<<それで　ぜんぶ　だーよ！&&こっちへ　おいで。{{", 0x00, "center"),
    0x2085:    (None, "<<も一度　ちょ～せんするだーか？^^<<１回　５ルピーで　やる？>>&&:2##\x02はい&&いいえ##\x00", 0x00, "left"),
    0x2086:    (None, "<<マロンのムコさんにならね～だか？>>&&:2##\x02はい&&いいえ##\x00", 0x00, "left"),
    0x2087:    (None, "<<いや～　じょーだん　じょーだん！&&約束どおり##\x01イイもの##\x00やるだーよ！{{", 0x00, "center"),
    0x2088:    (None, "<<おっきくなったら　この牧場で&&はたらかねえだか？&&いつでも　待ってるだーよ。{{", 0x00, "center"),
    0x2089:    (None, "<<ほら、とれとれの&&##\x01ロンロン牛乳##\x00　持って行くだ！{{", 0x00, "center"),
    0x208A:    (None, "<<ざんねんだーよ。&&からのビンが　ないだーよ。", 0x00, "center"),
    0x208B:    (None, ":3##\x02ロンロン牛乳　　　３０ルピー&&コッコ当てゲーム　１０ルピー&&やめる##\x00", 0x00, "left"),
    0x208E:    (None, "<<もう一度　挑戦するなら&&エポナに乗って　準備して！", 0x00, "center"),
    0x208F:    (None, "<<やったわネ　@N！&&##\x01@R##\x00、新記録よ！", 0x00, "center"),
    0x2090:    (None, "<<これまでの記録は　##\x01５０秒##\x00。&&キミの記録は　##\x01@H\x03##\x00。&&じゃ、始めるヨ！{{", 0x00, "center"),
    0x2091:    (None, "<<記録は　キミの　##\x01@H\x03##\x00。&&じゃ、始めるヨ！{{", 0x00, "center"),
    0x2092:    (None, "<<これまでの記録は　##\x01５０秒##\x00。&&じゃ、始めるヨ！{{", 0x00, "center"),
    0x507B:    (bytearray(b'\x08I tell you, I saw him!\x04\x08I saw the ghostly figure of Damp\x96\x01the gravekeeper sinking into\x01his grave. It looked like he was\x01holding some kind of \x05\x41treasure\x05\x40!\x02'), "<<オレ、ほんとに　見たんだよ！&&墓守りダンペイが##\x01お宝##\x00を持って&&自分の墓の中に消えてくのをサ…", 0x00, "center"),
    0x502D:    (None, "<<やるな　ニイチャン！&&オラの足に　ついてこれるとは&&イイ走りしてるじゃネェか、ヘヘヘ！", 0x00, "center"),
    0x503B:    (None, "<<コッコ　つかまえてくれて&&ありがとう！&&おれいに　コレあげる！{{", 0x00, "center"),
    0x3017:    (None, "<<今、アニキは…&&自分の部屋に　閉じこもってるゴロ。", 0x00, "center"),
    0x3019:    (None, "<<そういえば　アニキ　よく&&##\x02森から流れてくる歌##\x00を&&聞いてたゴロなあ…}}\x30\x2C", 0x00, "center"),
    0x3020:    (None, "<<う～ん、ちょっとちがうゴロ…", 0x03, "center"),
    0x3022:    (None, "<<棒に火を点けたままにしとくと&&燃え尽きてなくなるゴロよ。", 0x00, "center"),
    0x3025:    (None, "<<投げて落とせば　よかったのね…", 0x00, "center"),
    0x302A:    (None, "<<このあたりの話を　聞きたいなら&&オラたちの町に　行けばいいゴロ。", 0x00, "center"),
    0x302F:    (None, "<<オマエ、この穴の奥から&&聞こえてくる曲、知ってるゴロ？&&オラたち　コレが　お気に入りゴロ。", 0x00, "center"),
    0x3034:    (None, "<<なにを　聞く？:2##\x02&&リュウについて&&ゴロンたちについて##\x00", 0x20, "left"),
    0x3038:    (None, "<<##\x01神サマの像##\x00を　うごかすコロ！", 0x00, "center"),
    0x3042:    (None, "<<オラも　おっきくなったら&&つよ～いオトコに　なるコロ！", 0x00, "center"),
    0x304B:    (None, "<<５、６年　待ってほしいゴロ。", 0x00, "center"),
    0x3056:    (None, "<<あぁ～&&もう　だめゴロォ～！", 0x03, "center"),
    0x3063:    (None, "<<近くへ来て　足につかまりなさい。&&さあ、勇気を出して。　ホホ～ッ！", 0x00, "center"),
    0x4003:    (None, "<<いっしょに　くるなら&&私に　つかまりなさい。", 0x03, "center"),
    0x4004:    (None, "<<いっしょに　くるなら&&私に　つかまりなさい。", 0x00, "center"),
    0x4009:    (None, "<<ジャブジャブさまは　ゾーラの神。&&お食事のしたくは&&##\x01ルト姫サマ##\x00の　担当だったんだ。", 0x00, "center"),
    0x0422:    ("They say that once \x05\x41Morpha's Curse\x05\x40\x01is lifted, striking \x05\x42this stone\x05\x40 can\x01shift the tides of \x05\x44Lake Hylia\x05\x40.\x02", "<<##\x01モーファの呪い##\x00が　解けた後、&&##\x01この岩##\x00をたたくと　ハイリア湖の&&水位が変わるらしい。", 0x23, "center"),
    0x4012:    (None, "<<余の　感謝の気持ちとして&&##\x01これ##\x00を　さずけよう！", 0x03, "center"),
    0x4013:    (None, "<<ルト姫は　ハイリア湖を&&調べたいと　言っておったゾラ…&&心配だゾラ…", 0x03, "center"),
    0x401B:    (None, "<<おー、その手紙は！？&&##\x01ルト姫の手紙##\x00ゾラ！！^^<<入っていた##\x01ビン##\x00は、そちにやるから&&ありがたく　受け取るゾラ！}}\x40\x1C", 0x03, "center"),
    0x401C:    ("Please find my dear \05\x41Princess Ruto\x05\x40\x01immediately... Zora!\x12\x68\x7A", "<<はやく、余の　かわいい　##\x01ルト姫##\x00を&&見つけ出してきてくれぃ…ゾラ！$$\x68\x7A", 0x23, "center"),
    0x4022:    (None, "<<チョッピリ…&&ココロぼそかったゾラ…", 0x00, "center"),
    0x405F:    (None, "<<１つぶ　##\x01２０ルピー##\x00　でどう？:2##\x02&&かう&&やめとく##\x00", 0x00, "left"),
    0x4060:    (None, "<<１つぶ　##\x01３０ルピー##\x00　でどう？:2##\x02&&かう&&やめとく##\x00", 0x00, "left"),
    0x4061:    (None, "<<１つぶ　##\x01４０ルピー##\x00　でどう？:2##\x02&&かう&&やめとく##\x00", 0x00, "left"),
    0x4062:    (None, "<<１つぶ　##\x01５０ルピー##\x00　でどう？:2##\x02&&かう&&やめとく##\x00", 0x00, "left"),
    0x4063:    (None, "<<１つぶ　##\x01６０ルピー##\x00　でどう？:2##\x02&&かう&&やめとく##\x00", 0x00, "left"),
    0x4064:    (None, "<<１つぶ　##\x01７０ルピー##\x00　でどう？:2##\x02&&かう&&やめとく##\x00", 0x00, "left"),
    0x4065:    (None, "<<１つぶ　##\x01８０ルピー##\x00　でどう？:2##\x02&&かう&&やめとく##\x00", 0x00, "left"),
    0x4066:    (None, "<<１つぶ　##\x01９０ルピー##\x00　でどう？:2##\x02&&かう&&やめとく##\x00", 0x00, "left"),
    0x4067:    (None, "<<１つぶ　##\x01１００ルピー##\x00　でどう？:2##\x02&&かう&&やめとく##\x00", 0x00, "left"),
    0x5011:    (None, "<<もう一度　聞く？:2##\x02&&はい&&いいえ##\x00", 0x00, "left"),
    0x5015:    (None, "<<ＺＺＺ…", 0x00, "center"),
    0x501C:    (None, "<<@N、&&大変なことに　なった…&&##\x01闇の魔物##\x00が　復活したんだ！", 0x03, "center"),
    0x5041:    (None, "<<こう見えても　オラは　自信あり！&&ココで　オラと　競争するだ。&&ついてこれるもんなら　ついてきな！", 0x00, "center"),
    0x5046:    (None, "<<魔法使いの　バアちゃんも&&裏で　クスリ屋　やってるんだ。{{", 0x03, "center"),
    0x5054:    (None, "<<もう　おりたくありませ～ん！", 0x00, "center"),
    0x5058:    (None, "<<もし、ニワトリのコトで　何か&&ねーちゃんに頼まれたら&&聞いてやれよ。", 0x03, "center"),
    0x505A:    (None, "<<このコ、ニワトリの世話してるけど&&本当は　トリアレルギーなんだぜ。", 0x03, "center"),
    0x505F:    (None, "<<インパ様は　いらっしゃらないよ。", 0x03, "center"),
    0x5061:    (None, "<<あそこで寝てる&&ヒゲのオヤジさんにも&&色々あるんだよ、きっと。", 0x03, "center"),
    0x5067:    (None, "<<ピン　ポン　パン　ポン！&&ただいま　@T　です。", 0x00, "center"),
    0x508D:    (None, "<<リチャードちゃんを　知らない？&&有名な　おイヌちゃん　ザマス！&&ほんとに　知らないザマスか？", 0x03, "center"),
    0x6019:    (None, "<<なんで　こんなとこに　きたんだい？&&ま…アタイも言えないけどサ。}}\x60\x1A", 0x00, "center"),
    0x6023:    (None, "<<アタイは、ゲルド族の　##\x01ナボール##\x00。&&一匹オオカミの　盗賊さ。}}\x60\x24", 0x00, "center"),
    0x6044:    (None, "<<信じられない！！&&お前こそ　究極の達人だ。&&達人に　ふさわしい武具を与えよう！", 0x00, "center"),
    0x6046:    (None, "<<素晴らしい！！&&お前こそ　真の達人。&&達人に　ふさわしい物を与えよう！", 0x00, "center"),
    0x605B:    (None, "<<もう、ゲルドなんて　コリゴリ！&&あと##\x01３人##\x00、仲間が　捕まってるから&&助けてやってね。　たのんだわよ！", 0x00, "center"),
    0x605C:    (None, "<<もう　こんなとこ　サヨナラよ！&&あと##\x01２人##\x00、仲間が　捕まってるから&&助けてやってね。　たのむわね！", 0x00, "center"),
    0x605D:    (None, "<<はやく　かえって　安心させなきゃ。&&あと##\x01１人##\x00、仲間が　捕まってるから&&助けてやってね。　おねがいね！", 0x00, "center"),
    0x605E:    (None, "<<アタイだけ　忘れられたんじゃ&&ないかと　思ったわ。　よかった！", 0x00, "center"),
    0x6062:    (None, "<<今じゃ、ナボールの盗賊団は&&冷酷・非情・残忍の代名詞。&&義賊なんて　聞いてあきれるわ。", 0x03, "center"),
    0x6065:    (None, "<<砦で　やぶさめに挑戦してみた？&&自分の馬が　あるなら&&砦で　受け付けてるわよ。", 0x03, "center"),
    0x606B:    (None, "<<ゲルドの砦へ　行くなら&&オレっちの仲間の　様子を&&見てきてくれねぇか？", 0x00, "center"),
    0x607A:    (None, "<<この先　おまえの勇気に&&ハイラルの　すべての民の&&未来が　かかっておる。}}\x60\x7B", 0x03, "center"),
    0x607C:    (None, "<<ワシは　お前を見守ってゆく&&今までも…　これからもな…&&ホホ～ッ！", 0x03, "center"),
    0x7004:    (None, "<<たいくつだ…&&もっと　世の中に　モメごとが&&あるほうが　楽しいぜ、きっと…", 0x00, "center"),
    0x7019:    (None, "<<城の右奥に　忍び込めそうな&&##\x01小さな水路##\x00を　見つけたけど&&抜けらんなくなったんだ～！", 0x00, "center"),
    0x701D:    (None, "<<##\x04時の神殿##\x00って　知ってる？}}\x70\x1E", 0x00, "center"),
    0x701E:    (None, "<<時の神殿は　聖地への入口だ、という&&言い伝えが　あるのよ。", 0x00, "center"),
    0x7020:    (None, "<<このバカのせいで　お城の警備が&&キビしく　なったんだぜ！", 0x00, "center"),
    0x7028:    (None, "<<##\x01ゼルダ姫##\x00に　お会いしたいだと？^^<<かえれ！　かえれ！&&姫がお前のような者に&&お会いになるわけないわ！", 0x00, "center"),
    0x7037:    (None, "<<そう…　時の神殿とは、&&この地上から　聖地へ入るための&&入口なのです。{{", 0x03, "center"),
    0x70F4:    (None, "<<ニイさんも&&ポウを　つかまえてきたら&&高く　買ってやるよ。　イーッヒッヒ！", 0x00, "center"),
    0x70FC:    (None, "<<わたし、夢を　見たのです。&&##\x02みどりに光る石##\x00を　かかげた&&人の姿に　変わったのです。{{", 0x03, "center"),
    0x7123:    (None, "<<よかった。あなたが　来てくれて…{{", 0x03, "center"),
    0x71AF:    (None, "<<パーフェクト～ッ！！！{{", 0x00, "center"),
    0x9100:    ("I am out of goods now.\x01Sorry!\x04The mark that will lead you to\x01the Spirit Temple is the \x05\x41flag on\x01the left \x05\x40outside the shop.\x01Be seeing you!\x02", "<<マタ　来テネ～。", 0x00, "center"),
}


# convert byte array to an integer
def bytes_to_int(bytes, signed=False):
    return int.from_bytes(bytes, byteorder='big', signed=signed)


# convert int to an array of bytes of the given width
def int_to_bytes(num, width, signed=False):
    return int.to_bytes(num, width, byteorder='big', signed=signed)

# convert text to an array of bytes of the given width
def text_to_bytes(text, width, signed=False):
    text = text.replace(r"\x" or r"0x" or "\\x", "")
    num = int(text, 16)
    n = width
    try:
        a = int.to_bytes(num, n, byteorder='big', signed=signed)
    except OverflowError:
        raise(TypeError("%s %s" % (text,width)))
    return int.to_bytes(num, n, byteorder='big', signed=signed)
    
def display_code_list(codes):
    message = ""
    for code in codes:
        message += str(code)
    return message


def encode_text_string(text):
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

# mode: 0 normal, 1 scrub, 2 item
def JPencode(text, mode = 0, replace_chars=True):
    rawtext = text
    if replace_chars:
        if mode == 0:
            for char in CONTROL_CHARS_JP.values():
                text = text.replace(char[0],char[1])
        elif mode == 1:
            for char in CONTROL_CHARS_JP.values():
                text = text.replace(char[0],char[1])
        elif mode == 2:
            for char in CONTROL_CHARS_JP_1.values():
                text = text.replace(char[0],char[1])
    jp_text = (''.join([r'\x{:02x}'.format(x) for x in text.encode('cp932')]))
    if mode == 0:
        for char in IGNORE_CHARS.values():
            jp_text = jp_text.replace(char[0],char[1])
    elif mode == 1:
        for char in IGNORE_CHARS_1.values():
            jp_text = jp_text.replace(char[0],char[1])
    elif mode == 2:
        for char in IGNORE_CHARS.values():
            jp_text = jp_text.replace(char[0],char[1])
    while r'\x5c\x78' in jp_text:
        splitText = jp_text.split(r'\x5c\x78',1)
        a = splitText[1][0:4]
        b = splitText[1][4:8]
        c = splitText[1][8:]
        for num in NUMBERS.values():
            if num[0] == a:
                a = num[1]
            if num[0] == b:
                b = num[1]
        splitText[1] = r'\x' + a + b + c
        jp_text = ''.join(splitText)
    return (jp_text)
 
def name_replace(text):
    if r"\x86\xc7" in text:
        split = text.split(r"\x86\xc7\x00")
        p = 1
        while p <= text.count(r"\x86\xc7"):
            i = split[p].count(r"\x83\x8a\x83\x93\x83\x4e") + split[p].count(r"\x82\xe8\x82\xf1\x82\xad") + split[p].count(r"\x82\xa0\x82\xc8\x82\xbd") + split[p].count(r"\x83\x41\x83\x69\x83\x5e")
            split[p] = split[p].replace(r"\x83\x8a\x83\x93\x83\x4e",r"\x87\x4f")
            split[p] = split[p].replace(r"\x82\xe8\x82\xf1\x82\xad",r"\x87\x4f")
            split[p] = split[p].replace(r"\x82\xa0\x82\xc8\x82\xbd",r"\x87\x4f")
            split[p] = split[p].replace(r"\x83\x41\x83\x69\x83\x5e",r"\x87\x4f")
            f = split[p][:4]
            num = int(f.replace("\\x",""), 16)
            new_num = format(num - (40 * i),"02x")
            if "-" in new_num:
                split[p] = split[p][4:]
            else:
                new_f = r"\x86\xc7\x00\x{}".format(new_num)
                split[p] = new_f + split[p][4:]
            p += 1
        text = "".join(split)
    return text
    
def parse_control_codes(text):
    if isinstance(text, list):
        bytes = text
    elif isinstance(text, bytearray):
        bytes = list(text)
    else:
        bytes = encode_text_string(text)

    text_codes = []
    index = 0
    while index < len(bytes):
        next_char = bytes[index]
        data = 0
        index += 1
        if next_char in CONTROL_CODES:
            extra_bytes = CONTROL_CODES[next_char][1]
            if extra_bytes > 0:
                data = bytes_to_int(bytes[index : index + extra_bytes])
                index += extra_bytes
        text_code = Text_Code(next_char, data)
        text_codes.append(text_code)
        if text_code.code == 0x02:  # message end code
            break

    return text_codes

def jp_start(rom, mode = 0):
    NULLTEXT = bytes([0x00] * JPN_TEXT_SIZE_LIMIT)
    rom.write_bytes(TEXT_START_JP,NULLTEXT)
    NULLTABLE = bytes([0x00] * JPN_TABLE_SIZE)
    if mode == 1:
        rom.write_bytes(EXTENDED_TABLE_START,NULLTABLE)
    lines = open(local_path('textJP.py'),encoding='utf-8').readlines()
    NewLines = []
    increments = 1

    for line in lines:
        a = ("  '" + str(increments) + "'")
        NewLines.append(line.replace(' :',a))
        increments += 1
        
    with open(temporal,"w",encoding="utf-8")as new:
        new.write(''.join(NewLines))

        
    with open(temporal,'a') as new:
        new.write("\n")
        new.write("MESTEXT = {\n")

# holds a single character or control code of a string
class Text_Code:
    def display(self):
        if self.code in CONTROL_CODES:
            return CONTROL_CODES[self.code][2](self.data)
        elif self.code in SPECIAL_CHARACTERS:
            return SPECIAL_CHARACTERS[self.code]
        elif self.code >= 0x7F:
            return '?'
        else:
            return chr(self.code)

    def get_python_string(self):
        if self.code in CONTROL_CODES:
            ret = ''
            subdata = self.data
            for _ in range(0, CONTROL_CODES[self.code][1]):
                ret = ('\\x%02X' % (subdata & 0xFF)) + ret
                subdata = subdata >> 8
            ret = '\\x%02X' % self.code + ret
            return ret
        elif self.code in SPECIAL_CHARACTERS:
            return '\\x%02X' % self.code
        elif self.code >= 0x7F:
            return '?'
        else:
            return chr(self.code)

    def get_string(self):
        if self.code in CONTROL_CODES:
            ret = ''
            subdata = self.data
            for _ in range(0, CONTROL_CODES[self.code][1]):
                ret = chr(subdata & 0xFF) + ret
                subdata = subdata >> 8
            ret = chr(self.code) + ret
            return ret
        else:
            # raise ValueError(repr(REVERSE_MAP))
            return REVERSE_MAP[self.code]

    # writes the code to the given offset, and returns the offset of the next byte
    def size(self):
        size = 1
        if self.code in CONTROL_CODES:
            size += CONTROL_CODES[self.code][1]
        return size

    # writes the code to the given offset, and returns the offset of the next byte
    def write(self, rom, offset):
        rom.write_byte(TEXT_START + offset, self.code)

        extra_bytes = 0
        if self.code in CONTROL_CODES:
            extra_bytes = CONTROL_CODES[self.code][1]
            bytes_to_write = int_to_bytes(self.data, extra_bytes)
            rom.write_bytes(TEXT_START + offset + 1, bytes_to_write)

        return offset + 1 + extra_bytes

    def __init__(self, code, data):
        self.code = code
        if code in CONTROL_CODES:
            self.type = CONTROL_CODES[code][0]
        else:
            self.type = 'character'
        self.data = data

    __str__ = __repr__ = display


# holds a single message, and all its data
class Message:
    def display(self):
        meta_data = [
            "#" + str(self.index),
            "ID: 0x" + "{:04x}".format(self.id),
            "Offset: 0x" + "{:06x}".format(self.offset),
            "Length: 0x" + "{:04x}".format(self.unpadded_length) + "/0x" + "{:04x}".format(self.length),
            "Box Type: " + str(self.box_type),
            "Postion: " + str(self.position)
        ]
        return ', '.join(meta_data) + '\n' + self.text

    def get_python_string(self):
        ret = ''
        for code in self.text_codes:
            ret = ret + code.get_python_string()
        return ret

    # check if this is an unused message that just contains it's own id as text
    def is_id_message(self):
        if self.unpadded_length != 5:
            return False
        for i in range(4):
            code = self.text_codes[i].code
            if not (
                    code in range(ord('0'), ord('9')+1)
                    or code in range(ord('A'), ord('F')+1)
                    or code in range(ord('a'), ord('f')+1)
            ):
                return False
        return True

    def parse_text(self):
        self.text_codes = parse_control_codes(self.raw_text)

        index = 0
        for text_code in self.text_codes:
            index += text_code.size()
            if text_code.code == 0x02:  # message end code
                break
            if text_code.code == 0x07:  # goto
                self.has_goto = True
                self.ending = text_code
            if text_code.code == 0x0A:  # keep-open
                self.has_keep_open = True
                self.ending = text_code
            if text_code.code == 0x0B:  # event
                self.has_event = True
                self.ending = text_code
            if text_code.code == 0x0E:  # fade out
                self.has_fade = True
                self.ending = text_code
            if text_code.code == 0x10:  # ocarina
                self.has_ocarina = True
                self.ending = text_code
            if text_code.code == 0x1B:  # two choice
                self.has_two_choice = True
            if text_code.code == 0x1C:  # three choice
                self.has_three_choice = True
        self.text = display_code_list(self.text_codes)
        self.unpadded_length = index

    def is_basic(self):
        return not (self.has_goto or self.has_keep_open or self.has_event or self.has_fade or self.has_ocarina or self.has_two_choice or self.has_three_choice)

    # computes the size of a message, including padding
    def size(self):
        size = 0

        for code in self.text_codes:
            size += code.size()

        size = (size + 3) & -4 # align to nearest 4 bytes

        return size
    
    # applies whatever transformations we want to the dialogs
    def transform(self, replace_ending=False, ending=None, always_allow_skip=True, speed_up_text=True):
        ending_codes = [0x02, 0x07, 0x0A, 0x0B, 0x0E, 0x10]
        box_breaks = [0x04, 0x0C]
        slows_text = [0x08, 0x09, 0x14]

        text_codes = []

        # # speed the text
        if speed_up_text:
            text_codes.append(Text_Code(0x08, 0)) # allow instant

        # write the message
        for code in self.text_codes:
            # ignore ending codes if it's going to be replaced
            if replace_ending and code.code in ending_codes:
                pass
            # ignore the "make unskippable flag"
            elif always_allow_skip and code.code == 0x1A:
                pass
            # ignore anything that slows down text
            elif speed_up_text and code.code in slows_text:
                pass
            elif speed_up_text and code.code in box_breaks:
                # some special cases for text that needs to be on a timer
                if (self.id == 0x605A or  # twinrova transformation
                    self.id == 0x706C or  # raru ending text
                    self.id == 0x70DD or  # ganondorf ending text
                    self.id == 0x7070
                ):   # zelda ending text
                    text_codes.append(code)
                    text_codes.append(Text_Code(0x08, 0))  # allow instant
                else:
                    text_codes.append(Text_Code(0x04, 0))  # un-delayed break
                    text_codes.append(Text_Code(0x08, 0))  # allow instant
            else:
                text_codes.append(code)

        if replace_ending:
            if ending:
                if speed_up_text and ending.code == 0x10:  # ocarina
                    text_codes.append(Text_Code(0x09, 0))  # disallow instant text
                text_codes.append(ending)  # write special ending
            text_codes.append(Text_Code(0x02, 0))  # write end code

        self.text_codes = text_codes

    # writes a Message back into the rom, using the given index and offset to update the table
    # returns the offset of the next message
    def write(self, rom, index, offset):
        # construct the table entry
        id_bytes = int_to_bytes(self.id, 2)
        offset_bytes = int_to_bytes(offset, 3)
        entry = id_bytes + bytes([self.opts, 0x00, 0x07]) + offset_bytes
        # write it back
        entry_offset = EXTENDED_TABLE_START + 8 * index
        rom.write_bytes(entry_offset, entry)

        for code in self.text_codes:
            offset = code.write(rom, offset)

        while offset % 4 > 0:
            offset = Text_Code(0x00, 0).write(rom, offset) # pad to 4 byte align

        return offset


    def __init__(self, raw_text, index, id, opts, offset, length):
        self.raw_text = raw_text

        self.index = index
        self.id = id
        self.opts = opts  # Textbox type and y position
        self.box_type = (self.opts & 0xF0) >> 4
        self.position = (self.opts & 0x0F)
        self.offset = offset
        self.length = length

        self.has_goto = False
        self.has_keep_open = False
        self.has_event = False
        self.has_fade = False
        self.has_ocarina = False
        self.has_two_choice = False
        self.has_three_choice = False
        self.ending = None

        self.parse_text()

    # read a single message from rom
    @classmethod
    def from_rom(cls, rom, index):
        entry_offset = ENG_TABLE_START + 8 * index
        entry = rom.read_bytes(entry_offset, 8)
        next = rom.read_bytes(entry_offset + 8, 8)

        id = bytes_to_int(entry[0:2])
        opts = entry[2]
        offset = bytes_to_int(entry[5:8])
        length = bytes_to_int(next[5:8]) - offset

        raw_text = rom.read_bytes(TEXT_START + offset, length)

        return cls(raw_text, index, id, opts, offset, length)

    @classmethod
    def from_string(cls, text, id=0, opts=0x00):
        bytes = text + "\x02"
        return cls(bytes, 0, id, opts, 0, len(bytes) + 1)

    @classmethod
    def from_bytearray(cls, bytearray, id=0, opts=0x00):
        bytes = list(bytearray) + [0x02]

        return cls(bytes, 0, id, opts, 0, len(bytes) + 1)

    __str__ = __repr__ = display

# wrapper for updating the text of a message, given its message id
# if the id does not exist in the list, then it will add it
def update_message_by_id(messages, id, text, opts=None):
    # get the message index
    index = next( (m.index for m in messages if m.id == id), -1)
    # update if it was found
    if index >= 0:
        update_message_by_index(messages, index, text, opts)
    else:
        add_message(messages, text, id, opts)

# Gets the message by its ID. Returns None if the index does not exist
def get_message_by_id(messages, id):
    # get the message index
    index = next( (m.index for m in messages if m.id == id), -1)
    if index >= 0:
        return messages[index]
    else:
        return None

# wrapper for updating the text of a message, given its index in the list
def update_message_by_index(messages, index, text, opts=None):
    if opts is None:
        opts = messages[index].opts

    if isinstance(text, bytearray):
        messages[index] = Message.from_bytearray(text, messages[index].id, opts)
    else:
        messages[index] = Message.from_string(text, messages[index].id, opts)
    messages[index].index = index

# wrapper for adding a string message to a list of messages
def add_message(messages, text, id=0, opts=0x00):
    if isinstance(text, bytearray):
        messages.append( Message.from_bytearray(text, id, opts) )
    else:
        messages.append( Message.from_string(text, id, opts) )
    messages[-1].index = len(messages) - 1

messages = []
def update_message_jp(messages, id, text, opts=None, mode = 0, align = "left"):
    if mode == 0:
        text = linewrapJP(text, 0, align)
        text = text + "|"
        jptext = (JPencode(text))
    elif mode == 1:
        text = linewrapJP(text, 0, align)
        text = text + "|"
        jptext = (JPencode(text, 1))
    elif mode == 2:
        text = linewrapJP(text, 1, align)
        text = text + "||"
        jptext = (JPencode(text, 2))
    jptext = name_replace(jptext)
    with open(temporal,'a') as new:
        new.write('    0x')
        new.write(str(f'{id:04x}'))
        new.write(":    (r'")
        new.write((jptext))
        new.write("', ")
        if opts is None:
            new.write("None, '")
        else:
            new.write('0x')
            new.write(str(f'{opts:02x}'))
            new.write(", '")
        new.write(parsejp(jptext, 0))
        new.write("', '")
        new.write(parsejp(jptext, 1))
        new.write("'),\n")
  
# holds a row in the shop item table (which contains pointers to the description and purchase messages)
class Shop_Item():

    def display(self):
        meta_data = ["#" + str(self.index),
         "Item: 0x" + "{:04x}".format(self.get_item_id),
         "Price: " + str(self.price),
         "Amount: " + str(self.pieces),
         "Object: 0x" + "{:04x}".format(self.object),
         "Model: 0x" + "{:04x}".format(self.model),
         "Description: 0x" + "{:04x}".format(self.description_message),
         "Purchase: 0x" + "{:04x}".format(self.purchase_message),]
        func_data = [
         "func1: 0x" + "{:08x}".format(self.func1),
         "func2: 0x" + "{:08x}".format(self.func2),
         "func3: 0x" + "{:08x}".format(self.func3),
         "func4: 0x" + "{:08x}".format(self.func4),]
        return ', '.join(meta_data) + '\n' + ', '.join(func_data)

    # write the shop item back
    def write(self, rom, shop_table_address, index):

        entry_offset = shop_table_address + 0x20 * index

        bytes = []
        bytes += int_to_bytes(self.object, 2)
        bytes += int_to_bytes(self.model, 2)
        bytes += int_to_bytes(self.func1, 4)
        bytes += int_to_bytes(self.price, 2, signed=True)
        bytes += int_to_bytes(self.pieces, 2)
        bytes += int_to_bytes(self.description_message, 2)
        bytes += int_to_bytes(self.purchase_message, 2)
        bytes += [0x00, 0x00]
        bytes += int_to_bytes(self.get_item_id, 2)
        bytes += int_to_bytes(self.func2, 4)
        bytes += int_to_bytes(self.func3, 4)
        bytes += int_to_bytes(self.func4, 4)

        rom.write_bytes(entry_offset, bytes)

    # read a single message
    def __init__(self, rom, shop_table_address, index):

        entry_offset = shop_table_address + 0x20 * index
        entry = rom.read_bytes(entry_offset, 0x20)

        self.index = index
        self.object = bytes_to_int(entry[0x00:0x02])
        self.model = bytes_to_int(entry[0x02:0x04])
        self.func1 = bytes_to_int(entry[0x04:0x08])
        self.price = bytes_to_int(entry[0x08:0x0A])
        self.pieces = bytes_to_int(entry[0x0A:0x0C])
        self.description_message = bytes_to_int(entry[0x0C:0x0E])
        self.purchase_message = bytes_to_int(entry[0x0E:0x10])
        # 0x10-0x11 is always 0000 padded apparently
        self.get_item_id = bytes_to_int(entry[0x12:0x14])
        self.func2 = bytes_to_int(entry[0x14:0x18])
        self.func3 = bytes_to_int(entry[0x18:0x1C])
        self.func4 = bytes_to_int(entry[0x1C:0x20])

    __str__ = __repr__ = display

# reads each of the shop items
def read_shop_items(rom, shop_table_address):
    shop_items = []

    for index in range(0, 100):
        shop_items.append( Shop_Item(rom, shop_table_address, index) )

    return shop_items

# writes each of the shop item back into rom
def write_shop_items(rom, shop_table_address, shop_items):
    for s in shop_items:
        s.write(rom, shop_table_address, s.index)

# these are unused shop items, and contain text ids that are used elsewhere, and should not be moved
SHOP_ITEM_EXCEPTIONS = [0x0A, 0x0B, 0x11, 0x12, 0x13, 0x14, 0x29]

# returns a set of all message ids used for shop items
def get_shop_message_id_set(shop_items):
    ids = set()
    for shop in shop_items:
        if shop.index not in SHOP_ITEM_EXCEPTIONS:
            ids.add(shop.description_message)
            ids.add(shop.purchase_message)
    return ids

# remove all messages that easy to tell are unused to create space in the message index table
def remove_unused_messages(messages):
    messages[:] = [m for m in messages if not m.is_id_message()]
    for index, m in enumerate(messages):
        m.index = index

# takes all messages used for shop items, and moves messages from the 00xx range into the unused 80xx range
def move_shop_item_messages(messages, shop_items):
    # checks if a message id is in the item message range
    def is_in_item_range(id):
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
            message.id |= 0x8000
    # update them in the shop item list
    for shop in shop_items:
        if is_in_item_range(shop.description_message):
            shop.description_message |= 0x8000
        if is_in_item_range(shop.purchase_message):
            shop.purchase_message |= 0x8000

def move_shop_item_messages_jp(messages, shop_items):
    # checks if a message id is in the item message range
    def is_in_item_range(id):
        bytes = int_to_bytes(id, 2)
        return bytes[0] == 0x00
    # update them in the shop item list
    for shop in shop_items:
        if is_in_item_range(shop.description_message):
            shop.description_message |= 0x8000
        if is_in_item_range(shop.purchase_message):
            shop.purchase_message |= 0x8000
            
def make_player_message(text):
    player_text = '\x05\x42\x0F\x05\x40'
    pronoun_mapping = {
        "You have ": player_text + " ",
        "You are ":  player_text + " is ",
        "You've ":   player_text + " ",
        "Your ":     player_text + "'s ",
        "You ":      player_text + " ",

        "you have ": player_text + " ",
        "you are ":  player_text + " is ",
        "you've ":   player_text + " ",
        "your ":     player_text + "'s ",
        "you ":      player_text + " ",
    }

    verb_mapping = {
        'obtained ': 'got ',
        'received ': 'got ',
        'learned ':  'got ',
        'borrowed ': 'got ',
        'found ':    'got ',
    }

    new_text = text

    # Replace the first instance of a 'You' with the player name
    lower_text = text.lower()
    you_index = lower_text.find('you')
    if you_index != -1:
        for find_text, replace_text in pronoun_mapping.items():
            # if the index do not match, then it is not the first 'You'
            if text.find(find_text) == you_index:
                new_text = new_text.replace(find_text, replace_text, 1)
                break

    # because names are longer, we shorten the verbs to they fit in the textboxes better
    for find_text, replace_text in verb_mapping.items():
        new_text = new_text.replace(find_text, replace_text)

    wrapped_text = line_wrap(new_text, False, False, False)
    if wrapped_text != new_text:
        new_text = line_wrap(new_text, True, True, False)

    return new_text


# reduce item message sizes and add new item messages
# make sure to call this AFTER move_shop_item_messages()
def update_item_messages(messages, world):
    new_item_messages = {**ITEM_MESSAGES, **KEYSANITY_MESSAGES}
    shop_mes = {**SHOP_MESSAGES}
    if world.settings.language_selection == "english":
        for id, (text, textJP) in new_item_messages.items():
            if world.settings.world_count > 1:
                update_message_by_id(messages, id, make_player_message(text), 0x23)
            else:
                update_message_by_id(messages, id, text, 0x23)

        for id, (text, textJP, opt, align) in MISC_MESSAGES.items():
            if text is None:
                pass
            else:
                update_message_by_id(messages, id, text, opt)
                
    elif world.settings.language_selection == "japanese":
        ntext = "<$痛いッピ！勘弁ッピ！{"
        update_message_jp(messages, 0x101A, ntext, 0x00, 1, align = "center")
        for id, (text, textJP) in new_item_messages.items():
            if "~" in textJP:
                update_message_jp(messages, id, textJP, 0x23, 2, align = "left")
            elif "~" not in textJP:
                update_message_jp(messages, id, textJP, 0x23, 2, align = "center")
            
        for id, text in shop_mes.items():
            update_message_jp(messages, id, text, 0x03, align = "left")
            
        for id, (text, textJP, opt, align) in MISC_MESSAGES.items():
            update_message_jp(messages, id, textJP, opt, 2, align = align)
            
        for id, (text, opt) in NAVI_MESSAGES.items():
            update_message_jp(messages, id, text, opt, align = "center")
            
        for id in MASK_MESSAGES:
            select = random.randrange(3)
            if select == 0:
                text = "<ひいいっ！！"
            elif select == 1:
                text = "<うわぁ！！"
            elif select == 2:
                text = "<！！"
            update_message_jp(messages, id, text, 0x00, align = "center")
    
# run all keysanity related patching to add messages for dungeon specific items
def add_item_messages(messages, shop_items, world):
    if world.settings.language_selection == "english":
        move_shop_item_messages(messages, shop_items)
    elif world.settings.language_selection == "japanese":
        move_shop_item_messages_jp(messages, shop_items)
    update_item_messages(messages, world)

# reads each of the game's messages into a list of Message objects
def read_messages(rom):
    table_offset = ENG_TABLE_START
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

        messages.append( Message.from_rom(rom, index) )

        index += 1
        table_offset += 8

    return messages

# write the messages back
def repack_messages(rom, messages, permutation=None, always_allow_skip=True, speed_up_text=True):

    rom.update_dmadata_record(TEXT_START, TEXT_START, TEXT_START + ENG_TEXT_SIZE_LIMIT)

    if permutation is None:
        permutation = range(len(messages))

    # repack messages
    offset = 0
    text_size_limit = ENG_TEXT_SIZE_LIMIT

    for old_index, new_index in enumerate(permutation):
        old_message = messages[old_index]
        new_message = messages[new_index]
        remember_id = new_message.id
        new_message.id = old_message.id

        # modify message, making it represent how we want it to be written
        new_message.transform(True, old_message.ending, always_allow_skip, speed_up_text)

        # actually write the message
        offset = new_message.write(rom, old_index, offset)

        new_message.id = remember_id

    # raise an exception if too much is written
    # we raise it at the end so that we know how much overflow there is
    if offset > text_size_limit:
        raise(TypeError("Message Text table is too large: 0x" + "{:x}".format(offset) + " written / 0x" + "{:x}".format(ENG_TEXT_SIZE_LIMIT) + " allowed."))

    # end the table
    table_index = len(messages)
    entry = bytes([0xFF, 0xFD, 0x00, 0x00, 0x07]) + int_to_bytes(offset, 3)
    entry_offset = EXTENDED_TABLE_START + 8 * table_index
    rom.write_bytes(entry_offset, entry)
    table_index += 1
    entry_offset = EXTENDED_TABLE_START + 8 * table_index
    if 8 * (table_index + 1) > EXTENDED_TABLE_SIZE:
        raise(TypeError("Message ID table is too large: 0x" + "{:x}".format(8 * (table_index + 1)) + " written / 0x" + "{:x}".format(EXTENDED_TABLE_SIZE) + " allowed."))
    rom.write_bytes(entry_offset, [0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

def reproduce_messages_jp(messages):
    with open(temporal,'a') as new:
        new.write("}\n")
        new.write("new_jp = {**RAWTEXT_JP,**MESTEXT}\n")
        new.write("mes_sorted = sorted(new_jp.items(), key=lambda x:x[0])")
    
def reformed(text, new_tag):
    p = 0
    if text.endswith(r"\x00\x00"):
        text = text[:-8]
        p = 1
    if r"\x81\x9e" or r"\x81\xcb" in text:
        text = text[:-24]
    else:
        text = text[:-16]
    if ("k" in new_tag) is True:
        text = text + r"\x86\xc8\x81\x70"
    if ("e" in new_tag) is True:
        text = text + r"\x81\x9f\x81\x70"
    if ("f" in new_tag) is True:
        text = text + r"\x81\x9e\x00\x30\x81\x70"
    if ("" == new_tag) is True:
        text = text + r"\x81\x70"
    if p == 1:
        text = text + r"\x00\x00"
    return text

def write_messages(rom, shuffle = False, shuffle_group = None, mode = 0):
    from temporal import new_jp, destinate_ids, MESTEXT, RAWTEXT_JP
    index = 0
    offset = 0
    idd = 0
    dif = 0
    d_text = None
    d_id = None
    opts = int_to_bytes(0,1)
    tex = None
    text_size_limit = JPN_TEXT_SIZE_LIMIT
    with open(temporal, "r+")as red:
        for id, (text, opt, tag, ending) in new_jp.items():
            for idr, offs in destinate_ids:
                if idr == id:
                    if (offs - offset) < 0:
                        raise(TypeError("Message Text table is too large: 0x" + "{:x}".format(id) + ", " + "{:x}".format((offset - offs))))                    
                    dif = (33280 + idd)
                    id_bytes = int_to_bytes(dif, 2)
                    offset_bytes = int_to_bytes(offset, 3)
                    opts = int_to_bytes(0,1)
                    entry = id_bytes + opts + bytes([0x00, 0x08]) + offset_bytes
                    entry_offset = EXTENDED_TABLE_START + 8 * index
                    if mode == 1:
                        rom.write_bytes(entry_offset, entry)
                    text_entry = bytes([0x81, 0x70])
                    offset = offs
                    text_offset = TEXT_START_JP + offset - 2
                    rom.write_bytes(text_offset, text_entry)
                    idd += 1
                    index += 1
                    break
            opts = int_to_bytes(int(0 if opt is None else opt),1)
            if shuffle is not False:
                id_bytes = int_to_bytes(id, 2)
                for (origin, replace) in shuffle_group:
                    if (origin == id)is True:
                        id_bytes = int_to_bytes(replace, 2)
                        try:
                            gin = MESTEXT[replace]
                        except KeyError:
                            gin = RAWTEXT_JP[replace]
                        tex = gin[2]
                        opt = gin[1]
                        opts = int_to_bytes(int(0 if opt is None else opt),1)
                        if not 'g' in tag:
                            if 'g' in tex:
                                tex = get_destination(replace,2)
                            if tex != tag:
                                text = reformed(text,tex)
                        elif 'g' in tag:
                            tag = get_destination(id,2)
                            if 'g' in tex:
                                tex = get_destination(replace,2)
                            if tex != tag:
                                text = reformed(text,tex)
                        break
            else:
                id_bytes = int_to_bytes(id, 2)
            offset_bytes = int_to_bytes(offset, 3)
            entry = id_bytes + opts + bytes([0x00, 0x08]) + offset_bytes
            entry_offset = EXTENDED_TABLE_START + 8 * index
            if mode == 1:
                rom.write_bytes(entry_offset, entry)

            if offset % 2 == 0:
                t = int(len(text) / 4)
                text_entry = text_to_bytes(text,t)
            elif offset % 2 != 0:
                t = int(1 + len(text) / 4)
                text_entry = text_to_bytes(text,t) + bytes([0x00])
            text_offset = TEXT_START_JP + offset
            rom.write_bytes(text_offset, text_entry)
            offset += t
            index += 1
            
    entry = bytes([0xFF, 0xFD, 0x00, 0x00, 0x08]) + int_to_bytes(offset, 3)
    entry_offset = EXTENDED_TABLE_START + 8 * index
    if 8 * (index + 1) > EXTENDED_TABLE_SIZE:
        raise(TypeError("Message ID table is too large: 0x" + "{:x}".format(8 * (index + 1)) + " written / 0x" + "{:x}".format(EXTENDED_TABLE_SIZE) + " allowed."))
    if mode == 1:
        rom.write_bytes(entry_offset,entry)
    text_entry = bytes([0x81, 0x70])
    text_offset = TEXT_START_JP + offset
    if offset > text_size_limit:
        raise(TypeError("Message Text table is too large: 0x" + "{:x}".format(offset) + " written / 0x" + "{:x}".format(JPN_TEXT_SIZE_LIMIT) + " allowed."))
    rom.write_bytes(text_offset, text_entry)
    index += 1
    entry_offset = EXTENDED_TABLE_START + 8 * index
    if mode == 1:
        rom.write_bytes(entry_offset, [0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        os.remove(temporal)

def get_destination(id, mode=0):
    from temporal import new_jp, destinate_ids, MESTEXT, RAWTEXT_JP
    try:
        taget = MESTEXT[id]
    except KeyError:
        taget = RAWTEXT_JP[id]
    id_to = int(taget[0][-16:-8].replace("\\x",""), base=16)
    if "g" in taget[2]:
        return get_destination(id_to, mode)
    else:
        if mode == 0:
            return taget[0]
        elif mode == 1:
            return taget[1]
        elif mode == 2:
            return taget[2]
        elif mode == 3:
            return taget[2]
        elif mode == 4:
            return id_to
            
# shuffles the messages in the game, making sure to keep various message types in their own group
def shuffle_messages(messages, except_hints=True, always_allow_skip=True):

    permutation = [i for i, _ in enumerate(messages)]

    def is_exempt(m):
        hint_ids = (
            GOSSIP_STONE_MESSAGES + TEMPLE_HINTS_MESSAGES + LIGHT_ARROW_HINT +
            list(KEYSANITY_MESSAGES.keys()) + shuffle_messages.shop_item_messages +
            shuffle_messages.scrubs_message_ids +
            [0x5036, 0x70F5] # Chicken count and poe count respectively
        )
        shuffle_exempt = [
            0x208D,         # "One more lap!" for Cow in House race.
        ]
        is_hint = (except_hints and m.id in hint_ids)
        is_error_message = (m.id == ERROR_MESSAGE)
        is_shuffle_exempt = (m.id in shuffle_exempt)
        return (is_hint or is_error_message or m.is_id_message() or is_shuffle_exempt)

    have_goto         = list( filter(lambda m: not is_exempt(m) and m.has_goto,         messages) )
    have_keep_open    = list( filter(lambda m: not is_exempt(m) and m.has_keep_open,    messages) )
    have_event        = list( filter(lambda m: not is_exempt(m) and m.has_event,        messages) )
    have_fade         = list( filter(lambda m: not is_exempt(m) and m.has_fade,         messages) )
    have_ocarina      = list( filter(lambda m: not is_exempt(m) and m.has_ocarina,      messages) )
    have_two_choice   = list( filter(lambda m: not is_exempt(m) and m.has_two_choice,   messages) )
    have_three_choice = list( filter(lambda m: not is_exempt(m) and m.has_three_choice, messages) )
    basic_messages    = list( filter(lambda m: not is_exempt(m) and m.is_basic(),       messages) )


    def shuffle_group(group):
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

# shuffles the messages in the game, making sure to keep various message types in their own group
def shuffle_messages_jp(messages, except_hints=True, always_allow_skip=True):

    have_gen_I = []
    have_gen_O = []
    have_ocarina_I = []
    have_ocarina_O = []
    have_two_I = []
    have_two_O = []
    have_three_I = []
    have_three_O = []
    shuffled = []

    def is_exempt(id):
        hint_ids = (
            GOSSIP_STONE_MESSAGES + TEMPLE_HINTS_MESSAGES + LIGHT_ARROW_HINT +
            list(KEYSANITY_MESSAGES.keys()) + list(SHOP_MESSAGES.keys()) +
            [0x10A0, 0x10A1, 0x10A2, 0x10CA, 0x10CB, 0x10CC, 0x10CD, 0x10CE, 0x10CF, 0x10DC, 0x10DD, 0x5036, 0x70F5, 0x088D, 0x088E, 0x088F, 0x0890, 0x0891, 0x0892] # Chicken count and poe count respectively
        )
        shuffle_exempt = [
            0x208D, 0xFFFC, 0xFFFD, 0xFFFF,          # "One more lap!" for Cow in House race.
        ]
        is_hint = (except_hints and str(id) in str(hint_ids))
        is_error_message = (str(id) == str(ERROR_MESSAGE))
        is_shuffle_exempt = (str(id) in str(shuffle_exempt))
        return (is_hint or is_error_message or is_shuffle_exempt)
    def is_destinate(id):
        destination_ids = (
            [0x1003, 0x1009, 0x100b, 0x100d, 0x100f, 0x1010, 0x1016, 0x1019, 0x1030, 0x1032, 0x1034, 0x1048, 0x1050, 0x1054, 0x1056, 0x1059, 0x105c, 0x105e, 0x1061, 0x1068, 0x106f, 0x1071, 0x10a3, 0x10a9, 0x10ad, 0x10b8, 0x10c1, 0x10c5, 0x10c8, 0x10c9, 0x10d0, 0x10d1, 0x10d2, 0x10d3, 0x10d6, 0x10d8, 0x2003, 0x200b, 0x202b, 0x2031, 0x2036, 0x2040, 0x2042, 0x2046, 0x2052, 0x2065, 0x2066, 0x3015, 0x3017, 0x3019, 0x301b, 0x3022, 0x3025, 0x302a, 0x302c, 0x3033, 0x3038, 0x3042, 0x304b, 0x304f, 0x3055, 0x305c, 0x4009, 0x400b, 0x4013, 0x4015, 0x401c, 0x4027, 0x5010, 0x5011, 0x5014, 0x5019, 0x5029, 0x503f, 0x5044, 0x504b, 0x5058, 0x505a, 0x505c, 0x505e, 0x5061, 0x5067, 0x507a, 0x508c, 0x6018, 0x601a, 0x6023, 0x6024, 0x6026, 0x6062, 0x6065, 0x606b, 0x606e, 0x607a, 0x607b, 0x607e, 0x7017, 0x7019, 0x701c, 0x701e, 0x7020, 0x7022, 0x7024, 0x7028, 0x7051, 0x7072]
        )
        is_destin = (str(id) == str(destination_ids))
        return (is_destin)
    with open(temporal,"r+") as dec:
        from temporal import new_jp
        for id, (text, opt, tag, ending) in new_jp.items():
            if "g" in tag :
                d_tag = get_destination(id, 2)
                if (((("k" in d_tag)or("e" in d_tag)or("f" in d_tag))is True) or (("" == d_tag)is True) and not is_exempt(id) and not is_destinate(id)):
                    have_gen_I.append(id)
                    have_gen_O.append(id)
                if(((("o" in d_tag) is True))and not is_exempt(id) and not is_destinate(id)):
                    have_ocarina_I.append(id)
                    have_ocarina_O.append(id)
                if(((("2" in d_tag) is True))and not is_exempt(id) and not is_destinate(id)):
                    have_two_I.append(id)
                    have_two_O.append(id)
                if(((("3" in d_tag) is True))and not is_exempt(id) and not is_destinate(id)):
                    have_three_I.append(id)
                    have_three_O.append(id)
            if (((("k" in tag)or("e" in tag)or("f" in tag))is True) or (("" == tag)is True) and not is_exempt(id) and not is_destinate(id)):
                have_gen_I.append(id)
                have_gen_O.append(id)
            if(((("o" in tag) is True))and not is_exempt(id) and not is_destinate(id)):
                have_ocarina_I.append(id)
                have_ocarina_O.append(id)
            if(((("2" in tag) is True))and not is_exempt(id) and not is_destinate(id)):
                have_two_I.append(id)
                have_two_O.append(id)
            if(((("3" in tag) is True))and not is_exempt(id) and not is_destinate(id)):
                have_three_I.append(id)
                have_three_O.append(id)

    random.shuffle(have_gen_I)
    random.shuffle(have_ocarina_I)
    random.shuffle(have_two_I)
    random.shuffle(have_three_I)
    gen = [(i, j) for i, j in zip(have_gen_O, have_gen_I)]
    ocarina = [(i, j) for i, j in zip(have_ocarina_O, have_ocarina_I)]
    two = [(i, j) for i, j in zip(have_two_O, have_two_I)]
    three = [(i, j) for i, j in zip(have_three_O, have_three_I)]
    shuffled = (gen + ocarina + two + three)
    return shuffled

# Update warp song text boxes for ER
def update_warp_song_text(messages, world):
    msg_list = {
        0x088D: 'Minuet of Forest Warp -> Sacred Forest Meadow',
        0x088E: 'Bolero of Fire Warp -> DMC Central Local',
        0x088F: 'Serenade of Water Warp -> Lake Hylia',
        0x0890: 'Requiem of Spirit Warp -> Desert Colossus',
        0x0891: 'Nocturne of Shadow Warp -> Graveyard Warp Pad Region',
        0x0892: 'Prelude of Light Warp -> Temple of Time',
    }
    if world.settings.language_selection == "english":
        for id, entr in msg_list.items():
            destination = world.get_entrance(entr).connected_region

            if destination.pretty_name:
                destination_name = destination.pretty_name
            elif destination.hint:
                destination_name = destination.hint
            elif destination.dungeon:
                destination_name = destination.dungeon.hint
            else:
                destination_name = destination.name
            color = COLOR_MAP[destination.font_color or 'White']

            new_msg = f"\x08\x05{color}Warp to {destination_name}?\x05\40\x09\x01\x01\x1b\x05{color}OK\x01No\x05\40"
            update_message_by_id(messages, id, new_msg)
    elif world.settings.language_selection == "japanese":
        for id, entr in msg_list.items():
            destination = world.get_entrance(entr).connected_region

            if destination.pretty_name_JP:
                destination_name = destination.pretty_name_JP
            elif destination.hint_JP:
                destination_name = destination.hint_JP
            elif destination.dungeon:
                destination_name = destination.dungeon.hint_JP
            elif destination.name_JP:
                destination_name = destination.name_JP
            else:
                destination_name = destination.name
                destination_name = destination_name.translate(str.maketrans({chr(0x0021 + i): chr(0xFF01 + i) for i in range(94)}))
            color = COLOR_MAP_JP[destination.font_color or 'White']

            new_msg = f"<#{color}{destination_name}へワープ！#\x00>&:2#{color}はい&いいえ#\x00"
            update_message_jp(messages, id, new_msg, align = "left")
