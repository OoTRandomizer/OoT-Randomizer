from __future__ import annotations
import json
from typing import Any

# Property of the Language
lang_property = {
    "base": "en", # base of the language [en, jp]
    "display_name": "English", # Name that displayed as selection
    "description": "Play with English language.", # Not implemented, it will be description which you can see while hovering above
    "align_text": "Left" # alignation of the texts [Left, Center, Right]
}

# DON'T CHANGE THESE VV
color_white = "#00" if lang_property["base"] == "jp" else "\x05\x40" 
# DON'T CHANGE THESE ^^

# Prefix property for the language
prefix = {
    "gender":["no_gender"],
    "prefix":{
        "definite":{
            "no_gender":"the"
            },
        "indefinite":{
            "next_first":["a","e","i","o","u"],
            "no_gender":["a","an"]
        }
    }
}

# Messages for Items
# Format: {"id": int, "text": str}
ITEM_MESSAGES = [
    {
        "id": 0x0001,
        "text": "\x08\x06\x30\x05\x41TEXT ID ERROR!\x05\x40",
    }, # Fallback text
    {
        "id": 0x9001,
        "text": "\x08\x13\x2DYou borrowed a \x05\x41Pocket Egg\x05\x40!\x01A Pocket Cucco will hatch from\x01it overnight. Be sure to give it\x01back.",
    },
    {
        "id": 0x0002,
        "text": "\x08\x13\x2FYou returned the Pocket Cucco\x01and got \x05\x41Cojiro\x05\x40 in return!\x01Unlike other Cuccos, Cojiro\x01rarely crows.",
    },
    {
        "id": 0x0003,
        "text": "\x08\x13\x30You got an \x05\x41Odd Mushroom\x05\x40!\x01It is sure to spoil quickly! Take\x01it to the Kakariko Potion Shop.",
    },
    {
        "id": 0x0004,
        "text": "\x08\x13\x31You received an \x05\x41Odd Potion\x05\x40!\x01It may be useful for something...\x01Hurry to the Lost Woods!",
    },
    {
        "id": 0x0005,
        "text": "\x08\x13\x32You returned the Odd Potion \x01and got the \x05\x41Poacher's Saw\x05\x40!\x01The young punk guy must have\x01left this.",
    },
    {
        "id": 0x0007,
        "text": "\x08\x13\x48You got a \x01\x05\x41Deku Seeds Bullet Bag\x05\x40.\x01This bag can hold up to \x05\x4640\x05\x40\x01slingshot bullets.",
    },
    {
        "id": 0x0008,
        "text": "\x08\x13\x33You traded the Poacher's Saw \x01for a \x05\x41Broken Goron's Sword\x05\x40!\x01Visit Biggoron to get it repaired!",
    },
    {
        "id": 0x0009,
        "text": "\x08\x13\x34You checked in the Broken \x01Goron's Sword and received a \x01\x05\x41Prescription\x05\x40!\x01Go see King Zora!",
    },
    {
        "id": 0x000A,
        "text": "\x08\x13\x37The Biggoron's Sword...\x01You got a \x05\x41Claim Check \x05\x40for it!\x01You can't wait for the sword!",
    },
    {
        "id": 0x000B,
        "text": "\x08\x13\x2EYou got a \x05\x41Pocket Cucco, \x05\x40one\x01of Anju's prized hens! It fits \x01in your pocket.",
    },
    {
        "id": 0x000C,
        "text": "\x08\x13\x3DYou got the \x05\x41Biggoron's Sword\x05\x40!\x01This blade was forged by a \x01master smith and won't break!",
    },
    {
        "id": 0x000D,
        "text": "\x08\x13\x35You used the Prescription and\x01received an \x05\x41Eyeball Frog\x05\x40!\x01Be quick and deliver it to Lake \x01Hylia!",
    },
    {
        "id": 0x000E,
        "text": "\x08\x13\x36You traded the Eyeball Frog \x01for the \x05\x41World's Finest Eye Drops\x05\x40!\x01Hurry! Take them to Biggoron!",
    },
    {
        "id": 0x0010,
        "text": "\x08\x13\x25You got a \x05\x41Skull Mask\x05\x40.\x01You feel like a monster while you\x01wear this mask!",
    },
    {
        "id": 0x0011,
        "text": "\x08\x13\x26You got a \x05\x41Spooky Mask\x05\x40.\x01You can scare many people\x01with this mask!",
    },
    {
        "id": 0x0012,
        "text": "\x08\x13\x24You got a \x05\x41Keaton Mask\x05\x40.\x01You'll be a popular guy with\x01this mask on!",
    },
    {
        "id": 0x0013,
        "text": "\x08\x13\x27You got a \x05\x41Bunny Hood\x05\x40.\x01The hood's long ears are so\x01cute!",
    },
    {
        "id": 0x0014,
        "text": "\x08\x13\x28You got a \x05\x41Goron Mask\x05\x40.\x01It will make your head look\x01big, though.",
    },
    {
        "id": 0x0015,
        "text": "\x08\x13\x29You got a \x05\x41Zora Mask\x05\x40.\x01With this mask, you can\x01become one of the Zoras!",
    },
    {
        "id": 0x0016,
        "text": "\x08\x13\x2AYou got a \x05\x41Gerudo Mask\x05\x40.\x01This mask will make you look\x01like...a girl?",
    },
    {
        "id": 0x0017,
        "text": "\x08\x13\x2BYou got a \x05\x41Mask of Truth\x05\x40.\x01Show it to many people!",
    },
    {
        "id": 0x0030,
        "text": "\x08\x13\x06You found the \x05\x41Fairy Slingshot\x05\x40!",
    },
    {
        "id": 0x0031,
        "text": "\x08\x13\x03You found the \x05\x41Fairy Bow\x05\x40!",
    },
    {
        "id": 0x0035,
        "text": "\x08\x13\x0EYou found the \x05\x41Boomerang\x05\x40!",
    },
    {
        "id": 0x0036,
        "text": "\x08\x13\x0AYou found the \x05\x41Hookshot\x05\x40!\x01It's a spring-loaded chain that\x01you can cast out to hook things.",
    },
    {
        "id": 0x0038,
        "text": "\x08\x13\x11You found the \x05\x41Megaton Hammer\x05\x40!\x01It's so heavy, you need to\x01use two hands to swing it!",
    },
    {
        "id": 0x0039,
        "text": "\x08\x13\x0FYou found the \x05\x41Lens of Truth\x05\x40!\x01Mysterious things are hidden\x01everywhere!",
    },
    {
        "id": 0x003A,
        "text": "\x08\x13\x08You found the \x05\x41Ocarina of Time\x05\x40!\x01It glows with a mystical light...",
    },
    {
        "id": 0x003C,
        "text": "\x08\x13\x67You received the \x05\x41Fire\x01Medallion\x05\x40!\x01Darunia awakens as a Sage and\x01adds his power to yours!",
    },
    {
        "id": 0x003D,
        "text": "\x08\x13\x68You received the \x05\x43Water\x01Medallion\x05\x40!\x01Ruto awakens as a Sage and\x01adds her power to yours!",
    },
    {
        "id": 0x003E,
        "text": "\x08\x13\x66You received the \x05\x42Forest\x01Medallion\x05\x40!\x01Saria awakens as a Sage and\x01adds her power to yours!",
    },
    {
        "id": 0x003F,
        "text": "\x08\x13\x69You received the \x05\x46Spirit\x01Medallion\x05\x40!\x01Nabooru awakens as a Sage and\x01adds her power to yours!",
    },
    {
        "id": 0x0040,
        "text": "\x08\x13\x6BYou received the \x05\x44Light\x01Medallion\x05\x40!\x01Rauru the Sage adds his power\x01to yours!",
    },
    {
        "id": 0x0041,
        "text": "\x08\x13\x6AYou received the \x05\x45Shadow\x01Medallion\x05\x40!\x01Impa awakens as a Sage and\x01adds her power to yours!",
    },
    {
        "id": 0x0042,
        "text": "\x08\x13\x14You got an \x05\x41Empty Bottle\x05\x40!\x01You can put something in this\x01bottle.",
    },
    {
        "id": 0x0048,
        "text": "\x08\x13\x10You got a \x05\x41Magic Bean\x05\x40!\x01Find a suitable spot for a garden\x01and plant it.",
    },
    {
        "id": 0x9048,
        "text": "\x08\x13\x10You got a \x05\x41Pack of Magic Beans\x05\x40!\x01Find suitable spots for a garden\x01and plant them.",
    },
    {
        "id": 0x004A,
        "text": "\x08\x13\x07You received the \x05\x41Fairy Ocarina\x05\x40!\x01This is a memento from Saria.",
    },
    {
        "id": 0x004B,
        "text": "\x08\x13\x3DYou got the \x05\x42Giant's Knife\x05\x40!\x01Hold it with both hands to\x01attack! It's so long, you\x01can't use it with a \x05\x44shield\x05\x40.",
    },
    {
        "id": 0x004E,
        "text": "\x08\x13\x40You found the \x05\x44Mirror Shield\x05\x40!\x01The shield's polished surface can\x01reflect light or energy.",
    },
    {
        "id": 0x004F,
        "text": "\x08\x13\x0BYou found the \x05\x41Longshot\x05\x40!\x01It's an upgraded Hookshot.\x01It extends \x05\x41twice\x05\x40 as far!",
    },
    {
        "id": 0x0052,
        "text": "\x08You got a \x05\x42Magic Jar\x05\x40!\x01Your Magic Meter is filled!",
    },
    {
        "id": 0x0053,
        "text": "\x08\x13\x45You got the \x05\x41Iron Boots\x05\x40!\x01So heavy, you can't run.\x01So heavy, you can't float.",
    },
    {
        "id": 0x0054,
        "text": "\x08\x13\x46You got the \x05\x41Hover Boots\x05\x40!\x01With these mysterious boots\x01you can hover above the ground.",
    },
    {
        "id": 0x0056,
        "text": "\x08\x13\x4BYou upgraded your quiver to a\x01\x05\x41Big Quiver\x05\x40!\x01Now you can carry more arrows-\x01\x05\x4640 \x05\x40in total!",
    },
    {
        "id": 0x0057,
        "text": "\x08\x13\x4CYou upgraded your quiver to\x01the \x05\x41Biggest Quiver\x05\x40!\x01Now you can carry to a\x01maximum of \x05\x4650\x05\x40 arrows!",
    },
    {
        "id": 0x0058,
        "text": "\x08\x13\x4DYou found a \x05\x41Bomb Bag\x05\x40!\x01You found \x05\x4120 Bombs\x05\x40 inside!",
    },
    {
        "id": 0x0059,
        "text": "\x08\x13\x4EYou got a \x05\x41Big Bomb Bag\x05\x40!\x01Now you can carry more \x01Bombs, up to a maximum of \x05\x4630\x05\x40!",
    },
    {
        "id": 0x005A,
        "text": "\x08\x13\x4FYou got the \x01\x05\x41Biggest Bomb Bag\x05\x40!\x01Now, you can carry up to \x01\x05\x4640\x05\x40 Bombs!",
    },
    {
        "id": 0x005B,
        "text": "\x08\x13\x51You found the \x05\x43Silver Gauntlets\x05\x40!\x01You feel the power to lift\x01big things with it!",
    },
    {
        "id": 0x005C,
        "text": "\x08\x13\x52You found the \x05\x43Golden Gauntlets\x05\x40!\x01You can feel even more power\x01coursing through your arms!",
    },
    {
        "id": 0x005E,
        "text": "\x08\x13\x56You got an \x05\x43Adult's Wallet\x05\x40!\x01Now you can hold\x01up to \x05\x46200\x05\x40 \x05\x46Rupees\x05\x40.",
    },
    {
        "id": 0x005F,
        "text": "\x08\x13\x57You got a \x05\x43Giant's Wallet\x05\x40!\x01Now you can hold\x01up to \x05\x46500\x05\x40 \x05\x46Rupees\x05\x40.",
    },
    {
        "id": 0x0060,
        "text": "\x08\x13\x77You found a \x05\x41Small Key\x05\x40!\x01This key will open a locked \x01door. You can use it only\x01in this dungeon.",
    },
    {
        "id": 0x0066,
        "text": "\x08\x13\x76You found the \x05\x41Dungeon Map\x05\x40!\x01It's the map to this dungeon.",
    },
    {
        "id": 0x0067,
        "text": "\x08\x13\x75You found the \x05\x41Compass\x05\x40!\x01Now you can see the locations\x01of many hidden things in the\x01dungeon!",
    },
    {
        "id": 0x0068,
        "text": "\x08\x13\x6FYou obtained the \x05\x41Stone of Agony\x05\x40!\x01If you equip a \x05\x44Rumble Pak\x05\x40, it\x01will react to nearby...secrets.",
    },
    {
        "id": 0x0069,
        "text": "\x08\x13\x23You received \x05\x41Zelda's Letter\x05\x40!\x01Wow! This letter has Princess\x01Zelda's autograph!",
    },
    {
        "id": 0x006C,
        "text": "\x08\x13\x49Your \x05\x41Deku Seeds Bullet Bag \x01\x05\x40has become bigger!\x01This bag can hold \x05\x4650\x05\x41 \x05\x40bullets!",
    },
    {
        "id": 0x006F,
        "text": "\x08You got a \x05\x42Green Rupee\x05\x40!\x01That's \x05\x42one Rupee\x05\x40!",
    },
    {
        "id": 0x0070,
        "text": "\x08\x13\x04You got the \x05\x41Fire Arrow\x05\x40!\x01If you hit your target,\x01it will catch fire.",
    },
    {
        "id": 0x0071,
        "text": "\x08\x13\x0CYou got the \x05\x43Ice Arrow\x05\x40!\x01If you hit your target,\x01it will freeze.",
    },
    {
        "id": 0x0072,
        "text": "\x08\x13\x12You got the \x05\x44Light Arrow\x05\x40!\x01The light of justice\x01will smite evil!",
    },
    {
        "id": 0x0079,
        "text": "\x08\x13\x50You got the \x05\x41Goron's Bracelet\x05\x40!\x01Now you can pull up Bomb\x01Flowers.",
    },
    {
        "id": 0x007B,
        "text": "\x08\x13\x70You obtained the \x05\x41Gerudo's \x01Membership Card\x05\x40!\x01You can get into the Gerudo's\x01training ground.",
    },
    {
        "id": 0x0080,
        "text": "\x08\x13\x6CYou got the \x05\x42Kokiri's Emerald\x05\x40!\x01This is the Spiritual Stone of \x01Forest passed down by the\x01Great Deku Tree.",
    },
    {
        "id": 0x0081,
        "text": "\x08\x13\x6DYou obtained the \x05\x41Goron's Ruby\x05\x40!\x01This is the Spiritual Stone of \x01Fire passed down by the Gorons!",
    },
    {
        "id": 0x0082,
        "text": "\x08\x13\x6EYou obtained \x05\x43Zora's Sapphire\x05\x40!\x01This is the Spiritual Stone of\x01Water passed down by the\x01Zoras!",
    },
    {
        "id": 0x0090,
        "text": "\x08\x13\x00Now you can pick up \x01many \x05\x41Deku Sticks\x05\x40!\x01You can carry up to \x05\x4620\x05\x40 of them!",
    },
    {
        "id": 0x0091,
        "text": "\x08\x13\x00You can now pick up \x01even more \x05\x41Deku Sticks\x05\x40!\x01You can carry up to \x05\x4630\x05\x40 of them!",
    },
    {
        "id": 0x0098,
        "text": "\x08\x13\x1AYou got \x05\x41Lon Lon Milk\x05\x40!\x01This milk is very nutritious!\x01There are two drinks in it.",
    },
    {
        "id": 0x0099,
        "text": "\x08\x13\x1BYou found \x05\x41Ruto's Letter\x05\x40 in a\x01bottle! Show it to King Zora.",
    },
    {
        "id": 0x9099,
        "text": "\x08\x13\x1BYou found \x05\x41a letter in a bottle\x05\x40!\x01You remove the letter from the\x01bottle, freeing it for other uses.",
    },
    {
        "id": 0x009A,
        "text": "\x08\x13\x21You got a \x05\x41Weird Egg\x05\x40!\x01Feels like there's something\x01moving inside!",
    },
    {
        "id": 0x00A4,
        "text": "\x08\x13\x3BYou got the \x05\x42Kokiri Sword\x05\x40!\x01This is a hidden treasure of\x01the Kokiri.",
    },
    {
        "id": 0x00A7,
        "text": "\x08\x13\x01Now you can carry\x01many \x05\x41Deku Nuts\x05\x40!\x01You can hold up to \x05\x4630\x05\x40 nuts!",
    },
    {
        "id": 0x00A8,
        "text": "\x08\x13\x01You can now carry even\x01more \x05\x41Deku Nuts\x05\x40! You can carry\x01up to \x05\x4640\x05\x41 \x05\x40nuts!",
    },
    {
        "id": 0x00AD,
        "text": "\x08\x13\x05You got \x05\x41Din's Fire\x05\x40!\x01Its fireball engulfs everything!",
    },
    {
        "id": 0x00AE,
        "text": "\x08\x13\x0DYou got \x05\x42Farore's Wind\x05\x40!\x01This is warp magic you can use!",
    },
    {
        "id": 0x00AF,
        "text": "\x08\x13\x13You got \x05\x43Nayru's Love\x05\x40!\x01Cast this to create a powerful\x01protective barrier.",
    },
    {
        "id": 0x00B4,
        "text": "\x08You got a \x05\x41Gold Skulltula Token\x05\x40!\x01You've collected \x05\x41\x19\x05\x40 tokens in total.",
    },
    {
        "id": 0x00B5,
        "text": "\x08You destroyed a \x05\x41Gold Skulltula\x05\x40.\x01You got a token proving you \x01destroyed it!",
    }, #Unused
    {
        "id": 0x00C2,
        "text": "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Collect four pieces total to get\x01another Heart Container.",
    },
    {
        "id": 0x90C2,
        "text": "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01You are already at\x01maximum health.",
    },
    {
        "id": 0x00C3,
        "text": "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01So far, you've collected two \x01pieces.",
    },
    {
        "id": 0x00C4,
        "text": "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Now you've collected three \x01pieces!",
    },
    {
        "id": 0x00C5,
        "text": "\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01You've completed another Heart\x01Container!",
    },
    {
        "id": 0x00C6,
        "text": "\x08\x13\x72You got a \x05\x41Heart Container\x05\x40!\x01Your maximum life energy is \x01increased by one heart.",
    },
    {
        "id": 0x90C6,
        "text": "\x08\x13\x72You got a \x05\x41Heart Container\x05\x40!\x01You are already at\x01maximum health.",
    },
    {
        "id": 0x00C7,
        "text": "\x08\x13\x74You got the \x05\x41Boss Key\x05\x40!\x01Now you can get inside the \x01chamber where the Boss lurks.",
    },
    {
        "id": 0x00CC,
        "text": "\x08You got a \x05\x43Blue Rupee\x05\x40!\x01That's \x05\x43five Rupees\x05\x40!",
    },
    {
        "id": 0x00CD,
        "text": "\x08\x13\x53You got the \x05\x43Silver Scale\x05\x40!\x01You can dive deeper than you\x01could before.",
    },
    {
        "id": 0x00CE,
        "text": "\x08\x13\x54You got the \x05\x43Golden Scale\x05\x40!\x01Now you can dive much\x01deeper than you could before!",
    },
    {
        "id": 0x00DD,
        "text": "\x08You mastered the secret sword\x01technique of the \x05\x41Spin Attack\x05\x40!",
    },
    {
        "id": 0x00E4,
        "text": "\x08You can now use \x05\x42Magic\x05\x40!",
    },
    {
        "id": 0x00E5,
        "text": "\x08Your \x05\x44defensive power\x05\x40 is enhanced!",
    },
    {
        "id": 0x00E8,
        "text": "\x08Your magic power has been \x01enhanced! Now you have twice\x01as much \x05\x41Magic Power\x05\x40!",
    },
    {
        "id": 0x00E9,
        "text": "\x08Your defensive power has been \x01enhanced! Damage inflicted by \x01enemies will be \x05\x41reduced by half\x05\x40.",
    },
    {
        "id": 0x00F0,
        "text": "\x08You got a \x05\x41Red Rupee\x05\x40!\x01That's \x05\x41twenty Rupees\x05\x40!",
    },
    {
        "id": 0x00F1,
        "text": "\x08You got a \x05\x45Purple Rupee\x05\x40!\x01That's \x05\x45fifty Rupees\x05\x40!",
    },
    {
        "id": 0x00F2,
        "text": "\x08You got a \x05\x46Huge Rupee\x05\x40!\x01This Rupee is worth a whopping\x01\x05\x46two hundred Rupees\x05\x40!",
    },
    {
        "id": 0x00F4,
        "text": "\x08\x05\x44Loser!\x05\x40\x04\x08You found only \x05\x42one Rupee\x05\x40.\x01You are not very lucky.",
    },
    {
        "id": 0x00F5,
        "text": "\x08\x05\x44Loser!\x05\x40\x04\x08You found \x05\x43five Rupees\x05\x40.\x01Even so, you are not very lucky.",
    },
    {
        "id": 0x00F6,
        "text": "\x08\x05\x44Loser!\x05\x40\x04\x08You found \x05\x41twenty Rupees\x05\x40.\x01Your last selection was a mistake,\x01wasn't it! How frustrating!",
    },
    {
        "id": 0x00F7,
        "text": "\x08\x05\x41Winner!\x05\x40\x04\x08You found \x05\x46fifty Rupees\x05\x40.\x01You are a genuinely lucky guy!",
    },
    {
        "id": 0x00FA,
        "text": "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Collect four pieces total to get\x01another Heart Container.",
    },
    {
        "id": 0x00FB,
        "text": "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01So far, you've collected two \x01pieces.",
    },
    {
        "id": 0x00FC,
        "text": "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01Now you've collected three \x01pieces!",
    },
    {
        "id": 0x00FD,
        "text": "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01You've completed another Heart\x01Container!",
    },
    {
        "id": 0x90FA,
        "text": "\x08\x06\x49\x05\x41WINNER\x05\x40!\x04\x08\x13\x73You got a \x05\x41Piece of Heart\x05\x40!\x01You are already at\x01maximum health.",
    },
    #{"id": 0x6074,"text": "\x08Oh, that's too bad.\x04\x08If you change your mind, please\x01come back again!\x04\x08The mark that will lead you to the\x01Spirit Temple is the \x05\x41flag on\x01the left \x05\x40outside the shop."},
    {
        "id": 0x9002,
        "text": "\x08You are a \x05\x43FOOL\x05\x40!",
    },
    {
        "id": 0x9003,
        "text": "\x08You found a piece of the \x05\x41Triforce\x05\x40!",
    },
    {
        "id": 0x9019,
        "text": "\x08\x13\x09You found a \x05\x41Bombchu Bag\x05\x40!\x01It has some \x05\x41Bombchus\x05\x40 inside!\x01Find more in tall grass.",
    },
    {
        "id": 0x901A,
        "text": "\x08You can't buy Bombchus without a\x01\x05\x41Bombchu Bag\x05\x40!",
    },
    {
        "id": 0x908C,
        "text": "\x08You got the\x01\x05\x41Ocarina A Button!\x05\x40\x01You can now play \x9F on the Ocarina!",
    },
    {
        "id": 0x908D,
        "text": "\x08You got the\x01\x05\x41Ocarina C-up Button!\x05\x40\x01You can now play \xA5 on the Ocarina!",
    },
    {
        "id": 0x908E,
        "text": "\x08You got the\x01\x05\x41Ocarina C-down Button!\x05\x40\x01You can now play \xA6 on the Ocarina!",
    },
    {
        "id": 0x908F,
        "text": "\x08You got the\x01\x05\x41Ocarina C-left Button!\x05\x40\x01You can now play \xA7 on the Ocarina!",
    },
    {
        "id": 0x9090,
        "text": "\x08You got the\x01\x05\x41Ocarina C-right Button!\x05\x40\x01You can now play \xA8 on the Ocarina!",
    },
    {
        "id": 0x9091,
        "text": "\x08\x06\x28You have learned the\x01\x06\x2F\x05\x42Minuet of Forest\x05\x40!",
    },
    {
        "id": 0x9092,
        "text": "\x08\x06\x28You have learned the\x01\x06\x37\x05\x41Bolero of Fire\x05\x40!",
    },
    {
        "id": 0x9093,
        "text": "\x08\x06\x28You have learned the\x01\x06\x29\x05\x43Serenade of Water\x05\x40!",
    },
    {
        "id": 0x9094,
        "text": "\x08\x06\x28You have learned the\x01\x06\x2D\x05\x46Requiem of Spirit\x05\x40!",
    },
    {
        "id": 0x9095,
        "text": "\x08\x06\x28You have learned the\x01\x06\x28\x05\x45Nocturne of Shadow\x05\x40!",
    },
    {
        "id": 0x9096,
        "text": "\x08\x06\x28You have learned the\x01\x06\x32\x05\x44Prelude of Light\x05\x40!",
    },
    {
        "id": 0x9097,
        "text": "\x08\x13\x2EYou got a \x05\x41Chicken, \x05\x40one\x01of Anju's prized hens! It fits \x01in your pocket.",
    },
    # 0x9098 unused
    # 0x9099 used above
    {
        "id": 0x909A,
        "text": "\x08\x06\x15You've learned \x05\x43Zelda's Lullaby\x05\x40!",
    },
    {
        "id": 0x909B,
        "text": "\x08\x06\x11You've learned \x05\x41Epona's Song\x05\x40!",
    },
    {
        "id": 0x909C,
        "text": "\x08\x06\x14You've learned \x05\x42Saria's Song\x05\x40!",
    },
    {
        "id": 0x909D,
        "text": "\x08\x06\x0BYou've learned the \x05\x46Sun's Song\x05\x40!",
    },
    {
        "id": 0x909E,
        "text": "\x08\x06\x05You've learned the \x05\x44Song of Time\x05\x40!",
    },
    {
        "id": 0x909F,
        "text": "\x08You've learned the \x05\x45Song of Storms\x05\x40!",
    },
    {
        "id": 0x90A0,
        "text": "\x08\x13\x15You got a \x05\x41Red Potion\x05\x40!\x01It will restore your health",
    },
    {
        "id": 0x90A1,
        "text": "\x08\x13\x16You got a \x05\x42Green Potion\x05\x40!\x01It will restore your magic.",
    },
    {
        "id": 0x90A2,
        "text": "\x08\x13\x17You got a \x05\x43Blue Potion\x05\x40!\x01It will recover your health\x01and magic.",
    },
    {
        "id": 0x90A3,
        "text": "\x08\x13\x18You caught a \x05\x41Fairy\x05\x40 in a bottle!\x01It will revive you\x01the moment you run out of life \x01energy.",
    },
    {
        "id": 0x90A4,
        "text": "\x08\x13\x19You got a \x05\x41Fish\x05\x40!\x01It looks so fresh and\x01delicious!",
    },
    {
        "id": 0x90A5,
        "text": "\x08\x13\x1CYou put a \x05\x44Blue Fire\x05\x40\x01into the bottle!\x01This is a cool flame you can\x01use on red ice.",
    },
    {
        "id": 0x90A6,
        "text": "\x08\x13\x1DYou put a \x05\x41Bug \x05\x40in the bottle!\x01This kind of bug prefers to\x01live in small holes in the ground.",
    },
    {
        "id": 0x90A7,
        "text": "\x08\x13\x1EYou put a \x05\x41Big Poe \x05\x40in a bottle!\x01Let's sell it at the \x05\x41Ghost Shop\x05\x40!\x01Something good might happen!",
    },
    {
        "id": 0x90A8,
        "text": "\x08\x13\x20You caught a \x05\x41Poe \x05\x40in a bottle!\x01Something good might happen!",
    },
    {
        "id": 0x90A9,
        "text": "\x08\x13\x02You got \x05\x41Bombs\x05\x40!\x01If you see something\x01suspicious, bomb it!",
    },
    {
        "id": 0x90AA,
        "text": "\x08\x13\x01You got a \x05\x41Deku Nut\x05\x40!",
    },
    {
        "id": 0x90AB,
        "text": "\x08\x13\x09You got \x05\x41Bombchus\x05\x40!",
    },
    {
        "id": 0x90AC,
        "text": "\x08\x13\x00You got a \x05\x41Deku Stick\x05\x40!",
    },
    {
        "id": 0x90AD,
        "text": "\x08\x13\x3EYou got a \x05\x44Deku Shield\x05\x40!",
    },
    {
        "id": 0x90AE,
        "text": "\x08\x13\x3FYou got a \x05\x44Hylian Shield\x05\x40!",
    },
    {
        "id": 0x90AF,
        "text": "\x08\x13\x42You got a \x05\x41Goron Tunic\x05\x40!\x01Going to a hot place? No worry!",
    },
    {
        "id": 0x90B0,
        "text": "\x08\x13\x43You got a \x05\x43Zora Tunic\x05\x40!\x01Wear it, and you won't drown\x01underwater.",
    },
    {
        "id": 0x90B1,
        "text": "\x08You got a \x05\x45Recovery Heart\x05\x40!\x01Your life energy is recovered!",
    },
    {
        "id": 0x90B2,
        "text": "\x08You got a \x05\x46bundle of arrows\x05\x40!",
    },
    {
        "id": 0x90B3,
        "text": "\x08\x13\x58You got \x05\x41Deku Seeds\x05\x40!\x01Use these as bullets\x01for your Slingshot.",
    },
    {
        "id": 0x90B4,
        "text": "\x08You found a \x05\x41fairy\x05\x40!\x01Your health has been restored!",
    },
    {
        "id": 0x90B5,
        "text": "\x08You found \x05\x43literally nothing\x05\x40!",
    },
]

