#include "grotto.h"
#include "entrance_table.h"

GrottoTableEntry gGrottoTable[GROTTO_TABLE_SIZE];

void SetGrottoSceneLayer() {
    for (uint8_t i = 0; i < GROTTO_TABLE_SIZE; i++) {
        if (gGrottoTable[i].entranceIndex == z64_file.entrance_index) {
            z64_file.scene_setup_index = gGrottoTable[i].sceneLayer;
            CURRENT_GROTTO_ID = i;
        }
    }
}

void SetGrottoEntranceIndex(DoorAna* this, z64_game_t* play) {
    int16_t exit_index = this->actor.rot_init.z;
    play->entrance_index = play->scene_exit_list[exit_index];
}

void Play_SetupRespawnPoint(z64_game_t* this, int32_t respawnMode, int32_t playerParams) {
    z64_link_t* player = GET_PLAYER(this);
    int32_t entranceIndex;
    int8_t roomIndex;

    if (PLAYER_GET_START_MODE(player) == PLAYER_START_MODE_GROTTO) {
        playerParams = PLAYER_START_MODE_GROTTO;
    }

    roomIndex = this->room_index;
    entranceIndex = z64_file.entrance_index;
    z64_Play_SetRespawnData(this, respawnMode, entranceIndex, roomIndex, playerParams, &player->common.pos_world,
                        player->common.rot_2.y);
}

void OverrideRespawnPlayerParams(z64_link_t* thisx) {
    int32_t startMode;
    if (PLAYER_GET_START_MODE(thisx) == PLAYER_START_MODE_GROTTO) {
        startMode = PLAYER_START_MODE_GROTTO;
    } else {
        startMode = PLAYER_START_MODE_IDLE;
    }
    z64_file.respawn[RESPAWN_MODE_DOWN].playerParams = PLAYER_PARAMS(startMode, PLAYER_GET_START_BG_CAM_INDEX(thisx));
}

void Play_TriggerRespawn(z64_game_t* this) {
    int32_t startMode;
    z64_link_t* player = GET_PLAYER(this);
    if (PLAYER_GET_START_MODE(player) == PLAYER_START_MODE_GROTTO) {
        startMode = PLAYER_START_MODE_GROTTO;
    } else {
        startMode = PLAYER_START_MODE_IDLE;
    }
    Play_SetupRespawnPoint(this, RESPAWN_MODE_DOWN, PLAYER_PARAMS(startMode, PLAYER_START_BG_CAM_DEFAULT));
    z64_Play_LoadToLastEntrance(this);
}
