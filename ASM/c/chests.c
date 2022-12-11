#include "chests.h"
#include "dungeon_info.h"
#include "item_effects.h"
#include "item_table.h"
#include "rng.h"
#include "n64.h"
#include "gfx.h"
#include "sys_matrix.h"
#include "textures.h"

#define BROWN_FRONT_TEXTURE 0x06001798
#define BROWN_BASE_TEXTURE 0x06002798
#define GOLD_FRONT_TEXTURE 0x06002F98
#define GOLD_BASE_TEXTURE 0x06003798

#define CHEST_BASE 1
#define CHEST_LID 3

#define box_obj_idx(actor) ((int8_t *)actor)[0x015A] // forest_hallway_actor->box_obj_idx
#define OBJECT_BOX 0x000E

uint32_t CHEST_TEXTURE_MATCH_CONTENTS = 0;
uint32_t CHEST_SIZE_MATCH_CONTENTS = 0;
uint32_t CHEST_SIZE_TEXTURE = 0;

extern uint8_t CFG_GLITCHLESS_LOGIC;

extern Mtx_t* write_matrix_stack_top(z64_gfx_t* gfx);
asm(".equ write_matrix_stack_top, 0x800AB900");

#define NUM_CHEST_TYPES 8
ChestType CHEST_TYPES[NUM_CHEST_TYPES] = {
    BROWN_CHEST,
    GILDED_CHEST,
    SILVER_CHEST,
    GOLD_CHEST,
    SKULL_CHEST_SMALL,
    SKULL_CHEST_BIG,
    HEART_CHEST_SMALL,
    HEART_CHEST_BIG,
};

void disallow_chest_type(bool *allowed_types, ChestType type_to_disallow) {
    switch (type_to_disallow) {
        case BROWN_CHEST: allowed_types[0] = false; break;
        case GILDED_CHEST: allowed_types[1] = false; break;
        case SILVER_CHEST: allowed_types[2] = false; break;
        case GOLD_CHEST: allowed_types[3] = false; break;
        case SKULL_CHEST_SMALL: allowed_types[4] = false; break;
        case SKULL_CHEST_BIG: allowed_types[5] = false; break;
        case HEART_CHEST_SMALL: allowed_types[6] = false; break;
        case HEART_CHEST_BIG: allowed_types[7] = false; break;
    }
}