# Item texts when you use keysanity
# Format: {"id": int, "text": str}
IMPORTANT_ITEM_MESSAGES = [
    {
        "id": 0x001C,
        "text": "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09",
    },
    {
        "id": 0x0006,
        "text": "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09",
    },
    {
        "id": 0x001D,
        "text": "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09",
    },
    {
        "id": 0x001E,
        "text": "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x002A,
        "text": "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x0061,
        "text": "\x13\x74\x08You got the \x05\x41Boss Key\x05\x40\x01for \x05\x41Ganon's Castle\x05\x40!\x09",
    },
    {
        "id": 0x0062,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x42Deku Tree\x05\x40!\x09",
    },
    {
        "id": 0x0063,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for \x05\x41Dodongo's Cavern\x05\x40!\x09",
    },
    {
        "id": 0x0064,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for \x05\x43Jabu Jabu's Belly\x05\x40!\x09",
    },
    {
        "id": 0x0065,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09",
    },
    {
        "id": 0x007C,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09",
    },
    {
        "id": 0x007D,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09",
    },
    {
        "id": 0x007E,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x007F,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x0087,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x44Ice Cavern\x05\x40!\x09",
    },
    {
        "id": 0x0088,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x42Deku Tree\x05\x40!\x09",
    },
    {
        "id": 0x0089,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for \x05\x41Dodongo's Cavern\x05\x40!\x09",
    },
    {
        "id": 0x008A,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for \x05\x43Jabu Jabu's Belly\x05\x40!\x09",
    },
    {
        "id": 0x008B,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09",
    },
    {
        "id": 0x008C,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09",
    },
    {
        "id": 0x008E,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09",
    },
    {
        "id": 0x008F,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x0092,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x44Ice Cavern\x05\x40!\x09",
    },
    {
        "id": 0x0093,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x42Forest Temple\x05\x40!\x09",
    },
    {
        "id": 0x0094,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x41Fire Temple\x05\x40!\x09",
    },
    {
        "id": 0x0095,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x43Water Temple\x05\x40!\x09",
    },
    {
        "id": 0x009B,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x45Bottom of the Well\x05\x40!\x09",
    },
    {
        "id": 0x009F,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x46Gerudo Training\x01Ground\x05\x40!\x09",
    },
    {
        "id": 0x00A0,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x46Thieves' Hideout\x05\x40!\x09",
    },
    {
        "id": 0x00A1,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for \x05\x41Ganon's Castle\x05\x40!\x09",
    },
    {
        "id": 0x00A2,
        "text": "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for the \x05\x45Bottom of the Well\x05\x40!\x09",
    },
    {
        "id": 0x00A3,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x00A5,
        "text": "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for the \x05\x45Bottom of the Well\x05\x40!\x09",
    },
    {
        "id": 0x00A6,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x00A9,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x00F3,
        "text": "\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for the \x05\x44Treasure Box Shop\x05\x40!\x09",
    },
    # 0x9019 and 0x901A used above
    # Silver Rupee Messages with count.
    {
        "id": 0x901B,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01staircase room in \x05\x41Dodongo's Cavern\x05\x40!\x01You have found \x05\x41\xF0\x00\x05\x40 so far!\x09",
    },
    {
        "id": 0x901C,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44spinning scythe room\x05\x40 in the \x05\x44Ice\x01Cavern\x05\x40! You have found \x05\x41\xF0\x01\x05\x40 so far!\x09",
    },
    {
        "id": 0x901D,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43push block room\x05\x40 in the \x05\x44Ice Cavern\x05\x40!\x01You have found \x05\x41\xF0\x02\x05\x40 so far!\x09",
    },
    {
        "id": 0x901E,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01basement in the \x05\x45Bottom of the Well\x05\x40!\x01You have found \x05\x41\xF0\x03\x05\x40 so far!\x09",
    },
    {
        "id": 0x901F,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42scythe shortcut room\x05\x40 in the \x05\x45Shadow\x01Temple\x05\x40! You have found \x05\x41\xF0\x04\x05\x40 so far!\x09",
    },
    {
        "id": 0x9020,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44invisible blade room\x05\x40 in the \x05\x45Shadow\x01Temple\x05\x40! You have found \x05\x41\xF0\x05\x05\x40 so far!\x09",
    },
    {
        "id": 0x9021,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46huge pit\x05\x40 in the \x05\x45Shadow Temple\x05\x40!\x01You have found \x05\x41\xF0\x06\x05\x40 so far!\x09",
    },
    {
        "id": 0x9022,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01room with \x05\x45invisible spikes\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40!\x01You have found \x05\x41\xF0\x07\x05\x40 so far!\x09",
    },
    {
        "id": 0x9023,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46sloped room\x05\x40 in the \x05\x46Gerudo Training\x01Ground\x05\x40! You have found \x05\x41\xF0\x08\x05\x40 so far!\x09",
    },
    {
        "id": 0x9024,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x41lava\x01room\x05\x40 in the \x05\x46Gerudo Training Ground\x05\x40!\x01You have found \x05\x41\xF0\x09\x05\x40 so far!\x09",
    },
    {
        "id": 0x9025,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43water room\x05\x40 in the \x05\x46Gerudo Training\x01Ground\x05\x40! You have found \x05\x41\xF0\x0A\x05\x40 so far!\x09",
    },
    {
        "id": 0x9026,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x41torch room\x05\x40 in the child side of the\x01\x05\x46Spirit Temple\x05\x40! You have found \x05\x41\xF0\x0B\x05\x40\x01so far!\x09",
    },
    {
        "id": 0x9027,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42boulder room\x05\x40 in the adult side of the\x01\x05\x46Spirit Temple\x05\x40! You have found \x05\x41\xF0\x0C\x05\x40\x01so far!\x09",
    },
    {
        "id": 0x9028,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44lobby and adult side\x05\x40 of the \x05\x46Spirit\x01Temple\x05\x40! You have found \x05\x41\xF0\x0D\x05\x40 so far!\x09",
    },
    {
        "id": 0x9029,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x46sun\x01block room\x05\x40 in the \x05\x46Spirit Temple\x05\x40!\x01You have found \x05\x41\xF0\x0E\x05\x40 so far!\x09",
    },
    {
        "id": 0x902A,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43climbable wall\x05\x40 in the \x05\x46Spirit Temple\x05\x40!\x01You have found \x05\x41\xF0\x0F\x05\x40 so far!\x09",
    },
    {
        "id": 0x902B,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46Spirit Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x10\x05\x40 so far!\x09",
    },
    {
        "id": 0x902C,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44Light Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x11\x05\x40 so far!\x09",
    },
    {
        "id": 0x902D,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x41Fire\x01Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x12\x05\x40 so far!\x09",
    },
    {
        "id": 0x902E,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x45Shadow Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x13\x05\x40 so far!\x09",
    },
    {
        "id": 0x902F,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43Water Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x14\x05\x40 so far!\x09",
    },
    {
        "id": 0x9030,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42Forest Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x01You have found \x05\x41\xF0\x15\x05\x40 so far!\x09",
    },
    # Silver Rupee messages when all have been collected. IDs are 0x16 after the base messages and calculated in resolve_text_id_silver_rupees. Also used for silver rupee pouches
    {
        "id": 0x9031,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the staircase room in\x01\x05\x41Dodongo's Cavern\x05\x40!\x09",
    },
    {
        "id": 0x9032,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44spinning scythe room\x05\x40\x01in the \x05\x44Ice Cavern\x05\x40!\x09",
    },
    {
        "id": 0x9033,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43push block room\x05\x40 in\x01the \x05\x44Ice Cavern\x05\x40!\x09",
    },
    {
        "id": 0x9034,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the basement in the\x01\x05\x45Bottom of the Well\x05\x40!\x09",
    },
    {
        "id": 0x9035,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42scythe shortcut room\x05\x40\x01in the \x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x9036,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44invisible blade room\x05\x40 in\x01the \x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x9037,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46huge pit\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x9038,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the room with \x05\x45invisible\x01spikes\x05\x40 in the \x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x9039,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sloped room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40!\x09",
    },
    {
        "id": 0x903A,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41lava room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40!\x09",
    },
    {
        "id": 0x903B,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43water room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40!\x09",
    },
    {
        "id": 0x903C,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41torch room\x05\x40 in the\x01child side of the \x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x903D,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42boulder room\x05\x40 in the\x01adult side of the \x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x903E,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44lobby and adult side\x05\x40\x01of the \x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x903F,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sun block room\x05\x40 in the\x01\x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x9040,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43climbable wall\x05\x40 in the\x01\x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x9041,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46Spirit Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40!\x09",
    },
    {
        "id": 0x9042,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44Light Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40!\x09",
    },
    {
        "id": 0x9043,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41Fire Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40!\x09",
    },
    {
        "id": 0x9044,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x45Shadow Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40!\x09",
    },
    {
        "id": 0x9045,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43Water Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40!\x09",
    },
    {
        "id": 0x9046,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42Forest Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40!\x09",
    },
    # 0x9048 used above
    # Silver Rupee messages for MQ dungeons when all have been collected. Offset 0x2E from the base messages.
    {
        "id": 0x9049,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the staircase room in\x01\x05\x41Dodongo's Cavern\x05\x40! The way to the\x01hanging bridge is open!\x09",
    },
    # 0x904A, 0x904B, and 0x904C unused
    {
        "id": 0x904D,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42scythe shortcut room\x05\x40\x01in the \x05\x45Shadow Temple\x05\x40! Now you can\x01access the \x05\x42chest\x05\x40 there!\x09",
    },
    {
        "id": 0x904E,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44invisible blade room\x05\x40 in\x01the \x05\x45Shadow Temple\x05\x40! Now you can\x01access the \x05\x44chest\x05\x40 there!\x09",
    },
    {
        "id": 0x904F,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46huge pit\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40! A \x05\x46chest\x05\x40 has\x01appeared!\x09",
    },
    {
        "id": 0x9050,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the room with \x05\x45invisible\x01spikes\x05\x40 in the \x05\x45Shadow Temple\x05\x40! The\x01way to the \x05\x45Stalfos room\x05\x40 is open!\x09",
    },
    {
        "id": 0x9051,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sloped room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! The way to\x01the room with the \x05\x46heavy block\x05\x40 is\x04open!\x09",
    },
    {
        "id": 0x9052,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41lava room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! The way to\x01the \x05\x41water room\x05\x40 is open!\x09",
    },
    {
        "id": 0x9053,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43water room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! A \x05\x43chest\x05\x40\x01has appeared!\x09",
    },
    # 0x9054 and 0x9055 unused
    {
        "id": 0x9056,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44lobby and adult side\x05\x40\x01of the \x05\x46Spirit Temple\x05\x40! A \x05\x44chest\x05\x40 has\x01appeared!\x09",
    },
    # 0x9057 unused
    {
        "id": 0x9058,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43climbable wall\x05\x40 in the\x01\x05\x46Spirit Temple\x05\x40! The way to the\x01\x05\x43upstairs\x05\x40 is open!\x09",
    },
    # 0x9059 and 0x905A unused
    {
        "id": 0x905B,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41Fire Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40! The way to the \x05\x41final room\x05\x40 is\x01open!\x09",
    },
    {
        "id": 0x905C,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x45Shadow Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40! The way to the \x05\x45final\x01room\x05\x40 is open!\x09",
    },
    {
        "id": 0x905D,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43Water Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40! The way to the \x05\x43final\x01room\x05\x40 is open!\x09",
    },
    # 0x905E unused
    # Silver Rupee messages for non-MQ dungeons when all have been collected. Offset 0x44 from the base messages.
    # 0x905F unused
    {
        "id": 0x9060,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44spinning scythe room\x05\x40\x01in the \x05\x44Ice Cavern\x05\x40! The way to the\x01\x05\x44map room\x05\x40 is open!\x09",
    },
    {
        "id": 0x9061,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43push block room\x05\x40 in\x01the \x05\x44Ice Cavern\x05\x40! The way to the \x05\x43final\x01room\x05\x40 is open!\x09",
    },
    {
        "id": 0x9062,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the basement in the\x01\x05\x45Bottom of the Well\x05\x40! Now you can\x01get back to the upper level!\x09",
    },
    {
        "id": 0x9063,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42scythe shortcut room\x05\x40\x01in the \x05\x45Shadow Temple\x05\x40! Now you can\x01access the \x05\x42chest\x05\x40 there!\x09",
    },
    # 0x9064 unused
    {
        "id": 0x9065,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46huge pit\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40! The way to the\x01room with \x05\x46falling spikes\x05\x40 is open!\x09",
    },
    {
        "id": 0x9066,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the room with \x05\x45invisible\x01spikes\x05\x40 in the \x05\x45Shadow Temple\x05\x40! The\x01way to the room with the \x05\x45giant pot\x05\x40\x04is open!\x09",
    },
    {
        "id": 0x9067,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sloped room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! The way to\x01the room with the \x05\x46heavy block\x05\x40 is\x04open!\x09",
    },
    {
        "id": 0x9068,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41lava room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! The way to\x01the \x05\x41water room\x05\x40 is open!\x09",
    },
    {
        "id": 0x9069,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x43water room\x05\x40 in the\x01\x05\x46Gerudo Training Ground\x05\x40! A \x05\x43chest\x05\x40\x01has appeared!\x09",
    },
    {
        "id": 0x906A,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41torch room\x05\x40 in the\x01child side of the \x05\x46Spirit Temple\x05\x40! Now\x01the \x05\x41metal bridge\x05\x40 there is lowered!\x09",
    },
    {
        "id": 0x906B,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42boulder room\x05\x40 in the\x01adult side of the \x05\x46Spirit Temple\x05\x40! Now\x01you can access the \x05\x42chest\x05\x40 there!\x09",
    },
    # 0x906C unused
    {
        "id": 0x906D,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46sun block room\x05\x40 in the\x01\x05\x46Spirit Temple\x05\x40! The \x05\x46torch\x05\x40 has been\x01lit!\x09",
    },
    # 0x906E unused
    {
        "id": 0x906F,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x46Spirit Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40! The way to the \x05\x46second room\x05\x40\x01is open!\x09",
    },
    {
        "id": 0x9070,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x44Light Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40! The way to the \x05\x44final room\x05\x40 is\x01open!\x09",
    },
    {
        "id": 0x9071,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x41Fire Trial\x05\x40 in \x05\x41Ganon's\x01Castle\x05\x40! The way to the \x05\x41final room\x05\x40 is\x01open!\x09",
    },
    # 0x9072 and 0x9073 unused
    {
        "id": 0x9074,
        "text": "\x08You have found all of the \x05\x44Silver\x01Rupees\x05\x40 for the \x05\x42Forest Trial\x05\x40 in\x01\x05\x41Ganon's Castle\x05\x40! The way to the \x05\x42final\x01room\x05\x40 is open!\x09",
    },
    # Silver Rupee messages without count. Offset 0x5A from the base messages.
    {
        "id": 0x9075,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01staircase room in \x05\x41Dodongo's Cavern\x05\x40!\x09",
    },
    {
        "id": 0x9076,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44spinning scythe room\x05\x40 in the \x05\x44Ice\x01Cavern\x05\x40!\x09",
    },
    {
        "id": 0x9077,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43push block room\x05\x40 in the \x05\x44Ice Cavern\x05\x40!\x09",
    },
    {
        "id": 0x9078,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01basement in the \x05\x45Bottom of the Well\x05\x40!\x09",
    },
    {
        "id": 0x9079,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42scythe shortcut room\x05\x40 in the \x05\x45Shadow\x01Temple\x05\x40!\x09",
    },
    {
        "id": 0x907A,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44invisible blade room\x05\x40 in the \x05\x45Shadow\x01Temple\x05\x40!\x09",
    },
    {
        "id": 0x907B,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46huge pit\x05\x40 in the \x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x907C,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01room with \x05\x45invisible spikes\x05\x40 in the\x01\x05\x45Shadow Temple\x05\x40!\x09",
    },
    {
        "id": 0x907D,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46sloped room\x05\x40 in the \x05\x46Gerudo Training\x01Ground\x05\x40!\x09",
    },
    {
        "id": 0x907E,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x41lava\x01room\x05\x40 in the \x05\x46Gerudo Training Ground\x05\x40!\x09",
    },
    {
        "id": 0x907F,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43water room\x05\x40 in the \x05\x46Gerudo Training\x01Ground\x05\x40!\x09",
    },
    {
        "id": 0x9080,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x41torch room\x05\x40 in the child side of the\x01\x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x9081,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42boulder room\x05\x40 in the adult side of the\x01\x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x9082,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44lobby and adult side\x05\x40 of the \x05\x46Spirit\x01Temple\x05\x40!\x09",
    },
    {
        "id": 0x9083,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x46sun\x01block room\x05\x40 in the \x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x9084,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43climbable wall\x05\x40 in the \x05\x46Spirit Temple\x05\x40!\x09",
    },
    {
        "id": 0x9085,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x46Spirit Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09",
    },
    {
        "id": 0x9086,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x44Light Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09",
    },
    {
        "id": 0x9087,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the \x05\x41Fire\x01Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09",
    },
    {
        "id": 0x9088,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x45Shadow Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09",
    },
    {
        "id": 0x9089,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x43Water Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09",
    },
    {
        "id": 0x908A,
        "text": "\x08You found a \x05\x44Silver Rupee\x05\x40 for the\x01\x05\x42Forest Trial\x05\x40 in \x05\x41Ganon's Castle\x05\x40!\x09",
    },
]


dungeon_list = {
    'Deku Tree':          {
                              "name": "the \x05\x42Deku Tree",
                              "gender": "no_gender",
                          },
    'Dodongos Cavern':    {
                              "name": "\x05\x41Dodongo\'s Cavern",
                              "gender": "no_gender",
                          },
    'Jabu Jabus Belly':   {
                              "name": "\x05\x43Jabu Jabu\'s Belly",
                              "gender": "no_gender",
                          },
    'Forest Temple':      {
                              "name": "the \x05\x42Forest Temple",
                              "gender": "no_gender",
                          },
    'Fire Temple':        {
                              "name": "the \x05\x41Fire Temple",
                              "gender": "no_gender",
                          },
    'Water Temple':       {
                              "name": "the \x05\x43Water Temple",
                              "gender": "no_gender",
                          },
    'Spirit Temple':      {
                              "name": "the \x05\x46Spirit Temple",
                              "gender": "no_gender",
                          },
    'Shadow Temple':      {
                              "name": "the \x05\x45Shadow Temple",
                              "gender": "no_gender",
                          },
    'Bottom of the Well': {
                              "name": "the \x05\x45Bottom of the Well",
                              "gender": "no_gender",
                          },
    'Ice Cavern':         {
                              "name": "the \x05\x44Ice Cavern",
                              "gender": "no_gender",
                          },
    'Ganons Castle Tower':  None,
    'Gerudo Training Ground': {
                              "name": "the \x05\x46Gerudo Training Ground",
                              "gender": "no_gender",
                          },
    'Hideout':              {
                              "name": "the \x05\x46Thieves' Hideout\x05\x40",
                              "gender": "no_gender",
                            },
    'Ganons Castle':      {
                              "name": "\x05\x41Ganon's Castle",
                              "gender": "no_gender",
                          },
    'Tower Collapse':       None,
    'Castle Collapse':      None,
    'Treasure Box Shop':    {
                              "name": "the \x05\x44Treasure Box Shop\x05\x40",
                              "gender": "no_gender",
                            }
}

# Goal place text mappings for Goal's hint texts

goal_place_textboxes = {
    "the Tower": "path to #the Tower#",
    "gold": "path of #gold#",
    "Door of Time": "path of #time#",
    "Evil's Bane":"path to #Evil\'s Bane#",
    "Skulls":"path of #Skulls#",
    "hearts":"path of #hearts#",
    "the Key":"path to #the Key#",
    "the hero":"path of #the hero#",
}
    
    

# Boss room text mappings for enhanced descriptions on compass

boss_textboxes = {
    'Queen Gohma Boss Room': "\x05\x41Queen Gohma",
    'King Dodongo Boss Room': "\x05\x41King Dodongo",
    'Barinade Boss Room': "\x05\x41Barinade",
    'Phantom Ganon Boss Room': "\x05\x41Phantom Ganon",
    'Volvagia Boss Room': "\x05\x41Volvagia",
    'Morpha Boss Room': "\x05\x41Morpha",
    'Bongo Bongo Boss Room': "\x05\x41Bongo Bongo",
    'Twinrova Boss Room': "\x05\x41Twinrova",
    'Ganons Castle Tower': "\x05\x41Ganondorf",
}

reduction_dungeon_list = ['Ganons Castle Tower', 'Hideout', 'Tower Collapse', 'Castle Collapse', 'Treasure Box Shop']

dungeon_names = []

for key, dungeon in dungeon_list.items():
    if dungeon is not None:
        dungeon_list[key]["has_map"] = key not in ["Gerudo Training Ground", "Ganons Castle"]
        dungeon_names += [(dungeon["name"] + color_white, dungeon["gender"]) if key not in ['Deku Tree', 'Dodongos Cavern', 'Jabu Jabus Belly', 'Ice Cavern'] else None]
    else:
        dungeon_names += [None]
for key in reduction_dungeon_list:
    dungeon_list.pop(key)

i = 0x9101
# Add small key messages starting at 0x9101
# These are grouped in dungeon order as follows:
#       0x9101 - Small key messages for the first one collected
#       0x9112 - Small key messages containing the count
#       0x9123 - Small key messages for collecting more than enough

for dungeon_name in dungeon_names:
    if dungeon_name is not None:
        IMPORTANT_ITEM_MESSAGES.append({"id": i, "text": f"\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for {dungeon_name[0]}!\x01It's your \x05\x41first\x05\x40 one!\x09"})
    i += 1
c = 0
for dungeon_name in dungeon_names:
    if dungeon_name is not None:
        IMPORTANT_ITEM_MESSAGES.append({"id": i, "text": f"\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for {dungeon_name[0]}!\x01You've collected \x05\x41" + "\xF1" + c.to_bytes(1, 'big').decode() + "\x05\x40 of them.\x09"})
    i += 1
    c += 1
for dungeon_name in dungeon_names:
    if dungeon_name is not None:
        IMPORTANT_ITEM_MESSAGES.append({"id": i, "text": f"\x13\x77\x08You found a \x05\x41Small Key\x05\x40\x01for {dungeon_name[0]}!\x01You already have enough keys.\x09"})
    i += 1

# Add key ring messages starting at 0x9200
i = 0x9200
for dungeon_name in dungeon_names:
    if dungeon_name is not None:
        IMPORTANT_ITEM_MESSAGES.append({"id": i, "text": f"\x13\x77\x08You found a \x05\x41Small Key Ring\x05\x40\x01for {dungeon_name[0]}!\x09"})
    i += 1

key_rings_with_bk_dungeon_names = [(dungeon["name"] + color_white, dungeon["gender"]) for key, dungeon in dungeon_list.items() if key in ['Forest Temple','Fire Temple','Water Temple','Spirit Temple','Shadow Temple']]

for dungeon_name in key_rings_with_bk_dungeon_names:
    IMPORTANT_ITEM_MESSAGES.append({"id": i, "text": f"\x13\x77\x08You found a \x05\x41Key Ring\x05\x40\x01for {dungeon_name[0]}!\x09\x01It includes the \x05\x41Boss Key\x05\x40!"})
    i += 1
    
# Miscellaneous texts
# Format: {"id": int, "text": str, "box_type": int}
MISC_MESSAGES = [
    {
        "id": 0x0032,
        "text": "\x08\x13\x02You got \x05\x41Bombs\x05\x40!\x01If you see something\x01suspicious, bomb it!",
        "box_type": 0x23
    },
    {
        "id": 0x0033,
        "text": "\x08\x13\x09You got \x05\x41Bombchus\x05\x40!",
        "box_type": 0x23
    },
    {
        "id": 0x0034,
        "text": "\x08\x13\x01You got a \x05\x41Deku Nut\x05\x40!",
        "box_type": 0x23
    },
    {
        "id": 0x0037,
        "text": "\x08\x13\x00You got a \x05\x41Deku Stick\x05\x40!",
        "box_type": 0x23
    },
    {
        "id": 0x003B,
        "text": "\x08You cast Farore's Wind!\x01\x1C\x05\x42Return to \xF3\x01Dispel the Warp Point\x01Exit\x05\x40",
        "box_type": 0x23
    },
    {
        "id": 0x0043,
        "text": "\x08\x13\x15You got a \x05\x41Red Potion\x05\x40!\x01It will restore your health",
        "box_type": 0x23
    },
    {
        "id": 0x0044,
        "text": "\x08\x13\x16You got a \x05\x42Green Potion\x05\x40!\x01It will restore your magic.",
        "box_type": 0x23
    },
    {
        "id": 0x0045,
        "text": "\x08\x13\x17You got a \x05\x43Blue Potion\x05\x40!\x01It will recover your health\x01and magic.",
        "box_type": 0x23
    },
    {
        "id": 0x0046,
        "text": "\x08\x13\x18You caught a \x05\x41Fairy\x05\x40 in a bottle!\x01It will revive you\x01the moment you run out of life \x01energy.",
        "box_type": 0x23
    },
    {
        "id": 0x0047,
        "text": "\x08\x13\x19You got a \x05\x41Fish\x05\x40!\x01It looks so fresh and\x01delicious!",
        "box_type": 0x23
    },
    {
        "id": 0x004C,
        "text": "\x08\x13\x3EYou got a \x05\x44Deku Shield\x05\x40!",
        "box_type": 0x23
    },
    {
        "id": 0x004D,
        "text": "\x08\x13\x3FYou got a \x05\x44Hylian Shield\x05\x40!",
        "box_type": 0x23
    },
    {
        "id": 0x0050,
        "text": "\x08\x13\x42You got a \x05\x41Goron Tunic\x05\x40!\x01Going to a hot place? No worry!",
        "box_type": 0x23
    },
    {
        "id": 0x0051,
        "text": "\x08\x13\x43You got a \x05\x43Zora Tunic\x05\x40!\x01Wear it, and you won't drown\x01underwater.",
        "box_type": 0x23
    },
    {
        "id": 0x0055,
        "text": "\x08You got a \x05\x45Recovery Heart\x05\x40!\x01Your life energy is recovered!",
        "box_type": 0x23
    },
    {
        "id": 0x005D,
        "text": "\x08\x13\x1CYou put a \x05\x44Blue Fire\x05\x40\x01into the bottle!\x01This is a cool flame you can\x01use on red ice.",
        "box_type": 0x23
    },
    {
        "id": 0x007A,
        "text": "\x08\x13\x1DYou put a \x05\x41Bug \x05\x40in the bottle!\x01This kind of bug prefers to\x01live in small holes in the ground.",
        "box_type": 0x23
    },
    {
        "id": 0x0097,
        "text": "\x08\x13\x20You caught a \x05\x41Poe \x05\x40in a bottle!\x01Something good might happen!",
        "box_type": 0x23
    },
    {
        "id": 0x00DC,
        "text": "\x08\x13\x58You got \x05\x41Deku Seeds\x05\x40!\x01Use these as bullets\x01for your Slingshot.",
        "box_type": 0x23
    },
    {
        "id": 0x00E6,
        "text": "\x08You got a \x05\x46bundle of arrows\x05\x40!",
        "box_type": 0x23
    },
    {
        "id": 0x00F9,
        "text": "\x08\x13\x1EYou put a \x05\x41Big Poe \x05\x40in a bottle!\x01Let's sell it at the \x05\x41Ghost Shop\x05\x40!\x01Something good might happen!",
        "box_type": 0x23
    },
    {
        "id": 0x507B,
        "text": "\x08I tell you, I saw him!\x04\x08I saw the ghostly figure of Damp\x96\x01the gravekeeper sinking into\x01his grave. It looked like he was\x01holding some kind of \x05\x41treasure\x05\x40!\x02",
        "box_type": 0x00
    },
    {
        "id": 0x0422,
        "text": "They say that once \x05\x41Morpha's Curse\x05\x40\x01is lifted, striking \x05\x42this stone\x05\x40 can\x01shift the tides of \x05\x44Lake Hylia\x05\x40.\x02",
        "box_type": 0x23
    },
    {
        "id": 0x401C,
        "text": "Please find my dear \05\x41Princess Ruto\x05\x40\x01immediately... Zora!\x12\x68\x7A",
        "box_type": 0x03
    },
    {
        "id": 0x9100,
        "text": "I am out of goods now.\x01Sorry!\x04The mark that will lead you to\x01the Spirit Temple is the \x05\x41flag on\x01the left \x05\x40outside the shop.\x01Be seeing you!\x02",
        "box_type": 0x00
    },
    {
        "id": 0x0451,
        "text": "\x12\x68\x7AMweep\x07\x04\x52",
        "box_type": 0x23
    },
    {
        "id": 0x0452,
        "text": "\x12\x68\x7AMweep\x07\x04\x53",
        "box_type": 0x23
    },
    {
        "id": 0x0453,
        "text": "\x12\x68\x7AMweep\x07\x04\x54",
        "box_type": 0x23
    },
    {
        "id": 0x0454,
        "text": "\x12\x68\x7AMweep\x07\x04\x55",
        "box_type": 0x23
    },
    {
        "id": 0x0455,
        "text": "\x12\x68\x7AMweep\x07\x04\x56",
        "box_type": 0x23
    },
    {
        "id": 0x0456,
        "text": "\x12\x68\x7AMweep\x07\x04\x57",
        "box_type": 0x23
    },
    {
        "id": 0x0457,
        "text": "\x12\x68\x7AMweep\x07\x04\x58",
        "box_type": 0x23
    },
    {
        "id": 0x0458,
        "text": "\x12\x68\x7AMweep\x07\x04\x59",
        "box_type": 0x23
    },
    {
        "id": 0x0459,
        "text": "\x12\x68\x7AMweep\x07\x04\x5A",
        "box_type": 0x23
    },
    {
        "id": 0x045A,
        "text": "\x12\x68\x7AMweep\x07\x04\x5B",
        "box_type": 0x23
    },
    {
        "id": 0x045B,
        "text": "\x12\x68\x7AMweep",
        "box_type": 0x23
    },
    {
        "id": 0x045C,
        "text": "Come back when you have\x01your own bow and you'll get the\x01\x05\x41real prize\x05\x40!\x0E\x78",
        "box_type": 0x00
    },
    {
        "id": 0x045D,
        "text": "\x12\x68\x5F\x05\x44This game seems shady. Maybe\x01the \x05\x41eye of truth\x05\x44 will show the\x01way forward?\x0E\x78",
        "box_type": 0x00
    },
    {
        "id": 0x6013,
        "text": "Hey, newcomer!\x04Want me to throw you in jail?\x01\x01\x1B\x05\x42No\x01Yes\x05\x40",
        "box_type": 0x00
    },
]

# Texts that is used in Patches.py
PATCH_TEXTS = {
    "warp_to":                      "to {destination_name}",
    "warp_mysterious":              "to a mysterious place",
    "warp_msg":                     "\x08\x05{color}Warp {destination_name}?\x05\40\x09\x01\x01\x1b\x05\x42OK\x01No\x05\40",
    "warp_owl":                     "Hold on to my talons! I'll fly you\x01\x08\x05{color}{destination_name}\x05\40\x09!",
    "ordinary":                     "\x42ordinary",
    "masterful":                    "\x41masterful",
    "scrub_texts":                  [
                                        "\x12\x38\x82I surrender! In return, I will sell\x01you {item}!\x01{price} Rupees it is!\x07\x10\xA3\x02",
                                        "\x12\x38\x82All right! You win! In return,\x01I will sell you {item}!\x01{price} Rupees it is!\x07\x10\xA3\x02",
                                        "\x12\x38\x82All right! You win! In return for\x01sparing me, I will sell you\x01{item}!\x01{price} Rupees it is!\x07\x10\xA3\x02",
                                        "\x12\x38\x82I give up! If you let me go,\x01I will sell you {item}!\x01It's {price} Rupees!\x07\x10\xA3\x02",
                                        "\x12\x38\x82I quit! If you let me go, I'll sell\x01you {item}!\x01{price} Rupees it is!\x07\x10\xA3\x02",
                                        "\x12\x38\x82Knock it off! Leave me alone, and\x01I will sell you {item}!\x01{price} Rupees it is!\x07\x10\xA3\x02",
                                        "\x12\x38\x82All right! You win! If you spare\x01me, I will sell you {item}\x01for {price} Rupees!\x07\x10\xA3\x02",
                                        "\x12\x38\x82All right! You win! Spare me, and\x01I will sell you {item}\x01for {price} Rupees!\x07\x10\xA3\x02",
                                        "\x12\x38\x82I surrender!\x04\x12\x38\x80To make your quest easier,\x01I can give you {item}!\x01But, it'll cost you {price} Rupees!\x07\x10\xA3\x02",
                                    ],
    "claim":                        "Brrrring me the Claim Check...\x01to rrreceive anotherrrrrr item...",
    "brought_poe":                  "\x1AOh, you brought a Poe today!\x04\x1AHmmmm!\x04\x1AVery interesting!\x01This is a \x05\x41Big Poe\x05\x40!\x04\x1AI'll buy it for \x05\x4150 Rupees\x05\x40.\x04On top of that, I'll put \x05\x41100\x01points \x05\x40on your card.\x04\x1AIf you earn \x05\x41{poe} points\x05\x40, you'll\x01be a happy man! Heh heh.",
    "enough_poes":                  "\x1AWait a minute! WOW!\x04\x1AYou have earned \x05\x41{poe} points\x05\x40!\x04\x1AYoung man, you are a genuine\x01\x05\x41Ghost Hunter\x05\x40!\x04\x1AIs that what you expected me to\x01say? Heh heh heh!\x04\x1ABecause of you, I have extra\x01inventory of \x05\x41Big Poes\x05\x40, so this will\x01be the last time I can buy a \x01ghost.\x04\x1AYou're thinking about what I \x01promised would happen when you\x01earned {poe} points. Heh heh.\x04\x1ADon't worry, I didn't forget.\x01Just take this.",
    "child_anju":                   "\x08What should I do!?\x01My \x05\x41Cuccos\x05\x40 have all flown away!\x04You, little boy, please!\x01Please gather at least \x05\x41{chicken} Cuccos\x05\x40\x01for me.\x02",
    "ruto_nothing":                 "\x08Princess Ruto got \x01\x05\x43nothing\x05\x40!\x01Well, that's disappointing...\x02",
    "ruto_fool":                    "\x08Princess Ruto is a \x05\x43FOOL\x05\x40!\x01But why Princess Ruto?\x02",
    "ruto_text":                    "\x08Princess Ruto got \x01\x05{color}{reward_text}\x05\x40!\x01But why Princess Ruto?\x02",
    "gallop":                       "Hey newcomer, you have a fine \x01horse!\x04I don't know where you stole \x01it from, but...\x04OK, how about challenging this \x01\x05\x41horseback archery\x05\x40?\x04Once the horse starts galloping,\x01shoot the targets with your\x01arrows. \x04Let's see how many points you \x01can score. You get 20 arrows.\x04If you can score \x05\x411,000 points\x05\x40, I will \x01give you something good! And even \x01more if you score \x05\x411,500 points\x05\x40!\x0B\x02",
    "bombchu_description":          "\x08\x05\x41Bombchu   (5 pieces)   60 Rupees\x01\x05\x40This looks like a toy mouse, but\x01it\'s actually a self-propelled time\x01bomb!\x09\x0A",
    "bombchu_purchase":             "\x08Bombchu    5 Pieces    60 Rupees\x01\x01\x1B\x05\x42Buy\x01Don\'t buy\x05\x40\x09",
    "bombchu_description_10":       "\x08\x05\x41Bombchu  (10 pieces)  99 Rupees\x01\x05\x40This looks like a toy mouse, but\x01it's actually a self-propelled time\x01bomb!\x09\x0A",
    "bombchu_purchase_10":          "\x08Bombchu  10 pieces   99 Rupees\x09\x01\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40",
    "blue_potion_description":      "\x08\x05\x43Blue Potion 100 Rupees\x01\x05\x40If you drink this, you will\x01recover your life energy and magic.\x09\x0A",
    "blue_potion_purchase":         "\x08Blue Potion 100 Rupees\x01\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40",
    "mysterious":                   "mysterious item",
    "bean_mysterious":              "\x1AChomp chomp chomp...\x01We have... \x05\x41a mysterious item\x05\x40! \x01Do you want it...huh? Huh?\x04\x05\x41\x0860 Rupees\x05\x40 and it's yours!\x01Keyahahah!\x01\x1B\x05\x42Yes\x01No\x05\x40\x02",
    "bean_wrapped":                 "\x1AChomp chomp chomp...We have...\x01\x05\x41{item}\x05\x40!\x04\x05\x41\x0860 Rupees\x05\x40 and it's yours!\x01Keyahahah!\x01\x1B\x05\x42Yes\x01No\x05\x40\x02",
    "bean_item":                    "\x1AChomp chomp chomp...We have...\x01\x05\x41{item}\x05\x40! \x01Do you want it...huh? Huh?\x04\x05\x41\x0860 Rupees\x05\x40 and it's yours!\x01Keyahahah!\x01\x1B\x05\x42Yes\x01No\x05\x40\x02",
    "bean_low":                     "You don't have enough money.\x01I can't sell it to you.\x01Chomp chomp...\x02",
    "bean_enough":                  "We hope you like it!\x01Chomp chomp chomp.\x02",
    "carpet_mysterious":            "\x06\x41Well Come!\x04I am selling stuff, strange and \x01rare, from all over the world to \x01everybody.\x01Today's special is...\x04A mysterious item! \x01Intriguing! \x01I won't tell you what it is until \x01I see the money....\x04How about \x05\x41200 Rupees\x05\x40?\x01\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40\x02",
    "carpet_wrapped":               "\x06\x41Well Come!\x04I am selling stuff, strange and \x01rare. Today's special is...\x01\x05\x41{item}\x05\x40!\x04How about \x05\x41200 Rupees\x05\x40?\x01\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40\x02",
    "carpet_item":                  "\x06\x41Well Come!\x04I am selling stuff, strange and \x01rare, from all over the world to \x01everybody. Today's special is...\x01\x05\x41{item}\x05\x40! \x01\x04How about \x05\x41200 Rupees\x05\x40?\x01\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40\x02",
    "carpet_enough":                "Thank you very much!\x04The mark that will lead you to\x01the Spirit Temple is the \x05\x41flag on\x01the left \x05\x40outside the shop.\x01Be seeing you!\x02",
    "medigoron_cool":               "I have something cool right here.\x01How about it...\x07\x30\x4F\x02",
    "medigoron_ask":                "How do you like it?\x02",
    "medigoron_mysterious":         "How about buying this cool item for \x01200 Rupees?\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40\x02",
    "medigoron_wrapped":            "For 200 Rupees, how about buying...\x04\x05\x41{item}\x05\x40?\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40\x02",
    "medigoron_item":               "For 200 Rupees, how about buying...\x04\x05\x41{item}\x05\x40?\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40\x02",
    "granny_mysterious":            "Mysterious item! How about\x01\x05\x41100 Rupees\x05\x40?\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40\x02",
    "granny_wrapped":               "How about \x05\x41100 Rupees\x05\x40 for...\x04\x05\x41{item}\x05\x40?\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40\x02",
    "granny_item":                  "How about \x05\x41100 Rupees\x05\x40 for\x01\x05\x41{item}\x05\x40?\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40\x02",
    "play":                         "All right. You don't have to play\x01if you don't want to.\x0B\x02",
    "salesman_mysterious":          "I seem to have misplaced my\x01keys, but I have a fun item to\x01sell instead.\x04How about \x05\x4110 Rupees\x05\x40?\x01\x01\x1B\x05\x42Buy\x01Don't Buy\x05\x40\x02",
    "salesman_wrapped":             "I seem to have misplaced my\x01keys, but I have a fun item to\x01sell instead.\x01How about \x05\x4110 Rupees\x05\x40 for...\x04\x05\x41{item}\x05\x40?\x01\x1B\x05\x42Buy\x01Don't Buy\x05\x40\x02",
    "salesman_item":                "I seem to have misplaced my\x01keys, but I have a fun item to\x01sell instead.\x04How about \x05\x4110 Rupees\x05\x40 for\x01\x05\x41{item}\x05\x40?\x01\x1B\x05\x42Buy\x01Don't Buy\x05\x40\x02",
    "salesman_ok":                  "That's OK!\x01More fun for me.\x0B\x02",
    "salesman_limit":               "Wait, that room was off limits!\x02",
    "salesman_hope":                "I hope you like it!\x02",
    "map":                          "\x13\x76\x08You found the \x05\x41Map\x05\x40 for\x01{dungeon_name}\x05\x40!\x01It\'s {dungeon_state}!\x09",
    "map_location":                 "\x13\x76\x08You found the \x05\x41Map\x05\x40 for\x01{dungeon_name}\x05\x40!\x01This dungeon is at\x01{dungeon_location}!\x05\x40\x09",
    "map_location_mq":              "\x13\x76\x08You found the \x05\x41Map\x05\x40 for \x05{dungeon_state}\x05\x40\x01{dungeon_name}\x05\x40! This dungeon\x01is at {dungeon_location}!\x05\x40\x09",
    "compass":                      "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for {dungeon_name}\x05\x40!\x01It holds the \x05{color}{dungeon_reward}\x05\x40!\x09",
    "compass_area":                 "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for {dungeon_name}\x05\x40!\x01The {vanilla_reward} can be found\x01{area}!\x09",
    "compass_boss":                 "\x13\x75\x08You found the \x05\x41Compass\x05\x40 for\x01{dungeon_name}\x05\x40! In this dungeon,\x01{boss_name}\x05\x40 lurks!\x09",
    "compass_boss_area":            "\x13\x75\x08You found the \x05\x41Compass\x05\x40 for\x01{dungeon_name}\x05\x40! {boss_name}\x05\x40\x01lurks, and the {vanilla_reward}\x01is {area}!\x09",
    "compass_boss_reward":          "\x13\x75\x08You found the \x05\x41Compass\x05\x40 for\x01{dungeon_name}\x05\x40!\x01In this dungeon, {boss_name}\x05\x40\x01guards the \x05{color}{dungeon_reward}\x05\x40!\x09",
    "tycoon":                       "\x08\x13\x57You got a \x05\x43Tycoon's Wallet\x05\x40!\x01Now you can hold\x01up to \x05\x46999\x05\x40 \x05\x46Rupees\x05\x40.",
    "blue_fire_arrow":              "\x08\x13\x0CYou got the \x05\x43Blue Fire Arrow\x05\x40!\x01This is a cool arrow you can\x01use on red ice.",
}

