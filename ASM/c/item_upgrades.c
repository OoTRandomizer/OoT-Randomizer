#include "item_upgrades.h"

#include "get_items.h"
#include "z64.h"

extern uint32_t FREE_BOMBCHU_DROPS;


// The layout of this struct is part of the definition of the co-op context.
// If you change it, bump the co-op context version in coop_state.asm and update Notes/coop-ctx.md
typedef struct {
    uint16_t _pad : 9;  // reserved for future use
    bool chu_bag : 1;  // added in version 6 of the co-op context
    uint8_t ocarina : 2;  // 0 = no ocarina, 1 = fairy ocarina, 2 = ocarina of time
    uint8_t magic : 2;  // 0 = no magic, 1 = single magic, 2 = double magic
    uint8_t sticks : 2;  // 0 = no sticks, 1 = 10, 2 = 20, 3 = 30
    uint8_t nuts : 2;  // 0 = no nuts, 1 = 20, 2 = 30, 3 = 40
    uint8_t scale : 2;  // 0 = no scale, 1 = silver scale, 2 = gold scale
    uint8_t wallet : 2;  // 0 = 99, 1 = 200, 2 = 500, 3 = 999
    uint8_t slingshot : 2;  // 0 = no slingshot, 1 = 30, 2 = 40, 3 = 50
    uint8_t bow : 2;  // 0 = no bow, 1 = 30, 2 = 40, 3 = 50
    uint8_t bomb_bag : 2;  // 0 = no bomb bag, 1 = 20, 2 = 30, 3 = 40
    uint8_t strength : 2;  // 0 = no strength, 1 = Goron bracelet, 2 = silver gauntlets, 3 = gold gauntlets
    uint8_t hookshot : 2;  // 0 = no hookshot, 1 = hookshot, 2 = longshot
} mw_progressive_items_state_t;

// Co-op state
extern uint8_t PLAYER_ID;
extern uint8_t MW_PROGRESSIVE_ITEMS_ENABLE;
extern mw_progressive_items_state_t MW_PROGRESSIVE_ITEMS_STATE[256];

// 0x80000000 is used as a way to avoid this symbol to be placed on bss
uint32_t UPGRADEFUL_ITEM_FLAGS = 0x80000000;

uint16_t no_upgrade(z64_file_t *save, override_t override) {
    return override.value.base.item_id;
}

uint16_t hookshot_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_HOOKSHOT)) {
        INV_CONTENT(ITEM_LONGSHOT) = ITEM_LONGSHOT;
        return 0x09; // Longshot
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->items[Z64_SLOT_HOOKSHOT] : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].hookshot) {
        case -1: case 0: return 0x08; // Hookshot
        default: return 0x09; // Longshot
    }
}

uint16_t strength_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_STRENGTH)) {
        Inventory_ChangeUpgrade(UPG_STRENGTH, 3);
        return 0x36; // Gold Gauntlets
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->strength_upgrade : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].strength) {
        case 0: return 0x54; // Goron Bracelet
        case 1: return 0x35; // Silver Gauntlets
        default: return 0x36; // Gold Gauntlets
    }
}

uint16_t bomb_bag_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_BOMB_BAG)) {
        Inventory_ChangeUpgrade(UPG_BOMB_BAG, 3);
        INV_CONTENT(ITEM_BOMB) = ITEM_BOMB;
        AMMO(ITEM_BOMB) = CAPACITY(UPG_BOMB_BAG, 3);
        return 0x34;
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->bomb_bag : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].bomb_bag) {
        case 0: return 0x32; // Bomb Bag
        case 1: return 0x33; // Bigger Bomb Bag
        default: return 0x34; // Biggest Bomb Bag
    }
}

uint16_t bow_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_BOW)) {
        z64_Inventory_ChangeUpgrade(UPG_QUIVER, 3);
        INV_CONTENT(ITEM_BOW) = ITEM_BOW;
        AMMO(ITEM_BOW) = CAPACITY(UPG_QUIVER, 3);
        return 0x31; // Biggest Quiver
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->quiver : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].bow) {
        case 0: return 0x04; // Bow
        case 1: return 0x30; // Big Quiver
        default: return 0x31; // Biggest Quiver
    }
}

uint16_t slingshot_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_SLINGSHOT)) {
        Inventory_ChangeUpgrade(UPG_BULLET_BAG, 3);
        INV_CONTENT(ITEM_SLINGSHOT) = ITEM_SLINGSHOT;
        AMMO(ITEM_SLINGSHOT) = CAPACITY(UPG_BULLET_BAG, 3);
        return 0x7B; // Bullet Bag (50)
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->bullet_bag : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].slingshot) {
        case 0: return 0x05; // Slingshot
        case 1: return 0x60; // Bullet Bag (40)
        default: return 0x7B; // Bullet Bag (50)
    }
}

uint16_t wallet_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_WALLET)) {
        // TODO ?
        // Inventory_ChangeUpgrade(UPG_WALLET, 2);
        return 0xC7; // Tycoon's Wallet
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->wallet : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].wallet) {
        case 0: return 0x45; // Adult's Wallet
        case 1: return 0x46; // Giant's Wallet
        default: return 0xC7; // Tycoon's Wallet
    }
}

uint16_t scale_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_SCALE)) {
        Inventory_ChangeUpgrade(UPG_SCALE, 2);
        return 0x38; // Gold Scale
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->diving_upgrade : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].scale) {
        case 0: return 0x37; // Silver Scale
        default: return 0x38; // Gold Scale
    }
}

