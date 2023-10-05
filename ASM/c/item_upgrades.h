#ifndef ITEM_UPGRADES_H
#define ITEM_UPGRADES_H

#include "get_items.h"
#include "z64.h"

typedef enum ProgressiveItemIdentifier {
    /* 0 */ PROG_ID_HOOKSHOT,
    /* 1 */ PROG_ID_STRENGTH,
    /* 1 */ PROG_ID_BOMB_BAG,
    /* 1 */ PROG_ID_BOW,
    /* 1 */ PROG_ID_SLINGSHOT,
    /* 1 */ PROG_ID_WALLET,
    /* 1 */ PROG_ID_SCALE,
    /* 1 */ PROG_ID_NUT,
    /* 1 */ PROG_ID_STICK,
    /* 1 */ PROG_ID_BOMBCHU,
    /* 1 */ PROG_ID_MAGIC,
    /* 1 */ PROG_ID_OCARINA,
} ProgressiveItemIdentifier;

extern uint8_t upgradeful_item_flags;

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

#endif
