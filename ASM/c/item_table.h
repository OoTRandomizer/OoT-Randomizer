#ifndef ITEM_TABLE_H
#define ITEM_TABLE_H

#include "z64.h"

#define BROWN_CHEST 0
#define GOLD_CHEST 2
#define GILDED_CHEST 12
#define SILVER_CHEST 13
#define SKULL_CHEST_SMALL 14
#define SKULL_CHEST_BIG 15

typedef uint16_t (*upgrade_fn)(z64_file_t *save, uint16_t item_id);
typedef void (*effect_fn)(z64_file_t *save, int16_t arg1, int16_t arg2);

typedef struct {
    int8_t      base_item_id;
    uint8_t     action_id;
    uint16_t    text_id;

    uint16_t    object_id;
    int8_t      graphic_id;
    uint8_t     chest_type;

    upgrade_fn  upgrade;

    effect_fn   effect;
    int16_t     effect_arg1;
    int16_t     effect_arg2;
} item_row_t;

uint16_t resolve_upgrades(uint16_t item_id);
item_row_t *get_item_row(uint16_t item_id);
void call_effect_function(item_row_t *item_row);

#endif
