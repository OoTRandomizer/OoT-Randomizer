#include "objects.h"

#include "z64.h"

extern uint8_t FIX_BROKEN_DROPS;

#define OBJECT_EXCHANGE_BANK_MAX 19

int32_t object_index_or_spawn(z64_obj_ctxt_t *object_ctx, int16_t object_id)
{
    int32_t index = z64_ObjectIndex(object_ctx, object_id);
    if (index == -1 && object_ctx->n_objects < OBJECT_EXCHANGE_BANK_MAX)
    {
        // Track the number of spawned objects so the Object List
        // SceneCmd can clear out all subsequent objects and kill the
        // corresponding actors on room transition
        uint8_t n_spawned_objects = object_ctx->n_spawned_objects;
        index = z64_ObjectSpawn(object_ctx, object_id);
        object_ctx->n_spawned_objects = n_spawned_objects;
    }

    return index;
}

// Fix autocollect magic jar wonder items
void enitem00_set_link_incoming_item_id(z64_actor_t *actor, z64_game_t *game, int32_t incoming_item_id)
{
    EnItem00 *this = (EnItem00 *)actor;

    // Run z64_ActorSetLinkIncomingItemId regardless of FIX_BROKEN_DROPS
    if (!z64_ActorSetLinkIncomingItemId(&this->actor, game, incoming_item_id, 50.0f, 10.0f) && FIX_BROKEN_DROPS)
    {
        switch (incoming_item_id)
        {
            case 0x43: // GI_MAGIC_SMALL
                z64_GiveItem(game, Z64_ITEM_MAGIC_SMALL);
                break;
            case 0x44: // GI_MAGIC_LARGE
                z64_GiveItem(game, Z64_ITEM_MAGIC_LARGE);
                break;
        }
    }
}
