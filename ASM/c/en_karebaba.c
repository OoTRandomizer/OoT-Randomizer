#include "z64.h"
#include "util.h"
#include "actor.h"
#include "en_item00.h"

typedef void(*EnKarebaba_ActionFunc)(z64_actor_t* this, z64_game_t* globalCtx);

extern void* OVL_EnKarebaba_SetupDeadItemDrop;

// Hacked EnKarebaba item drop function to drop a collectible w/ enemy drop shuffle.
void EnKarebaba_SetupDeadItemDropHack(z64_actor_t* this, z64_game_t* globalCtx) {
    xflag_t* flag = &Actor_GetAdditionalData(this)->flag;
    if (flag->all && !Get_NewFlag(flag)) {
        drop_collectible_override_flag = *flag;
        EnItem00* spawned = Item_DropCollectible(globalCtx, &GET_PLAYER(globalCtx)->common.pos_world, 0);
        z64_bzero(&drop_collectible_override_flag, sizeof(drop_collectible_override_flag));
        z64_ActorKill(this);
        return;
    }
    EnKarebaba_ActionFunc EnKarebaba_SetupDeadItemDrop = resolve_overlay_addr(&OVL_EnKarebaba_SetupDeadItemDrop, this->actor_id);
    EnKarebaba_SetupDeadItemDrop(this, globalCtx);
}
