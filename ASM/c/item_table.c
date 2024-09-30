#include "item_table.h"

#include "dungeon_info.h"
#include "item_effects.h"
#include "item_upgrades.h"
#include "save.h"
#include "util.h"
#include "z64.h"

extern uint8_t SHUFFLE_CHEST_GAME;

#define ITEM_ROW( \
        base_item_id_, chest_type_, action_id_, collectible_, text_id_, object_id_, graphic_id_, \
        upgrade_, effect_, effect_arg1_, effect_arg2_, alt_text_func_) \
    { .base_item_id = base_item_id_, .chest_type = chest_type_, .action_id = action_id_, \
      .collectible = collectible_, .text_id = text_id_, .object_id = object_id_, .graphic_id = graphic_id_, \
      .upgrade = upgrade_, .effect = effect_, \
      .effect_arg1 = effect_arg1_, .effect_arg2 = effect_arg2_, .alt_text_func = alt_text_func_}

// The "base item" mostly controls the sound effect made when you receive the item. It should be
// set to something that doesn't break NPCs. Good options include:
// 0x53 = Gerudo Mask (major item sound effect)
// 0x4D = Blue Rupee (minor item sound effect)

// Action ID 0x41 (give kokiri tunic) is used to indicate no action.

// "graphic id" - 1 indicates the entry used in the item_draw_table when rendering the GI model.

