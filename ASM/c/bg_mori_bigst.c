#include "z64.h"
#include "actor.h"

extern xflag_t* spawn_actor_with_flag;

z64_actor_t * BgMoriBigst_SpawnSingleStalfos(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params) {
    return Actor_SpawnAsChildWithSubflag(actorCtx, parent, globalCtx, actorId, posX, posY, posZ, rotX, rotY, rotZ, params, 1);
}
z64_actor_t * BgMoriBigst_SpawnStalfosPair1(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params) {
    return Actor_SpawnAsChildWithSubflag(actorCtx, parent, globalCtx, actorId, posX, posY, posZ, rotX, rotY, rotZ, params, 2);
}
z64_actor_t * BgMoriBigst_SpawnStalfosPair2(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params) {
    return Actor_SpawnAsChildWithSubflag(actorCtx, parent, globalCtx, actorId, posX, posY, posZ, rotX, rotY, rotZ, params, 3);
}