# Texts that is used in shops' decription and purchase message
SHOP_TEXTS = {
    "dungeon-item_extra":                         {
                                                    'Dodongos Cavern': "Dodongo's Cavern",
                                                    'Jabu Jabus Belly': "Jabu Jabu's Belly",
                                                    'Thieves Hideout': "Thieves' Hideout",
                                                    'Ganons Castle': "Ganon's Castle",
                                                    'Dodongos Cavern Staircase': "Dodongo's Cavern Staircase",
                                                    'Ganons Castle Spirit Trial': "Ganon's Castle Spirit Trial",
                                                    'Ganons Castle Light Trial': "Ganon's Castle Light Trial",
                                                    'Ganons Castle Fire Trial': "Ganon's Castle Fire Trial",
                                                    'Ganons Castle Shadow Trial': "Ganon's Castle Shadow Trial",
                                                    'Ganons Castle Water Trial': "Ganon's Castle Water Trial",
                                                    'Ganons Castle Forest Trial': "Ganon's Castle Forest Trial",
                                            },
    "censor":                               ['cum', 'cunt', 'dike', 'penis', 'puss', 'rape', 'shit'],
    "dungeon-item_description_multiplay":   '\x08\x05\x41{base_name}  {price} Rupees\x01({extra_name})\x01\x05\x42Player {player_id}\x05\x40\x01Special deal! ONE LEFT!\x09\x0A\x02',
    "dungeon-item_description":             '\x08\x05\x41{base_name}  {price} Rupees\x01({extra_name})\x01\x05\x40Special deal! ONE LEFT!\x01Get it while it lasts!\x09\x0A\x02',
    "dungeon-item_purchase":                '\x08{base_name}  {price} Rupees\x09\x01({extra_name})\x01\x1B\x05\x42Buy\x01Don\'t buy\x05\x40\x02',
    "description_multiplay":                '\x08\x05\x41{base_name}  {price} Rupees\x01\x05\x42Player {player_id}\x05\x40\x01Special deal! ONE LEFT!\x09\x0A\x02',
    "description":                          '\x08\x05\x41{base_name}  {price} Rupees\x01\x05\x40Special deal! ONE LEFT!\x01Get it while it lasts!\x09\x0A\x02',
    "purchase":                             '\x08{base_name}  {price} Rupees\x09\x01\x01\x1B\x05\x42Buy\x01Don\'t buy\x05\x40\x02',
}

# Names that is used on extra_name via SHOP_TEXTS
region_list = {
    'Tower (N/A)':                              "Tower (N/A)",
    'Hideout (N/A)':                            "Hideout (N/A)",
    "Deku Tree":                                "Deku Tree",
    "Forest Temple":                            "Forest Temple", 
    "Fire Temple":                              "Fire Temple", 
    "Water Temple":                             "Water Temple", 
    "Shadow Temple":                            "Shadow Temple", 
    "Spirit Temple":                            "Spirit Temple", 
    "Ganons Castle":                            "Ganon's Castle", 
    'Dodongos Cavern':                          "Dodongo's Cavern",
    'Jabu Jabus Belly':                         "Jabu Jabu's Belly",
    "Bottom of the Well":                       "Bottom of the Well", 
    "Gerudo Training Ground":                   "Gerudo Training Ground", 
    "Thieves Hideout":                          "Thieves' Hideout", 
    "Treasure Chest Game":                      "Treasure Chest Game", 
    "Dodongos Cavern Staircase":                "Dodongo's Cavern Staircase", 
    "Ice Cavern Spinning Scythe":               "Ice Cavern Spinning Scythe", 
    "Ice Cavern Push Block":                    "Ice Cavern Push Block", 
    "Bottom of the Well Basement":              "Bottom of the Well Basement", 
    "Shadow Temple Scythe Shortcut":            "Shadow Temple Scythe Shortcut", 
    "Shadow Temple Invisible Blades":           "Shadow Temple Invisible Blades", 
    "Shadow Temple Huge Pit":                   "Shadow Temple Huge Pit", 
    "Shadow Temple Invisible Spikes":           "Shadow Temple Invisible Spikes", 
    "Gerudo Training Ground Slopes":            "Gerudo Training Ground Slopes", 
    "Gerudo Training Ground Lava":              "Gerudo Training Ground Lava", 
    "Gerudo Training Ground Water":             "Gerudo Training Ground Water", 
    "Spirit Temple Child Early Torches":        "Spirit Temple Child Early Torches", 
    "Spirit Temple Adult Boulders":             "Spirit Temple Adult Boulders", 
    "Spirit Temple Lobby and Lower Adult":      "Spirit Temple Lobby and Lower Adult", 
    "Spirit Temple Sun Block":                  "Spirit Temple Sun Block", 
    "Spirit Temple Adult Climb":                "Spirit Temple Adult Climb", 
    "Ganons Castle Spirit Trial":               "Ganon's Castle Spirit Trial", 
    "Ganons Castle Light Trial":                "Ganon's Castle Light Trial", 
    "Ganons Castle Fire Trial":                 "Ganon's Castle Fire Trial", 
    "Ganons Castle Shadow Trial":               "Ganon's Castle Shadow Trial", 
    "Ganons Castle Water Trial":                "Ganon's Castle Water Trial", 
    "Ganons Castle Forest Trial":               "Ganon's Castle Forest Trial",
}

# Hint words

# Table of hints, format is (name, hint text, clear hint text, gender) there are special characters that are read for certain in game commands:
# ^ is a box break
# & is a new line
# @ will print the player name
# # sets color to white (currently only used for dungeon reward hints).
#
# sfx IDs (see junk hints 1090 and 1174 for examples of how to use them): https://wiki.cloudmodding.com/oot/Sound_Effect_Ids
# Some sound effects loop infinitely, like child link drinking from a bottle, so make sure you test them.
#
# How to use button icons in hints (see junk hint 1180 for an example):
#   \u009F      A
#   \u00A0      B
#   \u00A1      C
#   \u00A2      L
#   \u00A3      R
#   \u00A4      Z
#   \u00A5      C-Up
#   \u00A6      C-Down
#   \u00A7      C-Left
#   \u00A8      C-Right
#   \u00A9      Down arrow
#   \u00AA      Joystick

