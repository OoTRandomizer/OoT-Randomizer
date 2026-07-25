#ifndef Z_BG_MORI_BIGST_H
#define Z_BG_MORI_BIGST_H

#include "z64.h"

struct BgMoriBigst;

typedef void (*BgMoriBigstActionFunc)(struct BgMoriBigst*, z64_game_t*);

typedef struct BgMoriBigst {
    /* 0x0000 */ DynaPolyActor dyna;
    /* 0x0154 */ BgMoriBigstActionFunc actionFunc;
    /* 0x0158 */ int16_t waitTimer;
    /* 0x015A */ int8_t moriTexObjectSlot;
    /* 0x015C */ z64_actor_t* child1;
    /* 0x0160 */ z64_actor_t* child2;
} BgMoriBigst; // size = 0x016C

#endif
