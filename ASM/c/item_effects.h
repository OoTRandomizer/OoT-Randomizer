#ifndef ITEM_EFFECTS_H
#define ITEM_EFFECTS_H

#include "z64.h"
#include "icetrap.h"
#include "triforce.h"
#include "ocarina_buttons.h"

void no_effect(z64_file_t* save, int16_t arg1, int16_t arg2);
void full_heal(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_triforce_piece(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_tycoon_wallet(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_biggoron_sword(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_bottle(z64_file_t* save, int16_t bottle_item_id, int16_t arg2);
void give_dungeon_item(z64_file_t* save, int16_t mask, int16_t dungeon_id);
void give_small_key(z64_file_t* save, int16_t dungeon_id, int16_t arg2);
void give_small_key_ring(z64_file_t* save, int16_t dungeon_id, int16_t arg2);
void give_silver_rupee(z64_file_t* save, int16_t dungeon_id, int16_t silver_rupee_id);
void give_silver_rupee_pouch(z64_file_t* save, int16_t dungeon_id, int16_t silver_rupee_id);
void give_defense(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_magic(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_double_magic(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_fairy_ocarina(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_quest_item(z64_file_t* save, int16_t quest_bit, int16_t arg2);
void ice_trap_effect(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_bean_pack(z64_file_t* save, int16_t arg1, int16_t arg2);
void fill_wallet_upgrade(z64_file_t* save, int16_t arg1, int16_t arg2);
void clear_excess_hearts(z64_file_t* save, int16_t arg1, int16_t arg2);
void open_gate_and_mask_shop(z64_file_t* save, int16_t arg1, int16_t arg2);
void give_bombchus(z64_file_t* save, int16_t arg1, int16_t arg2);
void trade_quest_upgrade(z64_file_t* save, int16_t item_id, int16_t arg2);
extern uint8_t KEYRING_BOSSKEY_CONDITION;
void unlock_ocarina_note(z64_file_t* save, int16_t arg1, int16_t arg2);

typedef enum dungeon {
    DEKU_ID       = 0,
    DODONGO_ID    = 1,
    JABU_ID       = 2,
    FOREST_ID     = 3,
    FIRE_ID       = 4,
    WATER_ID      = 5,
    SPIRIT_ID     = 6,
    SHADOW_ID     = 7,
    BOTW_ID       = 8,
    ICE_ID        = 9,
    TOWER_ID      = 10,
    GTG_ID        = 11,
    FORT_ID       = 12,
    CASTLE_ID     = 13,
    TOWER_COL_ID  = 14,
    CASTLE_COL_ID = 15,
    TCG_ID        = 16,
} dungeon;

typedef struct {
    uint8_t needed_count;
    uint8_t switch_flag;
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t room;
} silver_rupee_data_t;

extern char key_counts[17][2];
extern silver_rupee_data_t silver_rupee_vars[0x16][2];

#endif