hintTable = {
    'Kokiri Emerald':                                           (["a tree's farewell", "the Spiritual Stone of the Forest"],                "the Kokiri Emerald", "no_gender"),
    'Goron Ruby':                                               (["the Gorons' hidden treasure", "the Spiritual Stone of Fire"],            "the Goron Ruby", "no_gender"),
    'Zora Sapphire':                                            (["an engagement ring", "the Spiritual Stone of Water"], "the Zora Sapphire", "no_gender"),
    'Light Medallion':                                          (["a sagely power frozen in time", "an old man's sagely power", "a yellow disc"], "the Light Medallion", "no_gender"),
    'Forest Medallion':                                         (["a sagely power given by a childhood friend", "a Kokiri's sagely power", "a green disc"], "the Forest Medallion", "no_gender"),
    'Fire Medallion':                                           (["a sagely power forged in lava", "a Goron's sagely power", "a red disc"], "the Fire Medallion", "no_gender"),
    'Water Medallion':                                          (["a sagely power given by your fiancée", "a Zora's sagely power", "a blue disc"], "the Water Medallion", "no_gender"),
    'Shadow Medallion':                                         (["a sagely power forged in blood", "a Sheikah's sagely power", "a purple disc"], "the Shadow Medallion", "no_gender"),
    'Spirit Medallion':                                         (["a sagely power tainted by mind control", "a Gerudo's sagely power", "an orange disc"], "the Spirit Medallion", "no_gender"),
    'Triforce Piece':                                           (["a triumph fork", "cheese", "a gold fragment"], "a Piece of the Triforce", "no_gender"),
    'Magic Meter':                                              (["mystic training", "pixie dust", "a green rectangle"], "a Magic Meter", "no_gender"),
    'Double Defense':                                           (["a white outline", "damage decrease", "strengthened love"], "Double Defense", "no_gender"),
    'Slingshot':                                                (["a seed shooter", "a rubberband", "a child's catapult"], "a Slingshot", "no_gender"),
    'Boomerang':                                                (["a banana", "a stun stick"], "the Boomerang", "no_gender"),
    'Bow':                                                      (["an archery enabler", "a danger dart launcher"], "a Bow", "no_gender"),
    'Bomb Bag':                                                 (["an explosive container", "a blast bag"], "a Bomb Bag", "no_gender"),
    'Progressive Hookshot':                                     (["Dampé's keepsake", "the Grapple Beam", "the BOING! chain"], "a Hookshot", "no_gender"),
    'Progressive Strength Upgrade':                             (["power gloves", "metal mittens", "the heavy lifty"], "a Strength Upgrade", "no_gender"),
    'Progressive Scale':                                        (["a deeper dive", "a piece of Zora"], "a Zora Scale", "no_gender"),
    'Megaton Hammer':                                           (["the dragon smasher", "the metal mallet", "the heavy hitter"], "the Megaton Hammer", "no_gender"),
    'Iron Boots':                                               (["sink shoes", "clank cleats"], "the Iron Boots", "no_gender"),
    'Hover Boots':                                              (["butter boots", "sacred slippers", "spacewalkers"], "the Hover Boots", "no_gender"),
    'Kokiri Sword':                                             (["a butter knife", "a starter slasher", "a switchblade"], "the Kokiri Sword", "no_gender"),
    'Giants Knife':                                             (["a fragile blade", "a breakable cleaver"], "the Giant's Knife", "no_gender"),
    'Biggoron Sword':                                           (["the biggest blade", "a colossal cleaver"], "the Biggoron Sword", "no_gender"),
    'Master Sword':                                             (["evil's bane"], "the Master Sword", "no_gender"),
    'Deku Shield':                                              (["a wooden ward", "a burnable barrier"], "a Deku Shield", "no_gender"),
    'Hylian Shield':                                            (["a steel safeguard", "Like Like's metal meal"], "a Hylian Shield", "no_gender"),
    'Mirror Shield':                                            (["the reflective rampart", "Medusa's weakness", "a silvered surface"], "the Mirror Shield", "no_gender"),
    'Farores Wind':                                             (["teleportation", "a relocation rune", "a green ball", "a green gust"], "Farore's Wind", "no_gender"),
    'Nayrus Love':                                              (["a safe space", "an impregnable aura", "a blue barrier", "a blue crystal"], "Nayru's Love", "no_gender"),
    'Dins Fire':                                                (["an inferno", "a heat wave", "a red ball"], "Din's Fire", "no_gender"),
    'Fire Arrows':                                              (["the furnace firearm", "the burning bolts", "a magma missile"], "the Fire Arrows", "no_gender"),
    'Ice Arrows':                                               (["the refrigerator rocket", "the frostbite bolts", "an iceberg maker"], "the Ice Arrows", "no_gender"),
    'Blue Fire Arrows':                                         (["the icy hot rocket", "the blue bolts", "an iceberg destroyer"], "the Blue Fire Arrows", "no_gender"),
    'Light Arrows':                                             (["the shining shot", "the luminous launcher", "Ganondorf's bane", "the lighting bolts"], "the Light Arrows", "no_gender"),
    'Lens of Truth':                                            (["a lie detector", "a ghost tracker", "true sight", "a detective's tool"], "the Lens of Truth", "no_gender"),
    'Ocarina':                                                  (["a flute", "a music maker"], "an Ocarina", "no_gender"),
    'Goron Tunic':                                              (["ruby robes", "fireproof fabric", "cooking clothes"], "a Goron Tunic", "no_gender"),
    'Zora Tunic':                                               (["a sapphire suit", "scuba gear", "a swimsuit"], "a Zora Tunic", "no_gender"),
    'Epona':                                                    (["a horse", "a four legged friend"], "Epona", "no_gender"),
    'Zeldas Lullaby':                                           (["a song of royal slumber", "a triforce tune"], "Zelda's Lullaby", "no_gender"),
    'Eponas Song':                                              (["an equestrian etude", "Malon's melody", "a ranch song"], "Epona's Song", "no_gender"),
    'Sarias Song':                                              (["a song of dancing Gorons", "Saria's phone number"], "Saria's Song", "no_gender"),
    'Suns Song':                                                (["Sunny Day", "the ReDead's bane", "the Gibdo's bane"], "the Sun's Song", "no_gender"),
    'Song of Time':                                             (["a song 7 years long", "the tune of ages"], "the Song of Time", "no_gender"),
    'Song of Storms':                                           (["Rain Dance", "a thunderstorm tune", "windmill acceleration"], "the Song of Storms", "no_gender"),
    'Minuet of Forest':                                         (["the song of tall trees", "an arboreal anthem", "a green spark trail"], "the Minuet of Forest", "no_gender"),
    'Bolero of Fire':                                           (["a song of lethal lava", "a red spark trail", "a volcanic verse"], "the Bolero of Fire", "no_gender"),
    'Serenade of Water':                                        (["a song of a damp ditch", "a blue spark trail", "the lake's lyric"], "the Serenade of Water", "no_gender"),
    'Requiem of Spirit':                                        (["a song of sandy statues", "an orange spark trail", "the desert ditty"], "the Requiem of Spirit", "no_gender"),
    'Nocturne of Shadow':                                       (["a song of spooky spirits", "a graveyard boogie", "a haunted hymn", "a purple spark trail"], "the Nocturne of Shadow", "no_gender"),
    'Prelude of Light':                                         (["a luminous prologue melody", "a yellow spark trail", "the temple traveler"], "the Prelude of Light", "no_gender"),
    'Bottle':                                                   (["a glass container", "an empty jar", "encased air"], "a Bottle", "no_gender"),
    'Rutos Letter':                                             (["a call for help", "the note that Mweeps", "an SOS call", "a fishy stationery"], "Ruto's Letter", "no_gender"),
    'Bottle with Milk':                                         (["cow juice", "a white liquid", "a baby's breakfast"], "a Milk Bottle", "no_gender"),
    'Bottle with Red Potion':                                   (["a vitality vial", "a red liquid"], "a Red Potion Bottle", "no_gender"),
    'Bottle with Green Potion':                                 (["a magic mixture", "a green liquid"], "a Green Potion Bottle", "no_gender"),
    'Bottle with Blue Potion':                                  (["an ailment antidote", "a blue liquid"], "a Blue Potion Bottle", "no_gender"),
    'Bottle with Fairy':                                        (["an imprisoned fairy", "an extra life"], "a Fairy Bottle", "no_gender"),
    'Bottle with Fish':                                         (["an aquarium", "a deity's snack"], "a Fish Bottle", "no_gender"),
    'Bottle with Blue Fire':                                    (["a conflagration canteen", "an icemelt jar"], "a Blue Fire Bottle", "no_gender"),
    'Bottle with Bugs':                                         (["an insectarium", "Skulltula finders"], "a Bug Bottle", "no_gender"),
    'Bottle with Poe':                                          (["a spooky ghost", "a face in the jar"], "a Poe Bottle", "no_gender"),
    'Bottle with Big Poe':                                      (["the spookiest ghost", "a sidequest spirit"], "a Big Poe Bottle", "no_gender"),
    'Stone of Agony':                                           (["the shake stone", "the Rumble Pak (TM)"], "the Stone of Agony", "no_gender"),
    'Gerudo Membership Card':                                   (["a girl club membership", "a desert tribe's pass"], "the Gerudo Card", "no_gender"),
    'Progressive Wallet':                                       (["a mo' money holder", "a gem purse", "a portable bank"], "a Wallet", "no_gender"),
    'Deku Stick Capacity':                                      (["a lumber rack", "more flammable twigs"], "Deku Stick Capacity", "no_gender"),
    'Deku Nut Capacity':                                        (["more nuts", "flashbang storage"], "Deku Nut Capacity", "no_gender"),
    'Heart Container':                                          (["a lot of love", "a Valentine's gift", "a boss's organ"], "a Heart Container", "no_gender"),
    'Piece of Heart':                                           (["a little love", "a broken heart"], "a Piece of Heart", "no_gender"),
    'Piece of Heart (Treasure Chest Game)':                     ("a victory valentine", "a Piece of Heart", "no_gender"),
    'Recovery Heart':                                           (["a free heal", "a hearty meal", "a Band-Aid"], "a Recovery Heart", "no_gender"),
    'Rupee (Treasure Chest Game) (1)':                          ("the green gem of grief", 'a Green Rupee', "no_gender"),
    'Rupees (Treasure Chest Game) (5)':                         ("the blue gem of blunder", 'a Blue Rupee', "no_gender"),
    'Rupees (Treasure Chest Game) (20)':                        ("the red gem of regret", 'a Red Rupee', "no_gender"),
    'Rupees (Treasure Chest Game) (50)':                        ("the purple gem of punishment", 'a Purple Rupee', "no_gender"),
    'Deku Stick (1)':                                           ("a breakable branch", 'a Deku Stick', "no_gender"),
    'Rupee (1)':                                                (["a unique coin", "a penny", "a green gem"], "a Green Rupee", "no_gender"),
    'Rupees (5)':                                               (["a common coin", "a blue gem"], "a Blue Rupee", "no_gender"),
    'Rupees (20)':                                              (["couch cash", "a red gem"], "a Red Rupee", "no_gender"),
    'Rupees (50)':                                              (["big bucks", "a purple gem", "wealth"], "a Purple Rupee", "no_gender"),
    'Rupees (200)':                                             (["a juicy jackpot", "a yellow gem", "a giant gem", "great wealth"], "a Huge Rupee", "no_gender"),
    'Weird Egg':                                                (["a chicken dilemma"], "the Weird Egg", "no_gender"),
    'Chicken':                                                  (["a chicken dilemma"], "the Chicken","no_gender"),
    'Zeldas Letter':                                            (["an autograph", "royal stationery", "royal snail mail"], "Zelda's Letter", "no_gender"),
    'Keaton Mask':                                              (["the famous façade"], "the Keaton Mask", "no_gender"),
    'Skull Mask':                                               (["the fleshless façade"], "the Skull Mask", "no_gender"),
    'Spooky Mask':                                              (["the frightening façade"], "the Spooky Mask", "no_gender"),
    'Bunny Hood':                                               (["the fast façade"], "the Bunny Hood", "no_gender"),
    'Goron Mask':                                               (["the fraternal façade"], "the Goron Mask", "no_gender"),
    'Zora Mask':                                                (["the fishy façade"], "the Zora Mask", "no_gender"),
    'Gerudo Mask':                                              (["the feminine façade"], "the Gerudo Mask", "no_gender"),
    'Mask of Truth':                                            (["the factual façade"], "the Mask of Truth", "no_gender"),
    'Pocket Egg':                                               (["a Cucco container", "a Cucco, eventually", "a fowl youth"], "the Pocket Egg", "no_gender"),
    'Pocket Cucco':                                             (["a little clucker"], "the Pocket Cucco", "no_gender"),
    'Cojiro':                                                   (["a cerulean capon"], "Cojiro", "no_gender"),
    'Odd Mushroom':                                             (["a powder ingredient"], "an Odd Mushroom", "no_gender"),
    'Odd Potion':                                               (["Granny's goodies"], "an Odd Potion", "no_gender"),
    'Poachers Saw':                                             (["a tree killer"], "the Poacher's Saw", "no_gender"),
    'Broken Sword':                                             (["a shattered slicer"], "the Broken Sword", "no_gender"),
    'Prescription':                                             (["a pill pamphlet", "a doctor's note"], "the Prescription", "no_gender"),
    'Eyeball Frog':                                             (["a perceiving polliwog"], "the Eyeball Frog", "no_gender"),
    'Eyedrops':                                                 (["a vision vial"], "the Eyedrops", "no_gender"),
    'Claim Check':                                              (["a three day wait"], "the Claim Check", "no_gender"),
    'Map':                                                      (["a dungeon atlas", "blueprints"], "a Map", "no_gender"),
    'Map (Deku Tree)':                                          (["an atlas of an ancient tree", "blueprints of an ancient tree"], "a Map of the Deku Tree", "no_gender"),
    'Map (Dodongos Cavern)':                                    (["an atlas of an immense cavern", "blueprints of an immense cavern"], "a Map of Dodongo's Cavern", "no_gender"),
    'Map (Jabu Jabus Belly)':                                   (["an atlas of the belly of a deity", "blueprints of the belly of a deity"], "a Map of Jabu Jabu's Belly", "no_gender"),
    'Map (Forest Temple)':                                      (["an atlas of a deep forest", "blueprints of a deep forest"], "a Map of the Forest Temple", "no_gender"),
    'Map (Fire Temple)':                                        (["an atlas of a high mountain", "blueprints of a high mountain"], "a Map of the Fire Temple", "no_gender"),
    'Map (Water Temple)':                                       (["an atlas of a vast lake", "blueprints of a vast lake"], "a Map of the Water Temple", "no_gender"),
    'Map (Shadow Temple)':                                      (["an atlas of the house of the dead", "blueprints of the house of the dead"], "a Map of the Shadow Temple", "no_gender"),
    'Map (Spirit Temple)':                                      (["an atlas of the goddess of the sand", "blueprints of the goddess of the sand"], "a Map of the Spirit Temple", "no_gender"),
    'Map (Bottom of the Well)':                                 (["an atlas of a shadow's prison", "blueprints of a shadow's prison"], "a Map of the Bottom of the Well", "no_gender"),
    'Map (Ice Cavern)':                                         (["an atlas of a frozen maze", "blueprints of a frozen maze"], "a Map of the Ice Cavern", "no_gender"),
    'Compass':                                                  (["a treasure tracker", "a magnetic needle"], "a Compass", "no_gender"),
    'Compass (Deku Tree)':                                      (["a treasure tracker for an ancient tree", "a magnetic needle for an ancient tree"], "a Deku Tree Compass", "no_gender"),
    'Compass (Dodongos Cavern)':                                (["a treasure tracker for an immense cavern", "a magnetic needle for an immense cavern"], "a Dodongo's Cavern Compass", "no_gender"),
    'Compass (Jabu Jabus Belly)':                               (["a treasure tracker for the belly of a deity", "a magnetic needle for the belly of a deity"], "a Jabu Jabu's Belly Compass", "no_gender"),
    'Compass (Forest Temple)':                                  (["a treasure tracker for a deep forest", "a magnetic needle for a deep forest"], "a Forest Temple Compass", "no_gender"),
    'Compass (Fire Temple)':                                    (["a treasure tracker for a high mountain", "a magnetic needle for a high mountain"], "a Fire Temple Compass", "no_gender"),
    'Compass (Water Temple)':                                   (["a treasure tracker for a vast lake", "a magnetic needle for a vast lake"], "a Water Temple Compass", "no_gender"),
    'Compass (Shadow Temple)':                                  (["a treasure tracker for the house of the dead", "a magnetic needle for the house of the dead"], "a Shadow Temple Compass", "no_gender"),
    'Compass (Spirit Temple)':                                  (["a treasure tracker for a goddess of the sand", "a magnetic needle for a goddess of the sand"], "a Spirit Temple Compass", "no_gender"),
    'Compass (Bottom of the Well)':                             (["a treasure tracker for a shadow's prison", "a magnetic needle for a shadow's prison"], "a Bottom of the Well Compass", "no_gender"),
    'Compass (Ice Cavern)':                                     (["a treasure tracker for a frozen maze", "a magnetic needle for a frozen maze"], "an Ice Cavern Compass", "no_gender"),
    'BossKey':                                                  (["a master of unlocking", "a dungeon's master pass"], "a Boss Key", "no_gender"),
    'GanonBossKey':                                             (["a master of unlocking", "a dungeon's master pass"], "a Boss Key", "no_gender"),
    'SmallKey':                                                 (["a tool for unlocking", "a dungeon pass", "a lock remover", "a lockpick"], "a Small Key", "no_gender"),
    'HideoutSmallKey':                                          (["a get out of jail free card"], "a Jail Key", "no_gender"),
    'TCGSmallKey':                                              (["a key to becoming a winner"], "a Game Key", "no_gender"),
    'SmallKeyRing':                                             (["a toolbox for unlocking", "a dungeon season pass", "a jingling ring", "a skeleton key"], "a Small Key Ring", "no_gender"),
    'HideoutSmallKeyRing':                                      (["a deck of get out of jail free cards"], "a Jail Key Ring", "no_gender"),
    'TCGSmallKeyRing':                                          (["the keys to becoming a winner"], "a Game Key Ring", "no_gender"),
    'SilverRupee':                                              (["an entry fee", "a priced artifact"], "a Silver Rupee", "no_gender"),
    'Boss Key (Forest Temple)':                                 (["a master of unlocking for a deep forest", "a master pass for a deep forest"], "the Forest Temple Boss Key", "no_gender"),
    'Boss Key (Fire Temple)':                                   (["a master of unlocking for a high mountain", "a master pass for a high mountain"], "the Fire Temple Boss Key", "no_gender"),
    'Boss Key (Water Temple)':                                  (["a master of unlocking for under a vast lake", "a master pass for under a vast lake"], "the Water Temple Boss Key", "no_gender"),
    'Boss Key (Shadow Temple)':                                 (["a master of unlocking for the house of the dead", "a master pass for the house of the dead"], "the Shadow Temple Boss Key", "no_gender"),
    'Boss Key (Spirit Temple)':                                 (["a master of unlocking for a goddess of the sand", "a master pass for a goddess of the sand"], "the Spirit Temple Boss Key", "no_gender"),
    'Boss Key (Ganons Castle)':                                 (["a master of unlocking for a conquered citadel", "a floating dungeon's master pass"], "Ganon's Castle Boss Key", "no_gender"),
    'Small Key (Forest Temple)':                                (["a tool for unlocking a deep forest", "a dungeon pass for a deep forest", "a lock remover for a deep forest", "a lockpick for a deep forest"], "a Forest Temple Small Key", "no_gender"),
    'Small Key (Fire Temple)':                                  (["a tool for unlocking a high mountain", "a dungeon pass for a high mountain", "a lock remover for a high mountain", "a lockpick for a high mountain"], "a Fire Temple Small Key", "no_gender"),
    'Small Key (Water Temple)':                                 (["a tool for unlocking a vast lake", "a dungeon pass for under a vast lake", "a lock remover for under a vast lake", "a lockpick for under a vast lake"], "a Water Temple Small Key", "no_gender"),
    'Small Key (Shadow Temple)':                                (["a tool for unlocking the house of the dead", "a dungeon pass for the house of the dead", "a lock remover for the house of the dead", "a lockpick for the house of the dead"], "a Shadow Temple Small Key", "no_gender"),
    'Small Key (Spirit Temple)':                                (["a tool for unlocking a goddess of the sand", "a dungeon pass for a goddess of the sand", "a lock remover for a goddess of the sand", "a lockpick for a goddess of the sand"], "a Spirit Temple Small Key", "no_gender"),
    'Small Key (Bottom of the Well)':                           (["a tool for unlocking a shadow's prison", "a dungeon pass for a shadow's prison", "a lock remover for a shadow's prison", "a lockpick for a shadow's prison"], "a Bottom of the Well Small Key", "no_gender"),
    'Small Key (Gerudo Training Ground)':                       (["a tool for unlocking the test of thieves", "a dungeon pass for the test of thieves", "a lock remover for the test of thieves", "a lockpick for the test of thieves"], "a Gerudo Training Ground Small Key", "no_gender"),
    'Small Key (Ganons Castle)':                                (["a tool for unlocking a conquered citadel", "a dungeon pass for a conquered citadel", "a lock remover for a conquered citadel", "a lockpick for a conquered citadel"], "a Ganon's Castle Small Key", "no_gender"),
    'Small Key (Thieves Hideout)':                              (["a get out of jail free card"], "a Jail Key", "no_gender"),
    'Small Key (Treasure Chest Game)':                          (["a key to becoming a winner"], "a Game Key", "no_gender"),
    'Small Key Ring (Forest Temple)':                           (["a toolbox for unlocking a deep forest", "a dungeon season pass for a deep forest", "a jingling ring for a deep forest", "a skeleton key for a deep forest"], "a Forest Temple Small Key Ring", "no_gender"),
    'Small Key Ring (Fire Temple)':                             (["a toolbox for unlocking a high mountain", "a dungeon season pass for a high mountain", "a jingling ring for a high mountain", "a skeleton key for a high mountain"], "a Fire Temple Small Key Ring", "no_gender"),
    'Small Key Ring (Water Temple)':                            (["a toolbox for unlocking a vast lake", "a dungeon season pass for under a vast lake", "a jingling ring for under a vast lake", "a skeleton key for under a vast lake"], "a Water Temple Small Key Ring", "no_gender"),
    'Small Key Ring (Shadow Temple)':                           (["a toolbox for unlocking the house of the dead", "a dungeon season pass for the house of the dead", "a jingling ring for the house of the dead", "a skeleton key for the house of the dead"], "a Shadow Temple Small Key Ring", "no_gender"),
    'Small Key Ring (Spirit Temple)':                           (["a toolbox for unlocking a goddess of the sand", "a dungeon season pass for a goddess of the sand", "a jingling ring for a goddess of the sand", "a skeleton key for a goddess of the sand"], "a Spirit Temple Small Key Ring", "no_gender"),
    'Small Key Ring (Bottom of the Well)':                      (["a toolbox for unlocking a shadow's prison", "a dungeon season pass for a shadow's prison", "a jingling ring for a shadow's prison", "a skeleton key for a shadow's prison"], "a Bottom of the Well Small Key Ring", "no_gender"),
    'Small Key Ring (Gerudo Training Ground)':                  (["a toolbox for unlocking the test of thieves", "a dungeon season pass for the test of thieves", "a jingling ring for the test of thieves", "a skeleton key for the test of thieves"], "a Gerudo Training Ground Small Key Ring", "no_gender"),
    'Small Key Ring (Ganons Castle)':                           (["a toolbox for unlocking a conquered citadel", "a dungeon season pass for a conquered citadel", "a jingling ring for a conquered citadel", "a skeleton key for a conquered citadel"], "a Ganon's Castle Small Key Ring", "no_gender"),
    'Small Key Ring (Thieves Hideout)':                         (["a deck of get out of jail free cards"], "a Jail Key Ring", "no_gender"),
    'Small Key Ring (Treasure Chest Game)':                     (["the keys to becoming a winner"], "a Game Key Ring", "no_gender"),
    'Silver Rupee (Dodongos Cavern Staircase)':                 (["an entry fee for an immense cavern", "a priced artifact from an immense cavern"], "a Silver Rupee for Dodongo's Cavern", "no_gender"),
    'Silver Rupee (Ice Cavern Spinning Scythe)':                (["an entry fee for a frozen maze", "a priced artifact from a frozen maze"], "a Silver Rupee for the Ice Cavern", "no_gender"),
    'Silver Rupee (Ice Cavern Push Block)':                     (["an entry fee for a frozen maze", "a priced artifact from a frozen maze"], "a Silver Rupee for the Ice Cavern", "no_gender"),
    'Silver Rupee (Bottom of the Well Basement)':               (["an entry fee for a shadow's prison", "a priced artifact from a shadow's prison"], "a Silver Rupee for the Bottom of the Well", "no_gender"),
    'Silver Rupee (Shadow Temple Scythe Shortcut)':             (["an entry fee for the house of the dead", "a priced artifact from the house of the dead"], "a Silver Rupee for the Shadow Temple", "no_gender"),
    'Silver Rupee (Shadow Temple Invisible Blades)':            (["an entry fee for the house of the dead", "a priced artifact from the house of the dead"], "a Silver Rupee for the Shadow Temple", "no_gender"),
    'Silver Rupee (Shadow Temple Huge Pit)':                    (["an entry fee for the house of the dead", "a priced artifact from the house of the dead"], "a Silver Rupee for the Shadow Temple", "no_gender"),
    'Silver Rupee (Shadow Temple Invisible Spikes)':            (["an entry fee for the house of the dead", "a priced artifact from the house of the dead"], "a Silver Rupee for the Shadow Temple", "no_gender"),
    'Silver Rupee (Gerudo Training Ground Slopes)':             (["an entry fee for the test of thieves", "a priced artifact from the test of thieves"], "a Silver Rupee for the Gerudo Training Ground", "no_gender"),
    'Silver Rupee (Gerudo Training Ground Lava)':               (["an entry fee for the test of thieves", "a priced artifact from the test of thieves"], "a Silver Rupee for the Gerudo Training Ground", "no_gender"),
    'Silver Rupee (Gerudo Training Ground Water)':              (["an entry fee for the test of thieves", "a priced artifact from the test of thieves"], "a Silver Rupee for the Gerudo Training Ground", "no_gender"),
    'Silver Rupee (Spirit Temple Child Early Torches)':         (["an entry fee for a goddess of the sand", "a priced artifact from a goddess of the sand"], "a Silver Rupee for the Spirit Temple", "no_gender"),
    'Silver Rupee (Spirit Temple Adult Boulders)':              (["an entry fee for a goddess of the sand", "a priced artifact from a goddess of the sand"], "a Silver Rupee for the Spirit Temple", "no_gender"),
    'Silver Rupee (Spirit Temple Lobby and Lower Adult)':       (["an entry fee for a goddess of the sand", "a priced artifact from a goddess of the sand"], "a Silver Rupee for the Spirit Temple", "no_gender"),
    'Silver Rupee (Spirit Temple Sun Block)':                   (["an entry fee for a goddess of the sand", "a priced artifact from a goddess of the sand"], "a Silver Rupee for the Spirit Temple", "no_gender"),
    'Silver Rupee (Spirit Temple Adult Climb)':                 (["an entry fee for a goddess of the sand", "a priced artifact from a goddess of the sand"], "a Silver Rupee for the Spirit Temple", "no_gender"),
    'Silver Rupee (Ganons Castle Spirit Trial)':                (["an entry fee for a conquered citadel", "a priced artifact from a conquered citadel"], "a Silver Rupee for Ganon's Castle", "no_gender"),
    'Silver Rupee (Ganons Castle Light Trial)':                 (["an entry fee for a conquered citadel", "a priced artifact from a conquered citadel"], "a Silver Rupee for Ganon's Castle", "no_gender"),
    'Silver Rupee (Ganons Castle Fire Trial)':                  (["an entry fee for a conquered citadel", "a priced artifact from a conquered citadel"], "a Silver Rupee for Ganon's Castle", "no_gender"),
    'Silver Rupee (Ganons Castle Shadow Trial)':                (["an entry fee for a conquered citadel", "a priced artifact from a conquered citadel"], "a Silver Rupee for Ganon's Castle", "no_gender"),
    'Silver Rupee (Ganons Castle Water Trial)':                 (["an entry fee for a conquered citadel", "a priced artifact from a conquered citadel"], "a Silver Rupee for Ganon's Castle", "no_gender"),
    'Silver Rupee (Ganons Castle Forest Trial)':                (["an entry fee for a conquered citadel", "a priced artifact from a conquered citadel"], "a Silver Rupee for Ganon's Castle", "no_gender"),
    'Silver Rupee Pouch (Dodongos Cavern Staircase)':           (["a silver lining for an immense cavern", "a stash of silver shekels for an immense cavern"], "a Pouch of Silver Rupees for Dodongo's Cavern", "no_gender"),
    'Silver Rupee Pouch (Ice Cavern Spinning Scythe)':          (["a silver lining for a frozen maze", "a stash of silver shekels for a frozen maze"], "a Pouch of Silver Rupees for the Ice Cavern", "no_gender"),
    'Silver Rupee Pouch (Ice Cavern Push Block)':               (["a silver lining for a frozen maze", "a stash of silver shekels for a frozen maze"], "a Pouch of Silver Rupees for the Ice Cavern", "no_gender"),
    'Silver Rupee Pouch (Bottom of the Well Basement)':         (["a silver lining for a shadow's prison", "a stash of silver shekels for a shadow's prison"], "a Pouch of Silver Rupees for the Bottom of the Well", "no_gender"),
    'Silver Rupee Pouch (Shadow Temple Scythe Shortcut)':       (["a silver lining for the house of the dead", "a stash of silver shekels for the house of the dead"], "a Pouch of Silver Rupees for the Shadow Temple", "no_gender"),
    'Silver Rupee Pouch (Shadow Temple Invisible Blades)':      (["a silver lining for the house of the dead", "a stash of silver shekels for the house of the dead"], "a Pouch of Silver Rupees for the Shadow Temple", "no_gender"),
    'Silver Rupee Pouch (Shadow Temple Huge Pit)':              (["a silver lining for the house of the dead", "a stash of silver shekels for the house of the dead"], "a Pouch of Silver Rupees for the Shadow Temple", "no_gender"),
    'Silver Rupee Pouch (Shadow Temple Invisible Spikes)':      (["a silver lining for the house of the dead", "a stash of silver shekels for the house of the dead"], "a Pouch of Silver Rupees for the Shadow Temple", "no_gender"),
    'Silver Rupee Pouch (Gerudo Training Ground Slopes)':       (["a silver lining for the test of thieves", "a stash of silver shekels for the test of thieves"], "a Pouch of Silver Rupees for the Gerudo Training Ground", "no_gender"),
    'Silver Rupee Pouch (Gerudo Training Ground Lava)':         (["a silver lining for the test of thieves", "a stash of silver shekels for the test of thieves"], "a Pouch of Silver Rupees for the Gerudo Training Ground", "no_gender"),
    'Silver Rupee Pouch (Gerudo Training Ground Water)':        (["a silver lining for the test of thieves", "a stash of silver shekels for the test of thieves"], "a Pouch of Silver Rupees for the Gerudo Training Ground", "no_gender"),
    'Silver Rupee Pouch (Spirit Temple Child Early Torches)':   (["a silver lining for a goddess of the sand", "a stash of silver shekels for a goddess of the sand"], "a Pouch of Silver Rupees for the Spirit Temple", "no_gender"),
    'Silver Rupee Pouch (Spirit Temple Adult Boulders)':        (["a silver lining for a goddess of the sand", "a stash of silver shekels for a goddess of the sand"], "a Pouch of Silver Rupees for the Spirit Temple", "no_gender"),
    'Silver Rupee Pouch (Spirit Temple Lobby and Lower Adult)': (["a silver lining for a goddess of the sand", "a stash of silver shekels for a goddess of the sand"], "a Pouch of Silver Rupees for the Spirit Temple", "no_gender"),
    'Silver Rupee Pouch (Spirit Temple Sun Block)':             (["a silver lining for a goddess of the sand", "a stash of silver shekels for a goddess of the sand"], "a Pouch of Silver Rupees for the Spirit Temple", "no_gender"),
    'Silver Rupee Pouch (Spirit Temple Adult Climb)':           (["a silver lining for a goddess of the sand", "a stash of silver shekels for a goddess of the sand"], "a Pouch of Silver Rupees for the Spirit Temple", "no_gender"),
    'Silver Rupee Pouch (Ganons Castle Spirit Trial)':          (["a silver lining for a conquered citadel", "a stash of silver shekels for a conquered citadel"], "a Pouch of Silver Rupees for Ganon's Castle", "no_gender"),
    'Silver Rupee Pouch (Ganons Castle Light Trial)':           (["a silver lining for a conquered citadel", "a stash of silver shekels for a conquered citadel"], "a Pouch of Silver Rupees for Ganon's Castle", "no_gender"),
    'Silver Rupee Pouch (Ganons Castle Fire Trial)':            (["a silver lining for a conquered citadel", "a stash of silver shekels for a conquered citadel"], "a Pouch of Silver Rupees for Ganon's Castle", "no_gender"),
    'Silver Rupee Pouch (Ganons Castle Shadow Trial)':          (["a silver lining for a conquered citadel", "a stash of silver shekels for a conquered citadel"], "a Pouch of Silver Rupees for Ganon's Castle", "no_gender"),
    'Silver Rupee Pouch (Ganons Castle Water Trial)':           (["a silver lining for a conquered citadel", "a stash of silver shekels for a conquered citadel"], "a Pouch of Silver Rupees for Ganon's Castle", "no_gender"),
    'Silver Rupee Pouch (Ganons Castle Forest Trial)':          (["a silver lining for a conquered citadel", "a stash of silver shekels for a conquered citadel"], "a Pouch of Silver Rupees for Ganon's Castle", "no_gender"),
    'KeyError':                                                 (["something mysterious", "an unknown treasure"], "An Error (Please Report This)", "no_gender"),
    'Arrows (5)':                                               (["a few danger darts", "a few sharp shafts"], "Arrows (5 pieces)", "no_gender"),
    'Arrows (10)':                                              (["some danger darts", "some sharp shafts"], "Arrows (10 pieces)", "no_gender"),
    'Arrows (30)':                                              (["plenty of danger darts", "plenty of sharp shafts"], "Arrows (30 pieces)", "no_gender"),
    'Bombs (5)':                                                (["a few explosives", "a few blast balls"], "Bombs (5 pieces)", "no_gender"),
    'Bombs (10)':                                               (["some explosives", "some blast balls"], "Bombs (10 pieces)", "no_gender"),
    'Bombs (20)':                                               (["lots-o-explosives", "plenty of blast balls"], "Bombs (20 pieces)", "no_gender"),
    'Ice Trap':                                                 (["a gift from Ganon", "a chilling discovery", "frosty fun"], "an Ice Trap", "no_gender"),
    'Magic Bean':                                               (["a wizardly legume"], "a Magic Bean", "no_gender"),
    'Buy Magic Bean':                                           (["a wizardly legume"], "a Magic Bean", "no_gender"),
    'Magic Bean Pack':                                          (["wizardly legumes"], "Magic Beans", "no_gender"),
    'Bombchus':                                                 (["mice bombs", "proximity mice", "wall crawlers", "trail blazers"], "Bombchus", "no_gender"),
    'Bombchus (5)':                                             (["a few mice bombs", "a few proximity mice", "a few wall crawlers", "a few trail blazers"], "Bombchus (5 pieces)", "no_gender"),
    'Bombchus (10)':                                            (["some mice bombs", "some proximity mice", "some wall crawlers", "some trail blazers"], "Bombchus (10 pieces)", "no_gender"),
    'Bombchus (20)':                                            (["plenty of mice bombs", "plenty of proximity mice", "plenty of wall crawlers", "plenty of trail blazers"], "Bombchus (20 pieces)", "no_gender"),
    'Deku Nuts (5)':                                            (["some nuts", "some flashbangs", "some scrub spit"], "Deku Nuts (5 pieces)", "no_gender"),
    'Deku Nuts (10)':                                           (["lots-o-nuts", "plenty of flashbangs", "plenty of scrub spit"], "Deku Nuts (10 pieces)", "no_gender"),
    'Deku Seeds (30)':                                          (["catapult ammo", "lots-o-seeds"], "Deku Seeds (30 pieces)", "no_gender"),
    'Gold Skulltula Token':                                     (["proof of destruction", "an arachnid chip", "spider remains", "one percent of a curse"], "a Gold Skulltula Token", "no_gender"),
    'Ocarina A Button':                                         (["a blue note"], "the Ocarina A Button", "no_gender"),
    'Ocarina C up Button':                                      (["a high note"], "the Ocarina C up Button", "no_gender"),
    'Ocarina C down Button':                                    (["a low note"], "the Ocarina C down Button", "no_gender"),
    'Ocarina C left Button':                                    (["a somewhat high note"], "the Ocarina C left Button", "no_gender"),
    'Ocarina C right Button':                                   (["a middle note"], "the Ocarina C right Button", "no_gender"),
    'Fairy Drop':                                               (["an annoying companion", "Navi's cousin"], "a Stray Fairy", "no_gender"),
    'Nothing':                                                  (["emptiness", "loneliness"], "Nothing", "no_gender"),

    'ZR Frogs Ocarina Game':                                       (["an #amphibian feast# yields", "the #croaking choir's magnum opus# awards", "the #froggy finale# yields"], "the final reward from the #Frogs of Zora's River# is", None),
    'KF Links House Cow':                                          ("the #bovine bounty of a horseback hustle# gifts", "#Malon's obstacle course# leads to", None),

    'Song from Ocarina of Time':                                   ("the #Ocarina of Time# teaches", "the song taught by the #Ocarina of Time# is", None),
    'Song from Royal Familys Tomb':                                (["#ReDead in the royal tomb# guard", "the #Composer Brothers wrote#"], "the song written in the #royal tomb# is", None),
    'Sheik in Forest':                                             ("#in a meadow# Sheik teaches", "in the #Sacred Forest Meadow#, Sheik teaches", None),
    'Sheik at Temple':                                             ("Sheik waits at a #monument to time# to teach", "the #Temple of Time# chimes with the music of", None),
    'Sheik in Crater':                                             ("the #crater's melody# is", "Sheik waits in the #Death Mountain Crater# to teach", None),
    'Sheik in Ice Cavern':                                         ("the #frozen cavern# echoes with", "the #Ice Cavern# corridors ring with", None),
    'Sheik in Kakariko':                                           ("a #ravaged village# mourns with", "amidst flames in #Kakariko Village#, Sheik gives", None),
    'Sheik at Colossus':                                           ("a hero ventures #beyond the wasteland# to learn", "the #Desert Colossus# sands echo with", None),

    'Market 10 Big Poes':                                          ("#ghost hunters# will be rewarded with", "catching #Big Poes# leads to", None),
    'Deku Theater Skull Mask':                                     ("the #Skull Mask# yields", "wearing the #Skull Mask in the Deku Theater# rewards", None),
    'Deku Theater Mask of Truth':                                  ("showing a #truthful eye to the crowd# rewards", "showing the #Mask of Truth in the Deku Theater# rewards", None),
    'HF Ocarina of Time Item':                                     ("the #treasure thrown by Princess Zelda# is", None, None),
    'DMT Biggoron':                                                ("#Biggoron# crafts", "showing the #Claim Check to Biggoron# rewards", None),
    'Kak 100 Gold Skulltula Reward':                               (["#100 bug badges# rewards", "#100 spider souls# yields", "#100 auriferous arachnids# lead to"], "slaying #100 Gold Skulltulas# reveals", None),
    'Kak 50 Gold Skulltula Reward':                                (["#50 bug badges# rewards", "#50 spider souls# yields", "#50 auriferous arachnids# lead to"], "slaying #50 Gold Skulltulas# reveals", None),
    'Kak 40 Gold Skulltula Reward':                                (["#40 bug badges# rewards", "#40 spider souls# yields", "#40 auriferous arachnids# lead to"], "slaying #40 Gold Skulltulas# reveals", None),
    'Kak 30 Gold Skulltula Reward':                                (["#30 bug badges# rewards", "#30 spider souls# yields", "#30 auriferous arachnids# lead to"], "slaying #30 Gold Skulltulas# reveals", None),
    'Kak 20 Gold Skulltula Reward':                                (["#20 bug badges# rewards", "#20 spider souls# yields", "#20 auriferous arachnids# lead to"], "slaying #20 Gold Skulltulas# reveals", None),
    'Kak Anju as Child':                                           (["#wrangling roosters# rewards", "#chucking chickens# gifts"], "#collecting cuccos# rewards", None),
    'GC Darunias Joy':                                             ("a #groovin' goron# gifts", "#Darunia's dance# leads to", None),
    'LW Skull Kid':                                                ("the #Skull Kid# grants", None, None),
    'LH Sun':                                                      ("staring into #the sun# grants", "shooting #the sun# grants", None),
    'Market Treasure Chest Game Reward':                           (["#gambling in the market# grants", "there is a #1/32 chance# to win"], "winning the #treasure chest game# rewards", None),
    'GF HBA 1500 Points':                                          ("mastery of #horseback archery# grants", "scoring 1500 in #horseback archery# grants", None),
    'Graveyard Heart Piece Grave Chest':                           ("playing #Sun's Song# in a grave spawns", None, None),
    'GC Maze Left Chest':                                          ("in #Goron City# the hammer unlocks", None, None),
    'GV Chest':                                                    ("in #Gerudo Valley# the hammer unlocks", None, None),
    'GV Cow':                                                      ("a #cow in Gerudo Valley# gifts", None, None),
    'HC GS Storms Grotto':                                         ("a #spider behind a muddy wall# in a grotto holds", None, None),
    'HF GS Cow Grotto':                                            ("a #spider behind webs# in a grotto holds", None, None),
    'HF Cow Grotto Cow':                                           ("the #cobwebbed cow# gifts", "a #cow behind webs# in a grotto gifts", None),
    'ZF GS Hidden Cave':                                           ("a spider high #above the icy waters# holds", None, None),
    'Wasteland Chest':                                             (["#deep in the wasteland# is", "beneath #the sands#, flames reveal"], "the #Haunted Wasteland torches# reveal", None),
    'Wasteland GS':                                                ("a #spider in the wasteland# holds", None, None),
    'Graveyard Royal Familys Tomb Chest':                          (["#flames in the royal tomb# reveal", "the #Composer Brothers hid#"], "#lighting flames in the royal tomb# rewards", None),
    'ZF Bottom Freestanding PoH':                                  ("#under the icy waters# lies", "at the #bottom of Zora's Fountain# lies", None),
    'GC Pot Freestanding PoH':                                     ("spinning #Goron pottery# contains", "the #Goron Pot's happy face# spits out", None),
    'ZD King Zora Thawed':                                         ("a #defrosted dignitary# gifts", "unfreezing #King Zora# grants", None),
    'DMC Deku Scrub':                                              ("a single #scrub in the crater# sells", "a lone #scrub in Death Mountain Crater# sells", None),
    'DMC GS Crate':                                                ("a spider under a #crate in the crater# holds", None, None),
    'LW Target in Woods':                                          ("shooting a #target in the woods# grants", None, None),
    'ZR Frogs in the Rain':                                        ("#frogs in a storm# gift", "playing #Song of Storms to Frogs# rewards", None),
    'LH Lab Dive':                                                 ("a #diving experiment# is rewarded with", "a #lakeside lab diving experiment# rewards", None),
    'HC Great Fairy Reward':                                       ("the #fairy of fire# holds", "a #fairy outside Hyrule Castle# holds", None),
    'OGC Great Fairy Reward':                                      ("the #fairy of strength# holds", "a #fairy outside Ganon's Castle# holds", None),

    'Deku Tree MQ After Spinning Log Chest':                       ("a #temporal stone within a tree# contains", "a #temporal stone within the Deku Tree# contains", None),
    'Deku Tree MQ GS Basement Graves Room':                        ("a #spider on a ceiling in a tree# holds", "a #spider on a ceiling in the Deku Tree# holds", None),
    'Dodongos Cavern MQ GS Song of Time Block Room':               ("a spider under #temporal stones in a cavern# holds", "a spider under #temporal stones in Dodongo's Cavern# holds", None),
    'Jabu Jabus Belly Boomerang Chest':                            ("a school of #stingers swallowed by a deity# guard", "a school of #stingers swallowed by Jabu Jabu# guard", None),
    'Jabu Jabus Belly MQ GS Invisible Enemies Room':               ("a spider surrounded by #shadows in the belly of a deity# holds", "a spider surrounded by #shadows in Jabu Jabu's Belly# holds", None),
    'Jabu Jabus Belly MQ Cow':                                     ("a #cow swallowed by a deity# gifts", "a #cow swallowed by Jabu Jabu# gifts", None),
    'Fire Temple Scarecrow Chest':                                 ("a #scarecrow atop the volcano# hides", "#Pierre atop the Fire Temple# hides", None),
    'Fire Temple Megaton Hammer Chest':                            ("the #Flare Dancer atop the volcano# guards a chest containing", "the #Flare Dancer atop the Fire Temple# guards a chest containing", None),
    'Fire Temple MQ Chest On Fire':                                ("the #Flare Dancer atop the volcano# guards a chest containing", "the #Flare Dancer atop the Fire Temple# guards a chest containing", None),
    'Fire Temple MQ GS Skull On Fire':                             ("a #spider under a block in the volcano# holds", "a #spider under a block in the Fire Temple# holds", None),
    'Water Temple River Chest':                                    ("beyond the #river under the lake# waits", "beyond the #river in the Water Temple# waits", None),
    'Water Temple Central Pillar Chest':                           ("beneath a #tall tower under a vast lake# lies", "a chest in the #central pillar of Water Temple# contains", None),
    'Water Temple Boss Key Chest':                                 ("dodging #rolling boulders under the lake# leads to", "dodging #rolling boulders in the Water Temple# leads to", None),
    'Water Temple GS Behind Gate':                                 ("a spider behind a #gate under the lake# holds", "a spider behind a #gate in the Water Temple# holds", None),
    'Water Temple MQ Central Pillar Chest':                        ("beneath a #tall tower under a vast lake# lies", "a chest in the #central pillar of Water Temple# contains", None),
    'Water Temple MQ Freestanding Key':                            ("hidden in a #box under the lake# lies", "hidden in a #box in the Water Temple# lies", None),
    'Water Temple MQ GS Freestanding Key Area':                    ("the #locked spider under the lake# holds", "the #locked spider in the Water Temple# holds", None),
    'Water Temple MQ GS Triple Wall Torch':                        ("a spider behind a #gate under the lake# holds", "a spider behind a #gate in the Water Temple# holds", None),
    'Gerudo Training Ground Underwater Silver Rupee Chest':        (["those who seek #sunken silver rupees# will find", "the #thieves' underwater training# rewards"], "obtaining the #underwater silver rupees in Gerudo Training Ground# rewards", None),
    'Gerudo Training Ground MQ Underwater Silver Rupee Chest':     (["those who seek #sunken silver rupees# will find", "the #thieves' underwater training# rewards"], "obtaining the #underwater silver rupees in Gerudo Training Ground# rewards", None),
    'Gerudo Training Ground Maze Path Final Chest':                ("the final prize of #the thieves' training# is", "#Gerudo Training Ground final reward# contains", None),
    'Gerudo Training Ground MQ Ice Arrows Chest':                  ("the final prize of #the thieves' training# is", "#Gerudo Training Ground final reward# contains", None),
    'Spirit Temple Silver Gauntlets Chest':                        ("the treasure #sought by Nabooru# is", "upon the #Colossus's right hand# is", None),
    'Spirit Temple Mirror Shield Chest':                           ("upon the #Colossus's left hand# is", None, None),
    'Spirit Temple MQ Child Hammer Switch Chest':                  ("a #temporal paradox in the Colossus# yields", "a #temporal paradox in the Spirit Temple# yields", None),
    'Spirit Temple MQ Symphony Room Chest':                        ("a #symphony in the Colossus# yields", "a #symphony in the Spirit Temple# yields", None),
    'Spirit Temple MQ GS Symphony Room':                           ("a #spider's symphony in the Colossus# yields", "a #spider's symphony in the Spirit Temple# yields", None),
    'Shadow Temple Freestanding Key':                              ("a #burning skull in the house of the dead# holds", "a #giant pot in the Shadow Temple# holds", None),
    'Shadow Temple MQ Bomb Flower Chest':                          ("a #grasping ghoul surrounded by Bomb Flowers# guards", "the #Dead Hand surrounded by Bomb Flowers# guards", None),
    'Shadow Temple MQ Stalfos Room Chest':                         ("near an #empty pedestal within the house of the dead# lies", "#stalfos in the Shadow Temple# guard", None),
    'Ice Cavern Iron Boots Chest':                                 ("a #monster in a frozen cavern# guards", "the #final treasure of Ice Cavern# is", None),
    'Ice Cavern MQ Iron Boots Chest':                              ("a #monster in a frozen cavern# guards", "the #final treasure of Ice Cavern# is", None),
    'Ganons Castle Shadow Trial Golden Gauntlets Chest':           ("#deep in the test of darkness# lies", "a #like-like in Ganon's Shadow Trial# guards", None),
    'Ganons Castle MQ Shadow Trial Eye Switch Chest':              ("#deep in the test of darkness# lies", "shooting an #eye switch in Ganon's Shadow Trial# reveals", None),

    'Deku Theater Rewards':                                        ("the #Skull Mask and Mask of Truth# reward...^", None, None),
    'HF Ocarina of Time Retrieval':                                ("during her escape, #Princess Zelda# entrusted you with both...^", "the #Ocarina of Time# rewards both...^", None),
    'HF Valley Grotto':                                            ("in a grotto with a #spider and a cow# you will find...^", None, None),
    'Market Bombchu Bowling Rewards':                              ("at the #Bombchu Bowling Alley#, you will be rewarded with...^", None, None),
    'ZR Frogs Rewards':                                            ("the #Frogs of Zora River# will reward you with...^", None, None),
    'ZD Child Checks':                                             ("the Zora's Domain #diving game and torch run# lead to...^", None, None),
    'LH Lake Lab Pool':                                            ("inside the #lakeside lab# a person and a spider hold...^", None, None),
    'LH Adult Bean Destination Checks':                            ("#riding the bean in Lake Hylia# leads to...^", None, None),
    'GV Pieces of Heart Ledges':                                   ("within the #valley#, the crate and waterfall conceal...^", None, None),
    'GF Horseback Archery Rewards':                                ("the #Gerudo Horseback Archery# rewards...^", None, None),
    'Colossus Nighttime GS':                                       ("#at the Desert Colossus#, skulltulas at night hold...^", None, None),
    'Graveyard Dampe Race Rewards':                                ("racing #Dampé's ghost# rewards...^", None, None),
    'Graveyard Royal Family Tomb Contents':                        ("inside the #Royal Family Tomb#, you will find...^", None, None),
    'DMC Child Upper Checks':                                      ("in the #crater, a spider in a crate and a single scrub# guard...^", None, None),
    'Haunted Wasteland Checks':                                    ("deep in the #wasteland a spider and a chest# hold...^", None, None),
    'Castle Fairy Checks':                                         ("Great Fairies outside #Hyrule and Ganon's castles# reward...^", None, None),
    'King Zora Items':                                             ("#unfreezing King Zora and giving him the Prescription# rewards...^", None, None),

    'Deku Tree MQ Basement GS':                                    ("in the back of the #basement of the Great Deku Tree# two spiders hold...^", None, None),
    'Dodongos Cavern Upper Business Scrubs':                       ("deep in #Dodongo's Cavern a pair of scrubs# sell...^", None, None),
    'Dodongos Cavern MQ Larvae Room':                              ("amid #larvae in Dodongo's Cavern# a chest and a spider hold...^", None, None),
    'Fire Temple Lower Loop':                                      ("under the #entrance of the Fire Temple# a blocked path leads to...^", None, None),
    'Fire Temple MQ Lower Loop':                                   ("under the #entrance of the Fire Temple# a blocked path leads to...^", None, None),
    'Water Temple River Loop Chests':                              ("#chests past a shadowy fight# in the Water Temple hold...^", "#chests past Dark Link# in the Water Temple hold...^", None),
    'Water Temple River Checks':                                   ("in the #river in the Water Temple# lies...^", None, None),
    'Water Temple North Basement Checks':                          ("the #northern basement of the Water Temple# contains...^", None, None),
    'Water Temple MQ North Basement Checks':                       ("the #northern basement of the Water Temple# contains...^", None, None),
    'Water Temple MQ Lower Checks':                                ("#a chest and a crate in locked basements# in the Water Temple hold...^", None, None),
    'Spirit Temple Colossus Hands':                                ("upon the #Colossus's right and left hands# lie...^", None, None),
    'Spirit Temple Child Lower':                                   ("between the #crawl spaces in the Spirit Temple# chests contain...^", None, None),
    'Spirit Temple Child Top':                                     ("on the path to the #right hand of the Spirit Temple# a chest and a spider hold...^", None, None),
    'Spirit Temple Adult Lower':                                   ("past a #silver block in the Spirit Temple# a melody and boulders conceal...^", None, None),
    'Spirit Temple MQ Child Top':                                  ("on the path to the #right hand of the Spirit Temple# a chest and a spider hold respectively...^", None, None),
    'Spirit Temple MQ Symphony Room':                              ("#the symphony room# in the Spirit Temple protects...^", None, None),
    'Spirit Temple MQ Throne Room GS':                             ("in the #nine thrones room# of the Spirit Temple spiders hold...^", None, None),
    'Shadow Temple Invisible Blades Chests':                       ("an #invisible spinning blade# in the Shadow Temple guards...^", None, None),
    'Shadow Temple Single Pot Room':                               ("a room containing #a single skull-shaped pot# holds...^", "a room containing a #large pot in the Shadow Temple# holds...^", None),
    'Shadow Temple Spike Walls Room':                              ("#wooden walls# in the Shadow Temple hide...^", None, None),
    'Shadow Temple MQ Upper Checks':                               ("#before the Truth Spinner gap# in the Shadow Temple locked chests contain...^", None, None),
    'Shadow Temple MQ Invisible Blades Chests':                    ("an #invisible spinning blade# in the Shadow Temple guards...^", None, None),
    'Shadow Temple MQ Spike Walls Room':                           ("#wooden walls# in the Shadow Temple hide...^", None, None),
    'Bottom of the Well Inner Rooms GS':                           ("in the #central rooms of the well# spiders hold...^", None, None),
    'Bottom of the Well Dead Hand Room':                           ("#Dead Hand in the well# guards...^", None, None),
    'Bottom of the Well MQ Dead Hand Room':                        ("#Dead Hand in the well# guards...^", None, None),
    'Bottom of the Well MQ Basement':                              ("in the #depths of the well# a spider and a chest hold...^", None, None),
    'Ice Cavern Final Room':                                       ("the #final treasures of Ice Cavern# are...^", None, None),
    'Ice Cavern MQ Final Room':                                    ("the #final treasures of Ice Cavern# are...^", None, None),
    'Ganons Castle Spirit Trial Chests':                           ("#within the Spirit Trial#, chests contain...^", None, None),

    'Queen Gohma Rewards':                                         ("the #Parasitic Armored Arachnid# holds...^", "#Queen Gohma# holds...^", None),
    'King Dodongo Rewards':                                        ("the #Infernal Dinosaur# holds...^", "#King Dodongo# holds...^", None),
    'Barinade Rewards':                                            ("the #Bio-Electric Anemone# holds...^", "#Barinade# holds...^", None),
    'Phantom Ganon Rewards':                                       ("the #Evil Spirit from Beyond# holds...^", "#Phantom Ganon# holds...^", None),
    'Volvagia Rewards':                                            ("the #Subterranean Lava Dragon# holds...^", "#Volvagia# holds...^", None),
    'Morpha Rewards':                                              ("the #Giant Aquatic Amoeba# holds...^", "#Morpha# holds...^", None),
    'Bongo Bongo Rewards':                                         ("the #Phantom Shadow Beast# holds...^", "#Bongo Bongo# holds...^", None),
    'Twinrova Rewards':                                            ("the #Sorceress Sisters# hold...^", "#Twinrova# holds...^", None),

    'KF Kokiri Sword Chest':                                       ("the #hidden treasure of the Kokiri# is", None, None),
    'KF Midos Top Left Chest':                                     ("the #leader of the Kokiri# hides", "#inside Mido's house# is", None),
    'KF Midos Top Right Chest':                                    ("the #leader of the Kokiri# hides", "#inside Mido's house# is", None),
    'KF Midos Bottom Left Chest':                                  ("the #leader of the Kokiri# hides", "#inside Mido's house# is", None),
    'KF Midos Bottom Right Chest':                                 ("the #leader of the Kokiri# hides", "#inside Mido's house# is", None),
    'Graveyard Shield Grave Chest':                                ("the #treasure of a fallen soldier# is", None, None),
    'DMT Chest':                                                   ("hidden behind a wall on a #mountain trail# is", None, None),
    'GC Maze Right Chest':                                         ("in #Goron City# explosives unlock", None, None),
    'GC Maze Center Chest':                                        ("in #Goron City# explosives unlock", None, None),
    'ZD Chest':                                                    ("fire #beyond a waterfall# reveals", None, None),
    'Graveyard Dampe Race Hookshot Chest':                         ("a chest hidden by a #speedy spectre# holds", "#dead Dampé's first prize# is", None),
    'GF Chest':                                                    ("on a #rooftop in the desert# lies", None, None),
    'Kak Redead Grotto Chest':                                     ("#zombies beneath the earth# guard", None, None),
    'SFM Wolfos Grotto Chest':                                     ("#wolves beneath the earth# guard", None, None),
    'HF Near Market Grotto Chest':                                 ("a #hole in a field near a drawbridge# holds", None, None),
    'HF Southeast Grotto Chest':                                   ("a #hole amongst trees in a field# holds", None, None),
    'HF Open Grotto Chest':                                        ("an #open hole in a field# holds", None, None),
    'Kak Open Grotto Chest':                                       ("an #open hole in a town# holds", None, None),
    'ZR Open Grotto Chest':                                        ("a #hole along a river# holds", None, None),
    'KF Storms Grotto Chest':                                      ("a #hole in a forest village# holds", None, None),
    'LW Near Shortcuts Grotto Chest':                              ("a #hole in a wooded maze# holds", None, None),
    'DMT Storms Grotto Chest':                                     ("#hole flooded with rain on a mountain# holds", None, None),
    'DMC Upper Grotto Chest':                                      ("a #hole in a volcano# holds", None, None),

    'ToT Light Arrows Cutscene':                                   ("the #final gift of a princess# is", None, None),
    'LW Gift from Saria':                                          (["a #potato hoarder# holds", "a rooty tooty #flutey cutey# gifts"], "#Saria's Gift# is", None),
    'ZF Great Fairy Reward':                                       ("the #fairy of winds# holds", None, None),
    'Colossus Great Fairy Reward':                                 ("the #fairy of love# holds", None, None),
    'DMT Great Fairy Reward':                                      ("a #magical fairy# gifts", None, None),
    'DMC Great Fairy Reward':                                      ("a #magical fairy# gifts", None, None),

    'Song from Impa':                                              ("#deep in a castle#, Impa teaches", None, None),
    'Song from Malon':                                             ("#a farm girl# sings", None, None),
    'Song from Saria':                                             ("#deep in the forest#, Saria teaches", None, None),
    'Song from Windmill':                                          ("a man #in a windmill# is obsessed with", None, None),

    'HC Malon Egg':                                                ("a #girl looking for her father# gives", None, None),
    'HC Zeldas Letter':                                            ("a #princess in a castle# gifts", None, None),
    'ZD Diving Minigame':                                          ("an #unsustainable business model# gifts", "those who #dive for Zora rupees# will find", None),
    'LH Child Fishing':                                            ("#fishing in youth# bestows", None, None),
    'LH Adult Fishing':                                            ("#fishing in maturity# bestows", None, None),
    'LH Loach Fishing':                                            ("#catching the legendary fish# bestows", None, None),
    'GC Rolling Goron as Adult':                                   ("#comforting yourself# provides", "#reassuring a young Goron# is rewarded with", None),
    'Market Bombchu Bowling First Prize':                          ("the #first explosive prize# is", None, None),
    'Market Bombchu Bowling Second Prize':                         ("the #second explosive prize# is", None, None),
    'Market Lost Dog':                                             ("#puppy lovers# will find", "#rescuing Richard the Dog# is rewarded with", None),
    'LW Ocarina Memory Game':                                      (["the prize for a #game of Simon Says# is", "a #child sing-a-long# holds"], "#playing an Ocarina in Lost Woods# is rewarded with", None),
    'Kak 10 Gold Skulltula Reward':                                (["#10 bug badges# rewards", "#10 spider souls# yields", "#10 auriferous arachnids# lead to"], "slaying #10 Gold Skulltulas# reveals", None),
    'Kak Man on Roof':                                             ("a #rooftop wanderer# holds", None, None),
    'ZR Magic Bean Salesman':                                      ("a seller of #colorful crops# has", "a #bean seller# offers", None),
    'GF HBA 1000 Points':                                          ("scoring 1000 in #horseback archery# grants", None, None),
    'Market Shooting Gallery Reward':                              ("#shooting in youth# grants", None, None),
    'Kak Shooting Gallery Reward':                                 ("#shooting in maturity# grants", None, None),
    'Kak Anju as Adult':                                           ("a #chicken caretaker# offers adults", None, None),
    'LLR Talons Chickens':                                         ("#finding Super Cuccos# is rewarded with", None, None),
    'GC Rolling Goron as Child':                                   ("the prize offered by a #large rolling Goron# is", None, None),
    'LH Underwater Item':                                          ("the #sunken treasure in a lake# is", None, None),
    'Hideout Gerudo Membership Card':                              ("#rescuing captured carpenters# is rewarded with", None, None),
    'Wasteland Bombchu Salesman':                                  ("a #carpet guru# sells", None, None),
    'GC Medigoron':                                                ("#Medigoron# sells", None, None),

    'Kak Impas House Freestanding PoH':                            ("#imprisoned in a house# lies", None, None),
    'HF Tektite Grotto Freestanding PoH':                          ("#deep underwater in a hole# is", None, None),
    'Kak Windmill Freestanding PoH':                               ("on a #windmill ledge# lies", None, None),
    'Graveyard Dampe Race Freestanding PoH':                       ("#racing a ghost# leads to", "#dead Dampé's second# prize is", None),
    'LLR Freestanding PoH':                                        ("in a #ranch silo# lies", None, None),
    'Graveyard Freestanding PoH':                                  ("a #crate in a graveyard# hides", None, None),
    'Graveyard Dampe Gravedigging Tour':                           ("a #gravekeeper digs up#", None, None),
    'ZR Near Open Grotto Freestanding PoH':                        ("on top of a #pillar in a river# lies", None, None),
    'ZR Near Domain Freestanding PoH':                             ("on a #river ledge by a waterfall# lies", None, None),
    'LH Freestanding PoH':                                         ("high on a #lab rooftop# one can find", None, None),
    'ZF Iceberg Freestanding PoH':                                 ("#floating on ice# is", None, None),
    'GV Waterfall Freestanding PoH':                               ("behind a #desert waterfall# is", None, None),
    'GV Crate Freestanding PoH':                                   ("a #crate in a valley# hides", None, None),
    'Colossus Freestanding PoH':                                   ("on top of an #arch of stone# lies", None, None),
    'DMT Freestanding PoH':                                        ("above a #mountain cavern entrance# is", None, None),
    'DMC Wall Freestanding PoH':                                   ("nestled in a #volcanic wall# is", None, None),
    'DMC Volcano Freestanding PoH':                                ("obscured by #volcanic ash# is", None, None),
    'Hideout 1 Torch Jail Gerudo Key':                             ("#defeating Gerudo guards# reveals", None, None),
    'Hideout 2 Torches Jail Gerudo Key':                           ("#defeating Gerudo guards# reveals", None, None),
    'Hideout 3 Torches Jail Gerudo Key':                           ("#defeating Gerudo guards# reveals", None, None),
    'Hideout 4 Torches Jail Gerudo Key':                           ("#defeating Gerudo guards# reveals", None, None),

    'ZR Frogs Zeldas Lullaby':                                     ("after hearing #Zelda's Lullaby, frogs gift#", None, None),
    'ZR Frogs Eponas Song':                                        ("after hearing #Epona's Song, frogs gift#", None, None),
    'ZR Frogs Sarias Song':                                        ("after hearing #Saria's Song, frogs gift#", None, None),
    'ZR Frogs Suns Song':                                          ("after hearing the #Sun's Song, frogs gift#", None, None),
    'ZR Frogs Song of Time':                                       ("after hearing the #Song of Time, frogs gift#", None, None),

    'Deku Tree Map Chest':                                         ("in the #center of the Deku Tree# lies", None, None),
    'Deku Tree Slingshot Chest':                                   ("the #treasure guarded by a scrub# in the Deku Tree is", None, None),
    'Deku Tree Slingshot Room Side Chest':                         ("the #treasure guarded by a scrub# in the Deku Tree is", None, None),
    'Deku Tree Compass Chest':                                     ("#pillars of wood# in the Deku Tree lead to", None, None),
    'Deku Tree Compass Room Side Chest':                           ("#pillars of wood# in the Deku Tree lead to", None, None),
    'Deku Tree Basement Chest':                                    ("#webs in the Deku Tree# hide", None, None),

    'Deku Tree MQ Map Chest':                                      ("in the #center of the Deku Tree# lies", None, None),
    'Deku Tree MQ Compass Chest':                                  ("a #treasure guarded by a large spider# in the Deku Tree is", None, None),
    'Deku Tree MQ Slingshot Chest':                                ("#pillars of wood# in the Deku Tree lead to", None, None),
    'Deku Tree MQ Slingshot Room Back Chest':                      ("#pillars of wood# in the Deku Tree lead to", None, None),
    'Deku Tree MQ Basement Chest':                                 ("#webs in the Deku Tree# hide", None, None),
    'Deku Tree MQ Before Spinning Log Chest':                      ("#magical fire in the Deku Tree# leads to", None, None),

    'Dodongos Cavern Boss Room Chest':                             ("#above King Dodongo# lies", None, None),

    'Dodongos Cavern Map Chest':                                   ("a #muddy wall in Dodongo's Cavern# hides", None, None),
    'Dodongos Cavern Compass Chest':                               ("a #statue in Dodongo's Cavern# guards", None, None),
    'Dodongos Cavern Bomb Flower Platform Chest':                  ("above a #maze of stone# in Dodongo's Cavern lies", None, None),
    'Dodongos Cavern Bomb Bag Chest':                              ("the #second lizard cavern battle# yields", None, None),
    'Dodongos Cavern End of Bridge Chest':                         ("a #chest at the end of a bridge# yields", None, None),

    'Dodongos Cavern MQ Map Chest':                                ("a #muddy wall in Dodongo's Cavern# hides", None, None),
    'Dodongos Cavern MQ Bomb Bag Chest':                           ("an #elevated alcove# in Dodongo's Cavern holds", None, None),
    'Dodongos Cavern MQ Compass Chest':                            ("#fire-breathing lizards# in Dodongo's Cavern guard", None, None),
    'Dodongos Cavern MQ Larvae Room Chest':                        ("#baby spiders# in Dodongo's Cavern guard", None, None),
    'Dodongos Cavern MQ Torch Puzzle Room Chest':                  ("above a #maze of stone# in Dodongo's Cavern lies", None, None),
    'Dodongos Cavern MQ Under Grave Chest':                        ("#beneath a headstone# in Dodongo's Cavern lies", None, None),

    'Jabu Jabus Belly Map Chest':                                  ("#tentacle trouble# in a deity's belly guards", "a #slimy thing# guards", None),
    'Jabu Jabus Belly Compass Chest':                              ("#bubble trouble# in a deity's belly guards", "#bubbles# guard", None),

    'Jabu Jabus Belly MQ First Room Side Chest':                   ("shooting a #mouth cow# reveals", None, None),
    'Jabu Jabus Belly MQ Map Chest':                               (["#pop rocks# hide", "an #explosive palate# holds"], "a #boulder before cows# hides", None),
    'Jabu Jabus Belly MQ Second Room Lower Chest':                 ("near a #spiked elevator# lies", None, None),
    'Jabu Jabus Belly MQ Compass Chest':                           ("a #drowning cow# unveils", None, None),
    'Jabu Jabus Belly MQ Second Room Upper Chest':                 ("#moving anatomy# creates a path to", None, None),
    'Jabu Jabus Belly MQ Basement Near Switches Chest':            ("a #pair of digested cows# hold", None, None),
    'Jabu Jabus Belly MQ Basement Near Vines Chest':               ("a #pair of digested cows# hold", None, None),
    'Jabu Jabus Belly MQ Near Boss Chest':                         ("the #final cows' reward# in a deity's belly is", None, None),
    'Jabu Jabus Belly MQ Falling Like Like Room Chest':            ("#cows protected by falling monsters# in a deity's belly guard", None, None),
    'Jabu Jabus Belly MQ Boomerang Room Small Chest':              ("a school of #stingers swallowed by a deity# guard", "a school of #stingers swallowed by Jabu Jabu# guard", None),
    'Jabu Jabus Belly MQ Boomerang Chest':                         ("a school of #stingers swallowed by a deity# guard", "a school of #stingers swallowed by Jabu Jabu# guard", None),

    'Forest Temple First Room Chest':                              ("a #tree in the Forest Temple# supports", None, None),
    'Forest Temple First Stalfos Chest':                           ("#defeating enemies beneath a falling ceiling# in Forest Temple yields", None, None),
    'Forest Temple Well Chest':                                    ("a #sunken chest deep in the woods# contains", None, None),
    'Forest Temple Map Chest':                                     ("a #fiery skull# in Forest Temple guards", None, None),
    'Forest Temple Raised Island Courtyard Chest':                 ("a #chest on a small island# in the Forest Temple holds", None, None),
    'Forest Temple Falling Ceiling Room Chest':                    ("beneath a #checkerboard falling ceiling# lies", None, None),
    'Forest Temple Eye Switch Chest':                              ("a #sharp eye# will spot", "#blocks of stone# in the Forest Temple surround", None),
    'Forest Temple Floormaster Chest':                             ("deep in the forest #shadows guard a chest# containing", None, None),
    'Forest Temple Bow Chest':                                     ("an #army of the dead# guards", "#Stalfos deep in the Forest Temple# guard", None),
    'Forest Temple Red Poe Chest':                                 ("#Joelle# guards", "a #red ghost# guards", None),
    'Forest Temple Blue Poe Chest':                                ("#Beth# guards", "a #blue ghost# guards", None),
    'Forest Temple Basement Chest':                                ("#revolving walls# in the Forest Temple conceal", None, None),
    'Forest Temple Boss Key Chest':                                ("a #turned trunk# contains", "a #sideways chest in the Forest Temple# hides", None),

    'Forest Temple MQ Boss Key Chest':                             ("a #turned trunk# contains", "a #sideways chest in the Forest Temple# hides", None),
    'Forest Temple MQ First Room Chest':                           ("a #tree in the Forest Temple# supports", None, None),
    'Forest Temple MQ Wolfos Chest':                               ("#defeating enemies beneath a falling ceiling# in Forest Temple yields", None, None),
    'Forest Temple MQ Bow Chest':                                  ("an #army of the dead# guards", "#Stalfos deep in the Forest Temple# guard", None),
    'Forest Temple MQ Raised Island Courtyard Lower Chest':        ("a #chest on a small island# in the Forest Temple holds", None, None),
    'Forest Temple MQ Raised Island Courtyard Upper Chest':        ("#high in a courtyard# within the Forest Temple is", None, None),
    'Forest Temple MQ Well Chest':                                 ("a #sunken chest deep in the woods# contains", None, None),
    'Forest Temple MQ Map Chest':                                  ("#Joelle# guards", "a #red ghost# guards", None),
    'Forest Temple MQ Compass Chest':                              ("#Beth# guards", "a #blue ghost# guards", None),
    'Forest Temple MQ Falling Ceiling Room Chest':                 ("beneath a #checkerboard falling ceiling# lies", None, None),
    'Forest Temple MQ Basement Chest':                             ("#revolving walls# in the Forest Temple conceal", None, None),
    'Forest Temple MQ Redead Chest':                               ("deep in the forest #undead guard a chest# containing", None, None),

    'Fire Temple Near Boss Chest':                                 ("#near a dragon# is", None, None),
    'Fire Temple Flare Dancer Chest':                              ("the #Flare Dancer behind a totem# guards", None, None),
    'Fire Temple Boss Key Chest':                                  ("a #prison beyond a totem# holds", None, None),
    'Fire Temple Big Lava Room Blocked Door Chest':                ("#explosives over a lava pit# unveil", None, None),
    'Fire Temple Big Lava Room Lower Open Door Chest':             ("a #Goron trapped near lava# holds", None, None),
    'Fire Temple Boulder Maze Lower Chest':                        ("a #Goron at the end of a maze# holds", None, None),
    'Fire Temple Boulder Maze Upper Chest':                        ("a #Goron above a maze# holds", None, None),
    'Fire Temple Boulder Maze Side Room Chest':                    ("a #Goron hidden near a maze# holds", None, None),
    'Fire Temple Boulder Maze Shortcut Chest':                     ("a #blocked path# in Fire Temple holds", None, None),
    'Fire Temple Map Chest':                                       ("a #caged chest# in the Fire Temple hoards", None, None),
    'Fire Temple Compass Chest':                                   ("a #chest in a fiery maze# contains", None, None),
    'Fire Temple Highest Goron Chest':                             ("a #Goron atop the Fire Temple# holds", None, None),

    'Fire Temple MQ Near Boss Chest':                              ("#near a dragon# is", None, None),
    'Fire Temple MQ Megaton Hammer Chest':                         ("the #Flare Dancer in the depths of a volcano# guards", "the #Flare Dancer in the depths of the Fire Temple# guards", None),
    'Fire Temple MQ Compass Chest':                                ("a #blocked path# in Fire Temple holds", None, None),
    'Fire Temple MQ Lizalfos Maze Lower Chest':                    ("#crates in a maze# contain", None, None),
    'Fire Temple MQ Lizalfos Maze Upper Chest':                    ("#crates in a maze# contain", None, None),
    'Fire Temple MQ Map Room Side Chest':                          ("a #falling slug# in the Fire Temple guards", None, None),
    'Fire Temple MQ Map Chest':                                    ("using a #hammer in the depths of the Fire Temple# reveals", None, None),
    'Fire Temple MQ Boss Key Chest':                               ("#illuminating a lava pit# reveals the path to", None, None),
    'Fire Temple MQ Big Lava Room Blocked Door Chest':             ("#explosives over a lava pit# unveil", None, None),
    'Fire Temple MQ Lizalfos Maze Side Room Chest':                ("a #Goron hidden near a maze# holds", None, None),
    'Fire Temple MQ Freestanding Key':                             ("hidden #beneath a block of stone# lies", None, None),

    'Water Temple Map Chest':                                      ("#rolling spikes# in the Water Temple surround", None, None),
    'Water Temple Compass Chest':                                  ("#roaming stingers in the Water Temple# guard", None, None),
    'Water Temple Torches Chest':                                  ("#fire in the Water Temple# reveals", None, None),
    'Water Temple Dragon Chest':                                   ("a #serpent's prize# in the Water Temple is", None, None),
    'Water Temple Central Bow Target Chest':                       ("#blinding an eye# in the Water Temple leads to", None, None),
    'Water Temple Cracked Wall Chest':                             ("#through a crack# in the Water Temple is", None, None),
    'Water Temple Longshot Chest':                                 (["#facing yourself# reveals", "a #dark reflection# of yourself guards"], "#Dark Link# guards", None),

    'Water Temple MQ Boss Key Chest':                              ("fire in the Water Temple unlocks a #vast gate# revealing a chest with", None, None),
    'Water Temple MQ Longshot Chest':                              ("#through a crack# in the Water Temple is", None, None),
    'Water Temple MQ Compass Chest':                               ("#fire in the Water Temple# reveals", None, None),
    'Water Temple MQ Map Chest':                                   ("#sparring soldiers# in the Water Temple guard", None, None),

    'Spirit Temple Child Bridge Chest':                            ("a child conquers a #skull in green fire# in the Spirit Temple to reach", None, None),
    'Spirit Temple Child Early Torches Chest':                     ("a child can find a #caged chest# in the Spirit Temple with", None, None),
    'Spirit Temple Compass Chest':                                 ("#across a pit of sand# in the Spirit Temple lies", None, None),
    'Spirit Temple Early Adult Right Chest':                       ("#dodging boulders to collect silver rupees# in the Spirit Temple yields", None, None),
    'Spirit Temple First Mirror Left Chest':                       ("a #shadow circling reflected light# in the Spirit Temple guards", None, None),
    'Spirit Temple First Mirror Right Chest':                      ("a #shadow circling reflected light# in the Spirit Temple guards", None, None),
    'Spirit Temple Map Chest':                                     ("#before a giant statue# in the Spirit Temple lies", None, None),
    'Spirit Temple Child Climb North Chest':                       ("#lizards in the Spirit Temple# guard", None, None),
    'Spirit Temple Child Climb East Chest':                        ("#lizards in the Spirit Temple# guard", None, None),
    'Spirit Temple Sun Block Room Chest':                          ("#torchlight among Beamos# in the Spirit Temple reveals", None, None),
    'Spirit Temple Statue Room Hand Chest':                        ("a #statue in the Spirit Temple# holds", None, None),
    'Spirit Temple Statue Room Northeast Chest':                   ("on a #ledge by a statue# in the Spirit Temple rests", None, None),
    'Spirit Temple Near Four Armos Chest':                         ("those who #show the light among statues# in the Spirit Temple find", None, None),
    'Spirit Temple Hallway Right Invisible Chest':                 ("the #Eye of Truth in the Spirit Temple# reveals", None, None),
    'Spirit Temple Hallway Left Invisible Chest':                  ("the #Eye of Truth in the Spirit Temple# reveals", None, None),
    'Spirit Temple Boss Key Chest':                                ("a #chest engulfed in flame# in the Spirit Temple holds", None, None),
    'Spirit Temple Topmost Chest':                                 ("those who #show the light above the Colossus# find", None, None),

    'Spirit Temple MQ Entrance Front Left Chest':                  ("#lying unguarded# in the Spirit Temple is", None, None),
    'Spirit Temple MQ Entrance Back Right Chest':                  ("a #switch in a pillar# within the Spirit Temple drops", None, None),
    'Spirit Temple MQ Entrance Front Right Chest':                 ("#collecting rupees through a water jet# reveals", None, None),
    'Spirit Temple MQ Entrance Back Left Chest':                   ("an #eye blinded by stone# within the Spirit Temple conceals", None, None),
    'Spirit Temple MQ Map Chest':                                  ("surrounded by #fire and wrappings# lies", None, None),
    'Spirit Temple MQ Map Room Enemy Chest':                       ("a child defeats a #gauntlet of monsters# within the Spirit Temple to find", None, None),
    'Spirit Temple MQ Child Climb North Chest':                    ("#explosive sunlight# within the Spirit Temple uncovers", None, None),
    'Spirit Temple MQ Child Climb South Chest':                    ("#trapped by falling enemies# within the Spirit Temple is", None, None),
    'Spirit Temple MQ Compass Chest':                              ("#blinding the colossus# unveils", None, None),
    'Spirit Temple MQ Statue Room Lullaby Chest':                  ("a #royal melody awakens the colossus# to reveal", None, None),
    'Spirit Temple MQ Statue Room Invisible Chest':                ("the #Eye of Truth# finds the colossus's hidden", None, None),
    'Spirit Temple MQ Silver Block Hallway Chest':                 ("#the old hide what the young find# to reveal", None, None),
    'Spirit Temple MQ Sun Block Room Chest':                       ("#sunlight in a maze of fire# hides", None, None),
    'Spirit Temple MQ Leever Room Chest':                          ("#across a pit of sand# in the Spirit Temple lies", None, None),
    'Spirit Temple MQ Beamos Room Chest':                          ("where #temporal stone blocks the path# within the Spirit Temple lies", None, None),
    'Spirit Temple MQ Chest Switch Chest':                         ("a #chest of double purpose# holds", None, None),
    'Spirit Temple MQ Boss Key Chest':                             ("a #temporal stone blocks the light# leading to", None, None),
    'Spirit Temple MQ Mirror Puzzle Invisible Chest':              ("those who #show the light above the Colossus# find", None, None),

    'Shadow Temple Map Chest':                                     ("the #Eye of Truth# pierces a hall of faces to reveal", None, None),
    'Shadow Temple Hover Boots Chest':                             ("a #nether dweller in the Shadow Temple# holds", "#Dead Hand in the Shadow Temple# holds", None),
    'Shadow Temple Compass Chest':                                 ("#mummies revealed by the Eye of Truth# guard", None, None),
    'Shadow Temple Early Silver Rupee Chest':                      ("#spinning scythes# protect", None, None),
    'Shadow Temple Invisible Blades Visible Chest':                ("#invisible blades# guard", None, None),
    'Shadow Temple Invisible Blades Invisible Chest':              ("#invisible blades# guard", None, None),
    'Shadow Temple Falling Spikes Lower Chest':                    ("#falling spikes# block the path to", None, None),
    'Shadow Temple Falling Spikes Upper Chest':                    ("#falling spikes# block the path to", None, None),
    'Shadow Temple Falling Spikes Switch Chest':                   ("#falling spikes# block the path to", None, None),
    'Shadow Temple Invisible Spikes Chest':                        ("the #dead roam among invisible spikes# guarding", None, None),
    'Shadow Temple Wind Hint Chest':                               ("an #invisible chest guarded by the dead# holds", None, None),
    'Shadow Temple After Wind Enemy Chest':                        ("#mummies guarding a ferry# hide", None, None),
    'Shadow Temple After Wind Hidden Chest':                       ("#mummies guarding a ferry# hide", None, None),
    'Shadow Temple Spike Walls Left Chest':                        ("#walls consumed by a ball of fire# reveal", None, None),
    'Shadow Temple Invisible Floormaster Chest':                   ("the #Floormaster in the house of the dead# guards", "the #Floormaster in the Shadow Temple# guards", None),
    'Shadow Temple Boss Key Chest':                                ("#walls consumed by a ball of fire# reveal", None, None),

    'Shadow Temple MQ Compass Chest':                              ("the #Eye of Truth# pierces a hall of faces to reveal", None, None),
    'Shadow Temple MQ Hover Boots Chest':                          ("#Dead Hand in the Shadow Temple# holds", None, None),
    'Shadow Temple MQ Early Gibdos Chest':                         ("#mummies revealed by the Eye of Truth# guard", None, None),
    'Shadow Temple MQ Map Chest':                                  ("#spinning scythes# protect", None, None),
    'Shadow Temple MQ Beamos Silver Rupees Chest':                 ("#collecting rupees in a vast cavern# with the Shadow Temple unveils", None, None),
    'Shadow Temple MQ Falling Spikes Switch Chest':                ("#falling spikes# block the path to", None, None),
    'Shadow Temple MQ Falling Spikes Lower Chest':                 ("#falling spikes# block the path to", None, None),
    'Shadow Temple MQ Falling Spikes Upper Chest':                 ("#falling spikes# block the path to", None, None),
    'Shadow Temple MQ Invisible Spikes Chest':                     ("the #dead roam among invisible spikes# guarding", None, None),
    'Shadow Temple MQ Boss Key Chest':                             ("#walls consumed by a ball of fire# reveal", None, None),
    'Shadow Temple MQ Spike Walls Left Chest':                     ("#walls consumed by a ball of fire# reveal", None, None),
    'Shadow Temple MQ Invisible Blades Invisible Chest':           ("#invisible blades# guard", None, None),
    'Shadow Temple MQ Invisible Blades Visible Chest':             ("#invisible blades# guard", None, None),
    'Shadow Temple MQ Wind Hint Chest':                            ("an #invisible chest guarded by the dead# holds", None, None),
    'Shadow Temple MQ After Wind Hidden Chest':                    ("#mummies guarding a ferry# hide", None, None),
    'Shadow Temple MQ After Wind Enemy Chest':                     ("#mummies guarding a ferry# hide", None, None),
    'Shadow Temple MQ Near Ship Invisible Chest':                  ("#caged near a ship# lies", None, None),
    'Shadow Temple MQ Freestanding Key':                           ("#behind three burning skulls# lies", None, None),

    'Bottom of the Well Front Left Fake Wall Chest':               ("the #Eye of Truth in the well# reveals", None, None),
    'Bottom of the Well Front Center Bombable Chest':              ("#gruesome debris# in the well hides", None, None),
    'Bottom of the Well Right Bottom Fake Wall Chest':             ("the #Eye of Truth in the well# reveals", None, None),
    'Bottom of the Well Compass Chest':                            ("a #hidden entrance to a cage# in the well leads to", None, None),
    'Bottom of the Well Center Skulltula Chest':                   ("a #spider guarding a cage# in the well protects", None, None),
    'Bottom of the Well Back Left Bombable Chest':                 ("#gruesome debris# in the well hides", None, None),
    'Bottom of the Well Invisible Chest':                          ("#Dead Hand's invisible secret# is", None, None),
    'Bottom of the Well Underwater Front Chest':                   ("a #royal melody in the well# uncovers", None, None),
    'Bottom of the Well Underwater Left Chest':                    ("a #royal melody in the well# uncovers", None, None),
    'Bottom of the Well Map Chest':                                ("in the #depths of the well# lies", None, None),
    'Bottom of the Well Fire Keese Chest':                         ("#perilous pits# in the well guard the path to", None, None),
    'Bottom of the Well Like Like Chest':                          ("#locked in a cage# in the well lies", None, None),
    'Bottom of the Well Freestanding Key':                         ("#inside a coffin# hides", None, None),
    'Bottom of the Well Lens of Truth Chest':                      (["the well's #grasping ghoul# hides", "a #nether dweller in the well# holds"], "#Dead Hand in the well# holds", None),

    'Bottom of the Well MQ Compass Chest':                         (["the well's #grasping ghoul# hides", "a #nether dweller in the well# holds"], "#Dead Hand in the well# holds", None),
    'Bottom of the Well MQ Map Chest':                             ("a #royal melody in the well# uncovers", None, None),
    'Bottom of the Well MQ Lens of Truth Chest':                   ("an #army of the dead# in the well guards", None, None),
    'Bottom of the Well MQ Dead Hand Freestanding Key':            ("#Dead Hand's explosive secret# is", None, None),
    'Bottom of the Well MQ East Inner Room Freestanding Key':      ("an #invisible path in the well# leads to", None, None),

    'Ice Cavern Map Chest':                                        ("#winds of ice# surround", "a chest #atop a pillar of ice# contains", None),
    'Ice Cavern Compass Chest':                                    ("a #wall of ice# protects", None, None),
    'Ice Cavern Freestanding PoH':                                 ("a #wall of ice# protects", None, None),

    'Ice Cavern MQ Compass Chest':                                 ("#winds of ice# surround", None, None),
    'Ice Cavern MQ Map Chest':                                     ("a #wall of ice# protects", None, None),
    'Ice Cavern MQ Freestanding PoH':                              ("#winds of ice# surround", None, None),

    'Gerudo Training Ground Lobby Left Chest':                     ("a #blinded eye in the Gerudo Training Ground# drops", None, None),
    'Gerudo Training Ground Lobby Right Chest':                    ("a #blinded eye in the Gerudo Training Ground# drops", None, None),
    'Gerudo Training Ground Stalfos Chest':                        ("#soldiers walking on shifting sands# in the Gerudo Training Ground guard", None, None),
    'Gerudo Training Ground Beamos Chest':                         ("#reptilian warriors# in the Gerudo Training Ground protect", None, None),
    'Gerudo Training Ground Hidden Ceiling Chest':                 ("the #Eye of Truth# in the Gerudo Training Ground reveals", None, None),
    'Gerudo Training Ground Maze Path First Chest':                ("the first prize of #the thieves' training# is", None, None),
    'Gerudo Training Ground Maze Path Second Chest':               ("the second prize of #the thieves' training# is", None, None),
    'Gerudo Training Ground Maze Path Third Chest':                ("the third prize of #the thieves' training# is", None, None),
    'Gerudo Training Ground Maze Right Central Chest':             ("the #Song of Time# in the Gerudo Training Ground leads to", None, None),
    'Gerudo Training Ground Maze Right Side Chest':                ("the #Song of Time# in the Gerudo Training Ground leads to", None, None),
    'Gerudo Training Ground Hammer Room Clear Chest':              ("#fiery foes# in the Gerudo Training Ground guard", None, None),
    'Gerudo Training Ground Hammer Room Switch Chest':             ("#engulfed in flame# where thieves train lies", None, None),
    'Gerudo Training Ground Eye Statue Chest':                     ("thieves #blind four faces# to find", None, None),
    'Gerudo Training Ground Near Scarecrow Chest':                 ("thieves #blind four faces# to find", None, None),
    'Gerudo Training Ground Before Heavy Block Chest':             ("#before a block of silver# thieves can find", None, None),
    'Gerudo Training Ground Heavy Block First Chest':              ("a #feat of strength# rewards thieves with", None, None),
    'Gerudo Training Ground Heavy Block Second Chest':             ("a #feat of strength# rewards thieves with", None, None),
    'Gerudo Training Ground Heavy Block Third Chest':              ("a #feat of strength# rewards thieves with", None, None),
    'Gerudo Training Ground Heavy Block Fourth Chest':             ("a #feat of strength# rewards thieves with", None, None),
    'Gerudo Training Ground Freestanding Key':                     ("the #Song of Time# in the Gerudo Training Ground leads to", None, None),

    'Gerudo Training Ground MQ Lobby Right Chest':                 ("#thieves prepare for training# with", None, None),
    'Gerudo Training Ground MQ Lobby Left Chest':                  ("#thieves prepare for training# with", None, None),
    'Gerudo Training Ground MQ First Iron Knuckle Chest':          ("#soldiers walking on shifting sands# in the Gerudo Training Ground guard", None, None),
    'Gerudo Training Ground MQ Before Heavy Block Chest':          ("#before a block of silver# thieves can find", None, None),
    'Gerudo Training Ground MQ Eye Statue Chest':                  ("thieves #blind four faces# to find", None, None),
    'Gerudo Training Ground MQ Flame Circle Chest':                ("#engulfed in flame# where thieves train lies", None, None),
    'Gerudo Training Ground MQ Second Iron Knuckle Chest':         ("#fiery foes# in the Gerudo Training Ground guard", None, None),
    'Gerudo Training Ground MQ Dinolfos Chest':                    ("#reptilian warriors# in the Gerudo Training Ground protect", None, None),
    'Gerudo Training Ground MQ Maze Right Central Chest':          ("a #path of fire# leads thieves to", None, None),
    'Gerudo Training Ground MQ Maze Path First Chest':             ("the first prize of #the thieves' training# is", None, None),
    'Gerudo Training Ground MQ Maze Right Side Chest':             ("a #path of fire# leads thieves to", None, None),
    'Gerudo Training Ground MQ Maze Path Third Chest':             ("the third prize of #the thieves' training# is", None, None),
    'Gerudo Training Ground MQ Maze Path Second Chest':            ("the second prize of #the thieves' training# is", None, None),
    'Gerudo Training Ground MQ Hidden Ceiling Chest':              ("the #Eye of Truth# in the Gerudo Training Ground reveals", None, None),
    'Gerudo Training Ground MQ Heavy Block Chest':                 ("a #feat of strength# rewards thieves with", None, None),

    'Ganons Tower Boss Key Chest':                                 ("the #Evil King# hoards", None, None),

    'Ganons Castle Forest Trial Chest':                            ("the #test of the wilds# holds", None, None),
    'Ganons Castle Water Trial Left Chest':                        ("the #test of the seas# holds", None, None),
    'Ganons Castle Water Trial Right Chest':                       ("the #test of the seas# holds", None, None),
    'Ganons Castle Shadow Trial Front Chest':                      ("#music in the test of darkness# unveils", None, None),
    'Ganons Castle Spirit Trial Crystal Switch Chest':             ("the #test of the sands# holds", None, None),
    'Ganons Castle Spirit Trial Invisible Chest':                  ("the #test of the sands# holds", None, None),
    'Ganons Castle Light Trial First Left Chest':                  ("the #test of radiance# holds", None, None),
    'Ganons Castle Light Trial Second Left Chest':                 ("the #test of radiance# holds", None, None),
    'Ganons Castle Light Trial Third Left Chest':                  ("the #test of radiance# holds", None, None),
    'Ganons Castle Light Trial First Right Chest':                 ("the #test of radiance# holds", None, None),
    'Ganons Castle Light Trial Second Right Chest':                ("the #test of radiance# holds", None, None),
    'Ganons Castle Light Trial Third Right Chest':                 ("the #test of radiance# holds", None, None),
    'Ganons Castle Light Trial Invisible Enemies Chest':           ("the #test of radiance# holds", None, None),
    'Ganons Castle Light Trial Lullaby Chest':                     ("#music in the test of radiance# reveals", None, None),

    'Ganons Castle MQ Water Trial Chest':                          ("the #test of the seas# holds", None, None),
    'Ganons Castle MQ Forest Trial Eye Switch Chest':              ("the #test of the wilds# holds", None, None),
    'Ganons Castle MQ Forest Trial Frozen Eye Switch Chest':       ("the #test of the wilds# holds", None, None),
    'Ganons Castle MQ Light Trial Lullaby Chest':                  ("#music in the test of radiance# reveals", None, None),
    'Ganons Castle MQ Shadow Trial Bomb Flower Chest':             ("the #test of darkness# holds", None, None),
    'Ganons Castle MQ Spirit Trial Golden Gauntlets Chest':        ("#reflected light in the test of the sands# reveals", None, None),
    'Ganons Castle MQ Spirit Trial Sun Back Right Chest':          ("#reflected light in the test of the sands# reveals", None, None),
    'Ganons Castle MQ Spirit Trial Sun Back Left Chest':           ("#reflected light in the test of the sands# reveals", None, None),
    'Ganons Castle MQ Spirit Trial Sun Front Left Chest':          ("#reflected light in the test of the sands# reveals", None, None),
    'Ganons Castle MQ Spirit Trial First Chest':                   ("#reflected light in the test of the sands# reveals", None, None),
    'Ganons Castle MQ Spirit Trial Invisible Chest':               ("#reflected light in the test of the sands# reveals", None, None),
    'Ganons Castle MQ Forest Trial Freestanding Key':              ("the #test of the wilds# holds", None, None),

    'Deku Tree Queen Gohma Heart':                                 ("the #Parasitic Armored Arachnid# holds", "#Queen Gohma# holds", None),
    'Dodongos Cavern King Dodongo Heart':                          ("the #Infernal Dinosaur# holds", "#King Dodongo# holds", None),
    'Jabu Jabus Belly Barinade Heart':                             ("the #Bio-Electric Anemone# holds", "#Barinade# holds", None),
    'Forest Temple Phantom Ganon Heart':                           ("the #Evil Spirit from Beyond# holds", "#Phantom Ganon# holds", None),
    'Fire Temple Volvagia Heart':                                  ("the #Subterranean Lava Dragon# holds", "#Volvagia# holds", None),
    'Water Temple Morpha Heart':                                   ("the #Giant Aquatic Amoeba# holds", "#Morpha# holds", None),
    'Shadow Temple Bongo Bongo Heart':                             ("the #Phantom Shadow Beast# holds", "#Bongo Bongo# holds", None),
    'Spirit Temple Twinrova Heart':                                ("the #Sorceress Sisters# hold", "#Twinrova# holds", None),

    'Queen Gohma':                                                 ("the #Parasitic Armored Arachnid# holds", "#Queen Gohma# holds", None),
    'King Dodongo':                                                ("the #Infernal Dinosaur# holds", "#King Dodongo# holds", None),
    'Barinade':                                                    ("the #Bio-Electric Anemone# holds", "#Barinade# holds", None),
    'Phantom Ganon':                                               ("the #Evil Spirit from Beyond# holds", "#Phantom Ganon# holds", None),
    'Volvagia':                                                    ("the #Subterranean Lava Dragon# holds", "#Volvagia# holds", None),
    'Morpha':                                                      ("the #Giant Aquatic Amoeba# holds", "#Morpha# holds", None),
    'Bongo Bongo':                                                 ("the #Phantom Shadow Beast# holds", "#Bongo Bongo# holds", None),
    'Twinrova':                                                    ("the #Sorceress Sisters# hold", "#Twinrova# holds", None),
    'ToT Reward from Rauru':                                       ("#coming of age# grants", "beyond the #Door of Time# waits", None),

    'Deku Tree GS Basement Back Room':                             ("a #spider deep within the Deku Tree# hides", None, None),
    'Deku Tree GS Basement Gate':                                  ("a #web protects a spider# within the Deku Tree holding", None, None),
    'Deku Tree GS Basement Vines':                                 ("a #web protects a spider# within the Deku Tree holding", None, None),
    'Deku Tree GS Compass Room':                                   ("a #spider atop the Deku Tree# holds", None, None),

    'Deku Tree MQ GS Lobby':                                       ("a #spider in a crate# within the Deku Tree hides", None, None),
    'Deku Tree MQ GS Compass Room':                                ("a #wall of rock protects a spider# within the Deku Tree holding", None, None),
    'Deku Tree MQ GS Basement Back Room':                          ("a #spider deep within the Deku Tree# hides", None, None),

    'Dodongos Cavern GS Vines Above Stairs':                       ("a #spider entangled in vines# in Dodongo's Cavern guards", None, None),
    'Dodongos Cavern GS Scarecrow':                                ("a #spider among explosive slugs# hides", None, None),
    'Dodongos Cavern GS Alcove Above Stairs':                      ("a #spider just out of reach# in Dodongo's Cavern holds", None, None),
    'Dodongos Cavern GS Back Room':                                ("a #spider behind a statue# in Dodongo's Cavern holds", None, None),
    'Dodongos Cavern GS Side Room Near Lower Lizalfos':            ("a #spider among bats# in Dodongo's Cavern holds", None, None),

    'Dodongos Cavern MQ GS Scrub Room':                            ("a #spider high on a wall# in Dodongo's Cavern holds", None, None),
    'Dodongos Cavern MQ GS Lizalfos Room':                         ("a #spider on top of a pillar of rock# in Dodongo's Cavern holds", None, None),
    'Dodongos Cavern MQ GS Larvae Room':                           ("a #spider in a crate# in Dodongo's Cavern holds", None, None),
    'Dodongos Cavern MQ GS Back Area':                             ("a #spider among graves# in Dodongo's Cavern holds", None, None),

    'Jabu Jabus Belly GS Lobby Basement Lower':                    ("a #spider resting near a princess# in Jabu Jabu's Belly holds", None, None),
    'Jabu Jabus Belly GS Lobby Basement Upper':                    ("a #spider resting near a princess# in Jabu Jabu's Belly holds", None, None),
    'Jabu Jabus Belly GS Near Boss':                               ("#jellyfish surround a spider# holding", None, None),
    'Jabu Jabus Belly GS Water Switch Room':                       ("a #spider guarded by a school of stingers# in Jabu Jabu's Belly holds", None, None),

    'Jabu Jabus Belly MQ GS Tailpasaran Room':                     ("a #spider surrounded by electricity# in Jabu Jabu's Belly holds", None, None),
    'Jabu Jabus Belly MQ GS Boomerang Chest Room':                 ("a #spider guarded by a school of stingers# in Jabu Jabu's Belly holds", None, None),
    'Jabu Jabus Belly MQ GS Near Boss':                            ("a #spider in a web within Jabu Jabu's Belly# holds", None, None),

    'Forest Temple GS Raised Island Courtyard':                    ("a #spider on a small island# in the Forest Temple holds", None, None),
    'Forest Temple GS First Room':                                 ("a #spider high on a wall of vines# in the Forest Temple holds", None, None),
    'Forest Temple GS Level Island Courtyard':                     ("#stone columns# lead to a spider in the Forest Temple hiding", None, None),
    'Forest Temple GS Lobby':                                      ("a #spider among ghosts# in the Forest Temple guards", None, None),
    'Forest Temple GS Basement':                                   ("a #spider within revolving walls# in the Forest Temple holds", None, None),

    'Forest Temple MQ GS First Hallway':                           ("an #ivy-hidden spider# in the Forest Temple hoards", None, None),
    'Forest Temple MQ GS Block Push Room':                         ("a #spider in a hidden nook# within the Forest Temple holds", None, None),
    'Forest Temple MQ GS Raised Island Courtyard':                 ("a #spider on an arch# in the Forest Temple holds", None, None),
    'Forest Temple MQ GS Level Island Courtyard':                  ("a #spider on a ledge# in the Forest Temple holds", None, None),
    'Forest Temple MQ GS Well':                                    ("#draining a well# in Forest Temple uncovers a spider with", None, None),

    'Fire Temple GS Song of Time Room':                            ("#eight tiles of malice# guard a spider holding", None, None),
    'Fire Temple GS Boss Key Loop':                                ("#five tiles of malice# guard a spider holding", None, None),
    'Fire Temple GS Boulder Maze':                                 ("#explosives in a maze# unveil a spider hiding", None, None),
    'Fire Temple GS Scarecrow Top':                                ("a #spider-friendly scarecrow# atop a volcano hides", "a #spider-friendly scarecrow# atop the Fire Temple hides", None),
    'Fire Temple GS Scarecrow Climb':                              ("a #spider-friendly scarecrow# atop a volcano hides", "a #spider-friendly scarecrow# atop the Fire Temple hides", None),

    'Fire Temple MQ GS Above Flame Maze':                          ("a #spider above a fiery maze# holds", None, None),
    'Fire Temple MQ GS Flame Maze Center':                         ("a #spider within a fiery maze# holds", None, None),
    'Fire Temple MQ GS Big Lava Room Open Door':                   ("a #Goron trapped near lava# befriended a spider with", None, None),
    'Fire Temple MQ GS Flame Maze Side Room':                      ("a #spider beside a fiery maze# holds", None, None),

    'Water Temple GS Falling Platform Room':                       ("a #spider over a waterfall# in the Water Temple holds", None, None),
    'Water Temple GS Central Pillar':                              ("a #spider in the center of the Water Temple# holds", None, None),
    'Water Temple GS Near Boss Key Chest':                         ("a spider protected by #rolling boulders under the lake# hides", "a spider protected by #rolling boulders in the Water Temple# hides", None),
    'Water Temple GS River':                                       ("a #spider over a river# in the Water Temple holds", None, None),

    'Water Temple MQ GS Before Upper Water Switch':                ("#beyond a pit of lizards# is a spider holding", None, None),
    'Water Temple MQ GS Lizalfos Hallway':                         ("#lizards guard a spider# in the Water Temple with", None, None),
    'Water Temple MQ GS River':                                    ("a #spider over a river# in the Water Temple holds", None, None),

    'Spirit Temple GS Hall After Sun Block Room':                  ("a spider in the #hall of a knight# guards", None, None),
    'Spirit Temple GS Boulder Room':                               ("a #spider behind a temporal stone# in the Spirit Temple yields", None, None),
    'Spirit Temple GS Lobby':                                      ("a #spider beside a statue# holds", None, None),
    'Spirit Temple GS Sun on Floor Room':                          ("a #spider at the top of a deep shaft# in the Spirit Temple holds", None, None),
    'Spirit Temple GS Metal Fence':                                ("a child defeats a #spider among bats# in the Spirit Temple to gain", None, None),

    'Spirit Temple MQ GS Leever Room':                             ("#above a pit of sand# in the Spirit Temple hides", None, None),
    'Spirit Temple MQ GS Nine Thrones Room West':                  ("a spider in the #hall of a knight# guards", None, None),
    'Spirit Temple MQ GS Nine Thrones Room North':                 ("a spider in the #hall of a knight# guards", None, None),
    'Spirit Temple MQ GS Sun Block Room':                          ("#upon a web of glass# in the Spirit Temple sits a spider holding", None, None),

    'Shadow Temple GS Single Giant Pot':                           ("#beyond a burning skull# lies a spider with", None, None),
    'Shadow Temple GS Falling Spikes Room':                        ("a #spider beyond falling spikes# holds", None, None),
    'Shadow Temple GS Triple Giant Pot':                           ("#beyond three burning skulls# lies a spider with", None, None),
    'Shadow Temple GS Invisible Blades Room':                      ("a spider guarded by #invisible blades# holds", None, None),
    'Shadow Temple GS Near Ship':                                  ("a spider near a #docked ship# hoards", None, None),

    'Shadow Temple MQ GS Falling Spikes Room':                     ("a #spider beyond falling spikes# holds", None, None),
    'Shadow Temple MQ GS Wind Hint Room':                          ("a #spider amidst roaring winds# in the Shadow Temple holds", None, None),
    'Shadow Temple MQ GS After Wind':                              ("a #spider beneath gruesome debris# in the Shadow Temple hides", None, None),
    'Shadow Temple MQ GS After Ship':                              ("a #fallen statue# reveals a spider with", None, None),
    'Shadow Temple MQ GS Near Boss':                               ("a #suspended spider# guards", None, None),

    'Bottom of the Well GS Like Like Cage':                        ("a #spider locked in a cage# in the well holds", None, None),
    'Bottom of the Well GS East Inner Room':                       ("an #invisible path in the well# leads to", None, None),
    'Bottom of the Well GS West Inner Room':                       ("a #spider locked in a crypt# within the well guards", None, None),

    'Bottom of the Well MQ GS Basement':                           ("a #gauntlet of invisible spiders# protects", None, None),
    'Bottom of the Well MQ GS Coffin Room':                        ("a #spider crawling near the dead# in the well holds", None, None),
    'Bottom of the Well MQ GS West Inner Room':                    ("a #spider locked in a crypt# within the well guards", None, None),

    'Ice Cavern GS Push Block Room':                               ("a #spider above icy pits# holds", None, None),
    'Ice Cavern GS Spinning Scythe Room':                          ("#spinning ice# guards a spider holding", None, None),
    'Ice Cavern GS Heart Piece Room':                              ("a #spider behind a wall of ice# hides", None, None),

    'Ice Cavern MQ GS Scarecrow':                                  ("a #spider above icy pits# holds", None, None),
    'Ice Cavern MQ GS Ice Block':                                  ("a #web of ice# surrounds a spider with", None, None),
    'Ice Cavern MQ GS Red Ice':                                    ("a #spider in fiery ice# hoards", None, None),

    'HF GS Near Kak Grotto':                                       ("a #spider-guarded spider in a hole# hoards", None, None),

    'LLR GS Back Wall':                                            ("night reveals a #spider in a ranch# holding", None, None),
    'LLR GS Rain Shed':                                            ("night reveals a #spider in a ranch# holding", None, None),
    'LLR GS House Window':                                         ("night reveals a #spider in a ranch# holding", None, None),
    'LLR GS Tree':                                                 ("a spider hiding in a #ranch tree# holds", None, None),

    'KF GS Bean Patch':                                            ("a #spider buried in a forest# holds", None, None),
    'KF GS Know It All House':                                     ("night in the past reveals a #spider in a forest# holding", None, None),
    'KF GS House of Twins':                                        ("night in the future reveals a #spider in a forest# holding", None, None),

    'LW GS Bean Patch Near Bridge':                                ("a #spider buried deep in a forest maze# holds", None, None),
    'LW GS Bean Patch Near Theater':                               ("a #spider buried deep in a forest maze# holds", None, None),
    'LW GS Above Theater':                                         ("night reveals a #spider deep in a forest maze# holding", None, None),
    'SFM GS':                                                      ("night reveals a #spider in a forest meadow# holding", None, None),

    'OGC GS':                                                      ("a #spider outside a tyrant's tower# holds", None, None),
    'HC GS Tree':                                                  ("a spider hiding in a #tree outside of a castle# holds", None, None),
    'Market GS Guard House':                                       ("a #spider in a guarded crate# holds", None, None),

    'DMC GS Bean Patch':                                           ("a #spider buried in a volcano# holds", None, None),

    'DMT GS Bean Patch':                                           ("a #spider buried outside a cavern# holds", None, None),
    'DMT GS Near Kak':                                             ("a #spider hidden in a mountain nook# holds", None, None),
    'DMT GS Above Dodongos Cavern':                                ("the hammer reveals a #spider on a mountain# holding", None, None),
    'DMT GS Falling Rocks Path':                                   ("the hammer reveals a #spider on a mountain# holding", None, None),

    'GC GS Center Platform':                                       ("a #suspended spider# in Goron City holds", None, None),
    'GC GS Boulder Maze':                                          ("a spider in a #Goron City crate# holds", None, None),

    'Kak GS House Under Construction':                             ("night in the past reveals a #spider in a town# holding", None, None),
    'Kak GS Skulltula House':                                      ("night in the past reveals a #spider in a town# holding", None, None),
    'Kak GS Near Gate Guard':                                      ("night in the past reveals a #spider in a town# holding", None, None),
    'Kak GS Tree':                                                 ("night in the past reveals a #spider in a town# holding", None, None),
    'Kak GS Watchtower':                                           ("night in the past reveals a #spider in a town# holding", None, None),
    'Kak GS Above Impas House':                                    ("night in the future reveals a #spider in a town# holding", None, None),

    'Graveyard GS Wall':                                           ("night reveals a #spider in a graveyard# holding", None, None),
    'Graveyard GS Bean Patch':                                     ("a #spider buried in a graveyard# holds", None, None),

    'ZR GS Ladder':                                                ("night in the past reveals a #spider in a river# holding", None, None),
    'ZR GS Tree':                                                  ("a spider hiding in a #tree by a river# holds", None, None),
    'ZR GS Above Bridge':                                          ("night in the future reveals a #spider in a river# holding", None, None),
    'ZR GS Near Raised Grottos':                                   ("night in the future reveals a #spider in a river# holding", None, None),

    'ZD GS Frozen Waterfall':                                      ("night reveals a #spider by a frozen waterfall# holding", None, None),
    'ZF GS Above the Log':                                         ("night reveals a #spider near a deity# holding", None, None),
    'ZF GS Tree':                                                  ("a spider hiding in a #tree near a deity# holds", None, None),

    'LH GS Bean Patch':                                            ("a #spider buried by a lake# holds", None, None),
    'LH GS Small Island':                                          ("night reveals a #spider by a lake# holding", None, None),
    'LH GS Lab Wall':                                              ("night reveals a #spider by a lake# holding", None, None),
    'LH GS Lab Crate':                                             ("a spider deed underwater in a #lab crate# holds", None, None),
    'LH GS Tree':                                                  ("night reveals a #spider by a lake high in a tree# holding", None, None),

    'GV GS Bean Patch':                                            ("a #spider buried in a valley# holds", None, None),
    'GV GS Small Bridge':                                          ("night in the past reveals a #spider in a valley# holding", None, None),
    'GV GS Pillar':                                                ("night in the future reveals a #spider in a valley# holding", None, None),
    'GV GS Behind Tent':                                           ("night in the future reveals a #spider in a valley# holding", None, None),

    'GF GS Archery Range':                                         ("night reveals a #spider in a fortress# holding", None, None),
    'GF GS Top Floor':                                             ("night reveals a #spider in a fortress# holding", None, None),

    'Colossus GS Bean Patch':                                      ("a #spider buried in the desert# holds", None, None),
    'Colossus GS Hill':                                            ("night reveals a #spider deep in the desert# holding", None, None),
    'Colossus GS Tree':                                            ("night reveals a #spider deep in the desert# holding", None, None),

    'KF Shop Item 1':                                              ("a #child shopkeeper# sells", None, None),
    'KF Shop Item 2':                                              ("a #child shopkeeper# sells", None, None),
    'KF Shop Item 3':                                              ("a #child shopkeeper# sells", None, None),
    'KF Shop Item 4':                                              ("a #child shopkeeper# sells", None, None),
    'KF Shop Item 5':                                              ("a #child shopkeeper# sells", None, None),
    'KF Shop Item 6':                                              ("a #child shopkeeper# sells", None, None),
    'KF Shop Item 7':                                              ("a #child shopkeeper# sells", None, None),
    'KF Shop Item 8':                                              ("a #child shopkeeper# sells", None, None),

    'Kak Potion Shop Item 1':                                      ("a #potion seller# offers", "the #Kakariko Potion Shop# offers", None),
    'Kak Potion Shop Item 2':                                      ("a #potion seller# offers", "the #Kakariko Potion Shop# offers", None),
    'Kak Potion Shop Item 3':                                      ("a #potion seller# offers", "the #Kakariko Potion Shop# offers", None),
    'Kak Potion Shop Item 4':                                      ("a #potion seller# offers", "the #Kakariko Potion Shop# offers", None),
    'Kak Potion Shop Item 5':                                      ("a #potion seller# offers", "the #Kakariko Potion Shop# offers", None),
    'Kak Potion Shop Item 6':                                      ("a #potion seller# offers", "the #Kakariko Potion Shop# offers", None),
    'Kak Potion Shop Item 7':                                      ("a #potion seller# offers", "the #Kakariko Potion Shop# offers", None),
    'Kak Potion Shop Item 8':                                      ("a #potion seller# offers", "the #Kakariko Potion Shop# offers", None),

    'Market Bombchu Shop Item 1':                                  ("a #Bombchu merchant# sells", None, None),
    'Market Bombchu Shop Item 2':                                  ("a #Bombchu merchant# sells", None, None),
    'Market Bombchu Shop Item 3':                                  ("a #Bombchu merchant# sells", None, None),
    'Market Bombchu Shop Item 4':                                  ("a #Bombchu merchant# sells", None, None),
    'Market Bombchu Shop Item 5':                                  ("a #Bombchu merchant# sells", None, None),
    'Market Bombchu Shop Item 6':                                  ("a #Bombchu merchant# sells", None, None),
    'Market Bombchu Shop Item 7':                                  ("a #Bombchu merchant# sells", None, None),
    'Market Bombchu Shop Item 8':                                  ("a #Bombchu merchant# sells", None, None),

    'Market Potion Shop Item 1':                                   ("a #potion seller# offers", "the #Market Potion Shop# offers", None),
    'Market Potion Shop Item 2':                                   ("a #potion seller# offers", "the #Market Potion Shop# offers", None),
    'Market Potion Shop Item 3':                                   ("a #potion seller# offers", "the #Market Potion Shop# offers", None),
    'Market Potion Shop Item 4':                                   ("a #potion seller# offers", "the #Market Potion Shop# offers", None),
    'Market Potion Shop Item 5':                                   ("a #potion seller# offers", "the #Market Potion Shop# offers", None),
    'Market Potion Shop Item 6':                                   ("a #potion seller# offers", "the #Market Potion Shop# offers", None),
    'Market Potion Shop Item 7':                                   ("a #potion seller# offers", "the #Market Potion Shop# offers", None),
    'Market Potion Shop Item 8':                                   ("a #potion seller# offers", "the #Market Potion Shop# offers", None),

    'Market Bazaar Item 1':                                        ("the #Market Bazaar# offers", None, None),
    'Market Bazaar Item 2':                                        ("the #Market Bazaar# offers", None, None),
    'Market Bazaar Item 3':                                        ("the #Market Bazaar# offers", None, None),
    'Market Bazaar Item 4':                                        ("the #Market Bazaar# offers", None, None),
    'Market Bazaar Item 5':                                        ("the #Market Bazaar# offers", None, None),
    'Market Bazaar Item 6':                                        ("the #Market Bazaar# offers", None, None),
    'Market Bazaar Item 7':                                        ("the #Market Bazaar# offers", None, None),
    'Market Bazaar Item 8':                                        ("the #Market Bazaar# offers", None, None),

    'Kak Bazaar Item 1':                                           ("the #Kakariko Bazaar# offers", None, None),
    'Kak Bazaar Item 2':                                           ("the #Kakariko Bazaar# offers", None, None),
    'Kak Bazaar Item 3':                                           ("the #Kakariko Bazaar# offers", None, None),
    'Kak Bazaar Item 4':                                           ("the #Kakariko Bazaar# offers", None, None),
    'Kak Bazaar Item 5':                                           ("the #Kakariko Bazaar# offers", None, None),
    'Kak Bazaar Item 6':                                           ("the #Kakariko Bazaar# offers", None, None),
    'Kak Bazaar Item 7':                                           ("the #Kakariko Bazaar# offers", None, None),
    'Kak Bazaar Item 8':                                           ("the #Kakariko Bazaar# offers", None, None),

    'ZD Shop Item 1':                                              ("a #Zora shopkeeper# sells", None, None),
    'ZD Shop Item 2':                                              ("a #Zora shopkeeper# sells", None, None),
    'ZD Shop Item 3':                                              ("a #Zora shopkeeper# sells", None, None),
    'ZD Shop Item 4':                                              ("a #Zora shopkeeper# sells", None, None),
    'ZD Shop Item 5':                                              ("a #Zora shopkeeper# sells", None, None),
    'ZD Shop Item 6':                                              ("a #Zora shopkeeper# sells", None, None),
    'ZD Shop Item 7':                                              ("a #Zora shopkeeper# sells", None, None),
    'ZD Shop Item 8':                                              ("a #Zora shopkeeper# sells", None, None),

    'GC Shop Item 1':                                              ("a #Goron shopkeeper# sells", None, None),
    'GC Shop Item 2':                                              ("a #Goron shopkeeper# sells", None, None),
    'GC Shop Item 3':                                              ("a #Goron shopkeeper# sells", None, None),
    'GC Shop Item 4':                                              ("a #Goron shopkeeper# sells", None, None),
    'GC Shop Item 5':                                              ("a #Goron shopkeeper# sells", None, None),
    'GC Shop Item 6':                                              ("a #Goron shopkeeper# sells", None, None),
    'GC Shop Item 7':                                              ("a #Goron shopkeeper# sells", None, None),
    'GC Shop Item 8':                                              ("a #Goron shopkeeper# sells", None, None),

    'Deku Tree MQ Deku Scrub':                                     ("a #scrub in the Deku Tree# sells", None, None),

    'HF Deku Scrub Grotto':                                        ("a lonely #scrub in a hole# sells", None, None),
    'LLR Deku Scrub Grotto Left':                                  ("a #trio of scrubs# sells", None, None),
    'LLR Deku Scrub Grotto Right':                                 ("a #trio of scrubs# sells", None, None),
    'LLR Deku Scrub Grotto Center':                                ("a #trio of scrubs# sells", None, None),

    'LW Deku Scrub Near Deku Theater Right':                       ("a pair of #scrubs in the woods# sells", None, None),
    'LW Deku Scrub Near Deku Theater Left':                        ("a pair of #scrubs in the woods# sells", None, None),
    'LW Deku Scrub Near Bridge':                                   ("a #scrub by a bridge# sells", None, None),
    'LW Deku Scrub Grotto Rear':                                   ("a #scrub underground duo# sells", None, None),
    'LW Deku Scrub Grotto Front':                                  ("a #scrub underground duo# sells", None, None),

    'SFM Deku Scrub Grotto Rear':                                  ("a #scrub underground duo# sells", None, None),
    'SFM Deku Scrub Grotto Front':                                 ("a #scrub underground duo# sells", None, None),

    'GC Deku Scrub Grotto Left':                                   ("a #trio of scrubs# sells", None, None),
    'GC Deku Scrub Grotto Right':                                  ("a #trio of scrubs# sells", None, None),
    'GC Deku Scrub Grotto Center':                                 ("a #trio of scrubs# sells", None, None),

    'Dodongos Cavern Deku Scrub Near Bomb Bag Left':               ("a pair of #scrubs in Dodongo's Cavern# sells", None, None),
    'Dodongos Cavern Deku Scrub Side Room Near Dodongos':          ("a #scrub guarded by Lizalfos# sells", None, None),
    'Dodongos Cavern Deku Scrub Near Bomb Bag Right':              ("a pair of #scrubs in Dodongo's Cavern# sells", None, None),
    'Dodongos Cavern Deku Scrub Lobby':                            ("a #scrub in Dodongo's Cavern# sells", None, None),

    'Dodongos Cavern MQ Deku Scrub Lobby Rear':                    ("a pair of #scrubs in Dodongo's Cavern# sells", None, None),
    'Dodongos Cavern MQ Deku Scrub Lobby Front':                   ("a pair of #scrubs in Dodongo's Cavern# sells", None, None),
    'Dodongos Cavern MQ Deku Scrub Staircase':                     ("a #scrub in Dodongo's Cavern# sells", None, None),
    'Dodongos Cavern MQ Deku Scrub Side Room Near Lower Lizalfos': ("a #scrub guarded by Lizalfos# sells", None, None),

    'DMC Deku Scrub Grotto Left':                                  ("a #trio of scrubs# sells", None, None),
    'DMC Deku Scrub Grotto Right':                                 ("a #trio of scrubs# sells", None, None),
    'DMC Deku Scrub Grotto Center':                                ("a #trio of scrubs# sells", None, None),

    'ZR Deku Scrub Grotto Rear':                                   ("a #scrub underground duo# sells", None, None),
    'ZR Deku Scrub Grotto Front':                                  ("a #scrub underground duo# sells", None, None),

    'Jabu Jabus Belly Deku Scrub':                                 ("a #scrub in a deity# sells", None, None),

    'LH Deku Scrub Grotto Left':                                   ("a #trio of scrubs# sells", None, None),
    'LH Deku Scrub Grotto Right':                                  ("a #trio of scrubs# sells", None, None),
    'LH Deku Scrub Grotto Center':                                 ("a #trio of scrubs# sells", None, None),

    'GV Deku Scrub Grotto Rear':                                   ("a #scrub underground duo# sells", None, None),
    'GV Deku Scrub Grotto Front':                                  ("a #scrub underground duo# sells", None, None),

    'Colossus Deku Scrub Grotto Front':                            ("a #scrub underground duo# sells", None, None),
    'Colossus Deku Scrub Grotto Rear':                             ("a #scrub underground duo# sells", None, None),

    'Ganons Castle Deku Scrub Center-Left':                        ("#scrubs in Ganon's Castle# sell", None, None),
    'Ganons Castle Deku Scrub Center-Right':                       ("#scrubs in Ganon's Castle# sell", None, None),
    'Ganons Castle Deku Scrub Right':                              ("#scrubs in Ganon's Castle# sell", None, None),
    'Ganons Castle Deku Scrub Left':                               ("#scrubs in Ganon's Castle# sell", None, None),

    'Ganons Castle MQ Deku Scrub Right':                           ("#scrubs in Ganon's Castle# sell", None, None),
    'Ganons Castle MQ Deku Scrub Center-Left':                     ("#scrubs in Ganon's Castle# sell", None, None),
    'Ganons Castle MQ Deku Scrub Center':                          ("#scrubs in Ganon's Castle# sell", None, None),
    'Ganons Castle MQ Deku Scrub Center-Right':                    ("#scrubs in Ganon's Castle# sell", None, None),
    'Ganons Castle MQ Deku Scrub Left':                            ("#scrubs in Ganon's Castle# sell", None, None),

    'LLR Stables Left Cow':                                        ("a #cow in a stable# gifts", None, None),
    'LLR Stables Right Cow':                                       ("a #cow in a stable# gifts", None, None),
    'LLR Tower Right Cow':                                         ("a #cow in a ranch silo# gifts", None, None),
    'LLR Tower Left Cow':                                          ("a #cow in a ranch silo# gifts", None, None),
    'Kak Impas House Cow':                                         ("a #cow imprisoned in a house# protects", None, None),
    'DMT Cow Grotto Cow':                                          ("a #cow in a luxurious hole# offers", None, None),

    'Desert Colossus -> Colossus Grotto':                       ("lifting a #rock in the desert# reveals", None, None),
    'GV Grotto Ledge -> GV Octorok Grotto':                     ("a rock on #a ledge in the valley# hides", None, None),
    'GC Grotto Platform -> GC Grotto':                          ("a #pool of lava# in Goron City blocks the way to", None, None),
    'GF Entrances Behind Crates -> GF Storms Grotto':           ("a #storm within Gerudo's Fortress# reveals", None, None),
    'Zoras Domain -> ZD Storms Grotto':                         ("a #storm within Zora's Domain# reveals", None, None),
    'Hyrule Castle Grounds -> HC Storms Grotto':                ("a #storm near the castle# reveals", None, None),
    'GV Fortress Side -> GV Storms Grotto':                     ("a #storm in the valley# reveals", None, None),
    'Desert Colossus -> Colossus Great Fairy Fountain':         ("a #fractured desert wall# hides", None, None),
    'Ganons Castle Grounds -> OGC Great Fairy Fountain':        ("a #heavy pillar# outside the castle obstructs", None, None),
    'Zoras Fountain -> ZF Great Fairy Fountain':                ("a #fountain wall# hides", None, None),
    'GV Fortress Side -> GV Carpenter Tent':                    ("a #tent in the valley# covers", None, None),
    'Graveyard Warp Pad Region -> Shadow Temple Entryway':      ("at the #back of the Graveyard#, there is", None, None),
    'Lake Hylia -> Water Temple Lobby':                         ("deep #under a vast lake#, one can find", None, None),
    'Gerudo Fortress -> Gerudo Training Ground Lobby':          ("paying a #fee to the Gerudos# grants access to", None, None),
    'Zoras Fountain -> Jabu Jabus Belly Beginning':             ("inside #Jabu Jabu#, one can find", None, None),
    'Kakariko Village -> Bottom of the Well':                   ("a #village well# leads to", None, None),

    'Ganons Castle Ledge -> Ganons Castle Lobby':               ("the #rainbow bridge# leads to", None, None),
    'Ganons Castle Main -> Ganons Castle Tower':                ("a #castle barrier# protects the way to", "#Ganon's trials# protect the way to", None),

    'KF Links House':                                           ("Link's House", None, "no_gender"),
    'Temple of Time':                                           ("the #Temple of Time#", None, "no_gender"),
    'KF Midos House':                                           ("Mido's house", None, "no_gender"),
    'KF Sarias House':                                          ("Saria's House", None, "no_gender"),
    'KF House of Twins':                                        ("the #House of Twins#", None, "no_gender"),
    'KF Know It All House':                                     ("Know-It-All Brothers' House", None, "no_gender"),
    'KF Kokiri Shop':                                           ("the #Kokiri Shop#", None, "no_gender"),
    'LH Lab':                                                   ("the #Lakeside Laboratory#", None, "no_gender"),
    'LH Fishing Hole':                                          ("the #Fishing Pond#", None, "no_gender"),
    'GV Carpenter Tent':                                        ("the #Carpenters' tent#", None, "no_gender"),
    'Market Guard House':                                       ("the #Guard House#", None, "no_gender"),
    'Market Mask Shop':                                         ("the #Happy Mask Shop#", None, "no_gender"),
    'Market Bombchu Bowling':                                   ("the #Bombchu Bowling Alley#", None, "no_gender"),
    'Market Potion Shop':                                       ("the #Market Potion Shop#", None, "no_gender"),
    'Market Treasure Chest Game':                               ("the #Treasure Box Shop#", None, "no_gender"),
    'Market Bombchu Shop':                                      ("the #Bombchu Shop#", None, "no_gender"),
    'Market Man in Green House':                                ("Man in Green's House", None, "no_gender"),
    'Kak Windmill':                                             ("the #Windmill#", None, "no_gender"),
    'Kak Carpenter Boss House':                                 ("the #Carpenters' Boss House#", None, "no_gender"),
    'Kak House of Skulltula':                                   ("the #House of Skulltula#", None, "no_gender"),
    'Kak Impas House':                                          ("Impa's House", None, "no_gender"),
    'Kak Impas House Back':                                     ("Impa's cow cage", None, "no_gender"),
    'Kak Odd Medicine Building':                                ("Granny's Potion Shop", None, "no_gender"),
    'Graveyard Dampes House':                                   ("Dampé's Hut", None, "no_gender"),
    'GC Shop':                                                  ("the #Goron Shop#", None, "no_gender"),
    'ZD Shop':                                                  ("the #Zora Shop#", None, "no_gender"),
    'LLR Talons House':                                         ("Talon's House", None, "no_gender"),
    'LLR Stables':                                              ("a #stable#", None, "no_gender"),
    'LLR Tower':                                                ("the #Lon Lon Tower#", None, "no_gender"),
    'Market Bazaar':                                            ("the #Market Bazaar#", None, "no_gender"),
    'Market Shooting Gallery':                                  ("a #Slingshot Shooting Gallery#", None, "no_gender"),
    'Kak Bazaar':                                               ("the #Kakariko Bazaar#", None, "no_gender"),
    'Kak Potion Shop Front':                                    ("the #Kakariko Potion Shop#", None, "no_gender"),
    'Kak Potion Shop Back':                                     ("the #Kakariko Potion Shop#", None, "no_gender"),
    'Kak Shooting Gallery':                                     ("a #Bow Shooting Gallery#", None, "no_gender"),
    'Colossus Great Fairy Fountain':                            ("a #Great Fairy Fountain#", None, "no_gender"),
    'HC Great Fairy Fountain':                                  ("a #Great Fairy Fountain#", None, "no_gender"),
    'OGC Great Fairy Fountain':                                 ("a #Great Fairy Fountain#", None, "no_gender"),
    'DMC Great Fairy Fountain':                                 ("a #Great Fairy Fountain#", None, "no_gender"),
    'DMT Great Fairy Fountain':                                 ("a #Great Fairy Fountain#", None, "no_gender"),
    'ZF Great Fairy Fountain':                                  ("a #Great Fairy Fountain#", None, "no_gender"),
    'Graveyard Shield Grave':                                   ("a #grave with a free chest#", None, "no_gender"),
    'Graveyard Heart Piece Grave':                              ("a chest spawned by #Sun's Song#", None, "no_gender"),
    'Graveyard Royal Familys Tomb':                             ("the #Royal Family's Tomb#", None, "no_gender"),
    'Graveyard Dampes Grave':                                   ("Dampé's Grave", None, "no_gender"),
    'DMT Cow Grotto':                                           ("a solitary #Cow#", None, "no_gender"),
    'HC Storms Grotto':                                         ("a sandy grotto with #fragile walls#", None, "no_gender"),
    'HF Tektite Grotto':                                        ("a pool guarded by a #Tektite#", None, "no_gender"),
    'HF Near Kak Grotto':                                       ("a #Big Skulltula# guarding a Gold one", None, "no_gender"),
    'HF Cow Grotto':                                            ("a grotto full of #spider webs#", None, "no_gender"),
    'Kak Redead Grotto':                                        ("#ReDeads# guarding a chest", None, "no_gender"),
    'SFM Wolfos Grotto':                                        ("#Wolfos# guarding a chest", None, "no_gender"),
    'GV Octorok Grotto':                                        ("an #Octorok# guarding a rich pool", None, "no_gender"),
    'Deku Theater':                                             ("the #Lost Woods Stage#", None, "no_gender"),
    'ZR Open Grotto':                                           ("a #generic grotto#", None, "no_gender"),
    'DMC Upper Grotto':                                         ("a #generic grotto#", None, "no_gender"),
    'DMT Storms Grotto':                                        ("a #generic grotto#", None, "no_gender"),
    'Kak Open Grotto':                                          ("a #generic grotto#", None, "no_gender"),
    'HF Near Market Grotto':                                    ("a #generic grotto#", None, "no_gender"),
    'HF Open Grotto':                                           ("a #generic grotto#", None, "no_gender"),
    'HF Southeast Grotto':                                      ("a #generic grotto#", None, "no_gender"),
    'KF Storms Grotto':                                         ("a #generic grotto#", None, "no_gender"),
    'LW Near Shortcuts Grotto':                                 ("a #generic grotto#", None, "no_gender"),
    'HF Inside Fence Grotto':                                   ("a #lonely Deku Scrub#", None, "no_gender"),
    'LW Scrubs Grotto':                                         ("#2 Deku Scrubs# including an Upgrade one", None, "no_gender"),
    'Colossus Grotto':                                          ("2 Deku Scrubs", None, "no_gender"),
    'ZR Storms Grotto':                                         ("2 Deku Scrubs", None, "no_gender"),
    'SFM Storms Grotto':                                        ("2 Deku Scrubs", None, "no_gender"),
    'GV Storms Grotto':                                         ("2 Deku Scrubs", None, "no_gender"),
    'LH Grotto':                                                ("3 Deku Scrubs", None, "no_gender"),
    'DMC Hammer Grotto':                                        ("3 Deku Scrubs", None, "no_gender"),
    'GC Grotto':                                                ("3 Deku Scrubs", None, "no_gender"),
    'LLR Grotto':                                               ("3 Deku Scrubs", None, "no_gender"),
    'ZR Fairy Grotto':                                          ("a small #Fairy Fountain#", None, "no_gender"),
    'HF Fairy Grotto':                                          ("a small #Fairy Fountain#", None, "no_gender"),
    'SFM Fairy Grotto':                                         ("a small #Fairy Fountain#", None, "no_gender"),
    'ZD Storms Grotto':                                         ("a small #Fairy Fountain#", None, "no_gender"),
    'GF Storms Grotto':                                         ("a small #Fairy Fountain#", None, "no_gender"),
    'Queen Gohma Boss Room':                                    ("the #Parasitic Armored Arachnid#", "#Queen Gohma#", "no_gender"),
    'King Dodongo Boss Room':                                   ("the #Infernal Dinosaur#", "#King Dodongo#", "no_gender"),
    'Barinade Boss Room':                                       ("the #Bio-Electric Anemone#", "#Barinade#", "no_gender"),
    'Phantom Ganon Boss Room':                                  ("the #Evil Spirit from Beyond#", "#Phantom Ganon#", "no_gender"),
    'Volvagia Boss Room':                                       ("the #Subterranean Lava Dragon#", "#Volvagia#", "no_gender"),
    'Morpha Boss Room':                                         ("the #Giant Aquatic Amoeba#", "#Morpha#", "no_gender"),
    'Bongo Bongo Boss Room':                                    ("the #Phantom Shadow Beast#", "#Bongo Bongo#", "no_gender"),
    'Twinrova Boss Room':                                       ("the #Sorceress Sisters#", "#Twinrova#", "no_gender"),
    'Ganons Castle Tower':                                      ("#Ganon's Tower#", None, "no_gender"),

    # Junk hints must satisfy all the following conditions:
    # - They aren't inappropriate.
    # - They aren't absurdly long copy pastas.
    # - They aren't quotes or references that are simply not funny when out-of-context.
    # To elaborate on this last point: junk hints need to be able to be understood
    # by everyone, and not just those who get the obscure references.
    # Zelda references are considered fair game.

    # First generation junk hints
    '1002':                                                     ("${12 68 79}They say that monarchy is a terrible system of governance.", None, None), # sfx: Zelda gasp
    '1003':                                                     ("${12 68 79}They say that Zelda is a poor leader.", None, None), # sfx: Zelda gasp
    '1004':                                                     ("These hints can be quite useful. This is an exception.", None, None),
    '1006':                                                     ("They say that all the Zora drowned in Wind Waker.", None, None),
    '1008':                                                     ("Remember when Ganon was a blue pig?^I remember.", None, None), # ref: A Link to the Past
    '1009':                                                     ("One who does not have Triforce can't go in.", None, None),
    '1010':                                                     ("Save your future, end the Happy Mask Salesman.", None, None),
    '1012':                                                     ("I'm stoned. Get it?", None, None),
    '1013':                                                     ("Hoot! Hoot! Would you like me to repeat that?", None, None), # ref: Kaepora Gaebora (the owl)
    '1014':                                                     ("Gorons are stupid. They eat rocks. Except, apparently, the big rock blocking Dodongo's Cavern.", None, None),
    '1015':                                                     ("They say that Lon Lon Ranch prospered under Ingo.", None, None),
    '1017':                                                     ("Without the Lens of Truth, the Treasure Chest Mini-Game is a 1 out of 32 chance.^Good luck!", None, None),
    '1018':                                                     ("Use bombs wisely.", None, None),
    '1022':                                                     ("You're comparing yourself to me?^Ha! You're not even good enough to be my fake.", None, None), # ref: SA2
    '1024':                                                     ("What happened to Sheik?", None, None),
    '1026':                                                     ("I've heard Sploosh Kaboom is a tricky game.", None, None), # ref: Wind Waker
    '1028':                                                     ("I bet you'd like to have more bombs.", None, None),
    '1029':                                                     ("When all else fails, use Fire.", None, None),
    '1030':                                                     ("Here's a hint, @. Don't be bad.", None, None),
    '1031':                                                     ("Game Over. Return of Ganon.", None, None), # ref: Zelda II
    '1032':                                                     ("May the way of the Hero lead to the Triforce.", None, None),
    '1033':                                                     ("Can't find an item? Scan an Amiibo.", None, None),
    '1034':                                                     ("They say this game has just a few glitches.", None, None),
    '1035':                                                     ("BRRING BRRING This is Ulrira. Wrong number?", None, None), # ref: Link's Awakening
    '1036':                                                     ("Tingle Tingle Kooloo Limpah", None, None), # ref: Majora's Mask
    '1038':                                                     ("They say that Ganondorf will appear in the next Mario Tennis.", None, None),
    '1039':                                                     ("Medigoron sells the earliest Breath of the Wild demo.", None, None),
    '1041':                                                     ("You were almost a @ sandwich.", None, None),
    '1042':                                                     ("I'm a helpful hint Gossip Stone!^See, I'm helping.", None, None),
    '1043':                                                     ("Dear @, please come to the castle. I've baked a cake for you.&Yours truly, princess Zelda.", None, None), # ref: Super Mario 64
    '1044':                                                     ("They say all toasters toast toast.", None, None), # ref: Hotel Mario
    '1045':                                                     ("They say that Okami is the best Zelda game.", None, None), # ref: people often say that Okami feels and plays like a Zelda game
    '1046':                                                     ("They say that quest guidance can be found at a talking rock.", None, None),
    '1047':                                                     ("They say that the final item you're looking for can be found somewhere in Hyrule.", None, None),
    '1048':                                                     ("${12 68 7a}Mweep${07 04 51}", None, None), # Mweep
    '1049':                                                     ("They say that Barinade fears Deku Nuts.", None, None),
    '1050':                                                     ("They say that Flare Dancers do not fear Goron-crafted blades.", None, None),
    '1051':                                                     ("They say that Morpha is easily trapped in a corner.", None, None),
    '1052':                                                     ("They say that Bongo Bongo really hates the cold.", None, None),
    '1053':                                                     ("They say that crouch stabs mimic the effects of your last attack.", None, None),
    '1054':                                                     ("They say that bombing the hole Volvagia last flew into can be rewarding.", None, None),
    '1055':                                                     ("They say that invisible ghosts can be exposed with Deku Nuts.", None, None),
    '1056':                                                     ("They say that the real Phantom Ganon is bright and loud.", None, None),
    '1057':                                                     ("They say that the fastest way forward is walking backwards.", None, None),
    '1058':                                                     ("They say that leaping above the Market entrance enriches most children.", None, None),
    '1059':                                                     ("They say that looking into darkness may find darkness looking back into you.", None, None), # ref: Nietzsche
    '1060':                                                     ("You found a spiritual Stone! By which I mean, I worship Nayru.", None, None),
    '1061':                                                     ("A broken stick is just as good as a Master Sword. Who knew?", None, None),
    '1062':                                                     ("Open your eyes.^Open your eyes.^Wake up, @.", None, None), # ref: Breath of the Wild
    '1063':                                                     ("They say that arbitrary code execution leads to the credits sequence.", None, None),
    '1064':                                                     ("They say that Twinrova always casts the same spell the first three times.", None, None),
    '1065':                                                     ("They say that the Development branch may be unstable.", None, None),
    '1066':                                                     ("You're playing a Randomizer. I'm randomized!^${12 48 31}Here's a random number:  #4#.&Enjoy your Randomizer!", None, None), # ref: xkcd comic / sfx: get small item from chest
    '1067':                                                     ("They say Ganondorf's bolts can be reflected with glass or steel.", None, None),
    '1068':                                                     ("They say Ganon's tail is vulnerable to nuts, arrows, swords, explosives, hammers...^...sticks, seeds, boomerangs...^...rods, shovels, iron balls, angry bees...", None, None), # ref: various Zelda games
    '1069':                                                     ("They say that you're wasting time reading this hint, but I disagree. Talk to me again!", None, None),
    '1070':                                                     ("They say Ganondorf knows where to find the instrument of his doom.", None, None),
    '1071':                                                     ("I heard @ is pretty good at Zelda.", None, None),

    # Second generation junk hints
    '1072':                                                     ("Fingers-Mazda, the first thief in the world, stole fire from the gods.^But he was unable to fence it.&It was too hot.&He got really burned on that deal.", None, None), # ref: Discworld
    '1073':                                                     ("Boing-oing!^There are times in life when one should seek the help of others...^Thus, when standing alone fails to help, stand together.", None, None), # ref: Gossip Stone in Phantom Hourglass
    '1074':                                                     ("They say that if you don't use your slingshot at all when you play the slingshot minigame, the owner gets upset with you.", None, None),
    '1075':                                                     ("Hey! Wait! Don't go out! It's unsafe!^Wild Pokémon live in tall grass!^You need your own Pokémon for your protection.", None, None), # ref: Pokémon
    '1076':                                                     ("They say it's 106 miles to Hyrule Castle, we have half a bar of magic, it's dark, and we're wearing sunglasses.", None, None), # ref: Blues Brothers
    '1078':                                                     ("It would be a shame if something... unfortunate... were to happen to you.^Have you considered saving lately?", None, None), # ref: meme
    '1079':                                                     ("They say that something wonderful happens when playing the Song of Storms after planting a magic bean.", None, None),
    '1080':                                                     ("Long time watcher, first time player. Greetings from Termina. Incentive goes to Randobot's choice.", None, None), # ref: GDQ meme
    '1081':                                                     ("No matter what happens...Do not give up, do not complain, and do NOT stay up all night playing!", None, None), # ref: Wind Waker
    '1082':                                                     ("That's a nice wall you got there. Would be a shame if I just... clipped right through that.", None, None),
    '1083':                                                     ("Ganondorf used to be an adventurer like me, but then he took a light arrow to the knee.", None, None), # ref: Skyrim
    '1084':                                                     ("They say that the easiest way to kill Peahats is using Din's Fire while they're grounded.", None, None),
    '1085':                                                     ("They say that the castle guards' routes have major security vulnerabilities.", None, None),
    '1086':                                                     ("They say that Epona is an exceptional horse. Able to clear canyons in a single bound.", None, None),
    '1087':                                                     ("They say only one heart piece in all of Hyrule will declare the holder a winner.", None, None),
    '1088':                                                     ("Are you stuck? Try asking for help in our Discord server or check out our Wiki!", None, None),
    '1089':                                                     ("You would be surprised at all the things you can Hookshot in the Spirit Temple!", None, None),
    '1090':                                                     ("I once glued a set of false teeth to the Boomerang.^${12 39 c7}That came back to bite me.", None, None), # sfx: Ganondorf laugh
    '1091':                                                     ("They say that most of the water in Hyrule flows through King Zora's buttocks.", None, None),
    '1092':                                                     ("Space, space, wanna go to space, yes, please space. Space space. Go to space.", None, None), # ref: Portal 2
    '1093':                                                     ("They say that you must read the names of \"Special Deal\" items in shops carefully.", None, None),
    '1094':                                                     ("Did you know that the Boomerang instantly stuns Phantom Ganon's second form?", None, None),
    '1095':                                                     ("I came here to chew bubblegum and play rando. And I'm all out of bubblegum.", None, None), # ref: They Live
    '1096':                                                     ("Did you know that Stalchildren leave you alone when wearing the Bunny Hood?", None, None),
    '1097':                                                     ("This Gossip Stone Is Dedicated to Those Who Perished Before Ganon Was Defeated.", None, None),
    '1098':                                                     ("Did you know that Blue Fire destroys mud walls and detonates Bomb Flowers?", None, None),
    '1099':                                                     ("Are you sure you want to play this? Wanna go get some tacos or something?", None, None),
    '1100':                                                     ("What did Zelda suggest that Link do when diplomacy didn't work?^${12 39 C7}Triforce.", None, None), # sfx: Ganondorf laugh
    '1101':                                                     ("They say that bombing the hole Volvagia last flew into can be rewarding.", None, None),
    '1102':                                                     ("Hi @, we've been trying to reach you about your horse's extended warranty.", None, None),
    '1103':                                                     ("Ganondorf brushes his rotten teeth with salted slug flavoured tooth paste!", None, None), # ref: Banjo Kazooie
    '1104':                                                     ("I'm Commander Shepard, and this is my favorite Gossip Stone in Hyrule!", None, None), # ref: Mass Effect
    '1105':                                                     ("They say that tossing a bomb will cause a Blue Bubble to go after it.", None, None),
    '1106':                                                     ("They say that the Lizalfos in Dodongo's Cavern like to play in lava.", None, None),
    '1107':                                                     ("Why won't anyone acknowledge the housing crisis in Kakariko Village?", None, None),
    '1108':                                                     ("Don't believe in yourself. Believe in the me that believes in you!", None, None), # ref: Anime
    '1109':                                                     ("This is a haiku&Five syllables then seven&Five more to finish", None, None),
    '1110':                                                     ("They say that beating Bongo Bongo quickly requires an even tempo.", None, None),
    '1111':                                                     ("Did you know that you can tune a piano but you can't tune a fish?", None, None), # Studio Album by REO Speedwagon
    '1112':                                                     ("You thought it would be a useful hint, but it was me, Junk Hint!", None, None), # ref: Jojo's Bizarre Adventure
    '1113':                                                     ("They say you can cut corners to get to your destination faster.", None, None),
    '1114':                                                     ("Three things are certain: death, taxes, and forgetting a check.", None, None), # ref: Benjamin Franklin, allegedly
    '1115':                                                     ("Have you thought about going where the items are?^Just saying.", None, None),
    '1116':                                                     ("They say that the true reward is the friends we made along the way.", None, None), # ref: common meme with unknown origins
    '1117':                                                     ("Gossip Stone Shuffle must be on. I'm normally in Zora's Domain!", None, None),
    '1118':                                                     ("When ASM is used to code a randomizer they should call it ASMR.", None, None),
    '1119':                                                     ("It's so lonely being stuck here with nobody else to talk to...", None, None),
    '1120':                                                     ("Why are they called Wallmasters if they come from the ceiling?", None, None),
    '1121':                                                     ("They say that Zelda's Lullaby can be used to repair broken signs.", None, None),
    '1122':                                                     ("Fell for it, didn't you, fool? Junk hint cross split attack!", None, None), # ref: Jojo's Bizarre Adventure
    '1123':                                                     ("Please don't abandon this seed. Our world deserves saving!", None, None),
    '1124':                                                     ("I wanna be a rocketship, @! Please help me live my dreams!", None, None),
    '1125':                                                     ("They say that King Zora needs to build a taller fence.", None, None),
    '1126':                                                     ("They say Goron fabrics protect against more than fire.", None, None),
    '1127':                                                     ("Did you know that ReDead mourn their defeated friends?", None, None),
    '1128':                                                     ("Did you know that ReDead eat their defeated friends?", None, None),
    '1129':                                                     ("What is a Hylian? A miserable little pile of secrets!", None, None), # ref: Castlevania
    '1130':                                                     ("The hint stone you have dialed&has been disconnected.", None, None), # ref: telephone error message
    '1131':                                                     ("We don't make mistakes, we have happy accidents.", None, None), # ref: Bob Ross
    '1132':                                                     ("I've heard Ganon dislikes lemon-flavored popsicles.", None, None),
    '1133':                                                     ("If Gorons eat rocks, does that mean I'm in danger?", None, None),
    '1134':                                                     ("They say Ingo is not very good at planning ahead.", None, None),
    '1136':                                                     ("They say that Anju needs to stop losing her chickens.", None, None),
    '1137':                                                     ("Can you move me? I don't get great service here.", None, None),
    '1138':                                                     ("Have you embraced the power of the Deku Nut yet?", None, None),
    '1139':                                                     ("They say that Mido is easily confused by sick flips.", None, None), # ref: Mido Skip
    '1140':                                                     ("They say that the path to Termina is a one-way trip.", None, None), # ref: Majora's Mask
    '1141':                                                     ("They say that @ deserves a hug. Everyone does!", None, None),
    '1142':                                                     ("I hear Termina is a great spot for a vacation!", None, None), # ref: Majora's Mask
    '1144':                                                     ("You've met with a terrible fate, haven't you?", None, None), # ref: Majora's Mask
    '1145':                                                     ("Try using various items and weapons on me :)", None, None),
    '1146':                                                     ("On second thought, let's not go to Hyrule Castle. 'Tis a silly place.", None, None), # ref: Monty Python
    '1147':                                                     ("If you see something suspicious, bomb it!", None, None),
    '1148':                                                     ("Don't forget to write down your hints :)", None, None),
    '1149':                                                     ("Would you kindly...&close this textbox?", None, None), # ref: Bioshock
    '1150':                                                     ("They say that King Dodongo dislikes smoke.", None, None), # ref: Zelda 1
    '1151':                                                     ("Never give up. Trust your instincts!", None, None), # ref: Star Fox 64
    '1152':                                                     ("I love to gossip! Wanna be friends?", None, None),
    '1153':                                                     ("This isn't where I parked my horse!", None, None), # ref: EuroTrip
    '1156':                                                     ("Anything not saved will be lost.", None, None), # ref: Nintendo (various games and platforms)
    '1157':                                                     ("I was voted least helpful hint stone five years in a row!", None, None),
    '1158':                                                     ("They say that the Groose is loose.", None, None), # ref: Skyward Sword
    '1159':                                                     ("Twenty-three is number one!^And thirty-one is number two!", None, None), # ref: Deku Scrubs in Deku Tree
    '1160':                                                     ("Ya ha ha! You found me!", None, None), # ref: Breath of the Wild
    '1161':                                                     ("Do you like Like Likes?", None, None),
    '1162':                                                     ("Next you'll say:^\"Why am I still reading these?\"", None, None), # ref: Jojo's Bizarre Adventure
    '1165':                                                     ("You're a cool cat, @.", None, None),
    '1167':                                                     ("This hint is in another castle.", None, None), # ref: Mario
    '1169':                                                     ("Hydrate!", None, None),
    '1170':                                                     ("They say that there is an alcove with a Recovery Heart behind the lava wall in Dodongo's Cavern.", None, None),
    '1171':                                                     ("Having regrets? Reset without saving!", None, None),
    '1172':                                                     ("Did you know that Gorons understood SRM long before speedrunners did?", None, None), # ref: Goron City murals
    '1173':                                                     ("Did you know that the Discord server has a public Plandomizer library?", None, None),
    '1174':                                                     ("${12 28 DF}Moo!", None, None), # sfx: cow
    '1175':                                                     ("${12 28 D8}Woof!", None, None), # sfx: dog
    '1176':                                                     ("${12 68 08}Aah! You startled me!", None, None), # sfx: adult Link scream (when falling)
    '1178':                                                     ("Use Multiworld to cross the gaps between worlds and engage in jolly co-operation!", None, None), # ref: Dark Souls
    '1179':                                                     ("${12 68 51}What in tarnation!", None, None), # sfx: Talon surprised at being woken
    '1180':                                                     ("Press \u00A5\u00A5\u00A6\u00A6\u00A7\u00A8\u00A7\u00A8\u00A0\u009F to warp to&the credits.", None, None), # ref: Konami Code
    '1181':                                                     ("Oh!^Oh-oh!^C'mon!^Come on! Come on! Come on!^HOT!!^What a hot beat!^WHOOOOAH!^YEEEEAH!^YAHOOO!!", None, None), # ref: Darunia dancing
    '1182':                                                     ("${12 68 5F}Hey! Listen!", None, None), # sfx: Navi: "Hey!"
    '1183':                                                     ("I am the King of Gossip Stones, but fear not - I have the common touch! That means I can make conversation with everyone^from foreign dignitaries to the lowliest bumpkin - such as yourself!", None, None), # ref: Dragon Quest XI
    '1184':                                                     ("I am @, hero of the Gossip Stones! Hear my name and tremble!", None, None), # ref: Link the Goron
    '1185':                                                     ("Having trouble defeating Dark Link?^Look away from him while holding Z-Target and then when Dark Link walks up behind you, strafe sideways and slash your sword.", None, None),
    '1186':                                                     ("They say that if Link could say a few words, he'd be a better public speaker.", None, None),
    '1187':                                                     ("Did you know that you only need to play the Song of Time to open the Door of Time? The Spiritual Stones are not needed.", None, None),
    '1188':                                                     ("Where did Anju meet her lover?^${12 39 C7}At a Kafei.", None, None), # ref: Majora's Mask / sfx: Ganondorf laugh
    '1189':                                                     ("Did you know that you can access the Fire Temple boss door without dropping the pillar by using the Hover boots?", None, None),
    '1190':                                                     ("Key-locked in Fire Temple? Maybe Volvagia has your Small Key.", None, None),
    '1191':                                                     ("Expired Spoiler Log? Don't worry! The OoTR Discord staff can help you out.", None, None),
    '1192':                                                     ("Try holding a D-pad button on the item screen.", None, None),
    '1193':                                                     ("Did you know that in the Forest Temple you can reach the alcove in the block push room with Hover Boots?", None, None),
    '1194':                                                     ("Dodongo's Cavern is much easier and faster to clear as Adult.", None, None),
    '1195':                                                     ("Did you know that the solution to the Truth Spinner in Shadow Temple is never one of the two positions closest to the initial position?", None, None),
    '1196':                                                     ("Did you know that the Kokiri Sword is as effective as Deku Sticks against Dead Hand?", None, None),
    '1197':                                                     ("Did you know that Ruto is strong enough to defeat enemies and activate ceiling switches inside Jabu Jabu's Belly?", None, None),
    '1198':                                                     ("Did you know that Barinade, Volvagia and Twinrova hard require the Boomerang, Megaton Hammer and Mirror Shield, respectively?", None, None),
    '1199':                                                     ("Did you know that Dark Link's max health is equal to @'s max health?", None, None),
    '1200':                                                     ("Did you know that you can reach the invisible Hookshot target before the fans room in Shadow Temple with just the Hookshot if you backflip onto the chest?", None, None),
    '1201':                                                     ("${12 68 54}Objection!", None, None), # ref: Ace Attorney / sfx: Ingo's BWAAAAAH
    '1202':                                                     ("They say that in the castle courtyard you can see a portrait of a young Talon.", None, None), # ref: Talon = Mario joke
    '1203':                                                     ("They say that Phantom Ganon is a big Louisa May Alcott fan.", None, None), # ref: The Poe Sisters are named after characters from one of her novels
    '1204':                                                     ("Have you found all 41 Gossip Stones?^Only 40 of us give hints.", None, None), # The 41th stone is the Lake Hylia water level stone
    '1205':                                                     ("It's time for you to look inward and begin asking yourself the big questions:^How did Medigoron get inside that hole, and how does he get out for the credits?", None, None), # ref: Avatar The Last Airbender
    '1206':                                                     ("They say that Jabu Jabu is no longer a pescetarian in Master Quest.", None, None),
    '1207':                                                     ("Why are the floating skulls called \"Bubbles\" and the floating bubbles \"Shaboms\"?", None, None),
    '1208':                                                     ("Why aren't ReDead called ReAlive?", None, None),
    '1209':                                                     ("${12 48 27}Songs are hard, aren't they?", None, None), # sfx: failing a song
    '1210':                                                     ("Did you know that you can Boomerang items that are freestanding Heart Pieces in the unrandomized game?", None, None),
    '1211':                                                     ("Did you know that ReDead won't attack if you walk very slowly?", None, None),
    '1212':                                                     ("Did you know that ReDead and Gibdo have their own version of Sun's Song that freezes you?", None, None),
    '1213':                                                     ("${12 28 B1}\u009F \u00A7\u00A8\u00A6 \u00A7\u00A8\u00A6 \u009F\u00A6 \u009F\u00A6 \u00A8\u00A7\u009F", None, None), # ref: Frogs 2 / sfx: Frogs
    '1214':                                                     ("${12 28 A2}Help! I'm melting away!", None, None), # sfx: red ice melting
    '1215':                                                     ("${12 38 80}Eek!^I'm a little shy...", None, None), # sfx: Scrub hurt/stunned by Link
    '1216':                                                     ("Master, there is a 0 percent chance that this hint is useful in any way.", None, None), # ref: Skyward Sword
    '1217':                                                     ("${12 48 0B}Here, have a heart <3", None, None), # sfx: get Recovery Heart
    '1218':                                                     ("${12 48 03}Here, have a Rupee.", None, None), # sfx: get Rupee
    '1219':                                                     ("${12 68 31}Don't forget to stand up and stretch regularly.", None, None), # sfx: child Link stretching and yawning
    '1220':                                                     ("Remember that time you did that really embarrassing thing?^${12 68 3A}Yikes.", None, None), # sfx: child Link fall damage
    '1221':                                                     ("@ tries to read the Gossip Stone...^${12 48 06}but he's standing on the wrong side of it!", None, None), # ref: Dragon Quest XI / sfx: error (e.g. trying to equip an item as the wrong age)
    '1222':                                                     ("Plandomizer is a pathway to many abilities some consider to be... unnatural.", None, None), # ref: Star Wars
    '1223':                                                     ("Did you know that you can have complete control over the item placement, item pool, and more, using Plandomizer?", None, None),
    '1224':                                                     ("They say that the earth is round.^Just like pizza.", None, None),
    '1225':                                                     ("${12 68 62}Keeeyaaaah!^What is this?! A Hylian?!", None, None), # ref: Ruto meeting Big Octo / sfx: Ruto screaming
    '1226':                                                     ("For you, the day you read this hint was the most important day of your life.^But for me, it was Tuesday.", None, None), # ref: Street Fighter (the movie)
    '1227':                                                     ("Did you know that Barinade is allergic to bananas?", None, None),
    '1228':                                                     ("Have you seen my dodongo? Very large, eats everything, responds to \"King\".^Call Darunia in Goron City if found. Huge rupee reward!", None, None),
    '1229':                                                     ("Having trouble breathing underwater?^Have you tried wearing more BLUE?", None, None),
    '1230':                                                     ("Hi! I'm currently on an exchange program from Termina.^They say that East Clock Town is on the way of the hero.", None, None), # ref: Majora's Mask
    '1231':                                                     ("Why are you asking me? I don't have any answers! I'm just as confused as you are!", None, None),
    '1232':                                                     ("What do you call a group of Gorons?^${12 39 C7}A rock band.", None, None), # sfx: Ganondorf laugh
    '1233':                                                     ("When the moon hits Termina like a big pizza pie that's game over.", None, None), # ref: That's Amore by Dean Martin + Majora's Mask
    '1234':                                                     ("Ganondorf doesn't specialize in hiding items, nor in keeping secrets for that matter.", None, None),
    '1235':                                                     ("While you're wasting time reading this hint, the others are playing the seed.", None, None),
    '1236':                                                     ("Have you ever tried hammering the ground or wall in a room with Torch Slugs, Flare Dancers, Tektites, Walltulas, Scrubs or Deku Babas?", None, None),
    '1237':                                                     ("Did you know that there's a 1/201 chance per Rupee that the Zora from the diving minigame tosses a 500 Rupee?^Keep winning and the odds go up!", None, None),
    '1238':                                                     ("J = 0;&while J < 10;&   Press \u009F;&   J++;^   Press \u009F;&   J++;^   Press \u009F;&   J++;^   Press \u009F;&   J++;^   Press \u009F;&   J++;^   Press \u009F;&   J++;^   Press \u009F;&   J++;^   Press \u009F;&   J++;^   Press \u009F;&   J++;^   Press \u009F;^break;", None, None), # \u009F = A button

    'Deku Tree':                                                ("an ancient tree", "the Deku Tree", None),
    'Dodongos Cavern':                                          ("an immense cavern", "Dodongo's Cavern", None),
    'Jabu Jabus Belly':                                         ("the belly of a deity", "Jabu Jabu's Belly", None),
    'Forest Temple':                                            ("a deep forest", "the Forest Temple", None),
    'Fire Temple':                                              ("a high mountain", "the Fire Temple", None),
    'Water Temple':                                             ("a vast lake", "the Water Temple", None),
    'Shadow Temple':                                            ("the house of the dead", "the Shadow Temple", None),
    'Spirit Temple':                                            ("the goddess of the sand", "the Spirit Temple", None),
    'Ice Cavern':                                               ("a frozen maze", "the Ice Cavern", None),
    'Bottom of the Well':                                       ("a shadow's prison", "the Bottom of the Well", None),
    'Gerudo Training Ground':                                   ("the test of thieves", "the Gerudo Training Ground", None),
    'Ganons Castle':                                            ("a conquered citadel", "inside Ganon's Castle", None),

    'ganonBK_dungeon':                                          ("hidden somewhere #inside its castle#", None, None),
    'ganonBK_regional':                                         ("hidden somewhere #inside or nearby its castle#", None, None),
    'ganonBK_vanilla':                                          ("kept in a big chest #inside its tower#", None, None),
    'ganonBK_overworld':                                        ("hidden #outside of dungeons# in Hyrule", None, None),
    'ganonBK_any_dungeon':                                      ("hidden #inside a dungeon# in Hyrule", None, None),
    'ganonBK_keysanity':                                        ("hidden #anywhere in Hyrule#", None, None),
    'ganonBK_triforce':                                         ("given to the Hero once the #Triforce# is completed", None, None),

    'Spiritual Stone Text Start':                               ("3 Spiritual Stones found in Hyrule...", None, None),
    'Adult Altar Text Start':                                   ("When evil rules all, an awakening&voice from the Sacred Realm will&call those destined to be Sages,&who dwell in the \x05\x41five temples\x05\x40.", None, None),
    'Adult Altar Text End':                                     ("Together with the Hero of Time,&the awakened ones will bind the&evil and return the light of peace&to the world...", None, None),

    'Validation Line':                                          ("Hmph... Since you made it this far,&I'll let you know what glorious&prize of Ganon's you likely&missed out on in my tower.^Behold...^", None, None),
    '2001':                                                     ("Oh! It's @.&I was expecting someone called&Sheik. Do you know what&happened to them?", None, None),
    '2002':                                                     ("I knew I shouldn't have put the key&on the other side of my door.", None, None),
    '2003':                                                     ("Looks like it's time for a&round of tennis.", None, None),
    '2004':                                                     ("You'll never deflect my bolts of&energy with your sword,&then shoot me with those Light&Arrows you happen to have.", None, None),
    '2005':                                                     ("Why did I leave my trident&back in the desert?", None, None),
    '2006':                                                     ("Zelda is probably going to do&something stupid, like send you&back to your own timeline.^So this is quite meaningless.&Do you really want&to save this moron?", None, None),
    '2007':                                                     ("What about Zelda makes you think&she'd be a better ruler than I?^I saved Lon Lon Ranch,&fed the hungry,&and my castle floats.", None, None),
    '2008':                                                     ("I've learned this spell,&it's really neat,&I'll keep it later&for your treat!", None, None),
    '2009':                                                     ("Many tricks are up my sleeve,&to save yourself&you'd better leave!", None, None),
    '2010':                                                     ("After what you did to&Koholint Island, how can&you call me the bad guy?", None, None),
    '2011':                                                     ("Today, let's begin down&'The Hero is Defeated' timeline.", None, None),
}

