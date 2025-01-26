#include "z64.h"
#include "actor.h"
#include "bg_mori_bigst.h"
#include "util.h"

extern xflag_t* spawn_actor_with_flag;
extern BgMoriBigstActionFunc OVL_BgMoriBigst_SetupFall;
extern BgMoriBigstActionFunc OVL_BgMoriBigst_SetupDone;
extern int16_t OnePointCutscene_Init(z64_game_t* play, int16_t csId, int16_t timer, z64_actor_t* actor, int16_t parentCamId);
extern Player_InCsMode(z64_game_t* globalCtx);

extern bool curr_room_enemies_inhibited;

z64_actor_t * BgMoriBigst_SpawnSingleStalfos(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params) {
    z64_actor_t* spawned = Actor_SpawnAsChildWithSubflag(actorCtx, parent, globalCtx, actorId, posX, posY, posZ, rotX, rotY, rotZ, params, 1);
    ((BgMoriBigst*)(parent))->child1 = spawned;
    return spawned;
}
z64_actor_t * BgMoriBigst_SpawnStalfosPair1(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params) {
    z64_actor_t* spawned = Actor_SpawnAsChildWithSubflag(actorCtx, parent, globalCtx, actorId, posX, posY, posZ, rotX, rotY, rotZ, params, 2);
    ((BgMoriBigst*)(parent))->child1 = spawned;
    return spawned;
}
z64_actor_t * BgMoriBigst_SpawnStalfosPair2(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params) {
    z64_actor_t* spawned = Actor_SpawnAsChildWithSubflag(actorCtx, parent, globalCtx, actorId, posX, posY, posZ, rotX, rotY, rotZ, params, 3);
    ((BgMoriBigst*)(parent))->child2 = spawned;
    return spawned;
}

void BgMoriBigst_StalfosFight_new(BgMoriBigst* this, z64_game_t* globalCtx) {
    z64_link_t* player = GET_PLAYER(globalCtx);

    if ((!curr_room_enemies_inhibited && !this->child1) &&
        ((this->dyna.actor.pos_init.y - 5.0f) <= GET_PLAYER(globalCtx)->common.pos_world.y)) {
        BgMoriBigstActionFunc BgMoriBigst_SetupFall = (BgMoriBigstActionFunc)resolve_overlay_addr(&OVL_BgMoriBigst_SetupFall, this->dyna.actor.actor_id);
        BgMoriBigst_SetupFall(this, globalCtx);
        OnePointCutscene_Init(globalCtx, 3220, 72, &this->dyna.actor, 0);
    }
}

void BgMoriBigst_StalfosPairFight_new(BgMoriBigst* this, z64_game_t* globalCtx) {
    if ((!curr_room_enemies_inhibited && !this->child1 && !this->child2) && !Player_InCsMode(globalCtx)) {
        Flags_SetSwitch(globalCtx, PARAMS_GET_U(this->dyna.actor.variable, 8, 6));
        BgMoriBigstActionFunc BgMoriBigst_SetupDone = (BgMoriBigstActionFunc)resolve_overlay_addr(&OVL_BgMoriBigst_SetupDone, this->dyna.actor.actor_id);
        BgMoriBigst_SetupDone(this, globalCtx);
    }
}