uint16_t nut_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_NUT)) {
        INV_CONTENT(ITEM_NUT) = ITEM_NUT;
        Inventory_ChangeUpgrade(UPG_DEKU_NUTS, 3);
        AMMO(ITEM_NUT) = CAPACITY(UPG_DEKU_NUTS, 3);
        return 0x7A; // 40 Nuts
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->nut_upgrade : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].nuts) {
        case 0: return 0x79; // 30 Nuts. 0 and 1 are both starting capacity
        case 1: return 0x79; // 30 Nuts
        default: return 0x7A; // 40 Nuts
    }
}

uint16_t stick_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_STICK)) {
        INV_CONTENT(ITEM_STICK) = ITEM_STICK;
        Inventory_ChangeUpgrade(UPG_DEKU_STICKS, 3);
        AMMO(ITEM_STICK) = CAPACITY(UPG_DEKU_STICKS, 3);
        return 0x78; // 30 Sticks
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->stick_upgrade : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].sticks) {
        case 0: return 0x77; // 20 Sticks. 0 and 1 are both starting capacity
        case 1: return 0x77; // 20 Sticks
        default: return 0x78; // 30 Sticks
    }
}

uint16_t magic_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_MAGIC)) {
        return 0xBA; // Double Magic
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->magic_acquired : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].magic) {
        case 0: return 0xB9; // Single Magic
        default: return 0xBA; // Double Magic
    }
}

uint16_t bombchu_upgrade(z64_file_t *save, override_t override) {
    // TODO

    if (INV_CONTENT(ITEM_BOMBCHU) == ITEM_NONE) {
        return 0x6B; // Bombchu 20 pack
    }
    if (AMMO(ITEM_BOMBCHU) <= 5) {
        return 0x03; // Bombchu 10 pack
    }
    return 0x6A; // Bombchu 5 pack
}

uint16_t ocarina_upgrade(z64_file_t *save, override_t override) {
    if (UPGRADEFUL_ITEM_FLAGS & (1 << PROG_ID_OCARINA)) {
        INV_CONTENT(ITEM_OCARINA_TIME) = ITEM_OCARINA_TIME;
        return 0x0C; // Ocarina of Time
    }

    switch ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->items[Z64_SLOT_OCARINA] : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].ocarina) {
        case -1: case 0: return 0x3B; // Fairy Ocarina
        default: return 0x0C; // Ocarina of Time
    }
}

uint16_t arrows_to_rupee(z64_file_t *save, override_t override) {
    return ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->quiver : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].bow) ? override.value.base.item_id : 0x4D; // Blue Rupee
}

uint16_t bombs_to_rupee(z64_file_t *save, override_t override) {
    return ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->bomb_bag : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].bomb_bag) ? override.value.base.item_id : 0x4D; // Blue Rupee
}

uint16_t seeds_to_rupee(z64_file_t *save, override_t override) {
    return ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->bullet_bag : MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].slingshot) ? override.value.base.item_id : 0x4D; // Blue Rupee
}

uint16_t letter_to_bottle(z64_file_t *save, override_t override) {
    if (save->event_chk_inf[3] & 0x0008) // "King Zora Moved Aside"
        return 0xC8; // Redundant Letter Bottle
    if (save->items[Z64_SLOT_BOTTLE_1] == 0x1B || save->items[Z64_SLOT_BOTTLE_2] == 0x1B
     || save->items[Z64_SLOT_BOTTLE_3] == 0x1B || save->items[Z64_SLOT_BOTTLE_4] == 0x1B)
        return 0xC8; // Redundant Letter Bottle
    return override.value.base.item_id;
}

uint16_t health_upgrade_cap(z64_file_t *save, override_t override) {
    if (save->energy_capacity >= 20 * 0x10) {  // Already at capped health.
        if (override.value.base.item_id == 0x76) {  // Piece of Heart (Chest Game)
            return 0x7F;
        }
        if (override.value.base.item_id == 0x3D) {  // Heart Container
            return 0x7E;
        }
        return 0x7D;          // Piece of Heart / Fallthrough
    }
    return override.value.base.item_id;
}

uint16_t bombchus_to_bag(z64_file_t *save, override_t override) {
    if (FREE_BOMBCHU_DROPS && ((override.value.base.player == PLAYER_ID || !MW_PROGRESSIVE_ITEMS_ENABLE) ? save->items[Z64_SLOT_BOMBCHU] == -1 : !MW_PROGRESSIVE_ITEMS_STATE[override.value.base.player].chu_bag)) {
        // First chu pack found, convert to bombchu bag to
        // tell player about chu drops. Different bags
        // to preserve original chu refill count.
        switch (override.value.base.item_id) {
            case 0x03: return 0xD5; // 10 pack
            case 0x6A: return 0xD6; // 5 pack
            case 0x6B: return 0xD4; // 20 pack
        }
    } else {
        // Subsequent chu packs stay as chu packs
        return override.value.base.item_id;
    }
}

uint16_t upgrade_key_model(z64_file_t *save, override_t override) {
    uint16_t item_id = override.value.base.item_id;
    if (CUSTOM_KEY_MODELS) {
        if (item_id == 0x0071) {
            // Treasure Chest Game Key
            return 0x0118;
        } else if (item_id < 0x00AF) {
            // Boss Keys
            return item_id + 0x74;
        } else {
            // Small Keys
            return item_id + 0x60;
        }
    } else {
        return item_id;
    }
}