hintTableFix = {key: {"vague_hint": vague, "clear_hint": clear, "gender": gender} for key, (vague, clear, gender) in hintTable.items()}

# Texts that is used in Hints.py
hint_text = {
    "gossip_prefix": "They say that ",
    "separator": " ",
    "move_prefixes": ['outside', 'inside'],
    "own_prefix": "Link's",
    "pocket": "#your pocket#",
    "second_own": "your {suffix}",
    "player_own": "@'s {suffix}",
    "world's": "world {world}'s {suffix}",
    "move_world": "{prefix} world {world}'s {suffix}",
    "player's": "player {world}'s {suffix}",
    "world_is_world_player": "the",
    "prep_position": "first", # placing of prepositon, either first or last
    "player_text": "Player {world}'s",
    "way_of_hero": "{location_text} is on the way of the hero.",
    "goal_format": "{location_text} is on {player_text} {goal_text}.",
    "foolish":"plundering {area} is a foolish choice.",
    "hoards": "{location_text} hoards #{item_text}#.",
    "can_be_found": "#{item_text}# can be found {location_text}.",
    "hero_path": "{location_text} may be on the hero's path.",
    "conjunction": " and ",
    "conjunction_more": ", ",
    "dual_always": "{location} #{first_item}# and #{second_item}#.",
    "always": "{location} #{item}#.",
    "entrance": "{entrance} {region}.",
    "trial_all": "#Ganon's Tower# is protected by a powerful barrier.",
    "trial_none": "Sheik dispelled the barrier around #Ganon's Tower#.",
    "trial_combine_sheik": "the #{trials} Trials# were dispelled by Sheik.",
    "trial_sheik": "the #{trial} Trial# was dispelled by Sheik.",
    "trial_combine_ganon": "the #{trials} Trials# protect Ganon's Tower.",
    "trial_ganon": "#the #{trial} Trials# protects Ganon's Tower.",
    "boss_pocket_clear": "\x08\x13{item_icon}One #@ already has#...",
    "boss_pocket_vague": "\x08\x13{item_icon}One in #@'s pocket#...",
    "boss_string": "\x08\x13{item_icon}One {location_text}...",
    "req_custom": "{count} {item}",
    "bridge_open": "The awakened ones will have #already created a bridge# to the castle where the evil dwells.",
    "bridge_vanilla": "the #Shadow and Spirit Medallions# as well as the #Light Arrows#",
    "bridge_clear": "The rainbow bridge will be built once the Hero collects {item_req}.",
    "bridge_vague": "The awakened ones will await for the Hero to collect {item_req}.",
    "major_item": "{hint_loc} has #{item_count}# major item.",
    "major_items": "{hint_loc} has #{item_count}# major items.",
    "dot_open": "Ye who may become a Hero...&Go and pull the Master Sword from the Pedestal of Time.",
    "dot_sot": "\x13\x07Ye who may become a Hero...&Stand with the Ocarina and play the Song of Time.",
    "dot_oot_sot": "\x13\x08Ye who may become a Hero... Stand with the Ocarina of Time and play the Song of Time.",
    "dot_stones": "Ye who owns 3 Spiritual Stones...&Go and pull the Master Sword from the Pedestal of Time.",
    "dot_stones_sot": "\x13\x07Ye who owns 3 Spiritual Stones...&Stand with the Ocarina and play the Song of Time.",
    "dot_stones_oot_sot": "\x13\x08Ye who owns 3 Spiritual Stones... Stand with the Ocarina of Time and play the Song of Time.",
    "ganon_remove": "And the door to the \x05\x41evil one\x05\x40's chamber will be left #unlocked#.",
    "ganon_req_vanilla": "the #Shadow and Spirit Medallions#",
    "ganon_stones": ("#Spiritual Stone#", "#Spiritual Stones#", "is", "are"),
    "ganon_medallions": ("#Medallion#", "#Medallions#", "is", "are"),
    "ganon_dungeons": ("#Spiritual Stone or Medallion#", "#Spiritual Stones and Medallions#", "is", "are"),
    "ganon_tokens": ("#Gold Skulltula Token#", "#Gold Skulltula Tokens#", "is", "are"),
    "ganon_hearts": ("#heart#", "#hearts#", "is", "are"),
    "ganon_lacs_bk": "provided by Zelda once {item_req_string} {verb} retrieved",
    "ganon_grant_bk": "automatically granted once {item_req} {verb} retrieved",
    "ganon_base": "And the \x05\x41evil one\x05\x40's key will be {bk_location_string}"
}

