#include "item_draw_table.h"

#include "z64.h"
#include "item_draw_functions.h"

// This table should usually be changed to define new models and rendering routines for use in the item_table.
// To refer to a model, set the "graphic id" in the item_table row by the index in the draw table + 1.

// Each entry should contain a function called every frame when displaying the model, as well as optional segment addresses
// referring to display lists inside the object associated to this item, that may then be used in the specified function.

// Be very careful when inserting/removing entries somewhere other than the end of the table,
// because a lot of indexes for this table are still hardcoded throughout the game and rando code.

item_draw_table_entry_t item_draw_table[] = {
    [0x00] = { draw_gi_various_opa0_xlu1,   { 0x06000670, 0x06000750 } }, // Empty Bottle
    [0x01] = { draw_gi_small_keys,          { 0x06000800, 0xFFFFFFFF, 0x3C505AFF } }, // Small Key
    [0x02] = { draw_gi_song_notes,          { 0x06000AE0, 0x00C800FF } }, // Music Note (Green)
    [0x03] = { draw_gi_song_notes,          { 0x06000AE0, 0xFF3200FF } }, // Music Note (Red)
    [0x04] = { draw_gi_song_notes,          { 0x06000AE0, 0x0096FFFF } }, // Music Note (Blue)
    [0x05] = { draw_gi_song_notes,          { 0x06000AE0, 0xFF9600FF } }, // Music Note (Orange)
    [0x06] = { draw_gi_song_notes,          { 0x06000AE0, 0xC832FFFF } }, // Music Note (Purple)
    [0x07] = { draw_gi_song_notes,          { 0x06000AE0, 0xC8FF00FF } }, // Music Note (Yellow)
    [0x08] = { draw_gi_recovery_heart,      { 0x060000E0 } }, // Recovery Heart
    [0x09] = { draw_gi_boss_keys,           { 0x06000CA0, 0x06000F08, 0xFFAAFFFF, 0xFF0064FF } }, // Boss Key
    [0x0A] = { draw_gi_compass,             { 0x06000960, 0x06000C50 } }, // Compass
    [0x0B] = { draw_gi_eggs_and_medallions, { 0x06000CB0, 0x06000E18 } }, // Forest Medallion
    [0x0C] = { draw_gi_eggs_and_medallions, { 0x06001AF0, 0x06000E18 } }, // Fire Medallion
    [0x0D] = { draw_gi_eggs_and_medallions, { 0x06002830, 0x06000E18 } }, // Water Medallion
    [0x0E] = { draw_gi_eggs_and_medallions, { 0x06003610, 0x06000E18 } }, // Spirit Medallion
    [0x0F] = { draw_gi_eggs_and_medallions, { 0x06004330, 0x06000E18 } }, // Shadow Medallion
    [0x10] = { draw_gi_eggs_and_medallions, { 0x06005220, 0x06000E18 } }, // Light Medallion
    [0x11] = { draw_gi_deku_nut,            { 0x06000E90 } }, // Deku Nut
    [0x12] = { draw_gi_various_xlu01,       { 0x06001290, 0x06001470 } }, // Heart Container
    [0x13] = { draw_gi_various_xlu01,       { 0x06001290, 0x06001590 } }, // Piece of Heart
    [0x14] = { draw_gi_various_opa1023,     { 0x06000990, 0x060008D0, 0x06000930, 0x06000A80 } }, // Quiver
    [0x15] = { draw_gi_various_opa1023,     { 0x06000990, 0x060008F0, 0x06000950, 0x06000A80 } }, // Big Quiver
    [0x16] = { draw_gi_various_opa1023,     { 0x06000990, 0x06000910, 0x06000970, 0x06000A80 } }, // Biggest Quiver
    [0x17] = { draw_gi_various_opa1023,     { 0x06000B90, 0x06000AD0, 0x06000B30, 0x06000D98 } }, // Bomb Bag
    [0x18] = { draw_gi_various_opa1023,     { 0x06000B90, 0x06000AF0, 0x06000B50, 0x06000D98 } }, // Big Bomb Bag
    [0x19] = { draw_gi_various_opa1023,     { 0x06000B90, 0x06000B10, 0x06000B70, 0x06000D98 } }, // Biggest Bomb Bag
    [0x1A] = { draw_gi_various_opa0,        { 0x060004D0 } }, // Deku Stick
    [0x1B] = { draw_gi_various_opa0,        { 0x060003C0 } }, // Map
    [0x1C] = { draw_gi_various_opa0,        { 0x06000A50 } }, // Deku Shield
    [0x1D] = { draw_gi_various_opa0,        { 0x06000580 } }, // Small Magic Jar
    [0x1E] = { draw_gi_various_opa0,        { 0x06000EE0 } }, // Large Magic Jar
    [0x1F] = { draw_gi_various_opa0,        { 0x060009A0 } }, // Bomb
    [0x20] = { draw_gi_various_opa0,        { 0x06000B70 } }, // Stone of Agony
    [0x21] = { draw_gi_wallets,             { 0x06001850, 0x06001750, 0x06001790, 0x060019A0, 0x060017B0, 0x06001A28, 0x060017D0, 0x06001AD8 } }, // Adult's Wallet
    [0x22] = { draw_gi_wallets,             { 0x06001850, 0x06001770, 0x060017F0, 0x060019A0, 0x06001810, 0x06001A28, 0x06001830, 0x06001AD8 } }, // Giant's Wallet
    [0x23] = { draw_gi_various_opa0,        { 0x06000F60 } }, // Gerudo's Card
    [0x24] = { draw_gi_various_opa0,        { 0x06000340 } }, // Arrow
    [0x25] = { draw_gi_various_opa0,        { 0x06000B90 } }, // Arrows (2)
    [0x26] = { draw_gi_various_opa0,        { 0x06001830 } }, // Arrows (3)
    [0x27] = { draw_gi_bombchu_and_masks,   { 0x060004B0 } }, // Bombchu
    [0x28] = { draw_gi_eggs_and_medallions, { 0x06000FD0, 0x06001008 } }, // Weird Egg & Pocket Egg
    [0x29] = { draw_gi_scales,              { 0x06000AA0, 0x06000A20, 0x06000A60, 0x06000CC8 } }, // Silver Scale
    [0x2A] = { draw_gi_scales,              { 0x06000AA0, 0x06000A40, 0x06000A80, 0x06000CC8 } }, // Golden Scale
    [0x2B] = { draw_gi_various_opa0,        { 0x06000C70 } }, // Hylian Shield
    [0x2C] = { draw_gi_various_opa0,        { 0x06000750 } }, // Hookshot
    [0x2D] = { draw_gi_various_opa0,        { 0x06001240 } }, // Longshot
    [0x2E] = { draw_gi_various_opa0_xlu1,   { 0x060008C0, 0x06000AF8 } }, // Ocarina of Time
    [0x2F] = { draw_gi_various_opa0_xlu1,   { 0x06001060, 0x06001288 } }, // Lon Lon Milk
    [0x30] = { draw_gi_various_opa0_xlu1,   { 0x06000AC0, 0x06000D50 } }, // Keaton Mask
    [0x31] = { draw_gi_various_opa0,        { 0x060007E0 } }, // Spooky Mask
    [0x32] = { draw_gi_various_opa0,        { 0x06000940 } }, // Fairy Slingshot
    [0x33] = { draw_gi_various_opa0,        { 0x06000A30 } }, // Boomerang
    [0x34] = { draw_gi_various_opa0,        { 0x06000990 } }, // Fairy Bow
    [0x35] = { draw_gi_various_opa0_xlu1,   { 0x06000D80, 0x06001010 } }, // Lens of Truth
    [0x36] = { draw_gi_potions,             { 0x06001438, 0x06001270, 0x060012D0, 0x06001790, 0x06001330, 0x06001848 } }, // Green Potion
    [0x37] = { draw_gi_potions,             { 0x06001438, 0x06001290, 0x060012F0, 0x06001790, 0x06001388, 0x06001848 } }, // Red Potion
    [0x38] = { draw_gi_potions,             { 0x06001438, 0x060012B0, 0x06001310, 0x06001790, 0x060013E0, 0x06001848 } }, // Blue Potion
    [0x39] = { draw_gi_mirror_shield,       { 0x06000FB0, 0x060011C8 } }, // Mirror Shield
    [0x3A] = { draw_gi_various_opa0_xlu1,   { 0x06000CC0, 0x06000D60 } }, // Zelda's Letter
    [0x3B] = { draw_gi_various_opa1023,     { 0x06001560, 0x060014E0, 0x06001520, 0x06001608 } }, // Goron Tunic
    [0x3C] = { draw_gi_various_opa1023,     { 0x06001560, 0x06001500, 0x06001540, 0x06001608 } }, // Zora Tunic
    [0x3D] = { draw_gi_various_opa0,        { 0x06000580 } }, // Magic Bean
    [0x3E] = { draw_gi_fish_bottle,         { 0x06000600 } }, // Fish
    [0x3F] = { draw_gi_various_opa0,        { 0x060007E0 } }, // Poacher's Saw
    [0x40] = { draw_gi_various_opa0,        { 0x060009D0 } }, // Megaton Hammer
    [0x41] = { draw_gi_various_opa0,        { 0x060008E0 } }, // Reed Whistle
    [0x42] = { draw_gi_goron_swords,        { 0x06000600 } }, // Giant's Knife & Biggoron's Sword
    [0x43] = { draw_gi_coins_and_cuccos,    { 0x06001630, 0x060015F0, 0x06001948 } }, // Chicken & Pocket Cucco
    [0x44] = { draw_gi_various_opa0_xlu1,   { 0x060008E0, 0x06000AE0 } }, // Bottled Ruto's Letter
    [0x45] = { draw_gi_various_opa0_xlu1,   { 0x060008E0, 0x06000B58 } }, // Fairy Ocarina
    [0x46] = { draw_gi_various_opa0_xlu1,   { 0x06001630, 0x06001A98 } }, // Iron Boots
    [0x47] = { draw_gi_various_opa0,        { 0x06000810 } }, // Deku Seeds
    [0x48] = { draw_gi_various_opa10_xlu32, { 0x06001540, 0x060014C0, 0x06001860, 0x06001500 } }, // Silver Gauntlets
    [0x49] = { draw_gi_various_opa10_xlu32, { 0x06001540, 0x060014E0, 0x06001860, 0x06001520 } }, // Golden Gauntlets
    [0x4A] = { draw_gi_coins_and_cuccos,    { 0x060005E0, 0x06000560, 0x06000768 } }, // N Coin (Yellow)
    [0x4B] = { draw_gi_coins_and_cuccos,    { 0x060005E0, 0x06000580, 0x06000768 } }, // N Coin (Red)
    [0x4C] = { draw_gi_coins_and_cuccos,    { 0x060005E0, 0x060005A0, 0x06000768 } }, // N Coin (Green)
    [0x4D] = { draw_gi_coins_and_cuccos,    { 0x060005E0, 0x060005C0, 0x06000768 } }, // N Coin (Blue)
    [0x4E] = { draw_gi_various_opa0,        { 0x060009D0 } }, // Skull Mask
    [0x4F] = { draw_gi_various_opa0_xlu1,   { 0x06000BC0, 0x06000E58 } }, // Bunny Hood
    [0x50] = { draw_gi_various_opa0_xlu1,   { 0x060013D0, 0x060016B0 } }, // Mask of Truth
    [0x51] = { draw_gi_various_opa0_xlu1,   { 0x06000680, 0x06000768 } }, // Eye Drops
    [0x52] = { draw_gi_various_opa0,        { 0x060008B0 } }, // Odd Potion
    [0x53] = { draw_gi_various_opa0,        { 0x060009D0 } }, // Odd Mushroom
    [0x54] = { draw_gi_various_opa0_xlu1,   { 0x06000F00, 0x06001188 } }, // Claim Check
    [0x55] = { draw_gi_goron_swords,        { 0x060006E0 } }, // Giant's Knife & Biggoron's Sword (Broken)
    [0x56] = { draw_gi_various_opa0_xlu1,   { 0x060009C0, 0x06000AF0 } }, // Prescription
    [0x57] = { draw_gi_various_opa0,        { 0x06000960 } }, // Goron's Bracelet
    [0x58] = { draw_gi_sold_out,            { 0x06000440 } }, // SOLD OUT
    [0x59] = { draw_gi_various_opa0_xlu1,   { 0x06000D60, 0x06001060 } }, // Eyeball Frog
    [0x5A] = { draw_gi_bombchu_and_masks,   { 0x060014F8 } }, // Goron Mask
    [0x5B] = { draw_gi_bombchu_and_masks,   { 0x06001398 } }, // Zora Mask
    [0x5C] = { draw_gi_bombchu_and_masks,   { 0x060010E8 } }, // Gerudo Mask
    [0x5D] = { draw_gi_coins_and_cuccos,    { 0x06001630, 0x06001610, 0x06001948 } }, // Cojiro
    [0x5E] = { draw_gi_various_opa0,        { 0x06001850 } }, // Hover Boots
    [0x5F] = { draw_gi_magic_arrows,        { 0x06000AE0, 0x06000CA0, 0x06000D00 } }, // Fire Arrow
    [0x60] = { draw_gi_magic_arrows,        { 0x06000AE0, 0x06000CC0, 0x06000D00 } }, // Ice Arrow
    [0x61] = { draw_gi_magic_arrows,        { 0x06000AE0, 0x06000CE0, 0x06000D00 } }, // Light Arrow
    [0x62] = { draw_gi_gs_token,            { 0x06000330, 0x06000438 } }, // Gold Skulltula Token I (commonly used)
    [0x63] = { draw_gi_magic_spells,        { 0x06000920, 0x060009E0, 0x06000A40 } }, // Din's Fire
    [0x64] = { draw_gi_magic_spells,        { 0x06000920, 0x06000A00, 0x06000A40 } }, // Farore's Wind
    [0x65] = { draw_gi_magic_spells,        { 0x06000920, 0x06000A20, 0x06000A40 } }, // Nayru's Love
    [0x66] = { draw_gi_blue_fire_candle,    { 0x06000C60, 0x06000F08 } }, // Blue Fire
    [0x67] = { draw_gi_various_opa0_xlu1,   { 0x06000830, 0x06000B20 } }, // Bug
    [0x68] = { draw_gi_various_opa0_xlu1,   { 0x06000830, 0x06000A70 } }, // Butterfly
    [0x69] = { draw_gi_poe_bottles,         { 0x06000990, 0x06000BE0, 0x06000CF0, 0x06000950 } }, // Poe
    [0x6A] = { draw_gi_fairy_lantern,       { 0x06000BD0, 0x06000DB8, 0x06000EF0 } }, // Fairy
    [0x6B] = { draw_gi_bullet_bags,         { 0x06000B70, 0x06000AF0, 0x06000F48, 0x06000B30, 0x06000FF0 } }, // Bullet Bag (40)
    [0x6C] = { draw_gi_small_rupees,        { 0x060005E0, 0x060004A0, 0x060006F0, 0x06000540 } }, // Green Rupee
    [0x6D] = { draw_gi_small_rupees,        { 0x060005E0, 0x060004C0, 0x060006F0, 0x06000560 } }, // Blue Rupee
    [0x6E] = { draw_gi_small_rupees,        { 0x060005E0, 0x060004E0, 0x060006F0, 0x06000580 } }, // Red Rupee
    [0x6F] = { draw_gi_poe_bottles,         { 0x06000990, 0x06000BE0, 0x06000CF0, 0x06000970 } }, // Big Poe
    [0x70] = { draw_gi_various_opa10_xlu32, { 0x060005E0, 0x06000500, 0x060006F0, 0x060005A0 } }, // Purple Rupee
    [0x71] = { draw_gi_various_opa10_xlu32, { 0x060005E0, 0x06000520, 0x060006F0, 0x060005C0 } }, // Huge Rupee
    [0x72] = { draw_gi_bullet_bags,         { 0x06000B70, 0x06000B10, 0x06000F48, 0x06000B50, 0x06000FF0 } }, // Bullet Bag (50)
    [0x73] = { draw_gi_various_opa0,        { 0x06000960 } }, // Kokiri Sword
    [0x74] = { draw_gi_gs_token,            { 0x06004DB0, 0x06004EB8 } }, // Gold Skulltula Token II (only for En_Si)

    //Rando-added functions
    [0x75] = { draw_gi_various_opa0,        { 0x06000A30 } }, // Triforce Piece
    [0x76] = { draw_gi_various_opa0,        { 0x060015E8 } }, // Key Ring
};

void base_draw_gi_model(z64_game_t *game, uint32_t draw_id) {
    item_draw_table[draw_id].draw_func(game, draw_id);
}
