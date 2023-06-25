#include "z64.h"
#include "pots.h"
#include "item_table.h"
#include "get_items.h"
#include "obj_kibako.h"
#include "obj_kibako2.h"
#include "obj_comb.h"
#include "textures.h"
#include "actor.h"

extern uint8_t POTCRATE_TEXTURES_MATCH_CONTENTS;
extern uint16_t CURR_ACTOR_SPAWN_INDEX;
extern uint8_t SHUFFLE_SILVER_RUPEES;
extern int8_t curr_scene_setup;

#define BG_HAKA_TUBO        0x00BB  // Shadow temple spinning pot
#define BG_SPOT18_BASKET    0x015C  // Goron city spinning pot
#define OBJ_COMB            0x19E   // Beehive
#define OBJ_MURE3           0x1AB   // Rupee towers/circles
#define OBJ_TSUBO           0x0111  // Pot
#define EN_ITEM00           0x0015  // Collectible item
#define EN_TUBO_TRAP        0x11D   // Flying Pot
#define OBJ_KIBAKO          0x110   // Small Crate
#define OBJ_KIBAKO2         0x1A0   // Large Crate
#define EN_G_SWITCH         0x0117 //Silver Rupee

// Called at the end of Actor_SetWorldToHome
// Reset the rotations for any actors that we may have passed data in through Actor_Spawn
void Actor_SetWorldToHome_End(z64_actor_t *actor) {
    switch (actor->actor_id) {
        case BG_HAKA_TUBO:
        case BG_SPOT18_BASKET:
        case OBJ_MURE3:
        case OBJ_COMB: {
            actor->rot_world.z = 0;
            break;
        }
        case EN_ITEM00: {
            actor->rot_world.y = 0;
        }
        default: {
            break;
        }
    }
}

// Called from Actor_UpdateAll when spawning the actors in the scene's/room's actor list.
// For Pots/Crates/Beehives, sets the actors spawn index into unused y/z rotation fields
// This works because this hack occurs after the actor has been spawned and Actor_SetWorldToHome has been called
// Otherwise the actor would be rotated :)
// Now that we resized pots/crates/beehives we could probably just store this info in new space in the actor. But this works for now.
// Prior to being called, CURR_ACTOR_SPAWN_INDEX is set to the current position in the actor spawn list.
void Actor_After_UpdateAll_Hack(z64_actor_t *actor, z64_game_t *game) {
    Actor_StoreFlagInRotation(actor, game, CURR_ACTOR_SPAWN_INDEX);
    Actor_StoreChestType(actor, game);

    CURR_ACTOR_SPAWN_INDEX = 0; // reset CURR_ACTOR_SPAWN_INDEX
}

// For pots/crates/beehives, store the flag in the actor's unused initial rotation fields
// Flag consists of the room # and the actor index
void Actor_StoreFlagInRotation(z64_actor_t *actor, z64_game_t *game, uint16_t actor_index) {
    uint16_t flag = actor_index | (actor->room_index << 8); // Calculate the flag
    switch (actor->actor_id) {
        // For the following actors we store the flag in the z rotation
        case OBJ_TSUBO:
        case EN_TUBO_TRAP:
        case OBJ_KIBAKO:
        case OBJ_COMB: {
            actor->rot_init.z = flag;
            break;
        }
        // For the following actors we store the flag in the y rotation
        case OBJ_KIBAKO2: {
            actor->rot_init.y = flag;
            break;
        }
        default: {
            break;
        }
    }
}

