#include "z64.h"
#include "actor.h"
#include "get_items.h"

void en_skj_drop_collectible_hack(z64_actor_t* actor, z64_game_t* game) {
    xflag_t* flag = &(Actor_GetAdditionalData(actor)->flag);
    if(flag->all && !Get_NewFlag(flag))
    {
        drop_collectible_override_flag = *flag;
        EnItem00* spawned = z64_Item_DropCollectible(game, &actor->pos_world, 0);
        z64_bzero(&drop_collectible_override_flag, sizeof(drop_collectible_override_flag));
        return;
    }

    EnItem00* spawned = z64_Item_DropCollectible(game, &actor->pos_world, ITEM00_RUPEE_ORANGE);
}
