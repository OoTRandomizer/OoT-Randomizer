#include "item_table.h"
#include "get_items.h"
#include "z64.h"
#include "textures.h"
#include "z64.h"
#include "obj_kibako.h"

#define SMALLCRATE_DLIST (z64_gfx_t *)0x05005290
#define SMALLCRATE_TEXTURE (uint8_t *)0x05011CA0
extern uint8_t POTCRATE_TEXTURES_MATCH_CONTENTS;
extern uint16_t drop_collectible_override_flag;

override_t get_smallcrate_override(z64_actor_t *actor, z64_game_t *game) {
    // make a dummy EnItem00 with enough info to get the override
    EnItem00 dummy;
    dummy.actor.actor_id = 0x15;
    dummy.actor.rot_init.y = actor->rot_init.z;
    dummy.actor.variable = 0;
    
    override_t override = lookup_override(&dummy, game->scene_index, 0);
    if(override.key.all != 0)
    {
        dummy.override = override;
        if(!Get_CollectibleOverrideFlag(&dummy))
        {
            return override;
        }    
    }
    return (override_t) { 0 };
}

void ObjKibako_Draw(z64_actor_t *actor, z64_game_t *game) {
    uint8_t *texture = SMALLCRATE_TEXTURE; // get original texture

    ObjKibako* this = (ObjKibako*)actor;
    if (this->chest_type == GILDED_CHEST) {
        texture = get_texture(TEXTURE_ID_SMALLCRATE_GOLD);
    } else if (this->chest_type == SILVER_CHEST) {
        texture = get_texture(TEXTURE_ID_SMALLCRATE_KEY);
    } else if (this->chest_type == GOLD_CHEST) {
        texture = get_texture(TEXTURE_ID_SMALLCRATE_BOSSKEY);
    } else if (this->chest_type == SKULL_CHEST_SMALL || this->chest_type == SKULL_CHEST_BIG) {
        texture = get_texture(TEXTURE_ID_SMALLCRATE_SKULL);
    }

    // push custom dlists (that set the palette and textures) to segment 09
    z64_gfx_t *gfx = game->common.gfx;
    gfx->poly_opa.d -= 2;
    gDPSetTextureImage(gfx->poly_opa.d, G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, texture);
    gSPEndDisplayList(gfx->poly_opa.d + 1);

    gMoveWd(gfx->poly_opa.p++, G_MW_SEGMENT, 9 * sizeof(int), gfx->poly_opa.d);

    // draw the original dlist that has been hacked in ASM to jump to the custom dlists
    z64_Gfx_DrawDListOpa(game, SMALLCRATE_DLIST);
}

void ObjKibako_SpawnCollectible_Hack(z64_actor_t* this, z64_game_t* globalCtx) {
    int16_t collectible;

    collectible = this->variable & 0x1F;
    if ((collectible >= 0) && (collectible <= 0x19)) {
        drop_collectible_override_flag = this->rot_init.z;
        EnItem00* spawned = z64_Item_DropCollectible(globalCtx, &this->pos_world,
                             collectible | (((this->variable >> 8) & 0x3F) << 8));
    }
}