#include "item_effects.h"
#include "dungeon_info.h"
#include "trade_quests.h"
#include "bg_gate_shutter.h"
#include "save.h"

#define rupee_cap ((uint16_t*)0x800F8CEC)
volatile uint8_t MAX_RUPEES = 0;

typedef void (*commit_scene_flags_fn)(z64_game_t* game_ctxt);
#define commit_scene_flags ((commit_scene_flags_fn)0x8009D894)
typedef void (*save_game_fn)(void* unk);
#define save_game ((save_game_fn)0x800905D4)

void no_effect(z64_file_t* save, int16_t arg1, int16_t arg2) {
}

void full_heal(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->refill_hearts = 20 * 0x10;
}

void give_triforce_piece(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->scene_flags[0x48].unk_00_ += 1; //Unused word in scene x48.
    set_triforce_render();

    // Trigger win when the target is hit
    if (save->scene_flags[0x48].unk_00_ == TRIFORCE_PIECES_REQUIRED) {
        // Give GC boss key to allow beating the game again afterwards
        give_dungeon_item(save, 0x01, 10);

        // Save Game
        save->entrance_index = z64_game.entrance_index;
        save->scene_index = z64_game.scene_index;
        commit_scene_flags(&z64_game);
        save_game(&z64_game + 0x1F74);

        // warp to start of credits sequence
        z64_file.cutscene_next = 0xFFF8;
        z64_game.entrance_index = 0x00A0;
        z64_game.scene_load_flag = 0x14;
        z64_game.fadeout_transition = 0x01;
    }
}

void give_tycoon_wallet(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->wallet = 3;
    if(MAX_RUPEES)
        save->rupees = rupee_cap[arg1];
}

void give_biggoron_sword(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->bgs_flag = 1; // Set flag to make the sword durable
}

void give_bottle(z64_file_t* save, int16_t bottle_item_id, int16_t arg2) {
    for (int i = Z64_SLOT_BOTTLE_1; i <= Z64_SLOT_BOTTLE_4; i++) {
        if (save->items[i] == ITEM_NONE) {
            save->items[i] = bottle_item_id;
            return;
        }
    }
}

void give_dungeon_item(z64_file_t* save, int16_t mask, int16_t dungeon_id) {
    save->dungeon_items[dungeon_id].items |= mask;
}

char key_counts[17][2] = {
    {0, 0}, // Deku Tree
    {0, 0}, // Dodongo's Cavern
    {0, 0}, // Inside Jabu Jabu's Belly
    {5, 6}, // Forest Temple
    {8, 5}, // Fire Temple
    {6, 2}, // Water Temple
    {5, 7}, // Spirit Temple
    {5, 6}, // Shadow Temple
    {3, 2}, // Bottom of the Well
    {0, 0}, // Ice Cavern
    {0, 0}, // Ganon's Tower
    {9, 3}, // Gerudo Training Ground
    {4, 4}, // Thieves' Hideout
    {2, 3}, // Ganon's Castle
    {0, 0}, // Ganon's Tower (Collapsing)
    {0, 0}, // Ganon's Castle (Collapsing)
    {6, 6}, // Treasure Box Shop
};

void give_small_key(z64_file_t* save, int16_t dungeon_id, int16_t arg2) {
    int8_t current_keys = save->dungeon_keys[dungeon_id] > 0 ? save->dungeon_keys[dungeon_id] : 0;
    save->dungeon_keys[dungeon_id] = current_keys + 1;
    uint32_t flag = save->scene_flags[dungeon_id].unk_00_;
    int8_t total_keys = flag >> 0x10;
    int8_t max_keys = key_counts[dungeon_id][CFG_DUNGEON_IS_MQ[dungeon_id]];
    if (total_keys < max_keys) {
        save->scene_flags[dungeon_id].unk_00_ = (flag & 0x0000ffff) | ((total_keys + 1) << 0x10);
    }
}