item_row_t item_table[GI_RANDO_MAX] = {
    [GI_BOMBS_5]                                                = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8E, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (5)
    [GI_DEKU_NUTS_5]                                            = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8C, 12, 0x90AA, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nuts (5)
    [GI_BOMBCHUS_10]                                            = ITEM_ROW(0x4D,       BROWN_CHEST, 0x09, -1, 0x90AB, 0x00D9, 0x28, bombchus_to_bag, no_effect, -1, -1, NULL), // Bombchu (10)
    [GI_BOW]                                                    = ITEM_ROW(0x53,      GILDED_CHEST, 0x03, -1, 0x0031, 0x00E9, 0x35, no_upgrade, no_effect, -1, -1, NULL), // Fairy Bow
    [GI_SLINGSHOT]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x06, -1, 0x0030, 0x00E7, 0x33, no_upgrade, no_effect, -1, -1, NULL), // Fairy Slingshot
    [GI_BOOMERANG]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x0E, -1, 0x0035, 0x00E8, 0x34, no_upgrade, no_effect, -1, -1, NULL), // Boomerang
    [GI_DEKU_STICKS_1]                                          = ITEM_ROW(0x4D,       BROWN_CHEST, 0x00, 13, 0x90AC, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Stick
    [GI_HOOKSHOT]                                               = ITEM_ROW(0x53,      GILDED_CHEST, 0x0A, -1, 0x0036, 0x00DD, 0x2D, no_upgrade, no_effect, -1, -1, NULL), // Hookshot
    [GI_LONGSHOT]                                               = ITEM_ROW(0x53,      GILDED_CHEST, 0x0B, -1, 0x004F, 0x00DD, 0x2E, no_upgrade, no_effect, -1, -1, NULL), // Longshot
    [GI_LENS_OF_TRUTH]                                          = ITEM_ROW(0x53,      GILDED_CHEST, 0x0F, -1, 0x0039, 0x00EA, 0x36, no_upgrade, no_effect, -1, -1, NULL), // Lens of Truth
    [GI_ZELDAS_LETTER]                                          = ITEM_ROW(0x53,      GILDED_CHEST, 0x23, -1, 0x0069, 0x00EF, 0x3B, no_upgrade, open_gate_and_mask_shop, 0x23, -1, NULL), // Zelda's Letter
    [GI_OCARINA_OF_TIME]                                        = ITEM_ROW(0x53,      GILDED_CHEST, 0x08, -1, 0x003A, 0x00DE, 0x2F, no_upgrade, no_effect, -1, -1, NULL), // Ocarina of Time
    [GI_HAMMER]                                                 = ITEM_ROW(0x53,      GILDED_CHEST, 0x11, -1, 0x0038, 0x00F6, 0x41, no_upgrade, no_effect, -1, -1, NULL), // Megaton Hammer
    [GI_COJIRO]                                                 = ITEM_ROW(0x53,      GILDED_CHEST, 0x2F, -1, 0x0002, 0x0109, 0x5E, no_upgrade, trade_quest_upgrade, 0x2F, -1, NULL), // Cojiro

    [GI_BOTTLE_EMPTY]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x14, -1, 0x0042, 0x00C6, 0x01, no_upgrade, no_effect, -1, -1, NULL), // Empty Bottle
    [GI_BOTTLE_POTION_RED]                                      = ITEM_ROW(0x53,      GILDED_CHEST, 0x15, -1, 0x0043, 0x00EB, 0x38, no_upgrade, no_effect, -1, -1, NULL), // Red Potion
    [GI_BOTTLE_POTION_GREEN]                                    = ITEM_ROW(0x53,      GILDED_CHEST, 0x16, -1, 0x0044, 0x00EB, 0x37, no_upgrade, no_effect, -1, -1, NULL), // Green Potion
    [GI_BOTTLE_POTION_BLUE]                                     = ITEM_ROW(0x53,      GILDED_CHEST, 0x17, -1, 0x0045, 0x00EB, 0x39, no_upgrade, no_effect, -1, -1, NULL), // Blue Potion
    [GI_BOTTLE_FAIRY]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x18, -1, 0x0046, 0x00C6, 0x01, no_upgrade, no_effect, -1, -1, NULL), // Bottled Fairy
    [GI_BOTTLE_MILK_FULL]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x1A, -1, 0x0098, 0x00DF, 0x30, no_upgrade, no_effect, -1, -1, NULL), // Bottled Lon Lon Milk
    [GI_BOTTLE_RUTOS_LETTER]                                    = ITEM_ROW(0x53,      GILDED_CHEST, 0x1B, -1, 0x0099, 0x010B, 0x45, letter_to_bottle, no_effect, -1, -1, NULL), // Bottled Ruto's Letter

    [GI_MAGIC_BEAN]                                             = ITEM_ROW(0x53,       BROWN_CHEST, 0x10, -1, 0x0048, 0x00F3, 0x3E, no_upgrade, no_effect, -1, -1, NULL), // Magic Bean
    [GI_MASK_SKULL]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x25, -1, 0x0010, 0x0136, 0x4F, no_upgrade, trade_quest_upgrade, 0x25, -1, NULL), // Skull Mask
    [GI_MASK_SPOOKY]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x26, -1, 0x0011, 0x0135, 0x32, no_upgrade, trade_quest_upgrade, 0x26, -1, NULL), // Spooky Mask
    [GI_CHICKEN]                                                = ITEM_ROW(0x53,      GILDED_CHEST, 0x22, -1, 0x000B, 0x0109, 0x44, no_upgrade, trade_quest_upgrade, 0x22, -1, NULL), // Chicken
    [GI_MASK_KEATON]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x24, -1, 0x0012, 0x0134, 0x31, no_upgrade, trade_quest_upgrade, 0x24, -1, NULL), // Keaton Mask
    [GI_MASK_BUNNY_HOOD]                                        = ITEM_ROW(0x53,      GILDED_CHEST, 0x27, -1, 0x0013, 0x0137, 0x50, no_upgrade, trade_quest_upgrade, 0x27, -1, NULL), // Bunny Hood
    [GI_MASK_TRUTH]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x2B, -1, 0x0017, 0x0138, 0x51, no_upgrade, trade_quest_upgrade, 0x2B, -1, NULL), // Mask of Truth
    [GI_POCKET_EGG]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x2D, -1, 0x9001, 0x00DA, 0x29, no_upgrade, trade_quest_upgrade, 0x2D, -1, NULL), // Pocket Egg
    [GI_POCKET_CUCCO]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x2E, -1, 0x000B, 0x0109, 0x44, no_upgrade, trade_quest_upgrade, 0x2E, -1, NULL), // Pocket Cucco
    [GI_ODD_MUSHROOM]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x30, -1, 0x0003, 0x0141, 0x54, no_upgrade, trade_quest_upgrade, 0x30, -1, NULL), // Odd Mushroom
    [GI_ODD_POTION]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x31, -1, 0x0004, 0x0140, 0x53, no_upgrade, trade_quest_upgrade, 0x31, -1, NULL), // Odd Potion
    [GI_POACHERS_SAW]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x32, -1, 0x0005, 0x00F5, 0x40, no_upgrade, trade_quest_upgrade, 0x32, -1, NULL), // Poacher's Saw
    [GI_BROKEN_GORONS_SWORD]                                    = ITEM_ROW(0x53,      GILDED_CHEST, 0x33, -1, 0x0008, 0x0143, 0x56, no_upgrade, trade_quest_upgrade, 0x33, -1, NULL), // Goron's Sword (Broken)
    [GI_PRESCRIPTION]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x34, -1, 0x0009, 0x0146, 0x57, no_upgrade, trade_quest_upgrade, 0x34, -1, NULL), // Prescription
    [GI_EYEBALL_FROG]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x35, -1, 0x000D, 0x0149, 0x5A, no_upgrade, trade_quest_upgrade, 0x35, -1, NULL), // Eyeball Frog
    [GI_EYE_DROPS]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x36, -1, 0x000E, 0x013F, 0x52, no_upgrade, trade_quest_upgrade, 0x36, -1, NULL), // Eye Drops
    [GI_CLAIM_CHECK]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x37, -1, 0x000A, 0x0142, 0x55, no_upgrade, trade_quest_upgrade, 0x37, -1, NULL), // Claim Check

    [GI_SWORD_KOKIRI]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x3B, -1, 0x00A4, 0x018D, 0x74, no_upgrade, no_effect, -1, -1, NULL), // Kokiri Sword
    [GI_SWORD_KNIFE]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x3D, -1, 0x004B, 0x00F8, 0x43, no_upgrade, no_effect, -1, -1, NULL), // Giant's Knife
    [GI_SHIELD_DEKU]                                            = ITEM_ROW(0x53,       BROWN_CHEST, 0x3E, -1, 0x90AD, 0x00CB, 0x1D, no_upgrade, no_effect, -1, -1, NULL), // Deku Shield
    [GI_SHIELD_HYLIAN]                                          = ITEM_ROW(0x53,       BROWN_CHEST, 0x3F, -1, 0x90AE, 0x00DC, 0x2C, no_upgrade, no_effect, -1, -1, NULL), // Hylian Shield
    [GI_SHIELD_MIRROR]                                          = ITEM_ROW(0x53,      GILDED_CHEST, 0x40, -1, 0x004E, 0x00EE, 0x3A, no_upgrade, no_effect, -1, -1, NULL), // Mirror Shield
    [GI_TUNIC_GORON]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x42, -1, 0x90AF, 0x00F2, 0x3C, no_upgrade, no_effect, -1, -1, NULL), // Goron Tunic
    [GI_TUNIC_ZORA]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x43, -1, 0x90B0, 0x00F2, 0x3D, no_upgrade, no_effect, -1, -1, NULL), // Zora Tunic
    [GI_BOOTS_IRON]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x45, -1, 0x0053, 0x0118, 0x47, no_upgrade, no_effect, -1, -1, NULL), // Iron Boots
    [GI_BOOTS_HOVER]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x46, -1, 0x0054, 0x0157, 0x5F, no_upgrade, no_effect, -1, -1, NULL), // Hover Boots
    [GI_QUIVER_40]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x4B, -1, 0x0056, 0x00BE, 0x16, no_upgrade, no_effect, -1, -1, NULL), // Big Quiver
    [GI_QUIVER_50]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x4C, -1, 0x0057, 0x00BE, 0x17, no_upgrade, no_effect, -1, -1, NULL), // Biggest Quiver
    [GI_BOMB_BAG_20]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x4D, -1, 0x0058, 0x00BF, 0x18, no_upgrade, no_effect, -1, -1, NULL), // Bomb Bag
    [GI_BOMB_BAG_30]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x4E, -1, 0x0059, 0x00BF, 0x19, no_upgrade, no_effect, -1, -1, NULL), // Big Bomb Bag
    [GI_BOMB_BAG_40]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x4F, -1, 0x005A, 0x00BF, 0x1A, no_upgrade, no_effect, -1, -1, NULL), // Biggest Bomb Bag
    [GI_SILVER_GAUNTLETS]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x51, -1, 0x005B, 0x012D, 0x49, no_upgrade, no_effect, -1, -1, NULL), // Silver Gauntlets
    [GI_GOLD_GAUNTLETS]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x52, -1, 0x005C, 0x012D, 0x4A, no_upgrade, no_effect, -1, -1, NULL), // Golden Gauntlets
    [GI_SCALE_SILVER]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x53, -1, 0x00CD, 0x00DB, 0x2A, no_upgrade, no_effect, -1, -1, NULL), // Silver Scale
    [GI_SCALE_GOLDEN]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x54, -1, 0x00CE, 0x00DB, 0x2B, no_upgrade, no_effect, -1, -1, NULL), // Golden Scale
    [GI_STONE_OF_AGONY]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x6F, -1, 0x0068, 0x00C8, 0x21, no_upgrade, no_effect, -1, -1, NULL), // Stone of Agony
    [GI_GERUDOS_CARD]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x70, -1, 0x007B, 0x00D7, 0x24, no_upgrade, no_effect, -1, -1, NULL), // Gerudo Membership Card

    [GI_OCARINA_FAIRY]                                          = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x004A, 0x010E, 0x46, no_upgrade, give_fairy_ocarina, -1, -1, NULL), // Fairy Ocarina
    [GI_DEKU_SEEDS_5]                                           = ITEM_ROW(0x4D,       BROWN_CHEST, 0x58, 16, 0x90B3, 0x0119, 0x48, seeds_to_rupee, no_effect, -1, -1, NULL), // Deku Seeds (5)
    [GI_HEART_CONTAINER]                                        = ITEM_ROW(0x3D, HEART_CHEST_SMALL, 0x72, -1, 0x00C6, 0x00BD, 0x13, health_upgrade_cap, clear_excess_hearts, -1, -1, NULL), // Heart Container
    [GI_HEART_PIECE]                                            = ITEM_ROW(0x3E, HEART_CHEST_SMALL, 0x7A, -1, 0x00C2, 0x00BD, 0x14, health_upgrade_cap, full_heal, -1, -1, NULL), // Piece of Heart
    [GI_BOSS_KEY]                                               = ITEM_ROW(0x53,        GOLD_CHEST, 0x74, -1, 0x00C7, 0x00B9, 0x0A, no_upgrade, no_effect, -1, -1, NULL), // Boss Key
    [GI_COMPASS]                                                = ITEM_ROW(0x53,       BROWN_CHEST, 0x75, -1, 0x0067, 0x00B8, 0x0B, no_upgrade, no_effect, -1, -1, NULL), // Compass
    [GI_DUNGEON_MAP]                                            = ITEM_ROW(0x53,       BROWN_CHEST, 0x76, -1, 0x0066, 0x00C8, 0x1C, no_upgrade, no_effect, -1, -1, NULL), // Map
    [GI_SMALL_KEY]                                              = ITEM_ROW(0x53,      SILVER_CHEST, 0x77, -1, 0x0060, 0x00AA, 0x02, no_upgrade, no_effect, -1, -1, NULL), // Small Key
    [GI_MAGIC_JAR_SMALL]                                        = ITEM_ROW(0x53,       BROWN_CHEST, 0x78, -1, 0x0052, 0x00CD, 0x1E, no_upgrade, no_effect, -1, -1, NULL), // Small Magic Jar
    [GI_MAGIC_JAR_LARGE]                                        = ITEM_ROW(0x53,       BROWN_CHEST, 0x79, -1, 0x0052, 0x00CD, 0x1F, no_upgrade, no_effect, -1, -1, NULL), // Large Magic Jar
    [GI_WALLET_ADULT]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x56, -1, 0x005E, 0x00D1, 0x22, no_upgrade, fill_wallet_upgrade, 1, -1, NULL), // Adult's Wallet
    [GI_WALLET_GIANT]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x57, -1, 0x005F, 0x00D1, 0x23, no_upgrade, fill_wallet_upgrade, 2, -1, NULL), // Giant's Wallet
    [GI_WEIRD_EGG]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x21, -1, 0x009A, 0x00DA, 0x29, no_upgrade, trade_quest_upgrade, 0x21, -1, NULL), // Weird Egg
    [GI_RECOVERY_HEART]                                         = ITEM_ROW(0x4D,       BROWN_CHEST, 0x83,  3, 0x90B1, 0x00B7, 0x09, no_upgrade, no_effect, -1, -1, NULL), // Recovery Heart
    [GI_ARROWS_5]                                               = ITEM_ROW(0x4D,       BROWN_CHEST, 0x92,  8, 0x90B2, 0x00D8, 0x25, arrows_to_rupee, no_effect, -1, -1, NULL), // Arrows (5)
    [GI_ARROWS_10]                                              = ITEM_ROW(0x4D,       BROWN_CHEST, 0x93,  9, 0x90B2, 0x00D8, 0x26, arrows_to_rupee, no_effect, -1, -1, NULL), // Arrows (10)
    [GI_ARROWS_30]                                              = ITEM_ROW(0x4D,       BROWN_CHEST, 0x94, 10, 0x90B2, 0x00D8, 0x27, arrows_to_rupee, no_effect, -1, -1, NULL), // Arrows (30)
    [GI_RUPEE_GREEN]                                            = ITEM_ROW(0x4D,       BROWN_CHEST, 0x84,  0, 0x006F, 0x017F, 0x6D, no_upgrade, no_effect, -1, -1, NULL), // Green Rupee
    [GI_RUPEE_BLUE]                                             = ITEM_ROW(0x4D,       BROWN_CHEST, 0x85,  1, 0x00CC, 0x017F, 0x6E, no_upgrade, no_effect, -1, -1, NULL), // Blue Rupee
    [GI_RUPEE_RED]                                              = ITEM_ROW(0x4D,       BROWN_CHEST, 0x86,  2, 0x00F0, 0x017F, 0x6F, no_upgrade, no_effect, -1, -1, NULL), // Red Rupee
    [GI_HEART_CONTAINER_2]                                      = ITEM_ROW(0x3D, HEART_CHEST_SMALL, 0x72, -1, 0x00C6, 0x00BD, 0x13, no_upgrade, full_heal, -1, -1, NULL), // Heart Container
    [GI_MILK]                                                   = ITEM_ROW(0x53,      GILDED_CHEST, 0x82, -1, 0x0098, 0x00DF, 0x30, no_upgrade, no_effect, -1, -1, NULL), // Lon Lon Milk (Refill)
    [GI_MASK_GORON]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x28, -1, 0x0014, 0x0150, 0x5B, no_upgrade, trade_quest_upgrade, 0x28, -1, NULL), // Goron Mask
    [GI_MASK_ZORA]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x29, -1, 0x0015, 0x0151, 0x5C, no_upgrade, trade_quest_upgrade, 0x29, -1, NULL), // Zora Mask
    [GI_MASK_GERUDO]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x2A, -1, 0x0016, 0x0152, 0x5D, no_upgrade, trade_quest_upgrade, 0x2A, -1, NULL), // Gerudo Mask
    [GI_GORONS_BRACELET]                                        = ITEM_ROW(0x53,      GILDED_CHEST, 0x50, -1, 0x0079, 0x0147, 0x58, no_upgrade, no_effect, -1, -1, NULL), // Goron's Bracelet
    [GI_RUPEE_PURPLE]                                           = ITEM_ROW(0x4D,       BROWN_CHEST, 0x87, 20, 0x00F1, 0x017F, 0x71, no_upgrade, no_effect, -1, -1, NULL), // Purple Rupee
    [GI_RUPEE_GOLD]                                             = ITEM_ROW(0x4D,       BROWN_CHEST, 0x88, 19, 0x00F2, 0x017F, 0x72, no_upgrade, no_effect, -1, -1, NULL), // Huge Rupee
    [GI_SWORD_BIGGORON]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x3D, -1, 0x000C, 0x00F8, 0x43, no_upgrade, give_biggoron_sword, -1, -1, NULL), // Biggoron's Sword
    [GI_ARROW_FIRE]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x04, -1, 0x0070, 0x0158, 0x60, no_upgrade, no_effect, -1, -1, NULL), // Fire Arrow
    [GI_ARROW_ICE]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x0C, -1, 0x0071, 0x0158, 0x61, no_upgrade, no_effect, -1, -1, NULL), // Ice Arrow
    [GI_ARROW_LIGHT]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x12, -1, 0x0072, 0x0158, 0x62, no_upgrade, no_effect, -1, -1, NULL), // Light Arrow
    [GI_SKULL_TOKEN]                                            = ITEM_ROW(0x5B, SKULL_CHEST_SMALL, 0x71, -1, 0x00B4, 0x015C, 0x63, no_upgrade, no_effect, -1, -1, NULL), // Gold Skulltula Token
    [GI_DINS_FIRE]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x05, -1, 0x00AD, 0x015D, 0x64, no_upgrade, no_effect, -1, -1, NULL), // Din's Fire
    [GI_FARORES_WIND]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x0D, -1, 0x00AE, 0x015D, 0x65, no_upgrade, no_effect, -1, -1, NULL), // Farore's Wind
    [GI_NAYRUS_LOVE]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x13, -1, 0x00AF, 0x015D, 0x66, no_upgrade, no_effect, -1, -1, NULL), // Nayru's Love
    [GI_BULLET_BAG_30]                                          = ITEM_ROW(0x53,      GILDED_CHEST, 0x47, -1, 0x0007, 0x017B, 0x6C, no_upgrade, no_effect, -1, -1, NULL), // Bullet Bag (30)
    [GI_BULLET_BAG_40]                                          = ITEM_ROW(0x53,      GILDED_CHEST, 0x48, -1, 0x0007, 0x017B, 0x6C, no_upgrade, no_effect, -1, -1, NULL), // Bullet Bag (40)
    [GI_DEKU_STICKS_5]                                          = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8A, 13, 0x90AC, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Sticks (5)
    [GI_DEKU_STICKS_10]                                         = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8B, 13, 0x90AC, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Sticks (10)
    [GI_DEKU_NUTS_5_2]                                          = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8C, 12, 0x90AA, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nuts (5)
    [GI_DEKU_NUTS_10]                                           = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8D, 12, 0x90AA, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nuts (10)
    [GI_BOMBS_1]                                                = ITEM_ROW(0x4D,       BROWN_CHEST, 0x02, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bomb
    [GI_BOMBS_10]                                               = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8F, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (10)
    [GI_BOMBS_20]                                               = ITEM_ROW(0x4D,       BROWN_CHEST, 0x90, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (20)
    [GI_BOMBS_30]                                               = ITEM_ROW(0x4D,       BROWN_CHEST, 0x91, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (30)
    [GI_DEKU_SEEDS_30]                                          = ITEM_ROW(0x4D,       BROWN_CHEST, 0x95, 16, 0x90B3, 0x0119, 0x48, seeds_to_rupee, no_effect, -1, -1, NULL), // Deku Seeds (30)
    [GI_BOMBCHUS_5]                                             = ITEM_ROW(0x4D,       BROWN_CHEST, 0x96, -1, 0x90AB, 0x00D9, 0x28, bombchus_to_bag, no_effect, -1, -1, NULL), // Bombchu (5)
    [GI_BOMBCHUS_20]                                            = ITEM_ROW(0x4D,       BROWN_CHEST, 0x97, -1, 0x90AB, 0x00D9, 0x28, bombchus_to_bag, no_effect, -1, -1, NULL), // Bombchu (20)
    [GI_BOTTLE_FISH]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x19, -1, 0x0047, 0x00F4, 0x3F, no_upgrade, no_effect, -1, -1, NULL), // Fish (Refill)
    [GI_BOTTLE_BUGS]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x1D, -1, 0x007A, 0x0174, 0x68, no_upgrade, no_effect, -1, -1, NULL), // Bugs (Refill)
    [GI_BOTTLE_BLUE_FIRE]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x1C, -1, 0x005D, 0x0173, 0x67, no_upgrade, no_effect, -1, -1, NULL), // Blue Fire (Refill)
    [GI_BOTTLE_POE]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x20, -1, 0x0097, 0x0176, 0x6A, no_upgrade, no_effect, -1, -1, NULL), // Poe (Refill)
    [GI_BOTTLE_BIG_POE]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x1E, -1, 0x00F9, 0x0176, 0x70, no_upgrade, no_effect, -1, -1, NULL), // Big Poe (Refill)
    [GI_DOOR_KEY]                                               = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00F3, 0x00AA, 0x02, upgrade_key_model, give_small_key, TCG_ID, -1, resolve_text_small_keys_cmg), // Small Key (Chest Game)
    [GI_RUPEE_GREEN_LOSE]                                       = ITEM_ROW(0x4D,       BROWN_CHEST, 0x84, -1, 0x00F4, 0x017F, 0x6D, no_upgrade, no_effect, -1, -1, NULL), // Green Rupee (Chest Game)
    [GI_RUPEE_BLUE_LOSE]                                        = ITEM_ROW(0x4D,       BROWN_CHEST, 0x85, -1, 0x00F5, 0x017F, 0x6E, no_upgrade, no_effect, -1, -1, NULL), // Blue Rupee (Chest Game)
    [GI_RUPEE_RED_LOSE]                                         = ITEM_ROW(0x4D,       BROWN_CHEST, 0x86, -1, 0x00F6, 0x017F, 0x6F, no_upgrade, no_effect, -1, -1, NULL), // Red Rupee (Chest Game)
    [GI_RUPEE_PURPLE_LOSE]                                      = ITEM_ROW(0x4D,       BROWN_CHEST, 0x87, -1, 0x00F7, 0x017F, 0x71, no_upgrade, no_effect, -1, -1, NULL), // Purple Rupee (Chest Game)
    [GI_HEART_PIECE_WIN]                                        = ITEM_ROW(0x53, HEART_CHEST_SMALL, 0x7A, -1, 0x00FA, 0x00BD, 0x14, health_upgrade_cap, full_heal, -1, -1, NULL), // Piece of Heart (Chest Game)
    [GI_DEKU_STICK_UPGRADE_20]                                  = ITEM_ROW(0x53,       BROWN_CHEST, 0x98, -1, 0x0090, 0x00C7, 0xA1, no_upgrade, no_effect, -1, -1, NULL), // Deku Stick Upgrade (20)
    [GI_DEKU_STICK_UPGRADE_30]                                  = ITEM_ROW(0x53,       BROWN_CHEST, 0x99, -1, 0x0091, 0x00C7, 0xA1, no_upgrade, no_effect, -1, -1, NULL), // Deku Stick Upgrade (30)
    [GI_DEKU_NUT_UPGRADE_30]                                    = ITEM_ROW(0x53,       BROWN_CHEST, 0x9A, -1, 0x00A7, 0x00BB, 0xA2, no_upgrade, no_effect, -1, -1, NULL), // Deku Nut Upgrade (30)
    [GI_DEKU_NUT_UPGRADE_40]                                    = ITEM_ROW(0x53,       BROWN_CHEST, 0x9B, -1, 0x00A8, 0x00BB, 0xA2, no_upgrade, no_effect, -1, -1, NULL), // Deku Nut Upgrade (40)
    [GI_BULLET_BAG_50]                                          = ITEM_ROW(0x53,      GILDED_CHEST, 0x49, -1, 0x006C, 0x017B, 0x73, no_upgrade, no_effect, -1, -1, NULL), // Bullet Bag (50)
    [GI_ICE_TRAP]                                               = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9002, 0x0000, 0x00, no_upgrade, ice_trap_effect, -1, -1, NULL), // Ice Trap

    [GI_CAPPED_PIECE_OF_HEART]                                  = ITEM_ROW(0x3E, HEART_CHEST_SMALL, 0x41, -1, 0x90C2, 0x00BD, 0x14, no_upgrade, full_heal, -1, -1, NULL), // Capped Piece of Heart
    [GI_CAPPED_HEART_CONTAINER]                                 = ITEM_ROW(0x3E, HEART_CHEST_SMALL, 0x41, -1, 0x90C6, 0x00BD, 0x13, no_upgrade, full_heal, -1, -1, NULL), // Capped Heart Container
    [GI_CAPPED_PIECE_OF_HEART_CHESTGAME]                        = ITEM_ROW(0x53, HEART_CHEST_SMALL, 0x41, -1, 0x90FA, 0x00BD, 0x14, no_upgrade, full_heal, -1, -1, NULL), // Capped Piece of Heart (Chest Game)

    [GI_PROGRESSIVE_HOOKSHOT]                                   = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00DD, 0x2D, hookshot_upgrade,  no_effect, -1, -1, NULL), // Progressive Hookshot
    [GI_PROGRESSIVE_STRENGTH]                                   = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x0147, 0x58, strength_upgrade,  no_effect, -1, -1, NULL), // Progressive Strength
    [GI_PROGRESSIVE_BOMB_BAG]                                   = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00BF, 0x18, bomb_bag_upgrade,  no_effect, -1, -1, NULL), // Progressive Bomb Bag
    [GI_PROGRESSIVE_BOW]                                        = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00E9, 0x35, bow_upgrade,       no_effect, -1, -1, NULL), // Progressive Bow
    [GI_PROGRESSIVE_SLINGSHOT]                                  = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00E7, 0x33, slingshot_upgrade, no_effect, -1, -1, NULL), // Progressive Slingshot
    [GI_PROGRESSIVE_WALLET]                                     = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00D1, 0x22, wallet_upgrade,    no_effect, -1, -1, NULL), // Progressive Wallet
    [GI_PROGRESSIVE_SCALE]                                      = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00DB, 0x2A, scale_upgrade,     no_effect, -1, -1, NULL), // Progressive Scale
    [GI_PROGRESSIVE_NUT_CAPACITY]                               = ITEM_ROW(  -1,       BROWN_CHEST,   -1, -1,     -1, 0x00BB, 0xA2, nut_upgrade,       no_effect, -1, -1, NULL), // Progressive Nut Capacity
    [GI_PROGRESSIVE_STICK_CAPACITY]                             = ITEM_ROW(  -1,       BROWN_CHEST,   -1, -1,     -1, 0x00C7, 0xA1, stick_upgrade,     no_effect, -1, -1, NULL), // Progressive Stick Capacity
    [GI_PROGRESSIVE_BOMBCHUS]                                   = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00D9, 0x28, bombchu_upgrade,   no_effect, -1, -1, NULL), // Progressive Bombchus
    [GI_PROGRESSIVE_MAGIC_METER]                                = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00CD, 0x1E, magic_upgrade,     no_effect, -1, -1, NULL), // Progressive Magic Meter
    [GI_PROGRESSIVE_OCARINA]                                    = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x010E, 0x46, ocarina_upgrade,   no_effect, -1, -1, NULL), // Progressive Ocarina

    [GI_BOTTLE_WITH_RED_POTION]                                 = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A0, 0x00C6, 0x01, no_upgrade, give_bottle, 0x15, -1, NULL), // Bottle with Red Potion
    [GI_BOTTLE_WITH_GREEN_POTION]                               = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A1, 0x00C6, 0x01, no_upgrade, give_bottle, 0x16, -1, NULL), // Bottle with Green Potion
    [GI_BOTTLE_WITH_BLUE_POTION]                                = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A2, 0x00C6, 0x01, no_upgrade, give_bottle, 0x17, -1, NULL), // Bottle with Blue Potion
    [GI_BOTTLE_WITH_FAIRY]                                      = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A3, 0x0177, 0x6B, no_upgrade, give_bottle, 0x18, -1, NULL), // Bottle with Fairy
    [GI_BOTTLE_WITH_FISH]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A4, 0x00F4, 0x3F, no_upgrade, give_bottle, 0x19, -1, NULL), // Bottle with Fish
    [GI_BOTTLE_WITH_BLUE_FIRE]                                  = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A5, 0x0173, 0x67, no_upgrade, give_bottle, 0x1C, -1, NULL), // Bottle with Blue Fire
    [GI_BOTTLE_WITH_BUGS]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A6, 0x0174, 0x68, no_upgrade, give_bottle, 0x1D, -1, NULL), // Bottle with Bugs
    [GI_BOTTLE_WITH_BIG_POE]                                    = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A7, 0x0176, 0x70, no_upgrade, give_bottle, 0x1E, -1, NULL), // Bottle with Big Poe
    [GI_BOTTLE_WITH_POE]                                        = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A8, 0x0176, 0x6A, no_upgrade, give_bottle, 0x20, -1, NULL), // Bottle with Poe

    [GI_BOSS_KEY_FOREST_TEMPLE]                                 = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0006, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, FOREST_ID, NULL), // Forest Temple Boss Key
    [GI_BOSS_KEY_FIRE_TEMPLE]                                   = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001C, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, FIRE_ID,   NULL), // Fire Temple Boss Key
    [GI_BOSS_KEY_WATER_TEMPLE]                                  = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001D, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, WATER_ID,  NULL), // Water Temple Boss Key
    [GI_BOSS_KEY_SPIRIT_TEMPLE]                                 = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001E, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, SPIRIT_ID, NULL), // Spirit Temple Boss Key
    [GI_BOSS_KEY_SHADOW_TEMPLE]                                 = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x002A, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, SHADOW_ID, NULL), // Shadow Temple Boss Key
    [GI_BOSS_KEY_GANONS_CASTLE]                                 = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0061, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, TOWER_ID,  NULL), // Ganon's Castle Boss Key

    [GI_COMPASS_DEKU_TREE]                                      = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0062, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, DEKU_ID,    NULL), // Deku Tree Compass
    [GI_COMPASS_DODONGOS_CAVERN]                                = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0063, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, DODONGO_ID, NULL), // Dodongo's Cavern Compass
    [GI_COMPASS_JABU_JABU]                                      = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0064, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, JABU_ID,    NULL), // Jabu Jabu Compass
    [GI_COMPASS_FOREST_TEMPLE]                                  = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0065, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, FOREST_ID,  NULL), // Forest Temple Compass
    [GI_COMPASS_FIRE_TEMPLE]                                    = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007C, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, FIRE_ID,    NULL), // Fire Temple Compass
    [GI_COMPASS_WATER_TEMPLE]                                   = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007D, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, WATER_ID,   NULL), // Water Temple Compass
    [GI_COMPASS_SPIRIT_TEMPLE]                                  = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007E, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, SPIRIT_ID,  NULL), // Spirit Temple Compass
    [GI_COMPASS_SHADOW_TEMPLE]                                  = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007F, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, SHADOW_ID,  NULL), // Shadow Temple Compass
    [GI_COMPASS_BOTTOM_OF_THE_WELL]                             = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x00A2, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, BOTW_ID,    NULL), // Bottom of the Well Compass
    [GI_COMPASS_ICE_CAVERN]                                     = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0087, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, ICE_ID,     NULL), // Ice Cavern Compass

    [GI_MAP_DEKU_TREE]                                          = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0088, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, DEKU_ID,    NULL), // Deku Tree Map
    [GI_MAP_DODONGOS_CAVERN]                                    = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0089, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, DODONGO_ID, NULL), // Dodongo's Cavern Map
    [GI_MAP_JABU_JABU]                                          = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008A, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, JABU_ID,    NULL), // Jabu Jabu Map
    [GI_MAP_FOREST_TEMPLE]                                      = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008B, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, FOREST_ID,  NULL), // Forest Temple Map
    [GI_MAP_FIRE_TEMPLE]                                        = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008C, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, FIRE_ID,    NULL), // Fire Temple Map
    [GI_MAP_WATER_TEMPLE]                                       = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008E, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, WATER_ID,   NULL), // Water Temple Map
    [GI_MAP_SPIRIT_TEMPLE]                                      = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008F, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, SPIRIT_ID,  NULL), // Spirit Temple Map
    [GI_MAP_SHADOW_TEMPLE]                                      = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x00A3, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, SHADOW_ID,  NULL), // Shadow Temple Map
    [GI_MAP_BOTTOM_OF_THE_WELL]                                 = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x00A5, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, BOTW_ID,    NULL), // Bottom of the Well Map
    [GI_MAP_ICE_CAVERN]                                         = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0092, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, ICE_ID,     NULL), // Ice Cavern Map

    [GI_SMALL_KEY_FOREST_TEMPLE]                                = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0093, 0x00AA, 0x02, upgrade_key_model, give_small_key, FOREST_ID, -1, resolve_text_small_keys), // Forest Temple Small Key
    [GI_SMALL_KEY_FIRE_TEMPLE]                                  = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0094, 0x00AA, 0x02, upgrade_key_model, give_small_key, FIRE_ID,   -1, resolve_text_small_keys), // Fire Temple Small Key
    [GI_SMALL_KEY_WATER_TEMPLE]                                 = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0095, 0x00AA, 0x02, upgrade_key_model, give_small_key, WATER_ID,  -1, resolve_text_small_keys), // Water Temple Small Key
    [GI_SMALL_KEY_SPIRIT_TEMPLE]                                = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A6, 0x00AA, 0x02, upgrade_key_model, give_small_key, SPIRIT_ID, -1, resolve_text_small_keys), // Spirit Temple Small Key
    [GI_SMALL_KEY_SHADOW_TEMPLE]                                = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A9, 0x00AA, 0x02, upgrade_key_model, give_small_key, SHADOW_ID, -1, resolve_text_small_keys), // Shadow Temple Small Key
    [GI_SMALL_KEY_BOTTOM_OF_THE_WELL]                           = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009B, 0x00AA, 0x02, upgrade_key_model, give_small_key, BOTW_ID,   -1, resolve_text_small_keys), // Bottom of the Well Small Key
    [GI_SMALL_KEY_GERUDO_TRAINING]                              = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009F, 0x00AA, 0x02, upgrade_key_model, give_small_key, GTG_ID,    -1, resolve_text_small_keys), // Gerudo Training Small Key
    [GI_SMALL_KEY_THIEVES_HIDEOUT]                              = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A0, 0x00AA, 0x02, upgrade_key_model, give_small_key, FORT_ID,   -1, resolve_text_small_keys), // Thieves' Hideout Small Key
    [GI_SMALL_KEY_GANONS_CASTLE]                                = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A1, 0x00AA, 0x02, upgrade_key_model, give_small_key, CASTLE_ID, -1, resolve_text_small_keys), // Ganon's Castle Small Key

    [GI_DOUBLE_DEFENSE]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00E9, 0x0194, 0x13, no_upgrade, give_defense,      -1, -1, NULL), // Double Defense
    [GI_MAGIC_METER]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00E4, 0x01B4, 0xA0, no_upgrade, give_magic,        -1, -1, NULL), // Magic Meter
    [GI_DOUBLE_MAGIC]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00E8, 0x01B4, 0xA0, no_upgrade, give_double_magic, -1, -1, NULL), // Double Magic

    [GI_MINUET_OF_FOREST]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9091, 0x0196, 0x78, no_upgrade, give_quest_item,  6, -1, NULL), // Minuet of Forest
    [GI_BOLERO_OF_FIRE]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9092, 0x0196, 0x79, no_upgrade, give_quest_item,  7, -1, NULL), // Bolero of Fire
    [GI_SERENADE_OF_WATER]                                      = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9093, 0x0196, 0x7A, no_upgrade, give_quest_item,  8, -1, NULL), // Serenade of Water
    [GI_REQUIEM_OF_SPIRIT]                                      = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9094, 0x0196, 0x7B, no_upgrade, give_quest_item,  9, -1, NULL), // Requiem of Spirit
    [GI_NOCTURNE_OF_SHADOW]                                     = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9095, 0x0196, 0x7C, no_upgrade, give_quest_item, 10, -1, NULL), // Nocturn of Shadow
    [GI_PRELUDE_OF_LIGHT]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9096, 0x0196, 0x7D, no_upgrade, give_quest_item, 11, -1, NULL), // Prelude of Light

    [GI_ZELDAS_LULLABY]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909A, 0x00B6, 0x04, no_upgrade, give_quest_item, 12, -1, NULL), // Zelda's Lullaby
    [GI_EPONAS_SONG]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909B, 0x00B6, 0x06, no_upgrade, give_quest_item, 13, -1, NULL), // Epona's Song
    [GI_SARIAS_SONG]                                            = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909C, 0x00B6, 0x03, no_upgrade, give_quest_item, 14, -1, NULL), // Saria's Song
    [GI_SUNS_SONG]                                              = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909D, 0x00B6, 0x08, no_upgrade, give_quest_item, 15, -1, NULL), // Sun's Song
    [GI_SONG_OF_TIME]                                           = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909E, 0x00B6, 0x05, no_upgrade, give_quest_item, 16, -1, NULL), // Song of Time
    [GI_SONG_OF_STORMS]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909F, 0x00B6, 0x07, no_upgrade, give_quest_item, 17, -1, NULL), // Song of Storms

    [GI_TYCOONS_WALLET]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00F8, 0x00D1, 0x23, no_upgrade, give_tycoon_wallet,   3, -1, NULL), // Tycoon's Wallet
    [GI_REDUNDANT_LETTER_BOTTLE]                                = ITEM_ROW(0x53,      GILDED_CHEST, 0x14, -1, 0x9099, 0x010B, 0x45, no_upgrade, no_effect,           -1, -1, NULL), // Redundant Letter Bottle
    [GI_MAGIC_BEAN_PACK]                                        = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9048, 0x00F3, 0x3E, no_upgrade, give_bean_pack,      -1, -1, NULL), // Magic Bean Pack
    [GI_TRIFORCE_PIECE]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9003, 0x0193, 0x76, no_upgrade, give_triforce_piece, -1, -1, NULL), // Triforce piece

    [GI_SMALL_KEY_RING_FOREST_TEMPLE]                           = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, FOREST_ID, 1, resolve_text_keyrings), // Forest Temple Small Key Ring
    [GI_SMALL_KEY_RING_FIRE_TEMPLE]                             = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, FIRE_ID,   1, resolve_text_keyrings), // Fire Temple Small Key Ring
    [GI_SMALL_KEY_RING_WATER_TEMPLE]                            = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, WATER_ID,  1, resolve_text_keyrings), // Water Temple Small Key Ring
    [GI_SMALL_KEY_RING_SPIRIT_TEMPLE]                           = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, SPIRIT_ID, 1, resolve_text_keyrings), // Spirit Temple Small Key Ring
    [GI_SMALL_KEY_RING_SHADOW_TEMPLE]                           = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, SHADOW_ID, 1, resolve_text_keyrings), // Shadow Temple Small Key Ring
    [GI_SMALL_KEY_RING_BOTTOM_OF_THE_WELL]                      = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, BOTW_ID,   0, resolve_text_keyrings), // Bottom of the Well Small Key Ring
    [GI_SMALL_KEY_RING_GERUDO_TRAINING]                         = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, GTG_ID,    0, resolve_text_keyrings), // Gerudo Training Small Key Ring
    [GI_SMALL_KEY_RING_THIEVES_HIDEOUT]                         = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, FORT_ID,   0, resolve_text_keyrings), // Thieves' Hideout Small Key Ring
    [GI_SMALL_KEY_RING_GANONS_CASTLE]                           = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, CASTLE_ID, 0, resolve_text_keyrings), // Ganon's Castle Small Key Ring

    [GI_BOMBCHU_BAG_20]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9019, 0x0197, 0x7E, no_upgrade, give_bombchus, 20, -1, NULL), // Bombchu Bag (20)
    [GI_BOMBCHU_BAG_10]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9019, 0x0197, 0x7E, no_upgrade, give_bombchus, 10, -1, NULL), // Bombchu Bag (10)
    [GI_BOMBCHU_BAG_5]                                          = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9019, 0x0197, 0x7E, no_upgrade, give_bombchus,  5, -1, NULL), // Bombchu Bag (5)

    [GI_SMALL_KEY_RING_TREASURE_CHEST_GAME]                     = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, TCG_ID, 0, resolve_text_keyrings), // Treasure Chest Game Small Key Ring

    [GI_SILVER_RUPEE_DODONGOS_CAVERN_STAIRCASE]                 = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901B, 0x0198, 0x72, no_upgrade, give_silver_rupee, DODONGO_ID, 0x00, resolve_text_silver_rupees), // Silver Rupee (Dodongos Cavern Staircase)
    [GI_SILVER_RUPEE_ICE_CAVERN_SPINNING_SCYTHE]                = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901C, 0x0198, 0x72, no_upgrade, give_silver_rupee, ICE_ID,     0x01, resolve_text_silver_rupees), // Silver Rupee (Ice Cavern Spinning Scythe)
    [GI_SILVER_RUPEE_ICE_CAVERN_PUSH_BLOCK]                     = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901D, 0x0198, 0x72, no_upgrade, give_silver_rupee, ICE_ID,     0x02, resolve_text_silver_rupees), // Silver Rupee (Ice Cavern Push Block)
    [GI_SILVER_RUPEE_BOTTOM_OF_THE_WELL_BASEMENT]               = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901E, 0x0198, 0x72, no_upgrade, give_silver_rupee, BOTW_ID,    0x03, resolve_text_silver_rupees), // Silver Rupee (Bottom of the Well Basement)
    [GI_SILVER_RUPEE_SHADOW_TEMPLE_SCYTHE_SHORTCUT]             = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901F, 0x0198, 0x72, no_upgrade, give_silver_rupee, SHADOW_ID,  0x04, resolve_text_silver_rupees), // Silver Rupee (Shadow Temple Scythe Shortcut)
    [GI_SILVER_RUPEE_SHADOW_TEMPLE_INVISIBLE_BLADES]            = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9020, 0x0198, 0x72, no_upgrade, give_silver_rupee, SHADOW_ID,  0x05, resolve_text_silver_rupees), // Silver Rupee (Shadow Temple Invisible Blades)
    [GI_SILVER_RUPEE_SHADOW_TEMPLE_HUGE_PIT]                    = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9021, 0x0198, 0x72, no_upgrade, give_silver_rupee, SHADOW_ID,  0x06, resolve_text_silver_rupees), // Silver Rupee (Shadow Temple Huge Pit)
    [GI_SILVER_RUPEE_SHADOW_TEMPLE_INVISIBLE_SPIKES]            = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9022, 0x0198, 0x72, no_upgrade, give_silver_rupee, SHADOW_ID,  0x07, resolve_text_silver_rupees), // Silver Rupee (Shadow Temple Invisible Spikes)
    [GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_SLOPES]             = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9023, 0x0198, 0x72, no_upgrade, give_silver_rupee, GTG_ID,     0x08, resolve_text_silver_rupees), // Silver Rupee (Gerudo Training Ground Slopes)
    [GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_LAVA]               = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9024, 0x0198, 0x72, no_upgrade, give_silver_rupee, GTG_ID,     0x09, resolve_text_silver_rupees), // Silver Rupee (Gerudo Training Ground Lava)
    [GI_SILVER_RUPEE_GERUDO_TRAINING_GROUND_WATER]              = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9025, 0x0198, 0x72, no_upgrade, give_silver_rupee, GTG_ID,     0x0A, resolve_text_silver_rupees), // Silver Rupee (Gerudo Training Ground Water)
    [GI_SILVER_RUPEE_SPIRIT_TEMPLE_CHILD_EARLY_TORCHES]         = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9026, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0B, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Child Early Torches)
    [GI_SILVER_RUPEE_SPIRIT_TEMPLE_ADULT_BOULDERS]              = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9027, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0C, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Adult Boulders)
    [GI_SILVER_RUPEE_SPIRIT_TEMPLE_LOBBY_AND_LOWER_ADULT]       = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9028, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0D, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Lobby and Lower Adult)
    [GI_SILVER_RUPEE_SPIRIT_TEMPLE_SUN_BLOCK]                   = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9029, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0E, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Sun Block)
    [GI_SILVER_RUPEE_SPIRIT_TEMPLE_ADULT_CLIMB]                 = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902A, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0F, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Adult Climb)
    [GI_SILVER_RUPEE_GANONS_CASTLE_SPIRIT_TRIAL]                = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902B, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x10, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Spirit Trial)
    [GI_SILVER_RUPEE_GANONS_CASTLE_LIGHT_TRIAL]                 = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902C, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x11, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Light Trial)
    [GI_SILVER_RUPEE_GANONS_CASTLE_FIRE_TRIAL]                  = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902D, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x12, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Fire Trial)
    [GI_SILVER_RUPEE_GANONS_CASTLE_SHADOW_TRIAL]                = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902E, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x13, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Shadow Trial)
    [GI_SILVER_RUPEE_GANONS_CASTLE_WATER_TRIAL]                 = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902F, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x14, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Water Trial)
    [GI_SILVER_RUPEE_GANONS_CASTLE_FOREST_TRIAL]                = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9030, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x15, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Forest Trial)

    [GI_SILVER_RUPEE_POUCH_DODONGOS_CAVERN_STAIRCASE]           = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901B, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, DODONGO_ID, 0x00, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Dodongos Cavern Staircase)
    [GI_SILVER_RUPEE_POUCH_ICE_CAVERN_SPINNING_SCYTHE]          = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901C, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, ICE_ID,     0x01, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ice Cavern Spinning Scythe)
    [GI_SILVER_RUPEE_POUCH_ICE_CAVERN_PUSH_BLOCK]               = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901D, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, ICE_ID,     0x02, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ice Cavern Push Block)
    [GI_SILVER_RUPEE_POUCH_BOTTOM_OF_THE_WELL_BASEMENT]         = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901E, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, BOTW_ID,    0x03, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Bottom of the Well Basement)
    [GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_SCYTHE_SHORTCUT]       = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901F, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SHADOW_ID,  0x04, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Shadow Temple Scythe Shortcut)
    [GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_INVISIBLE_BLADES]      = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9020, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SHADOW_ID,  0x05, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Shadow Temple Invisible Blades)
    [GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_HUGE_PIT]              = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9021, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SHADOW_ID,  0x06, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Shadow Temple Huge Pit)
    [GI_SILVER_RUPEE_POUCH_SHADOW_TEMPLE_INVISIBLE_SPIKES]      = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9022, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SHADOW_ID,  0x07, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Shadow Temple Invisible Spikes)
    [GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_SLOPES]       = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9023, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, GTG_ID,     0x08, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Gerudo Training Ground Slopes)
    [GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_LAVA]         = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9024, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, GTG_ID,     0x09, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Gerudo Training Ground Lava)
    [GI_SILVER_RUPEE_POUCH_GERUDO_TRAINING_GROUND_WATER]        = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9025, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, GTG_ID,     0x0A, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Gerudo Training Ground Water)
    [GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_CHILD_EARLY_TORCHES]   = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9026, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0B, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Child Early Torches)
    [GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_ADULT_BOULDERS]        = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9027, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0C, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Adult Boulders)
    [GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_LOBBY_AND_LOWER_ADULT] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9028, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0D, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Lobby and Lower Adult)
    [GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_SUN_BLOCK]             = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9029, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0E, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Sun Block)
    [GI_SILVER_RUPEE_POUCH_SPIRIT_TEMPLE_ADULT_CLIMB]           = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902A, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0F, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Adult Climb)
    [GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_SPIRIT_TRIAL]          = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902B, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x10, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Spirit Trial)
    [GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_LIGHT_TRIAL]           = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902C, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x11, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Light Trial)
    [GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_FIRE_TRIAL]            = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902D, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x12, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Fire Trial)
    [GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_SHADOW_TRIAL]          = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902E, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x13, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Shadow Trial)
    [GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_WATER_TRIAL]           = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902F, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x14, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Water Trial)
    [GI_SILVER_RUPEE_POUCH_GANONS_CASTLE_FOREST_TRIAL]          = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9030, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x15, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Forest Trial)

    // Ocarina button models
    [GI_OCARINA_BUTTON_A]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x908C, 0x01A8, 0x90, no_upgrade, unlock_ocarina_note, 0, -1, NULL), // Ocarina A
    [GI_OCARINA_BUTTON_C_UP]                                    = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x908D, 0x01AA, 0x91, no_upgrade, unlock_ocarina_note, 1, -1, NULL), // Ocarina C up
    [GI_OCARINA_BUTTON_C_DOWN]                                  = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x908E, 0x01AA, 0x92, no_upgrade, unlock_ocarina_note, 2, -1, NULL), // Ocarina C down
    [GI_OCARINA_BUTTON_C_LEFT]                                  = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x908F, 0x01A9, 0x93, no_upgrade, unlock_ocarina_note, 3, -1, NULL), // Ocarina C left
    [GI_OCARINA_BUTTON_C_RIGHT]                                 = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9090, 0x01A9, 0x94, no_upgrade, unlock_ocarina_note, 4, -1, NULL), // Ocarina C right

    // Custom Key Models
    [GI_BOSS_KEY_MODEL_FOREST_TEMPLE]                           = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0006, 0x01A3, 0x8A, no_upgrade, give_dungeon_item, 0x01, FOREST_ID, NULL), // Forest Temple Boss Key
    [GI_BOSS_KEY_MODEL_FIRE_TEMPLE]                             = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001C, 0x01A4, 0x8B, no_upgrade, give_dungeon_item, 0x01, FIRE_ID,   NULL), // Fire Temple Boss Key
    [GI_BOSS_KEY_MODEL_WATER_TEMPLE]                            = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001D, 0x01A5, 0x8C, no_upgrade, give_dungeon_item, 0x01, WATER_ID,  NULL), // Water Temple Boss Key
    [GI_BOSS_KEY_MODEL_SPIRIT_TEMPLE]                           = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001E, 0x01A6, 0x8D, no_upgrade, give_dungeon_item, 0x01, SPIRIT_ID, NULL), // Spirit Temple Boss Key
    [GI_BOSS_KEY_MODEL_SHADOW_TEMPLE]                           = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x002A, 0x01A7, 0x8E, no_upgrade, give_dungeon_item, 0x01, SHADOW_ID, NULL), // Shadow Temple Boss Key
    [GI_BOSS_KEY_MODEL_GANONS_CASTLE]                           = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0061, 0x00B9, 0x8F, no_upgrade, give_dungeon_item, 0x01, TOWER_ID,  NULL), // Ganon's Castle Boss Key

    [GI_SMALL_KEY_MODEL_FOREST_TEMPLE]                          = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0093, 0x0199, 0x80, no_upgrade, give_small_key, FOREST_ID, -1, resolve_text_small_keys), // Forest Temple Small Key
    [GI_SMALL_KEY_MODEL_FIRE_TEMPLE]                            = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0094, 0x019A, 0x81, no_upgrade, give_small_key, FIRE_ID,   -1, resolve_text_small_keys), // Fire Temple Small Key
    [GI_SMALL_KEY_MODEL_WATER_TEMPLE]                           = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0095, 0x019B, 0x82, no_upgrade, give_small_key, WATER_ID,  -1, resolve_text_small_keys), // Water Temple Small Key
    [GI_SMALL_KEY_MODEL_SPIRIT_TEMPLE]                          = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A6, 0x019C, 0x83, no_upgrade, give_small_key, SPIRIT_ID, -1, resolve_text_small_keys), // Spirit Temple Small Key
    [GI_SMALL_KEY_MODEL_SHADOW_TEMPLE]                          = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A9, 0x019D, 0x84, no_upgrade, give_small_key, SHADOW_ID, -1, resolve_text_small_keys), // Shadow Temple Small Key
    [GI_SMALL_KEY_MODEL_BOTTOM_OF_THE_WELL]                     = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009B, 0x019E, 0x85, no_upgrade, give_small_key, BOTW_ID,   -1, resolve_text_small_keys), // Bottom of the Well Small Key
    [GI_SMALL_KEY_MODEL_GERUDO_TRAINING]                        = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009F, 0x019F, 0x86, no_upgrade, give_small_key, GTG_ID,    -1, resolve_text_small_keys), // Gerudo Training Small Key
    [GI_SMALL_KEY_MODEL_THIEVES_HIDEOUT]                        = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A0, 0x01A0, 0x87, no_upgrade, give_small_key, FORT_ID,   -1, resolve_text_small_keys), // Thieves' Hideout Small Key
    [GI_SMALL_KEY_MODEL_GANONS_CASTLE]                          = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A1, 0x01A1, 0x88, no_upgrade, give_small_key, CASTLE_ID, -1, resolve_text_small_keys), // Ganon's Castle Small Key
    [GI_SMALL_KEY_MODEL_CHEST_GAME]                             = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00F3, 0x01A2, 0x89, no_upgrade, give_small_key, TCG_ID,    -1, resolve_text_small_keys_cmg), // Small Key (Chest Game)

    [GI_FAIRY]                                                  = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x90B4, 0x0177, 0x9E, no_upgrade, full_heal, -1, -1, NULL), // Fairy
    [GI_NOTHING]                                                = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x90B5, 0x0177, 0x9F, no_upgrade, no_effect, -1, -1, NULL), // Nothing :)

    // 0x011B through 0x0126 reserved for https://github.com/OoTRandomizer/OoT-Randomizer/pull/2108

    [GI_KOKIRI_EMERALD]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0080, 0x01AB, 0x9B, no_upgrade, give_quest_item, 18, -1, NULL), // Kokiri Emerald
    [GI_GORON_RUBY]                                             = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0081, 0x01AC, 0x9C, no_upgrade, give_quest_item, 19, -1, NULL), // Goron Ruby
    [GI_ZORA_SAPPHIRE]                                          = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0082, 0x01AD, 0x9D, no_upgrade, give_quest_item, 20, -1, NULL), // Zora Sapphire
    [GI_LIGHT_MEDALLION]                                        = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0040, 0x01AE, 0x95, no_upgrade, give_quest_item,  5, -1, NULL), // Light Medallion
    [GI_FOREST_MEDALLION]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x003E, 0x01AF, 0x96, no_upgrade, give_quest_item,  0, -1, NULL), // Forest Medallion
    [GI_FIRE_MEDALLION]                                         = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x003C, 0x01B0, 0x97, no_upgrade, give_quest_item,  1, -1, NULL), // Fire Medallion
    [GI_WATER_MEDALLION]                                        = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x003D, 0x01B1, 0x98, no_upgrade, give_quest_item,  2, -1, NULL), // Water Medallion
    [GI_SHADOW_MEDALLION]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0041, 0x01B2, 0x99, no_upgrade, give_quest_item,  4, -1, NULL), // Shadow Medallion
    [GI_SPIRIT_MEDALLION]                                       = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x003F, 0x01B3, 0x9A, no_upgrade, give_quest_item,  3, -1, NULL), // Spirit Medallion
};

