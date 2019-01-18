#include "models.h"

#include "get_items.h"
#include "item_table.h"
#include "util.h"
#include "z64.h"

#define slot_count 8
#define object_size 0x1E70

typedef struct {
    uint16_t object_id;
    int8_t graphic_id;
} model_t;

typedef struct {
    uint16_t object_id;
    uint8_t *buf;
} loaded_object_t;

loaded_object_t object_slots[slot_count] = { 0 };

void load_object_file(uint32_t object_id, uint8_t *buf) {
    z64_object_table_t *entry = &(z64_object_table[object_id]);
    uint32_t vrom_start = entry->vrom_start;
    uint32_t size = entry->vrom_end - vrom_start;
    read_file(buf, vrom_start, size);
}

void load_object(loaded_object_t *object, uint32_t object_id) {
    object->object_id = object_id;
    load_object_file(object_id, object->buf);
}

loaded_object_t *get_object(uint32_t object_id) {
    for (int i = 0; i < slot_count; i++) {
        loaded_object_t *object = &(object_slots[i]);
        if (object->object_id == object_id) {
            return object;
        }
        if (object->object_id == 0) {
            load_object(object, object_id);
            return object;
        }
    }

    return NULL;
}

void set_object_segment(loaded_object_t *object) {
    z64_disp_buf_t *xlu = &(z64_ctxt.gfx->poly_xlu);
    gSPSegment(xlu->p++, 6, (uint32_t)(object->buf));

    z64_disp_buf_t *opa = &(z64_ctxt.gfx->poly_opa);
    gSPSegment(opa->p++, 6, (uint32_t)(object->buf));
}

float scale_factor(int8_t graphic_id, z64_actor_t *actor) {
    // By default, normalize model sizes to the scale that ruto's letter / fire arrows
    // are usually drawn
    float base = 0.5 / actor->scale.x;

    if (graphic_id == 0x63) {
        // Draw skull tokens at half size so they match vanilla
        return base * 0.5;
    }
    if (graphic_id == 0x2F || graphic_id == 0x46) {
        // Draw ocarinas smaller so they don't look ridiculous
        return base * 0.75;
    }
    if (actor->actor_id == 0x15 && (actor->variable & 0xFF) == 0x11) {
        // Draw small key actors smaller so they don't stick out of places
        return base * 0.75;
    }

    return base;
}

void scale_top_matrix(float scale_factor) {
    float *matrix = z64_GetMatrixStackTop();
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            matrix[4*i + j] *= scale_factor;
        }
    }
}

typedef void (*pre_draw_fn)(z64_actor_t *actor, z64_game_t *game, uint32_t unknown);
typedef void (*gi_draw_fn)(z64_game_t *game, uint32_t graphic_id_minus_1);
typedef void (*actor_draw_fn)(z64_actor_t *actor, z64_game_t *game);
#define pre_draw_1 ((pre_draw_fn)0x80022438)
#define pre_draw_2 ((pre_draw_fn)0x80022554)
#define base_draw_gi_model ((gi_draw_fn)0x800570C0)
#define base_collectable_draw ((actor_draw_fn)0x80013268)

void draw_model_by_id(int8_t graphic_id, z64_actor_t *actor, z64_game_t *game) {
    scale_top_matrix(scale_factor(graphic_id, actor));
    pre_draw_1(actor, game, 0);
    pre_draw_2(actor, game, 0);
    base_draw_gi_model(game, graphic_id - 1);
}

void draw_model(model_t model, z64_actor_t *actor, z64_game_t *game) {
    loaded_object_t *object = get_object(model.object_id);
    set_object_segment(object);
    draw_model_by_id(model.graphic_id, actor, game);
}

void models_init() {
    for (int i = 0; i < slot_count; i++) {
        object_slots[i].object_id = 0;
        object_slots[i].buf = heap_alloc(object_size);
    }
}

void models_reset() {
    for (int i = 0; i < slot_count; i++) {
        object_slots[i].object_id = 0;
    }
}

