#include "z64.h"
#include "pots.h"
#include "item_table.h"
#include "get_items.h"
#include "obj_kibako.h"
#include "obj_kibako2.h"
#include "obj_comb.h"
#include "textures.h"
#include "actor.h"
#include "en_wonderitem.h"
#include "scene.h"
#include "en_item00.h"

extern uint8_t POTCRATE_TEXTURES_MATCH_CONTENTS;
extern uint16_t CURR_ACTOR_SPAWN_INDEX;
extern uint8_t SHUFFLE_SILVER_RUPEES;
extern int8_t curr_scene_setup;
extern xflag_t* spawn_actor_with_flag;

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
#define EN_WONDER_ITEM      0x0112  // Wonder Item

// Get a pointer to the additional data that is stored at the beginning of every actor
// This is calculated as the actor's address + the actor instance size from the overlay table.
ActorAdditionalData* Actor_GetAdditionalData(z64_actor_t* actor) {
    return (ActorAdditionalData*)(((uint8_t*)actor) - 0x10);
}

// Build an xflag from actor ID and subflag
// Store the flag using the pointer
void Actor_BuildFlag(z64_actor_t* actor, xflag_t* flag, uint16_t actor_index, uint8_t subflag) {
    flag->scene = z64_game.scene_index;
    if (z64_game.scene_index == 0x3E) {
        flag->grotto.room = actor->room_index;
        flag->grotto.grotto_id = z64_file.respawn[RESPAWN_MODE_RETURN].data & 0x1F;
        flag->grotto.flag = actor_index;
        flag->grotto.subflag = subflag;
    } else {
        flag->room = actor->room_index;
        flag->setup = curr_scene_setup;
        flag->flag = actor_index;
        flag->subflag = subflag;
    }
}

// Called from Actor_UpdateAll when spawning the actors in the scene's/room's actor list to store flags in the new space that we added to the actors.
// Prior to being called, CURR_ACTOR_SPAWN_INDEX is set to the current position in the actor spawn list.
void Actor_After_UpdateAll_Hack(z64_actor_t* actor, z64_game_t* game) {
    Actor_StoreFlagByIndex(actor, game, CURR_ACTOR_SPAWN_INDEX);
    Actor_StoreChestType(actor, game);

    // Add additional actor hacks here. These get called shortly after the call to actor_init
    // Hacks are responsible for checking that they are the correct actor.
    EnWonderitem_AfterInitHack(actor, game);
    CURR_ACTOR_SPAWN_INDEX = 0; // reset CURR_ACTOR_SPAWN_INDEX
}

// For pots/crates/beehives, store the flag in the new space in the actor instance.
// Flag consists of the room #, scene setup, and the actor index
void Actor_StoreFlag(z64_actor_t* actor, z64_game_t* game, xflag_t flag) {
    ActorAdditionalData* extra = Actor_GetAdditionalData(actor);
    flag = resolve_alternative_flag(&flag);
    if (CURR_ACTOR_SPAWN_INDEX) {
        extra->actor_id = CURR_ACTOR_SPAWN_INDEX;
    }
    override_t override = lookup_override_by_newflag(&flag);
    switch (actor->actor_id) {
        // For the following actors we store the flag in the new space added to the actor.
        case OBJ_TSUBO:
        case EN_TUBO_TRAP:
        case OBJ_KIBAKO:
        case OBJ_COMB:
        case OBJ_KIBAKO2:
        case EN_ITEM00:
        case EN_WONDER_ITEM:
        {
            // For these actors, only store the flag if there is a valid override
            if (override.key.all) {
                extra->flag = flag;
            }
            break;
        }
        case BG_SPOT18_BASKET:
        case OBJ_MURE3:
        case BG_HAKA_TUBO:
        {
            // For these actors which use subflags, always store the flag which serves as the base when calculating the subflag.
            // Don't really need to do this since we will recalculate the flag and check the override when spawning the subflags.
            extra->flag = flag;
        }
        default: {
            break;
        }
    }
}

// For pots/crates/beehives, store the flag in the new space in the actor instance.
// Flag consists of the room #, scene setup, and the actor index
void Actor_StoreFlagByIndex(z64_actor_t* actor, z64_game_t* game, uint16_t actor_index) {
    // Zeroize extra data;

    xflag_t flag = (xflag_t) { 0 };
    Actor_BuildFlag(actor, &flag, actor_index, 0);
    Actor_StoreFlag(actor, game, flag);
}

// Get an override for new flag. If the override doesn't exist, or flag has already been set, return 0.
override_t get_newflag_override(xflag_t* flag) {
    override_t override = lookup_override_by_newflag(flag);
    if (override.key.all != 0) {
        if (!Get_NewFlag(flag)) {
            return override;
        }
    }
    return (override_t) { 0 };
}

