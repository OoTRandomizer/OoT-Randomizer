#ifndef ITEM_EFFECTS_H
#define ITEM_EFFECTS_H

#include "z64.h"

void no_effect(z64_file_t *save, int16_t arg1, int16_t arg2);
void give_tycoon_wallet(z64_file_t *save, int16_t arg1, int16_t arg2);
void give_biggoron_sword(z64_file_t *save, int16_t arg1, int16_t arg2);
void give_bottle(z64_file_t *save, int16_t bottle_item_id, int16_t arg2);
void give_dungeon_item(z64_file_t *save, int16_t mask, int16_t dungeon_id);
void give_small_key(z64_file_t *save, int16_t dungeon_id, int16_t arg2);
void give_defense(z64_file_t *save, int16_t arg1, int16_t arg2);
void give_magic(z64_file_t *save, int16_t arg1, int16_t arg2);
void give_double_magic(z64_file_t *save, int16_t arg1, int16_t arg2);
void give_fairy_ocarina(z64_file_t *save, int16_t arg1, int16_t arg2);
void give_song(z64_file_t *save, int16_t quest_bit, int16_t arg2);
void ice_trap_effect(z64_file_t *save, int16_t arg1, int16_t arg2);

#endif