# Language specific text replace table
# Format: [[from: str, to: str]]
language_specific_replace_table = []

# Trial name replacer
trials = {
    'Spirit': "Spirit",
    'Light': "Light",
    'Fire': "Fire",
    'Shadow': "Shadow",
    'Water': "Water",
    'Forest': "Forest",
}

# Prefixes to remove for hints
hintPrefixes: list[str] = [
    'a few ',
    'some ',
    'plenty of ',
    'a ',
    'an ',
    'the ',
    '',
]

# Hint area texts
hint_area_enum = {
    "ROOT": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": "Link's pocket",
        "short_name": 'Free',
        "gender": "no_gender",
    },
    "HYRULE_FIELD": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'Hyrule Field',
        "short_name": 'Hyrule Field',
        "shorter_name": 'Field',
        "gender": "no_gender",
    },
    "LON_LON_RANCH": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": 'Lon Lon Ranch',
        "short_name": 'Lon Lon Ranch',
        "shorter_name": 'Ranch',
        "gender": "no_gender",
    },
    "MARKET": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'the Market',
        "short_name": 'Market',
        "shorter_name": 'Market',
        "gender": "no_gender",
    },
    "TEMPLE_OF_TIME": {
        "vague_prep": 'inside',
        "clear_prep": 'inside',
        "display_name": 'the Temple of Time',
        "short_name": 'Temple of Time',
        "shorter_name": 'ToT',
        "gender": "no_gender",
    },
    "CASTLE_GROUNDS": {
        "vague_prep": 'on',
        "clear_prep": 'on',
        "display_name": 'the Castle Grounds',
        "short_name": None,
        "shorter_name": 'Castle',
        "gender": "no_gender",
    },
    "HYRULE_CASTLE": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": 'Hyrule Castle',
        "short_name": 'Hyrule Castle',
        "shorter_name": 'HC',
        "gender": "no_gender",
    },
    "OUTSIDE_GANONS_CASTLE": {
        "vague_prep": None,
        "clear_prep": None,
        "display_name": "outside Ganon's Castle",
        "short_name": "Outside Ganon's Castle",
        "shorter_name": 'OGC',
        "gender": "no_gender",
    },
    "INSIDE_GANONS_CASTLE": {
        "vague_prep": 'inside',
        "clear_prep": None,
        "display_name": "inside Ganon's Castle",
        "short_name": "Inside Ganon's Castle",
        "shorter_name": 'Ganon',
        "gender": "no_gender",
    },
    "GANONDORFS_CHAMBER": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": "Ganondorf's Chamber",
        "short_name": "Ganondorf's Chamber",
        "gender": "no_gender",
    },
    "KOKIRI_FOREST": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'Kokiri Forest',
        "short_name": "Kokiri Forest",
        "shorter_name": 'Kokiri',
        "gender": "no_gender",
    },
    "DEKU_TREE": {
        "vague_prep": 'inside',
        "clear_prep": 'inside',
        "display_name": 'the Deku Tree',
        "short_name": "Deku Tree",
        "shorter_name": 'Deku',
        "gender": "no_gender",
    },
    "LOST_WOODS": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'the Lost Woods',
        "short_name": "Lost Woods",
        "shorter_name": 'Woods',
        "gender": "no_gender",
    },
    "SACRED_FOREST_MEADOW": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": 'the Sacred Forest Meadow',
        "short_name": "Sacred Forest Meadow",
        "shorter_name": 'Meadow',
        "gender": "no_gender",
    },
    "FOREST_TEMPLE": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'the Forest Temple',
        "short_name": "Forest Temple",
        "shorter_name": 'Forest',
        "gender": "no_gender",
    },
    "DEATH_MOUNTAIN_TRAIL": {
        "vague_prep": 'on',
        "clear_prep": 'on',
        "display_name": 'the Death Mountain Trail',
        "short_name": "Death Mountain Trail",
        "shorter_name": 'Trail',
        "gender": "no_gender",
    },
    "DODONGOS_CAVERN": {
        "vague_prep": 'within',
        "clear_prep": 'in',
        "display_name": "Dodongo's Cavern",
        "short_name": "Dodongo's Cavern",
        "shorter_name": 'DC',
        "gender": "no_gender",
    },
    "GORON_CITY": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'Goron City',
        "short_name": "Goron City",
        "shorter_name": 'Goron',
        "gender": "no_gender",
    },
    "DEATH_MOUNTAIN_CRATER": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'the Death Mountain Crater',
        "short_name": "Death Mountain Crater",
        "shorter_name": 'Crater',
        "gender": "no_gender",
    },
    "FIRE_TEMPLE": {
        "vague_prep": 'on',
        "clear_prep": 'in',
        "display_name": 'the Fire Temple',
        "short_name": "Fire Temple",
        "shorter_name": 'Fire',
        "gender": "no_gender",
    },
    "ZORA_RIVER": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": "Zora's River",
        "short_name": "Zora's River",
        "shorter_name": 'River',
        "gender": "no_gender",
    },
    "ZORAS_DOMAIN": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": "Zora's Domain",
        "short_name": "Zora's Domain",
        "shorter_name": 'Domain',
        "gender": "no_gender",
    },
    "ZORAS_FOUNTAIN": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": "Zora's Fountain",
        "short_name": "Zora's Fountain",
        "shorter_name": 'Fountain',
        "gender": "no_gender",
    },
    "JABU_JABUS_BELLY": {
        "vague_prep": 'in',
        "clear_prep": 'inside',
        "display_name": "Jabu Jabu's Belly",
        "short_name": "Jabu Jabu's Belly",
        "shorter_name": 'Jabu',
        "gender": "no_gender",
    },
    "ICE_CAVERN": {
        "vague_prep": 'inside',
        "clear_prep": 'in'    ,
        "display_name": 'the Ice Cavern',
        "short_name": "Ice Cavern",
        "shorter_name": 'Ice',
        "gender": "no_gender",
    },
    "LAKE_HYLIA": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": 'Lake Hylia',
        "short_name": "Lake Hylia",
        "shorter_name": 'Lake',
        "gender": "no_gender",
    },
    "WATER_TEMPLE": {
        "vague_prep": 'under',
        "clear_prep": 'in',
        "display_name": 'the Water Temple',
        "short_name": "Water Temple",
        "shorter_name": 'Water',
        "gender": "no_gender",
    },
    "KAKARIKO_VILLAGE": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'Kakariko Village',
        "short_name": "Kakariko Village",
        "shorter_name": 'Kakariko',
        "gender": "no_gender",
    },
    "BOTTOM_OF_THE_WELL": {
        "vague_prep": 'within',
        "clear_prep": 'at',
        "display_name": 'the Bottom of the Well',
        "short_name": "Bottom of the Well",
        "shorter_name": 'BotW',
        "gender": "no_gender",
    },
    "GRAVEYARD": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'the Graveyard',
        "short_name": "Graveyard",
        "shorter_name": 'GY',
        "gender": "no_gender",
    },
    "SHADOW_TEMPLE": {
        "vague_prep": 'within',
        "clear_prep": 'in',
        "display_name": 'the Shadow Temple',
        "short_name": "Shadow Temple",
        "shorter_name": 'Shadow',
        "gender": "no_gender",
    },
    "GERUDO_VALLEY": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": 'Gerudo Valley',
        "short_name": "Gerudo Valley",
        "shorter_name": 'Valley',
        "gender": "no_gender",
    },
    "GERUDO_FORTRESS": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": "Gerudo's Fortress",
        "short_name": "Gerudo's Fortress",
        "shorter_name": 'Fortress',
        "gender": "no_gender",
    },
    "THIEVES_HIDEOUT": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": "the Thieves' Hideout",
        "short_name": "Thieves' Hideout",
        "shorter_name": 'Hideout',
        "gender": "no_gender",
    },
    "GERUDO_TRAINING_GROUND": {
        "vague_prep": 'within',
        "clear_prep": 'on',
        "display_name": 'the Gerudo Training Ground',
        "short_name": "Gerudo Training Ground",
        "shorter_name": 'GTG',
        "gender": "no_gender",
    },
    "HAUNTED_WASTELAND": {
        "vague_prep": 'in',
        "clear_prep": 'in',
        "display_name": 'the Haunted Wasteland',
        "short_name": "Haunted Wasteland",
        "shorter_name": 'Wasteland',
        "gender": "no_gender",
    },
    "DESERT_COLOSSUS": {
        "vague_prep": 'at',
        "clear_prep": 'at',
        "display_name": 'the Desert Colossus',
        "short_name": "Desert Colossus",
        "shorter_name": 'Colossus',
        "gender": "no_gender",
    },
    "SPIRIT_TEMPLE": {
        "vague_prep": 'inside',
        "clear_prep": 'in',
        "display_name": 'the Spirit Temple',
        "short_name": "Spirit Temple",
        "shorter_name": 'Spirit',
        "gender": "no_gender",
    }
}

