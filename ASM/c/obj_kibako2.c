#include "obj_kibako2.h"
#include "textures.h"
#include "actor.h"
#define CRATE_DLIST (z64_gfx_t *)0x06000960

#define CRATE_CI8_TEXTURE_PALETTE_OFFSET 0x00
#define CRATE_CI8_TEXTURE_TOP_OFFSET 0x200
#define CRATE_CI8_TEXTURE_SIDE_OFFSET 0xA00

extern uint8_t POTCRATE_TEXTURES_MATCH_CONTENTS;
extern uint8_t POTCRATE_GOLD_TEXTURE;
extern uint8_t POTCRATE_GILDED_TEXTURE;
extern uint8_t POTCRATE_SILVER_TEXTURE;
extern uint8_t POTCRATE_SKULL_TEXTURE;
extern uint8_t POTCRATE_HEART_TEXTURE;
extern uint8_t SOA_UNLOCKS_POTCRATE_TEXTURE;

// Hacks the regular crate spawn collectible function to spawn overridden collectibles
void ObjKibako2_SpawnCollectible_Hack(ObjKibako2* this, z64_game_t* globalCtx) {
    int16_t itemDropped;
    int16_t collectibleFlagTemp;
    collectibleFlagTemp = this->collectibleFlag & 0x3F;
    itemDropped = this->dyna.actor.rot_init.x & 0x1F;

    xflag_t* flag = &(Actor_GetAdditionalData((z64_actor_t*)this)->flag);
    if (flag->all && !Get_NewFlag(flag)) {
        drop_collectible_override_flag = *flag;
        EnItem00* spawned = z64_Item_DropCollectible(globalCtx, &this->dyna.actor.pos_world, 0);
        z64_bzero(&drop_collectible_override_flag, sizeof(drop_collectible_override_flag));
        return;
    }
    if (itemDropped >= 0 && itemDropped < 0x1A) {
        EnItem00* spawned = z64_Item_DropCollectible(globalCtx, &this->dyna.actor.pos_world, itemDropped | (collectibleFlagTemp << 8));
    }
}

void ObjKibako2_Draw(z64_actor_t* actor, z64_game_t* game) {
    uint8_t* texture = get_texture(TEXTURE_ID_CRATE_DEFAULT);

    // get override palette and textures

    ObjKibako2* this = (ObjKibako2*)actor;

    if (!SOA_UNLOCKS_POTCRATE_TEXTURE || z64_file.stone_of_agony != 0) {
        switch (this->chest_type) {
            case GILDED_CHEST:
                if (POTCRATE_GILDED_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_CRATE_GOLD);
                }
                break;

            case SILVER_CHEST:
                if (POTCRATE_SILVER_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_CRATE_KEY);
                }
                break;

            case GOLD_CHEST:
                if (POTCRATE_GOLD_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_CRATE_BOSSKEY);
                }
                break;

            case SKULL_CHEST_SMALL:
            case SKULL_CHEST_BIG:
                if (POTCRATE_SKULL_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_CRATE_SKULL);
                }
                break;

            case HEART_CHEST_SMALL:
            case HEART_CHEST_BIG:
                if (POTCRATE_HEART_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_CRATE_HEART);
                }
                break;

            default:
                break;
        }
    }

    // push custom dlists (that set the palette and textures) to segment 09
    z64_gfx_t* gfx = game->common.gfx;
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
