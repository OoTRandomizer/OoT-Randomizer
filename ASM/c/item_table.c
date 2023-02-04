#include "item_table.h"

#include "item_effects.h"
#include "item_upgrades.h"
#include "util.h"
#include "z64.h"

#define ITEM_ROW( \
        base_item_id_, chest_type_, action_id_, collectible_,  text_id_, object_id_, graphic_id_, \
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

item_row_t item_table[] = {
    [0x01] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8E, 11, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (5)
    [0x02] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8C, 12, 0x0034, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nuts (5)
    [0x03] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x09, -1, 0x0033, 0x00D9, 0x28, no_upgrade, no_effect, -1, -1, NULL), // Bombchu (10)
    [0x04] = ITEM_ROW(0x53,      GILDED_CHEST, 0x03, -1, 0x0031, 0x00E9, 0x35, no_upgrade, no_effect, -1, -1, NULL), // Fairy Bow
    [0x05] = ITEM_ROW(0x53,      GILDED_CHEST, 0x06, -1, 0x0030, 0x00E7, 0x33, no_upgrade, no_effect, -1, -1, NULL), // Fairy Slingshot
    [0x06] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0E, -1, 0x0035, 0x00E8, 0x34, no_upgrade, no_effect, -1, -1, NULL), // Boomerang
    [0x07] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x00, 13, 0x0037, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Stick
    [0x08] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0A, -1, 0x0036, 0x00DD, 0x2D, no_upgrade, no_effect, -1, -1, NULL), // Hookshot
    [0x09] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0B, -1, 0x004F, 0x00DD, 0x2E, no_upgrade, no_effect, -1, -1, NULL), // Longshot
    [0x0A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0F, -1, 0x0039, 0x00EA, 0x36, no_upgrade, no_effect, -1, -1, NULL), // Lens of Truth
    [0x0B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x23, -1, 0x0069, 0x00EF, 0x3B, no_upgrade, open_mask_shop, -1, -1, NULL), // Zelda's Letter
    [0x0C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x08, -1, 0x003A, 0x00DE, 0x2F, no_upgrade, no_effect, -1, -1, NULL), // Ocarina of Time
    [0x0D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x11, -1, 0x0038, 0x00F6, 0x41, no_upgrade, no_effect, -1, -1, NULL), // Megaton Hammer
    [0x0E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2F, -1, 0x0002, 0x0109, 0x5E, no_upgrade, no_effect, -1, -1, NULL), // Cojiro
    [0x0F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x14, -1, 0x0042, 0x00C6, 0x01, no_upgrade, no_effect, -1, -1, NULL), // Empty Bottle
    [0x10] = ITEM_ROW(0x53,      GILDED_CHEST, 0x15, -1, 0x0043, 0x00EB, 0x38, no_upgrade, no_effect, -1, -1, NULL), // Red Potion
    [0x11] = ITEM_ROW(0x53,      GILDED_CHEST, 0x16, -1, 0x0044, 0x00EB, 0x37, no_upgrade, no_effect, -1, -1, NULL), // Green Potion
    [0x12] = ITEM_ROW(0x53,      GILDED_CHEST, 0x17, -1, 0x0045, 0x00EB, 0x39, no_upgrade, no_effect, -1, -1, NULL), // Blue Potion
    [0x13] = ITEM_ROW(0x53,      GILDED_CHEST, 0x18, -1, 0x0046, 0x00C6, 0x01, no_upgrade, no_effect, -1, -1, NULL), // Bottled Fairy
    [0x14] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1A, -1, 0x0098, 0x00DF, 0x30, no_upgrade, no_effect, -1, -1, NULL), // Bottled Lon Lon Milk
    [0x15] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1B, -1, 0x0099, 0x010B, 0x45, letter_to_bottle, no_effect, -1, -1, NULL), // Bottled Ruto's Letter
    [0x16] = ITEM_ROW(0x53,       BROWN_CHEST, 0x10, -1, 0x0048, 0x00F3, 0x3E, no_upgrade, no_effect, -1, -1, NULL), // Magic Bean
    [0x17] = ITEM_ROW(0x53,      GILDED_CHEST, 0x25, -1, 0x0010, 0x0136, 0x4F, no_upgrade, no_effect, -1, -1, NULL), // Skull Mask
    [0x18] = ITEM_ROW(0x53,      GILDED_CHEST, 0x26, -1, 0x0011, 0x0135, 0x32, no_upgrade, no_effect, -1, -1, NULL), // Spooky Mask
    [0x19] = ITEM_ROW(0x53,      GILDED_CHEST, 0x22, -1, 0x000B, 0x0109, 0x44, no_upgrade, no_effect, -1, -1, NULL), // Chicken
    [0x1A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x24, -1, 0x0012, 0x0134, 0x31, no_upgrade, no_effect, -1, -1, NULL), // Keaton Mask
    [0x1B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x27, -1, 0x0013, 0x0137, 0x50, no_upgrade, no_effect, -1, -1, NULL), // Bunny Hood
    [0x1C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2B, -1, 0x0017, 0x0138, 0x51, no_upgrade, no_effect, -1, -1, NULL), // Mask of Truth
    [0x1D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2D, -1, 0x9001, 0x00DA, 0x29, no_upgrade, no_effect, -1, -1, NULL), // Pocket Egg
    [0x1E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2E, -1, 0x000B, 0x0109, 0x44, no_upgrade, no_effect, -1, -1, NULL), // Pocket Cucco
    [0x1F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x30, -1, 0x0003, 0x0141, 0x54, no_upgrade, no_effect, -1, -1, NULL), // Odd Mushroom
    [0x20] = ITEM_ROW(0x53,      GILDED_CHEST, 0x31, -1, 0x0004, 0x0140, 0x53, no_upgrade, no_effect, -1, -1, NULL), // Odd Potion
    [0x21] = ITEM_ROW(0x53,      GILDED_CHEST, 0x32, -1, 0x0005, 0x00F5, 0x40, no_upgrade, no_effect, -1, -1, NULL), // Poacher's Saw
    [0x22] = ITEM_ROW(0x53,      GILDED_CHEST, 0x33, -1, 0x0008, 0x0143, 0x56, no_upgrade, no_effect, -1, -1, NULL), // Goron's Sword (Broken)
    [0x23] = ITEM_ROW(0x53,      GILDED_CHEST, 0x34, -1, 0x0009, 0x0146, 0x57, no_upgrade, no_effect, -1, -1, NULL), // Prescription
    [0x24] = ITEM_ROW(0x53,      GILDED_CHEST, 0x35, -1, 0x000D, 0x0149, 0x5A, no_upgrade, no_effect, -1, -1, NULL), // Eyeball Frog
    [0x25] = ITEM_ROW(0x53,      GILDED_CHEST, 0x36, -1, 0x000E, 0x013F, 0x52, no_upgrade, no_effect, -1, -1, NULL), // Eye Drops
    [0x26] = ITEM_ROW(0x53,      GILDED_CHEST, 0x37, -1, 0x000A, 0x0142, 0x55, no_upgrade, no_effect, -1, -1, NULL), // Claim Check
    [0x27] = ITEM_ROW(0x53,      GILDED_CHEST, 0x3B, -1, 0x00A4, 0x018D, 0x74, no_upgrade, no_effect, -1, -1, NULL), // Kokiri Sword
    [0x28] = ITEM_ROW(0x53,      GILDED_CHEST, 0x3D, -1, 0x004B, 0x00F8, 0x43, no_upgrade, no_effect, -1, -1, NULL), // Giant's Knife
    [0x29] = ITEM_ROW(0x53,       BROWN_CHEST, 0x3E, -1, 0x004C, 0x00CB, 0x1D, no_upgrade, no_effect, -1, -1, NULL), // Deku Shield
    [0x2A] = ITEM_ROW(0x53,       BROWN_CHEST, 0x3F, -1, 0x004D, 0x00DC, 0x2C, no_upgrade, no_effect, -1, -1, NULL), // Hylian Shield
    [0x2B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x40, -1, 0x004E, 0x00EE, 0x3A, no_upgrade, no_effect, -1, -1, NULL), // Mirror Shield
    [0x2C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x42, -1, 0x0050, 0x00F2, 0x3C, no_upgrade, no_effect, -1, -1, NULL), // Goron Tunic
    [0x2D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x43, -1, 0x0051, 0x00F2, 0x3D, no_upgrade, no_effect, -1, -1, NULL), // Zora Tunic
    [0x2E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x45, -1, 0x0053, 0x0118, 0x47, no_upgrade, no_effect, -1, -1, NULL), // Iron Boots
    [0x2F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x46, -1, 0x0054, 0x0157, 0x5F, no_upgrade, no_effect, -1, -1, NULL), // Hover Boots
    [0x30] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4B, -1, 0x0056, 0x00BE, 0x16, no_upgrade, no_effect, -1, -1, NULL), // Big Quiver
    [0x31] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4C, -1, 0x0057, 0x00BE, 0x17, no_upgrade, no_effect, -1, -1, NULL), // Biggest Quiver
    [0x32] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4D, -1, 0x0058, 0x00BF, 0x18, no_upgrade, no_effect, -1, -1, NULL), // Bomb Bag
    [0x33] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4E, -1, 0x0059, 0x00BF, 0x19, no_upgrade, no_effect, -1, -1, NULL), // Big Bomb Bag
    [0x34] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4F, -1, 0x005A, 0x00BF, 0x1A, no_upgrade, no_effect, -1, -1, NULL), // Biggest Bomb Bag
    [0x35] = ITEM_ROW(0x53,      GILDED_CHEST, 0x51, -1, 0x005B, 0x012D, 0x49, no_upgrade, no_effect, -1, -1, NULL), // Silver Gauntlets
    [0x36] = ITEM_ROW(0x53,      GILDED_CHEST, 0x52, -1, 0x005C, 0x012D, 0x4A, no_upgrade, no_effect, -1, -1, NULL), // Golden Gauntlets
    [0x37] = ITEM_ROW(0x53,      GILDED_CHEST, 0x53, -1, 0x00CD, 0x00DB, 0x2A, no_upgrade, no_effect, -1, -1, NULL), // Silver Scale
    [0x38] = ITEM_ROW(0x53,      GILDED_CHEST, 0x54, -1, 0x00CE, 0x00DB, 0x2B, no_upgrade, no_effect, -1, -1, NULL), // Golden Scale
    [0x39] = ITEM_ROW(0x53,      GILDED_CHEST, 0x6F, -1, 0x0068, 0x00C8, 0x21, no_upgrade, no_effect, -1, -1, NULL), // Stone of Agony
    [0x3A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x70, -1, 0x007B, 0x00D7, 0x24, no_upgrade, no_effect, -1, -1, NULL), // Gerudo Membership Card
    [0x3B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x004A, 0x010E, 0x46, no_upgrade, give_fairy_ocarina, -1, -1, NULL), // Fairy Ocarina
    [0x3C] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x58, 16, 0x00DC, 0x0119, 0x48, seeds_to_rupee, no_effect, -1, -1, NULL), // Deku Seeds (5)
    [0x3D] = ITEM_ROW(0x3D,       BROWN_CHEST, 0x72, -1, 0x00C6, 0x00BD, 0x13, health_upgrade_cap, clear_excess_hearts, -1, -1, NULL), // Heart Container
    [0x3E] = ITEM_ROW(0x3E,       BROWN_CHEST, 0x7A, -1, 0x00C2, 0x00BD, 0x14, health_upgrade_cap, full_heal, -1, -1, NULL), // Piece of Heart
    [0x3F] = ITEM_ROW(0x53,        GOLD_CHEST, 0x74, -1, 0x00C7, 0x00B9, 0x0A, no_upgrade, no_effect, -1, -1, NULL), // Boss Key
    [0x40] = ITEM_ROW(0x53,       BROWN_CHEST, 0x75, -1, 0x0067, 0x00B8, 0x0B, no_upgrade, no_effect, -1, -1, NULL), // Compass
    [0x41] = ITEM_ROW(0x53,       BROWN_CHEST, 0x76, -1, 0x0066, 0x00C8, 0x1C, no_upgrade, no_effect, -1, -1, NULL), // Map
    [0x42] = ITEM_ROW(0x53,      SILVER_CHEST, 0x77, -1, 0x0060, 0x00AA, 0x02, no_upgrade, no_effect, -1, -1, NULL), // Small Key
    [0x43] = ITEM_ROW(0x53,       BROWN_CHEST, 0x78, -1, 0x0052, 0x00CD, 0x1E, no_upgrade, no_effect, -1, -1, NULL), // Small Magic Jar
    [0x44] = ITEM_ROW(0x53,       BROWN_CHEST, 0x79, -1, 0x0052, 0x00CD, 0x1F, no_upgrade, no_effect, -1, -1, NULL), // Large Magic Jar
    [0x45] = ITEM_ROW(0x53,      GILDED_CHEST, 0x56, -1, 0x005E, 0x00D1, 0x22, no_upgrade, fill_wallet_upgrade, 1, -1, NULL), // Adult's Wallet
    [0x46] = ITEM_ROW(0x53,      GILDED_CHEST, 0x57, -1, 0x005F, 0x00D1, 0x23, no_upgrade, fill_wallet_upgrade, 2, -1, NULL), // Giant's Wallet
    [0x47] = ITEM_ROW(0x53,      GILDED_CHEST, 0x21, -1, 0x009A, 0x00DA, 0x29, no_upgrade, no_effect, -1, -1, NULL), // Weird Egg
    [0x48] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x83,  3, 0x0055, 0x00B7, 0x09, no_upgrade, no_effect, -1, -1, NULL), // Recovery Heart
    [0x49] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x92,  8, 0x00E6, 0x00D8, 0x25, arrows_to_rupee, no_effect, -1, -1, NULL), // Arrows (5)
    [0x4A] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x93,  9, 0x00E6, 0x00D8, 0x26, arrows_to_rupee, no_effect, -1, -1, NULL), // Arrows (10)
    [0x4B] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x94, 10, 0x00E6, 0x00D8, 0x27, arrows_to_rupee, no_effect, -1, -1, NULL), // Arrows (30)
    [0x4C] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x84,  0, 0x006F, 0x017F, 0x6D, no_upgrade, no_effect, -1, -1, NULL), // Green Rupee
    [0x4D] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x85,  1, 0x00CC, 0x017F, 0x6E, no_upgrade, no_effect, -1, -1, NULL), // Blue Rupee
    [0x4E] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x86,  2, 0x00F0, 0x017F, 0x6F, no_upgrade, no_effect, -1, -1, NULL), // Red Rupee
    [0x4F] = ITEM_ROW(0x3D,       BROWN_CHEST, 0x72, -1, 0x00C6, 0x00BD, 0x13, no_upgrade, full_heal, -1, -1, NULL), // Heart Container
    [0x50] = ITEM_ROW(0x53,      GILDED_CHEST, 0x82, -1, 0x0098, 0x00DF, 0x30, no_upgrade, no_effect, -1, -1, NULL), // Lon Lon Milk (Refill)
    [0x51] = ITEM_ROW(0x53,      GILDED_CHEST, 0x28, -1, 0x0014, 0x0150, 0x5B, no_upgrade, no_effect, -1, -1, NULL), // Goron Mask
    [0x52] = ITEM_ROW(0x53,      GILDED_CHEST, 0x29, -1, 0x0015, 0x0151, 0x5C, no_upgrade, no_effect, -1, -1, NULL), // Zora Mask
    [0x53] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2A, -1, 0x0016, 0x0152, 0x5D, no_upgrade, no_effect, -1, -1, NULL), // Gerudo Mask
    [0x54] = ITEM_ROW(0x53,      GILDED_CHEST, 0x50, -1, 0x0079, 0x0147, 0x58, no_upgrade, no_effect, -1, -1, NULL), // Goron's Bracelet
    [0x55] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x87, 19, 0x00F1, 0x017F, 0x71, no_upgrade, no_effect, -1, -1, NULL), // Purple Rupee
    [0x56] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x88, 20, 0x00F2, 0x017F, 0x72, no_upgrade, no_effect, -1, -1, NULL), // Huge Rupee
    [0x57] = ITEM_ROW(0x53,      GILDED_CHEST, 0x3D, -1, 0x000C, 0x00F8, 0x43, no_upgrade, give_biggoron_sword, -1, -1, NULL), // Biggoron's Sword
    [0x58] = ITEM_ROW(0x53,      GILDED_CHEST, 0x04, -1, 0x0070, 0x0158, 0x60, no_upgrade, no_effect, -1, -1, NULL), // Fire Arrow
    [0x59] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0C, -1, 0x0071, 0x0158, 0x61, no_upgrade, no_effect, -1, -1, NULL), // Ice Arrow
    [0x5A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x12, -1, 0x0072, 0x0158, 0x62, no_upgrade, no_effect, -1, -1, NULL), // Light Arrow
    [0x5B] = ITEM_ROW(0x5B, SKULL_CHEST_SMALL, 0x71, -1, 0x00B4, 0x015C, 0x63, no_upgrade, no_effect, -1, -1, NULL), // Gold Skulltula Token
    [0x5C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x05, -1, 0x00AD, 0x015D, 0x64, no_upgrade, no_effect, -1, -1, NULL), // Din's Fire
    [0x5D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0D, -1, 0x00AE, 0x015D, 0x65, no_upgrade, no_effect, -1, -1, NULL), // Farore's Wind
    [0x5E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x13, -1, 0x00AF, 0x015D, 0x66, no_upgrade, no_effect, -1, -1, NULL), // Nayru's Love
    [0x5F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x47, -1, 0x0007, 0x017B, 0x6C, no_upgrade, no_effect, -1, -1, NULL), // Bullet Bag (30)
    [0x60] = ITEM_ROW(0x53,      GILDED_CHEST, 0x48, -1, 0x0007, 0x017B, 0x6C, no_upgrade, no_effect, -1, -1, NULL), // Bullet Bag (40)
    [0x61] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8A, 13, 0x0037, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Sticks (5)
    [0x62] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8B, 13, 0x0037, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Sticks (10)
    [0x63] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8C, 12, 0x0034, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nuts (5)
    [0x64] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8D, 12, 0x0034, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nuts (10)
    [0x65] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x02, 11, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bomb
    [0x66] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8F, 11, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (10)
    [0x67] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x90, 11, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (20)
    [0x68] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x91, 11, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (30)
    [0x69] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x95, 16, 0x00DC, 0x0119, 0x48, seeds_to_rupee, no_effect, -1, -1, NULL), // Deku Seeds (30)
    [0x6A] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x96, -1, 0x0033, 0x00D9, 0x28, no_upgrade, no_effect, -1, -1, NULL), // Bombchu (5)
    [0x6B] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x97, -1, 0x0033, 0x00D9, 0x28, no_upgrade, no_effect, -1, -1, NULL), // Bombchu (20)
    [0x6C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x19, -1, 0x0047, 0x00F4, 0x3F, no_upgrade, no_effect, -1, -1, NULL), // Fish (Refill)
    [0x6D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1D, -1, 0x007A, 0x0174, 0x68, no_upgrade, no_effect, -1, -1, NULL), // Bugs (Refill)
    [0x6E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1C, -1, 0x005D, 0x0173, 0x67, no_upgrade, no_effect, -1, -1, NULL), // Blue Fire (Refill)
    [0x6F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x20, -1, 0x0097, 0x0176, 0x6A, no_upgrade, no_effect, -1, -1, NULL), // Poe (Refill)
    [0x70] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1E, -1, 0x00F9, 0x0176, 0x70, no_upgrade, no_effect, -1, -1, NULL), // Big Poe (Refill)
    [0x71] = ITEM_ROW(0x53,       BROWN_CHEST, 0x77, -1, 0x00F3, 0x00AA, 0x02, no_upgrade, no_effect, -1, -1, NULL), // Small Key (Chest Game)
    [0x72] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x84, -1, 0x00F4, 0x017F, 0x6D, no_upgrade, no_effect, -1, -1, NULL), // Green Rupee (Chest Game)
    [0x73] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x85, -1, 0x00F5, 0x017F, 0x6E, no_upgrade, no_effect, -1, -1, NULL), // Blue Rupee (Chest Game)
    [0x74] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x86, -1, 0x00F6, 0x017F, 0x6F, no_upgrade, no_effect, -1, -1, NULL), // Red Rupee (Chest Game)
    [0x75] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x87, -1, 0x00F7, 0x017F, 0x71, no_upgrade, no_effect, -1, -1, NULL), // Purple Rupee (Chest Game)
    [0x76] = ITEM_ROW(0x53,       BROWN_CHEST, 0x7A, -1, 0x00FA, 0x00BD, 0x14, health_upgrade_cap, full_heal, -1, -1, NULL), // Piece of Heart (Chest Game)
    [0x77] = ITEM_ROW(0x53,       BROWN_CHEST, 0x98, -1, 0x0090, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Stick Upgrade (20)
    [0x78] = ITEM_ROW(0x53,       BROWN_CHEST, 0x99, -1, 0x0091, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Stick Upgrade (30)
    [0x79] = ITEM_ROW(0x53,       BROWN_CHEST, 0x9A, -1, 0x00A7, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nut Upgrade (30)
    [0x7A] = ITEM_ROW(0x53,       BROWN_CHEST, 0x9B, -1, 0x00A8, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nut Upgrade (40)
    [0x7B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x49, -1, 0x006C, 0x017B, 0x73, no_upgrade, no_effect, -1, -1, NULL), // Bullet Bag (50)
    [0x7C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9002, 0x0000, 0x00, no_upgrade, ice_trap_effect, -1, -1, NULL), // Ice Trap
    [0x7D] = ITEM_ROW(0x3E,       BROWN_CHEST, 0x41, -1, 0x90C2, 0x00BD, 0x14, no_upgrade, full_heal, -1, -1, NULL), // Capped Piece of Heart
    [0x7E] = ITEM_ROW(0x3E,       BROWN_CHEST, 0x41, -1, 0x90C6, 0x00BD, 0x13, no_upgrade, full_heal, -1, -1, NULL), // Capped Heart Container
    [0x7F] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x90FA, 0x00BD, 0x14, no_upgrade, full_heal, -1, -1, NULL), // Capped Piece of Heart (Chest Game)

    [0x80] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x00DD, 0x2D, hookshot_upgrade,  no_effect, -1, -1, NULL), // Progressive Hookshot
    [0x81] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x0147, 0x58, strength_upgrade,  no_effect, -1, -1, NULL), // Progressive Strength
    [0x82] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x00BF, 0x18, bomb_bag_upgrade,  no_effect, -1, -1, NULL), // Progressive Bomb Bag
    [0x83] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x00E9, 0x35, bow_upgrade,       no_effect, -1, -1, NULL), // Progressive Bow
    [0x84] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x00E7, 0x33, slingshot_upgrade, no_effect, -1, -1, NULL), // Progressive Slingshot
    [0x85] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x00D1, 0x22, wallet_upgrade,    no_effect, -1, -1, NULL), // Progressive Wallet
    [0x86] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x00DB, 0x2A, scale_upgrade,     no_effect, -1, -1, NULL), // Progressive Scale
    [0x87] = ITEM_ROW(  -1,       BROWN_CHEST,   -1, -1,    -1, 0x00BB, 0x12, nut_upgrade,       no_effect, -1, -1, NULL), // Progressive Nut Capacity
    [0x88] = ITEM_ROW(  -1,       BROWN_CHEST,   -1, -1,    -1, 0x00C7, 0x1B, stick_upgrade,     no_effect, -1, -1, NULL), // Progressive Stick Capacity
    [0x89] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x00D9, 0x28, bombchu_upgrade,   no_effect, -1, -1, NULL), // Progressive Bombchus
    [0x8A] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x00CD, 0x1E, magic_upgrade,     no_effect, -1, -1, NULL), // Progressive Magic Meter
    [0x8B] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,    -1, 0x010E, 0x46, ocarina_upgrade,   no_effect, -1, -1, NULL), // Progressive Ocarina

    [0x8C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0043, 0x00C6, 0x01, no_upgrade, give_bottle, 0x15, -1, NULL), // Bottle with Red Potion
    [0x8D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0044, 0x00C6, 0x01, no_upgrade, give_bottle, 0x16, -1, NULL), // Bottle with Green Potion
    [0x8E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0045, 0x00C6, 0x01, no_upgrade, give_bottle, 0x17, -1, NULL), // Bottle with Blue Potion
    [0x8F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0046, 0x0177, 0x6B, no_upgrade, give_bottle, 0x18, -1, NULL), // Bottle with Fairy
    [0x90] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0047, 0x00F4, 0x3F, no_upgrade, give_bottle, 0x19, -1, NULL), // Bottle with Fish
    [0x91] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x005D, 0x0173, 0x67, no_upgrade, give_bottle, 0x1C, -1, NULL), // Bottle with Blue Fire
    [0x92] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x007A, 0x0174, 0x68, no_upgrade, give_bottle, 0x1D, -1, NULL), // Bottle with Bugs
    [0x93] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00F9, 0x0176, 0x70, no_upgrade, give_bottle, 0x1E, -1, NULL), // Bottle with Big Poe
    [0x94] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0097, 0x0176, 0x6A, no_upgrade, give_bottle, 0x20, -1, NULL), // Bottle with Poe

    [0x95] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0006, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, FOREST_ID, NULL ), // Forest Temple Boss Key
    [0x96] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001C, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, FIRE_ID, NULL   ), // Fire Temple Boss Key
    [0x97] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001D, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, WATER_ID, NULL  ), // Water Temple Boss Key
    [0x98] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001E, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, SPIRIT_ID, NULL ), // Spirit Temple Boss Key
    [0x99] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x002A, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, SHADOW_ID, NULL ), // Shadow Temple Boss Key
    [0x9A] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0061, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, TOWER_ID, NULL  ), // Ganon's Castle Boss Key

    [0x9B] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0062, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, DEKU_ID, NULL   ), // Deku Tree Compass
    [0x9C] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0063, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, DODONGO_ID, NULL), // Dodongo's Cavern Compass
    [0x9D] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0064, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, JABU_ID, NULL   ), // Jabu Jabu Compass
    [0x9E] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0065, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, FOREST_ID, NULL ), // Forest Temple Compass
    [0x9F] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007C, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, FIRE_ID, NULL   ), // Fire Temple Compass
    [0xA0] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007D, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, WATER_ID, NULL  ), // Water Temple Compass
    [0xA1] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007E, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, SPIRIT_ID, NULL ), // Spirit Temple Compass
    [0xA2] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007F, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, SHADOW_ID, NULL ), // Shadow Temple Compass
    [0xA3] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x00A2, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, BOTW_ID, NULL   ), // Bottom of the Well Compass
    [0xA4] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0087, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, ICE_ID, NULL    ), // Ice Cavern Compass

    [0xA5] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0088, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, DEKU_ID, NULL   ), // Deku Tree Map
    [0xA6] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0089, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, DODONGO_ID, NULL), // Dodongo's Cavern Map
    [0xA7] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008A, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, JABU_ID, NULL   ), // Jabu Jabu Map
    [0xA8] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008B, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, FOREST_ID, NULL ), // Forest Temple Map
    [0xA9] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008C, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, FIRE_ID, NULL   ), // Fire Temple Map
    [0xAA] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008E, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, WATER_ID, NULL  ), // Water Temple Map
    [0xAB] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008F, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, SPIRIT_ID, NULL ), // Spirit Temple Map
    [0xAC] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x00A3, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, SHADOW_ID, NULL ), // Shadow Temple Map
    [0xAD] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x00A5, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, BOTW_ID, NULL   ), // Bottom of the Well Map
    [0xAE] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0092, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, ICE_ID, NULL    ), // Ice Cavern Map

    [0xAF] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0093, 0x00AA, 0x02, no_upgrade, give_small_key, FOREST_ID, -1, NULL), // Forest Temple Small Key
    [0xB0] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0094, 0x00AA, 0x02, no_upgrade, give_small_key, FIRE_ID,   -1, NULL), // Fire Temple Small Key
    [0xB1] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0095, 0x00AA, 0x02, no_upgrade, give_small_key, WATER_ID,  -1, NULL), // Water Temple Small Key
    [0xB2] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A6, 0x00AA, 0x02, no_upgrade, give_small_key, SPIRIT_ID, -1, NULL), // Spirit Temple Small Key
    [0xB3] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A9, 0x00AA, 0x02, no_upgrade, give_small_key, SHADOW_ID, -1, NULL), // Shadow Temple Small Key
    [0xB4] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009B, 0x00AA, 0x02, no_upgrade, give_small_key, BOTW_ID,   -1, NULL), // Bottom of the Well Small Key
    [0xB5] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009F, 0x00AA, 0x02, no_upgrade, give_small_key, GTG_ID,    -1, NULL), // Gerudo Training Small Key
    [0xB6] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A0, 0x00AA, 0x02, no_upgrade, give_small_key, FORT_ID,   -1, NULL), // Gerudo Fortress Small Key
    [0xB7] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A1, 0x00AA, 0x02, no_upgrade, give_small_key, CASTLE_ID, -1, NULL), // Ganon's Castle Small Key

    [0xB8] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00E9, 0x0194, 0x13, no_upgrade, give_defense,      -1, -1, NULL), // Double Defense
    [0xB9] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00E4, 0x00CD, 0x1E, no_upgrade, give_magic,        -1, -1, NULL), // Magic Meter
    [0xBA] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00E8, 0x00CD, 0x1F, no_upgrade, give_double_magic, -1, -1, NULL), // Double Magic

    [0xBB] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0073, 0x0196, 0x78, no_upgrade, give_song, 6, -1 , NULL), // Minuet of Forest
    [0xBC] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0074, 0x0196, 0x79, no_upgrade, give_song, 7, -1 , NULL), // Bolero of Fire
    [0xBD] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0075, 0x0196, 0x7A, no_upgrade, give_song, 8, -1 , NULL), // Serenade of Water
    [0xBE] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0076, 0x0196, 0x7B, no_upgrade, give_song, 9, -1 , NULL), // Requiem of Spirit
    [0xBF] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0077, 0x0196, 0x7C, no_upgrade, give_song, 10, -1, NULL), // Nocturn of Shadow
    [0xC0] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0078, 0x0196, 0x7D, no_upgrade, give_song, 11, -1, NULL), // Prelude of Light

    [0xC1] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00D4, 0x00B6, 0x04, no_upgrade, give_song, 12, -1, NULL), // Zelda's Lullaby
    [0xC2] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00D2, 0x00B6, 0x06, no_upgrade, give_song, 13, -1, NULL), // Epona's Song
    [0xC3] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00D1, 0x00B6, 0x03, no_upgrade, give_song, 14, -1, NULL), // Saria's Song
    [0xC4] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00D3, 0x00B6, 0x08, no_upgrade, give_song, 15, -1, NULL), // Sun's Song
    [0xC5] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00D5, 0x00B6, 0x05, no_upgrade, give_song, 16, -1, NULL), // Song of Time
    [0xC6] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00D6, 0x00B6, 0x07, no_upgrade, give_song, 17, -1, NULL), // Song of Storms

    [0xC7] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00F8, 0x00D1, 0x23, no_upgrade, give_tycoon_wallet, 3, -1, NULL), // Tycoon's Wallet
    [0xC8] = ITEM_ROW(0x53,      GILDED_CHEST, 0x14, -1, 0x9099, 0x010B, 0x45, no_upgrade, no_effect, -1, -1, NULL), // Redundant Letter Bottle
    [0xC9] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9048, 0x00F3, 0x3E, no_upgrade, give_bean_pack, -1, -1, NULL), // Magic Bean Pack
    [0xCA] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9003, 0x0193, 0x76, no_upgrade, give_triforce_piece, -1, -1, NULL), // Triforce piece

    [0xCB] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9010, 0x0195, 0x77, no_upgrade, give_small_key_ring, FOREST_ID, -1, NULL), // Forest Temple Small Key Ring
    [0xCC] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9011, 0x0195, 0x77, no_upgrade, give_small_key_ring, FIRE_ID,   -1, NULL), // Fire Temple Small Key Ring
    [0xCD] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9012, 0x0195, 0x77, no_upgrade, give_small_key_ring, WATER_ID,  -1, NULL), // Water Temple Small Key Ring
    [0xCE] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9013, 0x0195, 0x77, no_upgrade, give_small_key_ring, SPIRIT_ID, -1, NULL), // Spirit Temple Small Key Ring
    [0xCF] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9014, 0x0195, 0x77, no_upgrade, give_small_key_ring, SHADOW_ID, -1, NULL), // Shadow Temple Small Key Ring
    [0xD0] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9015, 0x0195, 0x77, no_upgrade, give_small_key_ring, BOTW_ID,   -1, NULL), // Bottom of the Well Small Key Ring
    [0xD1] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9016, 0x0195, 0x77, no_upgrade, give_small_key_ring, GTG_ID,    -1, NULL), // Gerudo Training Small Key Ring
    [0xD2] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9017, 0x0195, 0x77, no_upgrade, give_small_key_ring, FORT_ID,   -1, NULL), // Gerudo Fortress Small Key Ring
    [0xD3] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9018, 0x0195, 0x77, no_upgrade, give_small_key_ring, CASTLE_ID, -1, NULL), // Ganon's Castle Small Key Ring

};

item_row_t *get_item_row(uint16_t item_id) {
    if (item_id >= array_size(item_table)) {
        return NULL;
    }
    item_row_t *item_row = &(item_table[item_id]);
    if (item_row->base_item_id == 0) {
        return NULL;
    }
    return item_row;
}

uint16_t resolve_upgrades(uint16_t item_id) {
    for (;;) {
        item_row_t *item_row = get_item_row(item_id);
        uint16_t new_item_id = item_row->upgrade(&z64_file, item_id);
        if (new_item_id == item_id) {
            return item_id;
        }
        item_id = new_item_id;
    }
}

uint16_t resolve_text_id(item_row_t* item_row) {
    if(item_row->alt_text_func != NULL)
    {
        return item_row->alt_text_func(item_row);
    }
    return item_row->text_id;
}

void call_effect_function(item_row_t *item_row) {
    item_row->effect(&z64_file, item_row->effect_arg1, item_row->effect_arg2);
}