uint8_t wrong_chest_type(uint8_t chest_type, override_key_t override_key, int16_t actor_id) {
    // Physically adjacent chests tend to have numerically adjacent override keys, which tend to yield identical random numbers. Byteswap the override key to get more variety based on the lower bits.
    uint32_t byteswapped_override_key = ((override_key.all >> 24) & 0xff) | ((override_key.all >> 8) & 0xff00) | ((override_key.all << 8) & 0xff0000) | ((override_key.all << 24) & 0xff000000);
    Seeded_Rand_Seed(RANDOMIZER_RNG_SEED ^ byteswapped_override_key);
    if (actor_id == 0x19E) { // beehive
        return chest_type == BROWN_CHEST ? GILDED_CHEST : BROWN_CHEST;
    }
    bool allowed_types[NUM_CHEST_TYPES] = {
        true, // BROWN_CHEST
        true, // GILDED_CHEST
        true, // SILVER_CHEST
        true, // GOLD_CHEST
        // Get the skull and heart chest textures from the item table to make sure they have the correct sizes for the randomizer settings.
        get_item_row(0x005B)->chest_type == SKULL_CHEST_SMALL,
        get_item_row(0x005B)->chest_type == SKULL_CHEST_BIG,
        get_item_row(0x003D)->chest_type == HEART_CHEST_SMALL,
        get_item_row(0x003D)->chest_type == HEART_CHEST_BIG,
    };
    if (CHEST_SIZE_MATCH_CONTENTS && override_key.type == OVR_CHEST) {
        // classic CSMC, treat skull/heart chests as brown or gilded depending on wincons
        disallow_chest_type(allowed_types, SKULL_CHEST_SMALL);
        disallow_chest_type(allowed_types, SKULL_CHEST_BIG);
        disallow_chest_type(allowed_types, HEART_CHEST_SMALL);
        disallow_chest_type(allowed_types, HEART_CHEST_BIG);
        switch (chest_type) {
            case BROWN_CHEST:
            case SKULL_CHEST_SMALL:
            case HEART_CHEST_SMALL:
                chest_type = BROWN_CHEST;
                break;
            case GILDED_CHEST:
            case SKULL_CHEST_BIG:
            case HEART_CHEST_BIG:
                chest_type = GILDED_CHEST;
                break;
            case SILVER_CHEST:
                chest_type = SILVER_CHEST;
                break;
            case GOLD_CHEST:
                chest_type = GOLD_CHEST;
                break;
        }
    }
    bool restricted = override_key.type == OVR_CHEST && (CHEST_SIZE_MATCH_CONTENTS || CHEST_SIZE_TEXTURE) && (
        override_key.scene == 0x0D && override_key.flag == 0x11 && !CFG_DUNGEON_IS_MQ[CASTLE_ID] // Ganons Castle Light Trial Lullaby Chest
        || override_key.scene == 0x06 && override_key.flag == 0x04 && !CFG_DUNGEON_IS_MQ[SPIRIT_ID] // Spirit Temple Compass Chest
        || override_key.scene == 0x5C && override_key.flag == 0x0B && !CFG_GLITCHLESS_LOGIC // Spirit Temple Silver Gauntlets Chest
    );
    if (restricted) {
        // chest size must change
        switch (chest_type) {
            case BROWN_CHEST:
            case SILVER_CHEST:
            case SKULL_CHEST_SMALL:
            case HEART_CHEST_SMALL:
                disallow_chest_type(allowed_types, BROWN_CHEST);
                disallow_chest_type(allowed_types, SILVER_CHEST);
                disallow_chest_type(allowed_types, SKULL_CHEST_SMALL);
                disallow_chest_type(allowed_types, HEART_CHEST_SMALL);
                break;
            case GILDED_CHEST:
            case GOLD_CHEST:
            case SKULL_CHEST_BIG:
            case HEART_CHEST_BIG:
                disallow_chest_type(allowed_types, GILDED_CHEST);
                disallow_chest_type(allowed_types, GOLD_CHEST);
                disallow_chest_type(allowed_types, SKULL_CHEST_BIG);
                disallow_chest_type(allowed_types, HEART_CHEST_BIG);
                break;
        }
    }
    // must not be the same as the original type
    disallow_chest_type(allowed_types, chest_type);
    // Pick a random chest type that's not the same as the original.
    int num_allowed_chest_types = 0;
    for (int i = 0; i < NUM_CHEST_TYPES; i++) {
        if (allowed_types[i]) {
            num_allowed_chest_types++;
        }
    }
    int random_index = Seeded_Rand_ZeroOne() * num_allowed_chest_types;
    for (int i = 0; i < NUM_CHEST_TYPES; i++) {
        if (allowed_types[i]) {
            if (i == random_index) {
                return CHEST_TYPES[i];
            }
        } else {
            random_index++;
        }
    }
}

