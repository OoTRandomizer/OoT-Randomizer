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

item_row_t item_table[] = {
    [0x0001] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8E, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (5)
    [0x0002] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8C, 12, 0x90AA, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nuts (5)
    [0x0003] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x09, -1, 0x90AB, 0x00D9, 0x28, bombchus_to_bag, no_effect, -1, -1, NULL), // Bombchu (10)
    [0x0004] = ITEM_ROW(0x53,      GILDED_CHEST, 0x03, -1, 0x0031, 0x00E9, 0x35, no_upgrade, no_effect, -1, -1, NULL), // Fairy Bow
    [0x0005] = ITEM_ROW(0x53,      GILDED_CHEST, 0x06, -1, 0x0030, 0x00E7, 0x33, no_upgrade, no_effect, -1, -1, NULL), // Fairy Slingshot
    [0x0006] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0E, -1, 0x0035, 0x00E8, 0x34, no_upgrade, no_effect, -1, -1, NULL), // Boomerang
    [0x0007] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x00, 13, 0x90AC, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Stick
    [0x0008] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0A, -1, 0x0036, 0x00DD, 0x2D, no_upgrade, no_effect, -1, -1, NULL), // Hookshot
    [0x0009] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0B, -1, 0x004F, 0x00DD, 0x2E, no_upgrade, no_effect, -1, -1, NULL), // Longshot
    [0x000A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0F, -1, 0x0039, 0x00EA, 0x36, no_upgrade, no_effect, -1, -1, NULL), // Lens of Truth
    [0x000B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x23, -1, 0x0069, 0x00EF, 0x3B, no_upgrade, open_gate_and_mask_shop, 0x23, -1, NULL), // Zelda's Letter
    [0x000C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x08, -1, 0x003A, 0x00DE, 0x2F, no_upgrade, no_effect, -1, -1, NULL), // Ocarina of Time
    [0x000D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x11, -1, 0x0038, 0x00F6, 0x41, no_upgrade, no_effect, -1, -1, NULL), // Megaton Hammer
    [0x000E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2F, -1, 0x0002, 0x0109, 0x5E, no_upgrade, trade_quest_upgrade, 0x2F, -1, NULL), // Cojiro
    [0x000F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x14, -1, 0x0042, 0x00C6, 0x01, no_upgrade, no_effect, -1, -1, NULL), // Empty Bottle
    [0x0010] = ITEM_ROW(0x53,      GILDED_CHEST, 0x15, -1, 0x0043, 0x00EB, 0x38, no_upgrade, no_effect, -1, -1, NULL), // Red Potion
    [0x0011] = ITEM_ROW(0x53,      GILDED_CHEST, 0x16, -1, 0x0044, 0x00EB, 0x37, no_upgrade, no_effect, -1, -1, NULL), // Green Potion
    [0x0012] = ITEM_ROW(0x53,      GILDED_CHEST, 0x17, -1, 0x0045, 0x00EB, 0x39, no_upgrade, no_effect, -1, -1, NULL), // Blue Potion
    [0x0013] = ITEM_ROW(0x53,      GILDED_CHEST, 0x18, -1, 0x0046, 0x00C6, 0x01, no_upgrade, no_effect, -1, -1, NULL), // Bottled Fairy
    [0x0014] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1A, -1, 0x0098, 0x00DF, 0x30, no_upgrade, no_effect, -1, -1, NULL), // Bottled Lon Lon Milk
    [0x0015] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1B, -1, 0x0099, 0x010B, 0x45, letter_to_bottle, no_effect, -1, -1, NULL), // Bottled Ruto's Letter
    [0x0016] = ITEM_ROW(0x53,       BROWN_CHEST, 0x10, -1, 0x0048, 0x00F3, 0x3E, no_upgrade, no_effect, -1, -1, NULL), // Magic Bean
    [0x0017] = ITEM_ROW(0x53,      GILDED_CHEST, 0x25, -1, 0x0010, 0x0136, 0x4F, no_upgrade, trade_quest_upgrade, 0x25, -1, NULL), // Skull Mask
    [0x0018] = ITEM_ROW(0x53,      GILDED_CHEST, 0x26, -1, 0x0011, 0x0135, 0x32, no_upgrade, trade_quest_upgrade, 0x26, -1, NULL), // Spooky Mask
    [0x0019] = ITEM_ROW(0x53,      GILDED_CHEST, 0x22, -1, 0x000B, 0x0109, 0x44, no_upgrade, trade_quest_upgrade, 0x22, -1, NULL), // Chicken
    [0x001A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x24, -1, 0x0012, 0x0134, 0x31, no_upgrade, trade_quest_upgrade, 0x24, -1, NULL), // Keaton Mask
    [0x001B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x27, -1, 0x0013, 0x0137, 0x50, no_upgrade, trade_quest_upgrade, 0x27, -1, NULL), // Bunny Hood
    [0x001C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2B, -1, 0x0017, 0x0138, 0x51, no_upgrade, trade_quest_upgrade, 0x2B, -1, NULL), // Mask of Truth
    [0x001D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2D, -1, 0x9001, 0x00DA, 0x29, no_upgrade, trade_quest_upgrade, 0x2D, -1, NULL), // Pocket Egg
    [0x001E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2E, -1, 0x000B, 0x0109, 0x44, no_upgrade, trade_quest_upgrade, 0x2E, -1, NULL), // Pocket Cucco
    [0x001F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x30, -1, 0x0003, 0x0141, 0x54, no_upgrade, trade_quest_upgrade, 0x30, -1, NULL), // Odd Mushroom
    [0x0020] = ITEM_ROW(0x53,      GILDED_CHEST, 0x31, -1, 0x0004, 0x0140, 0x53, no_upgrade, trade_quest_upgrade, 0x31, -1, NULL), // Odd Potion
    [0x0021] = ITEM_ROW(0x53,      GILDED_CHEST, 0x32, -1, 0x0005, 0x00F5, 0x40, no_upgrade, trade_quest_upgrade, 0x32, -1, NULL), // Poacher's Saw
    [0x0022] = ITEM_ROW(0x53,      GILDED_CHEST, 0x33, -1, 0x0008, 0x0143, 0x56, no_upgrade, trade_quest_upgrade, 0x33, -1, NULL), // Goron's Sword (Broken)
    [0x0023] = ITEM_ROW(0x53,      GILDED_CHEST, 0x34, -1, 0x0009, 0x0146, 0x57, no_upgrade, trade_quest_upgrade, 0x34, -1, NULL), // Prescription
    [0x0024] = ITEM_ROW(0x53,      GILDED_CHEST, 0x35, -1, 0x000D, 0x0149, 0x5A, no_upgrade, trade_quest_upgrade, 0x35, -1, NULL), // Eyeball Frog
    [0x0025] = ITEM_ROW(0x53,      GILDED_CHEST, 0x36, -1, 0x000E, 0x013F, 0x52, no_upgrade, trade_quest_upgrade, 0x36, -1, NULL), // Eye Drops
    [0x0026] = ITEM_ROW(0x53,      GILDED_CHEST, 0x37, -1, 0x000A, 0x0142, 0x55, no_upgrade, trade_quest_upgrade, 0x37, -1, NULL), // Claim Check
    [0x0027] = ITEM_ROW(0x53,      GILDED_CHEST, 0x3B, -1, 0x00A4, 0x018D, 0x74, no_upgrade, no_effect, -1, -1, NULL), // Kokiri Sword
    [0x0028] = ITEM_ROW(0x53,      GILDED_CHEST, 0x3D, -1, 0x004B, 0x00F8, 0x43, no_upgrade, no_effect, -1, -1, NULL), // Giant's Knife
    [0x0029] = ITEM_ROW(0x53,       BROWN_CHEST, 0x3E, -1, 0x90AD, 0x00CB, 0x1D, no_upgrade, no_effect, -1, -1, NULL), // Deku Shield
    [0x002A] = ITEM_ROW(0x53,       BROWN_CHEST, 0x3F, -1, 0x90AE, 0x00DC, 0x2C, no_upgrade, no_effect, -1, -1, NULL), // Hylian Shield
    [0x002B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x40, -1, 0x004E, 0x00EE, 0x3A, no_upgrade, no_effect, -1, -1, NULL), // Mirror Shield
    [0x002C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x42, -1, 0x90AF, 0x00F2, 0x3C, no_upgrade, no_effect, -1, -1, NULL), // Goron Tunic
    [0x002D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x43, -1, 0x90B0, 0x00F2, 0x3D, no_upgrade, no_effect, -1, -1, NULL), // Zora Tunic
    [0x002E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x45, -1, 0x0053, 0x0118, 0x47, no_upgrade, no_effect, -1, -1, NULL), // Iron Boots
    [0x002F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x46, -1, 0x0054, 0x0157, 0x5F, no_upgrade, no_effect, -1, -1, NULL), // Hover Boots
    [0x0030] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4B, -1, 0x0056, 0x00BE, 0x16, no_upgrade, no_effect, -1, -1, NULL), // Big Quiver
    [0x0031] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4C, -1, 0x0057, 0x00BE, 0x17, no_upgrade, no_effect, -1, -1, NULL), // Biggest Quiver
    [0x0032] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4D, -1, 0x0058, 0x00BF, 0x18, no_upgrade, no_effect, -1, -1, NULL), // Bomb Bag
    [0x0033] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4E, -1, 0x0059, 0x00BF, 0x19, no_upgrade, no_effect, -1, -1, NULL), // Big Bomb Bag
    [0x0034] = ITEM_ROW(0x53,      GILDED_CHEST, 0x4F, -1, 0x005A, 0x00BF, 0x1A, no_upgrade, no_effect, -1, -1, NULL), // Biggest Bomb Bag
    [0x0035] = ITEM_ROW(0x53,      GILDED_CHEST, 0x51, -1, 0x005B, 0x012D, 0x49, no_upgrade, no_effect, -1, -1, NULL), // Silver Gauntlets
    [0x0036] = ITEM_ROW(0x53,      GILDED_CHEST, 0x52, -1, 0x005C, 0x012D, 0x4A, no_upgrade, no_effect, -1, -1, NULL), // Golden Gauntlets
    [0x0037] = ITEM_ROW(0x53,      GILDED_CHEST, 0x53, -1, 0x00CD, 0x00DB, 0x2A, no_upgrade, no_effect, -1, -1, NULL), // Silver Scale
    [0x0038] = ITEM_ROW(0x53,      GILDED_CHEST, 0x54, -1, 0x00CE, 0x00DB, 0x2B, no_upgrade, no_effect, -1, -1, NULL), // Golden Scale
    [0x0039] = ITEM_ROW(0x53,      GILDED_CHEST, 0x6F, -1, 0x0068, 0x00C8, 0x21, no_upgrade, no_effect, -1, -1, NULL), // Stone of Agony
    [0x003A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x70, -1, 0x007B, 0x00D7, 0x24, no_upgrade, no_effect, -1, -1, NULL), // Gerudo Membership Card
    [0x003B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x004A, 0x010E, 0x46, no_upgrade, give_fairy_ocarina, -1, -1, NULL), // Fairy Ocarina
    [0x003C] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x58, 16, 0x90B3, 0x0119, 0x48, seeds_to_rupee, no_effect, -1, -1, NULL), // Deku Seeds (5)
    [0x003D] = ITEM_ROW(0x3D, HEART_CHEST_SMALL, 0x72, -1, 0x00C6, 0x00BD, 0x13, health_upgrade_cap, clear_excess_hearts, -1, -1, NULL), // Heart Container
    [0x003E] = ITEM_ROW(0x3E, HEART_CHEST_SMALL, 0x7A, -1, 0x00C2, 0x00BD, 0x14, health_upgrade_cap, full_heal, -1, -1, NULL), // Piece of Heart
    [0x003F] = ITEM_ROW(0x53,        GOLD_CHEST, 0x74, -1, 0x00C7, 0x00B9, 0x0A, no_upgrade, no_effect, -1, -1, NULL), // Boss Key
    [0x0040] = ITEM_ROW(0x53,       BROWN_CHEST, 0x75, -1, 0x0067, 0x00B8, 0x0B, no_upgrade, no_effect, -1, -1, NULL), // Compass
    [0x0041] = ITEM_ROW(0x53,       BROWN_CHEST, 0x76, -1, 0x0066, 0x00C8, 0x1C, no_upgrade, no_effect, -1, -1, NULL), // Map
    [0x0042] = ITEM_ROW(0x53,      SILVER_CHEST, 0x77, -1, 0x0060, 0x00AA, 0x02, no_upgrade, no_effect, -1, -1, NULL), // Small Key
    [0x0043] = ITEM_ROW(0x53,       BROWN_CHEST, 0x78, -1, 0x0052, 0x00CD, 0x1E, no_upgrade, no_effect, -1, -1, NULL), // Small Magic Jar
    [0x0044] = ITEM_ROW(0x53,       BROWN_CHEST, 0x79, -1, 0x0052, 0x00CD, 0x1F, no_upgrade, no_effect, -1, -1, NULL), // Large Magic Jar
    [0x0045] = ITEM_ROW(0x53,      GILDED_CHEST, 0x56, -1, 0x005E, 0x00D1, 0x22, no_upgrade, fill_wallet_upgrade, 1, -1, NULL), // Adult's Wallet
    [0x0046] = ITEM_ROW(0x53,      GILDED_CHEST, 0x57, -1, 0x005F, 0x00D1, 0x23, no_upgrade, fill_wallet_upgrade, 2, -1, NULL), // Giant's Wallet
    [0x0047] = ITEM_ROW(0x53,      GILDED_CHEST, 0x21, -1, 0x009A, 0x00DA, 0x29, no_upgrade, trade_quest_upgrade, 0x21, -1, NULL), // Weird Egg
    [0x0048] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x83,  3, 0x90B1, 0x00B7, 0x09, no_upgrade, no_effect, -1, -1, NULL), // Recovery Heart
    [0x0049] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x92,  8, 0x90B2, 0x00D8, 0x25, arrows_to_rupee, no_effect, -1, -1, NULL), // Arrows (5)
    [0x004A] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x93,  9, 0x90B2, 0x00D8, 0x26, arrows_to_rupee, no_effect, -1, -1, NULL), // Arrows (10)
    [0x004B] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x94, 10, 0x90B2, 0x00D8, 0x27, arrows_to_rupee, no_effect, -1, -1, NULL), // Arrows (30)
    [0x004C] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x84,  0, 0x006F, 0x017F, 0x6D, no_upgrade, no_effect, -1, -1, NULL), // Green Rupee
    [0x004D] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x85,  1, 0x00CC, 0x017F, 0x6E, no_upgrade, no_effect, -1, -1, NULL), // Blue Rupee
    [0x004E] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x86,  2, 0x00F0, 0x017F, 0x6F, no_upgrade, no_effect, -1, -1, NULL), // Red Rupee
    [0x004F] = ITEM_ROW(0x3D, HEART_CHEST_SMALL, 0x72, -1, 0x00C6, 0x00BD, 0x13, no_upgrade, full_heal, -1, -1, NULL), // Heart Container
    [0x0050] = ITEM_ROW(0x53,      GILDED_CHEST, 0x82, -1, 0x0098, 0x00DF, 0x30, no_upgrade, no_effect, -1, -1, NULL), // Lon Lon Milk (Refill)
    [0x0051] = ITEM_ROW(0x53,      GILDED_CHEST, 0x28, -1, 0x0014, 0x0150, 0x5B, no_upgrade, trade_quest_upgrade, 0x28, -1, NULL), // Goron Mask
    [0x0052] = ITEM_ROW(0x53,      GILDED_CHEST, 0x29, -1, 0x0015, 0x0151, 0x5C, no_upgrade, trade_quest_upgrade, 0x29, -1, NULL), // Zora Mask
    [0x0053] = ITEM_ROW(0x53,      GILDED_CHEST, 0x2A, -1, 0x0016, 0x0152, 0x5D, no_upgrade, trade_quest_upgrade, 0x2A, -1, NULL), // Gerudo Mask
    [0x0054] = ITEM_ROW(0x53,      GILDED_CHEST, 0x50, -1, 0x0079, 0x0147, 0x58, no_upgrade, no_effect, -1, -1, NULL), // Goron's Bracelet
    [0x0055] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x87, 20, 0x00F1, 0x017F, 0x71, no_upgrade, no_effect, -1, -1, NULL), // Purple Rupee
    [0x0056] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x88, 19, 0x00F2, 0x017F, 0x72, no_upgrade, no_effect, -1, -1, NULL), // Huge Rupee
    [0x0057] = ITEM_ROW(0x53,      GILDED_CHEST, 0x3D, -1, 0x000C, 0x00F8, 0x43, no_upgrade, give_biggoron_sword, -1, -1, NULL), // Biggoron's Sword
    [0x0058] = ITEM_ROW(0x53,      GILDED_CHEST, 0x04, -1, 0x0070, 0x0158, 0x60, no_upgrade, no_effect, -1, -1, NULL), // Fire Arrow
    [0x0059] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0C, -1, 0x0071, 0x0158, 0x61, no_upgrade, no_effect, -1, -1, NULL), // Ice Arrow
    [0x005A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x12, -1, 0x0072, 0x0158, 0x62, no_upgrade, no_effect, -1, -1, NULL), // Light Arrow
    [0x005B] = ITEM_ROW(0x5B, SKULL_CHEST_SMALL, 0x71, -1, 0x00B4, 0x015C, 0x63, no_upgrade, no_effect, -1, -1, NULL), // Gold Skulltula Token
    [0x005C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x05, -1, 0x00AD, 0x015D, 0x64, no_upgrade, no_effect, -1, -1, NULL), // Din's Fire
    [0x005D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x0D, -1, 0x00AE, 0x015D, 0x65, no_upgrade, no_effect, -1, -1, NULL), // Farore's Wind
    [0x005E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x13, -1, 0x00AF, 0x015D, 0x66, no_upgrade, no_effect, -1, -1, NULL), // Nayru's Love
    [0x005F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x47, -1, 0x0007, 0x017B, 0x6C, no_upgrade, no_effect, -1, -1, NULL), // Bullet Bag (30)
    [0x0060] = ITEM_ROW(0x53,      GILDED_CHEST, 0x48, -1, 0x0007, 0x017B, 0x6C, no_upgrade, no_effect, -1, -1, NULL), // Bullet Bag (40)
    [0x0061] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8A, 13, 0x90AC, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Sticks (5)
    [0x0062] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8B, 13, 0x90AC, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Sticks (10)
    [0x0063] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8C, 12, 0x90AA, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nuts (5)
    [0x0064] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8D, 12, 0x90AA, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nuts (10)
    [0x0065] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x02, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bomb
    [0x0066] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x8F, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (10)
    [0x0067] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x90, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (20)
    [0x0068] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x91, 11, 0x90A9, 0x00CE, 0x20, bombs_to_rupee, no_effect, -1, -1, NULL), // Bombs (30)
    [0x0069] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x95, 16, 0x90B3, 0x0119, 0x48, seeds_to_rupee, no_effect, -1, -1, NULL), // Deku Seeds (30)
    [0x006A] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x96, -1, 0x90AB, 0x00D9, 0x28, bombchus_to_bag, no_effect, -1, -1, NULL), // Bombchu (5)
    [0x006B] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x97, -1, 0x90AB, 0x00D9, 0x28, bombchus_to_bag, no_effect, -1, -1, NULL), // Bombchu (20)
    [0x006C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x19, -1, 0x0047, 0x00F4, 0x3F, no_upgrade, no_effect, -1, -1, NULL), // Fish (Refill)
    [0x006D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1D, -1, 0x007A, 0x0174, 0x68, no_upgrade, no_effect, -1, -1, NULL), // Bugs (Refill)
    [0x006E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1C, -1, 0x005D, 0x0173, 0x67, no_upgrade, no_effect, -1, -1, NULL), // Blue Fire (Refill)
    [0x006F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x20, -1, 0x0097, 0x0176, 0x6A, no_upgrade, no_effect, -1, -1, NULL), // Poe (Refill)
    [0x0070] = ITEM_ROW(0x53,      GILDED_CHEST, 0x1E, -1, 0x00F9, 0x0176, 0x70, no_upgrade, no_effect, -1, -1, NULL), // Big Poe (Refill)
    [0x0071] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00F3, 0x00AA, 0x02, upgrade_key_model, give_small_key, TCG_ID, -1, resolve_text_small_keys_cmg), // Small Key (Chest Game)
    [0x0072] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x84, -1, 0x00F4, 0x017F, 0x6D, no_upgrade, no_effect, -1, -1, NULL), // Green Rupee (Chest Game)
    [0x0073] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x85, -1, 0x00F5, 0x017F, 0x6E, no_upgrade, no_effect, -1, -1, NULL), // Blue Rupee (Chest Game)
    [0x0074] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x86, -1, 0x00F6, 0x017F, 0x6F, no_upgrade, no_effect, -1, -1, NULL), // Red Rupee (Chest Game)
    [0x0075] = ITEM_ROW(0x4D,       BROWN_CHEST, 0x87, -1, 0x00F7, 0x017F, 0x71, no_upgrade, no_effect, -1, -1, NULL), // Purple Rupee (Chest Game)
    [0x0076] = ITEM_ROW(0x53, HEART_CHEST_SMALL, 0x7A, -1, 0x00FA, 0x00BD, 0x14, health_upgrade_cap, full_heal, -1, -1, NULL), // Piece of Heart (Chest Game)
    [0x0077] = ITEM_ROW(0x53,       BROWN_CHEST, 0x98, -1, 0x0090, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Stick Upgrade (20)
    [0x0078] = ITEM_ROW(0x53,       BROWN_CHEST, 0x99, -1, 0x0091, 0x00C7, 0x1B, no_upgrade, no_effect, -1, -1, NULL), // Deku Stick Upgrade (30)
    [0x0079] = ITEM_ROW(0x53,       BROWN_CHEST, 0x9A, -1, 0x00A7, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nut Upgrade (30)
    [0x007A] = ITEM_ROW(0x53,       BROWN_CHEST, 0x9B, -1, 0x00A8, 0x00BB, 0x12, no_upgrade, no_effect, -1, -1, NULL), // Deku Nut Upgrade (40)
    [0x007B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x49, -1, 0x006C, 0x017B, 0x73, no_upgrade, no_effect, -1, -1, NULL), // Bullet Bag (50)
    [0x007C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9002, 0x0000, 0x00, no_upgrade, ice_trap_effect, -1, -1, NULL), // Ice Trap
    [0x007D] = ITEM_ROW(0x3E, HEART_CHEST_SMALL, 0x41, -1, 0x90C2, 0x00BD, 0x14, no_upgrade, full_heal, -1, -1, NULL), // Capped Piece of Heart
    [0x007E] = ITEM_ROW(0x3E, HEART_CHEST_SMALL, 0x41, -1, 0x90C6, 0x00BD, 0x13, no_upgrade, full_heal, -1, -1, NULL), // Capped Heart Container
    [0x007F] = ITEM_ROW(0x53, HEART_CHEST_SMALL, 0x41, -1, 0x90FA, 0x00BD, 0x14, no_upgrade, full_heal, -1, -1, NULL), // Capped Piece of Heart (Chest Game)

    [0x0080] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00DD, 0x2D, hookshot_upgrade,  no_effect, -1, -1, NULL), // Progressive Hookshot
    [0x0081] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x0147, 0x58, strength_upgrade,  no_effect, -1, -1, NULL), // Progressive Strength
    [0x0082] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00BF, 0x18, bomb_bag_upgrade,  no_effect, -1, -1, NULL), // Progressive Bomb Bag
    [0x0083] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00E9, 0x35, bow_upgrade,       no_effect, -1, -1, NULL), // Progressive Bow
    [0x0084] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00E7, 0x33, slingshot_upgrade, no_effect, -1, -1, NULL), // Progressive Slingshot
    [0x0085] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00D1, 0x22, wallet_upgrade,    no_effect, -1, -1, NULL), // Progressive Wallet
    [0x0086] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00DB, 0x2A, scale_upgrade,     no_effect, -1, -1, NULL), // Progressive Scale
    [0x0087] = ITEM_ROW(  -1,       BROWN_CHEST,   -1, -1,     -1, 0x00BB, 0x12, nut_upgrade,       no_effect, -1, -1, NULL), // Progressive Nut Capacity
    [0x0088] = ITEM_ROW(  -1,       BROWN_CHEST,   -1, -1,     -1, 0x00C7, 0x1B, stick_upgrade,     no_effect, -1, -1, NULL), // Progressive Stick Capacity
    [0x0089] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00D9, 0x28, bombchu_upgrade,   no_effect, -1, -1, NULL), // Progressive Bombchus
    [0x008A] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x00CD, 0x1E, magic_upgrade,     no_effect, -1, -1, NULL), // Progressive Magic Meter
    [0x008B] = ITEM_ROW(  -1,      GILDED_CHEST,   -1, -1,     -1, 0x010E, 0x46, ocarina_upgrade,   no_effect, -1, -1, NULL), // Progressive Ocarina

    [0x008C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A0, 0x00C6, 0x01, no_upgrade, give_bottle, 0x15, -1, NULL), // Bottle with Red Potion
    [0x008D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A1, 0x00C6, 0x01, no_upgrade, give_bottle, 0x16, -1, NULL), // Bottle with Green Potion
    [0x008E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A2, 0x00C6, 0x01, no_upgrade, give_bottle, 0x17, -1, NULL), // Bottle with Blue Potion
    [0x008F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A3, 0x0177, 0x6B, no_upgrade, give_bottle, 0x18, -1, NULL), // Bottle with Fairy
    [0x0090] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A4, 0x00F4, 0x3F, no_upgrade, give_bottle, 0x19, -1, NULL), // Bottle with Fish
    [0x0091] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A5, 0x0173, 0x67, no_upgrade, give_bottle, 0x1C, -1, NULL), // Bottle with Blue Fire
    [0x0092] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A6, 0x0174, 0x68, no_upgrade, give_bottle, 0x1D, -1, NULL), // Bottle with Bugs
    [0x0093] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A7, 0x0176, 0x70, no_upgrade, give_bottle, 0x1E, -1, NULL), // Bottle with Big Poe
    [0x0094] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x90A8, 0x0176, 0x6A, no_upgrade, give_bottle, 0x20, -1, NULL), // Bottle with Poe

    [0x0095] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0006, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, FOREST_ID, NULL), // Forest Temple Boss Key
    [0x0096] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001C, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, FIRE_ID,   NULL), // Fire Temple Boss Key
    [0x0097] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001D, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, WATER_ID,  NULL), // Water Temple Boss Key
    [0x0098] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001E, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, SPIRIT_ID, NULL), // Spirit Temple Boss Key
    [0x0099] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x002A, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, SHADOW_ID, NULL), // Shadow Temple Boss Key
    [0x009A] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0061, 0x00B9, 0x0A, upgrade_key_model, give_dungeon_item, 0x01, TOWER_ID,  NULL), // Ganon's Castle Boss Key

    [0x009B] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0062, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, DEKU_ID,    NULL), // Deku Tree Compass
    [0x009C] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0063, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, DODONGO_ID, NULL), // Dodongo's Cavern Compass
    [0x009D] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0064, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, JABU_ID,    NULL), // Jabu Jabu Compass
    [0x009E] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0065, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, FOREST_ID,  NULL), // Forest Temple Compass
    [0x009F] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007C, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, FIRE_ID,    NULL), // Fire Temple Compass
    [0x00A0] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007D, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, WATER_ID,   NULL), // Water Temple Compass
    [0x00A1] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007E, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, SPIRIT_ID,  NULL), // Spirit Temple Compass
    [0x00A2] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x007F, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, SHADOW_ID,  NULL), // Shadow Temple Compass
    [0x00A3] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x00A2, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, BOTW_ID,    NULL), // Bottom of the Well Compass
    [0x00A4] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0087, 0x00B8, 0x0B, no_upgrade, give_dungeon_item, 0x02, ICE_ID,     NULL), // Ice Cavern Compass

    [0x00A5] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0088, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, DEKU_ID,    NULL), // Deku Tree Map
    [0x00A6] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0089, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, DODONGO_ID, NULL), // Dodongo's Cavern Map
    [0x00A7] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008A, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, JABU_ID,    NULL), // Jabu Jabu Map
    [0x00A8] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008B, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, FOREST_ID,  NULL), // Forest Temple Map
    [0x00A9] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008C, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, FIRE_ID,    NULL), // Fire Temple Map
    [0x00AA] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008E, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, WATER_ID,   NULL), // Water Temple Map
    [0x00AB] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x008F, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, SPIRIT_ID,  NULL), // Spirit Temple Map
    [0x00AC] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x00A3, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, SHADOW_ID,  NULL), // Shadow Temple Map
    [0x00AD] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x00A5, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, BOTW_ID,    NULL), // Bottom of the Well Map
    [0x00AE] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x0092, 0x00C8, 0x1C, no_upgrade, give_dungeon_item, 0x04, ICE_ID,     NULL), // Ice Cavern Map

    [0x00AF] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0093, 0x00AA, 0x02, upgrade_key_model, give_small_key, FOREST_ID, -1, resolve_text_small_keys), // Forest Temple Small Key
    [0x00B0] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0094, 0x00AA, 0x02, upgrade_key_model, give_small_key, FIRE_ID,   -1, resolve_text_small_keys), // Fire Temple Small Key
    [0x00B1] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0095, 0x00AA, 0x02, upgrade_key_model, give_small_key, WATER_ID,  -1, resolve_text_small_keys), // Water Temple Small Key
    [0x00B2] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A6, 0x00AA, 0x02, upgrade_key_model, give_small_key, SPIRIT_ID, -1, resolve_text_small_keys), // Spirit Temple Small Key
    [0x00B3] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A9, 0x00AA, 0x02, upgrade_key_model, give_small_key, SHADOW_ID, -1, resolve_text_small_keys), // Shadow Temple Small Key
    [0x00B4] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009B, 0x00AA, 0x02, upgrade_key_model, give_small_key, BOTW_ID,   -1, resolve_text_small_keys), // Bottom of the Well Small Key
    [0x00B5] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009F, 0x00AA, 0x02, upgrade_key_model, give_small_key, GTG_ID,    -1, resolve_text_small_keys), // Gerudo Training Small Key
    [0x00B6] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A0, 0x00AA, 0x02, upgrade_key_model, give_small_key, FORT_ID,   -1, resolve_text_small_keys), // Thieves' Hideout Small Key
    [0x00B7] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A1, 0x00AA, 0x02, upgrade_key_model, give_small_key, CASTLE_ID, -1, resolve_text_small_keys), // Ganon's Castle Small Key

    [0x00B8] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00E9, 0x0194, 0x13, no_upgrade, give_defense,      -1, -1, NULL), // Double Defense
    [0x00B9] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00E4, 0x00CD, 0x1E, no_upgrade, give_magic,        -1, -1, NULL), // Magic Meter
    [0x00BA] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00E8, 0x00CD, 0x1F, no_upgrade, give_double_magic, -1, -1, NULL), // Double Magic

    [0x00BB] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9091, 0x0196, 0x78, no_upgrade, give_quest_item,  6, -1, NULL), // Minuet of Forest
    [0x00BC] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9092, 0x0196, 0x79, no_upgrade, give_quest_item,  7, -1, NULL), // Bolero of Fire
    [0x00BD] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9093, 0x0196, 0x7A, no_upgrade, give_quest_item,  8, -1, NULL), // Serenade of Water
    [0x00BE] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9094, 0x0196, 0x7B, no_upgrade, give_quest_item,  9, -1, NULL), // Requiem of Spirit
    [0x00BF] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9095, 0x0196, 0x7C, no_upgrade, give_quest_item, 10, -1, NULL), // Nocturne of Shadow
    [0x00C0] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9096, 0x0196, 0x7D, no_upgrade, give_quest_item, 11, -1, NULL), // Prelude of Light

    [0x00C1] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909A, 0x00B6, 0x04, no_upgrade, give_quest_item, 12, -1, NULL), // Zelda's Lullaby
    [0x00C2] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909B, 0x00B6, 0x06, no_upgrade, give_quest_item, 13, -1, NULL), // Epona's Song
    [0x00C3] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909C, 0x00B6, 0x03, no_upgrade, give_quest_item, 14, -1, NULL), // Saria's Song
    [0x00C4] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909D, 0x00B6, 0x08, no_upgrade, give_quest_item, 15, -1, NULL), // Sun's Song
    [0x00C5] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909E, 0x00B6, 0x05, no_upgrade, give_quest_item, 16, -1, NULL), // Song of Time
    [0x00C6] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x909F, 0x00B6, 0x07, no_upgrade, give_quest_item, 17, -1, NULL), // Song of Storms

    [0x00C7] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x00F8, 0x00D1, 0x23, no_upgrade, give_tycoon_wallet,   3, -1, NULL), // Tycoon's Wallet
    [0x00C8] = ITEM_ROW(0x53,      GILDED_CHEST, 0x14, -1, 0x9099, 0x010B, 0x45, no_upgrade, no_effect,           -1, -1, NULL), // Redundant Letter Bottle
    [0x00C9] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9048, 0x00F3, 0x3E, no_upgrade, give_bean_pack,      -1, -1, NULL), // Magic Bean Pack
    [0x00CA] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9003, 0x0193, 0x76, no_upgrade, give_triforce_piece, -1, -1, NULL), // Triforce piece

    [0x00CB] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, FOREST_ID, 1, resolve_text_keyrings), // Forest Temple Small Key Ring
    [0x00CC] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, FIRE_ID,   1, resolve_text_keyrings), // Fire Temple Small Key Ring
    [0x00CD] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, WATER_ID,  1, resolve_text_keyrings), // Water Temple Small Key Ring
    [0x00CE] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, SPIRIT_ID, 1, resolve_text_keyrings), // Spirit Temple Small Key Ring
    [0x00CF] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, SHADOW_ID, 1, resolve_text_keyrings), // Shadow Temple Small Key Ring
    [0x00D0] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, BOTW_ID,   0, resolve_text_keyrings), // Bottom of the Well Small Key Ring
    [0x00D1] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, GTG_ID,    0, resolve_text_keyrings), // Gerudo Training Small Key Ring
    [0x00D2] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, FORT_ID,   0, resolve_text_keyrings), // Thieves' Hideout Small Key Ring
    [0x00D3] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, CASTLE_ID, 0, resolve_text_keyrings), // Ganon's Castle Small Key Ring

    [0x00D4] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9019, 0x0197, 0x7E, no_upgrade, give_bombchus, 20, -1, NULL), // Bombchu Bag (20)
    [0x00D5] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9019, 0x0197, 0x7E, no_upgrade, give_bombchus, 10, -1, NULL), // Bombchu Bag (10)
    [0x00D6] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9019, 0x0197, 0x7E, no_upgrade, give_bombchus,  5, -1, NULL), // Bombchu Bag (5)

    [0x00D7] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x9200, 0x0195, 0x77, no_upgrade, give_small_key_ring, TCG_ID, 0, resolve_text_keyrings), // Treasure Chest Game Small Key Ring

    [0x00D8] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901B, 0x0198, 0x72, no_upgrade, give_silver_rupee, DODONGO_ID, 0x00, resolve_text_silver_rupees), // Silver Rupee (Dodongos Cavern Staircase)
    [0x00D9] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901C, 0x0198, 0x72, no_upgrade, give_silver_rupee, ICE_ID,     0x01, resolve_text_silver_rupees), // Silver Rupee (Ice Cavern Spinning Scythe)
    [0x00DA] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901D, 0x0198, 0x72, no_upgrade, give_silver_rupee, ICE_ID,     0x02, resolve_text_silver_rupees), // Silver Rupee (Ice Cavern Push Block)
    [0x00DB] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901E, 0x0198, 0x72, no_upgrade, give_silver_rupee, BOTW_ID,    0x03, resolve_text_silver_rupees), // Silver Rupee (Bottom of the Well Basement)
    [0x00DC] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x901F, 0x0198, 0x72, no_upgrade, give_silver_rupee, SHADOW_ID,  0x04, resolve_text_silver_rupees), // Silver Rupee (Shadow Temple Scythe Shortcut)
    [0x00DD] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9020, 0x0198, 0x72, no_upgrade, give_silver_rupee, SHADOW_ID,  0x05, resolve_text_silver_rupees), // Silver Rupee (Shadow Temple Invisible Blades)
    [0x00DE] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9021, 0x0198, 0x72, no_upgrade, give_silver_rupee, SHADOW_ID,  0x06, resolve_text_silver_rupees), // Silver Rupee (Shadow Temple Huge Pit)
    [0x00DF] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9022, 0x0198, 0x72, no_upgrade, give_silver_rupee, SHADOW_ID,  0x07, resolve_text_silver_rupees), // Silver Rupee (Shadow Temple Invisible Spikes)
    [0x00E0] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9023, 0x0198, 0x72, no_upgrade, give_silver_rupee, GTG_ID,     0x08, resolve_text_silver_rupees), // Silver Rupee (Gerudo Training Ground Slopes)
    [0x00E1] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9024, 0x0198, 0x72, no_upgrade, give_silver_rupee, GTG_ID,     0x09, resolve_text_silver_rupees), // Silver Rupee (Gerudo Training Ground Lava)
    [0x00E2] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9025, 0x0198, 0x72, no_upgrade, give_silver_rupee, GTG_ID,     0x0A, resolve_text_silver_rupees), // Silver Rupee (Gerudo Training Ground Water)
    [0x00E3] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9026, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0B, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Child Early Torches)
    [0x00E4] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9027, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0C, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Adult Boulders)
    [0x00E5] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9028, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0D, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Lobby and Lower Adult)
    [0x00E6] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9029, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0E, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Sun Block)
    [0x00E7] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902A, 0x0198, 0x72, no_upgrade, give_silver_rupee, SPIRIT_ID,  0x0F, resolve_text_silver_rupees), // Silver Rupee (Spirit Temple Adult Climb)
    [0x00E8] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902B, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x10, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Spirit Trial)
    [0x00E9] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902C, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x11, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Light Trial)
    [0x00EA] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902D, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x12, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Fire Trial)
    [0x00EB] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902E, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x13, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Shadow Trial)
    [0x00EC] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x902F, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x14, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Water Trial)
    [0x00ED] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x85, -1, 0x9030, 0x0198, 0x72, no_upgrade, give_silver_rupee, CASTLE_ID,  0x15, resolve_text_silver_rupees), // Silver Rupee (Ganons Castle Forest Trial)

    [0x00EE] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901B, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, DODONGO_ID, 0x00, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Dodongos Cavern Staircase)
    [0x00EF] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901C, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, ICE_ID,     0x01, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ice Cavern Spinning Scythe)
    [0x00F0] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901D, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, ICE_ID,     0x02, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ice Cavern Push Block)
    [0x00F1] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901E, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, BOTW_ID,    0x03, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Bottom of the Well Basement)
    [0x00F2] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x901F, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SHADOW_ID,  0x04, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Shadow Temple Scythe Shortcut)
    [0x00F3] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9020, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SHADOW_ID,  0x05, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Shadow Temple Invisible Blades)
    [0x00F4] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9021, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SHADOW_ID,  0x06, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Shadow Temple Huge Pit)
    [0x00F5] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9022, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SHADOW_ID,  0x07, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Shadow Temple Invisible Spikes)
    [0x00F6] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9023, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, GTG_ID,     0x08, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Gerudo Training Ground Slopes)
    [0x00F7] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9024, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, GTG_ID,     0x09, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Gerudo Training Ground Lava)
    [0x00F8] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9025, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, GTG_ID,     0x0A, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Gerudo Training Ground Water)
    [0x00F9] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9026, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0B, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Child Early Torches)
    [0x00FA] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9027, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0C, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Adult Boulders)
    [0x00FB] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9028, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0D, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Lobby and Lower Adult)
    [0x00FC] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9029, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0E, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Sun Block)
    [0x00FD] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902A, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, SPIRIT_ID,  0x0F, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Spirit Temple Adult Climb)
    [0x00FE] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902B, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x10, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Spirit Trial)
    [0x00FF] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902C, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x11, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Light Trial)
    [0x0100] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902D, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x12, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Fire Trial)
    [0x0101] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902E, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x13, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Shadow Trial)
    [0x0102] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x902F, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x14, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Water Trial)
    [0x0103] = ITEM_ROW(0x4D,      SILVER_CHEST, 0x41, -1, 0x9030, 0x00D1, 0x7F, no_upgrade, give_silver_rupee_pouch, CASTLE_ID,  0x15, resolve_text_silver_rupee_pouches), // Silver Rupee Pouch (Ganons Castle Forest Trial)

    // Ocarina button models
    [0x0104] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x908C, 0x01A8, 0x90, no_upgrade, unlock_ocarina_note, 0, -1, NULL), // Ocarina A
    [0x0105] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x908D, 0x01AA, 0x91, no_upgrade, unlock_ocarina_note, 1, -1, NULL), // Ocarina C up
    [0x0106] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x908E, 0x01AA, 0x92, no_upgrade, unlock_ocarina_note, 2, -1, NULL), // Ocarina C down
    [0x0107] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x908F, 0x01A9, 0x93, no_upgrade, unlock_ocarina_note, 3, -1, NULL), // Ocarina C left
    [0x0108] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x9090, 0x01A9, 0x94, no_upgrade, unlock_ocarina_note, 4, -1, NULL), // Ocarina C right

    // Custom Key Models
    [0x0109] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0006, 0x01A3, 0x8A, no_upgrade, give_dungeon_item, 0x01, FOREST_ID, NULL), // Forest Temple Boss Key
    [0x010A] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001C, 0x01A4, 0x8B, no_upgrade, give_dungeon_item, 0x01, FIRE_ID,   NULL), // Fire Temple Boss Key
    [0x010B] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001D, 0x01A5, 0x8C, no_upgrade, give_dungeon_item, 0x01, WATER_ID,  NULL), // Water Temple Boss Key
    [0x010C] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x001E, 0x01A6, 0x8D, no_upgrade, give_dungeon_item, 0x01, SPIRIT_ID, NULL), // Spirit Temple Boss Key
    [0x010D] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x002A, 0x01A7, 0x8E, no_upgrade, give_dungeon_item, 0x01, SHADOW_ID, NULL), // Shadow Temple Boss Key
    [0x010E] = ITEM_ROW(0x53,        GOLD_CHEST, 0x41, -1, 0x0061, 0x00B9, 0x8F, no_upgrade, give_dungeon_item, 0x01, TOWER_ID,  NULL), // Ganon's Castle Boss Key

    [0x010F] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0093, 0x0199, 0x80, no_upgrade, give_small_key, FOREST_ID, -1, resolve_text_small_keys), // Forest Temple Small Key
    [0x0110] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0094, 0x019A, 0x81, no_upgrade, give_small_key, FIRE_ID,   -1, resolve_text_small_keys), // Fire Temple Small Key
    [0x0111] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x0095, 0x019B, 0x82, no_upgrade, give_small_key, WATER_ID,  -1, resolve_text_small_keys), // Water Temple Small Key
    [0x0112] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A6, 0x019C, 0x83, no_upgrade, give_small_key, SPIRIT_ID, -1, resolve_text_small_keys), // Spirit Temple Small Key
    [0x0113] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A9, 0x019D, 0x84, no_upgrade, give_small_key, SHADOW_ID, -1, resolve_text_small_keys), // Shadow Temple Small Key
    [0x0114] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009B, 0x019E, 0x85, no_upgrade, give_small_key, BOTW_ID,   -1, resolve_text_small_keys), // Bottom of the Well Small Key
    [0x0115] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x009F, 0x019F, 0x86, no_upgrade, give_small_key, GTG_ID,    -1, resolve_text_small_keys), // Gerudo Training Small Key
    [0x0116] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A0, 0x01A0, 0x87, no_upgrade, give_small_key, FORT_ID,   -1, resolve_text_small_keys), // Thieves' Hideout Small Key
    [0x0117] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00A1, 0x01A1, 0x88, no_upgrade, give_small_key, CASTLE_ID, -1, resolve_text_small_keys), // Ganon's Castle Small Key
    [0x0118] = ITEM_ROW(0x53,      SILVER_CHEST, 0x41, -1, 0x00F3, 0x01A2, 0x89, no_upgrade, give_small_key, TCG_ID,    -1, resolve_text_small_keys_cmg), // Small Key (Chest Game)

    [0x0119] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x90B4, 0x0177, 0x9E, no_upgrade, full_heal, -1, -1, NULL), // Fairy
    [0x011A] = ITEM_ROW(0x53,       BROWN_CHEST, 0x41, -1, 0x90B5, 0x0177, 0x9F, no_upgrade, no_effect, -1, -1, NULL), // Nothing :)

    // 0x011B through 0x0126 reserved for https://github.com/OoTRandomizer/OoT-Randomizer/pull/2108

    [0x0127] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0080, 0x01AB, 0x9B, no_upgrade, give_quest_item, 18, -1, NULL), // Kokiri Emerald
    [0x0128] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0081, 0x01AC, 0x9C, no_upgrade, give_quest_item, 19, -1, NULL), // Goron Ruby
    [0x0129] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0082, 0x01AD, 0x9D, no_upgrade, give_quest_item, 20, -1, NULL), // Zora Sapphire
    [0x012A] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0040, 0x01AE, 0x95, no_upgrade, give_quest_item,  5, -1, NULL), // Light Medallion
    [0x012B] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x003E, 0x01AF, 0x96, no_upgrade, give_quest_item,  0, -1, NULL), // Forest Medallion
    [0x012C] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x003C, 0x01B0, 0x97, no_upgrade, give_quest_item,  1, -1, NULL), // Fire Medallion
    [0x012D] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x003D, 0x01B1, 0x98, no_upgrade, give_quest_item,  2, -1, NULL), // Water Medallion
    [0x012E] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x0041, 0x01B2, 0x99, no_upgrade, give_quest_item,  4, -1, NULL), // Shadow Medallion
    [0x012F] = ITEM_ROW(0x53,      GILDED_CHEST, 0x41, -1, 0x003F, 0x01B3, 0x9A, no_upgrade, give_quest_item,  3, -1, NULL), // Spirit Medallion
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
    if (item_id >= array_size(item_table)) {
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
