#include "en_wood02.h"
#include "n64.h"
#include "gfx.h"
#include "sys_matrix.h"
#include "get_items.h"
#include "item_table.h"
#include "textures.h"

#define MARKET_CHILD_DAY     0x20
#define MARKET_CHILD_NIGHT   0x21
#define WOOD_TREE_LAST_TYPE  0x0A
#define WOOD_SPAWN_SPAWNER   2
#define TREE_GROUP_CHILD_COUNT 5

#define WOOD_DRAW_TREE_CONICAL         0
#define WOOD_DRAW_TREE_OVAL            1
#define WOOD_DRAW_TREE_KAKARIKO_ADULT  2
#define WOOD_DRAW_TREE_COUNT           3

#define WOOD_TYPE_OVAL_GREEN           0x05
#define WOOD_TYPE_OVAL_YELLOW_SPAWNER  0x06
#define WOOD_TYPE_OVAL_YELLOW_SPAWNED  0x07
#define WOOD_TYPE_OVAL_GREEN_SPAWNER   0x08
#define WOOD_TYPE_OVAL_GREEN_SPAWNED   0x09

#define WOOD_TRUNK_TEXTURE_CONICAL ((uint8_t*)0x06000790)
#define WOOD_TRUNK_TEXTURE_OVAL    ((uint8_t*)0x06002F90)

#define WOOD_TRUNK_DLIST_CONICAL        ((z64_gfx_t*)0x060078D0)
#define WOOD_TRUNK_DLIST_OVAL           ((z64_gfx_t*)0x06007CA0)
#define WOOD_TRUNK_DLIST_KAKARIKO_ADULT ((z64_gfx_t*)0x060080D0)

#define WOOD_FOLIAGE_DLIST_CONICAL        ((Gfx*)0x06007968)
#define WOOD_FOLIAGE_DLIST_OVAL           ((Gfx*)0x06007D38)
#define WOOD_FOLIAGE_DLIST_KAKARIKO_ADULT ((Gfx*)0x060081A8)

typedef void (*EnWood02UpdateFunc)(z64_actor_t*, z64_game_t*);
typedef void (*append_setup_dl_25_to_xlu_fn)(z64_gfx_t*);

#define append_setup_dl_25_to_xlu ((append_setup_dl_25_to_xlu_fn)0x8007E2C0)

typedef struct {
    colorRGB8_t foliage_color;
    TextureId trunk_texture;
} EnWood02Appearance;

extern uint8_t POTCRATE_GOLD_TEXTURE;
extern uint8_t POTCRATE_GILDED_TEXTURE;
extern uint8_t POTCRATE_SILVER_TEXTURE;
extern uint8_t POTCRATE_SKULL_TEXTURE;
extern uint8_t POTCRATE_HEART_TEXTURE;
extern uint8_t SOA_UNLOCKS_POTCRATE_TEXTURE;

static void EnWood02_UpdateHook(z64_actor_t* actor, z64_game_t* game);
static void EnWood02_DrawHook(z64_actor_t* actor, z64_game_t* game);

// Five positions used by the vanilla En_Wood02 group spawner
static const float sTreeChildDistances[TREE_GROUP_CHILD_COUNT] = {
    707.0f, 525.0f, 510.0f, 500.0f, 566.0f,
};

static const int16_t sTreeChildAngles[TREE_GROUP_CHILD_COUNT] = {
    0x1FFF, 0x4C9E, 0x77F5, (int16_t)0xA5C9, (int16_t)0xD6C3,
};

static bool EnWood02_IsTree(const EnWood02* tree) {
    return (tree->actor.variable & 0xFF) <= WOOD_TREE_LAST_TYPE;
}

xflag_t EnWood02_NormalizeFlag(xflag_t flag) {
    // Market day and night are separate scenes, but represent as one.
    if (flag.scene == MARKET_CHILD_NIGHT) {
        flag.scene = MARKET_CHILD_DAY;
        flag.room = 0;
        flag.setup = 0;
        flag.flag = 15;
    }

    return flag;
}