void get_chest_override(z64_actor_t *actor) {
    Chest *chest = (Chest *)actor;
    uint8_t size = chest->en_box.type;
    uint8_t color = size;

    if (CHEST_SIZE_MATCH_CONTENTS || CHEST_SIZE_TEXTURE || CHEST_TEXTURE_MATCH_CONTENTS) {
        uint8_t scene = z64_game.scene_index;
        uint8_t item_id = (actor->variable & 0x0FE0) >> 5;

        override_t override = lookup_override(actor, scene, item_id);
        if (override.value.base.item_id != 0) {
            item_row_t *item_row = get_item_row(override.value.looks_like_item_id);
            if (item_row == NULL) {
                item_row = get_item_row(override.value.base.item_id);
            }
            uint8_t chest_type = item_row->chest_type;
            if (INCORRECT_CHEST_APPEARANCES) {
                chest_type = wrong_chest_type(chest_type, override.key, actor->actor_id);
            }
            if (CHEST_SIZE_MATCH_CONTENTS || CHEST_SIZE_TEXTURE) {
                if (chest_type == BROWN_CHEST || chest_type == SILVER_CHEST || chest_type == SKULL_CHEST_SMALL || chest_type == HEART_CHEST_SMALL) {
                    // Small chest
                    size = SMALL_CHEST;
                }
                else {
                    // Big chest
                    size = BROWN_CHEST;
                }
            }

            color = chest_type;
        }
    }

    chest->size = size;
    chest->color = color;
    if (CHEST_LENS_ONLY) {
        // Actor flag 7 makes actors invisible
        // Usually only applies to chest types 4 and 6
        actor->flags |= 0x80;
    }
}

uint8_t get_chest_type(z64_actor_t *actor)
{
    uint8_t chest_type = ((Chest *)actor)->color;
    if (CHEST_SIZE_MATCH_CONTENTS && chest_type == SILVER_CHEST)
    {
        chest_type = GOLD_CHEST;
    }

    return chest_type;
}

void set_chest_texture(z64_gfx_t *gfx, uint8_t chest_type, Gfx **opa_ptr) {
    //set texture type
    void* frontTexture = (void*)BROWN_FRONT_TEXTURE;
    void* baseTexture = (void*)BROWN_BASE_TEXTURE;

    if (CHEST_SIZE_TEXTURE || CHEST_TEXTURE_MATCH_CONTENTS) {
        switch (chest_type) {
            case GILDED_CHEST:
                frontTexture = get_texture(TEXTURE_ID_CHEST_FRONT_GILDED);
                baseTexture = get_texture(TEXTURE_ID_CHEST_BASE_GILDED);
                break;

            case SILVER_CHEST:
                frontTexture = get_texture(TEXTURE_ID_CHEST_FRONT_SILVER);
                baseTexture = get_texture(TEXTURE_ID_CHEST_BASE_SILVER);
                break;

            case SKULL_CHEST_SMALL:
            case SKULL_CHEST_BIG:
                frontTexture = get_texture(TEXTURE_ID_CHEST_FRONT_SKULL);
                baseTexture = get_texture(TEXTURE_ID_CHEST_BASE_SKULL);
                break;

            case HEART_CHEST_SMALL:
            case HEART_CHEST_BIG:
                frontTexture = get_texture(TEXTURE_ID_CHEST_FRONT_HEART);
                baseTexture = get_texture(TEXTURE_ID_CHEST_BASE_HEART);
                break;

            default:
                break;
        }
    }

    //the brown chest's base and lid dlist has been modified to jump to
    //segment 09 in order to dynamically set the chest front and base textures
    gfx->poly_opa.d -= 4;
    gDPSetTextureImage(gfx->poly_opa.d, G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, frontTexture);
    gSPEndDisplayList(gfx->poly_opa.d + 1);
    gDPSetTextureImage(gfx->poly_opa.d + 2, G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, baseTexture);
    gSPEndDisplayList(gfx->poly_opa.d + 3);

    //push custom dlist (that sets the texture) to segment 09
    gSPSegment((*opa_ptr)++, 0x09, gfx->poly_opa.d);
}

void draw_chest_base(z64_game_t *game, z64_actor_t *actor, Gfx **opa_ptr)
{
    z64_gfx_t *gfx = game->common.gfx;
    uint8_t chest_type = get_chest_type(actor);
    gSPMatrix((*opa_ptr)++, write_matrix_stack_top(gfx), G_MTX_NOPUSH | G_MTX_LOAD | G_MTX_MODELVIEW);
    if (chest_type != GOLD_CHEST)
    {
        set_chest_texture(gfx, chest_type, opa_ptr);
        gSPDisplayList((*opa_ptr)++, 0x060006F0);
    }
    else
    {
        gSPDisplayList((*opa_ptr)++, 0x06000AE8);
    }
}

