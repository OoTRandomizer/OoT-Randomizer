#include "z64.h"
#include "item_table.h"
#include "get_items.h"
#include "textures.h"
#include "obj_comb.h"
#include "actor.h"

#define GAMEPLAY_FIELD_KEEP_BEEHIVE_TEXTURE (uint8_t*)0x05008900

// Hack beehives to drop a collectible w / an extended flag, based on the grotto param
void obj_comb_drop_collectible(z64_actor_t* actor, int16_t params) {
    // Check if we're in a grotto
    xflag_t* flag = &(Actor_GetAdditionalData(actor)->flag);

    if (params >= 0) {
        if (flag->all && !Get_NewFlag(flag)) {
            // set up params for Item_DropCollectible
            drop_collectible_override_flag = *flag;
            EnItem00* spawned = z64_Item_DropCollectible2(&z64_game, &actor->pos_world, params);
            z64_bzero(&drop_collectible_override_flag, sizeof(drop_collectible_override_flag));
        } else { // Normal beehive behavior
            if (z64_Rand_ZeroOne() > 0.5f) {
                z64_Item_DropCollectible(&z64_game, &actor->pos_world, params);
            }
        }
    }
}

void ObjComb_Update(z64_actor_t* thisx, z64_game_t* game) {
    ObjComb* this = (ObjComb*)thisx;
    if (this->actor.dropFlag > 0) {
        this->actor.dropFlag --;
    }
    this->unk_1B2 += 0x2EE0;
    this->actionFunc(this, game);
    this->actor.rot_2.x = z64_Math_SinS(this->unk_1B2) * this->unk_1B0 + this->actor.rot_init.x;

    if (this->chest_type > 0) {
        if (this->unk_1B0 == 0 && this->actor.dropFlag == 0) {
            this->unk_1B0 = 0x0800;
            this->actor.dropFlag = 0x40;
        }
    }
}

/*
// Left here if we ever want to do beehive textures.
void ObjComb_Draw_Hack(z64_actor_t* this, z64_game_t* game) {
    uint8_t* texture = GAMEPLAY_FIELD_KEEP_BEEHIVE_TEXTURE;

    override_t override = get_beehive_override(this, game);

    if(override.key.all != 0) {
        uint16_t item_id = resolve_upgrades(override);
        item_row_t* row = get_item_row(override.value.looks_like_item_id);
        if (row == NULL) {
            row = get_item_row(override.value.item_id);
        }
        switch (row->chest_type) {
            case GILDED_CHEST:
                texture = get_texture(TEXTURE_ID_BEEHIVE_GOLD);
                break;

            case GOLD_CHEST:
                texture = get_texture(TEXTURE_ID_BEEHIVE_BOSSKEY);
                break;

            case HEART_CHEST:
                texture = get_texture(TEXTURE_ID_BEEHIVE_HEART);
                break;

            default:
                break;
        }
    }

    z64_gfx_t* gfx = game->common.gfx;
    gfx->poly_opa.d -= 2;
    gDPSetTextureImage(gfx->poly_opa.d, G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, texture);
    gSPEndDisplayList(gfx->poly_opa.d + 1);
    gMoveWd(gfx->poly_opa.p++, G_MW_SEGMENT, 9 * sizeof(int), gfx->poly_opa.d);
*/
