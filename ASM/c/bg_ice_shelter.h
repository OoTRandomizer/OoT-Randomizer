#ifndef BG_ICE_SHELTER_H
#define BG_ICE_SHELTER_H

#include "z64.h"

struct BgIceShelter;

typedef void (*BgIceShelterActionFunc)(struct BgIceShelter*, z64_game_t*);

typedef struct BgIceShelter {
    /* 0x0000 */ DynaPolyActor dyna;
    /* 0x0164 */ BgIceShelterActionFunc actionFunc;
    /* 0x0168 */ ColliderCylinder cylinder1; // Used to detect blue fire and also as OC for no-dynapoly types
    /* 0x01B4 */ ColliderCylinder cylinder2; // Only used by no-dynapoly types to make weapons bounce off
    /* 0x0200 */ int16_t alpha;
} BgIceShelter; // size = 0x0204

#endif
