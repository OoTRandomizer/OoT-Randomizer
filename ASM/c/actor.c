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

#define BG_HAKA_TUBO        0x00BB  // Shadow temple spinning pot
#define BG_SPOT18_BASKET    0x015C  // Goron city spinning pot
#define OBJ_COMB            0x19E   // Beehive
#define OBJ_MURE3           0x1AB   // Rupee towers/circles
#define OBJ_TSUBO           0x0111  // Pot
#define EN_ITEM00           0x0015  // Collectible item
#define EN_TUBO_TRAP        0x11D   // Flying Pot
#define OBJ_KIBAKO          0x110   // Small Crate
#define OBJ_KIBAKO2         0x1A0   // Large Crate

// Called at the end of Actor_SetWorldToHome
// Reset the rotations for any actors that we may have passed data in through Actor_Spawn
void Actor_SetWorldToHome_End(z64_actor_t *actor) {
   switch(actor->actor_id){
        case BG_HAKA_TUBO:
        case BG_SPOT18_BASKET:
        case OBJ_MURE3:
        case OBJ_COMB:
            actor->rot_world.z = 0;
            break;
        case EN_ITEM00:
            actor->rot_world.y = 0;
        default:
            break;
    }
}

// Called from Actor_UpdateAll when spawning the actors in the scene's/room's actor list.
// For Pots/Crates/Beehives, sets the actors spawn index into unused y/z rotation fields
// This works because this hack occurs after the actor has been spawned and Actor_SetWorldToHome has been called
// Otherwise the actor would be rotated :)
// Now that we resized pots/crates/beehives we could probably just store this info in new space in the actor. But this works for now.
// Prior to being called, CURR_ACTOR_SPAWN_INDEX is set to the current position in the actor spawn list.
void Actor_After_UpdateAll_Hack(z64_actor_t *actor, z64_game_t* game) {

    Actor_StoreFlagInRotation(actor, game, CURR_ACTOR_SPAWN_INDEX);
    Actor_StoreChestType(actor, game);

    CURR_ACTOR_SPAWN_INDEX = 0; //reset CURR_ACTOR_SPAWN_INDEX
}

// For pots/crates/beehives, store the flag in the actor's unused initial rotation fields
// Flag consists of the room # and the actor index
void Actor_StoreFlagInRotation(z64_actor_t* actor, z64_game_t* game, uint16_t actor_index) {
    uint16_t flag = (actor_index) | (actor->room_index << 8); // Calculate the flag
    switch(actor->actor_id)
    {
        // For the following actors we store the flag in the z rotation
        case OBJ_TSUBO:
        case EN_TUBO_TRAP:
        case OBJ_KIBAKO:
        case OBJ_COMB:
        {
            actor->rot_init.z = flag;
            break;
        }
        // For the following actors we store the flag in the y rotation
        case OBJ_KIBAKO2:
        {
            actor->rot_init.y = flag;
            break;
        }
        default:
        {
            break;
        }
    }
}

// For pots/crates/beehives, determine the override and store the chest type in new space in the actor instance
// So we don't have to hit the override table every frame.
void Actor_StoreChestType(z64_actor_t* actor, z64_game_t* game) {
    uint8_t* pChestType = NULL;
    override_t override;
    override.key.all = 0;
    override.value.all = 0;

    if(actor->actor_id == OBJ_TSUBO) //Pots
    {
        override = get_pot_override(actor, game);
        pChestType = &(((ObjTsubo*)actor)->chest_type);
    }
    else if(actor->actor_id == EN_TUBO_TRAP) // Flying Pots
    {
        override = get_flying_pot_override(actor, game);
        pChestType = &(((EnTuboTrap*)actor)->chest_type);
    }
    else if(actor->actor_id == OBJ_KIBAKO2) // Large Crates
    {
        override = get_crate_override(actor, game);
        pChestType = &(((ObjKibako2*)actor)->chest_type);
    }
    else if(actor->actor_id == OBJ_KIBAKO) // Small wooden crates
    {
        override = get_smallcrate_override(actor, game);
        pChestType = &(((ObjKibako*)actor)->chest_type);
    }
    else if(actor->actor_id == OBJ_COMB)
    {
        override = get_beehive_override(actor, game);
        pChestType = &(((ObjComb*)actor)->chest_type);
    }
    if(override.key.all != 0 && pChestType != NULL) // If we don't have an override key, then either this item doesn't have an override entry, or it has already been collected.
    {
        if(POTCRATE_TEXTURES_MATCH_CONTENTS == PTMC_UNCHECKED && override.key.all > 0) // For "unchecked" PTMC setting: Check if we have an override which means it wasn't collected.
        {
            *pChestType = GILDED_CHEST;
        }
        else if(POTCRATE_TEXTURES_MATCH_CONTENTS == PTMC_CONTENTS)
        {
            uint16_t item_id = resolve_upgrades(override.value.item_id);
            item_row_t *row = get_item_row(override.value.looks_like_item_id);
            if (row == NULL) {
                row = get_item_row(override.value.item_id);
            }
            *pChestType = row->chest_type;
        }
        else
        {
            *pChestType = 0;
        }

    }
}
