#ifndef ITEM_UPGRADES_H
#define ITEM_UPGRADES_H

#include "get_items.h"
#include "z64.h"

extern uint8_t CUSTOM_KEY_MODELS;

uint16_t no_upgrade(z64_file_t* save, override_t override);
uint16_t hookshot_upgrade(z64_file_t* save, override_t override);
uint16_t strength_upgrade(z64_file_t* save, override_t override);
uint16_t bomb_bag_upgrade(z64_file_t* save, override_t override);
uint16_t bow_upgrade(z64_file_t* save, override_t override);
uint16_t slingshot_upgrade(z64_file_t* save, override_t override);
uint16_t wallet_upgrade(z64_file_t* save, override_t override);
uint16_t scale_upgrade(z64_file_t* save, override_t override);
uint16_t nut_upgrade(z64_file_t* save, override_t override);
uint16_t stick_upgrade(z64_file_t* save, override_t override);
uint16_t magic_upgrade(z64_file_t* save, override_t override);
uint16_t bombchu_upgrade(z64_file_t* save, override_t override);
uint16_t ocarina_upgrade(z64_file_t* save, override_t override);
uint16_t arrows_to_rupee(z64_file_t* save, override_t override);
uint16_t bombs_to_rupee(z64_file_t* save, override_t override);
uint16_t seeds_to_rupee(z64_file_t* save, override_t override);
uint16_t letter_to_bottle(z64_file_t* save, override_t override);
uint16_t health_upgrade_cap(z64_file_t* save, override_t override);
uint16_t bombchus_to_bag(z64_file_t* save, override_t override);
uint16_t upgrade_key_model(z64_file_t* save, override_t override);

#endif
