#include "z64.h"
#include "get_items.h"
#include "actor.h"

z64_actor_t* Obj_Mure3_RupeeCircle_DropRupee(z64_actor_t* this, z64_xyzf_t* pos, uint16_t params, uint32_t index) {
    xflag_t flag = { 0 };
    ActorAdditionalData* extras = Actor_GetAdditionalData(this);
    Actor_BuildFlag(this, &flag, extras->actor_id, index + 1);
    flag = resolve_alternative_flag(&flag);
    if (get_newflag_override(&flag).key.all) {
        drop_collectible_override_flag = flag;
        z64_actor_t* spawned = (z64_actor_t*)z64_Item_DropCollectible2(&z64_game, pos, params);
        z64_bzero(&drop_collectible_override_flag, sizeof(drop_collectible_override_flag));
        return spawned;
    }
    return (z64_actor_t*)z64_Item_DropCollectible2(&z64_game, pos, params);
}