static bool EnWood02_FlagEquals(const xflag_t* lhs, const xflag_t* rhs) {
    return lhs->scene == rhs->scene && lhs->all == rhs->all;
}

static uint8_t EnWood02_FindChildSlot(const EnWood02* tree, const EnWood02* parent) {
    float best_distance_sq = 0.0f;
    uint8_t best_slot = 0;

    for (uint8_t slot = 0; slot < TREE_GROUP_CHILD_COUNT; slot++) {
        int16_t angle = sTreeChildAngles[slot] + parent->actor.rot_world.y;
        float expected_x = parent->actor.pos_init.x +
                           (sTreeChildDistances[slot] * z64_Math_SinS(angle));
        float expected_z = parent->actor.pos_init.z +
                           (sTreeChildDistances[slot] * z64_Math_SinS(angle + 0x4000));
        float delta_x = tree->actor.pos_init.x - expected_x;
        float delta_z = tree->actor.pos_init.z - expected_z;
        float distance_sq = (delta_x * delta_x) + (delta_z * delta_z);

        if (slot == 0 || distance_sq < best_distance_sq) {
            best_distance_sq = distance_sq;
            best_slot = slot;
        }
    }

    return best_slot;
}

static void EnWood02_SyncChildFlag(EnWood02* tree, z64_game_t* game) {
    if (tree->actor.parent == NULL || tree->actor.parent->actor_id != EN_WOOD02) {
        return;
    }

    EnWood02* parent = (EnWood02*)tree->actor.parent;
    ActorAdditionalData* parent_extra = Actor_GetAdditionalData(&parent->actor);
    if (!parent_extra->flag.all) {
        return;
    }

    uint8_t child_slot = EnWood02_FindChildSlot(tree, parent);

    xflag_t expected_flag = parent_extra->flag;
    expected_flag.flag = parent_extra->flag.flag + child_slot + 1;
    expected_flag.subflag = 0;

    ActorAdditionalData* extra = Actor_GetAdditionalData(&tree->actor);
    if (EnWood02_FlagEquals(&extra->flag, &expected_flag)) {
        return;
    }

    extra->flag = (xflag_t) { 0 };
    tree->chest_type = 0;
    Actor_StoreFlag(&tree->actor, game, expected_flag);
    Actor_StoreChestType(&tree->actor, game);
}

static bool EnWood02_GetContentAppearance(z64_actor_t* actor, EnWood02Appearance* appearance) {
    EnWood02* tree = (EnWood02*)actor;
    ActorAdditionalData* extra = Actor_GetAdditionalData(actor);

    if (!extra->flag.all) {
        return false;
    }

    if (Get_NewFlag(&extra->flag)) {
        tree->chest_type = 0;
        return false;
    }

    if (SOA_UNLOCKS_POTCRATE_TEXTURE && z64_file.stone_of_agony == 0) {
        return false;
    }

    switch (tree->chest_type) {
        case GILDED_CHEST:
            if (!POTCRATE_GILDED_TEXTURE) {
                return false;
            }
            appearance->foliage_color = (colorRGB8_t) { 40, 40, 255 };
            appearance->trunk_texture = TEXTURE_ID_TREE_GILDED;
            return true;
        case SILVER_CHEST:
            if (!POTCRATE_SILVER_TEXTURE) {
                return false;
            }
            appearance->foliage_color = (colorRGB8_t) { 20, 255, 255 };
            appearance->trunk_texture = TEXTURE_ID_TREE_SILVER;
            return true;
        case GOLD_CHEST:
            if (!POTCRATE_GOLD_TEXTURE) {
                return false;
            }
            appearance->foliage_color = (colorRGB8_t) { 255, 255, 20 };
            appearance->trunk_texture = TEXTURE_ID_TREE_GOLD;
            return true;
        case SKULL_CHEST_SMALL:
        case SKULL_CHEST_BIG:
            if (!POTCRATE_SKULL_TEXTURE) {
                return false;
            }
            appearance->foliage_color = (colorRGB8_t) { 225, 20, 255 };
            appearance->trunk_texture = TEXTURE_ID_TREE_SKULL;
            return true;
        case HEART_CHEST_SMALL:
        case HEART_CHEST_BIG:
            if (!POTCRATE_HEART_TEXTURE) {
                return false;
            }
            appearance->foliage_color = (colorRGB8_t) { 255, 55, 55 };
            appearance->trunk_texture = TEXTURE_ID_TREE_HEART;
            return true;
        default:
            return false;
    }
}