void give_small_key_ring(z64_file_t* save, int16_t dungeon_id, int16_t arg2) {
    int8_t current_keys = save->dungeon_keys[dungeon_id] > 0 ? save->dungeon_keys[dungeon_id] : 0;
    save->dungeon_keys[dungeon_id] = current_keys + key_counts[dungeon_id][CFG_DUNGEON_IS_MQ[dungeon_id]];
    if (KEYRING_BOSSKEY_CONDITION && dungeon_id > 2 && dungeon_id < 8) {
        save->dungeon_items[dungeon_id].boss_key = 1;
    }
    uint32_t flag = save->scene_flags[dungeon_id].unk_00_;
    int8_t max_keys = key_counts[dungeon_id][CFG_DUNGEON_IS_MQ[dungeon_id]];
    save->scene_flags[dungeon_id].unk_00_ = (flag & 0x0000ffff) | (max_keys << 0x10);
}

silver_rupee_data_t silver_rupee_vars[0x16][2] = {
    //Vanilla,                         Master Quest
    {{-1, 0xFF, 0x00, 0x00, 0x00,  2}, { 5, 0x1F, 0xFF, 0xFF, 0xFF,  2}}, // Dodongos Cavern Staircase. Patched to use switch flag 0x1F
    {{ 5, 0x08, 0x00, 0xFF, 0xFF,  3}, {-1, 0xFF, 0x00, 0x00, 0x00,  3}}, // Ice Cavern Spinning Scythe
    {{ 5, 0x09, 0x00, 0x64, 0xFF,  5}, {-1, 0xFF, 0x00, 0x00, 0x00,  5}}, // Ice Cavern Push Block
    {{ 5, 0x1F, 0xFF, 0xFF, 0xFF,  1}, {-1, 0xFF, 0x00, 0x00, 0x00,  1}}, // Bottom of the Well Basement
    {{ 5, 0x01, 0x00, 0xFF, 0x00,  6}, { 5, 0x01, 0x00, 0xFF, 0x00,  6}}, // Shadow Temple Scythe Shortcut
    {{-1, 0xFF, 0x00, 0x00, 0x00, 16}, {10, 0x03, 0x00, 0xFF, 0xFF, 16}}, // Shadow Temple Invisible Blades
    {{ 5, 0x09, 0xC8, 0xC8, 0x00,  9}, { 5, 0x11, 0xC8, 0xC8, 0x00,  9}}, // Shadow Temple Huge Pit
    {{ 5, 0x08, 0xC8, 0x32, 0xFF, 11}, {10, 0x08, 0xC8, 0x32, 0xFF, 11}}, // Shadow Temple Invisible Spikes
    {{ 5, 0x1C, 0xC8, 0xC8, 0x00,  2}, { 5, 0x1C, 0xC8, 0xC8, 0x00,  2}}, // Gerudo Training Ground Slopes
    {{ 5, 0x0C, 0xFF, 0x3C, 0x00,  6}, { 6, 0x0C, 0xFF, 0x3C, 0x00,  6}}, // Gerudo Training Ground Lava
    {{ 5, 0x1B, 0x00, 0x64, 0xFF,  9}, { 3, 0x1B, 0x00, 0x64, 0xFF,  9}}, // Gerudo Training Ground Water
    {{ 5, 0x05, 0xFF, 0x3C, 0x00,  2}, {-1, 0xFF, 0x00, 0x00, 0x00,  2}}, // Spirit Temple Child Early Torches
    {{ 5, 0x02, 0x00, 0xFF, 0x00, 13}, {-1, 0xFF, 0x00, 0x00, 0x00, 13}}, // Spirit Temple Adult Boulders
    {{-1, 0xFF, 0x00, 0x00, 0x00,  0}, { 5, 0x1F, 0x00, 0xFF, 0xFF,  0}}, // Spirit Temple Lobby and Lower Adult. Patched to use switch flag 0x1F
    {{ 5, 0x0A, 0xC8, 0xC8, 0x00,  8}, {-1, 0xFF, 0x00, 0x00, 0x00,  8}}, // Spirit Temple Sun Block
    {{-1, 0xFF, 0x00, 0x00, 0x00, 23}, { 5, 0x00, 0x00, 0x64, 0xFF, 23}}, // Spirit Temple Adult Climb
    {{ 5, 0x0B, 0xC8, 0xC8, 0x00, 17}, {-1, 0xFF, 0x00, 0x00, 0x00, 17}}, // Ganons Castle Spirit Trial
    {{ 5, 0x12, 0x00, 0xFF, 0xFF,  8}, {-1, 0xFF, 0x00, 0x00, 0x00,  8}}, // Ganons Castle Light Trial
    {{ 5, 0x09, 0xFF, 0x3C, 0x00, 14}, { 5, 0x01, 0xFF, 0x3C, 0x00, 14}}, // Ganons Castle Fire Trial
    {{-1, 0xFF, 0x00, 0x00, 0x00, 12}, { 5, 0x0B, 0xC8, 0x32, 0xFF, 12}}, // Ganons Castle Shadow Trial
    {{-1, 0xFF, 0x00, 0x00, 0x00,  3}, { 5, 0x02, 0x00, 0x64, 0xFF,  3}}, // Ganons Castle Water Trial
    {{ 5, 0x0E, 0x00, 0xFF, 0x00,  6}, {-1, 0xFF, 0x00, 0x00, 0x00,  6}}, // Ganons Castle Forest Trial
};

