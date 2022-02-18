#include "item_table.h"

#include "item_effects.h"
#include "item_upgrades.h"
#include "util.h"
#include "z64.h"

#define ITEM_ROW( \
        base_item_id_, chest_type_, action_id_,  text_id_, object_id_, graphic_id_, \
        upgrade_, effect_, effect_arg1_, effect_arg2_) \
    { .base_item_id = base_item_id_, .chest_type = chest_type_, .action_id = action_id_, \
      .text_id = text_id_, .object_id = object_id_, .graphic_id = graphic_id_, \
      .upgrade = upgrade_, .effect = effect_, \
      .effect_arg1 = effect_arg1_, .effect_arg2 = effect_arg2_ }

// The "base item" mostly controls the sound effect made when you receive the item. It should be
// set to something that doesn't break NPCs. Good options include:
// 0x53 = Gerudo Mask (major item sound effect)
// 0x4D = Blue Rupee (minor item sound effect)

// Action ID 0x41 (give kokiri tunic) is used to indicate no action.

item_row_t item_table[] = {
    [0x01] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8E, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1), // Bombs (5)
    [0x02] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8C, 0x0034, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1), // Deku Nuts (5)
    [0x03] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x09, 0x0033, 0x00D9, 0x28, no_upgrade, no_effect, -1, -1), // Bombchu (10)
    [0x04] = ITEM_ROW(0x53,      GILDED_CHEST, 0x03, 0x0031, 0x00E9, 0x35, no_upgrade, no_effect, -1, -1), // Fairy Bow
    [0x05] = ITEM_ROW(0x53,      GILDED_CHEST, 0x06, 0x0030, 0x00E7, 0x33, no_upgrade, no_effect, -1, -1), // Fairy Slingshot
    [0x06] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0E, 0x0035, 0x00E8, 0x34, no_upgrade, no_effect, -1, -1), // Boomerang
    [0x07] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x00, 0x0037, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1), // Deku Stick
    [0x08] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0A, 0x0036, 0x00DD, 0x2D, no_upgrade, no_effect, -1, -1), // Hookshot
    [0x09] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0B, 0x004F, 0x00DD, 0x2E, no_upgrade, no_effect, -1, -1), // Longshot
    [0x0A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0F, 0x0039, 0x00EA, 0x36, no_upgrade, no_effect, -1, -1), // Lens of Truth
    [0x0B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x23, 0x0069, 0x00EF, 0x3B, no_upgrade, open_mask_shop, -1, -1), // Zelda's Letter
    [0x0C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x08, 0x003A, 0x00DE, 0x2F, no_upgrade, no_effect, -1, -1), // Ocarina of Time
    [0x0D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x11, 0x0038, 0x00F6, 0x41, no_upgrade, no_effect, -1, -1), // Megaton Hammer
    [0x0E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2F, 0x0002, 0x0109, 0x5E, no_upgrade, no_effect, -1, -1), // Cojiro
    [0x0F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x14, 0x0042, 0x00C6, 0x01, no_upgrade, no_effect, -1, -1), // Empty Bottle
    [0x10] = ITEM_ROW(0x53,      GILDED_CHEST, 0x15, 0x0043, 0x00EB, 0x38, no_upgrade, no_effect, -1, -1), // Red Potion
    [0x11] = ITEM_ROW(0x53,      GILDED_CHEST, 0x16, 0x0044, 0x00EB, 0x37, no_upgrade, no_effect, -1, -1), // Green Potion
    [0x12] = ITEM_ROW(0x53,      GILDED_CHEST, 0x17, 0x0045, 0x00EB, 0x39, no_upgrade, no_effect, -1, -1), // Blue Potion
    [0x13] = ITEM_ROW(0x53,      GILDED_CHEST, 0x18, 0x0046, 0x00C6, 0x01, no_upgrade, no_effect, -1, -1), // Bottled Fairy
    [0x14] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1A, 0x0098, 0x00DF, 0x30, no_upgrade, no_effect, -1, -1), // Bottled Lon Lon Milk
    [0x15] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1B, 0x0099, 0x010B, 0x45, letter_to_bottle, no_effect, -1, -1), // Bottled Ruto's Letter
    [0x16] = ITEM_ROW(0x53,       BROWN_CHEST, 0x10, 0x0048, 0x00F3, 0x3E, no_upgrade, no_effect, -1, -1), // Magic Bean
    [0x17] = ITEM_ROW(0x53,      GILDED_CHEST, 0x25, 0x0010, 0x0136, 0x4F, no_upgrade, no_effect, -1, -1), // Skull Mask
    [0x18] = ITEM_ROW(0x53,      GILDED_CHEST, 0x26, 0x0011, 0x0135, 0x32, no_upgrade, no_effect, -1, -1), // Spooky Mask
    [0x19] = ITEM_ROW(0x53,      GILDED_CHEST, 0x22, 0x000B, 0x0109, 0x44, no_upgrade, no_effect, -1, -1), // Chicken
    [0x1A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x24, 0x0012, 0x0134, 0x31, no_upgrade, no_effect, -1, -1), // Keaton Mask
    [0x1B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x27, 0x0013, 0x0137, 0x50, no_upgrade, no_effect, -1, -1), // Bunny Hood
    [0x1C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2B, 0x0017, 0x0138, 0x51, no_upgrade, no_effect, -1, -1), // Mask of Truth
    [0x1D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2D, 0x9001, 0x00DA, 0x29, no_upgrade, no_effect, -1, -1), // Pocket Egg
    [0x1E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2E, 0x000B, 0x0109, 0x44, no_upgrade, no_effect, -1, -1), // Pocket Cucco
    [0x1F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x30, 0x0003, 0x0141, 0x54, no_upgrade, no_effect, -1, -1), // Odd Mushroom
    [0x20] = ITEM_ROW(0x53,      GILDED_CHEST, 0x31, 0x0004, 0x0140, 0x53, no_upgrade, no_effect, -1, -1), // Odd Potion
    [0x21] = ITEM_ROW(0x53,      GILDED_CHEST, 0x32, 0x0005, 0x00F5, 0x40, no_upgrade, no_effect, -1, -1), // Poacher's Saw
    [0x22] = ITEM_ROW(0x53,      GILDED_CHEST, 0x33, 0x0008, 0x0143, 0x56, no_upgrade, no_effect, -1, -1), // Goron's Sword (Broken)
    [0x23] = ITEM_ROW(0x53,      GILDED_CHEST, 0x34, 0x0009, 0x0146, 0x57, no_upgrade, no_effect, -1, -1), // Prescription
    [0x24] = ITEM_ROW(0x53,      GILDED_CHEST, 0x35, 0x000D, 0x0149, 0x5A, no_upgrade, no_effect, -1, -1), // Eyeball Frog
    [0x25] = ITEM_ROW(0x53,      GILDED_CHEST, 0x36, 0x000E, 0x013F, 0x52, no_upgrade, no_effect, -1, -1), // Eye Drops
    [0x26] = ITEM_ROW(0x53,      GILDED_CHEST, 0x37, 0x000A, 0x0142, 0x55, no_upgrade, no_effect, -1, -1), // Claim Check
    [0x27] = ITEM_ROW(0x53,      GILDED_CHEST, 0x3B, 0x00A4, 0x018D, 0x74, no_upgrade, no_effect, -1, -1), // Kokiri Sword
    [0x28] = ITEM_ROW(0x53,      GILDED_CHEST, 0x3D, 0x004B, 0x00F8, 0x43, no_upgrade, no_effect, -1, -1), // Giant's Knife
    [0x29] = ITEM_ROW(0x53,       BROWN_CHEST, 0x3E, 0x004C, 0x00CB, 0x1D, no_upgrade, no_effect, -1, -1), // Deku Shield
    [0x2A] = ITEM_ROW(0x53,       BROWN_CHEST, 0x3F, 0x004D, 0x00DC, 0x2C, no_upgrade, no_effect, -1, -1), // Hylian Shield
    [0x2B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x40, 0x004E, 0x00EE, 0x3A, no_upgrade, no_effect, -1, -1), // Mirror Shield
    [0x2C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x42, 0x0050, 0x00F2, 0x3C, no_upgrade, no_effect, -1, -1), // Goron Tunic
    [0x2D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x43, 0x0051, 0x00F2, 0x3D, no_upgrade, no_effect, -1, -1), // Zora Tunic
    [0x2E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x45, 0x0053, 0x0118, 0x47, no_upgrade, no_effect, -1, -1), // Iron Boots
    [0x2F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x46, 0x0054, 0x0157, 0x5F, no_upgrade, no_effect, -1, -1), // Hover Boots
    [0x30] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4B, 0x0056, 0x00BE, 0x16, no_upgrade, no_effect, -1, -1), // Big Quiver
    [0x31] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4C, 0x0057, 0x00BE, 0x17, no_upgrade, no_effect, -1, -1), // Biggest Quiver
    [0x32] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4D, 0x0058, 0x00BF, 0x18, no_upgrade, no_effect, -1, -1), // Bomb Bag
    [0x33] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4E, 0x0059, 0x00BF, 0x19, no_upgrade, no_effect, -1, -1), // Big Bomb Bag
    [0x34] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4F, 0x005A, 0x00BF, 0x1A, no_upgrade, no_effect, -1, -1), // Biggest Bomb Bag
    [0x35] = ITEM_ROW(0x53,      GILDED_CHEST, 0x51, 0x005B, 0x012D, 0x49, no_upgrade, no_effect, -1, -1), // Silver Gauntlets
    [0x36] = ITEM_ROW(0x53,      GILDED_CHEST, 0x52, 0x005C, 0x012D, 0x4A, no_upgrade, no_effect, -1, -1), // Golden Gauntlets
    [0x37] = ITEM_ROW(0x53,      GILDED_CHEST, 0x53, 0x00CD, 0x00DB, 0x2A, no_upgrade, no_effect, -1, -1), // Silver Scale
    [0x38] = ITEM_ROW(0x53,      GILDED_CHEST, 0x54, 0x00CE, 0x00DB, 0x2B, no_upgrade, no_effect, -1, -1), // Golden Scale
    [0x39] = ITEM_ROW(0x53,      GILDED_CHEST, 0x6F, 0x0068, 0x00C8, 0x21, no_upgrade, no_effect, -1, -1), // Stone of Agony
    [0x3A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x70, 0x007B, 0x00D7, 0x24, no_upgrade, no_effect, -1, -1), // Gerudo Membership Card
    [0x3B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x004A, 0x010E, 0x46, no_upgrade, give_fairy_ocarina, -1, -1), // Fairy Ocarina
    [0x3C] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x58, 0x00DC, 0x0119, 0x48, seeds_to_rupee, no_effect, -1, -1), // Deku Seeds (5)
    [0x3D] = ITEM_ROW(0x3D,       BROWN_CHEST, 0x72, 0x00C6, 0x00BD, 0x13, no_upgrade, full_heal, -1, -1), // Heart Container
    [0x3E] = ITEM_ROW(0x3E,       BROWN_CHEST, 0x7A, 0x00C2, 0x00BD, 0x14, no_upgrade, full_heal, -1, -1), // Piece of Heart
    [0x3F] = ITEM_ROW(0x53,        GOLD_CHEST, 0x74, 0x00C7, 0x00B9, 0x0A, no_upgrade, no_effect, -1, -1), // Boss Key
    [0x40] = ITEM_ROW(0x53,       BROWN_CHEST, 0x75, 0x0067, 0x00B8, 0x0B, no_upgrade, no_effect, -1, -1), // Compass
    [0x41] = ITEM_ROW(0x53,       BROWN_CHEST, 0x76, 0x0066, 0x00C8, 0x1C, no_upgrade, no_effect, -1, -1), // Map
    [0x42] = ITEM_ROW(0x53,      SILVER_CHEST, 0x77, 0x0060, 0x00AA, 0x02, no_upgrade, no_effect, -1, -1), // Small Key
    [0x43] = ITEM_ROW(0x53,       BROWN_CHEST, 0x78, 0x0052, 0x00CD, 0x1E, no_upgrade, no_effect, -1, -1), // Small Magic Jar
    [0x44] = ITEM_ROW(0x53,       BROWN_CHEST, 0x79, 0x0052, 0x00CD, 0x1F, no_upgrade, no_effect, -1, -1), // Large Magic Jar
    [0x45] = ITEM_ROW(0x53,      GILDED_CHEST, 0x56, 0x005E, 0x00D1, 0x22, no_upgrade, fill_wallet_upgrade, 1, -1), // Adult's Wallet
    [0x46] = ITEM_ROW(0x53,      GILDED_CHEST, 0x57, 0x005F, 0x00D1, 0x23, no_upgrade, fill_wallet_upgrade, 2, -1), // Giant's Wallet
    [0x47] = ITEM_ROW(0x53,      GILDED_CHEST, 0x21, 0x009A, 0x00DA, 0x29, no_upgrade, no_effect, -1, -1), // Weird Egg
    [0x48] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x83, 0x0055, 0x00B7, 0x09, no_upgrade, no_effect, -1, -1), // Recovery Heart
    [0x49] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x92, 0x00E6, 0x00D8, 0x25, arrows_to_rupee, no_effect, -1, -1), // Arrows (5)
    [0x4A] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x93, 0x00E6, 0x00D8, 0x26, arrows_to_rupee, no_effect, -1, -1), // Arrows (10)
    [0x4B] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x94, 0x00E6, 0x00D8, 0x27, arrows_to_rupee, no_effect, -1, -1), // Arrows (30)
    [0x4C] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x84, 0x006F, 0x017F, 0x6D, no_upgrade, no_effect, -1, -1), // Green Rupee
    [0x4D] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x85, 0x00CC, 0x017F, 0x6E, no_upgrade, no_effect, -1, -1), // Blue Rupee
    [0x4E] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x86, 0x00F0, 0x017F, 0x6F, no_upgrade, no_effect, -1, -1), // Red Rupee
    [0x4F] = ITEM_ROW(0x3D,       BROWN_CHEST, 0x72, 0x00C6, 0x00BD, 0x13, no_upgrade, full_heal, -1, -1), // Heart Container
    [0x50] = ITEM_ROW(0x53,      GILDED_CHEST, 0x82, 0x0098, 0x00DF, 0x30, no_upgrade, no_effect, -1, -1), // Lon Lon Milk (Refill)
    [0x51] = ITEM_ROW(0x53,      GILDED_CHEST, 0x28, 0x0014, 0x0150, 0x5B, no_upgrade, no_effect, -1, -1), // Goron Mask
    [0x52] = ITEM_ROW(0x53,      GILDED_CHEST, 0x29, 0x0015, 0x0151, 0x5C, no_upgrade, no_effect, -1, -1), // Zora Mask
    [0x53] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2A, 0x0016, 0x0152, 0x5D, no_upgrade, no_effect, -1, -1), // Gerudo Mask
    [0x54] = ITEM_ROW(0x53,      GILDED_CHEST, 0x50, 0x0079, 0x0147, 0x58, no_upgrade, no_effect, -1, -1), // Goron's Bracelet
    [0x55] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x87, 0x00F1, 0x017F, 0x71, no_upgrade, no_effect, -1, -1), // Purple Rupee
    [0x56] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x88, 0x00F2, 0x017F, 0x72, no_upgrade, no_effect, -1, -1), // Huge Rupee
    [0x57] = ITEM_ROW(0x53,      GILDED_CHEST, 0x3D, 0x000C, 0x00F8, 0x43, no_upgrade, give_biggoron_sword, -1, -1), // Biggoron's Sword
    [0x58] = ITEM_ROW(0x53,      GILDED_CHEST, 0x04, 0x0070, 0x0158, 0x60, no_upgrade, no_effect, -1, -1), // Fire Arrow
    [0x59] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0C, 0x0071, 0x0158, 0x61, no_upgrade, no_effect, -1, -1), // Ice Arrow
    [0x5A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x12, 0x0072, 0x0158, 0x62, no_upgrade, no_effect, -1, -1), // Light Arrow
    [0x5B] = ITEM_ROW(0x5B, SKULL_CHEST_SMALL, 0x71, 0x00B4, 0x015C, 0x63, no_upgrade, no_effect, -1, -1), // Gold Skulltula Token
    [0x5C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x05, 0x00AD, 0x015D, 0x64, no_upgrade, no_effect, -1, -1), // Din's Fire
    [0x5D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0D, 0x00AE, 0x015D, 0x65, no_upgrade, no_effect, -1, -1), // Farore's Wind
    [0x5E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x13, 0x00AF, 0x015D, 0x66, no_upgrade, no_effect, -1, -1), // Nayru's Love
    [0x5F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x47, 0x0007, 0x017B, 0x6C, no_upgrade, no_effect, -1, -1), // Bullet Bag (30)
    [0x60] = ITEM_ROW(0x53,      GILDED_CHEST, 0x48, 0x0007, 0x017B, 0x6C, no_upgrade, no_effect, -1, -1), // Bullet Bag (40)
    [0x61] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8A, 0x0037, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1), // Deku Sticks (5)
    [0x62] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8B, 0x0037, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1), // Deku Sticks (10)
    [0x63] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8C, 0x0034, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1), // Deku Nuts (5)
    [0x64] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8D, 0x0034, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1), // Deku Nuts (10)
    [0x65] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x02, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1), // Bomb
    [0x66] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8F, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1), // Bombs (10)
    [0x67] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x90, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1), // Bombs (20)
    [0x68] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x91, 0x0032, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1), // Bombs (30)
    [0x69] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x95, 0x00DC, 0x0119, 0x48, seeds_to_rupee, no_effect, -1, -1), // Deku Seeds (30)
    [0x6A] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x96, 0x0033, 0x00D9, 0x28, no_upgrade, no_effect, -1, -1), // Bombchu (5)
    [0x6B] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x97, 0x0033, 0x00D9, 0x28, no_upgrade, no_effect, -1, -1), // Bombchu (20)
    [0x6C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x19, 0x0047, 0x00F4, 0x3F, no_upgrade, no_effect, -1, -1), // Fish (Refill)
    [0x6D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1D, 0x007A, 0x0174, 0x68, no_upgrade, no_effect, -1, -1), // Bugs (Refill)
    [0x6E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1C, 0x005D, 0x0173, 0x67, no_upgrade, no_effect, -1, -1), // Blue Fire (Refill)
    [0x6F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x20, 0x0097, 0x0176, 0x6A, no_upgrade, no_effect, -1, -1), // Poe (Refill)
    [0x70] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1E, 0x00F9, 0x0176, 0x70, no_upgrade, no_effect, -1, -1), // Big Poe (Refill)
    [0x71] = ITEM_ROW(0x53,       BROWN_CHEST, 0x77, 0x00F3, 0x00AA, 0x02, no_upgrade, no_effect, -1, -1), // Small Key (Chest Game)
    [0x72] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x84, 0x00F4, 0x017F, 0x6D, no_upgrade, no_effect, -1, -1), // Green Rupee (Chest Game)
    [0x73] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x85, 0x00F5, 0x017F, 0x6E, no_upgrade, no_effect, -1, -1), // Blue Rupee (Chest Game)
    [0x74] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x86, 0x00F6, 0x017F, 0x6F, no_upgrade, no_effect, -1, -1), // Red Rupee (Chest Game)
    [0x75] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x87, 0x00F7, 0x017F, 0x71, no_upgrade, no_effect, -1, -1), // Purple Rupee (Chest Game)
    [0x76] = ITEM_ROW(0x53,       BROWN_CHEST, 0x7A, 0x00FA, 0x00BD, 0x14, no_upgrade, full_heal, -1, -1), // Piece of Heart (Chest Game)
    [0x77] = ITEM_ROW(0x53,       BROWN_CHEST, 0x98, 0x0090, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1), // Deku Stick Upgrade (20)
    [0x78] = ITEM_ROW(0x53,       BROWN_CHEST, 0x99, 0x0091, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1), // Deku Stick Upgrade (30)
    [0x79] = ITEM_ROW(0x53,       BROWN_CHEST, 0x9A, 0x00A7, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1), // Deku Nut Upgrade (30)
    [0x7A] = ITEM_ROW(0x53,       BROWN_CHEST, 0x9B, 0x00A8, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1), // Deku Nut Upgrade (40)
    [0x7B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x49, 0x006C, 0x017B, 0x73, no_upgrade, no_effect, -1, -1), // Bullet Bag (50)
    [0x7C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x9002, 0x0000, 0x00, no_upgrade, ice_trap_effect, -1, -1), // Ice Trap

    [0x80] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x00DD, 0x2D, hookshot_upgrade,  no_effect, -1, -1), // Progressive Hookshot
    [0x81] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x0147, 0x58, strength_upgrade,  no_effect, -1, -1), // Progressive Strength
    [0x82] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x00BF, 0x18, bomb_bag_upgrade,  no_effect, -1, -1), // Progressive Bomb Bag
    [0x83] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x00E9, 0x35, bow_upgrade,       no_effect, -1, -1), // Progressive Bow
    [0x84] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x00E7, 0x33, slingshot_upgrade, no_effect, -1, -1), // Progressive Slingshot
    [0x85] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x00D1, 0x22, wallet_upgrade,    no_effect, -1, -1), // Progressive Wallet
    [0x86] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x00DB, 0x2A, scale_upgrade,     no_effect, -1, -1), // Progressive Scale
    [0x87] = ITEM_ROW(  -1,       BROWN_CHEST,   -1,     -1, 0x00BB, 0x12, nut_upgrade,       no_effect, -1, -1), // Progressive Nut Capacity
    [0x88] = ITEM_ROW(  -1,       BROWN_CHEST,   -1,     -1, 0x00C7, 0x1B, stick_upgrade,     no_effect, -1, -1), // Progressive Stick Capacity
    [0x89] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x00D9, 0x28, bombchu_upgrade,   no_effect, -1, -1), // Progressive Bombchus
    [0x8A] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x00CD, 0x1E, magic_upgrade,     no_effect, -1, -1), // Progressive Magic Meter
    [0x8B] = ITEM_ROW(  -1,      GILDED_CHEST,   -1,     -1, 0x010E, 0x46, ocarina_upgrade,   no_effect, -1, -1), // Progressive Ocarina

    [0x8C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0043, 0x00C6, 0x01, no_upgrade, give_bottle, 0x15, -1), // Bottle with Red Potion
    [0x8D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0044, 0x00C6, 0x01, no_upgrade, give_bottle, 0x16, -1), // Bottle with Green Potion
    [0x8E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0045, 0x00C6, 0x01, no_upgrade, give_bottle, 0x17, -1), // Bottle with Blue Potion
    [0x8F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0046, 0x0177, 0x6B, no_upgrade, give_bottle, 0x18, -1), // Bottle with Fairy
    [0x90] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0047, 0x00F4, 0x3F, no_upgrade, give_bottle, 0x19, -1), // Bottle with Fish
    [0x91] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x005D, 0x0173, 0x67, no_upgrade, give_bottle, 0x1C, -1), // Bottle with Blue Fire
    [0x92] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x007A, 0x0174, 0x68, no_upgrade, give_bottle, 0x1D, -1), // Bottle with Bugs
    [0x93] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00F9, 0x0176, 0x70, no_upgrade, give_bottle, 0x1E, -1), // Bottle with Big Poe
    [0x94] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0097, 0x0176, 0x6A, no_upgrade, give_bottle, 0x20, -1), // Bottle with Poe

    [0x95] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, 0x0006, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, FOREST_ID ), // Forest Temple Boss Key
    [0x96] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, 0x001C, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, FIRE_ID   ), // Fire Temple Boss Key
    [0x97] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, 0x001D, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, WATER_ID  ), // Water Temple Boss Key
    [0x98] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, 0x001E, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, SPIRIT_ID ), // Spirit Temple Boss Key
    [0x99] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, 0x002A, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, SHADOW_ID ), // Shadow Temple Boss Key
    [0x9A] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, 0x0061, 0x00B9, 0x0A, no_upgrade, give_dungeon_item, 0x01, TOWER_ID  ), // Ganon's Castle Boss Key

    [0x9B] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x0062, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, DEKU_ID   ), // Deku Tree Compass
    [0x9C] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x0063, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, DODONGO_ID), // Dodongo's Cavern Compass
    [0x9D] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x0064, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, JABU_ID   ), // Jabu Jabu Compass
    [0x9E] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x0065, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, FOREST_ID ), // Forest Temple Compass
    [0x9F] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x007C, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, FIRE_ID   ), // Fire Temple Compass
    [0xA0] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x007D, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, WATER_ID  ), // Water Temple Compass
    [0xA1] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x007E, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, SPIRIT_ID ), // Spirit Temple Compass
    [0xA2] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x007F, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, SHADOW_ID ), // Shadow Temple Compass
    [0xA3] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x00A2, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, BOTW_ID   ), // Bottom of the Well Compass
    [0xA4] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x0087, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, ICE_ID    ), // Ice Cavern Compass

    [0xA5] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x0088, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, DEKU_ID   ), // Deku Tree Map
    [0xA6] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x0089, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, DODONGO_ID), // Dodongo's Cavern Map
    [0xA7] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x008A, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, JABU_ID   ), // Jabu Jabu Map
    [0xA8] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x008B, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, FOREST_ID ), // Forest Temple Map
    [0xA9] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x008C, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, FIRE_ID   ), // Fire Temple Map
    [0xAA] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x008E, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, WATER_ID  ), // Water Temple Map
    [0xAB] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x008F, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, SPIRIT_ID ), // Spirit Temple Map
    [0xAC] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x00A3, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, SHADOW_ID ), // Shadow Temple Map
    [0xAD] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x00A5, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, BOTW_ID   ), // Bottom of the Well Map
    [0xAE] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, 0x0092, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, ICE_ID    ), // Ice Cavern Map

    [0xAF] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x0093, 0x00AA, 0x02, no_upgrade, give_small_key, FOREST_ID, -1), // Forest Temple Small Key
    [0xB0] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x0094, 0x00AA, 0x02, no_upgrade, give_small_key, FIRE_ID,   -1), // Fire Temple Small Key
    [0xB1] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x0095, 0x00AA, 0x02, no_upgrade, give_small_key, WATER_ID,  -1), // Water Temple Small Key
    [0xB2] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x00A6, 0x00AA, 0x02, no_upgrade, give_small_key, SPIRIT_ID, -1), // Spirit Temple Small Key
    [0xB3] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x00A9, 0x00AA, 0x02, no_upgrade, give_small_key, SHADOW_ID, -1), // Shadow Temple Small Key
    [0xB4] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x009B, 0x00AA, 0x02, no_upgrade, give_small_key, BOTW_ID,   -1), // Bottom of the Well Small Key
    [0xB5] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x009F, 0x00AA, 0x02, no_upgrade, give_small_key, GTG_ID,    -1), // Gerudo Training Small Key
    [0xB6] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x00A0, 0x00AA, 0x02, no_upgrade, give_small_key, FORT_ID,   -1), // Gerudo Fortress Small Key
    [0xB7] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x00A1, 0x00AA, 0x02, no_upgrade, give_small_key, CASTLE_ID, -1), // Ganon's Castle Small Key

    [0xB8] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00E9, 0x0194, 0x13, no_upgrade, give_defense,      -1, -1), // Double Defense
    [0xB9] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00E4, 0x00CD, 0x1E, no_upgrade, give_magic,        -1, -1), // Magic Meter
    [0xBA] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00E8, 0x00CD, 0x1F, no_upgrade, give_double_magic, -1, -1), // Double Magic

    [0xBB] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0073, 0x00B6, 0x03, no_upgrade, give_song, 6, -1 ), // Minuet of Forest
    [0xBC] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0074, 0x00B6, 0x04, no_upgrade, give_song, 7, -1 ), // Bolero of Fire
    [0xBD] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0075, 0x00B6, 0x05, no_upgrade, give_song, 8, -1 ), // Serenade of Water
    [0xBE] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0076, 0x00B6, 0x06, no_upgrade, give_song, 9, -1 ), // Requiem of Spirit
    [0xBF] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0077, 0x00B6, 0x07, no_upgrade, give_song, 10, -1), // Nocturn of Shadow
    [0xC0] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x0078, 0x00B6, 0x08, no_upgrade, give_song, 11, -1), // Prelude of Light

    [0xC1] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00D4, 0x00B6, 0x04, no_upgrade, give_song, 12, -1), // Zelda's Lullaby
    [0xC2] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00D2, 0x00B6, 0x06, no_upgrade, give_song, 13, -1), // Epona's Song
    [0xC3] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00D1, 0x00B6, 0x03, no_upgrade, give_song, 14, -1), // Saria's Song
    [0xC4] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00D3, 0x00B6, 0x08, no_upgrade, give_song, 15, -1), // Sun's Song
    [0xC5] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00D5, 0x00B6, 0x05, no_upgrade, give_song, 16, -1), // Song of Time
    [0xC6] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00D6, 0x00B6, 0x07, no_upgrade, give_song, 17, -1), // Song of Storms

    [0xC7] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x00F8, 0x00D1, 0x23, no_upgrade, give_tycoon_wallet, 3, -1), // Tycoon's Wallet
    [0xC8] = ITEM_ROW(0x53,      GILDED_CHEST, 0x14, 0x9099, 0x010B, 0x45, no_upgrade, no_effect, -1, -1), // Redundant Letter Bottle
    [0xC9] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x9048, 0x00F3, 0x3E, no_upgrade, give_bean_pack, -1, -1), // Magic Bean Pack
    [0xCA] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, 0x9003, 0x0193, 0x35, no_upgrade, give_triforce_piece, -1, -1), // Triforce piece

    [0xCB] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x9010, 0x00AA, 0x02, no_upgrade, give_small_key_ring, FOREST_ID, -1), // Forest Temple Small Key Ring
    [0xCC] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x9011, 0x00AA, 0x02, no_upgrade, give_small_key_ring, FIRE_ID,   -1), // Fire Temple Small Key Ring
    [0xCD] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x9012, 0x00AA, 0x02, no_upgrade, give_small_key_ring, WATER_ID,  -1), // Water Temple Small Key Ring
    [0xCE] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x9013, 0x00AA, 0x02, no_upgrade, give_small_key_ring, SPIRIT_ID, -1), // Spirit Temple Small Key Ring
    [0xCF] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x9014, 0x00AA, 0x02, no_upgrade, give_small_key_ring, SHADOW_ID, -1), // Shadow Temple Small Key Ring
    [0xD0] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x9015, 0x00AA, 0x02, no_upgrade, give_small_key_ring, BOTW_ID,   -1), // Bottom of the Well Small Key Ring
    [0xD1] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x9016, 0x00AA, 0x02, no_upgrade, give_small_key_ring, GTG_ID,    -1), // Gerudo Training Small Key Ring
    [0xD2] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x9017, 0x00AA, 0x02, no_upgrade, give_small_key_ring, FORT_ID,   -1), // Gerudo Fortress Small Key Ring
    [0xD3] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, 0x9018, 0x00AA, 0x02, no_upgrade, give_small_key_ring, CASTLE_ID, -1), // Ganon's Castle Small Key Ring

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

void call_effect_function(item_row_t *item_row) {
    item_row->effect(&z64_file, item_row->effect_arg1, item_row->effect_arg2);
}
