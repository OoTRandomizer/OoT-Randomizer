#ifndef ACTOR_H
#define ACTOR_H

#include "z64.h"
#include <stdbool.h>

void Actor_SetWorldToHome_End(z64_actor_t* actor);
void Actor_After_UpdateAll_Hack(z64_actor_t* actor, z64_game_t* game);
void Actor_StoreFlagInRotation(z64_actor_t* actor, z64_game_t* game, uint16_t actor_index);
void Actor_StoreChestType(z64_actor_t* actor, z64_game_t* game);
z64_actor_t* Actor_SpawnEntry_Hack(void* actorCtx, ActorEntry* actorEntry, z64_game_t* globalCtx);
bool spawn_override_silver_rupee(ActorEntry* actorEntry, z64_game_t* globalCtx, bool* overridden);
void after_spawn_override_silver_rupee(z64_actor_t* actor, bool overridden);
#endif
