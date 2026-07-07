#include "z64.h"

// For other parts of the struct, see decomp
typedef struct MapData {
    /* 0x00 */ char known_01[0x24];
    /* 0x24 */ uint16_t* owMinimapTexSize;
    /* 0x28 */ char known_02[0x48];
} MapData; // size = 0x70

extern MapData* gMapData;

// Load extended minimap of Gerudo Fortress if receive Gerudo Card there
void GerudoCard_ChangeMinimap() {
    z64_game_t* play = &z64_game;
    z64_link_t* player = &z64_link;

    if (play->scene_index == 0x5D) { // SCENE_GERUDOS_FORTRESS
        // Using GI object DMA variables
        // 0x00974600 address to ext minimap data, 0xC = mapIndex
        DmaMgr_RequestAsync(&player->giObjectDmaRequest, play->mapSegment, 0x00974600,
                gMapData->owMinimapTexSize[0xC], 0, &player->giObjectLoadQueue, NULL);
    }
}

// Switch minimap of Lake Hylia when changing water level
void LakeHylia_ChangeMinimap(z64_game_t* play) {
    z64_link_t* player = &z64_link;
    uintptr_t minimapAddress;

    if (z64_file.event_chk_inf[6] & 0x200) {    // water level flag
        minimapAddress = 0x0096A9F8;    // filled
    } else {
        minimapAddress = 0x00972F30;    // drained
    }

    DmaMgr_RequestAsync(&player->giObjectDmaRequest, play->mapSegment, minimapAddress,
       gMapData->owMinimapTexSize[6], 0, &player->giObjectLoadQueue, NULL);
}
