#ifndef OBJ_KIBAKO_H
#define OBJ_KIBAKO_H

#include "z64.h"

typedef struct ObjKibako {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x013C */ void* actionFunc;
    /* 0x0140 */ uint8_t collider[0x4C];
    /* 0x018C */ uint8_t chest_type;
} ObjKibako; // size = 0x019C

override_t get_smallcrate_override(z64_actor_t *actor, z64_game_t *game);

#endif
