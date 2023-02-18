#ifndef Z_OBJ_KIBAKO2_H
#define Z_OBJ_KIBAKO2_H

#include "item_table.h"
#include "get_items.h"
#include "z64.h"

struct ObjKibako2;

typedef void (*ObjKibako2ActionFunc)(struct ObjKibako2 *, z64_game_t *);

typedef struct ObjKibako2 {
    /* 0x0000 */ DynaPolyActor dyna;
    /* 0x0154 */ uint8_t collider[0x4C];
    /* 0x01A0 */ void *actionFunc;
    /* 0x01A4 */ int16_t collectibleFlag;
    /* 0x01A8 */ uint8_t chest_type;
} ObjKibako2; // size = 0x01B8

override_t get_crate_override(z64_actor_t *actor, z64_game_t *game);

#endif
