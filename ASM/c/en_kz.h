#ifndef ENKZ_H
#define ENKZ_H

#include "z64.h"

struct EnKz;

typedef void (*EnKzActionFunc)(struct EnKz*, z64_game_t*);

typedef struct EnKz {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x013C */ uint8_t skelanime[0x44];
    /* 0x0180 */ EnKzActionFunc actionFunc;  
    /* 0x0184 */ ColliderCylinder collider;
    /* 0x01D0 */ NpcInteractInfo interactInfo;
    /* 0x01F8 */ uint8_t sfxPlayed;
    /* 0x01F9 */ uint8_t isTrading;
    /* 0x01FA */ int16_t waypoint;
    /* 0x01FC */ int16_t blinkTimer;
    /* 0x01FE */ char unk_20E[2];
    /* 0x0200 */ int16_t eyeIdx;
    /* 0x0202 */ int16_t subCamId;
    /* 0x0204 */ int16_t returnToCamId;
    /* 0x0206 */ z64_xyz_t jointTable[12];
    /* 0x024E */ z64_xyz_t morphTable[12];
    /* 0x0296 */ int16_t fidgetTableY[12];
    /* 0x02AE */ int16_t fidgetTableZ[12];
} EnKz; // size = 0x02C8

#endif
