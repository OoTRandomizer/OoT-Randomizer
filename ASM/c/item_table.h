#ifndef ITEM_TABLE_H
#define ITEM_TABLE_H

#include <stdbool.h>

#include "get_items.h"
#include "z64.h"

typedef enum {
    /*  0 */ BROWN_CHEST,            // big default chest
    /*  1 */ BIG_ROOM_CLEAR_CHEST,   // appear on room clear, store temp clear as permanent clear
    /*  2 */ GOLD_CHEST,             // boss key chest, different look, same as BROWN_CHEST otherwise
    /*  3 */ BIG_FALLING_CHEST,      // falling, appear on switch flag set
    /*  4 */ TYPE_4_CHEST,           // big, drawn differently
    /*  5 */ SMALL_CHEST,            // same as BROWN_CHEST but small
    /*  6 */ TYPE_6_CHEST,           // small, drawn differently
    /*  7 */ SMALL_ROOM_CLEAR_CHEST, // use room clear, store temp clear as perm clear
    /*  8 */ SMALL_FALLING_CHEST,    // falling, appear on switch flag set
    /*  9 */ TYPE_9_CHEST,           // big, has something more to do with player and message context?
    /* 10 */ TYPE_10_CHEST,          // like 9
    /* 11 */ BIG_SWITCH_FLAG_CHEST,  // big, appear on switch flag set
    /* 12 */ GILDED_CHEST,
    /* 13 */ SILVER_CHEST,
    /* 14 */ SKULL_CHEST_SMALL,
    /* 15 */ SKULL_CHEST_BIG,
    /* 16 */ HEART_CHEST_SMALL,
    /* 17 */ HEART_CHEST_BIG,
} ChestType;

struct item_row_t;

typedef uint16_t (*upgrade_fn)(z64_file_t* save, override_t override);
typedef void (*effect_fn)(z64_file_t* save, int16_t arg1, int16_t arg2);
typedef uint16_t (*alt_text_fn)(struct item_row_t* this, bool is_outgoing);

typedef struct item_row_t {
    int8_t      base_item_id;
    uint8_t     action_id;
    uint16_t    text_id;
    uint16_t    object_id;
    uint8_t     graphic_id;
    uint8_t     chest_type;
    upgrade_fn  upgrade;
    effect_fn   effect;
    int16_t     effect_arg1;
    int16_t     effect_arg2;
    int8_t      collectible;
    alt_text_fn alt_text_func;
} item_row_t;

uint16_t resolve_upgrades(override_t override);
item_row_t* get_item_row(uint16_t item_id);
void call_effect_function(item_row_t* item_row);
uint16_t resolve_item_text_id(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_silver_rupees(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_silver_rupee_pouches(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_small_keys(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_small_keys_cmg(item_row_t* item_row, bool is_outgoing);
uint16_t resolve_text_keyrings(item_row_t* item_row, bool is_outgoing);

#endif
