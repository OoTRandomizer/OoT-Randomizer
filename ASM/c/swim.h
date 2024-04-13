#ifndef SWIM_H
#define SWIM_H

#include "z64.h"
#include "save.h"

typedef struct {
    /* 0x00 */ z64_xyzf_t pos;
    /* 0x0C */ uint16_t yaw;
} SpecialRespawnInfo; // size = 0x10

typedef struct {
    int32_t scene_index;
    SpecialRespawnInfo respawnInfo;
} RespawnByScene;

void manage_swim();

#endif