void lookup_model_by_override(model_t *model, override_t override) {
    if (override.key.all != 0) {
        uint16_t item_id = override.value.looks_like_item_id ?
            override.value.looks_like_item_id :
            override.value.item_id;
        uint16_t resolved_item_id = resolve_upgrades(item_id);
        item_row_t *item_row = get_item_row(resolved_item_id);
        model->object_id = item_row->object_id;
        model->graphic_id = item_row->graphic_id;
    }
}

void lookup_model(model_t *model, z64_actor_t *actor, z64_game_t *game, uint16_t base_item_id) {
    override_t override = lookup_override(actor, game->scene_index, base_item_id);
    lookup_model_by_override(model, override);
}

void heart_piece_draw(z64_actor_t *actor, z64_game_t *game) {
    model_t model = {
        .object_id = 0x00BD,
        .graphic_id = 0x14,
    };
    lookup_model(&model, actor, game, 0);
    draw_model(model, actor, game);
}

void small_key_draw(z64_actor_t *actor, z64_game_t *game) {
    model_t model = { 0 };
    lookup_model(&model, actor, game, 0);
    if (model.graphic_id == 0 || model.graphic_id == 0x02) {
        base_collectable_draw(actor, game);
    } else {
        draw_model(model, actor, game);
    }
}

void heart_container_draw(z64_actor_t *actor, z64_game_t *game) {
    model_t model = {
        .object_id = 0x00BD,
        .graphic_id = 0x13,
    };
    lookup_model(&model, actor, game, 0x4F);
    draw_model(model, actor, game);
}

void skull_token_draw(z64_actor_t *actor, z64_game_t *game) {
    model_t model = {
        .object_id = 0x015C,
        .graphic_id = 0x63,
    };
    lookup_model(&model, actor, game, 0);
    draw_model(model, actor, game);
}

void ocarina_of_time_draw(z64_actor_t *actor, z64_game_t *game) {
    model_t model = {
        .object_id = 0x00DE,
        .graphic_id = 0x2F,
    };
    lookup_model(&model, actor, game, 0x0C);
    draw_model(model, actor, game);
}

void item_etcetera_draw(z64_actor_t *actor, z64_game_t *game) {
    override_t override = { 0 };
    if (actor->variable == 0x01) {
        // Ruto's letter
        override = lookup_override(actor, game->scene_index, 0x15);
    } else if (actor->variable == 0x07) {
        // Fire Arrow
        override = lookup_override(actor, game->scene_index, 0x58);
    } else if (actor->variable == 0x0A0C) {
        // Treasure chest game heart piece inside chest
        override_key_t key = {
            .scene = 0x10,
            .type = OVR_CHEST,
            .flag = 0x0A,
        };
        override = lookup_override_by_key(key);
    }

    model_t model = { 0 };
    lookup_model_by_override(&model, override);
    if (model.object_id != 0) {
        draw_model(model, actor, game);
    } else {
        uint8_t default_graphic_id = *(((uint8_t *)actor) + 0x141);
        draw_model_by_id(default_graphic_id, actor, game);
    }
}

void bowling_bomb_bag_draw(z64_actor_t *actor, z64_game_t *game) {
    override_t override = { 0 };
    if (actor->variable == 0x00 || actor->variable == 0x05) {
        override = lookup_override(actor, game->scene_index, 0x34);
    }

    model_t model = { 0 };
    lookup_model_by_override(&model, override);
    if (model.object_id != 0) {
        draw_model(model, actor, game);
    } else {
        uint8_t default_graphic_id = *(((uint8_t *)actor) + 0x147);
        draw_model_by_id(default_graphic_id, actor, game);
    }
}

void bowling_heart_piece_draw(z64_actor_t *actor, z64_game_t *game) {
    model_t model = {
        .object_id = 0x00BD,
        .graphic_id = 0x14,
    };
    lookup_model(&model, actor, game, 0x3E);
    draw_model(model, actor, game);
}
