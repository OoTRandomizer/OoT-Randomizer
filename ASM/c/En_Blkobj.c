#include <stdint.h>
#include "z64.h"
#include "enemy_spawn_shuffle.h"

// Hack dark link room when it checks if dark link is still alive
// The function is normally checking if the return value of this is NULL so just return 1 if the soul flag isn't set.
z64_actor_t* En_Blkobj_Actor_Find_Hook(void* actorCtx, int32_t actorId, int32_t actorCategory)
{
    // Check for enemy soul shuffle
    if(CFG_ENEMY_SPAWN_SHUFFLE == CFG_ENEMY_SPAWN_SHUFFLE_STANDARD)
    {
        // In enemy soul shuffle, return 1 if we don't have the soul, or if we have the soul but it's not enabled.
        if(!flags_getsoul(SOUL_ID_DARK_LINK) || (flags_getsoul(SOUL_ID_DARK_LINK) && !get_soul_enabled(SOUL_ID_DARK_LINK)))
        {
            return 1;
        }
    }
    else if(CFG_ENEMY_SPAWN_SHUFFLE == CFG_ENEMY_SPAWN_SHUFFLE_REGIONAL) {
        if(!flags_getsoul(SOUL_ID_REGIONAL_WATER_TEMPLE))
        {
            return 1;
        }
    }
    return z64_ActorFind(actorCtx, actorId, actorCategory);
}