/*  Determine which message to display based on the number of silver rupees collected.
    If player has collected less than the required amount for a particular puzzle,
    display the message saying that they have collected x # of silver rupees

    If they have collected the required amount, display the message that they
    have collected all of the silver rupees. This message should always be placed
    0x16 messages after the base message.

    Returns: text_id to use based on the logic above.
*/

uint16_t resolve_text_silver_rupees(item_row_t* item_row, bool is_outgoing) {
    // Get the arguments from the item_row struct.
    int16_t dungeon_id = item_row->effect_arg1;
    int16_t silver_rupee_id = item_row->effect_arg2;

    // Get the data for this silver rupee puzzle
    silver_rupee_data_t var = silver_rupee_vars[silver_rupee_id][CFG_DUNGEON_IS_MQ[dungeon_id]];

    if (!is_outgoing && extended_savectx.silver_rupee_counts[silver_rupee_id] >= var.needed_count) {
        // The player already has enough silver rupees.
        return item_row->text_id + 0x16;
    } else if (!is_outgoing && extended_savectx.silver_rupee_counts[silver_rupee_id] + 1 == var.needed_count) {
        // This silver rupee unlocks the puzzle.
        return item_row->text_id + (CFG_DUNGEON_IS_MQ[dungeon_id] ? 0x2E : 0x44);
    } else if (!is_outgoing && extended_savectx.silver_rupee_counts[silver_rupee_id] >= 0) {
        // Show number collected.
        return item_row->text_id;
    } else {
        // This silver rupee is for another player, don't show any extra info.
        return item_row->text_id + 0x5A;
    }
}

