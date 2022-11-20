#include "z64.h"
#include "en_item00.h"
#include "pots.h"
#include "item_table.h"
#include "get_items.h"
#include "obj_kibako.h"
#include "obj_kibako2.h"
#include "obj_comb.h"
#include "textures.h"

extern uint8_t POTCRATE_TEXTURES_MATCH_CONTENTS;

#define BG_HAKA_TUBO        0x00BB
#define BG_SPOT18_BASKET    0x015C
#define OBJ_COMB            0x19E   // Beehive
#define OBJ_MURE3           0x1AB
#define OBJ_TSUBO           0x0111  // Pot
#define EN_ITEM00           0x0015  // Collectible item
#define EN_TUBO_TRAP        0x11D   // Flying Pot
#define OBJ_KIBAKO          0x110   // Small Crate
#define OBJ_KIBAKO2         0x1A0   // Large Crate

void Actor_SetWorldToHome_End(z64_actor_t *actor) {
    // Reset rotations to 0 for any actors that it gets passed into the spawn params
    // bg_haka_tubo          0xBB
    // bg_spot18_basket      0x15C
    // obj_mure3             0x1AB
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

void Actor_After_UpdateAll_Hack(z64_actor_t *actor, z64_game_t* game) {
    if(actor->actor_id == EN_ITEM00) //Collectibles
    {
        EnItem00_Init_Hack((EnItem00*)actor, game);
    }
    uint8_t* p;
    override_t override;
    override.key.all = 0;
    override.value.all = 0;
    if(actor->actor_id == OBJ_TSUBO) //Pots
    {
        override = get_pot_override(actor, game);    
        p = &(((ObjTsubo*)actor)->chest_type);
    }
    else if(actor->actor_id == EN_TUBO_TRAP) // Flying Pots
    {
        override = get_flying_pot_override(actor, game);
        p = &(((EnTuboTrap*)actor)->chest_type);
    }
    else if(actor->actor_id == OBJ_KIBAKO2) // Large Crates
    {
        override = get_crate_override(actor, game);
        p = &(((ObjKibako2*)actor)->chest_type);
    }
    else if(actor->actor_id == OBJ_KIBAKO) // Small wooden crates
    {
        override = get_smallcrate_override(actor, game);
        p = &(((ObjKibako*)actor)->chest_type);
    }
    else if(actor->actor_id == OBJ_COMB)
    {
        override = get_beehive_override(actor, game);
        p = &(((ObjComb*)actor)->chest_type);
    }
    if(override.key.all != 0)
    {
        if(POTCRATE_TEXTURES_MATCH_CONTENTS == PTMC_UNCHECKED && override.key.all > 0)
        {
            *p = GILDED_CHEST;
        }
        else if(POTCRATE_TEXTURES_MATCH_CONTENTS == PTMC_CONTENTS)
        {
            uint16_t item_id = resolve_upgrades(override.value.item_id);
            item_row_t *row = get_item_row(override.value.looks_like_item_id);
            if (row == NULL) {
                row = get_item_row(override.value.item_id);
            }
            *p = row->chest_type;
        }
        else
        {
            *p = 0;
        }
        
    }
    
}