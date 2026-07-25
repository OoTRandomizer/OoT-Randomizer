#ifndef EN_BB_H
#define EN_BB_H

#include <stdint.h>
#include "z64.h"

typedef struct EnBb {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x013C */ char unk[0x1DC];
    /* 0x0318 */ uint8_t overridden;
    /* 0x0319 */ uint8_t spare;
} EnBb; // size = 0x0320 (increased in hacks.asm)

void bb_after_init_hack(z64_actor_t* this, z64_game_t* globalCtx);

#endif