uint16_t resolve_text_silver_rupee_pouches(item_row_t* item_row, bool is_outgoing) {
    // Get the arguments from the item_row struct.
    int16_t dungeon_id = item_row->effect_arg1;
    int16_t silver_rupee_id = item_row->effect_arg2;

    // Get the data for this silver rupee puzzle
    silver_rupee_data_t var = silver_rupee_vars[silver_rupee_id][CFG_DUNGEON_IS_MQ[dungeon_id]];

    if (!is_outgoing && extended_savectx.silver_rupee_counts[silver_rupee_id] < var.needed_count) {
        // This silver rupee pouch unlocks the puzzle.
        return item_row->text_id + (CFG_DUNGEON_IS_MQ[dungeon_id] ? 0x2E : 0x44);
    } else {
        // This silver rupee pouch is for another player or a duplicate, don't show any extra info.
        return item_row->text_id + 0x5A;
    }
}

uint16_t resolve_text_small_keys(item_row_t* item_row, bool is_outgoing) {
    // Get the arguments from the item_row struct.
    int16_t dungeon_id = item_row->effect_arg1;

    // Get the data for this dungeon
    uint32_t flag = z64_file.scene_flags[dungeon_id].unk_00_;
    int8_t total_keys = flag >> 0x10;
    int8_t max_keys = key_counts[dungeon_id][CFG_DUNGEON_IS_MQ[dungeon_id]];

    if (is_outgoing) {
        return item_row->text_id;
    } else if (total_keys >= max_keys) {
        // The player already has enough keys.
        return 0x9123 + dungeon_id;
    } else if (total_keys == 0) {
        // This is the first key.
        return 0x9101 + dungeon_id;
    } else {
        // Show number collected.
        return 0x9112 + dungeon_id;
    }
}

