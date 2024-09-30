#ifndef ITEM_TABLE_H
#define ITEM_TABLE_H

#include <stdbool.h>

#include "get_items.h"
#include "z64.h"

// Enum that indexes into item_table.
// Please update comments accordingly when adding new entries
typedef enum GetItemID {
    /* 0x0000 */ GI_NONE,
    /* 0x0001 */ GI_BOMBS_5, // Bombs (5)
    /* 0x0002 */ GI_DEKU_NUTS_5, // Deku Nuts (5)
    /* 0x0003 */ GI_BOMBCHUS_10, // Bombchu (10)
    /* 0x0004 */ GI_BOW, // Fairy Bow
    /* 0x0005 */ GI_SLINGSHOT, // Fairy Slingshot
    /* 0x0006 */ GI_BOOMERANG, // Boomerang
    /* 0x0007 */ GI_DEKU_STICKS_1, // Deku Stick
    /* 0x0008 */ GI_HOOKSHOT, // Hookshot
    /* 0x0009 */ GI_LONGSHOT, // Longshot
    /* 0x000A */ GI_LENS_OF_TRUTH, // Lens of Truth
    /* 0x000B */ GI_ZELDAS_LETTER, // Zelda's Letter
    /* 0x000C */ GI_OCARINA_OF_TIME, // Ocarina of Time
    /* 0x000D */ GI_HAMMER, // Megaton Hammer
    /* 0x000E */ GI_COJIRO, // Cojiro

    /* 0x000F */ GI_BOTTLE_EMPTY, // Empty Bottle
    /* 0x0010 */ GI_BOTTLE_POTION_RED, // Red Potion
    /* 0x0011 */ GI_BOTTLE_POTION_GREEN, // Green Potion
    /* 0x0012 */ GI_BOTTLE_POTION_BLUE, // Blue Potion
    /* 0x0013 */ GI_BOTTLE_FAIRY, // Bottled Fairy
    /* 0x0014 */ GI_BOTTLE_MILK_FULL, // Bottled Lon Lon Milk
    /* 0x0015 */ GI_BOTTLE_RUTOS_LETTER, // Bottled Ruto's Letter

    /* 0x0016 */ GI_MAGIC_BEAN, // Magic Bean
    /* 0x0017 */ GI_MASK_SKULL, // Skull Mask
    /* 0x0018 */ GI_MASK_SPOOKY, // Spooky Mask
    /* 0x0019 */ GI_CHICKEN, // Chicken
    /* 0x001A */ GI_MASK_KEATON, // Keaton Mask
    /* 0x001B */ GI_MASK_BUNNY_HOOD, // Bunny Hood
    /* 0x001C */ GI_MASK_TRUTH, // Mask of Truth
    /* 0x001D */ GI_POCKET_EGG, // Pocket Egg
    /* 0x001E */ GI_POCKET_CUCCO, // Pocket Cucco
    /* 0x001F */ GI_ODD_MUSHROOM, // Odd Mushroom
    /* 0x0020 */ GI_ODD_POTION, // Odd Potion
    /* 0x0021 */ GI_POACHERS_SAW, // Poacher's Saw
    /* 0x0022 */ GI_BROKEN_GORONS_SWORD, // Goron's Sword (Broken)
    /* 0x0023 */ GI_PRESCRIPTION, // Prescription
    /* 0x0024 */ GI_EYEBALL_FROG, // Eyeball Frog
    /* 0x0025 */ GI_EYE_DROPS, // Eye Drops
    /* 0x0026 */ GI_CLAIM_CHECK, // Claim Check
    /* 0x0027 */ GI_SWORD_KOKIRI, // Kokiri Sword
    /* 0x0028 */ GI_SWORD_KNIFE, // Giant's Knife
    /* 0x0029 */ GI_SHIELD_DEKU, // Deku Shield
    /* 0x002A */ GI_SHIELD_HYLIAN, // Hylian Shield
    /* 0x002B */ GI_SHIELD_MIRROR, // Mirror Shield
    /* 0x002C */ GI_TUNIC_GORON, // Goron Tunic
    /* 0x002D */ GI_TUNIC_ZORA, // Zora Tunic
    /* 0x002E */ GI_BOOTS_IRON, // Iron Boots
    /* 0x002F */ GI_BOOTS_HOVER, // Hover Boots
    /* 0x0030 */ GI_QUIVER_40, // Big Quiver
    /* 0x0031 */ GI_QUIVER_50, // Biggest Quiver
    /* 0x0032 */ GI_BOMB_BAG_20, // Bomb Bag
    /* 0x0033 */ GI_BOMB_BAG_30, // Big Bomb Bag
    /* 0x0034 */ GI_BOMB_BAG_40, // Biggest Bomb Bag
    /* 0x0035 */ GI_SILVER_GAUNTLETS, // Silver Gauntlets
    /* 0x0036 */ GI_GOLD_GAUNTLETS, // Golden Gauntlets
    /* 0x0037 */ GI_SCALE_SILVER, // Silver Scale
    /* 0x0038 */ GI_SCALE_GOLDEN, // Golden Scale
    /* 0x0039 */ GI_STONE_OF_AGONY, // Stone of Agony
    /* 0x003A */ GI_GERUDOS_CARD, // Gerudo Membership Card

    /* 0x003B */ GI_OCARINA_FAIRY, // Fairy Ocarina
    /* 0x003C */ GI_DEKU_SEEDS_5, // Deku Seeds (5)
    /* 0x003D */ GI_HEART_CONTAINER, // Heart Container
    /* 0x003E */ GI_HEART_PIECE, // Piece of Heart
    /* 0x003F */ GI_BOSS_KEY, // Boss Key
    /* 0x0040 */ GI_COMPASS, // Compass
    /* 0x0041 */ GI_DUNGEON_MAP, // Map
    /* 0x0042 */ GI_SMALL_KEY, // Small Key
    /* 0x0043 */ GI_MAGIC_JAR_SMALL, // Small Magic Jar
    /* 0x0044 */ GI_MAGIC_JAR_LARGE, // Large Magic Jar
    /* 0x0045 */ GI_WALLET_ADULT, // Adult's Wallet
    /* 0x0046 */ GI_WALLET_GIANT, // Giant's Wallet
    /* 0x0047 */ GI_WEIRD_EGG, // Weird Egg
    /* 0x0048 */ GI_RECOVERY_HEART, // Recovery Heart
    /* 0x0049 */ GI_ARROWS_5, // Arrows (5)
    /* 0x004A */ GI_ARROWS_10, // Arrows (10)
    /* 0x004B */ GI_ARROWS_30, // Arrows (30)
    /* 0x004C */ GI_RUPEE_GREEN, // Green Rupee
    /* 0x004D */ GI_RUPEE_BLUE, // Blue Rupee
    /* 0x004E */ GI_RUPEE_RED, // Red Rupee
    /* 0x004F */ GI_HEART_CONTAINER_2, // Heart Container
    /* 0x0050 */ GI_MILK, // Lon Lon Milk (Refill)
    /* 0x0051 */ GI_MASK_GORON, // Goron Mask
    /* 0x0052 */ GI_MASK_ZORA, // Zora Mask
    /* 0x0053 */ GI_MASK_GERUDO, // Gerudo Mask
    /* 0x0054 */ GI_GORONS_BRACELET, // Goron's Bracelet
    /* 0x0055 */ GI_RUPEE_PURPLE, // Purple Rupee
    /* 0x0056 */ GI_RUPEE_GOLD, // Huge Rupee
    /* 0x0057 */ GI_SWORD_BIGGORON, // Biggoron's Sword
    /* 0x0058 */ GI_ARROW_FIRE, // Fire Arrow
    /* 0x0059 */ GI_ARROW_ICE, // Ice Arrow
    /* 0x005A */ GI_ARROW_LIGHT, // Light Arrow
    /* 0x005B */ GI_SKULL_TOKEN, // Gold Skulltula Token
    /* 0x005C */ GI_DINS_FIRE, // Din's Fire
    /* 0x005D */ GI_FARORES_WIND, // Farore's Wind
    /* 0x005E */ GI_NAYRUS_LOVE, // Nayru's Love
    /* 0x005F */ GI_BULLET_BAG_30, // Bullet Bag (30)
    /* 0x0060 */ GI_BULLET_BAG_40, // Bullet Bag (40)
    /* 0x0061 */ GI_DEKU_STICKS_5, // Deku Sticks (5)
    /* 0x0062 */ GI_DEKU_STICKS_10, // Deku Sticks (10)
    /* 0x0063 */ GI_DEKU_NUTS_5_2, // Deku Nuts (5)
    /* 0x0064 */ GI_DEKU_NUTS_10, // Deku Nuts (10)
    /* 0x0065 */ GI_BOMBS_1, // Bomb
    /* 0x0066 */ GI_BOMBS_10, // Bombs (10)
    /* 0x0067 */ GI_BOMBS_20, // Bombs (20)
    /* 0x0068 */ GI_BOMBS_30, // Bombs (30)
    /* 0x0069 */ GI_DEKU_SEEDS_30, // Deku Seeds (30)
    /* 0x006A */ GI_BOMBCHUS_5, // Bombchu (5)
    /* 0x006B */ GI_BOMBCHUS_20, // Bombchu (20)
    /* 0x006C */ GI_BOTTLE_FISH, // Fish (Refill)
    /* 0x006D */ GI_BOTTLE_BUGS, // Bugs (Refill)
    /* 0x006E */ GI_BOTTLE_BLUE_FIRE, // Blue Fire (Refill)
    /* 0x006F */ GI_BOTTLE_POE, // Poe (Refill)
    /* 0x0070 */ GI_BOTTLE_BIG_POE, // Big Poe (Refill)
    /* 0x0071 */ GI_DOOR_KEY, // Small Key (Chest Game)
    /* 0x0072 */ GI_RUPEE_GREEN_LOSE, // Green Rupee (Chest Game)
    /* 0x0073 */ GI_RUPEE_BLUE_LOSE, // Blue Rupee (Chest Game)
    /* 0x0074 */ GI_RUPEE_RED_LOSE, // Red Rupee (Chest Game)
    /* 0x0075 */ GI_RUPEE_PURPLE_LOSE, // Purple Rupee (Chest Game)
    /* 0x0076 */ GI_HEART_PIECE_WIN, // Piece of Heart (Chest Game)
    /* 0x0077 */ GI_DEKU_STICK_UPGRADE_20, // Deku Stick Upgrade (20)
    /* 0x0078 */ GI_DEKU_STICK_UPGRADE_30, // Deku Stick Upgrade (30)
    /* 0x0079 */ GI_DEKU_NUT_UPGRADE_30, // Deku Nut Upgrade (30)
    /* 0x007A */ GI_DEKU_NUT_UPGRADE_40, // Deku Nut Upgrade (40)
    /* 0x007B */ GI_BULLET_BAG_50, // Bullet Bag (50)
    /* 0x007C */ GI_ICE_TRAP, // Ice Trap

    /* 0x007D */ GI_TEXT_0,
    /* 0x007D */ GI_CAPPED_PIECE_OF_HEART = GI_TEXT_0, // Capped Piece of Heart
    /* 0x007E */ GI_VANILLA_MAX,
    /* 0x007E */ GI_CAPPED_HEART_CONTAINER = GI_VANILLA_MAX, // Capped Heart Container

    /* 0x007F */ GI_CAPPED_PIECE_OF_HEART_CHESTGAME, // Capped Piece of Heart (Chest Game)

    /* 0x0080 */ GI_PROGRESSIVE_HOOKSHOT, // Progressive Hookshot
    /* 0x0081 */ GI_PROGRESSIVE_STRENGTH, // Progressive Strength
    /* 0x0082 */ GI_PROGRESSIVE_BOMB_BAG, // Progressive Bomb Bag
    /* 0x0083 */ GI_PROGRESSIVE_BOW, // Progressive Bow
    /* 0x0084 */ GI_PROGRESSIVE_SLINGSHOT, // Progressive Slingshot
    /* 0x0085 */ GI_PROGRESSIVE_WALLET, // Progressive Wallet
    /* 0x0086 */ GI_PROGRESSIVE_SCALE, // Progressive Scale
    /* 0x0087 */ GI_PROGRESSIVE_NUT_CAPACITY, // Progressive Nut Capacity
    /* 0x0088 */ GI_PROGRESSIVE_STICK_CAPACITY, // Progressive Stick Capacity
    /* 0x0089 */ GI_PROGRESSIVE_BOMBCHUS, // Progressive Bombchus
    /* 0x008A */ GI_PROGRESSIVE_MAGIC_METER, // Progressive Magic Meter
    /* 0x008B */ GI_PROGRESSIVE_OCARINA, // Progressive Ocarina

    /* 0x008C */ GI_BOTTLE_WITH_RED_POTION, // Bottle with Red Potion
    /* 0x008D */ GI_BOTTLE_WITH_GREEN_POTION, // Bottle with Green Potion
    /* 0x008E */ GI_BOTTLE_WITH_BLUE_POTION, // Bottle with Blue Potion
    /* 0x008F */ GI_BOTTLE_WITH_FAIRY, // Bottle with Fairy
    /* 0x0090 */ GI_BOTTLE_WITH_FISH, // Bottle with Fish
    /* 0x0091 */ GI_BOTTLE_WITH_BLUE_FIRE, // Bottle with Blue Fire
    /* 0x0092 */ GI_BOTTLE_WITH_BUGS, // Bottle with Bugs
    /* 0x0093 */ GI_BOTTLE_WITH_BIG_POE, // Bottle with Big Poe
    /* 0x0094 */ GI_BOTTLE_WITH_POE, // Bottle with Poe

    /* 0x0095 */ GI_BOSS_KEY_TEMPLE,
    /* 0x0095 */ GI_BOSS_KEY_FOREST_TEMPLE = GI_BOSS_KEY_TEMPLE, // Forest Temple Boss Key
    /* 0x0096 */ GI_BOSS_KEY_FIRE_TEMPLE, // Fire Temple Boss Key
    /* 0x0097 */ GI_BOSS_KEY_WATER_TEMPLE, // Water Temple Boss Key
    /* 0x0098 */ GI_BOSS_KEY_SPIRIT_TEMPLE, // Spirit Temple Boss Key
    /* 0x0099 */ GI_BOSS_KEY_SHADOW_TEMPLE, // Shadow Temple Boss Key
    /* 0x009A */ GI_BOSS_KEY_GANONS_CASTLE, // Ganon's Castle Boss Key

    /* 0x009B */ GI_COMPASS_DEKU_TREE, // Deku Tree Compass
    /* 0x009C */ GI_COMPASS_DODONGOS_CAVERN, // Dodongo's Cavern Compass
    /* 0x009D */ GI_COMPASS_JABU_JABU, // Jabu Jabu Compass
    /* 0x009E */ GI_COMPASS_FOREST_TEMPLE, // Forest Temple Compass
    /* 0x009F */ GI_COMPASS_FIRE_TEMPLE, // Fire Temple Compass
    /* 0x00A0 */ GI_COMPASS_WATER_TEMPLE, // Water Temple Compass
    /* 0x00A1 */ GI_COMPASS_SPIRIT_TEMPLE, // Spirit Temple Compass
    /* 0x00A2 */ GI_COMPASS_SHADOW_TEMPLE, // Shadow Temple Compass
    /* 0x00A3 */ GI_COMPASS_BOTTOM_OF_THE_WELL, // Bottom of the Well Compass
    /* 0x00A4 */ GI_COMPASS_ICE_CAVERN, // Ice Cavern Compass

    /* 0x00A5 */ GI_MAP_DEKU_TREE, // Deku Tree Map
    /* 0x00A6 */ GI_MAP_DODONGOS_CAVERN, // Dodongo's Cavern Map
    /* 0x00A7 */ GI_MAP_JABU_JABU, // Jabu Jabu Map
    /* 0x00A8 */ GI_MAP_FOREST_TEMPLE, // Forest Temple Map
    /* 0x00A9 */ GI_MAP_FIRE_TEMPLE, // Fire Temple Map
    /* 0x00AA */ GI_MAP_WATER_TEMPLE, // Water Temple Map
    /* 0x00AB */ GI_MAP_SPIRIT_TEMPLE, // Spirit Temple Map
    /* 0x00AC */ GI_MAP_SHADOW_TEMPLE, // Shadow Temple Map
    /* 0x00AD */ GI_MAP_BOTTOM_OF_THE_WELL, // Bottom of the Well Map
    /* 0x00AE */ GI_MAP_ICE_CAVERN, // Ice Cavern Map

    /* 0x00AF */ GI_SMALL_KEY_MIN,
    /* 0x00AF */ GI_SMALL_KEY_FOREST_TEMPLE = GI_SMALL_KEY_MIN, // Forest Temple Small Key
    /* 0x00B0 */ GI_SMALL_KEY_FIRE_TEMPLE, // Fire Temple Small Key
    /* 0x00B1 */ GI_SMALL_KEY_WATER_TEMPLE, // Water Temple Small Key
    /* 0x00B2 */ GI_SMALL_KEY_SPIRIT_TEMPLE, // Spirit Temple Small Key
    /* 0x00B3 */ GI_SMALL_KEY_SHADOW_TEMPLE, // Shadow Temple Small Key
    /* 0x00B4 */ GI_SMALL_KEY_BOTTOM_OF_THE_WELL, // Bottom of the Well Small Key
    /* 0x00B5 */ GI_SMALL_KEY_GERUDO_TRAINING, // Gerudo Training Small Key
    /* 0x00B6 */ GI_SMALL_KEY_THIEVES_HIDEOUT, // Thieves' Hideout Small Key
    /* 0x00AF */ GI_SMALL_KEY_MAX,
    /* 0x00B7 */ GI_SMALL_KEY_GANONS_CASTLE = GI_SMALL_KEY_MAX, // Ganon's Castle Small Key

    /* 0x00B8 */ GI_DOUBLE_DEFENSE, // Double Defense
    /* 0x00B9 */ GI_MAGIC_METER, // Magic Meter
    /* 0x00BA */ GI_DOUBLE_MAGIC, // Double Magic

    /* 0x00BB */ GI_MINUET_OF_FOREST, // Minuet of Forest
    /* 0x00BC */ GI_BOLERO_OF_FIRE, // Bolero of Fire
    /* 0x00BD */ GI_SERENADE_OF_WATER, // Serenade of Water
    /* 0x00BE */ GI_REQUIEM_OF_SPIRIT, // Requiem of Spirit
    /* 0x00BF */ GI_NOCTURNE_OF_SHADOW, // Nocturne of Shadow
    /* 0x00C0 */ GI_PRELUDE_OF_LIGHT, // Prelude of Light

    /* 0x00C1 */ GI_ZELDAS_LULLABY, // Zelda's Lullaby
    /* 0x00C2 */ GI_EPONAS_SONG, // Epona's Song
    /* 0x00C3 */ GI_SARIAS_SONG, // Saria's Song
    /* 0x00C4 */ GI_SUNS_SONG, // Sun's Song
    /* 0x00C5 */ GI_SONG_OF_TIME, // Song of Time
    /* 0x00C6 */ GI_SONG_OF_STORMS, // Song of Storms

    /* 0x00C7 */ GI_TYCOONS_WALLET, // Tycoon's Wallet
    /* 0x00C8 */ GI_REDUNDANT_LETTER_BOTTLE, // Redundant Letter Bottle
    /* 0x00C9 */ GI_MAGIC_BEAN_PACK, // Magic Bean Pack
    /* 0x00CA */ GI_TRIFORCE_PIECE, // Triforce piece

    /* 0x00CB */ GI_SMALL_KEY_RING_TEMPLE_MIN,
    /* 0x00CB */ GI_SMALL_KEY_RING_FOREST_TEMPLE = GI_SMALL_KEY_RING_TEMPLE_MIN, // Forest Temple Small Key Ring
    /* 0x00CC */ GI_SMALL_KEY_RING_FIRE_TEMPLE, // Fire Temple Small Key Ring
    /* 0x00CD */ GI_SMALL_KEY_RING_WATER_TEMPLE, // Water Temple Small Key Ring
    /* 0x00CE */ GI_SMALL_KEY_RING_SPIRIT_TEMPLE, // Spirit Temple Small Key Ring
    /* 0x00CF */ GI_SMALL_KEY_RING_TEMPLE_MAX,
    /* 0x00CF */ GI_SMALL_KEY_RING_SHADOW_TEMPLE = GI_SMALL_KEY_RING_TEMPLE_MAX, // Shadow Temple Small Key Ring
    /* 0x00D0 */ GI_SMALL_KEY_RING_BOTTOM_OF_THE_WELL, // Bottom of the Well Small Key Ring
    /* 0x00D1 */ GI_SMALL_KEY_RING_GERUDO_TRAINING, // Gerudo Training Small Key Ring
    /* 0x00D2 */ GI_SMALL_KEY_RING_THIEVES_HIDEOUT, // Thieves' Hideout Small Key Ring
    /* 0x00D3 */ GI_SMALL_KEY_RING_GANONS_CASTLE, // Ganon's Castle Small Key Ring

    /* 0x00D4 */ GI_BOMBCHU_BAG_20, // Bombchu Bag (20)
    /* 0x00D5 */ GI_BOMBCHU_BAG_10, // Bombchu Bag (10)
    /* 0x00D6 */ GI_BOMBCHU_BAG_5, // Bombchu Bag (5)

    /* 0x00D7 */ GI_SMALL_KEY_RING_TREASURE_CHEST_GAME, // Treasure Chest Game Small Key Ring

    /* 0x00D8 */ GI_SILVER_RUPEE_DODONGOS_CAVERN_STAIRCASE, // Silver Rupee (Dodongos Cavern Staircase)
    /* 0x00D9 */ GI_SILVER_RUPEE_ICE_CAVERN_SPINNING_SCYTHE, // Silver Rupee (Ice Cavern Spinning Scythe)
    /* 0x00DA */ GI_SILVER_RUPEE_ICE_CAVERN_PUSH_BLOCK, // Silver Rupee (Ice Cavern Push Block)
    /* 0x00DB */ GI_SILVER_RUPEE_BOTTOM_OF_THE_WELL_BASEMENT, // Silver Rupee (Bottom of the Well Basement)
    /* 0x00DC */ GI_SILVER_RUPEE_SHADOW_TEMPLE_SCYTHE_SHORTCUT, // Silver Rupee (Shadow Temple Scythe Shortcut)
    /* 0x00DD */ GI_SILVER_RUPEE_SHADOW_TEMPLE_INVISIBLE_BLADES, // Silver Rupee (Shadow Temple Invisible Blades)
    /* 0x00DE */ GI_SILVER_RUPEE_SHADOW_TEMPLE_HUGE_PIT, // Silver Rupee (Shadow Temple Huge Pit)
    /* 0x00DF */ GI_SILVER_RUPEE_SHADOW_TEMPLE_INVISIBLE_SPIKES, // Silver Rupee (Shadow Temple Invisible Spikes)
    /* 0x00E0 */ GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_SLOPES, // Silver Rupee (Gerudo Training Ground Slopes)
    /* 0x00E1 */ GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_LAVA, // Silver Rupee (Gerudo Training Ground Lava)
    /* 0x00E2 */ GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_WATER, // Silver Rupee (Gerudo Training Ground Water)
    /* 0x00E3 */ GI_SILVER_RUPEE_SPIRIT_TEMPLE_CHILD_EARLY_TORCHES, // Silver Rupee (Spirit Temple Child Early Torches)
    /* 0x00E4 */ GI_SILVER_RUPEE_SPIRIT_TEMPLE_ADULT_BOULDERS, // Silver Rupee (Spirit Temple Adult Boulders)
    /* 0x00E5 */ GI_SILVER_RUPEE_SPIRIT_TEMPLE_LOBBY_AND_LOWER_ADULT, // Silver Rupee (Spirit Temple Lobby and Lower Adult)
    /* 0x00E6 */ GI_SILVER_RUPEE_SPIRIT_TEMPLE_SUN_BLOCK, // Silver Rupee (Spirit Temple Sun Block)
    /* 0x00E7 */ GI_SILVER_RUPEE_SPIRIT_TEMPLE_ADULT_CLIMB, // Silver Rupee (Spirit Temple Adult Climb)
    /* 0x00E8 */ GI_SILVER_RUPEE_GANONS_CASTLE_SPIRIT_TRIAL, // Silver Rupee (Ganons Castle Spirit Trial)
    /* 0x00E9 */ GI_SILVER_RUPEE_GANONS_CASTLE_LIGHT_TRIAL, // Silver Rupee (Ganons Castle Light Trial)
    /* 0x00EA */ GI_SILVER_RUPEE_GANONS_CASTLE_FIRE_TRIAL, // Silver Rupee (Ganons Castle Fire Trial)
    /* 0x00EB */ GI_SILVER_RUPEE_GANONS_CASTLE_SHADOW_TRIAL, // Silver Rupee (Ganons Castle Shadow Trial)
    /* 0x00EC */ GI_SILVER_RUPEE_GANONS_CASTLE_WATER_TRIAL, // Silver Rupee (Ganons Castle Water Trial)
    /* 0x00ED */ GI_SILVER_RUPEE_GANONS_CASTLE_FOREST_TRIAL, // Silver Rupee (Ganons Castle Forest Trial)

    /* 0x00EE */ GI_SILVER_RUPEE_POUCH_DODONGOS_CAVERN_STAIRCASE, // Silver Rupee Pouch (Dodongos Cavern Staircase)
    /* 0x00EF */ GI_SILVER_RUPEE_POUCH_ICE_CAVERN_SPINNING_SCYTHE, // Silver Rupee Pouch (Ice Cavern Spinning Scythe)
    /* 0x00F0 */ GI_SILVER_RUPEE_POUCH_ICE_CAVERN_PUSH_BLOCK, // Silver Rupee Pouch (Ice Cavern Push Block)
    /* 0x00F1 */ GI_SILVER_RUPEE_POUCH_BOTTOM_OF_THE_WELL_BASEMENT, // Silver Rupee Pouch (Bottom of the Well Basement)
    /* 0x00F2 */ GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_SCYTHE_SHORTCUT, // Silver Rupee Pouch (Shadow Temple Scythe Shortcut)
    /* 0x00F3 */ GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_INVISIBLE_BLADES, // Silver Rupee Pouch (Shadow Temple Invisible Blades)
    /* 0x00F4 */ GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_HUGE_PIT, // Silver Rupee Pouch (Shadow Temple Huge Pit)
    /* 0x00F5 */ GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_INVISIBLE_SPIKES, // Silver Rupee Pouch (Shadow Temple Invisible Spikes)
    /* 0x00F6 */ GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_SLOPES, // Silver Rupee Pouch (Gerudo Training Ground Slopes)
    /* 0x00F7 */ GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_LAVA, // Silver Rupee Pouch (Gerudo Training Ground Lava)
    /* 0x00F8 */ GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_WATER, // Silver Rupee Pouch (Gerudo Training Ground Water)
    /* 0x00F9 */ GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_CHILD_EARLY_TORCHES, // Silver Rupee Pouch (Spirit Temple Child Early Torches)
    /* 0x00FA */ GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_ADULT_BOULDERS, // Silver Rupee Pouch (Spirit Temple Adult Boulders)
    /* 0x00FB */ GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_LOBBY_AND_LOWER_ADULT, // Silver Rupee Pouch (Spirit Temple Lobby and Lower Adult)
    /* 0x00FC */ GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_SUN_BLOCK, // Silver Rupee Pouch (Spirit Temple Sun Block)
    /* 0x00FD */ GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_ADULT_CLIMB, // Silver Rupee Pouch (Spirit Temple Adult Climb)
    /* 0x00FE */ GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_SPIRIT_TRIAL, // Silver Rupee Pouch (Ganons Castle Spirit Trial)
    /* 0x00FF */ GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_LIGHT_TRIAL, // Silver Rupee Pouch (Ganons Castle Light Trial)
    /* 0x0100 */ GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_FIRE_TRIAL, // Silver Rupee Pouch (Ganons Castle Fire Trial)
    /* 0x0101 */ GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_SHADOW_TRIAL, // Silver Rupee Pouch (Ganons Castle Shadow Trial)
    /* 0x0102 */ GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_WATER_TRIAL, // Silver Rupee Pouch (Ganons Castle Water Trial)
    /* 0x0103 */ GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_FOREST_TRIAL, // Silver Rupee Pouch (Ganons Castle Forest Trial)

    // Ocarina button models
    /* 0x0104 */ GI_OCARINA_BUTTON_A, // Ocarina A
    /* 0x0105 */ GI_OCARINA_BUTTON_C_UP, // Ocarina C up
    /* 0x0106 */ GI_OCARINA_BUTTON_C_DOWN, // Ocarina C down
    /* 0x0107 */ GI_OCARINA_BUTTON_C_LEFT, // Ocarina C left
    /* 0x0108 */ GI_OCARINA_BUTTON_C_RIGHT, // Ocarina C right

    // Custom Key Models
    /* 0x0109 */ GI_BOSS_KEY_MODEL_MIN,
    /* 0x0109 */ GI_BOSS_KEY_MODEL_FOREST_TEMPLE = GI_BOSS_KEY_MODEL_MIN, // Forest Temple Boss Key
    /* 0x010A */ GI_BOSS_KEY_MODEL_FIRE_TEMPLE, // Fire Temple Boss Key
    /* 0x010B */ GI_BOSS_KEY_MODEL_WATER_TEMPLE, // Water Temple Boss Key
    /* 0x010C */ GI_BOSS_KEY_MODEL_SPIRIT_TEMPLE, // Spirit Temple Boss Key
    /* 0x010D */ GI_BOSS_KEY_MODEL_SHADOW_TEMPLE, // Shadow Temple Boss Key
    /* 0x010E */ GI_BOSS_KEY_MODEL_GANONS_CASTLE, // Ganon's Castle Boss Key
    /* 0x010F */ GI_SMALL_KEY_MODEL_MIN,
    /* 0x010F */ GI_SMALL_KEY_MODEL_FOREST_TEMPLE = GI_SMALL_KEY_MODEL_MIN, // Forest Temple Small Key
    /* 0x0110 */ GI_SMALL_KEY_MODEL_FIRE_TEMPLE, // Fire Temple Small Key
    /* 0x0111 */ GI_SMALL_KEY_MODEL_WATER_TEMPLE, // Water Temple Small Key
    /* 0x0112 */ GI_SMALL_KEY_MODEL_SPIRIT_TEMPLE, // Spirit Temple Small Key
    /* 0x0113 */ GI_SMALL_KEY_MODEL_SHADOW_TEMPLE, // Shadow Temple Small Key
    /* 0x0114 */ GI_SMALL_KEY_MODEL_BOTTOM_OF_THE_WELL, // Bottom of the Well Small Key
    /* 0x0115 */ GI_SMALL_KEY_MODEL_GERUDO_TRAINING, // Gerudo Training Small Key
    /* 0x0116 */ GI_SMALL_KEY_MODEL_THIEVES_HIDEOUT, // Thieves' Hideout Small Key
    /* 0x0117 */ GI_SMALL_KEY_MODEL_MAX,
    /* 0x0117 */ GI_SMALL_KEY_MODEL_GANONS_CASTLE = GI_SMALL_KEY_MODEL_MAX, // Ganon's Castle Small Key
    /* 0x0118 */ GI_SMALL_KEY_MODEL_CHEST_GAME, // Small Key (Chest Game)

    /* 0x0119 */ GI_FAIRY,
    /* 0x011A */ GI_NOTHING,

    // 0x011B through 0x0126 reserved for https://github.com/OoTRandomizer/OoT-Randomizer/pull/2108

    // TODO: remove hardcoded value when that PR gets merged
    /* 0x0127 */ GI_KOKIRI_EMERALD = 0x0127,
    /* 0x0128 */ GI_GORON_RUBY,
    /* 0x0129 */ GI_ZORA_SAPPHIRE,
    /* 0x012A */ GI_LIGHT_MEDALLION,
    /* 0x012B */ GI_FOREST_MEDALLION,
    /* 0x012C */ GI_FIRE_MEDALLION,
    /* 0x012D */ GI_WATER_MEDALLION,
    /* 0x012E */ GI_SHADOW_MEDALLION,
    /* 0x012F */ GI_SPIRIT_MEDALLION,

    /* 0x0130 */ GI_RANDO_MAX
} GetItemId;

