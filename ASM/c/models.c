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

typedef void (*draw_fn)(z64_game_t *game, uint32_t graphic_id_minus_1);
#define base_draw_gi_model ((draw_fn)0x800570C0)

void draw_model(model_t model, z64_game_t *game) {
    loaded_object_t *object = get_object(model.object_id);
    set_object_segment(object);
    base_draw_gi_model(game, model.graphic_id - 1);
}

void scale_matrix(float *matrix, float scale_factor) {
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            matrix[4*i + j] *= scale_factor;
        }
    }
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

void lookup_model(model_t *model, z64_game_t *game, z64_actor_t *actor, uint16_t base_item_id) {
    override_t override = lookup_override(actor, game->scene_index, base_item_id);
    lookup_model_by_override(model, override);
}

typedef void (*default_draw_fn)(z64_actor_t *actor, z64_game_t *game);
typedef void (*pre_draw_fn)(z64_actor_t *actor, z64_game_t *game, uint32_t unknown);

#define default_heart_draw ((default_draw_fn)0x80013498)
#define pre_draw_1 ((pre_draw_fn)0x80022438)
#define pre_draw_2 ((pre_draw_fn)0x80022554)
#define matrix_stack_pointer ((float **)0x80121204)

void heart_piece_draw(z64_actor_t *heart_piece_actor, z64_game_t *game) {
    pre_draw_1(heart_piece_actor, game, 0);
    pre_draw_2(heart_piece_actor, game, 0);
    scale_matrix(*matrix_stack_pointer, 24.0);

    model_t model = {
        .object_id = 0x00BD,
        .graphic_id = 0x14,
    };
    lookup_model(&model, game, heart_piece_actor, 0x3E);
    draw_model(model, game);
}

void heart_container_draw(z64_actor_t *heart_container_actor, z64_game_t *game) {
    model_t model = {
        .object_id = 0x00BD,
        .graphic_id = 0x13,
    };
    lookup_model(&model, game, heart_container_actor, 0x4F);
    draw_model(model, game);
}

void skull_token_draw(z64_actor_t *token_actor, z64_game_t *game) {
    model_t model = {
        .object_id = 0x015C,
        .graphic_id = 0x63,
    };
    lookup_model(&model, game, token_actor, 0x5B);
    draw_model(model, game);
}

void ocarina_of_time_draw(z64_actor_t *ocarina_actor, z64_game_t *game) {
    model_t model = {
        .object_id = 0x00DE,
        .graphic_id = 0x2F,
    };
    lookup_model(&model, game, ocarina_actor, 0x0C);
    draw_model(model, game);
}

void item_etcetera_draw(z64_actor_t *item_actor, z64_game_t *game) {
    override_t override = { 0 };
    if (item_actor->variable == 0x01) {
        // Ruto's letter
        override = lookup_override(item_actor, game->scene_index, 0x15);
    } else if (item_actor->variable == 0x07) {
        // Fire Arrow
        override = lookup_override(item_actor, game->scene_index, 0x58);
    } else if (item_actor->variable == 0x0A0C) {
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
        draw_model(model, game);
    } else {
        uint8_t default_graphic_id = *(((uint8_t *)item_actor) + 0x141);
        base_draw_gi_model(game, default_graphic_id);
    }
}

void bowling_bomb_bag_draw(z64_actor_t *prize_actor, z64_game_t *game) {
    override_t override = { 0 };
    if (prize_actor->variable == 0x00 || prize_actor->variable == 0x05) {
        override = lookup_override(prize_actor, game->scene_index, 0x34);
    }

    model_t model = { 0 };
    lookup_model_by_override(&model, override);
    if (model.object_id != 0) {
        draw_model(model, game);
    } else {
        uint8_t default_graphic_id = *(((uint8_t *)prize_actor) + 0x147);
        base_draw_gi_model(game, default_graphic_id);
    }
}

void bowling_heart_piece_draw(z64_actor_t *prize_actor, z64_game_t *game) {
    model_t model = {
        .object_id = 0x00BD,
        .graphic_id = 0x14,
    };
    lookup_model(&model, game, prize_actor, 0x3E);
    draw_model(model, game);
}

typedef void (*actor_constructor_fn)(z64_actor_t *actor, z64_game_t *game);
#define default_item00_constructor ((actor_constructor_fn)0x80011B4C)

void item00_constructor(z64_actor_t *actor, z64_game_t *game) {
    // Constructor for En_Item00 (free standing heart piece / key)
    uint16_t var = actor->variable;
    if ((var & 0x00FF) == 0x11) {
        // Free standing small key
        override_key_t key = { 0 };
        key.scene = game->scene_index;
        key.type = OVR_COLLECTABLE;
        key.flag = var >> 8;
        override_t override = lookup_override_by_key(key);
        if (override.key.all != 0) {
            // Construct a piece of heart instead
            actor->variable = (var & 0xFF00) | 0x06;
        }
    }
    default_item00_constructor(actor, game);
}