void set_silver_rupee_flags(z64_file_t* save, int16_t dungeon_id, int16_t silver_rupee_id) {
    silver_rupee_data_t var = silver_rupee_vars[silver_rupee_id][CFG_DUNGEON_IS_MQ[dungeon_id]];

    if (silver_rupee_id == 8) { // GTG Boulder room needs to set room clear flag as well in order to make the timer go away. Maybe others?
        if (z64_game.scene_index == dungeon_id) {
            z64_game.clear_flags |= 1 << 2;
            z64_game.temp_clear_flags |= 1 << 2;
        } else {
            save->scene_flags[dungeon_id].clear |= 1 << 2;
        }
    }
    if (z64_game.scene_index == dungeon_id) {
        z64_game.swch_flags |= 1 << var.switch_flag;
    } else {
        save->scene_flags[dungeon_id].swch |= 1 << var.switch_flag;
    }
}

void give_silver_rupee(z64_file_t* save, int16_t dungeon_id, int16_t silver_rupee_id) {
    silver_rupee_data_t var = silver_rupee_vars[silver_rupee_id][CFG_DUNGEON_IS_MQ[dungeon_id]];

    if (extended_savectx.silver_rupee_counts[silver_rupee_id] == var.needed_count) return;
    extended_savectx.silver_rupee_counts[silver_rupee_id]++;

    if (extended_savectx.silver_rupee_counts[silver_rupee_id] == var.needed_count) {
        set_silver_rupee_flags(save, dungeon_id, silver_rupee_id);
    }
}

void give_silver_rupee_pouch(z64_file_t* save, int16_t dungeon_id, int16_t silver_rupee_id) {
    silver_rupee_data_t var = silver_rupee_vars[silver_rupee_id][CFG_DUNGEON_IS_MQ[dungeon_id]];

    Rupees_ChangeBy(5 * var.needed_count);

    if (extended_savectx.silver_rupee_counts[silver_rupee_id] == var.needed_count) return;
    extended_savectx.silver_rupee_counts[silver_rupee_id] = var.needed_count;

    set_silver_rupee_flags(save, dungeon_id, silver_rupee_id);
}

void give_defense(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->double_defense = 1;
    save->defense_hearts = 20;
    save->refill_hearts = 20 * 0x10;
}

void give_magic(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->magic_capacity_set = 1; // Set meter level
    save->magic_acquired = 1; // Required for meter to persist on save load
    save->magic_meter_size = 0x30; // Set meter size
    save->magic = 0x30; // Fill meter
}

void give_double_magic(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->magic_capacity_set = 2; // Set meter level
    save->magic_acquired = 1; // Required for meter to persist on save load
    save->magic_capacity = 1; // Required for meter to persist on save load
    save->magic_meter_size = 0x60; // Set meter size
    save->magic = 0x60; // Fill meter
}

