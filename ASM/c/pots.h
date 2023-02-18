#ifndef POTS_H
#define POTS_H

#include "item_table.h"
#include "get_items.h"
#include "z64.h"

// Regular Pot Struct
typedef struct ObjTsubo {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x013C */ void* actionFunc;
    /* 0x0140 */ uint8_t collider[0x4C];
    /* 0x018C */ int8_t objTsuboBankIndex;
    /* 0x0190 */ uint8_t chest_type;
} ObjTsubo; // size = 0x01A0

// Flying Pot Struct
typedef struct EnTuboTrap {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x013C */ void* actionFunc;
    /* 0x0140 */ float targetY;
    /* 0x0144 */ z64_xyzf_t originPos;
    /* 0x0150 */ uint8_t collider[0x4C];
    /* 0x019C */ uint8_t chest_type;
} EnTuboTrap; // size = 0x01AC

override_t get_pot_override(z64_actor_t *actor, z64_game_t *game);
override_t get_flying_pot_override(z64_actor_t *actor, z64_game_t *game);

#endif
