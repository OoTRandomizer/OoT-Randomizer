#ifndef ITEM_UPGRADES_H
#define ITEM_UPGRADES_H

#include "get_items.h"
#include "z64.h"

typedef enum ProgressiveItemIdentifier {
    /*  0 */ PROG_ID_HOOKSHOT,
    /*  1 */ PROG_ID_STRENGTH,
    /*  2 */ PROG_ID_BOMB_BAG,
    /*  3 */ PROG_ID_BOW,
    /*  4 */ PROG_ID_SLINGSHOT,
    /*  5 */ PROG_ID_WALLET,
    /*  6 */ PROG_ID_SCALE,
    /*  7 */ PROG_ID_NUT,
    /*  8 */ PROG_ID_STICK,
    /*  9 */ PROG_ID_BOMBCHU,
    /* 10 */ PROG_ID_MAGIC,
    /* 11 */ PROG_ID_OCARINA,
    /* 12 */ PROG_ID_MAX,
} ProgressiveItemIdentifier;

extern uint16_t UPGRADEFUL_ITEM_FLAGS;

extern uint8_t CUSTOM_KEY_MODELS;

uint16_t no_upgrade(z64_file_t *save, override_t override);
uint16_t hookshot_upgrade(z64_file_t *save, override_t override);
uint16_t strength_upgrade(z64_file_t *save, override_t override);
uint16_t bomb_bag_upgrade(z64_file_t *save, override_t override);
uint16_t bow_upgrade(z64_file_t *save, override_t override);
uint16_t slingshot_upgrade(z64_file_t *save, override_t override);
uint16_t wallet_upgrade(z64_file_t *save, override_t override);
uint16_t scale_upgrade(z64_file_t *save, override_t override);
uint16_t nut_upgrade(z64_file_t *save, override_t override);
uint16_t stick_upgrade(z64_file_t *save, override_t override);
uint16_t magic_upgrade(z64_file_t *save, override_t override);
uint16_t bombchu_upgrade(z64_file_t *save, override_t override);
uint16_t ocarina_upgrade(z64_file_t *save, override_t override);
uint16_t arrows_to_rupee(z64_file_t *save, override_t override);
uint16_t bombs_to_rupee(z64_file_t *save, override_t override);
uint16_t seeds_to_rupee(z64_file_t *save, override_t override);
uint16_t letter_to_bottle(z64_file_t *save, override_t override);
uint16_t health_upgrade_cap(z64_file_t *save, override_t override);
uint16_t bombchus_to_bag(z64_file_t *save, override_t override);
uint16_t upgrade_key_model(z64_file_t *save, override_t override);
uint16_t max_upgrade_wallet_upgrade(z64_file_t *save, override_t override);

#endif
