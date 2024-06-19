# text details: https://wiki.cloudmodding.com/oot/Text_Format

from __future__ import annotations
import random
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Optional, Any

from HintList import misc_item_hint_table, misc_location_hint_table
from TextBox import line_wrap
from Utils import find_last

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
}

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

REVERSE_MAP: list[str] = list(chr(x) for x in range(256))

for char, byte in CHARACTER_MAP.items():
    SPECIAL_CHARACTERS.setdefault(byte, char)
    REVERSE_MAP[byte] = char

# [0x0500,0x0560] (inclusive) are reserved for plandomakers
GOSSIP_STONE_MESSAGES: list[int] = list(range(0x0401, 0x04FF))  # ids of the actual hints
GOSSIP_STONE_MESSAGES += [0x2053, 0x2054]  # shared initial stone messages
TEMPLE_HINTS_MESSAGES: list[int] = [0x7057, 0x707A]  # dungeon reward hints from the temple of time pedestal
GS_TOKEN_MESSAGES: list[int] = [0x00B4, 0x00B5]  # Get Gold Skulltula Token messages
ERROR_MESSAGE: int = 0x0001

new_messages = [] # Used to keep track of new/updated messages to prevent duplicates. Clear it at the start of patches

# messages for shorter item messages
# ids are in the space freed up by move_shop_item_messages()
ITEM_MESSAGES: list[tuple[int, str]] = [
    (0x0001, "\x08\x06\x30\x05\x41TEXT ID ERROR!\x05\x40"),
    (0x9001, "\x08\x13\x2DYou borrowed a \x05\x41Pocket Egg\x05\x40!\x01A Pocket Cucco will hatch from\x01it overnight. Be sure to give it\x01back."),
    (0x0002, "\x08\x13\x2FYou returned the Pocket Cucco\x01and got \x05\x41Cojiro\x05\x40 in return!\x01Unlike other Cuccos, Cojiro\x01rarely crows."),
    (0x0003, "\x08\x13\x30You got an \x05\x41Odd Mushroom\x05\x40!\x01It is sure to spoil quickly! Take\x01it to the Kakariko Potion Shop."),
    (0x0004, "\x08\x13\x31You received an \x05\x41Odd Potion\x05\x40!\x01It may be useful for something...\x01Hurry to the Lost Woods!"),
    (0x0005, "\x08\x13\x32You returned the Odd Potion \x01and got the \x05\x41Poacher's Saw\x05\x40!\x01The young punk guy must have\x01left this."),
    (0x0007, "\x08\x13\x48You got a \x01\x05\x41Deku Seeds Bullet Bag\x05\x40.\x01This bag can hold up to \x05\x4640\x05\x40\x01slingshot bullets."),
    (0x0008, "\x08\x13\x33You traded the Poacher's Saw \x01for a \x05\x41Broken Goron's Sword\x05\x40!\x01Visit Biggoron to get it repaired!"),
    (0x0009, "\x08\x13\x34You checked in the Broken \x01Goron's Sword and received a \x01\x05\x41Prescription\x05\x40!\x01Go see King Zora!"),
    (0x000A, "\x08\x13\x37The Biggoron's Sword...\x01You got a \x05\x41Claim Check \x05\x40for it!\x01You can't wait for the sword!"),
    (0x000B, "\x08\x13\x2EYou got a \x05\x41Pocket Cucco, \x05\x40one\x01of Anju's prized hens! It fits \x01in your pocket."),
    (0x000C, "\x08\x13\x3DYou got the \x05\x41Biggoron's Sword\x05\x40!\x01This blade was forged by a \x01master smith and won't break!"),
    (0x000D, "\x08\x13\x35You used the Prescription and\x01received an \x05\x41Eyeball Frog\x05\x40!\x01Be quick and deliver it to Lake \x01Hylia!"),
    (0x000E, "\x08\x13\x36You traded the Eyeball Frog \x01for the \x05\x41World's Finest Eye Drops\x05\x40!\x01Hurry! Take them to Biggoron!"),
    (0x0010, "\x08\x13\x25You got a \x05\x41Skull Mask\x05\x40.\x01You feel like a monster while you\x01wear this mask!"),
    (0x0011, "\x08\x13\x26You got a \x05\x41Spooky Mask\x05\x40.\x01You can scare many people\x01with this mask!"),
    (0x0012, "\x08\x13\x24You got a \x05\x41Keaton Mask\x05\x40.\x01You'll be a popular guy with\x01this mask on!"),
    (0x0013, "\x08\x13\x27You got a \x05\x41Bunny Hood\x05\x40.\x01The hood's long ears are so\x01cute!"),
    (0x0014, "\x08\x13\x28You got a \x05\x41Goron Mask\x05\x40.\x01It will make your head look\x01big, though."),
    (0x0015, "\x08\x13\x29You got a \x05\x41Zora Mask\x05\x40.\x01With this mask, you can\x01become one of the Zoras!"),
    (0x0016, "\x08\x13\x2AYou got a \x05\x41Gerudo Mask\x05\x40.\x01This mask will make you look\x01like...a girl?"),
    (0x0017, "\x08\x13\x2BYou got a \x05\x41Mask of Truth\x05\x40.\x01Show it to many people!"),
    (0x0030, "\x08\x13\x06You found the \x05\x41Fairy Slingshot\x05\x40!"),
    (0x0031, "\x08\x13\x03You found the \x05\x41Fairy Bow\x05\x40!"),
    (0x0035, "\x08\x13\x0EYou found the \x05\x41Boomerang\x05\x40!"),
    (0x0036, "\x08\x13\x0AYou found the \x05\x41Hookshot\x05\x40!\x01It's a spring-loaded chain that\x01you can cast out to hook things."),
    (0x0038, "\x08\x13\x11You found the \x05\x41Megaton Hammer\x05\x40!\x01It's so heavy, you need to\x01use two hands to swing it!"),
    (0x0039, "\x08\x13\x0FYou found the \x05\x41Lens of Truth\x05\x40!\x01Mysterious things are hidden\x01everywhere!"),
    (0x003A, "\x08\x13\x08You found the \x05\x41Ocarina of Time\x05\x40!\x01It glows with a mystical light..."),
    (0x003C, "\x08\x13\x67You received the \x05\x41Fire\x01Medallion\x05\x40!\x01Darunia awakens as a Sage and\x01adds his power to yours!"),
    (0x003D, "\x08\x13\x68You received the \x05\x43Water\x01Medallion\x05\x40!\x01Ruto awakens as a Sage and\x01adds her power to yours!"),
    (0x003E, "\x08\x13\x66You received the \x05\x42Forest\x01Medallion\x05\x40!\x01Saria awakens as a Sage and\x01adds her power to yours!"),
    (0x003F, "\x08\x13\x69You received the \x05\x46Spirit\x01Medallion\x05\x40!\x01Nabooru awakens as a Sage and\x01adds her power to yours!"),
    (0x0040, "\x08\x13\x6BYou received the \x05\x44Light\x01Medallion\x05\x40!\x01Rauru the Sage adds his power\x01to yours!"),
    (0x0041, "\x08\x13\x6AYou received the \x05\x45Shadow\x01Medallion\x05\x40!\x01Impa awakens as a Sage and\x01adds her power to yours!"),
    (0x0042, "\x08\x13\x14You got an \x05\x41Empty Bottle\x05\x40!\x01You can put something in this\x01bottle."),
    (0x0048, "\x08\x13\x10You got a \x05\x41Magic Bean\x05\x40!\x01Find a suitable spot for a garden\x01and plant it."),
    (0x9048, "\x08\x13\x10You got a \x05\x41Pack of Magic Beans\x05\x40!\x01Find suitable spots for a garden\x01and plant them."),
    (0x004A, "\x08\x13\x07You received the \x05\x41Fairy Ocarina\x05\x40!\x01This is a memento from Saria."),
    (0x004B, "\x08\x13\x3DYou got the \x05\x42Giant's Knife\x05\x40!\x01Hold it with both hands to\x01attack! It's so long, you\x01can't use it with a \x05\x44shield\x05\x40."),
    (0x004E, "\x08\x13\x40You found the \x05\x44Mirror Shield\x05\x40!\x01The shield's polished surface can\x01reflect light or energy."),
    (0x004F, "\x08\x13\x0BYou found the \x05\x41Longshot\x05\x40!\x01It's an upgraded Hookshot.\x01It extends \x05\x41twice\x05\x40 as far!"),
    (0x0052, "\x08You got a \x05\x42Magic Jar\x05\x40!\x01Your Magic Meter is filled!"),
    (0x0053, "\x08\x13\x45You got the \x05\x41Iron Boots\x05\x40!\x01So heavy, you can't run.\x01So heavy, you can't float."),
    (0x0054, "\x08\x13\x46You got the \x05\x41Hover Boots\x05\x40!\x01With these mysterious boots\x01you can hover above the ground."),
    (0x0056, "\x08\x13\x4BYou upgraded your quiver to a\x01\x05\x41Big Quiver\x05\x40!\x01Now you can carry more arrows-\x01\x05\x4640 \x05\x40in total!"),
    (0x0057, "\x08\x13\x4CYou upgraded your quiver to\x01the \x05\x41Biggest Quiver\x05\x40!\x01Now you can carry to a\x01maximum of \x05\x4650\x05\x40 arrows!"),
    (0x0058, "\x08\x13\x4DYou found a \x05\x41Bomb Bag\x05\x40!\x01You found \x05\x4120 Bombs\x05\x40 inside!"),
    (0x0059, "\x08\x13\x4EYou got a \x05\x41Big Bomb Bag\x05\x40!\x01Now you can carry more \x01Bombs, up to a maximum of \x05\x4630\x05\x40!"),
    (0x005A, "\x08\x13\x4FYou got the \x01\x05\x41Biggest Bomb Bag\x05\x40!\x01Now, you can carry up to \x01\x05\x4640\x05\x40 Bombs!"),
    (0x005B, "\x08\x13\x51You found the \x05\x43Silver Gauntlets\x05\x40!\x01You feel the power to lift\x01big things with it!"),
    (0x005C, "\x08\x13\x52You found the \x05\x43Golden Gauntlets\x05\x40!\x01You can feel even more power\x01coursing through your arms!"),
    (0x005E, "\x08\x13\x56You got an \x05\x43Adult's Wallet\x05\x40!\x01Now you can hold\x01up to \x05\x46200\x05\x40 \x05\x46Rupees\x05\x40."),
    (0x005F, "\x08\x13\x57You got a \x05\x43Giant's Wallet\x05\x40!\x01Now you can hold\x01up to \x05\x46500\x05\x40 \x05\x46Rupees\x05\x40."),
    (0x0060, "\x08\x13\x77You found a \x05\x41Small Key\x05\x40!\x01This key will open a locked \x01door. You can use it only\x01in this dungeon."),
    (0x0066, "\x08\x13\x76You found the \x05\x41Dungeon Map\x05\x40!\x01It's the map to this dungeon."),
    (0x0067, "\x08\x13\x75You found the \x05\x41Compass\x05\x40!\x01Now you can see the locations\x01of many hidden things in the\x01dungeon!"),
    (0x0068, "\x08\x13\x6FYou obtained the \x05\x41Stone of Agony\x05\x40!\x01If you equip a \x05\x44Rumble Pak\x05\x40, it\x01will react to nearby...secrets."),
    (0x0069, "\x08\x13\x23You received \x05\x41Zelda's Letter\x05\x40!\x01Wow! This letter has Princess\x01Zelda's autograph!"),
    (0x006C, "\x08\x13\x49Your \x05\x41Deku Seeds Bullet Bag \x01\x05\x40has become bigger!\x01This bag can hold \x05\x4650\x05\x41 \x05\x40bullets!"),
    (0x006F, "\x08You got a \x05\x42Green Rupee\x05\x40!\x01That's \x05\x42one Rupee\x05\x40!"),
    (0x0070, "\x08\x13\x04You got the \x05\x41Fire Arrow\x05\x40!\x01If you hit your target,\x01it will catch fire."),
    (0x0071, "\x08\x13\x0CYou got the \x05\x43Ice Arrow\x05\x40!\x01If you hit your target,\x01it will freeze."),
    (0x0072, "\x08\x13\x12You got the \x05\x44Light Arrow\x05\x40!\x01The light of justice\x01will smite evil!"),
    (0x0079, "\x08\x13\x50You got the \x05\x41Goron's Bracelet\x05\x40!\x01Now you can pull up Bomb\x01Flowers."),
    (0x007B, "\x08\x13\x70You obtained the \x05\x41Gerudo's \x01Membership Card\x05\x40!\x01You can get into the Gerudo's\x01training ground."),
    (0x0080, "\x08\x13\x6CYou got the \x05\x42Kokiri's Emerald\x05\x40!\x01This is the Spiritual Stone of \x01Forest passed down by the\x01Great Deku Tree."),
    (0x0081, "\x08\x13\x6DYou obtained the \x05\x41Goron's Ruby\x05\x40!\x01This is the Spiritual Stone of \x01Fire passed down by the Gorons!"),
    (0x0082, "\x08\x13\x6EYou obtained \x05\x43Zora's Sapphire\x05\x40!\x01This is the Spiritual Stone of\x01Water passed down by the\x01Zoras!"),
    (0x0090, "\x08\x13\x00Now you can pick up \x01many \x05\x41Deku Sticks\x05\x40!\x01You can carry up to \x05\x4620\x05\x40 of them!"),
    (0x0091, "\x08\x13\x00You can now pick up \x01even more \x05\x41Deku Sticks\x05\x40!\x01You can carry up to \x05\x4630\x05\x40 of them!"),
    (0x0098, "\x08\x13\x1AYou got \x05\x41Lon Lon Milk\x05\x40!\x01This milk is very nutritious!\x01There are two drinks in it."),
    (0x0099, "\x08\x13\x1BYou found \x05\x41Ruto's Letter\x05\x40 in a\x01bottle! Show it to King Zora."),
    (0x9099, "\x08\x13\x1BYou found \x05\x41a letter in a bottle\x05\x40!\x01You remove the letter from the\x01bottle, freeing it for other uses."),
    (0x009A, "\x08\x13\x21You got a \x05\x41Weird Egg\x05\x40!\x01Feels like there's something\x01moving inside!"),
    (0x00A4, "\x08\x13\x3BYou got the \x05\x42Kokiri Sword\x05\x40!\x01This is a hidden treasure of\x01the Kokiri."),
    (0x00A7, "\x08\x13\x01Now you can carry\x01many \x05\x41Deku Nuts\x05\x40!\x01You can hold up to \x05\x4630\x05\x40 nuts!"),
    (0x00A8, "\x08\x13\x01You can now carry even\x01more \x05\x41Deku Nuts\x05\x40! You can carry\x01up to \x05\x4640\x05\x41 \x05\x40nuts!"),
    (0x00AD, "\x08\x13\x05You got \x05\x41Din's Fire\x05\x40!\x01Its fireball engulfs everything!"),
    (0x00AE, "\x08\x13\x0DYou got \x05\x42Farore's Wind\x05\x40!\x01This is warp magic you can use!"),
    (0x00AF, "\x08\x13\x13You got \x05\x43Nayru's Love\x05\x40!\x01Cast this to create a powerful\x01protective barrier."),
    (0x00B4, "\x08You got a \x05\x41Gold Skulltula Token\x05\x40!\x01You've collected \x05\x41\x19\x05\x40 tokens in total."),
    (0x00B5, "\x08You destroyed a \x05\x41Gold Skulltula\x05\x40.\x01You got a token proving you \x01destroyed it!"), #Unused
    (0x00C2, "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Collect four pieces total to get\x01another Heart Container."),
    (0x90C2, "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01You are already at\x01maximum health."),
    (0x00C3, "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01So far, you've collected two \x01pieces."),
    (0x00C4, "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Now you've collected three \x01pieces!"),
    (0x00C5, "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01You've completed another Heart\x01Container!"),
    (0x00C6, "\x08\x13\x72You got a \x05\x41Heart Container\x05\x40!\x01Your maximum life energy is \x01increased by one heart."),
    (0x90C6, "\x08\x13\x72You got a \x05\x41Heart Container\x05\x40!\x01You are already at\x01maximum health."),
    (0x00C7, "\x08\x13\x74You got the \x05\x41Boss Key\x05\x40!\x01Now you can get inside the \x01chamber where the Boss lurks."),
    (0x00CC, "\x08You got a \x05\x43Blue Rupee\x05\x40!\x01That's \x05\x43five Rupees\x05\x40!"),
    (0x00CD, "\x08\x13\x53You got the \x05\x43Silver Scale\x05\x40!\x01You can dive deeper than you\x01could before."),
    (0x00CE, "\x08\x13\x54You got the \x05\x43Golden Scale\x05\x40!\x01Now you can dive much\x01deeper than you could before!"),
    (0x00DD, "\x08You mastered the secret sword\x01technique of the \x05\x41Spin Attack\x05\x40!"),
    (0x00E4, "\x08You can now use \x05\x42Magic\x05\x40!"),
    (0x00E5, "\x08Your \x05\x44defensive power\x05\x40 is enhanced!"),
    (0x00E8, "\x08Your magic power has been \x01enhanced! Now you have twice\x01as much \x05\x41Magic Power\x05\x40!"),
    (0x00E9, "\x08Your defensive power has been \x01enhanced! Damage inflicted by \x01enemies will be \x05\x41reduced by half\x05\x40."),
    (0x00F0, "\x08You got a \x05\x41Red Rupee\x05\x40!\x01That's \x05\x41twenty Rupees\x05\x40!"),
    (0x00F1, "\x08You got a \x05\x45Purple Rupee\x05\x40!\x01That's \x05\x45fifty Rupees\x05\x40!"),
    (0x00F2, "\x08You got a \x05\x46Huge Rupee\x05\x40!\x01This Rupee is worth a whopping\x01\x05\x46two hundred Rupees\x05\x40!"),
    (0x00F4, "\x08\x05\x44Loser!\x05\x40\x04\x08You found only \x05\x42one Rupee\x05\x40.\x01You are not very lucky."),
    (0x00F5, "\x08\x05\x44Loser!\x05\x40\x04\x08You found \x05\x43five Rupees\x05\x40.\x01Even so, you are not very lucky."),
    (0x00F6, "\x08\x05\x44Loser!\x05\x40\x04\x08You found \x05\x41twenty Rupees\x05\x40.\x01Your last selection was a mistake,\x01wasn't it! How frustrating!"),
    (0x00F7, "\x08\x05\x41Winner!\x05\x40\x04\x08You found \x05\x46fifty Rupees\x05\x40.\x01You are a genuinely lucky guy!"),
    (0x00FA, "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Collect four pieces total to get\x01another Heart Container."),
    (0x00FB, "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01So far, you've collected two \x01pieces."),
    (0x00FC, "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Now you've collected three \x01pieces!"),
    (0x00FD, "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01You've completed another Heart\x01Container!"),
    (0x90FA, "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01You are already at\x01maximum health."),
    #(0x6074, "\x08Oh, that's too bad.\x04\x08If you change your mind, please\x01come back again!\x04\x08The mark that will lead you to the\x01Spirit Temple is the \x05\x41flag on\x01the left \x05\x40outside the shop."),
    (0x9002, "\x08You are a \x05\x43FOOL\x05\x40!"),
    (0x9003, "\x08You found a piece of the \x05\x41Triforce\x05\x40!"),
    (0x9019, "\x08\x13\x09You found a \x05\x41Bombchu Bag\x05\x40!\x01It has some \x05\x41Bombchus\x05\x40 inside!\x01Find more in tall grass."),
    (0x901A, "\x08You can't buy Bombchus without a\x01\x05\x41Bombchu Bag\x05\x40!"),
    (0x908C, "\x08You got the\x01\x05\x41Ocarina A Button!\x05\x40\x01You can now play \x9F on the Ocarina!"),
    (0x908D, "\x08You got the\x01\x05\x41Ocarina C-up Button!\x05\x40\x01You can now play \xA5 on the Ocarina!"),
    (0x908E, "\x08You got the\x01\x05\x41Ocarina C-down Button!\x05\x40\x01You can now play \xA6 on the Ocarina!"),
    (0x908F, "\x08You got the\x01\x05\x41Ocarina C-left Button!\x05\x40\x01You can now play \xA7 on the Ocarina!"),
    (0x9090, "\x08You got the\x01\x05\x41Ocarina C-right Button!\x05\x40\x01You can now play \xA8 on the Ocarina!"),
    (0x9091, "\x08\x06\x28You have learned the\x01\x06\x2F\x05\x42Minuet of Forest\x05\x40!"),
    (0x9092, "\x08\x06\x28You have learned the\x01\x06\x37\x05\x41Bolero of Fire\x05\x40!"),
    (0x9093, "\x08\x06\x28You have learned the\x01\x06\x29\x05\x43Serenade of Water\x05\x40!"),
    (0x9094, "\x08\x06\x28You have learned the\x01\x06\x2D\x05\x46Requiem of Spirit\x05\x40!"),
    (0x9095, "\x08\x06\x28You have learned the\x01\x06\x28\x05\x45Nocturne of Shadow\x05\x40!"),
    (0x9096, "\x08\x06\x28You have learned the\x01\x06\x32\x05\x44Prelude of Light\x05\x40!"),
    # 0x9097 and 0x9098 unused
    # 0x9099 used above
    (0x909A, "\x08\x06\x15You've learned \x05\x43Zelda's Lullaby\x05\x40!"),
    (0x909B, "\x08\x06\x11You've learned \x05\x41Epona's Song\x05\x40!"),
    (0x909C, "\x08\x06\x14You've learned \x05\x42Saria's Song\x05\x40!"),
    (0x909D, "\x08\x06\x0BYou've learned the \x05\x46Sun's Song\x05\x40!"),
    (0x909E, "\x08\x06\x05You've learned the \x05\x44Song of Time\x05\x40!"),
    (0x909F, "\x08You've learned the \x05\x45Song of Storms\x05\x40!"),
    (0x90A0, "\x08\x13\x15You got a \x05\x41Red Potion\x05\x40!\x01It will restore your health"),
    (0x90A1, "\x08\x13\x16You got a \x05\x42Green Potion\x05\x40!\x01It will restore your magic."),
    (0x90A2, "\x08\x13\x17You got a \x05\x43Blue Potion\x05\x40!\x01It will recover your health\x01and magic."),
    (0x90A3, "\x08\x13\x18You caught a \x05\x41Fairy\x05\x40 in a bottle!\x01It will revive you\x01the moment you run out of life \x01energy."),
    (0x90A4, "\x08\x13\x19You got a \x05\x41Fish\x05\x40!\x01It looks so fresh and\x01delicious!"),
    (0x90A5, "\x08\x13\x1CYou put a \x05\x44Blue Fire\x05\x40\x01into the bottle!\x01This is a cool flame you can\x01use on red ice."),
    (0x90A6, "\x08\x13\x1DYou put a \x05\x41Bug \x05\x40in the bottle!\x01This kind of bug prefers to\x01live in small holes in the ground."),
    (0x90A7, "\x08\x13\x1EYou put a \x05\x41Big Poe \x05\x40in a bottle!\x01Let's sell it at the \x05\x41Ghost Shop\x05\x40!\x01Something good might happen!"),
    (0x90A8, "\x08\x13\x20You caught a \x05\x41Poe \x05\x40in a bottle!\x01Something good might happen!"),
    (0x90A9, "\x08\x13\x02You got \x05\x41Bombs\x05\x40!\x01If you see something\x01suspicious, bomb it!"),
    (0x90AA, "\x08\x13\x01You got a \x05\x41Deku Nut\x05\x40!"),
    (0x90AB, "\x08\x13\x09You got \x05\x41Bombchus\x05\x40!"),
    (0x90AC, "\x08\x13\x00You got a \x05\x41Deku Stick\x05\x40!"),
    (0x90AD, "\x08\x13\x3EYou got a \x05\x44Deku Shield\x05\x40!"),
    (0x90AE, "\x08\x13\x3FYou got a \x05\x44Hylian Shield\x05\x40!"),
    (0x90AF, "\x08\x13\x42You got a \x05\x41Goron Tunic\x05\x40!\x01Going to a hot place? No worry!"),
    (0x90B0, "\x08\x13\x43You got a \x05\x43Zora Tunic\x05\x40!\x01Wear it, and you won't drown\x01underwater."),
    (0x90B1, "\x08You got a \x05\x45Recovery Heart\x05\x40!\x01Your life energy is recovered!"),
    (0x90B2, "\x08You got a \x05\x46bundle of arrows\x05\x40!"),
    (0x90B3, "\x08\x13\x58You got \x05\x41Deku Seeds\x05\x40!\x01Use these as bullets\x01for your Slingshot."),
    (0x90B4, "\x08You found a \x05\x41fairy\x05\x40!\x01Your health has been restored!"),
    (0x90B5, "\x08You found \x05\x43literally nothing\x05\x40!"),
]

