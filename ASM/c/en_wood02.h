#ifndef EN_WOOD02_H
#define EN_WOOD02_H

#include "actor.h"

#define EN_WOOD02 0x0077

typedef struct EnWood02 {
    /* 0x000 */ z64_actor_t actor;
    /* 0x13C */ uint8_t pad_13C[0x10];
    /* 0x14C */ int16_t drop_type;
    /* 0x14E */ uint8_t child_state[5];
    /* 0x153 */ uint8_t spawn_type;
    /* 0x154 */ uint8_t draw_type;
    /* 0x155 */ uint8_t pad_155[3];
    /* 0x158 */ uint8_t collider[0x4C];
    /* 0x1A4 */ uint8_t chest_type;
    /* 0x1A5 */ uint8_t pad_1A5[3];
    /* 0x1A8 */ void* original_update;
} EnWood02;

typedef char EnWood02SizeCheck[(sizeof(EnWood02) == 0x1AC) ? 1 : -1];

xflag_t EnWood02_NormalizeFlag(xflag_t flag);
void EnWood02_AfterInitHack(z64_actor_t* actor, z64_game_t* game);

#endif