void give_fairy_ocarina(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->items[Z64_SLOT_OCARINA] = 0x07;
}

void give_quest_item(z64_file_t* save, int16_t quest_bit, int16_t arg2) {
    save->quest_items |= 1 << quest_bit;
}

void ice_trap_effect(z64_file_t* save, int16_t arg1, int16_t arg2) {
    push_pending_ice_trap();
}

void give_bean_pack(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->items[Z64_SLOT_BEANS] = Z64_ITEM_BEANS;
    save->ammo[14] += 10; // 10 Magic Beans
}

void fill_wallet_upgrade(z64_file_t* save, int16_t arg1, int16_t arg2) {
    if(MAX_RUPEES)
        save->rupees = rupee_cap[arg1];
}

void clear_excess_hearts(z64_file_t* save, int16_t arg1, int16_t arg2) {
    if (save->energy_capacity >= 19 * 0x10)  // Giving a Heart Container at 19 hearts.
        save->heart_pieces = 0;
    save->refill_hearts = 20 * 0x10;
}

uint8_t OPEN_KAKARIKO = 0;
uint8_t COMPLETE_MASK_QUEST = 0;
void open_gate_and_mask_shop(z64_file_t* save, int16_t arg1, int16_t arg2) {
    // Check OPEN_KAKARIKO setting and open the gate
    if (OPEN_KAKARIKO) {
        save->inf_table[7] = save->inf_table[7] | 0x40; // "Spoke to Gate Guard About Mask Shop"
        if (!COMPLETE_MASK_QUEST) {
            save->item_get_inf[2] = save->item_get_inf[2] & 0xFB87; // Unset "Obtained Mask" flags just in case of savewarp before Impa.
        }
        // Check if we're in kak and actually open the gate
        if (z64_game.scene_index == 82) {
            // Loop through the actors looking for the gate
            z64_actor_t* curr = z64_game.actor_list[7].first;
            while (curr != NULL) {
                if (curr->actor_id == 0x100) { // Check for BG_GATE_SHUTTER
                    // Set the openingState so it starts to open
                    BgGateShutter* gate = (BgGateShutter*)curr;
                    gate->openingState = 2;
                    return;
                }
                curr = curr->next;
            }
        }
    }
    if (COMPLETE_MASK_QUEST) {
        save->inf_table[7] = save->inf_table[7] | 0x80; // "Soldier Wears Keaton Mask"
        save->item_get_inf[3] = save->item_get_inf[3] | 0x8F00; // "Sold Masks & Unlocked Masks" / "Obtained Mask of Truth"
        save->event_chk_inf[8] = save->event_chk_inf[8] | 0xF000; // "Paid Back Mask Fees"
    }
    // Set Zelda's Letter as collected in trade quest flags
    trade_quest_upgrade(save, arg1, arg2);
}

void give_bombchus(z64_file_t* save, int16_t arg1, int16_t arg2) {
    save->items[Z64_SLOT_BOMBCHU] = Z64_ITEM_BOMBCHU;
    save->ammo[8] += arg1;
}

void trade_quest_upgrade(z64_file_t* save, int16_t item_id, int16_t arg2) {
    SaveFile_SetTradeItemAsOwned(item_id);
}

void unlock_ocarina_note(z64_file_t* save, int16_t arg1, int16_t arg2) {
    switch(arg1) {
        case 0:
            save->scene_flags[0x50].unk_00_ |= 1 << 0; // Unused word in scene x50.
            break;
        case 1:
            save->scene_flags[0x50].unk_00_ |= 1 << 1;
            break;
        case 2:
            save->scene_flags[0x50].unk_00_ |= 1 << 2;
            break;
        case 3:
            save->scene_flags[0x50].unk_00_ |= 1 << 3;
            break;
        case 4:
            save->scene_flags[0x50].unk_00_ |= 1 << 4;
            break;
    }
}