KEYSANITY_MESSAGES: list[tuple[int, str]] = [
    (0x001C, "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09"),
    (0x0006, "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09"),
    (0x001D, "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09"),
    (0x001E, "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09"),
    (0x002A, "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09"),
    (0x0061, "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for \x05\x41Ganon's Castle\x05\x40!\x09"),
    (0x0062, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x42Deku Tree\x05\x40!\x09"),
    (0x0063, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for \x05\x41Dodongo's Cavern\x05\x40!\x09"),
    (0x0064, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for \x05\x43Jabu Jabu's Belly\x05\x40!\x09"),
    (0x0065, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09"),
    (0x007C, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09"),
    (0x007D, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09"),
    (0x007E, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09"),
    (0x007F, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09"),
    (0x0087, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x44Ice Cavern\x05\x40!\x09"),
    (0x0088, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x42Deku Tree\x05\x40!\x09"),
    (0x0089, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for \x05\x41Dodongo's Cavern\x05\x40!\x09"),
    (0x008A, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for \x05\x43Jabu Jabu's Belly\x05\x40!\x09"),
    (0x008B, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09"),
    (0x008C, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09"),
    (0x008E, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09"),
    (0x008F, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09"),
    (0x0092, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x44Ice Cavern\x05\x40!\x09"),
    (0x0093, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09"),
    (0x0094, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09"),
    (0x0095, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09"),
    (0x009B, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x45Bottom of the Well\x05\x40!\x09"),
    (0x009F, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x46Gerudo Training\x01Ground\x05\x40!\x09"),
    (0x00A0, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x46Thieves' Hideout\x05\x40!\x09"),
    (0x00A1, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for \x05\x41Ganon's Castle\x05\x40!\x09"),
    (0x00A2, "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x45Bottom of the Well\x05\x40!\x09"),
    (0x00A3, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09"),
    (0x00A5, "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x45Bottom of the Well\x05\x40!\x09"),
    (0x00A6, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09"),
    (0x00A9, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09"),
    (0x00F3, "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x44Treasure Box Shop\x05\x40!\x09"),
    # 0x9019 and 0x901A used above
    # Silver Rupee Messages with count.
    (0x901B, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01staircase room in \x05\x41Dodongo's Cavern\x05\x40!\x01You have found \x05\x41\xF0\x00\x05\x40 so far!\x09"),
    (0x901C, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44spinning scythe room\x05\x40 in the \x05\x44Ice\x01Cavern\x05\x40! You have found \x05\x41\xF0\x01\x05\x40 so far!\x09"),
    (0x901D, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43push block room\x05\x40 in the \x05\x44Ice Cavern\x05\x40!\x01You have found \x05\x41\xF0\x02\x05\x40 so far!\x09"),
    (0x901E, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01basement in the \x05\x45Bottom of the Well\x05\x40!\x01You have found \x05\x41\xF0\x03\x05\x40 so far!\x09"),
    (0x901F, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42scythe shortcut room\x05\x40 in the \x05\x45Shadow\x01Temple\x05\x40! You have found \x05\x41\xF0\x04\x05\x40 so far!\x09"),
    (0x9020, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44invisible blade room\x05\x40 in the \x05\x45Shadow\x01Temple\x05\x40! You have found \x05\x41\xF0\x05\x05\x40 so far!\x09"),
    (0x9021, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46huge pit\x05\x40 in the \x05\x45Shadow Temple\x05\x40!\x01You have found \x05\x41\xF0\x06\x05\x40 so far!\x09"),
    (0x9022, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01room with \x05\x45invisible spikes\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40!\x01You have found \x05\x41\xF0\x07\x05\x40 so far!\x09"),
    (0x9023, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46sloped room\x05\x40 in the \x05\x46Gerudo Training\x01Ground\x05\x40! You have found \x05\x41\xF0\x08\x05\x40 so far!\x09"),
    (0x9024, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x41lava\x01room\x05\x40 in the \x05\x46Gerudo Training Ground\x05\x40!\x01You have found \x05\x41\xF0\x09\x05\x40 so far!\x09"),
    (0x9025, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43water room\x05\x40 in the \x05\x46Gerudo Training\x01Ground\x05\x40! You have found \x05\x41\xF0\x0A\x05\x40 so far!\x09"),
    (0x9026, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x41torch room\x05\x40 in the child side of the\x01\x05\x46Spirit Temple\x05\x40! You have found \x05\x41\xF0\x0B\x05\x40\x01so far!\x09"),
    (0x9027, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42boulder room\x05\x40 in the adult side of the\x01\x05\x46Spirit Temple\x05\x40! You have found \x05\x41\xF0\x0C\x05\x40\x01so far!\x09"),
    (0x9028, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44lobby and adult side\x05\x40 of the \x05\x46Spirit\x01Temple\x05\x40! You have found \x05\x41\xF0\x0D\x05\x40 so far!\x09"),
    (0x9029, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x46sun\x01block room\x05\x40 in the \x05\x46Spirit Temple\x05\x40!\x01You have found \x05\x41\xF0\x0E\x05\x40 so far!\x09"),
    (0x902A, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43climbable wall\x05\x40 in the \x05\x46Spirit Temple\x05\x40!\x01You have found \x05\x41\xF0\x0F\x05\x40 so far!\x09"),
    (0x902B, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46Spirit Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x10\x05\x40 so far!\x09"),
    (0x902C, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44Light Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x11\x05\x40 so far!\x09"),
    (0x902D, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x41Fire\x01Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x12\x05\x40 so far!\x09"),
    (0x902E, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x45Shadow Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x13\x05\x40 so far!\x09"),
    (0x902F, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43Water Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x14\x05\x40 so far!\x09"),
    (0x9030, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42Forest Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x15\x05\x40 so far!\x09"),
    # Silver Rupee messages when all have been collected. IDs are 0x16 after the base messages and calculated in resolve_text_id_silver_rupees. Also used for silver rupee pouches
    (0x9031, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the staircase room in\x01\x05\x41Dodongo's Cavern\x05\x40!\x09"),
    (0x9032, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44spinning scythe room\x05\x40\x01in the \x05\x44Ice Cavern\x05\x40!\x09"),
    (0x9033, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43push block room\x05\x40 in\x01the \x05\x44Ice Cavern\x05\x40!\x09"),
    (0x9034, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the basement in the\x01\x05\x45Bottom of the Well\x05\x40!\x09"),
    (0x9035, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42scythe shortcut room\x05\x40\x01in the \x05\x45Shadow Temple\x05\x40!\x09"),
    (0x9036, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44invisible blade room\x05\x40 in\x01the \x05\x45Shadow Temple\x05\x40!\x09"),
    (0x9037, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46huge pit\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40!\x09"),
    (0x9038, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the room with \x05\x45invisible\x01spikes\x05\x40 in the \x05\x45Shadow Temple\x05\x40!\x09"),
    (0x9039, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sloped room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40!\x09"),
    (0x903A, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41lava room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40!\x09"),
    (0x903B, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43water room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40!\x09"),
    (0x903C, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41torch room\x05\x40 in the\x01child side of the \x05\x46Spirit Temple\x05\x40!\x09"),
    (0x903D, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42boulder room\x05\x40 in the\x01adult side of the \x05\x46Spirit Temple\x05\x40!\x09"),
    (0x903E, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44lobby and adult side\x05\x40\x01of the \x05\x46Spirit Temple\x05\x40!\x09"),
    (0x903F, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sun block room\x05\x40 in the\x01\x05\x46Spirit Temple\x05\x40!\x09"),
    (0x9040, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43climbable wall\x05\x40 in the\x01\x05\x46Spirit Temple\x05\x40!\x09"),
    (0x9041, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46Spirit Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40!\x09"),
    (0x9042, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44Light Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40!\x09"),
    (0x9043, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41Fire Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40!\x09"),
    (0x9044, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x45Shadow Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40!\x09"),
    (0x9045, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43Water Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40!\x09"),
    (0x9046, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42Forest Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40!\x09"),
    # 0x9048 used above
    # Silver Rupee messages for MQ dungeons when all have been collected. Offset 0x2E from the base messages.
    (0x9049, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the staircase room in\x01\x05\x41Dodongo's Cavern\x05\x40! The way to the\x01hanging bridge is open!\x09"),
    # 0x904A, 0x904B, and 0x904C unused
    (0x904D, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42scythe shortcut room\x05\x40\x01in the \x05\x45Shadow Temple\x05\x40! Now you can\x01access the \x05\x42chest\x05\x40 there!\x09"),
    (0x904E, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44invisible blade room\x05\x40 in\x01the \x05\x45Shadow Temple\x05\x40! Now you can\x01access the \x05\x44chest\x05\x40 there!\x09"),
    (0x904F, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46huge pit\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40! A \x05\x46chest\x05\x40 has\x01appeared!\x09"),
    (0x9050, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the room with \x05\x45invisible\x01spikes\x05\x40 in the \x05\x45Shadow Temple\x05\x40! The\x01way to the \x05\x45Stalfos room\x05\x40 is open!\x09"),
    (0x9051, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sloped room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! The way to\x01the room with the \x05\x46heavy block\x05\x40 is\x04open!\x09"),
    (0x9052, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41lava room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! The way to\x01the \x05\x41water room\x05\x40 is open!\x09"),
    (0x9053, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43water room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! A \x05\x43chest\x05\x40\x01has appeared!\x09"),
    # 0x9054 and 0x9055 unused
    (0x9056, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44lobby and adult side\x05\x40\x01of the \x05\x46Spirit Temple\x05\x40! A \x05\x44chest\x05\x40 has\x01appeared!\x09"),
    # 0x9057 unused
    (0x9058, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43climbable wall\x05\x40 in the\x01\x05\x46Spirit Temple\x05\x40! The way to the\x01\x05\x43upstairs\x05\x40 is open!\x09"),
    # 0x9059 and 0x905A unused
    (0x905B, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41Fire Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40! The way to the \x05\x41final room\x05\x40 is\x01open!\x09"),
    (0x905C, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x45Shadow Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40! The way to the \x05\x45final\x01room\x05\x40 is open!\x09"),
    (0x905D, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43Water Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40! The way to the \x05\x43final\x01room\x05\x40 is open!\x09"),
    # 0x905E unused
    # Silver Rupee messages for non-MQ dungeons when all have been collected. Offset 0x44 from the base messages.
    # 0x905F unused
    (0x9060, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44spinning scythe room\x05\x40\x01in the \x05\x44Ice Cavern\x05\x40! The way to the\x01\x05\x44map room\x05\x40 is open!\x09"),
    (0x9061, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43push block room\x05\x40 in\x01the \x05\x44Ice Cavern\x05\x40! The way to the \x05\x43final\x01room\x05\x40 is open!\x09"),
    (0x9062, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the basement in the\x01\x05\x45Bottom of the Well\x05\x40! Now you can\x01get back to the upper level!\x09"),
    (0x9063, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42scythe shortcut room\x05\x40\x01in the \x05\x45Shadow Temple\x05\x40! Now you can\x01access the \x05\x42chest\x05\x40 there!\x09"),
    # 0x9064 unused
    (0x9065, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46huge pit\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40! The way to the\x01room with \x05\x46falling spikes\x05\x40 is open!\x09"),
    (0x9066, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the room with \x05\x45invisible\x01spikes\x05\x40 in the \x05\x45Shadow Temple\x05\x40! The\x01way to the room with the \x05\x45giant pot\x05\x40\x04is open!\x09"),
    (0x9067, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sloped room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! The way to\x01the room with the \x05\x46heavy block\x05\x40 is\x04open!\x09"),
    (0x9068, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41lava room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! The way to\x01the \x05\x41water room\x05\x40 is open!\x09"),
    (0x9069, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43water room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! A \x05\x43chest\x05\x40\x01has appeared!\x09"),
    (0x906A, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41torch room\x05\x40 in the\x01child side of the \x05\x46Spirit Temple\x05\x40! Now\x01the \x05\x41metal bridge\x05\x40 there is lowered!\x09"),
    (0x906B, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42boulder room\x05\x40 in the\x01adult side of the \x05\x46Spirit Temple\x05\x40! Now\x01you can access the \x05\x42chest\x05\x40 there!\x09"),
    # 0x906C unused
    (0x906D, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sun block room\x05\x40 in the\x01\x05\x46Spirit Temple\x05\x40! The \x05\x46torch\x05\x40 has been\x01lit!\x09"),
    # 0x906E unused
    (0x906F, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46Spirit Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40! The way to the \x05\x46second room\x05\x40\x01is open!\x09"),
    (0x9070, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44Light Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40! The way to the \x05\x44final room\x05\x40 is\x01open!\x09"),
    (0x9071, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41Fire Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40! The way to the \x05\x41final room\x05\x40 is\x01open!\x09"),
    # 0x9072 and 0x9073 unused
    (0x9074, "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42Forest Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40! The way to the \x05\x42final\x01room\x05\x40 is open!\x09"),
    # Silver Rupee messages without count. Offset 0x5A from the base messages.
    (0x9075, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01staircase room in \x05\x41Dodongo's Cavern\x05\x40!\x09"),
    (0x9076, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44spinning scythe room\x05\x40 in the \x05\x44Ice\x01Cavern\x05\x40!\x09"),
    (0x9077, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43push block room\x05\x40 in the \x05\x44Ice Cavern\x05\x40!\x09"),
    (0x9078, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01basement in the \x05\x45Bottom of the Well\x05\x40!\x09"),
    (0x9079, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42scythe shortcut room\x05\x40 in the \x05\x45Shadow\x01Temple\x05\x40!\x09"),
    (0x907A, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44invisible blade room\x05\x40 in the \x05\x45Shadow\x01Temple\x05\x40!\x09"),
    (0x907B, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46huge pit\x05\x40 in the \x05\x45Shadow Temple\x05\x40!\x09"),
    (0x907C, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01room with \x05\x45invisible spikes\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40!\x09"),
    (0x907D, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46sloped room\x05\x40 in the \x05\x46Gerudo Training\x01Ground\x05\x40!\x09"),
    (0x907E, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x41lava\x01room\x05\x40 in the \x05\x46Gerudo Training Ground\x05\x40!\x09"),
    (0x907F, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43water room\x05\x40 in the \x05\x46Gerudo Training\x01Ground\x05\x40!\x09"),
    (0x9080, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x41torch room\x05\x40 in the child side of the\x01\x05\x46Spirit Temple\x05\x40!\x09"),
    (0x9081, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42boulder room\x05\x40 in the adult side of the\x01\x05\x46Spirit Temple\x05\x40!\x09"),
    (0x9082, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44lobby and adult side\x05\x40 of the \x05\x46Spirit\x01Temple\x05\x40!\x09"),
    (0x9083, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x46sun\x01block room\x05\x40 in the \x05\x46Spirit Temple\x05\x40!\x09"),
    (0x9084, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43climbable wall\x05\x40 in the \x05\x46Spirit Temple\x05\x40!\x09"),
    (0x9085, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46Spirit Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09"),
    (0x9086, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44Light Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09"),
    (0x9087, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x41Fire\x01Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09"),
    (0x9088, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x45Shadow Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09"),
    (0x9089, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43Water Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09"),
    (0x908A, "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42Forest Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09"),
]

dungeon_names = [
    None, # Unused Deku Tree
    None, # Unused Dodongos Cavern
    None, # Unused Jabu
    "the \x05\x42Forest Temple\x05\x40",
    "the \x05\x41Fire Temple\x05\x40",
    "the \x05\x43Water Temple\x05\x40",
    "the \x05\x46Spirit Temple\x05\x40",
    "the \x05\x45Shadow Temple\x05\x40",
    "the \x05\x45Bottom of the Well\x05\x40",
    None, # Unused Ice Cavern
    None, # Unused Ganons Castle Tower
    "the \x05\x46Gerudo Training\x01Ground\x05\x40",
    "the \x05\x46Thieves' Hideout\x05\x40",
    "\x05\x41Ganon's Castle\x05\x40",
    None, # Unused Tower Collapse
    None, # Unused Castle Collapse
    "the \x05\x44Treasure Box Shop\x05\x40",
]

i = 0x9101
# Add small key messages starting at 0x9101
# These are grouped in dungeon order as follows:
#       0x9101 - Small key messages for the first one collected
#       0x9112 - Small key messages containing the count
#       0x9123 - Small key messages for collecting more than enough

for dungeon_name in dungeon_names:
    if dungeon_name is not None:
        KEYSANITY_MESSAGES.append((i, f"\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for {dungeon_name}!\x01It's your \x05\x41first\x05\x40 one!\x09"))
    i += 1
c = 0
for dungeon_name in dungeon_names:
    if dungeon_name is not None:
        KEYSANITY_MESSAGES.append((i, f"\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for {dungeon_name}!\x01You've collected \x05\x41" + "\xF1" + c.to_bytes(1, 'big').decode() + "\x05\x40 of them.\x09"))
    i += 1
    c += 1
for dungeon_name in dungeon_names:
    if dungeon_name is not None:
        KEYSANITY_MESSAGES.append((i, f"\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for {dungeon_name}!\x01You already have enough keys.\x09"))
    i += 1

# Add key ring messages starting at 0x9200
i = 0x9200
for dungeon_name in dungeon_names:
    if dungeon_name is not None:
        KEYSANITY_MESSAGES.append((i, f"\x13\x77\x08You found a \x05\x41Small Key Ring\x05\x40\x01for {dungeon_name}!\x09"))
    i += 1

key_rings_with_bk_dungeon_names = [
    "the \x05\x42Forest Temple\x05\x40",
    "the \x05\x41Fire Temple\x05\x40",
    "the \x05\x43Water Temple\x05\x40",
    "the \x05\x46Spirit Temple\x05\x40",
    "the \x05\x45Shadow Temple\x05\x40"
]
for dungeon_name in key_rings_with_bk_dungeon_names:
    KEYSANITY_MESSAGES.append((i, f"\x13\x77\x08You found a \x05\x41Key Ring\x05\x40\x01for {dungeon_name}!\x09\x01It includes the \x05\x41Boss Key\x05\x40!"))
    i += 1

COLOR_MAP: dict[str, str] = {
    'White':      '\x40',
    'Red':        '\x41',
    'Green':      '\x42',
    'Blue':       '\x43',
    'Light Blue': '\x44',
    'Pink':       '\x45',
    'Yellow':     '\x46',
    'Black':      '\x47',
}

MISC_MESSAGES: list[tuple[int, tuple[str | bytearray, int]]] = [
    (0x0032, ("\x08\x13\x02You got \x05\x41Bombs\x05\x40!\x01If you see something\x01suspicious, bomb it!", 0x23)),
    (0x0033, ("\x08\x13\x09You got \x05\x41Bombchus\x05\x40!", 0x23)),
    (0x0034, ("\x08\x13\x01You got a \x05\x41Deku Nut\x05\x40!", 0x23)),
    (0x0037, ("\x08\x13\x00You got a \x05\x41Deku Stick\x05\x40!", 0x23)),
    (0x0043, ("\x08\x13\x15You got a \x05\x41Red Potion\x05\x40!\x01It will restore your health", 0x23)),
    (0x0044, ("\x08\x13\x16You got a \x05\x42Green Potion\x05\x40!\x01It will restore your magic.", 0x23)),
    (0x0045, ("\x08\x13\x17You got a \x05\x43Blue Potion\x05\x40!\x01It will recover your health\x01and magic.", 0x23)),
    (0x0046, ("\x08\x13\x18You caught a \x05\x41Fairy\x05\x40 in a bottle!\x01It will revive you\x01the moment you run out of life \x01energy.", 0x23)),
    (0x0047, ("\x08\x13\x19You got a \x05\x41Fish\x05\x40!\x01It looks so fresh and\x01delicious!", 0x23)),
    (0x004C, ("\x08\x13\x3EYou got a \x05\x44Deku Shield\x05\x40!", 0x23)),
    (0x004D, ("\x08\x13\x3FYou got a \x05\x44Hylian Shield\x05\x40!", 0x23)),
    (0x0050, ("\x08\x13\x42You got a \x05\x41Goron Tunic\x05\x40!\x01Going to a hot place? No worry!", 0x23)),
    (0x0051, ("\x08\x13\x43You got a \x05\x43Zora Tunic\x05\x40!\x01Wear it, and you won't drown\x01underwater.", 0x23)),
    (0x0055, ("\x08You got a \x05\x45Recovery Heart\x05\x40!\x01Your life energy is recovered!", 0x23)),
    (0x005D, ("\x08\x13\x1CYou put a \x05\x44Blue Fire\x05\x40\x01into the bottle!\x01This is a cool flame you can\x01use on red ice.", 0x23)),
    (0x007A, ("\x08\x13\x1DYou put a \x05\x41Bug \x05\x40in the bottle!\x01This kind of bug prefers to\x01live in small holes in the ground.", 0x23)),
    (0x0097, ("\x08\x13\x20You caught a \x05\x41Poe \x05\x40in a bottle!\x01Something good might happen!", 0x23)),
    (0x00DC, ("\x08\x13\x58You got \x05\x41Deku Seeds\x05\x40!\x01Use these as bullets\x01for your Slingshot.", 0x23)),
    (0x00E6, ("\x08You got a \x05\x46bundle of arrows\x05\x40!", 0x23)),
    (0x00F9, ("\x08\x13\x1EYou put a \x05\x41Big Poe \x05\x40in a bottle!\x01Let's sell it at the \x05\x41Ghost Shop\x05\x40!\x01Something good might happen!", 0x23)),
    (0x507B, (bytearray(
            b"\x08I tell you, I saw him!\x04"
            b"\x08I saw the ghostly figure of Damp\x96\x01"
            b"the gravekeeper sinking into\x01"
            b"his grave. It looked like he was\x01"
            b"holding some kind of \x05\x41treasure\x05\x40!\x02"
            ), 0x00)),
    (0x0422, ("They say that once \x05\x41Morpha's Curse\x05\x40\x01is lifted, striking \x05\x42this stone\x05\x40 can\x01shift the tides of \x05\x44Lake Hylia\x05\x40.\x02", 0x23)),
    (0x401C, ("Please find my dear \05\x41Princess Ruto\x05\x40\x01immediately... Zora!\x12\x68\x7A", 0x03)),
    (0x9100, ("I am out of goods now.\x01Sorry!\x04The mark that will lead you to\x01the Spirit Temple is the \x05\x41flag on\x01the left \x05\x40outside the shop.\x01Be seeing you!\x02", 0x00)),
    (0x0451, ("\x12\x68\x7AMweep\x07\x04\x52", 0x23)),
    (0x0452, ("\x12\x68\x7AMweep\x07\x04\x53", 0x23)),
    (0x0453, ("\x12\x68\x7AMweep\x07\x04\x54", 0x23)),
    (0x0454, ("\x12\x68\x7AMweep\x07\x04\x55", 0x23)),
    (0x0455, ("\x12\x68\x7AMweep\x07\x04\x56", 0x23)),
    (0x0456, ("\x12\x68\x7AMweep\x07\x04\x57", 0x23)),
    (0x0457, ("\x12\x68\x7AMweep\x07\x04\x58", 0x23)),
    (0x0458, ("\x12\x68\x7AMweep\x07\x04\x59", 0x23)),
    (0x0459, ("\x12\x68\x7AMweep\x07\x04\x5A", 0x23)),
    (0x045A, ("\x12\x68\x7AMweep\x07\x04\x5B", 0x23)),
    (0x045B, ("\x12\x68\x7AMweep", 0x23)),
    (0x045C, ("Come back when you have\x01your own bow and you'll get the\x01\x05\x41real prize\x05\x40!\x0E\x78", 0x00)),
    (0x6013, ("Hey, newcomer!\x04Want me to throw you in jail?\x01\x01\x1B\x05\x42No\x01Yes\x05\x40", 0x00)),
]


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


def parse_control_codes(text: list[int] | bytearray | str) -> list[TextCode]:
    if isinstance(text, list):
        text_bytes = text
    elif isinstance(text, bytearray):
        text_bytes = list(text)
    else:
        text_bytes = encode_text_string(text)

    text_codes = []
    index = 0
    while index < len(text_bytes):
        next_char = text_bytes[index]
        data = 0
        index += 1
        if next_char in CONTROL_CODES:
            extra_bytes = CONTROL_CODES[next_char][1]
            if extra_bytes > 0:
                data = bytes_to_int(text_bytes[index: index + extra_bytes])
                index += extra_bytes
        text_code = TextCode(next_char, data)
        text_codes.append(text_code)
        if text_code.code == 0x02:  # message end code
            break

    return text_codes


# holds a single character or control code of a string
class TextCode:
    def __init__(self, code: int, data: int) -> None:
        self.code: int = code
        if code in CONTROL_CODES:
            self.type = CONTROL_CODES[code][0]
        else:
            self.type = 'character'
        self.data: int = data

    def display(self) -> str:
        if self.code in CONTROL_CODES:
            return CONTROL_CODES[self.code][2](self.data)
        elif self.code in SPECIAL_CHARACTERS:
            return SPECIAL_CHARACTERS[self.code]
        elif self.code >= 0x7F:
            return '?'
        else:
            return chr(self.code)

    def get_python_string(self) -> str:
        if self.code in CONTROL_CODES:
            ret = ''
            data = self.data
            for _ in range(0, CONTROL_CODES[self.code][1]):
                ret = f'\\x{data & 0xFF:02X}{ret}'
                data = data >> 8
            ret = f'\\x{self.code:02X}{ret}'
            return ret
        elif self.code in SPECIAL_CHARACTERS:
            return f'\\x{self.code:02X}'
        elif self.code >= 0x7F:
            return '?'
        else:
            return chr(self.code)

    def get_string(self) -> str:
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

    def size(self) -> int:
        size = 1
        if self.code in CONTROL_CODES:
            size += CONTROL_CODES[self.code][1]
        return size

    # writes the code to the given offset, and returns the offset of the next byte
    def write(self, rom: Rom, text_start: int, offset: int) -> int:
        rom.write_byte(text_start + offset, self.code)

        extra_bytes = 0
        if self.code in CONTROL_CODES:
            extra_bytes = CONTROL_CODES[self.code][1]
            bytes_to_write = int_to_bytes(self.data, extra_bytes)
            rom.write_bytes(text_start + offset + 1, bytes_to_write)

        return offset + 1 + extra_bytes

    __str__ = __repr__ = display


# holds a single message, and all its data
class Message:
    def __init__(self, raw_text: list[int] | bytearray | str, index: int, id: int, opts: int, offset: int, length: int) -> None:
        if isinstance(raw_text, str):
            raw_text = encode_text_string(raw_text)
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

    # check if this is an unused message that just contains it's own id as text
    def is_id_message(self) -> bool:
        if self.unpadded_length != 5 or self.id == 0xFFFC:
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

    def parse_text(self) -> None:
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
        ending_codes = [0x02, 0x07, 0x0A, 0x0B, 0x0E, 0x10]
        box_breaks = [0x04, 0x0C]
        slows_text = [0x08, 0x09, 0x14]
        slow_icons = [0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x04, 0x02]

        text_codes = []
        instant_text_code = TextCode(0x08, 0)

        # # speed the text
        if speed_up_text:
            text_codes.append(instant_text_code) # allow instant

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
                    self.id == 0x706C or  # rauru ending text
                    self.id == 0x70DD or  # ganondorf ending text
                    self.id in (0x706F, 0x7091, 0x7092, 0x7093, 0x7094, 0x7095, 0x7070)  # zelda ending text
                ):
                    text_codes.append(code)
                    text_codes.append(instant_text_code)  # allow instant
                else:
                    text_codes.append(TextCode(0x04, 0))  # un-delayed break
                    text_codes.append(instant_text_code)  # allow instant
            elif speed_up_text and code.code == 0x13 and code.data in slow_icons:
                text_codes.append(code)
                text_codes.pop(find_last(text_codes, instant_text_code))  # remove last instance of instant text
                text_codes.append(instant_text_code)  # allow instant
            else:
                text_codes.append(code)

        if replace_ending:
            if ending:
                if speed_up_text and ending.code == 0x10:  # ocarina
                    text_codes.append(TextCode(0x09, 0))  # disallow instant text
                text_codes.append(ending)  # write special ending
            text_codes.append(TextCode(0x02, 0))  # write end code

        self.text_codes = text_codes

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
            offset = TextCode(0x00, 0).write(rom, text_start, offset) # pad to 4 byte align

        return offset

    # read a single message from rom
    @classmethod
    def from_rom(cls, rom: Rom, index: int, eng: bool = True) -> Message:
        if eng:
            table_start = ENG_TABLE_START
            text_start = ENG_TEXT_START
        else:
            table_start = JPN_TABLE_START
            text_start = JPN_TEXT_START
        entry_offset = table_start + 8 * index
        entry = rom.read_bytes(entry_offset, 8)
        next = rom.read_bytes(entry_offset + 8, 8)

        id = bytes_to_int(entry[0:2])
        opts = entry[2]
        offset = bytes_to_int(entry[5:8])
        length = bytes_to_int(next[5:8]) - offset

        raw_text = rom.read_bytes(text_start + offset, length)

        return cls(raw_text, index, id, opts, offset, length)

    @classmethod
    def from_string(cls, text: str, id: int = 0, opts: int = 0x00) -> Message:
        bytes = text + "\x02"
        return cls(bytes, 0, id, opts, 0, len(bytes) + 1)

    @classmethod
    def from_bytearray(cls, text: bytearray, id: int = 0, opts: int = 0x00) -> Message:
        bytes = list(text) + [0x02]
        return cls(bytes, 0, id, opts, 0, len(bytes) + 1)

    __str__ = __repr__ = display


# wrapper for updating the text of a message, given its message id
# if the id does not exist in the list, then it will add it
# Checks if the message being updated is a newly added message in order to prevent duplicates.
# Use allow_duplicates=True if the same message is purposely updated multiple times
def update_message_by_id(messages: list[Message], id: int, text: bytearray | str, opts: Optional[int] = None, allow_duplicates: bool = False):
    # Check is we have previously added/modified this message.
    if id in new_messages and not allow_duplicates:
        raise Exception(f'Attempting to add duplicate message {hex(id)}')

    new_messages.append(id)
    # get the message index
    index = next( (m.index for m in messages if m.id == id), -1)
    # update if it was found
    if index >= 0:
        update_message_by_index(messages, index, text, opts)
    else:
        add_message(messages, text, id, opts)


# Gets the message by its ID. Returns None if the index does not exist
def get_message_by_id(messages: list[Message], id: int) -> Optional[Message]:
    # get the message index
    index = next( (m.index for m in messages if m.id == id), -1)
    if index >= 0:
        return messages[index]
    else:
        return None


# wrapper for updating the text of a message, given its index in the list
def update_message_by_index(messages: list[Message], index: int, text: bytearray | str, opts: Optional[int] = None) -> None:
    if opts is None:
        opts = messages[index].opts

    if isinstance(text, bytearray):
        messages[index] = Message.from_bytearray(text, messages[index].id, opts)
    else:
        messages[index] = Message.from_string(text, messages[index].id, opts)
    messages[index].index = index


# wrapper for adding a string message to a list of messages
def add_message(messages: list[Message], text: bytearray | str, id: int = 0, opts: int = 0x00) -> None:
    if isinstance(text, bytearray):
        messages.append(Message.from_bytearray(text, id, opts))
    else:
        messages.append(Message.from_string(text, id, opts))
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


def make_player_message(text: str) -> str:
    player_text = '\x05\x42\xF2\x05\x40'
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
        new_text = line_wrap(new_text, True, False, False)

    return new_text


# reduce item message sizes and add new item messages
# make sure to call this AFTER move_shop_item_messages()
def update_item_messages(messages: list[Message], world: World) -> None:
    new_item_messages = ITEM_MESSAGES + KEYSANITY_MESSAGES
    for id, text in new_item_messages:
        if world.settings.world_count > 1:
            update_message_by_id(messages, id, make_player_message(text), 0x23)
        else:
            update_message_by_id(messages, id, text, 0x23)

    for id, (text, opt) in MISC_MESSAGES:
        update_message_by_id(messages, id, text, opt)

# run all keysanity related patching to add messages for dungeon specific items
def add_item_messages(messages: list[Message], shop_items: Iterable[ShopItem], world: World) -> None:
    move_shop_item_messages(messages, shop_items)
    update_item_messages(messages, world)


# reads each of the game's messages into a list of Message objects
def read_messages(rom: Rom) -> list[Message]:
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

        messages.append(Message.from_rom(rom, index))

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
def repack_messages(rom: Rom, messages: list[Message], permutation: Optional[list[int]] = None,
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
        [message_id for (message_id, message) in KEYSANITY_MESSAGES] + shuffle_messages.shop_item_messages +
        shuffle_messages.scrubs_message_ids +
        [0x5036, 0x70F5] # Chicken count and poe count respectively
    )

    permutation = [i for i, _ in enumerate(messages)]

    def is_exempt(m: Message) -> bool:
        hint_ids = (
            GOSSIP_STONE_MESSAGES + TEMPLE_HINTS_MESSAGES +
            [data['id'] for data in misc_item_hint_table.values()] +
            [data['id'] for data in misc_location_hint_table.values()] +
            [message_id for (message_id, message) in KEYSANITY_MESSAGES] +
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

    if world.settings.logic_rules != "glitched": # Entrances not set on glitched logic so following code will error
        for id, entr in msg_list.items():
            if 'warp_songs_and_owls' in world.settings.misc_hints or not world.settings.warp_songs:
                destination = world.get_entrance(entr).connected_region
                destination_name = HintArea.at(destination)
                color = COLOR_MAP[destination_name.color]
                if destination_name.preposition(True) is not None:
                    destination_name = f'to {destination_name}'
            else:
                destination_name = 'to a mysterious place'
                color = COLOR_MAP['White']

            new_msg = f"\x08\x05{color}Warp {destination_name}?\x05\40\x09\x01\x01\x1b\x05\x42OK\x01No\x05\40"
            update_message_by_id(messages, id, new_msg)

    if world.settings.owl_drops:
        for id, entr in owl_messages.items():
            if 'warp_songs_and_owls' in world.settings.misc_hints:
                destination = world.get_entrance(entr).connected_region
                destination_name = HintArea.at(destination)
                color = COLOR_MAP[destination_name.color]
                if destination_name.preposition(True) is not None:
                    destination_name = f'to {destination_name}'
            else:
                destination_name = 'to a mysterious place'
                color = COLOR_MAP['White']

            new_msg = f"Hold on to my talons! I'll fly you\x01\x08\x05{color}{destination_name}\x05\40\x09!"
            update_message_by_id(messages, id, new_msg)
