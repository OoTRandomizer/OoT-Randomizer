#include "pots.h"
#include "n64.h"
#include "gfx.h"
#include "textures.h"
#include "z64.h"

#define DUNGEON_POT_SIDE_TEXTURE (uint8_t*)0x050108A0
#define DUNGEON_POT_TOP_TEXTURE (uint8_t*)0x050118A0
#define DUNGEON_POT_DLIST (z64_gfx_t*)0x05017870

#define POT_SIDE_TEXTURE (uint8_t*)0x06000000
#define POT_TOP_TEXTURE (uint8_t*)0x06001000
#define POT_DLIST (z64_gfx_t*)0x060017C0

extern uint8_t POTCRATE_TEXTURES_MATCH_CONTENTS;
extern uint16_t drop_collectible_override_flag;
extern uint8_t POTCRATE_GOLD_TEXTURE;
extern uint8_t POTCRATE_GILDED_TEXTURE;
extern uint8_t POTCRATE_SILVER_TEXTURE;
extern uint8_t POTCRATE_SKULL_TEXTURE;
extern uint8_t POTCRATE_HEART_TEXTURE;
extern uint8_t SOA_UNLOCKS_POTCRATE_TEXTURE;

override_t get_pot_override(z64_actor_t* actor, z64_game_t* game) {
    EnItem00 dummy;
    dummy.actor.actor_id = 0x15;
    dummy.actor.rot_init.y = actor->rot_init.z;
    dummy.actor.variable = 0;

    override_t override = lookup_override(&(dummy.actor), game->scene_index, 0);
    if (override.key.all != 0) {
        dummy.override = override;
        if (!Get_CollectibleOverrideFlag(&dummy)) {
            return override;
        }
    }
    return (override_t) { 0 };
}

override_t get_flying_pot_override(z64_actor_t* actor, z64_game_t* game) {
    EnItem00 dummy;
    dummy.actor.actor_id = 0x15;
    dummy.actor.rot_init.y = actor->rot_init.z;
    dummy.actor.variable = 0;

    override_t override = lookup_override(&(dummy.actor), game->scene_index, 0);
    if (override.key.all != 0) {
        dummy.override = override;
        if (!Get_CollectibleOverrideFlag(&dummy)) {
            return override;
        }
    }
    return (override_t) { 0 };
}

void draw_pot(z64_actor_t* actor, z64_game_t* game) {
    // get original dlist and texture
    z64_gfx_t* dlist = DUNGEON_POT_DLIST;
    uint8_t* side_texture = DUNGEON_POT_SIDE_TEXTURE;
    uint8_t* top_texture = DUNGEON_POT_TOP_TEXTURE;

    // overworld pot or hba pot
    if ((actor->actor_id == 0x111 && (actor->variable >> 8) & 1) || actor->actor_id == 0x117) {
        dlist = POT_DLIST;
        side_texture = POT_SIDE_TEXTURE;
        top_texture = POT_TOP_TEXTURE;
    }

    uint8_t chest_type = 0;
    if (actor->actor_id == 0x111) { // Regular pot
        chest_type = ((ObjTsubo*)actor)->chest_type;
    } else if (actor->actor_id == 0x117) { // HBA Pot
        chest_type = BROWN_CHEST;
    } else if (actor->actor_id == 0x11D) { // Flying pot
        chest_type = ((EnTuboTrap*)actor)->chest_type;
    }

    // get override texture
    if (!SOA_UNLOCKS_POTCRATE_TEXTURE || z64_file.stone_of_agony != 0) {
        switch (chest_type) {
            case GILDED_CHEST:
                if (POTCRATE_GILDED_TEXTURE) {
                    side_texture = get_texture(TEXTURE_ID_POT_GOLD);
                }
                break;

            case SILVER_CHEST:
                if (POTCRATE_SILVER_TEXTURE) {
                    side_texture = get_texture(TEXTURE_ID_POT_KEY);
                }
                break;

            case GOLD_CHEST:
                if (POTCRATE_GOLD_TEXTURE) {
                    side_texture = get_texture(TEXTURE_ID_POT_BOSSKEY);
                }
                break;

            case SKULL_CHEST_SMALL:
            case SKULL_CHEST_BIG:
                if (POTCRATE_SKULL_TEXTURE) {
                    side_texture = get_texture(TEXTURE_ID_POT_SKULL);
                }
                break;

            case HEART_CHEST_SMALL:
            case HEART_CHEST_BIG:
                if (POTCRATE_HEART_TEXTURE) {
                    side_texture = get_texture(TEXTURE_ID_POT_SIDE_HEART);
                    top_texture = get_texture(TEXTURE_ID_POT_TOP_HEART);
                }
                break;

            default:
                break;
        }
    }

    // push custom dlist (that sets the texture) to segment 09
    z64_gfx_t* gfx = game->common.gfx;
    gfx->poly_opa.d -= 4;
    gDPSetTextureImage(gfx->poly_opa.d, G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, side_texture);
    gSPEndDisplayList(gfx->poly_opa.d + 1);
    gMoveWd(gfx->poly_opa.p++, G_MW_SEGMENT, 9 * sizeof(int), gfx->poly_opa.d);

    // push custom dlist (that sets the texture) to segment 0A
    gDPSetTextureImage(gfx->poly_opa.d + 2, G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, top_texture);
    gSPEndDisplayList(gfx->poly_opa.d + 3);
    gMoveWd(gfx->poly_opa.p++, G_MW_SEGMENT, 0x0A * sizeof(int), gfx->poly_opa.d + 2);

    // draw the original dlist that has been hacked in ASM to jump to the custom dlist
    z64_Gfx_DrawDListOpa(game, dlist);
}

void draw_pot_hack(z64_actor_t* actor, z64_game_t* game) {
    draw_pot(actor, game);
}

void draw_hba_pot_hack(z64_actor_t* actor, z64_game_t* game) {
    EnGSwitch* switch_actor = (EnGSwitch*)actor;

    if (!switch_actor->broken) {
        draw_pot(actor, game);
    }
}

void draw_flying_pot_hack(z64_actor_t* actor, z64_game_t* game) {
    draw_pot(actor, game);
}

void ObjTsubo_SpawnCollectible_Hack(z64_actor_t* this, z64_game_t* game) {
    int16_t dropParams = this->variable & 0x1F;
    if ((dropParams >= ITEM00_RUPEE_GREEN) && (dropParams <= ITEM00_BOMBS_SPECIAL)) {
        drop_collectible_override_flag = this->rot_init.z;
        EnItem00* spawned = z64_Item_DropCollectible(game, &this->pos_world, (dropParams | (((this->variable >> 9) & 0x3F) << 8)));
        drop_collectible_override_flag = 0;
    }
}

void EnTuboTrap_DropCollectible_Hack(z64_actor_t* this, z64_game_t* game) {
    int16_t params = this->variable;
    int16_t param3FF = (params >> 6) & 0x3FF;

    if (param3FF >= 0 && param3FF < 0x1A) {
        drop_collectible_override_flag = this->rot_init.z;
        EnItem00* spawned = z64_Item_DropCollectible(game, &this->pos_world, param3FF | ((params & 0x3F) << 8));
        drop_collectible_override_flag = 0;
    }
}
