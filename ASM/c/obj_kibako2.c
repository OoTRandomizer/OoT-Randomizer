#include "obj_kibako2.h"
#include "textures.h"
#define CRATE_DLIST (z64_gfx_t *)0x06000960

#define CRATE_CI8_TEXTURE_PALETTE_OFFSET 0x00
#define CRATE_CI8_TEXTURE_TOP_OFFSET 0x200
#define CRATE_CI8_TEXTURE_SIDE_OFFSET 0xA00


extern uint8_t POTCRATE_TEXTURES_MATCH_CONTENTS;
extern uint16_t drop_collectible_override_flag;

// Hacks the regular crate spawn collectible function to spawn overridden collectibles
void ObjKibako2_SpawnCollectible_Hack(ObjKibako2 *this, z64_game_t *globalCtx) {
    int16_t itemDropped;
    int16_t collectibleFlagTemp;

    collectibleFlagTemp = this->collectibleFlag & 0x3F;             
    itemDropped = this->dyna.actor.rot_init.x & 0x1F;
    if (itemDropped >= 0 && itemDropped < 0x1A) {
        drop_collectible_override_flag = this->dyna.actor.rot_init.y;
        EnItem00* spawned = z64_Item_DropCollectible(globalCtx, &this->dyna.actor.pos_world, itemDropped | (collectibleFlagTemp << 8));
    }
}

override_t get_crate_override(z64_actor_t *actor, z64_game_t *game) {
    // make a dummy EnItem00 with enough info to get the override
    EnItem00 dummy;
    dummy.actor.actor_id = 0x15;
    dummy.actor.rot_init.y = actor->rot_init.y;
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

void ObjKibako2_Draw(z64_actor_t *actor, z64_game_t *game) {
    uint8_t* texture = get_texture(TEXTURE_ID_CRATE_DEFAULT);

    // get override palette and textures
    
    ObjKibako2* this = (ObjKibako2*)actor;

    if (this->chest_type == GILDED_CHEST) {
        texture = get_texture(TEXTURE_ID_CRATE_GOLD);
    } else if (this->chest_type == SILVER_CHEST) {
        texture = get_texture(TEXTURE_ID_CRATE_KEY);
    } else if (this->chest_type == GOLD_CHEST) {
        texture = get_texture(TEXTURE_ID_CRATE_BOSSKEY);
    } else if (this->chest_type == SKULL_CHEST_SMALL || this->chest_type == SKULL_CHEST_BIG) {
        texture = get_texture(TEXTURE_ID_CRATE_SKULL);
    }
    

    // push custom dlists (that set the palette and textures) to segment 09
    z64_gfx_t *gfx = game->common.gfx;
    gfx->poly_opa.d -= 6;
    gDPSetTextureImage(gfx->poly_opa.d, G_IM_FMT_CI, G_IM_SIZ_16b, 1, texture + CRATE_CI8_TEXTURE_TOP_OFFSET);
    gSPEndDisplayList(gfx->poly_opa.d + 1);
    gDPSetTextureImage(gfx->poly_opa.d + 2, G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, texture + CRATE_CI8_TEXTURE_PALETTE_OFFSET);
    gSPEndDisplayList(gfx->poly_opa.d + 3);
    gDPSetTextureImage(gfx->poly_opa.d + 4, G_IM_FMT_CI, G_IM_SIZ_16b, 1, texture + CRATE_CI8_TEXTURE_SIDE_OFFSET);
    gSPEndDisplayList(gfx->poly_opa.d + 5);

    gMoveWd(gfx->poly_opa.p++, G_MW_SEGMENT, 9 * sizeof(int), gfx->poly_opa.d);

    // draw the original dlist that has been hacked in ASM to jump to the custom dlists
    z64_Gfx_DrawDListOpa(game, CRATE_DLIST);
}
