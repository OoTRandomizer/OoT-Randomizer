from __future__ import annotations
from enum import IntEnum
from typing import Optional, Any

class GetItemId(IntEnum):
    GI_NONE = 0x0000
    GI_BOMBS_5 = 0x0001
    GI_DEKU_NUTS_5 = 0x0002
    GI_BOMBCHUS_10 = 0x0003
    GI_BOW = 0x0004
    GI_SLINGSHOT = 0x0005
    GI_BOOMERANG = 0x0006
    GI_DEKU_STICKS_1 = 0x0007
    GI_HOOKSHOT = 0x0008
    GI_LONGSHOT = 0x0009
    GI_LENS_OF_TRUTH = 0x000A
    GI_ZELDAS_LETTER = 0x000B
    GI_OCARINA_OF_TIME = 0x000C
    GI_HAMMER = 0x000D
    GI_COJIRO = 0x000E
    GI_BOTTLE_EMPTY = 0x000F
    GI_BOTTLE_POTION_RED = 0x0010
    GI_BOTTLE_POTION_GREEN = 0x0011
    GI_BOTTLE_POTION_BLUE = 0x0012
    GI_BOTTLE_FAIRY = 0x0013
    GI_BOTTLE_MILK_FULL = 0x0014
    GI_BOTTLE_RUTOS_LETTER = 0x0015
    GI_MAGIC_BEAN = 0x0016
    GI_MASK_SKULL = 0x0017
    GI_MASK_SPOOKY = 0x0018
    GI_CHICKEN = 0x0019
    GI_MASK_KEATON = 0x001A
    GI_MASK_BUNNY_HOOD = 0x001B
    GI_MASK_TRUTH = 0x001C
    GI_POCKET_EGG = 0x001D
    GI_POCKET_CUCCO = 0x001E
    GI_ODD_MUSHROOM = 0x001F
    GI_ODD_POTION = 0x0020
    GI_POACHERS_SAW = 0x0021
    GI_BROKEN_GORONS_SWORD = 0x0022
    GI_PRESCRIPTION = 0x0023
    GI_EYEBALL_FROG = 0x0024
    GI_EYE_DROPS = 0x0025
    GI_CLAIM_CHECK = 0x0026
    GI_SWORD_KOKIRI = 0x0027
    GI_SWORD_KNIFE = 0x0028
    GI_SHIELD_DEKU = 0x0029
    GI_SHIELD_HYLIAN = 0x002A
    GI_SHIELD_MIRROR = 0x002B
    GI_TUNIC_GORON = 0x002C
    GI_TUNIC_ZORA = 0x002D
    GI_BOOTS_IRON = 0x002E
    GI_BOOTS_HOVER = 0x002F
    GI_QUIVER_40 = 0x0030
    GI_QUIVER_50 = 0x0031
    GI_BOMB_BAG_20 = 0x0032
    GI_BOMB_BAG_30 = 0x0033
    GI_BOMB_BAG_40 = 0x0034
    GI_SILVER_GAUNTLETS = 0x0035
    GI_GOLD_GAUNTLETS = 0x0036
    GI_SCALE_SILVER = 0x0037
    GI_SCALE_GOLDEN = 0x0038
    GI_STONE_OF_AGONY = 0x0039
    GI_GERUDOS_CARD = 0x003A
    GI_OCARINA_FAIRY = 0x003B
    GI_DEKU_SEEDS_5 = 0x003C
    GI_HEART_CONTAINER = 0x003D
    GI_HEART_PIECE = 0x003E
    GI_BOSS_KEY = 0x003F
    GI_COMPASS = 0x0040
    GI_DUNGEON_MAP = 0x0041
    GI_SMALL_KEY = 0x0042
    GI_MAGIC_JAR_SMALL = 0x0043
    GI_MAGIC_JAR_LARGE = 0x0044
    GI_WALLET_ADULT = 0x0045
    GI_WALLET_GIANT = 0x0046
    GI_WEIRD_EGG = 0x0047
    GI_RECOVERY_HEART = 0x0048
    GI_ARROWS_5 = 0x0049
    GI_ARROWS_10 = 0x004A
    GI_ARROWS_30 = 0x004B
    GI_RUPEE_GREEN = 0x004C
    GI_RUPEE_BLUE = 0x004D
    GI_RUPEE_RED = 0x004E
    GI_HEART_CONTAINER_2 = 0x004F
    GI_MILK = 0x0050
    GI_MASK_GORON = 0x0051
    GI_MASK_ZORA = 0x0052
    GI_MASK_GERUDO = 0x0053
    GI_GORONS_BRACELET = 0x0054
    GI_RUPEE_PURPLE = 0x0055
    GI_RUPEE_GOLD = 0x0056
    GI_SWORD_BIGGORON = 0x0057
    GI_ARROW_FIRE = 0x0058
    GI_ARROW_ICE = 0x0059
    GI_ARROW_LIGHT = 0x005A
    GI_SKULL_TOKEN = 0x005B
    GI_DINS_FIRE = 0x005C
    GI_FARORES_WIND = 0x005D
    GI_NAYRUS_LOVE = 0x005E
    GI_BULLET_BAG_30 = 0x005F
    GI_BULLET_BAG_40 = 0x0060
    GI_DEKU_STICKS_5 = 0x0061
    GI_DEKU_STICKS_10 = 0x0062
    GI_DEKU_NUTS_5_2 = 0x0063
    GI_DEKU_NUTS_10 = 0x0064
    GI_BOMBS_1 = 0x0065
    GI_BOMBS_10 = 0x0066
    GI_BOMBS_20 = 0x0067
    GI_BOMBS_30 = 0x0068
    GI_DEKU_SEEDS_30 = 0x0069
    GI_BOMBCHUS_5 = 0x006A
    GI_BOMBCHUS_20 = 0x006B
    GI_BOTTLE_FISH = 0x006C
    GI_BOTTLE_BUGS = 0x006D
    GI_BOTTLE_BLUE_FIRE = 0x006E
    GI_BOTTLE_POE = 0x006F
    GI_BOTTLE_BIG_POE = 0x0070
    GI_DOOR_KEY = 0x0071
    GI_RUPEE_GREEN_LOSE = 0x0072
    GI_RUPEE_BLUE_LOSE = 0x0073
    GI_RUPEE_RED_LOSE = 0x0074
    GI_RUPEE_PURPLE_LOSE = 0x0075
    GI_HEART_PIECE_WIN = 0x0076
    GI_DEKU_STICK_UPGRADE_20 = 0x0077
    GI_DEKU_STICK_UPGRADE_30 = 0x0078
    GI_DEKU_NUT_UPGRADE_30 = 0x0079
    GI_DEKU_NUT_UPGRADE_40 = 0x007A
    GI_BULLET_BAG_50 = 0x007B
    GI_ICE_TRAP = 0x007C
    GI_TEXT_0 = 0x007D
    GI_CAPPED_PIECE_OF_HEART = 0x007D
    GI_VANILLA_MAX = 0x007E
    GI_CAPPED_HEART_CONTAINER = 0x007E

    GI_CAPPED_PIECE_OF_HEART_CHESTGAME = 0x007F

    GI_PROGRESSIVE_HOOKSHOT = 0x0080
    GI_PROGRESSIVE_STRENGTH = 0x0081
    GI_PROGRESSIVE_BOMB_BAG = 0x0082
    GI_PROGRESSIVE_BOW = 0x0083
    GI_PROGRESSIVE_SLINGSHOT = 0x0084
    GI_PROGRESSIVE_WALLET = 0x0085
    GI_PROGRESSIVE_SCALE = 0x0086
    GI_PROGRESSIVE_NUT_CAPACITY = 0x0087
    GI_PROGRESSIVE_STICK_CAPACITY = 0x0088
    GI_PROGRESSIVE_BOMBCHUS = 0x0089
    GI_PROGRESSIVE_MAGIC_METER = 0x008A
    GI_PROGRESSIVE_OCARINA = 0x008B

    GI_BOTTLE_WITH_RED_POTION = 0x008C
    GI_BOTTLE_WITH_GREEN_POTION = 0x008D
    GI_BOTTLE_WITH_BLUE_POTION = 0x008E
    GI_BOTTLE_WITH_FAIRY = 0x008F
    GI_BOTTLE_WITH_FISH = 0x0090
    GI_BOTTLE_WITH_BLUE_FIRE = 0x0091
    GI_BOTTLE_WITH_BUGS = 0x0092
    GI_BOTTLE_WITH_BIG_POE = 0x0093
    GI_BOTTLE_WITH_POE = 0x0094

    GI_BOSS_KEY_FOREST_TEMPLE = 0x0095
    GI_BOSS_KEY_FIRE_TEMPLE = 0x0096
    GI_BOSS_KEY_WATER_TEMPLE = 0x0097
    GI_BOSS_KEY_SPIRIT_TEMPLE = 0x0098
    GI_BOSS_KEY_SHADOW_TEMPLE = 0x0099
    GI_BOSS_KEY_GANONS_CASTLE = 0x009A

    GI_COMPASS_DEKU_TREE = 0x009B
    GI_COMPASS_DODONGOS_CAVERN = 0x009C
    GI_COMPASS_JABU_JABU = 0x009D
    GI_COMPASS_FOREST_TEMPLE = 0x009E
    GI_COMPASS_FIRE_TEMPLE = 0x009F
    GI_COMPASS_WATER_TEMPLE = 0x00A0
    GI_COMPASS_SPIRIT_TEMPLE = 0x00A1
    GI_COMPASS_SHADOW_TEMPLE = 0x00A2
    GI_COMPASS_BOTTOM_OF_THE_WELL = 0x00A3
    GI_COMPASS_ICE_CAVERN = 0x00A4

    GI_MAP_DEKU_TREE = 0x00A5
    GI_MAP_DODONGOS_CAVERN = 0x00A6
    GI_MAP_JABU_JABU = 0x00A7
    GI_MAP_FOREST_TEMPLE = 0x00A8
    GI_MAP_FIRE_TEMPLE = 0x00A9
    GI_MAP_WATER_TEMPLE = 0x00AA
    GI_MAP_SPIRIT_TEMPLE = 0x00AB
    GI_MAP_SHADOW_TEMPLE = 0x00AC
    GI_MAP_BOTTOM_OF_THE_WELL = 0x00AD
    GI_MAP_ICE_CAVERN = 0x00AE

    GI_SMALL_KEY_FOREST_TEMPLE = 0x00AF
    GI_SMALL_KEY_FIRE_TEMPLE = 0x00B0
    GI_SMALL_KEY_WATER_TEMPLE = 0x00B1
    GI_SMALL_KEY_SPIRIT_TEMPLE = 0x00B2
    GI_SMALL_KEY_SHADOW_TEMPLE = 0x00B3
    GI_SMALL_KEY_BOTTOM_OF_THE_WELL = 0x00B4
    GI_SMALL_KEY_GERUDO_TRAINING = 0x00B5
    GI_SMALL_KEY_THIEVES_HIDEOUT = 0x00B6
    GI_SMALL_KEY_GANONS_CASTLE = 0x00B7

    GI_DOUBLE_DEFENSE = 0x00B8
    GI_MAGIC_METER = 0x00B9
    GI_DOUBLE_MAGIC = 0x00BA

    GI_MINUET_OF_FOREST = 0x00BB
    GI_BOLERO_OF_FIRE = 0x00BC
    GI_SERENADE_OF_WATER = 0x00BD
    GI_REQUIEM_OF_SPIRIT = 0x00BE
    GI_NOCTURNE_OF_SHADOW = 0x00BF
    GI_PRELUDE_OF_LIGHT = 0x00C0

    GI_ZELDAS_LULLABY = 0x00C1
    GI_EPONAS_SONG = 0x00C2
    GI_SARIAS_SONG = 0x00C3
    GI_SUNS_SONG = 0x00C4
    GI_SONG_OF_TIME = 0x00C5
    GI_SONG_OF_STORMS = 0x00C6

    GI_TYCOONS_WALLET = 0x00C7
    GI_REDUNDANT_LETTER_BOTTLE = 0x00C8
    GI_MAGIC_BEAN_PACK = 0x00C9
    GI_TRIFORCE_PIECE = 0x00CA

    GI_SMALL_KEY_RING_FOREST_TEMPLE = 0x00CB
    GI_SMALL_KEY_RING_FIRE_TEMPLE = 0x00CC
    GI_SMALL_KEY_RING_WATER_TEMPLE = 0x00CD
    GI_SMALL_KEY_RING_SPIRIT_TEMPLE = 0x00CE
    GI_SMALL_KEY_RING_SHADOW_TEMPLE = 0x00CF
    GI_SMALL_KEY_RING_BOTTOM_OF_THE_WELL = 0x00D0
    GI_SMALL_KEY_RING_GERUDO_TRAINING = 0x00D1
    GI_SMALL_KEY_RING_THIEVES_HIDEOUT = 0x00D2
    GI_SMALL_KEY_RING_GANONS_CASTLE = 0x00D3

    GI_BOMBCHU_BAG_20 = 0x00D4
    GI_BOMBCHU_BAG_10 = 0x00D5
    GI_BOMBCHU_BAG_5 = 0x00D6

    GI_SMALL_KEY_RING_TREASURE_CHEST_GAME = 0x00D7

    GI_SILVER_RUPEE_DODONGOS_CAVERN_STAIRCASE = 0x00D8
    GI_SILVER_RUPEE_ICE_CAVERN_SPINNING_SCYTHE = 0x00D9
    GI_SILVER_RUPEE_ICE_CAVERN_PUSH_BLOCK = 0x00DA
    GI_SILVER_RUPEE_BOTTOM_OF_THE_WELL_BASEMENT = 0x00DB
    GI_SILVER_RUPEE_SHADOW_TEMPLE_SCYTHE_SHORTCUT = 0x00DC
    GI_SILVER_RUPEE_SHADOW_TEMPLE_INVISIBLE_BLADES = 0x00DD
    GI_SILVER_RUPEE_SHADOW_TEMPLE_HUGE_PIT = 0x00DE
    GI_SILVER_RUPEE_SHADOW_TEMPLE_INVISIBLE_SPIKES = 0x00DF
    GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_SLOPES = 0x00E0
    GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_LAVA = 0x00E1
    GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_WATER = 0x00E2
    GI_SILVER_RUPEE_SPIRIT_TEMPLE_CHILD_EARLY_TORCHES = 0x00E3
    GI_SILVER_RUPEE_SPIRIT_TEMPLE_ADULT_BOULDERS = 0x00E4
    GI_SILVER_RUPEE_SPIRIT_TEMPLE_LOBBY_AND_LOWER_ADULT = 0x00E5
    GI_SILVER_RUPEE_SPIRIT_TEMPLE_SUN_BLOCK = 0x00E6
    GI_SILVER_RUPEE_SPIRIT_TEMPLE_ADULT_CLIMB = 0x00E7
    GI_SILVER_RUPEE_GANONS_CASTLE_SPIRIT_TRIAL = 0x00E8
    GI_SILVER_RUPEE_GANONS_CASTLE_LIGHT_TRIAL = 0x00E9
    GI_SILVER_RUPEE_GANONS_CASTLE_FIRE_TRIAL = 0x00EA
    GI_SILVER_RUPEE_GANONS_CASTLE_SHADOW_TRIAL = 0x00EB
    GI_SILVER_RUPEE_GANONS_CASTLE_WATER_TRIAL = 0x00EC
    GI_SILVER_RUPEE_GANONS_CASTLE_FOREST_TRIAL = 0x00ED

    GI_SILVER_RUPEE_POUCH_DODONGOS_CAVERN_STAIRCASE = 0x00EE
    GI_SILVER_RUPEE_POUCH_ICE_CAVERN_SPINNING_SCYTHE = 0x00EF
    GI_SILVER_RUPEE_POUCH_ICE_CAVERN_PUSH_BLOCK = 0x00F0
    GI_SILVER_RUPEE_POUCH_BOTTOM_OF_THE_WELL_BASEMENT = 0x00F1
    GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_SCYTHE_SHORTCUT = 0x00F2
    GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_INVISIBLE_BLADES = 0x00F3
    GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_HUGE_PIT = 0x00F4
    GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_INVISIBLE_SPIKES = 0x00F5
    GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_SLOPES = 0x00F6
    GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_LAVA = 0x00F7
    GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_WATER = 0x00F8
    GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_CHILD_EARLY_TORCHES = 0x00F9
    GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_ADULT_BOULDERS = 0x00FA
    GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_LOBBY_AND_LOWER_ADULT = 0x00FB
    GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_SUN_BLOCK = 0x00FC
    GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_ADULT_CLIMB = 0x00FD
    GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_SPIRIT_TRIAL = 0x00FE
    GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_LIGHT_TRIAL = 0x00FF
    GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_FIRE_TRIAL = 0x0100
    GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_SHADOW_TRIAL = 0x0101
    GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_WATER_TRIAL = 0x0102
    GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_FOREST_TRIAL = 0x0103

    # Ocarina button models
    GI_OCARINA_BUTTON_A = 0x0104
    GI_OCARINA_BUTTON_C_UP = 0x0105
    GI_OCARINA_BUTTON_C_DOWN = 0x0106
    GI_OCARINA_BUTTON_C_LEFT = 0x0107
    GI_OCARINA_BUTTON_C_RIGHT = 0x0108

    # Custom Key Models
    GI_BOSS_KEY_MODEL_FOREST_TEMPLE = 0x0109
    GI_BOSS_KEY_MODEL_FIRE_TEMPLE = 0x010A
    GI_BOSS_KEY_MODEL_WATER_TEMPLE = 0x010B
    GI_BOSS_KEY_MODEL_SPIRIT_TEMPLE = 0x010C
    GI_BOSS_KEY_MODEL_SHADOW_TEMPLE = 0x010D
    GI_BOSS_KEY_MODEL_GANONS_CASTLE = 0x010E
    GI_SMALL_KEY_MODEL_FOREST_TEMPLE = 0x010F
    GI_SMALL_KEY_MODEL_FIRE_TEMPLE = 0x0110
    GI_SMALL_KEY_MODEL_WATER_TEMPLE = 0x0111
    GI_SMALL_KEY_MODEL_SPIRIT_TEMPLE = 0x0112
    GI_SMALL_KEY_MODEL_SHADOW_TEMPLE = 0x0113
    GI_SMALL_KEY_MODEL_BOTTOM_OF_THE_WELL = 0x0114
    GI_SMALL_KEY_MODEL_GERUDO_TRAINING = 0x0115
    GI_SMALL_KEY_MODEL_THIEVES_HIDEOUT = 0x0116
    GI_SMALL_KEY_MODEL_GANONS_CASTLE = 0x0117
    GI_SMALL_KEY_MODEL_CHEST_GAME = 0x0118

    GI_FAIRY = 0x0119
    GI_NOTHING = 0x011A

    GI_KOKIRI_EMERALD = 0x0127
    GI_GORON_RUBY = 0x0128
    GI_ZORA_SAPPHIRE = 0x0129
    GI_LIGHT_MEDALLION = 0x012A
    GI_FOREST_MEDALLION = 0x012B
    GI_FIRE_MEDALLION = 0x012C
    GI_WATER_MEDALLION = 0x012D
    GI_SHADOW_MEDALLION = 0x012E
    GI_SPIRIT_MEDALLION = 0x012F

    GI_RANDO_MAX = 0x0130

