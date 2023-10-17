#ifndef ARROW_CYCLE_H
#define ARROW_CYCLE_H

#include "z64.h"
#include <stdio.h>

/* Functions */
#define z64_playsfx	((playsfx_t) 0x800C806C)

z64_actor_t* arrow_cycle_find_arrow(z64_link_t* player, z64_game_t* ctxt);
int8_t arrow_cycle_get_magic_cost(uint8_t index);
void handle_arrow_cycle(z64_link_t* player, z64_game_t* ctxt);
z64_actor_init_t* reloc_resolve_actor_init(z64_actor_ovl_t* ovl);
uint8_t actor_helper_does_actor_exist(const z64_actor_t* target, const z64_game_t* ctxt, uint8_t actorCategory);

#endif