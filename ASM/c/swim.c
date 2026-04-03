#include "swim.h"

RespawnByScene respawnsByScene[] = {
    { 0x1D9, { { -1455, -20, 1384 }, 28761 }},      // Hyrule Field to Zora River (in water)
    { 0x311, { { 5852, -20, 3725 }, -20025 }},      // Zora River to Hyrule Field (in water)
    { 0x4DA, { { 1978, -36, -855 }, -16384 }},      // Zora River to Lost Woods
    { 0x1DD, { { 4082, 860, -1018 }, -32768 }},     // Lost Woods to Zora River
    { 0x219, { { -3276, -1033, 2908 }, 11228 }},    // Gerudo Valley to Lake Hylia
    { 0x3D4,  { { -2361, 0, 610 }, 32768 }},        // Ice Cavern to Zora Fountain
    { 0x21D, { { -955, -1306, 6768 }, -32768 }},    // Water Temple to Lake Hylia
    { 0x328, { { -109, 11, -9 }, -29131 }},         // Lake Hylia to Zora Domain
    { 0x560, { { -912, -1326, 3391 }, 0 }},         // Zora Domain to Lake Hylia
    { 0x10E, { { -1500, 150, 1600 }, 32768}},       // Sapphire cutscene to Zora Fountain
    { 0x1A5, { { -224, -51, -117 }, 16384}},        // Caught by Gerudos as child
    { 0x199, { { 4129, 920, -1384 }, 49152}},       // Zora River from top of waterfall
    { 0x1FD, { { 0, 0, 1200 }, 0}},                 // Hyrule Field from Market
};

void set_new_respawn() {
    int32_t currentEntranceIndex = z64_game.entrance_index;
    for (uint8_t i = 0; i < 13; i++) {
        // Ensure we always respawn at a safe location.
        if (currentEntranceIndex == respawnsByScene[i].scene_index) {
            z64_Play_SetupRespawnPoint(&z64_game, 0x01, 0xDFF);
            z64_file.respawn[RESPAWN_MODE_RETURN].pos = respawnsByScene[i].respawnInfo.pos;
            z64_file.respawn[RESPAWN_MODE_RETURN].yaw = respawnsByScene[i].respawnInfo.yaw;
            z64_file.respawn_flag = 2;
            z64_game.scene_load_flag = 0x14;
            return;
        }
    }

    // Special case for Water Temple river area, so that player respawns at the start of the room.
    if (z64_game.scene_index == 5 && z64_game.room_index == 21) {
        z64_Play_SetupRespawnPoint(&z64_game, 0x01, 0xDFF);
        z64_xyzf_t riverPos = {-3063, 380, -4066};
        z64_file.respawn[RESPAWN_MODE_RETURN].pos = riverPos;
        z64_file.respawn[RESPAWN_MODE_RETURN].yaw = 9010;
        z64_file.respawn_flag = 2;
        z64_game.scene_load_flag = 0x14;
        return;
    }

    // Bottom of the Well respawn in the main room, mostly for advanced/no logic to avoid having to do the difficult glitch at the start if you fall into water.
    if (z64_game.scene_index == 8) {
        z64_Play_SetupRespawnPoint(&z64_game, 0x01, 0xDFF);
        z64_xyzf_t botwPos = { 0, -12, 117 };
        z64_file.respawn[RESPAWN_MODE_RETURN].pos = botwPos;
        z64_file.respawn[RESPAWN_MODE_RETURN].yaw = 32768;
        z64_file.respawn_flag = 2;
        z64_game.scene_load_flag = 0x14;
        return;
    }

    // Zoras river near waterfall, to have mercy if jumping for the rupees as adult.
    if (z64_game.scene_index == 84 && z64_link.common.pos_world.x > 3800) {
        z64_Play_SetupRespawnPoint(&z64_game, 0x01, 0xDFF);
        z64_xyzf_t riverPos = { 4129, 920, -1384 };
        z64_file.respawn[RESPAWN_MODE_RETURN].pos = riverPos;
        z64_file.respawn[RESPAWN_MODE_RETURN].yaw = 49152;
        z64_file.respawn_flag = 2;
        z64_game.scene_load_flag = 0x14;
        return;
    }

    // Normal case, just respawn at the last entrance.
    z64_game.entrance_index = z64_file.entrance_index;
    z64_game.fadeout_transition = 0x02;
    z64_file.respawn_flag = -2;
    z64_game.scene_load_flag = 0x14;
}

void manage_swim() {
    // We found the first scale.
    if (extended_savectx.extended_scale > 0) {
        return;
    }

    // Iron boots are equipped.
    if (z64_file.equip_boots == 2) {
        return;
    }

    // Always allow to swim out of water temple to avoid softlocks.
    if (z64_game.scene_index == 5 &&
        z64_game.room_index == 0 &&
        z64_link.common.pos_world.z > 700.0) {
        return;
    }

    if (z64_link.state_flags_1 & 0x08000000) { // Swimming state flag.
        PlaySFX(0x28CD); // NA_SE_EV_WATER_CONVECTION
        set_new_respawn();
    }
}
