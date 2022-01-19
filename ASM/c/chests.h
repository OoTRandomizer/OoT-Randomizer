#ifndef CHESTS_H
#define CHESTS_H

#include "item_table.h"
#include "get_items.h"
#include "z64.h"

extern uint32_t CHEST_SIZE_MATCH_CONTENTS;
extern uint32_t CHEST_TEXTURE_MATCH_CONTENTS;

void get_chest_override(z64_actor_t *actor);

#endif
