from enum import Enum
from typing import List, Dict, Tuple

SCENE_TABLE_ADDRESS = 0x00B71440

# Duplicate of vanilla scene table for non-debug ROM,
# plus additional metadata used for parsing scene files.
# Indexed on scene ID
#
#       |       |                          |                                             |          VROM         |   VROM (Title Card)   |     |     |     |    |
#       | ID    | Filename                 | Description                                 | Start     | End       | Start     | End       | ?   | Rn  | #   | *  |
#       |       |                          |                                             |           |           |           |           |     |     |     |    |
SCENE_TABLE = {
0x0000: (0x0000, "ydan_scene",              "Inside the Deku Tree",                       0x02499000, 0x024A6A10, 0x01994000, 0x01995B00, 0x01, 0x13, 0x02, 0x00 ),
0x0001: (0x0001, "ddan_scene",              "Dodongo's Cavern",                           0x01F12000, 0x01F27140, 0x01998000, 0x01999B00, 0x01, 0x14, 0x03, 0x00 ),
0x0002: (0x0002, "bdan_scene",              "Inside Jabu-Jabu's Belly",                   0x0273E000, 0x027537C0, 0x01996000, 0x01997B00, 0x01, 0x15, 0x04, 0x00 ),
0x0003: (0x0003, "Bmori1_scene",            "Forest Temple",                              0x023CF000, 0x023E4F90, 0x0198A000, 0x0198BB00, 0x02, 0x16, 0x05, 0x00 ),
0x0004: (0x0004, "HIDAN_scene",             "Fire Temple",                                0x022D8000, 0x022F2970, 0x0198E000, 0x0198FB00, 0x02, 0x12, 0x06, 0x00 ),
0x0005: (0x0005, "MIZUsin_scene",           "Water Temple",                               0x025B8000, 0x025CDCF0, 0x01990000, 0x01991B00, 0x01, 0x17, 0x07, 0x00 ),
0x0006: (0x0006, "jyasinzou_scene",         "Spirit Temple",                              0x02ADE000, 0x02AF7B40, 0x01992000, 0x01993B00, 0x01, 0x19, 0x08, 0x00 ),
0x0007: (0x0007, "HAKAdan_scene",           "Shadow Temple",                              0x027A7000, 0x027BF3C0, 0x0198C000, 0x0198DB00, 0x02, 0x18, 0x09, 0x00 ),
0x0008: (0x0008, "HAKAdanCH_scene",         "Bottom of the Well",                         0x032C6000, 0x032D2560, 0x019F4000, 0x019F5B00, 0x02, 0x18, 0x0A, 0x00 ),
0x0009: (0x0009, "ice_doukutu_scene",       "Ice Cavern",                                 0x02BEB000, 0x02BFC610, 0x0199C000, 0x0199DB00, 0x00, 0x25, 0x00, 0x00 ),
0x000A: (0x000A, "ganon_scene",             "Ganon's Tower",                              0x02EE3000, 0x02EF37B0, 0x00000000, 0x00000000, 0x02, 0x00, 0x00, 0x00 ),
0x000B: (0x000B, "men_scene",               "Gerudo Training Ground",                     0x02875000, 0x02886530, 0x0199E000, 0x0199FB00, 0x00, 0x1B, 0x00, 0x00 ),
0x000C: (0x000C, "gerudoway_scene",         "Thieves' Hideout",                           0x03292000, 0x0329F920, 0x019EA000, 0x019EBB00, 0x00, 0x28, 0x00, 0x00 ),
0x000D: (0x000D, "ganontika_scene",         "Inside Ganon's Castle",                      0x0318E000, 0x031AF7C0, 0x0199A000, 0x0199BB00, 0x00, 0x1A, 0x00, 0x00 ),
0x000E: (0x000E, "ganon_sonogo_scene",      "Ganon's Tower (Collapsing)",                 0x033CA000, 0x033D1F10, 0x00000000, 0x00000000, 0x00, 0x33, 0x00, 0x00 ),
0x000F: (0x000F, "ganontikasonogo_scene",   "Inside Ganon's Castle (Collapsing)",         0x0344A000, 0x0344EB00, 0x00000000, 0x00000000, 0x00, 0x34, 0x00, 0x00 ),
0x0010: (0x0010, "takaraya_scene",          "Treasure Box Shop",                          0x033A6000, 0x033AD1B0, 0x019EE000, 0x019EFB00, 0x00, 0x00, 0x00, 0x00 ),
0x0011: (0x0011, "ydan_boss_scene",         "Gohma's Lair",                               0x02EB4000, 0x02EB5740, 0x00000000, 0x00000000, 0x00, 0x1C, 0x00, 0x00 ),
0x0012: (0x0012, "ddan_boss_scene",         "King Dodongo's Lair",                        0x02EA8000, 0x02EAA860, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0013: (0x0013, "bdan_boss_scene",         "Barinade's Lair",                            0x02CB0000, 0x02CB0E40, 0x00000000, 0x00000000, 0x00, 0x15, 0x00, 0x00 ),
0x0014: (0x0014, "moribossroom_scene",      "Phantom Ganon's Lair",                       0x0284A000, 0x0284B900, 0x00000000, 0x00000000, 0x01, 0x00, 0x00, 0x00 ),
0x0015: (0x0015, "FIRE_bs_scene",           "Volvagia's Lair",                            0x02CBB000, 0x02CBFC00, 0x00000000, 0x00000000, 0x00, 0x12, 0x00, 0x00 ),
0x0016: (0x0016, "MIZUsin_bs_scene",        "Morpha's Lair",                              0x02ED0000, 0x02ED1A60, 0x00000000, 0x00000000, 0x00, 0x1D, 0x00, 0x00 ),
0x0017: (0x0017, "jyasinboss_scene",        "Twinrova's Lair & Nabooru's Mini-Boss Room", 0x02F57000, 0x02F5FCF0, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0018: (0x0018, "HAKAdan_bs_scene",        "Bongo Bongo's Lair",                         0x02EC4000, 0x02EC6780, 0x00000000, 0x00000000, 0x00, 0x18, 0x00, 0x00 ),
0x0019: (0x0019, "ganon_boss_scene",        "Ganondorf's Lair",                           0x02F49000, 0x02F50C20, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x001A: (0x001A, "ganon_final_scene",       "Tower Collapse Exterior",                    0x02FE7000, 0x02FF9180, 0x00000000, 0x00000000, 0x00, 0x26, 0x00, 0x00 ),
0x001B: (0x001B, "entra_scene",             "Market Entrance (Child - Day)",              0x02717000, 0x027173E0, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x001C: (0x001C, "entra_n_scene",           "Market Entrance (Child - Night)",            0x029DA000, 0x029DA430, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x001D: (0x001D, "enrui_scene",             "Market Entrance (Ruins)",                    0x02A01000, 0x02A013E0, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x001E: (0x001E, "market_alley_scene",      "Back Alley (Child - Day)",                   0x02944000, 0x02945250, 0x019AC000, 0x019ADB00, 0x00, 0x00, 0x00, 0x00 ),
0x001F: (0x001F, "market_alley_n_scene",    "Back Alley (Child - Night)",                 0x02A28000, 0x02A292F0, 0x019AC000, 0x019ADB00, 0x00, 0x00, 0x00, 0x00 ),
0x0020: (0x0020, "market_day_scene",        "Market (Child - Day)",                       0x022C6000, 0x022C8670, 0x019AA000, 0x019ABB00, 0x00, 0x00, 0x00, 0x00 ),
0x0021: (0x0021, "market_night_scene",      "Market (Child - Night)",                     0x022CF000, 0x022D1630, 0x019AA000, 0x019ABB00, 0x00, 0x00, 0x00, 0x00 ),
0x0022: (0x0022, "market_ruins_scene",      "Market (Ruins)",                             0x029D5000, 0x029D6630, 0x019AA000, 0x019ABB00, 0x00, 0x00, 0x00, 0x00 ),
0x0023: (0x0023, "shrine_scene",            "Temple of Time Exterior (Child - Day)",      0x03075000, 0x030764E0, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0024: (0x0024, "shrine_n_scene",          "Temple of Time Exterior (Child - Night)",    0x030E4000, 0x030E5500, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0025: (0x0025, "shrine_r_scene",          "Temple of Time Exterior (Ruins)",            0x03139000, 0x0313A490, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0026: (0x0026, "kokiri_home_scene",       "Know-It-All Brothers' House",                0x02686000, 0x02686CC0, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0027: (0x0027, "kokiri_home3_scene",      "House of Twins",                             0x02AA5000, 0x02AA67A0, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0028: (0x0028, "kokiri_home4_scene",      "Mido's House",                               0x02F79000, 0x02F7AAB0, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0029: (0x0029, "kokiri_home5_scene",      "Saria's House",                              0x02FB4000, 0x02FB5410, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x002A: (0x002A, "kakariko_scene",          "Carpenter Boss's House",                     0x02C84000, 0x02C84EA0, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x002B: (0x002B, "kakariko3_scene",         "Back Alley House (Man in Green)",            0x03007000, 0x03007840, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x002C: (0x002C, "shop1_scene",             "Bazaar",                                     0x028E3000, 0x028E32F0, 0x019B6000, 0x019B7B00, 0x00, 0x00, 0x00, 0x00 ),
0x002D: (0x002D, "kokiri_shop_scene",       "Kokiri Shop",                                0x02586000, 0x02586980, 0x019AE000, 0x019AFB00, 0x00, 0x00, 0x00, 0x00 ),
0x002E: (0x002E, "golon_scene",             "Goron Shop",                                 0x02D32000, 0x02D323A0, 0x019B0000, 0x019B1B00, 0x00, 0x00, 0x00, 0x00 ),
0x002F: (0x002F, "zoora_scene",             "Zora Shop",                                  0x02D5A000, 0x02D5A390, 0x019B2000, 0x019B3B00, 0x00, 0x00, 0x00, 0x00 ),
0x0030: (0x0030, "drag_scene",              "Kakariko Potion Shop",                       0x02D82000, 0x02D823F0, 0x019B8000, 0x019B9B00, 0x00, 0x00, 0x00, 0x00 ),
0x0031: (0x0031, "alley_shop_scene",        "Market Potion Shop",                         0x02DAF000, 0x02DAF5B0, 0x019B8000, 0x019B9B00, 0x00, 0x00, 0x00, 0x00 ),
0x0032: (0x0032, "night_shop_scene",        "Bombchu Shop",                               0x02DD7000, 0x02DD7670, 0x019F8000, 0x019F9B00, 0x00, 0x00, 0x00, 0x00 ),
0x0033: (0x0033, "face_shop_scene",         "Happy Mask Shop",                            0x03409000, 0x03409370, 0x019EC000, 0x019EDB00, 0x00, 0x00, 0x00, 0x00 ),
0x0034: (0x0034, "link_home_scene",         "Link's House",                               0x0255C000, 0x0255DB60, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0035: (0x0035, "impa_scene",              "Back Alley House (Dog Lady)",                0x02E01000, 0x02E01D10, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0036: (0x0036, "malon_stable_scene",      "Stable",                                     0x02C54000, 0x02C54670, 0x019E8000, 0x019E9B00, 0x00, 0x00, 0x00, 0x00 ),
0x0037: (0x0037, "labo_scene",              "Impa's House",                               0x02E29000, 0x02E29EF0, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0038: (0x0038, "hylia_labo_scene",        "Lakeside Laboratory",                        0x03344000, 0x03355090, 0x019BC000, 0x019BDB00, 0x00, 0x2B, 0x00, 0x00 ),
0x0039: (0x0039, "tent_scene",              "Carpenters' Tent",                           0x02E57000, 0x02E57680, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x003A: (0x003A, "hut_scene",               "Gravekeeper's Hut",                          0x02CCC000, 0x02CCC510, 0x019BA000, 0x019BBB00, 0x00, 0x00, 0x00, 0x00 ),
0x003B: (0x003B, "daiyousei_izumi_scene",   "Great Fairy's Fountain (Upgrades)",          0x02CF7000, 0x02D05000, 0x019A2000, 0x019A3B00, 0x00, 0x21, 0x00, 0x00 ),
0x003C: (0x003C, "yousei_izumi_tate_scene", "Fairy's Fountain",                           0x02D12000, 0x02D1A810, 0x019E2000, 0x019E3B00, 0x00, 0x27, 0x00, 0x00 ),
0x003D: (0x003D, "yousei_izumi_yoko_scene", "Great Fairy's Fountain (Spells)",            0x02D20000, 0x02D2CDA0, 0x019A2000, 0x019A3B00, 0x00, 0x21, 0x00, 0x00 ),
0x003E: (0x003E, "kakusiana_scene",         "Grottos",                                    0x026B3000, 0x026C0820, 0x00000000, 0x00000000, 0x00, 0x1F, 0x00, 0x00 ),
0x003F: (0x003F, "hakaana_scene",           "Grave (Redead)",                             0x02D09000, 0x02D09A90, 0x00000000, 0x00000000, 0x00, 0x30, 0x00, 0x00 ),
0x0040: (0x0040, "hakaana2_scene",          "Grave (Fairy's Fountain)",                   0x0327D000, 0x0328A090, 0x00000000, 0x00000000, 0x00, 0x27, 0x00, 0x00 ),
0x0041: (0x0041, "hakaana_ouke_scene",      "Royal Family's Tomb",                        0x03328000, 0x0332CAE0, 0x019E0000, 0x019E1B00, 0x00, 0x2A, 0x00, 0x00 ),
0x0042: (0x0042, "syatekijyou_scene",       "Shooting Gallery",                           0x02860000, 0x0286C2C0, 0x019A6000, 0x019A7B00, 0x00, 0x22, 0x00, 0x00 ),
0x0043: (0x0043, "tokinoma_scene",          "Temple of Time",                             0x02529000, 0x0253B7A0, 0x019A8000, 0x019A9B00, 0x00, 0x1E, 0x00, 0x00 ),
0x0044: (0x0044, "kenjyanoma_scene",        "Chamber of the Sages",                       0x02511000, 0x025148F0, 0x019A4000, 0x019A5B00, 0x00, 0x20, 0x00, 0x00 ),
0x0045: (0x0045, "hairal_niwa_scene",       "Castle Hedge Maze (Day)",                    0x0290E000, 0x0291F390, 0x019A0000, 0x019A1B00, 0x00, 0x23, 0x00, 0x00 ),
0x0046: (0x0046, "hairal_niwa_n_scene",     "Castle Hedge Maze (Night)",                  0x03304000, 0x0330D0F0, 0x019A0000, 0x019A1B00, 0x00, 0x23, 0x00, 0x00 ),
0x0047: (0x0047, "hiral_demo_scene",        "Cutscene Map",                               0x02AA0000, 0x02AA3D50, 0x00000000, 0x00000000, 0x00, 0x00, 0x00, 0x00 ),
0x0048: (0x0048, "hakasitarelay_scene",     "Dampé's Grave & Windmill",                   0x03033000, 0x03041270, 0x019FA000, 0x019FBB00, 0x00, 0x30, 0x00, 0x00 ),
0x0049: (0x0049, "turibori_scene",          "Fishing Pond",                               0x030CA000, 0x030DC6E0, 0x019E4000, 0x019E5B00, 0x00, 0x32, 0x00, 0x00 ),
0x004A: (0x004A, "nakaniwa_scene",          "Castle Courtyard",                           0x02E8C000, 0x02E8FA20, 0x019A0000, 0x019A1B00, 0x00, 0x2F, 0x00, 0x00 ),
0x004B: (0x004B, "bowling_scene",           "Bombchu Bowling Alley",                      0x03312000, 0x03320B20, 0x019E6000, 0x019E7B00, 0x00, 0x29, 0x00, 0x00 ),
0x004C: (0x004C, "souko_scene",             "Ranch House & Silo",                         0x0335E000, 0x03364C10, 0x00000000, 0x00000000, 0x00, 0x2C, 0x00, 0x00 ),
0x004D: (0x004D, "miharigoya_scene",        "Guard House",                                0x03383000, 0x0338F550, 0x00000000, 0x00000000, 0x00, 0x2D, 0x00, 0x00 ),
0x004E: (0x004E, "mahouya_scene",           "Granny's Potion Shop",                       0x03394000, 0x0339EA20, 0x019B8000, 0x019B9B00, 0x00, 0x2E, 0x00, 0x00 ),
0x004F: (0x004F, "ganon_demo_scene",        "Ganon's Tower Collapse & Battle Arena",      0x033FA000, 0x03403070, 0x00000000, 0x00000000, 0x00, 0x24, 0x00, 0x00 ),
0x0050: (0x0050, "kinsuta_scene",           "House of Skulltula",                         0x03439000, 0x0343A610, 0x019B4000, 0x019B5B00, 0x00, 0x00, 0x00, 0x00 ),
0x0051: (0x0051, "spot00_scene",            "Spot 00 - Hyrule Field",                   0x01FB8000, 0x01FE2220, 0x019BE000, 0x019BFB00, 0x00, 0x01, 0x00, 0x00 ),
0x0052: (0x0052, "spot01_scene",            "Spot 01 - Kakariko Village",               0x01FF9000, 0x02015150, 0x019C0000, 0x019C1B00, 0x00, 0x02, 0x00, 0x00 ),
0x0053: (0x0053, "spot02_scene",            "Spot 02 - Graveyard",                      0x02020000, 0x0202BC80, 0x019C2000, 0x019C3B00, 0x00, 0x00, 0x00, 0x00 ),
0x0054: (0x0054, "spot03_scene",            "Spot 03 - Zora's River",                   0x0204D000, 0x02058560, 0x019C4000, 0x019C5B00, 0x00, 0x03, 0x00, 0x00 ),
0x0055: (0x0055, "spot04_scene",            "Spot 04 - Kokiri Forest",                  0x0206F000, 0x02080240, 0x019C6000, 0x019C7B00, 0x00, 0x04, 0x00, 0x00 ),
0x0056: (0x0056, "spot05_scene",            "Spot 05 - Sacred Forest Meadow",           0x020AC000, 0x020C0D60, 0x019F0000, 0x019F1B00, 0x00, 0x2F, 0x00, 0x00 ),
0x0057: (0x0057, "spot06_scene",            "Spot 06 - Lake Hylia",                     0x020CB000, 0x020E6430, 0x019C8000, 0x019C9B00, 0x00, 0x05, 0x00, 0x00 ),
0x0058: (0x0058, "spot07_scene",            "Spot 07 - Zora's Domain",                  0x020F2000, 0x020FB820, 0x019CA000, 0x019CBB00, 0x00, 0x06, 0x00, 0x00 ),
0x0059: (0x0059, "spot08_scene",            "Spot 08 - Zora's Fountain",                0x02110000, 0x021216A0, 0x019CC000, 0x019CDB00, 0x00, 0x07, 0x00, 0x00 ),
0x005A: (0x005A, "spot09_scene",            "Spot 09 - Gerudo Valley",                  0x0212B000, 0x0213C160, 0x019CE000, 0x019CFB00, 0x00, 0x08, 0x00, 0x00 ),
0x005B: (0x005B, "spot10_scene",            "Spot 10 - Lost Woods",                     0x02146000, 0x02156430, 0x019D0000, 0x019D1B00, 0x00, 0x09, 0x00, 0x00 ),
0x005C: (0x005C, "spot11_scene",            "Spot 11 - Desert Colossus",                0x02186000, 0x0219F4E0, 0x019F6000, 0x019F7B00, 0x00, 0x0A, 0x00, 0x00 ),
0x005D: (0x005D, "spot12_scene",            "Spot 12 - Gerudo's Fortress",              0x021AD000, 0x021BCE80, 0x019F2000, 0x019F3B00, 0x00, 0x0B, 0x00, 0x00 ),
0x005E: (0x005E, "spot13_scene",            "Spot 13 - Haunted Wasteland",              0x021DC000, 0x021E1E30, 0x019D2000, 0x019D3B00, 0x00, 0x0C, 0x00, 0x00 ),
0x005F: (0x005F, "spot15_scene",            "Spot 15 - Hyrule Castle",                  0x021F6000, 0x0220E500, 0x019D4000, 0x019D5B00, 0x00, 0x0D, 0x00, 0x00 ),
0x0060: (0x0060, "spot16_scene",            "Spot 16 - Death Mountain Trail",           0x0221D000, 0x0223BA90, 0x019D6000, 0x019D7B00, 0x00, 0x0E, 0x00, 0x00 ),
0x0061: (0x0061, "spot17_scene",            "Spot 17 - Death Mountain Crater",          0x02247000, 0x02256EE0, 0x019D8000, 0x019D9B00, 0x00, 0x0F, 0x00, 0x00 ),
0x0062: (0x0062, "spot18_scene",            "Spot 18 - Goron City",                     0x02271000, 0x0227B450, 0x019DA000, 0x019DBB00, 0x00, 0x10, 0x00, 0x00 ),
0x0063: (0x0063, "spot20_scene",            "Spot 20 - Lon Lon Ranch",                  0x029BC000, 0x029CDDC0, 0x019DC000, 0x019DDB00, 0x00, 0x11, 0x00, 0x00 ),
0x0064: (0x0064, "ganon_tou_scene",         "Ganon's Castle Exterior",                    0x0292B000, 0x0292FB70, 0x019DE000, 0x019DFB00, 0x00, 0x24, 0x00, 0x00 ),
}


class RecordType(str, Enum):
    # Scene header record types
    SceneHeader = 'SceneHeader'
    AlternateHeaders = 'AlternateHeaders'
    RoomList = 'RoomList'
    TransitionActorList = 'TransitionActorList'
    CollisionHeader = 'CollisionHeader'
    EntranceList = 'EntranceList'
    Points = 'Points'
    PathList = 'PathList'
    SpawnList = 'SpawnList'
    ExitList = 'ExitList'
    LightSettings = 'LightSettings'
    CutsceneData = 'CutsceneData'

    # Collision header record types
    Vertices = 'Vertices'
    Polys = 'Polys'
    SurfaceTypes = 'SurfaceTypes'
    Cams = 'Cams'
    Waterboxes = 'Waterboxes'
    CamPosData = 'CamPosData'

    # Room header record types
    RoomHeader = 'RoomHeader'
    ObjectList = 'ObjectList'
    ActorList = 'ActorList'

    # Mesh header record types
    MeshHeader = 'MeshHeader'
    MeshHeaderImageSingle = 'MeshHeaderImage'
    MeshHeaderImageMulti = 'MeshHeaderImage'
    MeshHeaderCullable = 'MeshHeaderCullable'
    DlistEntries = 'DlistEntries'
    DlistEntry = 'DlistEntry'
    DlistCullableEntries = 'DlistCullableEntries'
    Dlist = 'Dlist'
    Vtx = 'Vtx'
    Mtx = 'Mtx'
    SetTImg = 'SetTImg'
    SetZImg = 'SetZImg'
    SetCImg = 'SetCImg'
    Backgrounds = 'Backgrounds'
    Background = 'Background'
    BackgroundImage = 'BackgroundImage'
    BackgroundTlut = 'BackgroundTlut'
    CullableEntries = 'CullableEntries'
    CullableEntry = 'CullableEntry'
    Cullable = 'Cullable'

    # Other unparsed data blob record types
    Texture = 'Texture'
    TextureAnimation = 'TextureAnimation'
    Symbol = 'Symbol'
    Scalar = 'Scalar'
    Vector = 'Vector'
    Array = 'Array'
    Pointer = 'Pointer'
    Blob = 'Blob'

    # Model-related record types
    Skeleton = 'Skeleton'
    LimbTable = 'LimbTable'
    Limb = 'Limb'
    Animation = 'Animation'
    PlayerAnimation = 'PlayerAnimation'
    PlayerAnimationData = 'PlayerAnimationData'
    CurveAnimation = 'CurveAnimation'
    LegacyAnimation = 'LegacyAnimation'

    # Unknown data not referenced in scene and room files
    Unknown = 'Unknown'

    # Record types referenced by header commands without count
    def has_unknown_count(self) -> bool:
        if self == RecordType.CollisionHeader:  # 0x03
            return True
        if self == RecordType.EntranceList:  # 0x06
            return True
        if self == RecordType.MeshHeader:  # 0x0A
            return True
        if self == RecordType.PathList:  # 0x0D
            return True
        if self == RecordType.ExitList:  # 0x13
            return True
        if self == RecordType.CutsceneData:  # 0x17
            return True
        if self == RecordType.AlternateHeaders:  # 0x18
            return True
        if self == RecordType.SurfaceTypes:
            return True
        if self == RecordType.Cams:
            return True
        if self == RecordType.SetTImg:
            return True
        if self == RecordType.SetZImg:
            return True
        if self == RecordType.SetCImg:
            return True
        return False


# z_demo tables
ENTRANCE_CUTSCENE_TABLE_ADDRESS = 0xB65C64
UNKNOWN_LIST_CUTSCENES = 0xB65D74 # does not include NULL first entry

# z_demo_kekkai list
SAGE_CUTSCENES = 0xECF8EC

# z_scene_table day/night texture list
SCENE_TEXTURE_LIST = 0xB71D4C

# Indexed by scene/room file name
# Data is the vanilla offset from the start of the file and
# a list of every VROM address where the segment address
# for that cutscene is referenced. Some addresses are
# used directly in the code, split into upper and lower
# halves of the full address. These are supplied as tuples
# of the addresses referencing the upper and lower segment
# address halves.

# Tuple data:
#   scene file record type,
#   record offset from file start,
#   data reference addresses,
#   code reference addresses

SCENE_EXTERNAL_REFERENCES: Dict[str, List[Tuple[RecordType, int, List[int], List[Tuple[int, int]]]]] = {
    'bdan_scene': [
        ( RecordType.CutsceneData, 0x155E0, [
            ENTRANCE_CUTSCENE_TABLE_ADDRESS + (17 * 0x8) + 0x4,
            UNKNOWN_LIST_CUTSCENES + 1 * 0x4,
        ], [] ),
    ],
    "Bmori1_scene": [
        ( RecordType.Texture, 0x14D90, [SCENE_TEXTURE_LIST + 26 * 0x4], [] ),
        ( RecordType.Texture, 0x14590, [SCENE_TEXTURE_LIST + 27 * 0x4], [] ),
    ],
    "ddan_boss_room_1": [
        ( RecordType.Texture, 0x021C8, [], [(0xC3BA9A, 0xC3BAA2), (0xC3E61A, 0xC3E626)] ),
    ],
    "ddan_scene": [
        ( RecordType.Texture, 0x12378, [SCENE_TEXTURE_LIST + 2 * 0x4], [] ),
        ( RecordType.Texture, 0x13378, [SCENE_TEXTURE_LIST + 3 * 0x4], [] ),
        ( RecordType.Texture, 0x11F78, [SCENE_TEXTURE_LIST + 4 * 0x4], [] ),
        ( RecordType.Texture, 0x14778, [SCENE_TEXTURE_LIST + 5 * 0x4], [] ),
        ( RecordType.Texture, 0x14378, [SCENE_TEXTURE_LIST + 6 * 0x4], [] ),
        ( RecordType.Texture, 0x13F78, [SCENE_TEXTURE_LIST + 7 * 0x4], [] ),
        ( RecordType.Texture, 0x14B78, [SCENE_TEXTURE_LIST + 8 * 0x4], [] ),
        ( RecordType.Texture, 0x13B78, [SCENE_TEXTURE_LIST + 9 * 0x4], [] ),
        ( RecordType.Texture, 0x12F78, [SCENE_TEXTURE_LIST + 10 * 0x4], [] ),
        ( RecordType.Texture, 0x12B78, [SCENE_TEXTURE_LIST + 11 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x14F80, [UNKNOWN_LIST_CUTSCENES + 2 * 0x4], [(0xC9EDAE, 0xC9EDB2)] ),
    ],
    'ganontika': [
        ( RecordType.CutsceneData, 0x19ED0, [SAGE_CUTSCENES + 6 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x1A8D0, [SAGE_CUTSCENES + 1 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x1B2A0, [SAGE_CUTSCENES + 4 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x1BC70, [SAGE_CUTSCENES + 3 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x1C6A0, [SAGE_CUTSCENES + 2 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x1D070, [SAGE_CUTSCENES + 5 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x1DA40, [UNKNOWN_LIST_CUTSCENES + 5 * 0x4], [(0xACA97E, 0xACA982)] ),
        ( RecordType.CutsceneData, 0x1DF80, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (28 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x1E3D0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (27 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x1E780, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (24 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x1EB30, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (29 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x1EF60, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (25 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x21370, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (26 * 0x8) + 0x4], [] ),
    ],
    "gerudoway_scene": [
        ( RecordType.Texture, 0x0B920, [SCENE_TEXTURE_LIST + 13 * 0x4], [] ),
        ( RecordType.Texture, 0x0BD20, [SCENE_TEXTURE_LIST + 12 * 0x4], [] ),
    ],
    "ice_doukutu_scene": [
        ( RecordType.Texture, 0x0F810, [SCENE_TEXTURE_LIST + 17 * 0x4], [] ),
        ( RecordType.Texture, 0x0FA10, [SCENE_TEXTURE_LIST + 16 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x00250, [UNKNOWN_LIST_CUTSCENES + 4 * 0x4], [(0xC7BD46, 0xC7BD4E)] ),
    ],
    "jyasinboss_scene": [
        ( RecordType.CutsceneData, 0x02BB0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (30 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x03F80, [UNKNOWN_LIST_CUTSCENES + 3 * 0x4], [(0xDED5C2, 0xDED5D6)] ),
    ],
    "jyasinzou_scene": [
        ( RecordType.Texture, 0x18940, [SCENE_TEXTURE_LIST + 28 * 0x4], [] ),
        ( RecordType.Texture, 0x18040, [SCENE_TEXTURE_LIST + 29 * 0x4], [] ),
    ],
    "men_scene": [
        ( RecordType.Texture, 0x0F930, [SCENE_TEXTURE_LIST + 18 * 0x4], [] ),
        ( RecordType.Texture, 0x10130, [SCENE_TEXTURE_LIST + 19 * 0x4], [] ),
    ],
    "MIZUsin_scene": [
        ( RecordType.Texture, 0x14CF0, [SCENE_TEXTURE_LIST + 14 * 0x4], [] ),
        ( RecordType.Texture, 0x158F0, [SCENE_TEXTURE_LIST + 15 * 0x4], [] ),
    ],
    "ydan_scene": [
        ( RecordType.Texture, 0x0BA08, [SCENE_TEXTURE_LIST + 0 * 0x4], [] ),
        ( RecordType.Texture, 0x0CA08, [SCENE_TEXTURE_LIST + 1 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x0B640, [
            ENTRANCE_CUTSCENE_TABLE_ADDRESS + (7 * 0x8) + 0x4,
            UNKNOWN_LIST_CUTSCENES + 0 * 0x4,
        ], [] ),
    ],
    "daiyousei_izumi_scene": [
        ( RecordType.CutsceneData, 0x00130, [], [(0xC89A0A, 0xC89A0E)] ),
        ( RecordType.CutsceneData, 0x013E0, [], [(0xC89A4E, 0xC89A52)] ),
        ( RecordType.CutsceneData, 0x025D0, [], [(0xC89A92, 0xC89A96)] ),
    ],
    "hakasitarelay_scene": [
        ( RecordType.CutsceneData, 0x0E080, [], [(0xE42A4E, 0xE42A5A)] ),
    ],
    "miharigoya_scene": [
        ( RecordType.Texture, 0x01350, [SCENE_TEXTURE_LIST + 25 * 0x4], [] ),
        ( RecordType.Texture, 0x02350, [SCENE_TEXTURE_LIST + 24 * 0x4], [] ),
        ( RecordType.Texture, 0x03550, [SCENE_TEXTURE_LIST + 23 * 0x4], [] ),
        ( RecordType.Texture, 0x06550, [SCENE_TEXTURE_LIST + 22 * 0x4], [] ),
    ],
    "nakaniwa_scene": [
        ( RecordType.CutsceneData, 0x00104, [], [(0xEFE0FA, 0xEFE0FE)] ),
        ( RecordType.CutsceneData, 0x00444, [], [(0xEFE09A, 0xEFE09E)] ),
        ( RecordType.CutsceneData, 0x03994, [], [(0xEFCEF2, 0xEFCEF6)] ),
        ( RecordType.CutsceneData, 0x02524, [], [(0xD12E72, 0xD12E76)] ),
    ],
    "souko_scene": [
        ( RecordType.Texture, 0x05210, [SCENE_TEXTURE_LIST + 20 * 0x4], [] ),
        ( RecordType.Texture, 0x05010, [SCENE_TEXTURE_LIST + 21 * 0x4], [] ),
    ],
    "tokinoma_scene": [
        ( RecordType.CutsceneData, 0x046F0, [], [(0xC8056E, 0xC80572)] ),
        ( RecordType.CutsceneData, 0x06D20, [], [(0xC8060E, 0xC80612)] ),
        ( RecordType.CutsceneData, 0x0CE00, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (6 * 0x8) + 0x4], [] ),
    ],
    "yousei_izumi_yoko_scene": [
        ( RecordType.CutsceneData, 0x00160, [], [(0xC8991A, 0xC8991E)] ),
        ( RecordType.CutsceneData, 0x01020, [], [(0xC8995E, 0xC89962)] ),
        ( RecordType.CutsceneData, 0x01F40, [], [(0xC899A2, 0xC899A6)] ),
    ],
    "hakaana_ouke_scene": [
        ( RecordType.CutsceneData, 0x024A0, [], [(0xE09F6E, 0xE09F72)] ),
        ( RecordType.CutsceneData, 0x028E0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (23 * 0x8) + 0x4], [] ),
    ],
    "ganon_tou_scene": [
        ( RecordType.CutsceneData, 0x02640, [], [(0xE2B502, 0xE2B506)] ),
        ( RecordType.CutsceneData, 0x04280, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (22 * 0x8) + 0x4], [] ),
    ],
    "spot00_scene": [
        ( RecordType.CutsceneData, 0x0BB80, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (12 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x0F870, [], [(0xDB529A, 0xDB529E)] ),
        ( RecordType.CutsceneData, 0x0FF00, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (9 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x13AA0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (0 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x0F9E0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (8 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x10550, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (10 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x10B30, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (11 * 0x8) + 0x4], [] ),
    ],
    "spot00_room_0": [
        ( RecordType.Dlist, 0x12B20, [], [(0xAFC812, 0xAFC816)] ),
    ],
    "spot01_scene": [
        ( RecordType.Texture, 0x15B50, [SCENE_TEXTURE_LIST + 30 * 0x4], [] ),
        ( RecordType.Texture, 0x16B50, [SCENE_TEXTURE_LIST + 31 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x0A540, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (2 * 0x8) + 0x4], [] ),
    ],
    "spot02_scene": [
        ( RecordType.CutsceneData, 0x03C80, [], [(0xE09D42, 0xE09D46)] ),
        ( RecordType.CutsceneData, 0x05020, [], [(0xE09D32, 0xE09D36)] ),
        ( RecordType.CutsceneData, 0x070C0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (18 * 0x8) + 0x4], [] ),
    ],
    "spot04_scene": [
        ( RecordType.CutsceneData, 0xC9D0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (33 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x10E20, [], [(0xE297AE, 0xE297B6)] ),
    ],
    "spot06_scene": [
        ( RecordType.CutsceneData, 0x07020, [], [(0xE9E222, 0xE9E226)] ),
        ( RecordType.CutsceneData, 0x07A30, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (13 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x1B0C0, [], [(0xE31302, 0xE31306)] ),
    ],
    "spot07_scene": [
        ( RecordType.Texture, 0x08F98, [SCENE_TEXTURE_LIST + 32 * 0x4], [] ),
        ( RecordType.Texture, 0x08FD8, [SCENE_TEXTURE_LIST + 33 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x03D70, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (3 * 0x8) + 0x4], [] ),
    ],
    "spot08_scene": [
        ( RecordType.CutsceneData, 0x04A80, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (19 * 0x8) + 0x4], [] ),
    ],
    "spot09_scene": [
        ( RecordType.CutsceneData, 0x02AC0, [], [(0xC1CCC6, 0xC1CCCA)] ),
        ( RecordType.CutsceneData, 0x00230, [], [(0xC1CD12, 0xC1CD16)] ),
        ( RecordType.CutsceneData, 0x031E0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (14 * 0x8) + 0x4], [] ),
    ],
    "spot11_scene": [
        ( RecordType.CutsceneData, 0x07990, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (20 * 0x8) + 0x4], [] ),
    ],
    "spot12_scene": [
        ( RecordType.Texture, 0x09678, [SCENE_TEXTURE_LIST + 34 * 0x4], [] ),
        ( RecordType.Texture, 0x0DE78, [SCENE_TEXTURE_LIST + 35 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x055C0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (31 * 0x8) + 0x4], [] ),
        ( RecordType.CutsceneData, 0x06490, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (15 * 0x8) + 0x4], [] ),
    ],
    "spot15_scene": [
        ( RecordType.CutsceneData, 0x03F40, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (4 * 0x8) + 0x4], [] ),
    ],
    "spot16_scene": [
        ( RecordType.CutsceneData, 0x1E6A0, [], [(0xE31342, 0xE31346)] ),
        ( RecordType.CutsceneData, 0x07EA0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (1 * 0x8) + 0x4], [] ),
    ],
    "spot16_room_0": [
        ( RecordType.Dlist, 0x0A9C8, [], [(0xAFDF2E, 0xAFDF32)] ),
    ],
    "spot17_scene": [
        ( RecordType.CutsceneData, 0x045D0, [], [(0xC7BBFE, 0xC7BC02)] ),
        ( RecordType.CutsceneData, 0x076D0, [
            ENTRANCE_CUTSCENE_TABLE_ADDRESS + (21 * 0x8) + 0x4,
            ENTRANCE_CUTSCENE_TABLE_ADDRESS + (32 * 0x8) + 0x4,
        ], [] ),
    ],
    "spot18_scene": [
        ( RecordType.Texture, 0x08FC8, [SCENE_TEXTURE_LIST + 37 * 0x4], [] ),
        ( RecordType.Texture, 0x09808, [SCENE_TEXTURE_LIST + 36 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x059E0, [], [(0xCF14DA, 0xCF14DE)] ),
        ( RecordType.CutsceneData, 0x06930, [], [(0xCF11C6, 0xCF11D6)] ),
        ( RecordType.CutsceneData, 0x07DE0, [], [(0xCF1436, 0xCF143A)] ),
        ( RecordType.CutsceneData, 0x08400, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (5 * 0x8) + 0x4], [] ),
    ],
    "spot20_scene": [
        ( RecordType.Texture, 0x08180, [SCENE_TEXTURE_LIST + 38 * 0x4], [] ),
        ( RecordType.Texture, 0x0FB80, [SCENE_TEXTURE_LIST + 39 * 0x4], [] ),
        ( RecordType.CutsceneData, 0x05B70, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (16 * 0x8) + 0x4], [] ),
    ],
}