# Misc item hint which diplayed on somme places with no use (dampe_diary and ganondolf speech)
# TODO: Make these a type of some sort instead of a dict.
misc_item_hint_table = {
    'dampe_diary': {
        'default_item_text': "Whoever reads this, please visit {area}. I will let you have my stretching, shrinking keepsake.^I'm waiting for you.&--Dampé",
        'custom_item_text': "Whoever reads this, please visit {area}. I will let you have {item}.^I'm waiting for you.&--Dampé",
        'default_item_fallback': "Whoever reads this, I'm sorry, but I seem to have #misplaced# my stretching, shrinking keepsake.&--Dampé",
        'custom_item_fallback': "Whoever reads this, I'm sorry, but I seem to have #misplaced# {item}.&--Dampé",
        'replace': {
            "visit #your pocket#. I will let you have": "check #your pocket#. You will find",
            "visit #the Temple of Time#": "enter #the Temple of Time#",
            "visit #outside Ganon's Castle#": "visit #the outside of Ganon's Castle#",
            "visit #inside Ganon's Castle#": "#enter Ganon's Castle#",
            "visit #the Deku Tree#": "enter #the Deku Tree#",
            "visit #the Forest Temple#": "enter #the Forest Temple#",
            "visit #Dodongo's Cavern#": "enter #Dodongo's Cavern#",
            "visit #the Fire Temple#": "enter #the Fire Temple#",
            "visit #Jabu Jabu's Belly#": "enter #Jabu Jabu's Belly#",
            "visit #the Ice Cavern#": "enter #the Ice Cavern#",
            "visit #the Water Temple#": "enter #the Water Temple#",
            "visit #the Bottom of the Well#": "enter #the Bottom of the Well#",
            "visit #the Shadow Temple#": "enter #the Shadow Temple#",
            "visit #the Thieves' Hideout#": "enter #the Thieves' Hideout#",
            "visit #the Gerudo Training Ground#": "enter #the Gerudo Training Ground#",
            "visit #the Spirit Temple#": "enter #the Spirit Temple#",
        },
    },
    'ganondorf': {
        'default_item_text': "Ha ha ha... You'll never beat me by reflecting my lightning bolts and unleashing the arrows from {area}!",
        'custom_item_text': "Ha ha ha... You'll never find {item} from {area}!",
        'replace': {
            "from #inside Ganon's Castle#": "from #inside my castle#",
            "from #outside Ganon's Castle#": "from #outside my castle#",
            "from #Ganondorf's Chamber#": "from #those pots over there#",
        },
    },
}

