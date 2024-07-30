#ifndef MODELS_H
#define MODELS_H

#include "z64.h"
#include "override.h"
#include <stdint.h>

typedef struct model_t {
    uint16_t object_id;
    uint8_t graphic_id;
} model_t;

typedef struct {
    uint16_t object_id;
    uint8_t* buf;
} loaded_object_t;


void models_init();
void models_reset();

void lookup_model_by_override(model_t* model, override_t override);
void draw_model(model_t model, z64_actor_t* actor, z64_game_t* game, float base_scale);

#endif