_Static_assert(GI_RANDO_MAX == 0x0130, "Remember to update the comment and the assert for the value of GI_RANDO_MAX when adding new items");

typedef enum {
    /*  0 */ BROWN_CHEST,            // big default chest
    /*  1 */ BIG_ROOM_CLEAR_CHEST,   // appear on room clear, store temp clear as permanent clear
    /*  2 */ GOLD_CHEST,             // boss key chest, different look, same as BROWN_CHEST otherwise
    /*  3 */ BIG_FALLING_CHEST,      // falling, appear on switch flag set
    /*  4 */ TYPE_4_CHEST,           // big, drawn differently
    /*  5 */ SMALL_CHEST,            // same as BROWN_CHEST but small
    /*  6 */ TYPE_6_CHEST,           // small, drawn differently
    /*  7 */ SMALL_ROOM_CLEAR_CHEST, // use room clear, store temp clear as perm clear
    /*  8 */ SMALL_FALLING_CHEST,    // falling, appear on switch flag set
    /*  9 */ TYPE_9_CHEST,           // big, has something more to do with player and message context?
    /* 10 */ TYPE_10_CHEST,          // like 9
    /* 11 */ BIG_SWITCH_FLAG_CHEST,  // big, appear on switch flag set
    /* 12 */ GILDED_CHEST,
    /* 13 */ SILVER_CHEST,
    /* 14 */ SKULL_CHEST_SMALL,
    /* 15 */ SKULL_CHEST_BIG,
    /* 16 */ HEART_CHEST_SMALL,
    /* 17 */ HEART_CHEST_BIG,
} ChestType;

struct item_row_t;

typedef uint16_t (*upgrade_fn)(z64_file_t* save, override_t override);
typedef void (*effect_fn)(z64_file_t* save, int16_t arg1, int16_t arg2);
typedef uint16_t (*alt_text_fn)(struct item_row_t* this, bool is_outgoing);

typedef struct item_row_t {
    int8_t      base_item_id;
    uint8_t     action_id;
    uint16_t    text_id;
    uint16_t    object_id;
    uint8_t     graphic_id;
    uint8_t     chest_type;
    upgrade_fn  upgrade;
    effect_fn   effect;
    int16_t     effect_arg1;
    int16_t     effect_arg2;
    int8_t      collectible;
    alt_text_fn alt_text_func;
} item_row_t;

uint16_t resolve_upgrades(override_t override);
item_row_t* get_item_row(uint16_t item_id);
void call_effect_function(item_row_t* item_row);
uint16_t resolve_item_text_id(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_silver_rupees(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_silver_rupee_pouches(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_small_keys(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_small_keys_cmg(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_keyrings(item_row_t* item_row, bool is_outgoing);

#endif
