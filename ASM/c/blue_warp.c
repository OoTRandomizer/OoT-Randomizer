#include <stdbool.h>

#include "blue_warp.h"
#include "save.h"
#include "z64.h"

#define TEXT_STATE_CLOSING 2

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

// Routine taken from Majora's Mask blue warps
int32_t DoorWarp1_PlayerInRange_Overwrite(z64_actor_t* actor, z64_game_t* game) {
    // Check vanilla range
    if (DoorWarp1_PlayerInRange(actor, game)) {

        // Check if dungeon reward has already been collected
        if (extended_savectx.collected_dungeon_rewards[game->scene_index - 0x0011]) {
            return true;
        }

        // Null out blue warp parent if it is still the dungeon boss
        if (z64_ActorHasParent(actor, game) && (actor->parent != &z64_link.common)) {
            actor->parent = NULL;
        }

        // Link will attach as the parent actor once the GetItem is accepted. Until then, offer the dungeon reward for Link.
        if (!z64_ActorHasParent(actor, game)) {
            // Put a dummy item value on the blue warp, which will be overwritten by the medallions
            z64_ActorOfferGetItem(actor, game, 0x65, 60.0f, 20.0f);
            return false;
        }

        // Wait until Link closes the textbox displaying the getItem reward
        if (z64_MessageGetState(((uint8_t*)(&z64_game)) + 0x20D8) == TEXT_STATE_CLOSING) {
            if ((game->scene_index != 0x17) && (game->scene_index != 0x18)) {
                extended_savectx.collected_dungeon_rewards[game->scene_index - 0x0011] = true;
            }
            return true;
        }
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