uint16_t resolve_text_small_keys_cmg(item_row_t* item_row, bool is_outgoing) {
    // Don't use custom message for Treasure Chest Game if it's not shuffled.
    if (!SHUFFLE_CHEST_GAME) {
        return item_row->text_id;
    }

    return resolve_text_small_keys(item_row, is_outgoing);
}

uint16_t resolve_text_keyrings(item_row_t* item_row, bool is_outgoing) {
    int16_t dungeon_id = item_row->effect_arg1;
    int16_t has_boss_key = item_row->effect_arg2;

    if (has_boss_key && KEYRING_BOSSKEY_CONDITION) {
        return item_row->text_id + dungeon_id + 14;
    }
    return item_row->text_id + dungeon_id;
}

item_row_t* get_item_row(uint16_t item_id) {
    if (item_id >= GI_RANDO_MAX) {
        return NULL;
    }
    item_row_t* item_row = &(item_table[item_id]);
    if (item_row->base_item_id == 0) {
        return NULL;
    }
    return item_row;
}

uint16_t resolve_item_text_id(item_row_t* item_row, bool is_outgoing) {
    if (item_row->alt_text_func == NULL) {
        return item_row->text_id;
    } else {
        return item_row->alt_text_func(item_row, is_outgoing);
    }
}

uint16_t resolve_upgrades(override_t override) {
    item_row_t* item_row = get_item_row(override.value.base.item_id);
    return item_row->upgrade(&z64_file, override);
}

void call_effect_function(item_row_t* item_row) {
    item_row->effect(&z64_file, item_row->effect_arg1, item_row->effect_arg2);
}
