#include "en_wood02.h"
#include "get_items.h"
#include "item_table.h"

#define MARKET_CHILD_DAY   0x20
#define MARKET_CHILD_NIGHT 0x21
#define WOOD_TREE_LAST_TYPE 0x0A
#define G_DL_OPCODE 0xDE
#define G_ENDDL_OPCODE 0xDF
#define G_SETPRIMCOLOR_OPCODE 0xFA
#define G_SETENVCOLOR_OPCODE 0xFB
#define TREE_DLIST_MAX_COMMANDS 64
#define TREE_DLIST_ALIGNMENT 16
#define K0_BASE 0x80000000
#define WOOD_SPAWN_SPAWNER 2
#define TREE_GROUP_CHILD_COUNT 5

typedef struct {
    /* 0x000 */ z64_actor_t actor;
    /* 0x13C */ uint8_t pad_13C[0x10];
    /* 0x14C */ int16_t drop_type;
    /* 0x14E */ uint8_t child_state[5];
    /* 0x153 */ uint8_t spawn_type;
} EnWood02;

typedef void (*EnWood02UpdateFunc)(z64_actor_t*, z64_game_t*);
typedef void (*EnWood02DrawFunc)(z64_actor_t*, z64_game_t*);

typedef struct {
    uint32_t w0;
    uint32_t w1;
} EnWood02GfxCommand;

static EnWood02DrawFunc sOriginalDraw;

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
    extra->chest_type = 0;
    Actor_StoreFlag(&tree->actor, game, expected_flag);
    Actor_StoreChestType(&tree->actor, game);
}

static bool EnWood02_GetContentColor(z64_actor_t* actor, colorRGB8_t* color) {
    ActorAdditionalData* extra = Actor_GetAdditionalData(actor);

    if (!extra->flag.all) {
        return false;
    }

    if (Get_NewFlag(&extra->flag)) {
        extra->chest_type = 0;
        return false;
    }

    switch (extra->chest_type) {
        case BROWN_CHEST:
            *color = (colorRGB8_t) { 20, 205, 50 };
            return true;
        case GILDED_CHEST:
            *color = (colorRGB8_t) { 40, 40, 255 };
            return true;
        case SILVER_CHEST:
            *color = (colorRGB8_t) { 20, 255, 255 };
            return true;
        case GOLD_CHEST:
            *color = (colorRGB8_t) { 255, 255, 20 };
            return true;
        case SKULL_CHEST_SMALL:
        case SKULL_CHEST_BIG:
            *color = (colorRGB8_t) { 225, 20, 255 };
            return true;
        case HEART_CHEST_SMALL:
        case HEART_CHEST_BIG:
            *color = (colorRGB8_t) { 255, 55, 55 };
            return true;
        default:
            return false;
    }
}

static uint32_t EnWood02_PackColor(colorRGB8_t color, uint8_t alpha) {
    return ((uint32_t)color.r << 24) |
           ((uint32_t)color.g << 16) |
           ((uint32_t)color.b << 8) |
           alpha;
}

static EnWood02GfxCommand* EnWood02_SegmentedToVirtual(uint32_t address) {
    uint8_t segment = address >> 24;
    if (segment >= 16 || z64_stab.seg[segment] == 0) {
        return NULL;
    }

    return (EnWood02GfxCommand*)(K0_BASE + z64_stab.seg[segment] + (address & 0x00FFFFFF));
}

static EnWood02GfxCommand* EnWood02_AllocXluCommands(z64_gfx_t* gfx, uint32_t command_count) {
    uint32_t size = command_count * sizeof(EnWood02GfxCommand);
    uint32_t aligned_size = (size + (TREE_DLIST_ALIGNMENT - 1)) & ~(TREE_DLIST_ALIGNMENT - 1);
    uint8_t* allocation = (uint8_t*)gfx->poly_xlu.d - aligned_size;

    if (allocation <= (uint8_t*)gfx->poly_xlu.p) {
        return NULL;
    }

    gfx->poly_xlu.d = (Gfx*)allocation;
    return (EnWood02GfxCommand*)allocation;
}

