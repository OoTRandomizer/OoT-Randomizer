#include "z64.h"
#include "actor.h"

z64_actor_t * EnAnubiceTag_SpawnChild(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params) {
    return Actor_SpawnAsChildWithSubflag(actorCtx, parent, globalCtx, actorId, posX, posY, posZ, rotX, rotY, rotZ, params, 0);
}