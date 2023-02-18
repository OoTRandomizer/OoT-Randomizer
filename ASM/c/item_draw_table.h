#ifndef ITEM_DRAW_TABLE_H
#define ITEM_DRAW_TABLE_H

#include "z64.h"
#include "color.h"

typedef union {
    uint32_t        dlist;
    colorRGBA8_t    color;
} item_draw_arg_t;

typedef struct {
    void            (*draw_func)(z64_game_t *game, uint32_t draw_id);
    item_draw_arg_t args[8];
} item_draw_table_entry_t;

extern item_draw_table_entry_t item_draw_table[];

void base_draw_gi_model(z64_game_t *game, uint32_t draw_id);

#endif