static void EnWood02_PatchFoliageEnvColor(
    z64_game_t* game,
    EnWood02GfxCommand* xlu_start,
    colorRGB8_t color
) {
    EnWood02GfxCommand* command = (EnWood02GfxCommand*)game->common.gfx->poly_xlu.p;
    while (command > xlu_start) {
        command--;
        if ((command->w0 >> 24) == G_SETENVCOLOR_OPCODE) {
            command->w1 = EnWood02_PackColor(color, 0);
            return;
        }
    }
}

static void EnWood02_PatchFoliagePrimColor(
    z64_game_t* game,
    EnWood02GfxCommand* xlu_start,
    colorRGB8_t color
) {
    EnWood02GfxCommand* display_list_call = (EnWood02GfxCommand*)game->common.gfx->poly_xlu.p;
    while (display_list_call > xlu_start) {
        display_list_call--;
        if ((display_list_call->w0 >> 24) == G_DL_OPCODE) {
            break;
        }
    }

    if (display_list_call <= xlu_start || (display_list_call->w0 >> 24) != G_DL_OPCODE) {
        return;
    }

    EnWood02GfxCommand* source = EnWood02_SegmentedToVirtual(display_list_call->w1);
    if (source == NULL) {
        return;
    }

    uint32_t command_count = 0;
    int32_t prim_color_index = -1;
    while (command_count < TREE_DLIST_MAX_COMMANDS) {
        if ((source[command_count].w0 >> 24) == G_SETPRIMCOLOR_OPCODE) {
            prim_color_index = command_count;
        }

        command_count++;
        if ((source[command_count - 1].w0 >> 24) == G_ENDDL_OPCODE) {
            break;
        }
    }

    if ((command_count == TREE_DLIST_MAX_COMMANDS &&
         (source[command_count - 1].w0 >> 24) != G_ENDDL_OPCODE) ||
        prim_color_index < 0) {
        return;
    }

    EnWood02GfxCommand* clone = EnWood02_AllocXluCommands(game->common.gfx, command_count);
    if (clone == NULL) {
        return;
    }

    for (uint32_t i = 0; i < command_count; i++) {
        clone[i] = source[i];
    }
    clone[prim_color_index].w1 = EnWood02_PackColor(color, 0xFF);

    display_list_call->w1 = ((uint32_t)clone) & 0x1FFFFFFF;
}

static void EnWood02_InstallHooks(z64_actor_t* actor) {
    ActorAdditionalData* extra = Actor_GetAdditionalData(actor);

    if (extra->original_update == NULL && actor->main_proc != (void*)EnWood02_UpdateHook) {
        extra->original_update = actor->main_proc;
        actor->main_proc = (void*)EnWood02_UpdateHook;
    }

    if (actor->draw_proc != NULL && actor->draw_proc != (void*)EnWood02_DrawHook) {
        sOriginalDraw = (EnWood02DrawFunc)actor->draw_proc;
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
    if (sOriginalDraw == NULL) {
        return;
    }

    EnWood02GfxCommand* xlu_start = (EnWood02GfxCommand*)game->common.gfx->poly_xlu.p;
    sOriginalDraw(actor, game);

    colorRGB8_t color;
    if (!EnWood02_GetContentColor(actor, &color)) {
        return;
    }

    EnWood02_PatchFoliageEnvColor(game, xlu_start, color);
    EnWood02_PatchFoliagePrimColor(game, xlu_start, color);
}

static void EnWood02_UpdateHook(z64_actor_t* actor, z64_game_t* game) {
    EnWood02* tree = (EnWood02*)actor;
    ActorAdditionalData* extra = Actor_GetAdditionalData(actor);
    EnWood02UpdateFunc original_update = (EnWood02UpdateFunc)extra->original_update;

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
