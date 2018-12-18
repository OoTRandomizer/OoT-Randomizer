#include "models.h"

#include "get_items.h"
#include "item_table.h"
#include "util.h"
#include "z64.h"

#define slot_count 8
#define object_size 0x1E70

extern uint8_t SHOW_CORRECT_FREESTANDING_MODELS;

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

typedef void (*default_draw_fn)(z64_actor_t *actor, z64_game_t *game);
typedef void (*pre_draw_fn)(z64_actor_t *actor, z64_game_t *game, uint32_t unknown);
typedef void (*draw_fn)(z64_game_t *game, uint32_t gi_id_minus_1);

#define default_heart_draw ((default_draw_fn)0x80013498)
#define pre_draw_1 ((pre_draw_fn)0x80022438)
#define pre_draw_2 ((pre_draw_fn)0x80022554)
#define draw_model ((draw_fn)0x800570C0)

#define matrix_stack_pointer ((float **)0x80121204)

void models_draw(z64_actor_t *heart_piece_actor, z64_game_t *game) {
    override_t override = lookup_override(heart_piece_actor, game->scene_index, 0x3E);
    uint16_t object_id;
    int8_t graphic_id;
    if (override.key.all == 0) {
        object_id = 0x00BD;
        graphic_id = 0x14;
    } else {
        uint16_t item_id = resolve_upgrades(override.value.item_id);
        item_row_t *item_row = get_item_row(item_id);
        object_id = item_row->object_id;
        graphic_id = item_row->graphic_id;
    }
    if(SHOW_CORRECT_FREESTANDING_MODELS==0){
        default_heart_draw(heart_piece_actor, game);
        return;
    }
    loaded_object_t *object = get_object(object_id);
    pre_draw_1(heart_piece_actor, game, 0);
    pre_draw_2(heart_piece_actor, game, 0);
    set_object_segment(object);
    scale_matrix(*matrix_stack_pointer, 24.0);
    draw_model(game, graphic_id - 1);       
}

typedef void (*actor_constructor_fn)(z64_actor_t *actor, z64_game_t *game);
#define default_item00_constructor ((actor_constructor_fn)0x80011B4C)

void item00_constructor(z64_actor_t *actor, z64_game_t *game) {
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
