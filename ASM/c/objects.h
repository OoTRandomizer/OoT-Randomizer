#ifndef OBJECTS_H
#define OBJECTS_H

#include "z64.h"

int32_t object_index_or_spawn(z64_obj_ctxt_t *object_ctx, int16_t object_id);
void enitem00_set_link_incoming_item_id(z64_actor_t *actor, z64_game_t *game, int32_t getItemId);

#endif