# Progressive: True  -> Advancement
#              False -> Priority
#              None  -> Normal
#    Item:                                            (type, Progressive, GetItemID, special),
#
# special "upgrade_ids" correspond to the item IDs in item_table.c for all of the upgrade tiers
# of that item.
#
item_table: dict[str, tuple[str, Optional[bool], Optional[int], Optional[dict[str, Any]]]] = {
    'Bombs (5)':                                       ('Item',     None,  GetItemId.GI_BOMBS_5, {'junk': 8}),
    'Deku Nuts (5)':                                   ('Item',     None,  GetItemId.GI_DEKU_NUTS_5, {'junk': 5}),
    'Bombchus (10)':                                   ('Item',     True,  GetItemId.GI_BOMBCHUS_10, None),
    'Boomerang':                                       ('Item',     True,  GetItemId.GI_BOOMERANG, None),
    'Deku Stick (1)':                                  ('Item',     None,  GetItemId.GI_DEKU_STICKS_1, {'junk': 5}),
    'Lens of Truth':                                   ('Item',     True,  GetItemId.GI_LENS_OF_TRUTH, None),
    'Megaton Hammer':                                  ('Item',     True,  GetItemId.GI_HAMMER, None),
    'Cojiro':                                          ('Item',     True,  GetItemId.GI_COJIRO, {'trade': True}),
    'Bottle':                                          ('Item',     True,  GetItemId.GI_BOTTLE_EMPTY, {'bottle': float('Inf')}),
    'Blue Potion':                                     ('Item',     True,  GetItemId.GI_BOTTLE_POTION_BLUE, None), # distinct from shop item
    'Bottle with Milk':                                ('Item',     True,  GetItemId.GI_BOTTLE_MILK_FULL, {'bottle': float('Inf')}),
    'Rutos Letter':                                    ('Item',     True,  GetItemId.GI_BOTTLE_RUTOS_LETTER, None),
    'Deliver Letter':                                  ('Item',     True,  None,   {'bottle': float('Inf')}),
    'Sell Big Poe':                                    ('Item',     True,  None,   {'bottle': float('Inf')}),
    'Magic Bean':                                      ('Item',     True,  GetItemId.GI_MAGIC_BEAN, {'progressive': 10}),
    'Skull Mask':                                      ('Item',     True,  GetItemId.GI_MASK_SKULL, {'trade': True, 'object': 0x0136}),
    'Spooky Mask':                                     ('Item',     True,  GetItemId.GI_MASK_SPOOKY, {'trade': True, 'object': 0x0135}),
    'Chicken':                                         ('Item',     True,  GetItemId.GI_CHICKEN, {'trade': True}),
    'Keaton Mask':                                     ('Item',     True,  GetItemId.GI_MASK_KEATON, {'trade': True, 'object': 0x0134}),
    'Bunny Hood':                                      ('Item',     True,  GetItemId.GI_MASK_BUNNY_HOOD, {'trade': True, 'object': 0x0137}),
    'Mask of Truth':                                   ('Item',     True,  GetItemId.GI_MASK_TRUTH, {'trade': True, 'object': 0x0138}),
    'Pocket Egg':                                      ('Item',     True,  GetItemId.GI_POCKET_EGG, {'trade': True}),
    'Pocket Cucco':                                    ('Item',     True,  GetItemId.GI_POCKET_CUCCO, {'trade': True}),
    'Odd Mushroom':                                    ('Item',     True,  GetItemId.GI_ODD_MUSHROOM, {'trade': True}),
    'Odd Potion':                                      ('Item',     True,  GetItemId.GI_ODD_POTION, {'trade': True}),
    'Poachers Saw':                                    ('Item',     True,  GetItemId.GI_POACHERS_SAW, {'trade': True}),
    'Broken Sword':                                    ('Item',     True,  GetItemId.GI_BROKEN_GORONS_SWORD, {'trade': True}),
    'Prescription':                                    ('Item',     True,  GetItemId.GI_PRESCRIPTION, {'trade': True}),
    'Eyeball Frog':                                    ('Item',     True,  GetItemId.GI_EYEBALL_FROG, {'trade': True}),
    'Eyedrops':                                        ('Item',     True,  GetItemId.GI_EYE_DROPS, {'trade': True}),
    'Claim Check':                                     ('Item',     True,  GetItemId.GI_CLAIM_CHECK, {'trade': True}),
    'Kokiri Sword':                                    ('Item',     True,  GetItemId.GI_SWORD_KOKIRI, None),
    'Giants Knife':                                    ('Item',     None,  GetItemId.GI_SWORD_KNIFE, None),
    'Deku Shield':                                     ('Item',     None,  GetItemId.GI_SHIELD_DEKU, None),
    'Hylian Shield':                                   ('Item',     None,  GetItemId.GI_SHIELD_HYLIAN, None),
    'Mirror Shield':                                   ('Item',     True,  GetItemId.GI_SHIELD_MIRROR, None),
    'Goron Tunic':                                     ('Item',     True,  GetItemId.GI_TUNIC_GORON, None),
    'Zora Tunic':                                      ('Item',     True,  GetItemId.GI_TUNIC_ZORA, None),
    'Iron Boots':                                      ('Item',     True,  GetItemId.GI_BOOTS_IRON, None),
    'Hover Boots':                                     ('Item',     True,  GetItemId.GI_BOOTS_HOVER, None),
    'Stone of Agony':                                  ('Item',     True,  GetItemId.GI_STONE_OF_AGONY, None),
    'Gerudo Membership Card':                          ('Item',     True,  GetItemId.GI_GERUDOS_CARD, None),
    'Heart Container':                                 ('Item',     True,  GetItemId.GI_HEART_CONTAINER, {'alias': ('Piece of Heart', 4), 'progressive': float('Inf')}),
    'Piece of Heart':                                  ('Item',     True,  GetItemId.GI_HEART_PIECE, {'progressive': float('Inf')}),
    'Piece of Heart (Out of Logic)':                   ('Item',     None,  GetItemId.GI_HEART_PIECE, None),
    'Boss Key':                                        ('BossKey',  True,  GetItemId.GI_BOSS_KEY, None),
    'Compass':                                         ('Compass',  None,  GetItemId.GI_COMPASS, None),
    'Map':                                             ('Map',      None,  GetItemId.GI_DUNGEON_MAP, None),
    'Small Key':                                       ('SmallKey', True,  GetItemId.GI_SMALL_KEY, {'progressive': float('Inf')}),
    'Weird Egg':                                       ('Item',     True,  GetItemId.GI_WEIRD_EGG, {'trade': True}),
    'Recovery Heart':                                  ('Item',     None,  GetItemId.GI_RECOVERY_HEART, {'junk': 0}),
    'Arrows (5)':                                      ('Item',     None,  GetItemId.GI_ARROWS_5, {'junk': 8}),
    'Arrows (10)':                                     ('Item',     None,  GetItemId.GI_ARROWS_10, {'junk': 2}),
    'Arrows (30)':                                     ('Item',     None,  GetItemId.GI_ARROWS_30, {'junk': 0}),
    'Rupee (1)':                                       ('Item',     None,  GetItemId.GI_RUPEE_GREEN, {'junk': -1}),
    'Rupees (5)':                                      ('Item',     None,  GetItemId.GI_RUPEE_BLUE, {'junk': 10}),
    'Rupees (20)':                                     ('Item',     None,  GetItemId.GI_RUPEE_RED, {'junk': 4}),
    'Milk':                                            ('Item',     None,  GetItemId.GI_MILK, None),
    'Goron Mask':                                      ('Item',     None,  GetItemId.GI_MASK_GORON, {'trade': True, 'object': 0x0150}),
    'Zora Mask':                                       ('Item',     None,  GetItemId.GI_MASK_ZORA, {'trade': True, 'object': 0x0151}),
    'Gerudo Mask':                                     ('Item',     None,  GetItemId.GI_MASK_GERUDO, {'trade': True, 'object': 0x0152}),
    'Rupees (50)':                                     ('Item',     None,  GetItemId.GI_RUPEE_PURPLE, {'junk': 1}),
    'Rupees (200)':                                    ('Item',     None,  GetItemId.GI_RUPEE_GOLD, {'junk': 0}),
    'Biggoron Sword':                                  ('Item',     None,  GetItemId.GI_SWORD_BIGGORON, None),
    'Fire Arrows':                                     ('Item',     True,  GetItemId.GI_ARROW_FIRE, None),
    'Ice Arrows':                                      ('Item',     True,  GetItemId.GI_ARROW_ICE, None),
    'Blue Fire Arrows':                                ('Item',     True,  GetItemId.GI_ARROW_ICE, None),
    'Light Arrows':                                    ('Item',     True,  GetItemId.GI_ARROW_LIGHT, None),
    'Gold Skulltula Token':                            ('Token',    True,  GetItemId.GI_SKULL_TOKEN, {'progressive': float('Inf')}),
    'Dins Fire':                                       ('Item',     True,  GetItemId.GI_DINS_FIRE, None),
    'Farores Wind':                                    ('Item',     True,  GetItemId.GI_FARORES_WIND, None),
    'Nayrus Love':                                     ('Item',     True,  GetItemId.GI_NAYRUS_LOVE, None),
    'Deku Nuts (10)':                                  ('Item',     None,  GetItemId.GI_DEKU_NUTS_10, {'junk': 0}),
    'Bomb (1)':                                        ('Item',     None,  GetItemId.GI_BOMBS_1, {'junk': -1}),
    'Bombs (10)':                                      ('Item',     None,  GetItemId.GI_BOMBS_10, {'junk': 2}),
    'Bombs (20)':                                      ('Item',     None,  GetItemId.GI_BOMBS_20, {'junk': 0}),
    'Deku Seeds (30)':                                 ('Item',     None,  GetItemId.GI_DEKU_SEEDS_30, {'junk': 5}),
    'Bombchus (5)':                                    ('Item',     True,  GetItemId.GI_BOMBCHUS_5, None),
    'Bombchus (20)':                                   ('Item',     True,  GetItemId.GI_BOMBCHUS_20, None),
    'Small Key (Treasure Chest Game)':              ('TCGSmallKey', True,  GetItemId.GI_DOOR_KEY, {'progressive': float('Inf')}),
    'Rupee (Treasure Chest Game) (1)':                 ('Item',     None,  GetItemId.GI_RUPEE_GREEN_LOSE, None),
    'Rupees (Treasure Chest Game) (5)':                ('Item',     None,  GetItemId.GI_RUPEE_BLUE_LOSE, None),
    'Rupees (Treasure Chest Game) (20)':               ('Item',     None,  GetItemId.GI_RUPEE_RED_LOSE, None),
    'Rupees (Treasure Chest Game) (50)':               ('Item',     None,  GetItemId.GI_RUPEE_PURPLE_LOSE, None),
    'Piece of Heart (Treasure Chest Game)':            ('Item',     True,  GetItemId.GI_HEART_PIECE_WIN, {'alias': ('Piece of Heart', 1), 'progressive': float('Inf')}),
    'Ice Trap':                                        ('Item',     None,  GetItemId.GI_ICE_TRAP, {'junk': 0}),
    'Progressive Hookshot':                            ('Item',     True,  GetItemId.GI_PROGRESSIVE_HOOKSHOT, {'progressive': 2}),
    'Progressive Strength Upgrade':                    ('Item',     True,  GetItemId.GI_PROGRESSIVE_STRENGTH, {'progressive': 3}),
    'Bomb Bag':                                        ('Item',     True,  GetItemId.GI_PROGRESSIVE_BOMB_BAG, None),
    'Bow':                                             ('Item',     True,  GetItemId.GI_PROGRESSIVE_BOW, None),
    'Slingshot':                                       ('Item',     True,  GetItemId.GI_PROGRESSIVE_SLINGSHOT, None),
    'Progressive Wallet':                              ('Item',     True,  GetItemId.GI_PROGRESSIVE_WALLET, {'progressive': 3}),
    'Progressive Scale':                               ('Item',     True,  GetItemId.GI_PROGRESSIVE_SCALE, {'progressive': 2}),
    'Deku Nut Capacity':                               ('Item',     None,  GetItemId.GI_PROGRESSIVE_NUT_CAPACITY, None),
    'Deku Stick Capacity':                             ('Item',     None,  GetItemId.GI_PROGRESSIVE_STICK_CAPACITY, None),
    'Bombchus':                                        ('Item',     True,  GetItemId.GI_PROGRESSIVE_BOMBCHUS, None),
    'Magic Meter':                                     ('Item',     True,  GetItemId.GI_PROGRESSIVE_MAGIC_METER, None),
    'Ocarina':                                         ('Item',     True,  GetItemId.GI_PROGRESSIVE_OCARINA, {'progressive': 2}),
    'Bottle with Red Potion':                          ('Item',     True,  GetItemId.GI_BOTTLE_WITH_RED_POTION, {'bottle': True, 'shop_object': 0x0F}),
    'Bottle with Green Potion':                        ('Item',     True,  GetItemId.GI_BOTTLE_WITH_GREEN_POTION, {'bottle': True, 'shop_object': 0x0F}),
    'Bottle with Blue Potion':                         ('Item',     True,  GetItemId.GI_BOTTLE_WITH_BLUE_POTION, {'bottle': True, 'shop_object': 0x0F}),
    'Bottle with Fairy':                               ('Item',     True,  GetItemId.GI_BOTTLE_WITH_FAIRY, {'bottle': True, 'shop_object': 0x0F}),
    'Bottle with Fish':                                ('Item',     True,  GetItemId.GI_BOTTLE_WITH_FISH, {'bottle': True, 'shop_object': 0x0F}),
    'Bottle with Blue Fire':                           ('Item',     True,  GetItemId.GI_BOTTLE_WITH_BLUE_FIRE, {'bottle': True, 'shop_object': 0x0F}),
    'Bottle with Bugs':                                ('Item',     True,  GetItemId.GI_BOTTLE_WITH_BUGS, {'bottle': True, 'shop_object': 0x0F}),
    'Bottle with Big Poe':                             ('Item',     True,  GetItemId.GI_BOTTLE_WITH_BIG_POE, {'shop_object': 0x0F}),
    'Bottle with Poe':                                 ('Item',     True,  GetItemId.GI_BOTTLE_WITH_POE, {'bottle': True, 'shop_object': 0x0F}),
    'Boss Key (Forest Temple)':                        ('BossKey',  True,  GetItemId.GI_BOSS_KEY_FOREST_TEMPLE, None),
    'Boss Key (Fire Temple)':                          ('BossKey',  True,  GetItemId.GI_BOSS_KEY_FIRE_TEMPLE, None),
    'Boss Key (Water Temple)':                         ('BossKey',  True,  GetItemId.GI_BOSS_KEY_WATER_TEMPLE, None),
    'Boss Key (Spirit Temple)':                        ('BossKey',  True,  GetItemId.GI_BOSS_KEY_SPIRIT_TEMPLE, None),
    'Boss Key (Shadow Temple)':                        ('BossKey',  True,  GetItemId.GI_BOSS_KEY_SHADOW_TEMPLE, None),
    'Boss Key (Ganons Castle)':                   ('GanonBossKey',  True,  GetItemId.GI_BOSS_KEY_GANONS_CASTLE, None),
    'Compass (Deku Tree)':                             ('Compass', False,  GetItemId.GI_COMPASS_DEKU_TREE, None),
    'Compass (Dodongos Cavern)':                       ('Compass', False,  GetItemId.GI_COMPASS_DODONGOS_CAVERN, None),
    'Compass (Jabu Jabus Belly)':                      ('Compass', False,  GetItemId.GI_COMPASS_JABU_JABU, None),
    'Compass (Forest Temple)':                         ('Compass', False,  GetItemId.GI_COMPASS_FOREST_TEMPLE, None),
    'Compass (Fire Temple)':                           ('Compass', False,  GetItemId.GI_COMPASS_FIRE_TEMPLE, None),
    'Compass (Water Temple)':                          ('Compass', False,  GetItemId.GI_COMPASS_WATER_TEMPLE, None),
    'Compass (Spirit Temple)':                         ('Compass', False,  GetItemId.GI_COMPASS_SPIRIT_TEMPLE, None),
    'Compass (Shadow Temple)':                         ('Compass', False,  GetItemId.GI_COMPASS_SHADOW_TEMPLE, None),
    'Compass (Bottom of the Well)':                    ('Compass', False,  GetItemId.GI_COMPASS_BOTTOM_OF_THE_WELL, None),
    'Compass (Ice Cavern)':                            ('Compass', False,  GetItemId.GI_COMPASS_ICE_CAVERN, None),
    'Map (Deku Tree)':                                 ('Map',     False,  GetItemId.GI_MAP_DEKU_TREE, None),
    'Map (Dodongos Cavern)':                           ('Map',     False,  GetItemId.GI_MAP_DODONGOS_CAVERN, None),
    'Map (Jabu Jabus Belly)':                          ('Map',     False,  GetItemId.GI_MAP_JABU_JABU, None),
    'Map (Forest Temple)':                             ('Map',     False,  GetItemId.GI_MAP_FOREST_TEMPLE, None),
    'Map (Fire Temple)':                               ('Map',     False,  GetItemId.GI_MAP_FIRE_TEMPLE, None),
    'Map (Water Temple)':                              ('Map',     False,  GetItemId.GI_MAP_WATER_TEMPLE, None),
    'Map (Spirit Temple)':                             ('Map',     False,  GetItemId.GI_MAP_SPIRIT_TEMPLE, None),
    'Map (Shadow Temple)':                             ('Map',     False,  GetItemId.GI_MAP_SHADOW_TEMPLE, None),
    'Map (Bottom of the Well)':                        ('Map',     False,  GetItemId.GI_MAP_BOTTOM_OF_THE_WELL, None),
    'Map (Ice Cavern)':                                ('Map',     False,  GetItemId.GI_MAP_ICE_CAVERN, None),
    'Small Key (Forest Temple)':                       ('SmallKey', True,  GetItemId.GI_SMALL_KEY_FOREST_TEMPLE, {'progressive': float('Inf')}),
    'Small Key (Fire Temple)':                         ('SmallKey', True,  GetItemId.GI_SMALL_KEY_FIRE_TEMPLE, {'progressive': float('Inf')}),
    'Small Key (Water Temple)':                        ('SmallKey', True,  GetItemId.GI_SMALL_KEY_WATER_TEMPLE, {'progressive': float('Inf')}),
    'Small Key (Spirit Temple)':                       ('SmallKey', True,  GetItemId.GI_SMALL_KEY_SPIRIT_TEMPLE, {'progressive': float('Inf')}),
    'Small Key (Shadow Temple)':                       ('SmallKey', True,  GetItemId.GI_SMALL_KEY_SHADOW_TEMPLE, {'progressive': float('Inf')}),
    'Small Key (Bottom of the Well)':                  ('SmallKey', True,  GetItemId.GI_SMALL_KEY_BOTTOM_OF_THE_WELL, {'progressive': float('Inf')}),
    'Small Key (Gerudo Training Ground)':              ('SmallKey', True,  GetItemId.GI_SMALL_KEY_GERUDO_TRAINING, {'progressive': float('Inf')}),
    'Small Key (Thieves Hideout)':              ('HideoutSmallKey', True,  GetItemId.GI_SMALL_KEY_THIEVES_HIDEOUT, {'progressive': float('Inf')}),
    'Small Key (Ganons Castle)':                       ('SmallKey', True,  GetItemId.GI_SMALL_KEY_GANONS_CASTLE, {'progressive': float('Inf')}),
    'Double Defense':                                  ('Item',     None,  GetItemId.GI_DOUBLE_DEFENSE, None),
    'Buy Magic Bean':                                  ('Item',     True,  GetItemId.GI_MAGIC_BEAN, {'alias': ('Magic Bean', 10), 'progressive': 10}),
    'Magic Bean Pack':                                 ('Item',     True,  GetItemId.GI_MAGIC_BEAN_PACK, {'alias': ('Magic Bean', 10), 'progressive': 10}),
    'Triforce Piece':                                  ('Item',     True,  GetItemId.GI_TRIFORCE_PIECE, {'progressive': float('Inf')}),
    'Zeldas Letter':                                   ('Item',     True,  GetItemId.GI_ZELDAS_LETTER, {'trade': True}),
    'Time Travel':                                     ('Event',    True,  None,   None),
    'Scarecrow Song':                                  ('Event',    True,  None,   None),
    'Triforce':                                        ('Event',    True,  None,   None),

    'Small Key Ring (Forest Temple)':                  ('SmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_FOREST_TEMPLE, {'alias': ('Small Key (Forest Temple)', 10), 'progressive': float('Inf')}),
    'Small Key Ring (Fire Temple)':                    ('SmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_FIRE_TEMPLE, {'alias': ('Small Key (Fire Temple)', 10), 'progressive': float('Inf')}),
    'Small Key Ring (Water Temple)':                   ('SmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_WATER_TEMPLE, {'alias': ('Small Key (Water Temple)', 10), 'progressive': float('Inf')}),
    'Small Key Ring (Spirit Temple)':                  ('SmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_SPIRIT_TEMPLE, {'alias': ('Small Key (Spirit Temple)', 10), 'progressive': float('Inf')}),
    'Small Key Ring (Shadow Temple)':                  ('SmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_SHADOW_TEMPLE, {'alias': ('Small Key (Shadow Temple)', 10), 'progressive': float('Inf')}),
    'Small Key Ring (Bottom of the Well)':             ('SmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_BOTTOM_OF_THE_WELL, {'alias': ('Small Key (Bottom of the Well)', 10), 'progressive': float('Inf')}),
    'Small Key Ring (Gerudo Training Ground)':         ('SmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_GERUDO_TRAINING, {'alias': ('Small Key (Gerudo Training Ground)', 10), 'progressive': float('Inf')}),
    'Small Key Ring (Thieves Hideout)':         ('HideoutSmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_THIEVES_HIDEOUT, {'alias': ('Small Key (Thieves Hideout)', 10), 'progressive': float('Inf')}),
    'Small Key Ring (Ganons Castle)':                  ('SmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_GANONS_CASTLE, {'alias': ('Small Key (Ganons Castle)', 10), 'progressive': float('Inf')}),
    'Small Key Ring (Treasure Chest Game)':         ('TCGSmallKeyRing', True,  GetItemId.GI_SMALL_KEY_RING_TREASURE_CHEST_GAME, {'alias': ('Small Key (Treasure Chest Game)', 10), 'progressive': float('Inf')}),

    'Silver Rupee (Dodongos Cavern Staircase)':                 ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_DODONGOS_CAVERN_STAIRCASE, {'progressive': 5}),
    'Silver Rupee (Ice Cavern Spinning Scythe)':                ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_ICE_CAVERN_SPINNING_SCYTHE, {'progressive': 5}),
    'Silver Rupee (Ice Cavern Push Block)':                     ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_ICE_CAVERN_PUSH_BLOCK, {'progressive': 5}),
    'Silver Rupee (Bottom of the Well Basement)':               ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_BOTTOM_OF_THE_WELL_BASEMENT, {'progressive': 5}),
    'Silver Rupee (Shadow Temple Scythe Shortcut)':             ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_SHADOW_TEMPLE_SCYTHE_SHORTCUT, {'progressive': 5}),
    'Silver Rupee (Shadow Temple Invisible Blades)':            ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_SHADOW_TEMPLE_INVISIBLE_BLADES, {'progressive': 10}),
    'Silver Rupee (Shadow Temple Huge Pit)':                    ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_SHADOW_TEMPLE_HUGE_PIT, {'progressive': 5}),
    'Silver Rupee (Shadow Temple Invisible Spikes)':            ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_SHADOW_TEMPLE_INVISIBLE_SPIKES, {'progressive': 10}),
    'Silver Rupee (Gerudo Training Ground Slopes)':             ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_SLOPES, {'progressive': 5}),
    'Silver Rupee (Gerudo Training Ground Lava)':               ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_LAVA, {'progressive': 6}),
    'Silver Rupee (Gerudo Training Ground Water)':              ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_WATER, {'progressive': 5}),
    'Silver Rupee (Spirit Temple Child Early Torches)':         ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_SPIRIT_TEMPLE_CHILD_EARLY_TORCHES, {'progressive': 5}),
    'Silver Rupee (Spirit Temple Adult Boulders)':              ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_SPIRIT_TEMPLE_ADULT_BOULDERS, {'progressive': 5}),
    'Silver Rupee (Spirit Temple Lobby and Lower Adult)':       ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_SPIRIT_TEMPLE_LOBBY_AND_LOWER_ADULT, {'progressive': 5}),
    'Silver Rupee (Spirit Temple Sun Block)':                   ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_SPIRIT_TEMPLE_SUN_BLOCK, {'progressive': 5}),
    'Silver Rupee (Spirit Temple Adult Climb)':                 ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_SPIRIT_TEMPLE_ADULT_CLIMB, {'progressive': 5}),
    'Silver Rupee (Ganons Castle Spirit Trial)':                ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_GANONS_CASTLE_SPIRIT_TRIAL, {'progressive': 5}),
    'Silver Rupee (Ganons Castle Light Trial)':                 ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_GANONS_CASTLE_LIGHT_TRIAL, {'progressive': 5}),
    'Silver Rupee (Ganons Castle Fire Trial)':                  ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_GANONS_CASTLE_FIRE_TRIAL, {'progressive': 5}),
    'Silver Rupee (Ganons Castle Shadow Trial)':                ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_GANONS_CASTLE_SHADOW_TRIAL, {'progressive': 5}),
    'Silver Rupee (Ganons Castle Water Trial)':                 ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_GANONS_CASTLE_WATER_TRIAL, {'progressive': 5}),
    'Silver Rupee (Ganons Castle Forest Trial)':                ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_GANONS_CASTLE_FOREST_TRIAL, {'progressive': 5}),

    'Silver Rupee Pouch (Dodongos Cavern Staircase)':           ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_DODONGOS_CAVERN_STAIRCASE, {'alias': ('Silver Rupee (Dodongos Cavern Staircase)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Ice Cavern Spinning Scythe)':          ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_ICE_CAVERN_SPINNING_SCYTHE, {'alias': ('Silver Rupee (Ice Cavern Spinning Scythe)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Ice Cavern Push Block)':               ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_ICE_CAVERN_PUSH_BLOCK, {'alias': ('Silver Rupee (Ice Cavern Push Block)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Bottom of the Well Basement)':         ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_BOTTOM_OF_THE_WELL_BASEMENT, {'alias': ('Silver Rupee (Bottom of the Well Basement)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Shadow Temple Scythe Shortcut)':       ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_SCYTHE_SHORTCUT, {'alias': ('Silver Rupee (Shadow Temple Scythe Shortcut)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Shadow Temple Invisible Blades)':      ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_INVISIBLE_BLADES, {'alias': ('Silver Rupee (Shadow Temple Invisible Blades)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Shadow Temple Huge Pit)':              ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_HUGE_PIT, {'alias': ('Silver Rupee (Shadow Temple Huge Pit)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Shadow Temple Invisible Spikes)':      ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_INVISIBLE_SPIKES, {'alias': ('Silver Rupee (Shadow Temple Invisible Spikes)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Gerudo Training Ground Slopes)':       ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_SLOPES, {'alias': ('Silver Rupee (Gerudo Training Ground Slopes)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Gerudo Training Ground Lava)':         ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_LAVA, {'alias': ('Silver Rupee (Gerudo Training Ground Lava)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Gerudo Training Ground Water)':        ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_WATER, {'alias': ('Silver Rupee (Gerudo Training Ground Water)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Spirit Temple Child Early Torches)':   ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_CHILD_EARLY_TORCHES, {'alias': ('Silver Rupee (Spirit Temple Child Early Torches)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Spirit Temple Adult Boulders)':        ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_ADULT_BOULDERS, {'alias': ('Silver Rupee (Spirit Temple Adult Boulders)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Spirit Temple Lobby and Lower Adult)': ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_LOBBY_AND_LOWER_ADULT, {'alias': ('Silver Rupee (Spirit Temple Lobby and Lower Adult)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Spirit Temple Sun Block)':             ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_SUN_BLOCK, {'alias': ('Silver Rupee (Spirit Temple Sun Block)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Spirit Temple Adult Climb)':           ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_ADULT_CLIMB, {'alias': ('Silver Rupee (Spirit Temple Adult Climb)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Ganons Castle Spirit Trial)':          ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_SPIRIT_TRIAL, {'alias': ('Silver Rupee (Ganons Castle Spirit Trial)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Ganons Castle Light Trial)':           ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_LIGHT_TRIAL, {'alias': ('Silver Rupee (Ganons Castle Light Trial)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Ganons Castle Fire Trial)':            ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_FIRE_TRIAL, {'alias': ('Silver Rupee (Ganons Castle Fire Trial)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Ganons Castle Shadow Trial)':          ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_SHADOW_TRIAL, {'alias': ('Silver Rupee (Ganons Castle Shadow Trial)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Ganons Castle Water Trial)':           ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_WATER_TRIAL, {'alias': ('Silver Rupee (Ganons Castle Water Trial)', 10), 'progressive': 1}),
    'Silver Rupee Pouch (Ganons Castle Forest Trial)':          ('SilverRupee', True,  GetItemId.GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_FOREST_TRIAL, {'alias': ('Silver Rupee (Ganons Castle Forest Trial)', 10), 'progressive': 1}),

    'Ocarina A Button':                                ('Item',     True,  GetItemId.GI_OCARINA_BUTTON_A, {'ocarina_button': True}),
    'Ocarina C up Button':                             ('Item',     True,  GetItemId.GI_OCARINA_BUTTON_C_UP, {'ocarina_button': True}),
    'Ocarina C down Button':                           ('Item',     True,  GetItemId.GI_OCARINA_BUTTON_C_DOWN, {'ocarina_button': True}),
    'Ocarina C left Button':                           ('Item',     True,  GetItemId.GI_OCARINA_BUTTON_C_LEFT, {'ocarina_button': True}),
    'Ocarina C right Button':                          ('Item',     True,  GetItemId.GI_OCARINA_BUTTON_C_RIGHT, {'ocarina_button': True}),
    'Fairy Drop':                                      ('Item',     None,  GetItemId.GI_FAIRY, None),
    'Nothing':                                         ('Item',     None,  GetItemId.GI_NOTHING, None),

    # Event items otherwise generated by generic event logic
    # can be defined here to enforce their appearance in playthroughs.
    'Water Temple Clear':               ('Event',    True,  None, None),
    'Forest Trial Clear':               ('Event',    True,  None, None),
    'Fire Trial Clear':                 ('Event',    True,  None, None),
    'Water Trial Clear':                ('Event',    True,  None, None),
    'Shadow Trial Clear':               ('Event',    True,  None, None),
    'Spirit Trial Clear':               ('Event',    True,  None, None),
    'Light Trial Clear':                ('Event',    True,  None, None),
    'Epona':                            ('Event',    True,  None, None),

    'Deku Stick Drop':                  ('Drop',     True,  None, None),
    'Deku Nut Drop':                    ('Drop',     True,  None, None),
    'Blue Fire':                        ('Drop',     True,  None, None),
    'Fairy':                            ('Drop',     True,  None, None),
    'Fish':                             ('Drop',     True,  None, None),
    'Bugs':                             ('Drop',     True,  None, None),
    'Big Poe':                          ('Drop',     True,  None, None),
    'Bombchu Drop':                     ('Drop',     True,  None, None),
    'Deku Shield Drop':                 ('Drop',     True,  None, None),

    # Consumable refills defined mostly to placate 'starting with' options
    'Arrows':                           ('Refill',   None,  None, None),
    'Bombs':                            ('Refill',   None,  None, None),
    'Deku Seeds':                       ('Refill',   None,  None, None),
    'Deku Sticks':                      ('Refill',   None,  None, None),
    'Deku Nuts':                        ('Refill',   None,  None, None),
    'Rupees':                           ('Refill',   None,  None, None),

    'Minuet of Forest':                 ('Song',     True,  GetItemId.GI_MINUET_OF_FOREST,
                                            {
                                                'text_id': 0x73,
                                                'song_id': 0x02,
                                                'item_id': 0x5A,
                                            }),
    'Bolero of Fire':                   ('Song',     True,  GetItemId.GI_BOLERO_OF_FIRE,
                                            {
                                                'text_id': 0x74,
                                                'song_id': 0x03,
                                                'item_id': 0x5B,
                                            }),
    'Serenade of Water':                ('Song',     True,  GetItemId.GI_SERENADE_OF_WATER,
                                            {
                                                'text_id': 0x75,
                                                'song_id': 0x04,
                                                'item_id': 0x5C,
                                            }),
    'Requiem of Spirit':                ('Song',     True,  GetItemId.GI_REQUIEM_OF_SPIRIT,
                                            {
                                                'text_id': 0x76,
                                                'song_id': 0x05,
                                                'item_id': 0x5D,
                                            }),
    'Nocturne of Shadow':               ('Song',     True,  GetItemId.GI_NOCTURNE_OF_SHADOW,
                                            {
                                                'text_id': 0x77,
                                                'song_id': 0x06,
                                                'item_id': 0x5E,
                                            }),
    'Prelude of Light':                 ('Song',     True,  GetItemId.GI_PRELUDE_OF_LIGHT,
                                            {
                                                'text_id': 0x78,
                                                'song_id': 0x07,
                                                'item_id': 0x5F,
                                            }),
    'Zeldas Lullaby':                   ('Song',     True,  GetItemId.GI_ZELDAS_LULLABY,
                                            {
                                                'text_id': 0xD4,
                                                'song_id': 0x0A,
                                                'item_id': 0x60,
                                            }),
    'Eponas Song':                      ('Song',     True,  GetItemId.GI_EPONAS_SONG,
                                            {
                                                'text_id': 0xD2,
                                                'song_id': 0x09,
                                                'item_id': 0x61,
                                            }),
    'Sarias Song':                      ('Song',     True,  GetItemId.GI_SARIAS_SONG,
                                            {
                                                'text_id': 0xD1,
                                                'song_id': 0x08,
                                                'item_id': 0x62,
                                            }),
    'Suns Song':                        ('Song',     True,  GetItemId.GI_SUNS_SONG,
                                            {
                                                'text_id': 0xD3,
                                                'song_id': 0x0B,
                                                'item_id': 0x63,
                                            }),
    'Song of Time':                     ('Song',     True,  GetItemId.GI_SONG_OF_TIME,
                                            {
                                                'text_id': 0xD5,
                                                'song_id': 0x0C,
                                                'item_id': 0x64,
                                            }),
    'Song of Storms':                   ('Song',     True,  GetItemId.GI_SONG_OF_STORMS,
                                            {
                                                'text_id': 0xD6,
                                                'song_id': 0x0D,
                                                'item_id': 0x65,
                                            }),

    'Buy Deku Nut (5)':                 ('Shop',     True,  0x00, {'object': 0x00BB, 'price': 15}),
    'Buy Arrows (30)':                  ('Shop',     False, 0x01, {'object': 0x00D8, 'price': 60}),
    'Buy Arrows (50)':                  ('Shop',     False, 0x02, {'object': 0x00D8, 'price': 90}),
    'Buy Bombs (5) for 25 Rupees':      ('Shop',     False, 0x03, {'object': 0x00CE, 'price': 25}),
    'Buy Deku Nut (10)':                ('Shop',     True,  0x04, {'object': 0x00BB, 'price': 30}),
    'Buy Deku Stick (1)':               ('Shop',     True,  0x05, {'object': 0x00C7, 'price': 10}),
    'Buy Bombs (10)':                   ('Shop',     False, 0x06, {'object': 0x00CE, 'price': 50}),
    'Buy Fish':                         ('Shop',     True,  0x07, {'object': 0x00F4, 'price': 200}),
    'Buy Red Potion for 30 Rupees':     ('Shop',     False, 0x08, {'object': 0x00EB, 'price': 30}),
    'Buy Green Potion':                 ('Shop',     False, 0x09, {'object': 0x00EB, 'price': 30}),
    'Buy Blue Potion':                  ('Shop',     False, 0x0A, {'object': 0x00EB, 'price': 100}),
    'Buy Hylian Shield':                ('Shop',     True,  0x0C, {'object': 0x00DC, 'price': 80}),
    'Buy Deku Shield':                  ('Shop',     True,  0x0D, {'object': 0x00CB, 'price': 40}),
    'Buy Goron Tunic':                  ('Shop',     True,  0x0E, {'object': 0x00F2, 'price': 200}),
    'Buy Zora Tunic':                   ('Shop',     True,  0x0F, {'object': 0x00F2, 'price': 300}),
    'Buy Heart':                        ('Shop',     False, 0x10, {'object': 0x00B7, 'price': 10}),
    'Buy Bombchu (10)':                 ('Shop',     True,  0x15, {'object': 0x00D9, 'price': 99}),
    'Buy Bombchu (20)':                 ('Shop',     True,  0x16, {'object': 0x00D9, 'price': 180}),
    'Buy Bombchu (5)':                  ('Shop',     True,  0x18, {'object': 0x00D9, 'price': 60}),
    'Buy Deku Seeds (30)':              ('Shop',     False, 0x1D, {'object': 0x0119, 'price': 30}),
    'Sold Out':                         ('Shop',     False, 0x26, {'object': 0x0148}),
    'Buy Blue Fire':                    ('Shop',     True,  0x27, {'object': 0x0173, 'price': 300}),
    'Buy Bottle Bug':                   ('Shop',     True,  0x28, {'object': 0x0174, 'price': 50}),
    'Buy Poe':                          ('Shop',     False, 0x2A, {'object': 0x0176, 'price': 30}),
    'Buy Fairy\'s Spirit':              ('Shop',     True,  0x2B, {'object': 0x0177, 'price': 50}),
    'Buy Arrows (10)':                  ('Shop',     False, 0x2C, {'object': 0x00D8, 'price': 20}),
    'Buy Bombs (20)':                   ('Shop',     False, 0x2D, {'object': 0x00CE, 'price': 80}),
    'Buy Bombs (30)':                   ('Shop',     False, 0x2E, {'object': 0x00CE, 'price': 120}),
    'Buy Bombs (5) for 35 Rupees':      ('Shop',     False, 0x2F, {'object': 0x00CE, 'price': 35}),
    'Buy Red Potion for 40 Rupees':     ('Shop',     False, 0x30, {'object': 0x00EB, 'price': 40}),
    'Buy Red Potion for 50 Rupees':     ('Shop',     False, 0x31, {'object': 0x00EB, 'price': 50}),

    'Kokiri Emerald':                   ('DungeonReward',    True,  GetItemId.GI_KOKIRI_EMERALD, {'stone':     True, 'item_id': 0x6C}),
    'Goron Ruby':                       ('DungeonReward',    True,  GetItemId.GI_GORON_RUBY, {'stone':     True, 'item_id': 0x6D}),
    'Zora Sapphire':                    ('DungeonReward',    True,  GetItemId.GI_ZORA_SAPPHIRE, {'stone':     True, 'item_id': 0x6E}),
    'Light Medallion':                  ('DungeonReward',    True,  GetItemId.GI_LIGHT_MEDALLION, {'medallion': True, 'item_id': 0x6B}),
    'Forest Medallion':                 ('DungeonReward',    True,  GetItemId.GI_FOREST_MEDALLION, {'medallion': True, 'item_id': 0x66}),
    'Fire Medallion':                   ('DungeonReward',    True,  GetItemId.GI_FIRE_MEDALLION, {'medallion': True, 'item_id': 0x67}),
    'Water Medallion':                  ('DungeonReward',    True,  GetItemId.GI_WATER_MEDALLION, {'medallion': True, 'item_id': 0x68}),
    'Shadow Medallion':                 ('DungeonReward',    True,  GetItemId.GI_SHADOW_MEDALLION, {'medallion': True, 'item_id': 0x6A}),
    'Spirit Medallion':                 ('DungeonReward',    True,  GetItemId.GI_SPIRIT_MEDALLION, {'medallion': True, 'item_id': 0x69}),
}

REWARD_COLORS: dict[str, str] = {
    'Kokiri Emerald': 'Green',
    'Goron Ruby': 'Red',
    'Zora Sapphire': 'Blue',
    'Light Medallion': 'Light Blue',
    'Forest Medallion': 'Green',
    'Fire Medallion': 'Red',
    'Water Medallion': 'Blue',
    'Shadow Medallion': 'Pink',
    'Spirit Medallion': 'Yellow',
}
