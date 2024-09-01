#include <stdbool.h>

#include "blue_warp.h"
#include "item_table.h"
#include "save.h"
#include "z64.h"

#define TEXT_STATE_CLOSING 2

extern uint8_t PLAYER_ID;
extern uint8_t PLAYER_NAME_ID;
extern bool REWARDS_AS_ITEMS;

// Original function copied over
int32_t DoorWarp1_PlayerInRange(z64_actor_t* actor, z64_game_t* game) {
    if (actor->xzdist_from_link < 60.0f) {
        if ((z64_link.common.pos_world.y - 20.0f) < actor->pos_world.y) {
            if (actor->pos_world.y < (z64_link.common.pos_world.y + 20.0f)) {
                return true;
            }
        }
    }
    return false;
};

int32_t DoorWarp1_PlayerInRange_Overwrite(z64_actor_t* actor, z64_game_t* game) {
    // Check vanilla range
    if (DoorWarp1_PlayerInRange(actor, game)) {
        uint8_t boss_idx = game->scene_index - 0x0011;
        // queue the item if not already collected
        if (!extended_savectx.collected_dungeon_rewards[boss_idx]) {
            if (REWARDS_AS_ITEMS) {
                push_delayed_item(0x05 + boss_idx);
            } else {
                override_key_t override_key = { .scene = 0xFF, .type = OVR_DELAYED, .flag = 0x05 + boss_idx };
                override_t override = lookup_override_by_key(override_key);
                uint16_t resolved_item_id = resolve_upgrades(override);
                item_row_t* item_row = get_item_row(resolved_item_id);
                call_effect_function(item_row);
                PLAYER_NAME_ID = override.value.base.player;
                z64_DisplayTextbox(&z64_game, resolve_item_text_id(item_row, PLAYER_NAME_ID != PLAYER_ID), 0);
            }
            extended_savectx.collected_dungeon_rewards[boss_idx] = true;
        }
        // immediately activate the blue warp. Queued item will be given after the warp
        return true;
    }
    return false;
}

int32_t DoorWarp1_IsSpiritRewardObtained(void) {
    return extended_savectx.collected_dungeon_rewards[6];
}

int32_t DoorWarp1_IsShadowRewardObtained(void) {
    return extended_savectx.collected_dungeon_rewards[7];
}

void DoorWarp1_KokiriEmerald_Overwrite(void) {
    z64_file.skybox_time = z64_file.day_time = 0x8000; // CLOCK_TIME(12, 00)
}

void DoorWarp1_GoronRuby_Overwrite(void) {
    z64_file.skybox_time = z64_file.day_time = 0x8000; // CLOCK_TIME(12, 00)
}

void DoorWarp1_ZoraSapphire_Overwrite(void) {
    z64_file.skybox_time = z64_file.day_time = 0x8000; // CLOCK_TIME(12, 00)
}

void DoorWarp1_ForestMedallion_Overwrite(void) {
    z64_file.skybox_time = z64_file.day_time = 0x8000; // CLOCK_TIME(12, 00)
}

void DoorWarp1_FireMedallion_Overwrite(void) {
    z64_file.skybox_time = z64_file.day_time = 0x8000; // CLOCK_TIME(12, 00)
    z64_file.event_chk_inf[2] |= 1 << 15; // DMT cloud circle no longer fire
    z64_file.timer_1_state = 0; // reset heat timer
}

void DoorWarp1_WaterMedallion_Overwrite(void) {
    z64_file.skybox_time = z64_file.day_time = 0x4800; // CLOCK_TIME(6, 45)
    z64_file.event_chk_inf[6] |= 1 << 9; // Lake Hylia water raised
}

void DoorWarp1_SpiritMedallion_Overwrite(void) {
    extended_savectx.collected_dungeon_rewards[6] = true;
    z64_file.skybox_time = z64_file.day_time = 0x8000; // CLOCK_TIME(12, 00)
}

void DoorWarp1_ShadowMedallion_Overwrite(void) {
    extended_savectx.collected_dungeon_rewards[7] = true;
    z64_file.skybox_time = z64_file.day_time = 0x8000; // CLOCK_TIME(12, 00)
}