static const z64_gfx_t* sTreeTrunkDLists[WOOD_DRAW_TREE_COUNT] = {
    WOOD_TRUNK_DLIST_CONICAL,
    WOOD_TRUNK_DLIST_OVAL,
    WOOD_TRUNK_DLIST_KAKARIKO_ADULT,
};

static const Gfx* sTreeFoliageDLists[WOOD_DRAW_TREE_COUNT] = {
    WOOD_FOLIAGE_DLIST_CONICAL,
    WOOD_FOLIAGE_DLIST_OVAL,
    WOOD_FOLIAGE_DLIST_KAKARIKO_ADULT,
};

static uint8_t* EnWood02_GetVanillaTrunkTexture(uint8_t draw_type) {
    return draw_type == WOOD_DRAW_TREE_OVAL ? WOOD_TRUNK_TEXTURE_OVAL : WOOD_TRUNK_TEXTURE_CONICAL;
}

static colorRGB8_t EnWood02_GetVanillaFoliageColor(const EnWood02* tree) {
    uint8_t type = tree->actor.variable & 0xFF;

    if (type == WOOD_TYPE_OVAL_GREEN ||
        type == WOOD_TYPE_OVAL_GREEN_SPAWNER ||
        type == WOOD_TYPE_OVAL_GREEN_SPAWNED) {
        return (colorRGB8_t) { 50, 170, 70 };
    }

    if (type == WOOD_TYPE_OVAL_YELLOW_SPAWNER ||
        type == WOOD_TYPE_OVAL_YELLOW_SPAWNED) {
        return (colorRGB8_t) { 180, 155, 0 };
    }

    if ((tree->draw_type & 0x0F) == WOOD_DRAW_TREE_KAKARIKO_ADULT) {
        return (colorRGB8_t) { 57, 197, 86 };
    }

    return (colorRGB8_t) { 28, 88, 13 };
}

static void EnWood02_SetTrunkTextureSegment(z64_gfx_t* gfx, uint8_t* texture) {
    gfx->poly_opa.d -= 2;
    gDPSetTextureImage(gfx->poly_opa.d, G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, texture);
    gSPEndDisplayList(gfx->poly_opa.d + 1);
    gSPSegment(gfx->poly_opa.p++, 0x09, gfx->poly_opa.d);
}

static void EnWood02_SetFoliageColorSegment(z64_gfx_t* gfx, colorRGB8_t color) {
    gfx->poly_xlu.d -= 2;
    gDPSetPrimColor(gfx->poly_xlu.d, 0, 0, color.r, color.g, color.b, 0xFF);
    gSPEndDisplayList(gfx->poly_xlu.d + 1);
    gSPSegment(gfx->poly_xlu.p++, 0x0A, gfx->poly_xlu.d);
}