void draw_chest_lid(z64_game_t *game, z64_actor_t *actor, Gfx **opa_ptr)
{
    z64_gfx_t *gfx = game->common.gfx;
    uint8_t chest_type = get_chest_type(actor);
    gSPMatrix((*opa_ptr)++, write_matrix_stack_top(gfx), G_MTX_NOPUSH | G_MTX_LOAD | G_MTX_MODELVIEW);
    if (chest_type != GOLD_CHEST)
    {
        set_chest_texture(gfx, chest_type, opa_ptr);
        gSPDisplayList((*opa_ptr)++, 0x060010C0);
    }
    else
    {
        gSPDisplayList((*opa_ptr)++, 0x06001678);
    }
}

void draw_chest(z64_game_t *game, int32_t part, void *unk, void *unk2, z64_actor_t *actor, Gfx **opa_ptr)
{
    if (part == CHEST_BASE)
    {
        draw_chest_base(game, actor, opa_ptr);
    }
    else if (part == CHEST_LID)
    {
        draw_chest_lid(game, actor, opa_ptr);
    }
}

_Bool should_draw_forest_hallway_chest(z64_actor_t *actor, z64_game_t *game)
{
    // Do not draw the chest if it is invisible, not open, and lens is not active
    if (CHEST_LENS_ONLY && !(game->chest_flags & 0x4000) && !game->actor_ctxt.lens_active)
    {
        return false;
    }

    // Vanilla code
    return (box_obj_idx(actor) > 0)
        && ((box_obj_idx(actor) = z64_ObjectIndex(&game->obj_ctxt, OBJECT_BOX)) > 0)
        && z64_ObjectIsLoaded(&game->obj_ctxt, box_obj_idx(actor));
}

void get_dummy_chest(Chest *dummy_chest)
{
    z64_actor_t dummy_actor;
    dummy_actor.actor_id = 0x000A;
    dummy_actor.variable = 0x27EE;
    dummy_chest->en_box.dyna.actor = dummy_actor;
}

void draw_forest_hallway_chest_base()
{
    // Use dummy forest hallway chest actor instance to get override
    Chest dummy_chest;
    get_dummy_chest(&dummy_chest);
    get_chest_override((z64_actor_t *)&dummy_chest);
    if (dummy_chest.size == SMALL_CHEST)
    {
        // Just scaled the matrix by 0.01 so matrix is now scaled by 0.005
        scale_sys_matrix(0.5f, 0.5f, 0.5f, 1);
    }

    draw_chest_base(&z64_game, (z64_actor_t *)&dummy_chest, &z64_game.common.gfx->poly_opa.p);
}

void draw_forest_hallway_chest_lid()
{
    // Use dummy forest hallway chest actor instance to get override
    Chest dummy_chest;
    get_dummy_chest(&dummy_chest);
    get_chest_override((z64_actor_t *)&dummy_chest);
    if (dummy_chest.size == SMALL_CHEST)
    {
        // Just scaled the matrix by 0.01 so matrix is now scaled by 0.005
        scale_sys_matrix(0.5f, 0.5f, 0.5f, 1);

        // Put lid back onto the base when open or closed
        if (z64_game.chest_flags & 0x4000) {
            // Equivalent to (-16, 7.5, 0) prior to scaling
            translate_sys_matrix(-3200.0f, 1500.0f, 0.0f, 1);
        } else {
            // Equivalent to (10.5, 13.5, 0) prior to scaling
            translate_sys_matrix(2100.0f, 2700.0f, 0.0f, 1);
        }
    }

    draw_chest_lid(&z64_game, (z64_actor_t *)&dummy_chest, &z64_game.common.gfx->poly_opa.p);
}