// For pots/crates/beehives, determine the override and store the chest type in new space in the actor instance
// So we don't have to hit the override table every frame.
void Actor_StoreChestType(z64_actor_t* actor, z64_game_t* game) {
    uint8_t* pChestType = NULL;
    override_t override = { 0 };

    if (actor->actor_id == OBJ_TSUBO) { // Pots
        override = get_pot_override(actor, game);
        pChestType = &(((ObjTsubo *)actor)->chest_type);
    } else if (actor->actor_id == EN_TUBO_TRAP) { // Flying Pots
        override = get_flying_pot_override(actor, game);
        pChestType = &(((EnTuboTrap *)actor)->chest_type);
    } else if (actor->actor_id == OBJ_KIBAKO2) { // Large Crates
        override = get_crate_override(actor, game);
        pChestType = &(((ObjKibako2 *)actor)->chest_type);
    } else if (actor->actor_id == OBJ_KIBAKO) { // Small wooden crates
        override = get_smallcrate_override(actor, game);
        pChestType = &(((ObjKibako *)actor)->chest_type);
    } else if (actor->actor_id == OBJ_COMB) {
        override = get_beehive_override(actor, game);
        pChestType = &(((ObjComb *)actor)->chest_type);
    }
    if (override.key.all != 0 && pChestType != NULL) { // If we don't have an override key, then either this item doesn't have an override entry, or it has already been collected.
        if (POTCRATE_TEXTURES_MATCH_CONTENTS == PTMC_UNCHECKED && override.key.all > 0) { // For "unchecked" PTMC setting: Check if we have an override which means it wasn't collected.
            *pChestType = GILDED_CHEST;
        } else if(POTCRATE_TEXTURES_MATCH_CONTENTS == PTMC_CONTENTS) {
            uint16_t item_id = resolve_upgrades(override);
            item_row_t *row = get_item_row(override.value.looks_like_item_id);
            if (row == NULL) {
                row = get_item_row(override.value.base.item_id);
            }
            *pChestType = row->chest_type;
        } else {
            *pChestType = 0;
        }
    }
}

typedef void(*actor_after_spawn_func)(z64_actor_t* actor, bool overridden);

z64_actor_t *Actor_SpawnEntry_Hack(void *actorCtx, ActorEntry *actorEntry, z64_game_t *globalCtx) {
    bool continue_spawn = true;
    bool overridden = false;
    actor_after_spawn_func after_spawn_func = NULL;
    switch (actorEntry->id) {
        case EN_G_SWITCH: {
            continue_spawn = spawn_override_silver_rupee(actorEntry, globalCtx, &overridden);
            after_spawn_func = after_spawn_override_silver_rupee;
            break;
        }
        default: {
            break;
        }
    }
    z64_actor_t *spawned = NULL;
    if (continue_spawn) {
        spawned = z64_SpawnActor(actorCtx, globalCtx, actorEntry->id, actorEntry->pos.x, actorEntry->pos.y, actorEntry->pos.z,
            actorEntry->rot.x, actorEntry->rot.y, actorEntry->rot.z, actorEntry->params);
        if(spawned && after_spawn_func) {
            after_spawn_func(spawned, overridden);
        }
    }
    return spawned;
}

// Override silver rupee spawns.
bool spawn_override_silver_rupee(ActorEntry *actorEntry, z64_game_t *globalCtx, bool* overridden) {
    *overridden = false;
    if (SHUFFLE_SILVER_RUPEES) { // Check if silver rupee shuffle is enabled.
        // Build a dummy enitem00 actor
        EnItem00 dummy;
        dummy.actor.actor_id = 0x15;
        dummy.actor.rot_init.y = (globalCtx->room_index << 8) + CURR_ACTOR_SPAWN_INDEX;
        dummy.actor.variable = 0;
        uint8_t type = (actorEntry->params >> 0x0C) & 0xF;
        if (type != 1) { // only override actual silver rupees, not the switches or pots.
            return true;
        }
        override_t override = lookup_override(&(dummy.actor), globalCtx->scene_index, 0);
        if (override.key.all != 0) {
            dummy.override = override;
            if (type == 1 && !Get_CollectibleOverrideFlag(&dummy)) {
                // Spawn a green rupee which will be overridden using the collectible hacks.
                actorEntry->params = 0;
                actorEntry->id = EN_ITEM00;
                *overridden = true;
                return true;
            }
        }
        return false;
    }
    return true;
}

// After silver rupee spawns as enitem00
void after_spawn_override_silver_rupee(z64_actor_t* spawned, bool overridden)
{
    if(overridden) {
        EnItem00* this = (EnItem00*)spawned;
        this->is_silver_rupee = true;
        this->collider.info.bumper.dmgFlags = 0; //Remove clear the bumper collider flags so it doesn't interact w/ boomerang
    }
}

z64_actor_t *Player_SpawnEntry_Hack(void *actorCtx, ActorEntry *playerEntry, z64_game_t *globalCtx) {
    if (z64_file.entrance_index == 0x423) {
        playerEntry->pos.y = 1000;
        playerEntry->pos.z = -1960;
        playerEntry->rot.y = 0;
    }
    return z64_SpawnActor(actorCtx, globalCtx, playerEntry->id, playerEntry->pos.x, playerEntry->pos.y, playerEntry->pos.z,
        playerEntry->rot.x, playerEntry->rot.y, playerEntry->rot.z, playerEntry->params);
}
