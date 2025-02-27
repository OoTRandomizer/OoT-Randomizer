#ifndef MESSAGE_H
#define MESSAGE_H

#include "z64.h"

void Inventory_ChangeEquipment(int16_t equipment, uint16_t value);
uint8_t Message_ShouldAdvance(z64_game_t* play);
void Player_SetEquipmentData(z64_game_t* play, z64_link_t* player);

void equip_kokiri_sword_message(z64_file_t* save, int16_t arg1, int16_t arg2);
void equip_biggoron_sword_message(z64_file_t* save, int16_t arg1, int16_t arg2);
void equip_deku_shield_message(z64_file_t* save, int16_t arg1, int16_t arg2);
void equip_hylian_shield_message(z64_file_t* save, int16_t arg1, int16_t arg2);
void equip_mirror_shield_message(z64_file_t* save, int16_t arg1, int16_t arg2);
void equip_goron_tunic_message(z64_file_t* save, int16_t arg1, int16_t arg2);
void equip_zora_tunic_message(z64_file_t* save, int16_t arg1, int16_t arg2);
void display_misc_messages();

#endif