// For pots/crates/beehives match contents, determine the override and store the chest type in new space in the actor instance
// So we don't have to hit the override table every frame.
void Actor_StoreChestType(z64_actor_t* actor, z64_game_t* game) {
    uint8_t* pChestType = NULL;
    override_t override = { 0 };
    xflag_t* flag = &(Actor_GetAdditionalData(actor)->flag);
    if (actor->actor_id == OBJ_TSUBO) { // Pots
        override = get_newflag_override(flag);
        pChestType = &(((ObjTsubo*)actor)->chest_type);
    } else if (actor->actor_id == EN_TUBO_TRAP) { // Flying Pots
        override = get_newflag_override(flag);
        pChestType = &(((EnTuboTrap*)actor)->chest_type);
    } else if (actor->actor_id == OBJ_KIBAKO2) { // Large Crates
        override = get_newflag_override(flag);
        pChestType = &(((ObjKibako2*)actor)->chest_type);
    } else if (actor->actor_id == OBJ_KIBAKO) { // Small wooden crates
        override = get_newflag_override(flag);
        pChestType = &(((ObjKibako*)actor)->chest_type);
    } else if (actor->actor_id == OBJ_COMB) {
        override = get_newflag_override(flag);
        pChestType = &(((ObjComb*)actor)->chest_type);
    }
    if (override.key.all != 0 && pChestType != NULL) { // If we don't have an override key, then either this item doesn't have an override entry, or it has already been collected.
        if (POTCRATE_TEXTURES_MATCH_CONTENTS == PTMC_UNCHECKED && override.key.all > 0) { // For "unchecked" PTMC setting: Check if we have an override which means it wasn't collected.
            *pChestType = GILDED_CHEST;
        } else if (POTCRATE_TEXTURES_MATCH_CONTENTS == PTMC_CONTENTS) {
            uint16_t item_id = resolve_upgrades(override);
            item_row_t* row = get_item_row(override.value.looks_like_item_id);
            if (row == NULL) {
                row = get_item_row(override.value.base.item_id);
            }
            *pChestType = row->chest_type;
        } else {
            *pChestType = 0;
        }
    }
}

typedef void (*actor_after_spawn_func)(z64_actor_t* actor, bool overridden);

z64_actor_t* Actor_SpawnEntry_Hack(void* actorCtx, ActorEntry* actorEntry, z64_game_t* globalCtx) {
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
    z64_actor_t* spawned = NULL;
    if (continue_spawn) {
        spawned = z64_SpawnActor(actorCtx, globalCtx, actorEntry->id, actorEntry->pos.x, actorEntry->pos.y, actorEntry->pos.z,
            actorEntry->rot.x, actorEntry->rot.y, actorEntry->rot.z, actorEntry->params);
        if (spawned && after_spawn_func) {
            after_spawn_func(spawned, overridden);
        }
    }
    return spawned;
}

// Override silver rupee spawns.
bool spawn_override_silver_rupee(ActorEntry* actorEntry, z64_game_t* globalCtx, bool* overridden) {
    *overridden = false;
    if (SHUFFLE_SILVER_RUPEES) { // Check if silver rupee shuffle is enabled.
        xflag_t flag = {
            .scene = globalCtx->scene_index,
            .setup = curr_scene_setup,
            .room = globalCtx->room_index,
            .flag = CURR_ACTOR_SPAWN_INDEX,
            .subflag = 0,
        };

        flag = resolve_alternative_flag(&flag);
        uint8_t type = (actorEntry->params >> 0x0C) & 0xF;
        if (type != 1) { // only override actual silver rupees, not the switches or pots.
            return true;
        }
        override_t override = lookup_override_by_newflag(&flag);
        if (override.key.all != 0) {
            if (type == 1 && !Get_NewFlag(&flag)) {
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
void after_spawn_override_silver_rupee(z64_actor_t* spawned, bool overridden) {
    if (overridden) {
        EnItem00* this = (EnItem00*)spawned;
        this->is_silver_rupee = true;
        this->collider.info.bumper.dmgFlags = 0; // Remove clear the bumper collider flags so it doesn't interact w/ boomerang
    }
}

z64_actor_t* Player_SpawnEntry_Hack(void* actorCtx, ActorEntry* playerEntry, z64_game_t* globalCtx) {
    if (z64_file.entrance_index == 0x423) {
        playerEntry->pos.y = 1000;
        playerEntry->pos.z = -1960;
        playerEntry->rot.y = 0;
    }
    return z64_SpawnActor(actorCtx, globalCtx, playerEntry->id, playerEntry->pos.x, playerEntry->pos.y, playerEntry->pos.z,
        playerEntry->rot.x, playerEntry->rot.y, playerEntry->rot.z, playerEntry->params);
}

// This is our entrypoint back into Actor_Spawn. Call/return this to spawn the actor
extern z64_actor_t* Actor_Spawn_Continue(void* actorCtx, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params);

z64_actor_t* Actor_Spawn_Hook(void* actorCtx, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params) {
    bool continue_spawn = true;

    ActorEntry entry;
    entry.id = actorId;
    entry.params = params;
    entry.pos.x = (int16_t)posX;
    entry.pos.y = (int16_t)posY;
    entry.pos.z = (int16_t)posZ;
    entry.rot.x = rotX;
    entry.rot.y = rotY;
    entry.rot.z = rotZ;

    if (continue_spawn) {
        z64_actor_t* spawned = Actor_Spawn_Continue(actorCtx, globalCtx, actorId, posX, posY, posZ, rotX, rotY, rotZ, params);
        if (spawned) {
            if (spawn_actor_with_flag) {
                Actor_StoreFlag(spawned, globalCtx, *spawn_actor_with_flag);
                Actor_StoreChestType(spawned, globalCtx);
            }
        }
        return spawned;
    }
    return NULL;
}
