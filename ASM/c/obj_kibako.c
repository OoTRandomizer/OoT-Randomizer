#include "item_table.h"
#include "get_items.h"
#include "z64.h"
#include "textures.h"
#include "obj_kibako.h"
#include "actor.h"

#define SMALLCRATE_DLIST (z64_gfx_t*)0x05005290
#define SMALLCRATE_TEXTURE (uint8_t*)0x05011CA0
extern uint8_t POTCRATE_TEXTURES_MATCH_CONTENTS;
extern uint8_t POTCRATE_GOLD_TEXTURE;
extern uint8_t POTCRATE_GILDED_TEXTURE;
extern uint8_t POTCRATE_SILVER_TEXTURE;
extern uint8_t POTCRATE_SKULL_TEXTURE;
extern uint8_t POTCRATE_HEART_TEXTURE;
extern uint8_t SOA_UNLOCKS_POTCRATE_TEXTURE;

void ObjKibako_Draw(z64_actor_t* actor, z64_game_t* game) {
    uint8_t* texture = SMALLCRATE_TEXTURE; // get original texture

    ObjKibako* this = (ObjKibako*)actor;

    if (!SOA_UNLOCKS_POTCRATE_TEXTURE || z64_file.stone_of_agony != 0) {
        switch (this->chest_type) {
            case GILDED_CHEST:
                if (POTCRATE_GILDED_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_SMALLCRATE_GOLD);
                }
                break;

            case SILVER_CHEST:
                if (POTCRATE_SILVER_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_SMALLCRATE_KEY);
                }
                break;

            case GOLD_CHEST:
                if (POTCRATE_GOLD_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_SMALLCRATE_BOSSKEY);
                }
                break;

            case SKULL_CHEST_SMALL:
            case SKULL_CHEST_BIG:
                if (POTCRATE_SKULL_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_SMALLCRATE_SKULL);
                }
                break;

            case HEART_CHEST_SMALL:
            case HEART_CHEST_BIG:
                if (POTCRATE_HEART_TEXTURE) {
                    texture = get_texture(TEXTURE_ID_SMALLCRATE_HEART);
                }
                break;

            default:
                break;
        }
    }

    // push custom dlists (that set the palette and textures) to segment 09
    z64_gfx_t* gfx = game->common.gfx;
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

    xflag_t* flag = &Actor_GetAdditionalData(this)->flag;
    if (flag->all && !Get_NewFlag(flag)) {
        drop_collectible_override_flag = *flag;
        EnItem00* spawned = z64_Item_DropCollectible(globalCtx, &this->pos_world, 0);
        z64_bzero(&drop_collectible_override_flag, sizeof(drop_collectible_override_flag));
        return;
    }

    if ((collectible >= 0) && (collectible <= 0x19)) {
        EnItem00* spawned = z64_Item_DropCollectible(globalCtx, &this->pos_world,
                             collectible | (((this->variable >> 8) & 0x3F) << 8));
    }
}