static void EnWood02_DrawTree(EnWood02* tree, z64_game_t* game) {
    z64_gfx_t* gfx = game->common.gfx;
    uint8_t draw_type = tree->draw_type & 0x0F;
    colorRGB8_t foliage_color;
    uint8_t* trunk_texture;
    EnWood02Appearance appearance;

    if (draw_type >= WOOD_DRAW_TREE_COUNT) {
        return;
    }

    foliage_color = EnWood02_GetVanillaFoliageColor(tree);
    trunk_texture = EnWood02_GetVanillaTrunkTexture(draw_type);

    if (EnWood02_GetContentAppearance(&tree->actor, &appearance)) {
        uint8_t* override_texture;

        foliage_color = appearance.foliage_color;
        override_texture = get_texture(appearance.trunk_texture);
        if (override_texture != NULL) {
            trunk_texture = override_texture;
        }
    }

    EnWood02_SetTrunkTextureSegment(gfx, trunk_texture);
    z64_Gfx_DrawDListOpa(game, (z64_gfx_t*)sTreeTrunkDLists[draw_type]);

    append_setup_dl_25_to_xlu(gfx);
    EnWood02_SetFoliageColorSegment(gfx, foliage_color);
    gDPSetEnvColor(gfx->poly_xlu.p++, foliage_color.r, foliage_color.g, foliage_color.b, 0);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx),
              G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, sTreeFoliageDLists[draw_type]);
}

static void EnWood02_InstallHooks(z64_actor_t* actor) {
    EnWood02* tree = (EnWood02*)actor;

    if (actor->main_proc != (void*)EnWood02_UpdateHook) {
        tree->original_update = actor->main_proc;
        actor->main_proc = (void*)EnWood02_UpdateHook;
    }

    if (actor->draw_proc != NULL && actor->draw_proc != (void*)EnWood02_DrawHook) {
        actor->draw_proc = (void*)EnWood02_DrawHook;
    }
}

static void EnWood02_RefreshChildren(EnWood02* parent, z64_game_t* game) {
    if (parent->spawn_type != WOOD_SPAWN_SPAWNER) {
        return;
    }

    z64_actor_t* actor = game->actorLists[ACTORTYPE_PROP].head;
    while (actor != NULL) {
        z64_actor_t* next = actor->next;
        if (actor->actor_id == EN_WOOD02 && actor->parent == &parent->actor &&
            EnWood02_IsTree((EnWood02*)actor)) {
            EnWood02_InstallHooks(actor);
            EnWood02_SyncChildFlag((EnWood02*)actor, game);
        }
        actor = next;
    }
}

static void EnWood02_DrawHook(z64_actor_t* actor, z64_game_t* game) {
    EnWood02_DrawTree((EnWood02*)actor, game);
}

static void EnWood02_UpdateHook(z64_actor_t* actor, z64_game_t* game) {
    EnWood02* tree = (EnWood02*)actor;
    ActorAdditionalData* extra = Actor_GetAdditionalData(actor);
    EnWood02UpdateFunc original_update = (EnWood02UpdateFunc)tree->original_update;

    if (original_update == NULL) {
        return;
    }

    EnWood02_SyncChildFlag(tree, game);

    // home.rot.y is set by the player bonk code and consumed by EnWood02_Update.
    if (EnWood02_IsTree(tree) && actor->rot_init.y != 0 && extra->flag.all) {
        override_t override = get_newflag_override(&extra->flag);
        if (override.key.all) {
            z64_xyzf_t drop_pos = actor->pos_world;
            drop_pos.y += 200.0f;

            tree->drop_type = -1;
            drop_collectible_override_flag = extra->flag;
            z64_Item_DropCollectible(game, &drop_pos, ITEM00_RUPEE_GREEN);
            z64_bzero(&drop_collectible_override_flag, sizeof(drop_collectible_override_flag));
        }
    }

    original_update(actor, game);

    // Hook spawners that may create replacement children during its vanilla update.
    EnWood02_RefreshChildren(tree, game);
}

void EnWood02_AfterInitHack(z64_actor_t* actor, z64_game_t* game) {
    (void)game;

    if (actor->actor_id != EN_WOOD02 || actor->main_proc == NULL || !EnWood02_IsTree((EnWood02*)actor)) {
        return;
    }

    EnWood02_InstallHooks(actor);
}
