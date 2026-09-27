#ifndef ENMD_H
#define ENMD_H

#include "z64.h"

struct EnMd;

typedef void (*EnMdActionFunc)(struct EnMd*, z64_game_t*);

typedef struct EnMd {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x013C */ SkelAnime skelanime;
    /* 0x0180 */ EnMdActionFunc actionFunc;
    /* 0x0184 */ ColliderCylinder collider;
    /* 0x01D0 */ NpcInteractInfo interactInfo;
    /* 0x01F8 */ uint8_t messageEntry; // tracks message state changes, like with `BOX_BREAK` or `TEXTID`
    /* 0x01F9 */ uint8_t messageState; // last known result of `Message_GetState`
    /* 0x01FA */ uint8_t animSequenceEntry; // each one changes animation info and waits
    /* 0x01FB */ uint8_t animSequence;
    /* 0x01FC */ int16_t blinkTimer;
    /* 0x01FE */ int16_t eyeTexIndex;
    /* 0x0200 */ int16_t alpha;
    /* 0x0202 */ int16_t waypoint;
    /* 0x0204 */ int16_t fidgetTableY[12];
    /* 0x0226 */ int16_t fidgetTableZ[12];
    /* 0x0248 */ z64_xyz_t jointTable[12];
    /* 0x02AE */ z64_xyz_t morphTable[12];
} EnMd; // size = 0x0314

#endif
