#ifndef ACTOR_H
#define ACTOR_H

#include "z64.h"

void Actor_SetWorldToHome_End(z64_actor_t *actor);
void Actor_After_UpdateAll_Hack(z64_actor_t *actor, z64_game_t* game);
void Actor_StoreFlagInRotation(z64_actor_t* actor, z64_game_t* game, uint16_t actor_index);
void Actor_StoreChestType(z64_actor_t* actor, z64_game_t* game);

#endif