# Location hints (skulltula house, masks, frogs and big poe)
misc_location_hint_table = {
    '10_skulltulas': {
        'location_text': "Yeaaarrgh! I'm cursed!! Please save me by destroying \x05\x4110 Spiders of the Curse\x05\x40 and I will give you \x05\x42{item}\x05\x40.",
        'location_fallback': "Yeaaarrgh! I'm cursed!!",
    },
    '20_skulltulas': {
        'location_text': "Yeaaarrgh! I'm cursed!! Please save me by destroying \x05\x4120 Spiders of the Curse\x05\x40 and I will give you \x05\x42{item}\x05\x40.",
        'location_fallback': "Yeaaarrgh! I'm cursed!!",
    },
    '30_skulltulas': {
        'location_text': "Yeaaarrgh! I'm cursed!! Please save me by destroying \x05\x4130 Spiders of the Curse\x05\x40 and I will give you \x05\x42{item}\x05\x40.",
        'location_fallback': "Yeaaarrgh! I'm cursed!!",
    },
    '40_skulltulas': {
        'location_text': "Yeaaarrgh! I'm cursed!! Please save me by destroying \x05\x4140 Spiders of the Curse\x05\x40 and I will give you \x05\x42{item}\x05\x40.",
        'location_fallback': "Yeaaarrgh! I'm cursed!!",
    },
    '50_skulltulas': {
        'location_text': "Yeaaarrgh! I'm cursed!! Please save me by destroying \x05\x4150 Spiders of the Curse\x05\x40 and I will give you \x05\x42{item}\x05\x40.",
        'location_fallback': "Yeaaarrgh! I'm cursed!!",
    },
    '100_skulltulas': {
        'location_text': "Yeaaarrgh! I'm cursed!! Please save me by destroying \x05\x41100 Spiders of the Curse\x05\x40 and I will give you \x05\x42{item}\x05\x40.",
        'location_fallback': "Yeaaarrgh! I'm cursed!!",
    },
    'frogs2': {
        'location_text': "Some frogs holding \x05\x42{item}\x05\x40 are looking at you from underwater...",
        'location_fallback': "Some frogs are looking at you from underwater...",
    },
    'skull_mask': {
        'location_text': 'Wearing the \x05\x41Skull Mask\x05\x40 will reward you with \x05\x42{item}\x05\x40.',
    },
    'mask_of_truth': {
        'location_text': 'Wearing the \x05\x41Mask of Truth\x05\x40 will reward you with \x05\x42{item}\x05\x40.',
    },
    'big_poes': {
        'location_text': "\x08Hey, young man. What's happening \x01today? Do you want\x01\x05\x41{item}\x05\x40?\x04\x1AIf you earn \x05\x41{poe_points} points\x05\x40, you'll\x01be a happy man! Heh heh.\x04\x08Your card now has \x05\x45\x1E\x01 \x05\x40points.\x01Come back again!\x01Heh heh heh!\x02",
        'location_fallback': "\x08Hey, young man. What's happening \x01today? If you have a \x05\x41Poe\x05\x40, I will \x01buy it.\x04\x1AIf you earn \x05\x41{poe_points} points\x05\x40, you'll\x01be a happy man! Heh heh.\x04\x08Your card now has \x05\x45\x1E\x01 \x05\x40points.\x01Come back again!\x01Heh heh heh!\x02",
    },
}

# Adds capability for dual misc hints. Only used when neither or both hints are enabled, uses corresponding misc_location_hint_table entries if only one is enabled.
# 'location_text' is the text for the dual hint where item_1 is the item from item_location_0 and item_2 is the item from item_location_1.
# 'location_fallback' is the text to handle if neither misc hint is turned on.
misc_dual_hint_table = {
    'skull_mask, mask_of_truth': {
        'location_text': '\x01Wearing the \x05\x41Skull Mask\x05\x40 will reward you with \x05\x42{item_1}\x05\x40.\x04Wearing the \x05\x41Mask of Truth\x05\x40 will reward you with \x05\x42{item_2}\x05\x40.',
        'location_fallback': '\x05\x42\x06\x3dForest Stage\x04\x01\x05\x40\x06\x14We are waiting to see your\x01\x06\x32beautiful face!\x01\x06\x28Win fabulous prizes!',
    },
}

# Separate table for goal names to avoid duplicates in the hint table.
# Link's Pocket will always be an empty goal, but it's included here to
# prevent key errors during the dungeon reward lookup.
BOSS_GOAL_TABLE = {
    'Queen Gohma':                                              {"vague": "path to the #Spider#", "clear": "path to #Queen Gohma#"},
    'King Dodongo':                                             {"vague": "path to the #Dinosaur#", "clear": "path to #King Dodongo#"},
    'Barinade':                                                 {"vague": "path to the #Tentacle#", "clear": "path to #Barinade#"},
    'Phantom Ganon':                                            {"vague": "path to the #Puppet#", "clear": "path to #Phantom Ganon#"},
    'Volvagia':                                                 {"vague": "path to the #Dragon#", "clear": "path to #Volvagia#"},
    'Morpha':                                                   {"vague": "path to the #Amoeba#", "clear": "path to #Morpha#"},
    'Bongo Bongo':                                              {"vague": "path to the #Hands#", "clear": "path to #Bongo Bongo#"},
    'Twinrova':                                                 {"vague": "path to the #Witches#", "clear": "path to #Twinrova#"},
    'ToT Reward from Rauru':                                    {"vague": "path of #time#", "clear": "path of #time#"},
}

# If dungeon rewards are shuffled, we don't use boss names for their goals.
REWARD_GOAL_TABLE = {
    'Kokiri Emerald':                                           {"vague": "path to a #tree's farewell#", "clear": "path to the #Kokiri Emerald#"},
    'Goron Ruby':                                               {"vague": "path to the #Gorons' hidden treasure#", "clear": "path to the #Goron Ruby#"},
    'Zora Sapphire':                                            {"vague": "path to an #engagement ring#", "clear": "path to the #Zora Sapphire#"},
    'Light Medallion':                                          {"vague": "path to #an old man's sagely power#", "clear": "path to the #Light Medallion#"},
    'Forest Medallion':                                         {"vague": "path to #a Kokiri's sagely power#", "clear": "path to the #Forest Medallion#"},
    'Fire Medallion':                                           {"vague": "path to #a Goron's sagely power#", "clear": "path to the #Fire Medallion#"},
    'Water Medallion':                                          {"vague": "path to #a Zora's sagely power#", "clear": "path to the #Water Medallion#"},
    'Shadow Medallion':                                         {"vague": "path to #a Sheikah's sagely power#", "clear": "path to the #Shadow Medallion#"},
    'Spirit Medallion':                                         {"vague": "path to #a Gerudo's sagely power#", "clear": "path to the #Spirit Medallion#"},
}

# Constructing player text for multiplayer, this involves pronoun and verb mapping as well
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

search = "you"

# Extra texts that is included in game (Other than English and Japanese needs these)
# Format: {"id": int, "text": str, "box_type": int}
PLAIN_TEXTS = []

# Per-language character width overrides.
# This is written to property.json and consumed by Language.get_char_widths().
# Keys may be visible characters ("A"), symbolic names ("[C-Up]"), message bytes ("0x9F"),
# or direct table slots ("index:143").  Values may be numbers or {"default": n, "ntsc": n, "pal": n}.
CHAR_WIDTHS = {
    "A":1,
    "I":1,
    "U":1,
    "E":1,
    "O":1,
    "a":1,
    "i":1,
    "u":1,
    "e":1,
    "o":1,
}


# Replace lang_info's string values' characters according to the replace_list
# replace_list: [[old_char, new_char], ...]
replace_list = []

lang_info = {
    'lang_property': lang_property,
    'prefix': prefix,
    'CHAR_WIDTHS': CHAR_WIDTHS,
    'ITEM_MESSAGES': ITEM_MESSAGES,
    "IMPORTANT_ITEM_MESSAGES": IMPORTANT_ITEM_MESSAGES,
    'MISC_MESSAGES': MISC_MESSAGES,
    "PATCH_TEXTS": PATCH_TEXTS,
    "SHOP_TEXTS": SHOP_TEXTS,
    'dungeon_list': dungeon_list,
    'boss_textboxes': boss_textboxes,
    "goal_place_textboxes": goal_place_textboxes,
    'region_list': region_list,
    "hintTable": hintTableFix,
    "hint_text": hint_text,
    "language_specific_replace_table": language_specific_replace_table,
    "trials": trials,
    "hintPrefixes": hintPrefixes,
    "hint_area_enum": hint_area_enum,
    "misc_item_hint_table": misc_item_hint_table,
    "misc_dual_hint_table": misc_dual_hint_table,
    "misc_location_hint_table": misc_location_hint_table,
    "BOSS_GOAL_TABLE": BOSS_GOAL_TABLE,
    "REWARD_GOAL_TABLE": REWARD_GOAL_TABLE,
    "search": search,
    "pronoun_mapping": pronoun_mapping,
    "verb_mapping": verb_mapping,
    "PLAIN_TEXTS": PLAIN_TEXTS,
}


def replace_char_in_dict(d: dict, replace_list: list[list[str, str]]) -> dict:
    """
    Replace lang_info's string values' characters according to the replace_list
    replace_list: [[old_char, new_char], ...]
    """
    if replace_list == []:
        return d

    def replace_in_str(s: str) -> str:
        for old, new in replace_list:
            s = s.replace(old, new)
        return s

    def replace_recursive(obj: Any) -> Any:
        if isinstance(obj, str):
            return replace_in_str(obj)

        if isinstance(obj, dict):
            return {k: replace_recursive(v) for k, v in obj.items()}

        if isinstance(obj, list):
            return [replace_recursive(item) for item in obj]

        return obj

    return replace_recursive(d)

lang_info = replace_char_in_dict(lang_info, replace_list)


json.dump(lang_info, open("data/lang/property.json", mode="w+", encoding='utf-8', newline=''), ensure_ascii=False, indent=4, sort_keys=True)
