#include "file_icons.h"

#include "color.h"
#include "hud_colors.h"
#include "triforce.h"
#include "ocarina_buttons.h"

#define ICON_SIZE    0x0C
#define MUSIC_WIDTH  0x06
#define MUSIC_HEIGHT 0x0A
#define BUTTON_WIDTH  0x09
#define BUTTON_HEIGHT 0x09

#define NUM_ICON_SPRITES 3
sprite_t* const icon_sprites[NUM_ICON_SPRITES] = {
    &items_sprite,
    &quest_items_sprite,
    &linkhead_skull_sprite
};


#define LEFT_OFFSET (int)0x37
#define TOP_OFFSET  (int)0x5C
typedef struct {
    uint8_t left;
    int8_t  top;
} tile_position;


static int get_left(tile_position pos) {
    return LEFT_OFFSET + (int)pos.left;
}


static int get_top(tile_position pos) {
    return TOP_OFFSET + (int)pos.top;
}


static const colorRGBA8_t WHITE = {0xFF, 0xFF, 0xFF, 0xFF};
static const colorRGBA8_t DIM   = {0x40, 0x40, 0x40, 0x90};
static int hasTriforceGoalBeenReached = 0;

// Approximate product of two colors. Result is within 1 of true product.
static uint8_t color_product(uint8_t c1, uint8_t c2) {
    uint16_t prod = (uint16_t)c1 * (uint16_t)c2;
    uint16_t div255 = (prod + 1 + (prod >> 8)) >> 8;
    return (uint8_t)div255;
}

static void draw_square_sprite(z64_disp_buf_t* db, sprite_t* sprite, int tile_index, tile_position pos, int size) {
    sprite_load(db, sprite, tile_index, 1);
    sprite_draw(db, sprite, 0, get_left(pos), get_top(pos), size, size);
}


/*=============================================================================
There are four types of tiles on the icon panel:
    1. Fixed tiles
        These tiles have a fixed image that is either dimmed out or displayed
        with full color. They can come from any sprite but must be a format
        with RGB data. Their lookup table consumes four bytes per tile
        (sprite, index, left, top) and one bit is used for their file data
        (dim or bright).
    2. Variable tiles
        These tiles can display any image from a fixed sprite table, either
        dimmed or bright. Their lookup table consumes three bytes per tile
        (sprite, left, top) and two bytes are used for file data (dim/bright,
        index).
    3. Music tiles
        These tiles display a music note with a variable color and can be
        dim or bright. Their lookup table uses five bytes per tile (color,
        left, top) and they use one bit for file data (dim/bright).
    4. Counter tiles
        These tiles are handled on a case-by-case basis, but generally
        display some kind of count beneath their icon.
=============================================================================*/

/*=============================================================================
Position Tables
=============================================================================*/

typedef struct {
    uint8_t sprite : 3;
    uint8_t size   : 5; // 0 for "not shown"
    uint8_t tile_index;
    tile_position pos;
} fixed_tile_data_t;

#define FIXED_BITS_PER_WORD 32
#define NUM_FIXED_WORDS 2
static fixed_tile_data_t fixed_tile_positions[NUM_FIXED_WORDS*FIXED_BITS_PER_WORD] = {
    {0, ICON_SIZE,   Z64_ITEM_STICK,            {0x4E, 0x00}}, // 0:0
    {0, ICON_SIZE,   Z64_ITEM_NUT,              {0x5A, 0x00}}, // 0:1
    {0, ICON_SIZE,   Z64_ITEM_BOMB,             {0x66, 0x00}}, // 0:2
    {0, ICON_SIZE,   Z64_ITEM_BOW,              {0x72, 0x00}}, // 0:3
    {0, ICON_SIZE,   Z64_ITEM_FIRE_ARROW,       {0x7E, 0x00}}, // 0:4
    {0, ICON_SIZE,   Z64_ITEM_DINS_FIRE,        {0x8A, 0x00}}, // 0:5
    {0, ICON_SIZE,   Z64_ITEM_SLINGSHOT,        {0x4E, 0x0C}}, // 0:6
    {0, 0,           Z64_ITEM_FAIRY_OCARINA,    {0x5A, 0x0C}}, // 0:7
    {0, ICON_SIZE,   Z64_ITEM_BOMBCHU,          {0x66, 0x0C}}, // 1:0
    {0, 0,           Z64_ITEM_HOOKSHOT,         {0x72, 0x0C}}, // 1:1
    {0, ICON_SIZE,   Z64_ITEM_ICE_ARROW,        {0x7E, 0x0C}}, // 1:2
    {0, ICON_SIZE,   Z64_ITEM_FARORES_WIND,     {0x8A, 0x0C}}, // 1:3
    {0, ICON_SIZE,   Z64_ITEM_BOOMERANG,        {0x4E, 0x18}}, // 1:4
    {0, ICON_SIZE,   Z64_ITEM_LENS,             {0x5A, 0x18}}, // 1:5
    {0, ICON_SIZE,   Z64_ITEM_BEANS,            {0x66, 0x18}}, // 1:6
    {0, ICON_SIZE,   Z64_ITEM_HAMMER,           {0x72, 0x18}}, // 1:7
    {0, ICON_SIZE,   Z64_ITEM_LIGHT_ARROW,      {0x7E, 0x18}}, // 2:0
    {0, ICON_SIZE,   Z64_ITEM_NAYRUS_LOVE,      {0x8A, 0x18}}, // 2:1
    {0, 0,           0,                         {0xFF, 0xFF}}, // 2:2
    {0, 0,           0,                         {0xFF, 0xFF}}, // 2:3
    {0, 0,           0,                         {0xFF, 0xFF}}, // 2:4
    {0, 0,           0,                         {0xFF, 0xFF}}, // 2:5
    {0, 0,           0,                         {0xFF, 0xFF}}, // 2:6
    {0, 0,           0,                         {0xFF, 0xFF}}, // 2:7
    {0, 0,           0,                         {0xFF, 0xFF}}, // 3:0
    {0, 0,           0,                         {0xFF, 0xFF}}, // 3:1
    {0, 0,           0,                         {0xFF, 0xFF}}, // 3:2
    {0, 0,           0,                         {0xFF, 0xFF}}, // 3:3
    {0, 0,           0,                         {0xFF, 0xFF}}, // 3:4
    {0, 0,           0,                         {0xFF, 0xFF}}, // 3:5
    {0, 0,           0,                         {0xFF, 0xFF}}, // 3:6
    {0, 0,           0,                         {0xFF, 0xFF}}, // 3:7

    {0, ICON_SIZE,   Z64_ITEM_KOKIRI_SWORD,     {0x7E, 0x2A}}, // 4:0
    {0, ICON_SIZE,   Z64_ITEM_MASTER_SWORD,     {0x8A, 0x2A}}, // 4:1
    {0, ICON_SIZE,   Z64_ITEM_BIGGORON_SWORD,   {0x96, 0x2A}}, // 4:2
    {0, 0,           0,                         {0xFF, 0xFF}}, // 4:3
    {0, ICON_SIZE,   Z64_ITEM_DEKU_SHIELD,      {0x7E, 0x36}}, // 4:4
    {0, ICON_SIZE-1, Z64_ITEM_HYLIAN_SHIELD,    {0x8B, 0x37}}, // 4:5
    {0, ICON_SIZE-1, Z64_ITEM_MIRROR_SHIELD,    {0x97, 0x37}}, // 4:6
    {0, 0,           0,                         {0xFF, 0xFF}}, // 4:7
    {0, ICON_SIZE,   Z64_ITEM_KOKIRI_TUNIC,     {0x7E, 0x42}}, // 5:0
    {0, ICON_SIZE,   Z64_ITEM_GORON_TUNIC,      {0x8A, 0x42}}, // 5:1
    {0, ICON_SIZE,   Z64_ITEM_ZORA_TUNIC,       {0x96, 0x42}}, // 5:2
    {0, 0,           0,                         {0xFF, 0xFF}}, // 5:3
    {0, ICON_SIZE,   Z64_ITEM_KOKIRI_BOOTS,     {0x7E, 0x4F}}, // 5:4
    {0, ICON_SIZE,   Z64_ITEM_IRON_BOOTS,       {0x8A, 0x4F}}, // 5:5
    {0, ICON_SIZE,   Z64_ITEM_HOVER_BOOTS,      {0x96, 0x4F}}, // 5:6
    {0, 0,           0,                         {0xFF, 0xFF}}, // 5:7
    {0, ICON_SIZE,   Z64_ITEM_BOTTLE,           {0x96, 0x00}}, // 6:0
    {0, 0,           0,                         {0xFF, 0xFF}}, // 6:1
    {1, ICON_SIZE,   6 /* Emerald (top) */,     {0x1B, 0x31}}, // 6:2
    {1, ICON_SIZE,   7 /* Ruby (left) */,       {0x29, 0x31}}, // 6:3
    {1, ICON_SIZE,   8 /* Sapphire (right) */,  {0x37, 0x31}}, // 6:4
    {1, 0x0A,        9 /* Stone of Agony */,    {0x6F, 0x51}}, // 6:5
    {1, ICON_SIZE,  10 /* Gerudo's Card */,     {0x72, 0x2A}}, // 6:6
    {0, 0,           0,                         {0xFF, 0xFF}}, // 6:7
    {1, ICON_SIZE,   0 /* Forest Med. (UR) */,  {0x37, 0x0A}}, // 7:0
    {1, ICON_SIZE,   1 /* Fire Med. (LR) */,    {0x37, 0x1A}}, // 7:1
    {1, ICON_SIZE,   2 /* Water Med. (btm) */,  {0x29, 0x22}}, // 7:2
    {1, ICON_SIZE,   3 /* Spirit Med. (LL) */,  {0x1B, 0x1A}}, // 7:3
    {1, ICON_SIZE,   4 /* Shadow Med. (UL) */,  {0x1B, 0x0A}}, // 7:4
    {1, ICON_SIZE,   5 /* Light Med. (top) */,  {0x29, 0x02}}, // 7:5
    {0, 0,           0,                         {0xFF, 0xFF}}, // 7:6
    {0, 0,           0,                         {0xFF, 0xFF}}, // 7:7
};

typedef struct {
    uint8_t sprite;
    tile_position pos;
} variable_tile_data_t;

#define NUM_VARIABLE 7
static const variable_tile_data_t variable_tile_positions[NUM_VARIABLE] = {
    {0, {0x5A, 0x0C}}, // Fairy Ocarina
    {0, {0x72, 0x0C}}, // Hookshot
    {0, {0x96, 0x0C}}, // Child Trade
    {0, {0x96, 0x18}}, // Adult Trade
    {1, {0x65, 0x2A}}, // Magic
    {0, {0x4E, 0x2A}}, // Strength
    {0, {0x5A, 0x2A}}, // Scale
};

typedef struct {
    colorRGB8_t color;
    tile_position pos;
} music_tile_data_t;

#define NUM_SONGS 12
#define SONG_SHIFT 6
static const music_tile_data_t song_note_data[NUM_SONGS] = {
    {{0x97, 0xFF, 0x63}, {0x50, 0x45}}, // Minuet of forest
    {{0xFF, 0x50, 0x28}, {0x57, 0x45}}, // Bolero of fire
    {{0x63, 0x97, 0xFF}, {0x5E, 0x45}}, // Serenade of water
    {{0xFF, 0x9F, 0x00}, {0x65, 0x45}}, // Requiem of spirit
    {{0xFF, 0x63, 0xFF}, {0x6C, 0x45}}, // Nocturne of shadow
    {{0xFF, 0xF0, 0x63}, {0x73, 0x45}}, // Prelude of light
    {{0xFF, 0xFF, 0xFF}, {0x50, 0x3A}}, // Zelda's lullaby
    {{0xFF, 0xFF, 0xFF}, {0x57, 0x3A}}, // Epona's song
    {{0xFF, 0xFF, 0xFF}, {0x5E, 0x3A}}, // Saria's song
    {{0xFF, 0xFF, 0xFF}, {0x65, 0x3A}}, // Sun's song
    {{0xFF, 0xFF, 0xFF}, {0x6C, 0x3A}}, // Song of time
    {{0xFF, 0xFF, 0xFF}, {0x73, 0x3A}}  // Song of storms
};

typedef struct {
    colorRGB8_t color;
    tile_position pos;
} button_tile_data_t;

#define NUM_BUTTONS 5
static const button_tile_data_t button_note_data[NUM_BUTTONS] = {
    {{0x00, 0x00, 0xFF}, {0x4E, 0x51}}, // A
    {{0xF4, 0xEC, 0x30}, {0x57, 0x51}}, // C down
    {{0xF4, 0xEC, 0x30}, {0x60, 0x51}}, // C right
    {{0xF4, 0xEC, 0x30}, {0x69, 0x51}}, // C left
    {{0xF4, 0xEC, 0x30}, {0x72, 0x51}}, // C up
};

#define NUM_COUNTER 6
#define COUNTER_ICON_SIZE 0x10

typedef enum {
    SLOT_HEARTS = 0,
    SLOT_RUPEES,
    SLOT_SKULLTULLAS,
    SLOT_TRIFORCE_CURRENT,
    SLOT_TRIFORCE_TOTAL,
    SLOT_DEATHS,
} counter_slot_t;

typedef struct {
    tile_position pos;
    int8_t counter_hoffset;
    int8_t counter_voffset;
    uint8_t align_center;
} counter_tile_data_t;

static counter_tile_data_t counter_positions[NUM_COUNTER] = {
    {{0x05, 0x00}, COUNTER_ICON_SIZE/2, 13, 1}, // Hearts
    {{0x05, 0x15}, COUNTER_ICON_SIZE/2, 13, 1}, // Rupees
    {{0x05, 0x2A}, COUNTER_ICON_SIZE/2, 13, 1}, // Skulltulas
    {{0x27, 0x27}, 3, 16, 0},  // Current Triforce Pieces
    {{0x33, 0x27}, 0, 16, 0},   // Total Triforce Pieces
    {{0x4D, 0x51}, 11,                   2, 0}, // Deaths
};


/*=============================================================================
File Data
=============================================================================*/

typedef union {
    uint32_t bits[NUM_FIXED_WORDS];
    struct {
        uint32_t inventory_bits; // word 0
        uint8_t  medallion_bits; // word 1 HI-3
        uint8_t  other_bits;     // word 1 HI-2
        uint16_t equipment_bits; // word 1 LO
    };
} fixed_tile_info_t;

typedef struct {
    uint8_t enabled;
    uint8_t tile_index;
} variable_tile_t;

typedef struct {
    variable_tile_t tiles[NUM_VARIABLE];
} variable_tile_info_t;

typedef struct {
    uint16_t bits;
} music_tile_info_t;

typedef struct {
    uint16_t bits;
} button_tile_info_t;

typedef uint8_t digits_t[3];

typedef struct {
    uint8_t wallet;
    uint8_t double_defense;
    digits_t digits[NUM_COUNTER];
} counter_tile_info_t;

typedef struct {
    fixed_tile_info_t fixed;
    variable_tile_info_t variable;
    counter_tile_info_t counters;
    music_tile_info_t songs;
    button_tile_info_t buttons;
} file_info_t;

// File data structure
static file_info_t draw_data;


/*=============================================================================
Data population functions
=============================================================================*/

static void change_meds_and_stones_tiles_for_triforce_hunt(fixed_tile_data_t* fixed_tile_original) {
    tile_position emerald_pos = {0x1A, 0x25};
    fixed_tile_original[50].pos = emerald_pos;
    tile_position ruby_pos = {0x29, 0x1A};
    fixed_tile_original[51].pos = ruby_pos;
    tile_position saphire_pos = {0x38, 0x25};
    fixed_tile_original[52].pos = saphire_pos;
    tile_position forest_med_pos = {0x1B, 0x00};
    fixed_tile_original[56].pos = forest_med_pos;
    tile_position fire_med_pos = {0x29, 0x00};
    fixed_tile_original[57].pos = fire_med_pos;
    tile_position water_med_pos = {0x37, 0x00};
    fixed_tile_original[58].pos = water_med_pos;
    tile_position shadow_med_pos = {0x29, 0x0C};
    fixed_tile_original[60].pos = shadow_med_pos;
    tile_position spirit_med_pos = {0x1B, 0x0C};
    fixed_tile_original[59].pos = spirit_med_pos;
    tile_position light_med_pos = {0x37, 0x0C};
    fixed_tile_original[61].pos = light_med_pos;
}

static void push_down_death_counter_and_soa_for_ocarina_button_shuffle(fixed_tile_data_t* fixed_tile_original,
                                                                        counter_tile_data_t* counter_data_original) {
    tile_position soa_pos = {0x6F, 0x5C};
    fixed_tile_original[53].pos = soa_pos;
    tile_position death_pos = {0x4D, 0x5C};
    counter_data_original[5].pos = death_pos;
}

// Populate fixed tiles
#define NUM_NORMAL_INVENTORY_SLOTS 18
static void populate_fixed(const z64_file_t* file, fixed_tile_info_t* info) {
    // inventory (excluding bottles and trade items)
    uint32_t inv = 0;
    uint32_t mask = 0x1;
    fixed_tile_data_t* inv_data = fixed_tile_positions;
    counter_tile_data_t* counter_data = counter_positions;
    if (TRIFORCE_HUNT_ENABLED) {
        change_meds_and_stones_tiles_for_triforce_hunt(inv_data);
    }
    if (SHUFFLE_OCARINA_BUTTONS) {
        push_down_death_counter_and_soa_for_ocarina_button_shuffle(inv_data, counter_data);
    }
    for (int i = 0; i < NUM_NORMAL_INVENTORY_SLOTS; ++i) {
        uint8_t item = file->items[i];
        if (inv_data->sprite == 0 && item == inv_data->tile_index) {
            inv |= mask;
        }
        ++inv_data;
        mask <<= 1;
    }
    info->inventory_bits = inv;

    // medallions
    info->medallion_bits = (uint8_t)(file->quest_items & 0x0000003F);

    // equipment
    uint16_t equipment = file->equipment;

    // special handling of Biggoron Sword (need to check flag)
    equipment &= 0xFFFB;
    if (file->bgs_flag) {
        equipment |= 0x0004;
    }
    info->equipment_bits = equipment;

    // other
    uint8_t other = (uint8_t)((file->quest_items & 0x007C0000) >> 16);

    for (uint8_t slot = Z64_SLOT_BOTTLE_1; slot <= Z64_SLOT_BOTTLE_4; ++slot) {
        uint8_t item = file->items[slot];
        if (Z64_ITEM_BOTTLE <= item && item <= Z64_ITEM_POE && item != Z64_ITEM_LETTER) {
            // bottle
            other |= (0x01 << 0);
        }
    }
    info->other_bits = other;
}


// Populate variable tiles
static void populate_upgrade_item(const z64_file_t* file, variable_tile_t* tile, uint8_t slot, uint8_t base_item);
static const uint8_t MASK_LOOKUP[16];
static void populate_child_trade(const z64_file_t* file, variable_tile_t* tile);
static void populate_adult_trade(const z64_file_t* file, variable_tile_t* tile);
static void populate_magic(const z64_file_t* file, variable_tile_t* tile);
static void populate_upgrade_equip(const z64_file_t* file, variable_tile_t* tile, uint8_t value, uint8_t max, uint8_t base_tile);

static void populate_variable(const z64_file_t* file, variable_tile_info_t* info) {
    variable_tile_t* tile = info->tiles;

    populate_upgrade_item( file, tile++, Z64_SLOT_OCARINA, Z64_ITEM_FAIRY_OCARINA);
    populate_upgrade_item( file, tile++, Z64_SLOT_HOOKSHOT, Z64_ITEM_HOOKSHOT);
    populate_child_trade(  file, tile++);
    populate_adult_trade(  file, tile++);
    populate_magic(        file, tile++);
    populate_upgrade_equip(file, tile++, file->strength_upgrade, 3, Z64_ITEM_GORONS_BRACELET);
    populate_upgrade_equip(file, tile++, file->diving_upgrade,   2, Z64_ITEM_SILVER_SCALE);
}


// Populate music tiles
static void populate_songs(const z64_file_t* file, music_tile_info_t* songs) {
    songs->bits = (uint16_t)((file->quest_items >> SONG_SHIFT) & 0x0FFF);
}

// Populate button titles
static void populate_buttons(const z64_file_t* file, button_tile_info_t* buttons) {
    buttons->bits = 0;
    if (file->scene_flags[0x50].unk_00_ & 1 << 0) { // A
       buttons->bits |= 1 << 0;
    }
    if (file->scene_flags[0x50].unk_00_ & 1 << 2) { // C Down
       buttons->bits |= 1 << 1;
    }
    if (file->scene_flags[0x50].unk_00_ & 1 << 4) { // C right
       buttons->bits |= 1 << 2;
    }
    if (file->scene_flags[0x50].unk_00_ & 1 << 3) { // C left
       buttons->bits |= 1 << 3;
    }
    if (file->scene_flags[0x50].unk_00_ & 1 << 1) { // C up
       buttons->bits |= 1 << 4;
    }
}


// Populate counter tiles
static void make_digits(uint8_t* digits, int16_t value);

static void populate_counts(const z64_file_t* file, counter_tile_info_t* counts) {

    // Rupees
    counts->wallet = file->wallet;
    make_digits(counts->digits[SLOT_RUPEES], (int16_t)file->rupees);

    // Skulltulas
    uint8_t draw_tullas = file->gold_skulltula != 0;
    make_digits(counts->digits[SLOT_SKULLTULLAS], draw_tullas ? file->gs_tokens : 0);

    // Triforce or Boss Key
    int16_t num_triforce_pieces = (int16_t)file->scene_flags[0x48].unk_00_;
    make_digits(counts->digits[SLOT_TRIFORCE_CURRENT], TRIFORCE_HUNT_ENABLED ? num_triforce_pieces : -1);
    int16_t total_triforce_pieces = TRIFORCE_PIECES_REQUIRED;
    make_digits(counts->digits[SLOT_TRIFORCE_TOTAL], TRIFORCE_HUNT_ENABLED ? total_triforce_pieces : -1);
    hasTriforceGoalBeenReached = num_triforce_pieces >= total_triforce_pieces;

    // Hearts
    counts->double_defense = (uint8_t)file->double_defense;
    make_digits(counts->digits[SLOT_HEARTS], file->energy_capacity / 0x10);

    // Deaths
    make_digits(counts->digits[SLOT_DEATHS], file->deaths);
}


// Main population function
void read_file_data(const z64_file_t* file) {
    populate_fixed(file, &draw_data.fixed);
    populate_variable(file, &draw_data.variable);
    populate_counts(file, &draw_data.counters);
    populate_songs(file, &draw_data.songs);
    populate_buttons(file, &draw_data.buttons);
}


/*=============================================================================
Drawing functions
=============================================================================*/

// Draw fixed tiles
static void draw_fixed(z64_disp_buf_t* db, const fixed_tile_info_t* info, uint8_t alpha) {
    colorRGBA8_t color = DIM;
    color.a = color_product(color.a, alpha);

    // Draw all dimmed first, then all bright
    for (uint8_t enabled = 0; enabled <= 1; ++enabled) {
        gDPSetPrimColor(db->p++, 0, 0, color.r, color.g, color.b, color.a);

        fixed_tile_data_t* data = fixed_tile_positions;
        if (TRIFORCE_HUNT_ENABLED) {
            change_meds_and_stones_tiles_for_triforce_hunt(data);
        }

        // Read one bit at a time, from least significant to most significant
        for (int i = 0; i < NUM_FIXED_WORDS; ++i) {
            uint32_t word = info->bits[i];
            for (int j = 0; j < FIXED_BITS_PER_WORD; ++j) {
                if (data->size > 0 && (word & 0x1) == enabled) {
                    sprite_t* sprite = icon_sprites[data->sprite];
                    draw_square_sprite(db, icon_sprites[data->sprite], data->tile_index, data->pos, data->size);
                }
                word >>= 1;
                ++data;
            }
        }

        color = WHITE;
        color.a = color_product(color.a, alpha);
    }
}


// Draw variable tiles
static void draw_variable(z64_disp_buf_t* db, const variable_tile_info_t* info, uint8_t alpha) {
    colorRGBA8_t color = DIM;
    color.a = color_product(color.a, alpha);

    // Draw all dimmed first, then all bright
    for (uint8_t enabled = 0; enabled <= 1; ++enabled) {
        gDPSetPrimColor(db->p++, 0, 0, color.r, color.g, color.b, color.a);

        const variable_tile_t* tile = info->tiles;
        const variable_tile_data_t* data = variable_tile_positions;
        while (data != variable_tile_positions + NUM_VARIABLE) {
            if (tile->enabled == enabled) {
                sprite_t* sprite = icon_sprites[data->sprite];
                draw_square_sprite(db, icon_sprites[data->sprite], tile->tile_index, data->pos, ICON_SIZE);
            }
            ++tile;
            ++data;
        }

        color = WHITE;
        color.a = color_product(color.a, alpha);
    }
}


// Draw music tiles
static void draw_songs(z64_disp_buf_t* db, const music_tile_info_t* songs, uint8_t alpha) {
    uint16_t bits = songs->bits;
    const music_tile_data_t* data = song_note_data;
    sprite_load(db, &song_note_sprite, 0, 1);

    uint8_t bright_alpha = color_product(WHITE.a, alpha);
    uint8_t dim_alpha = color_product(DIM.a, alpha);

    colorRGBA8_t last_color = {0x00, 0x00, 0x00, 0x00};
    while (data != song_note_data + NUM_SONGS) {
        colorRGBA8_t color;
        color.color = data->color;
        color.a = bright_alpha;
        if ((bits & 0x1) == 0) {
            // Dim color
            color.r = color_product(color.r, DIM.r);
            color.g = color_product(color.g, DIM.g);
            color.b = color_product(color.b, DIM.b);
            color.a = dim_alpha;
        }

        if (last_color.r != color.r || last_color.g != color.g || last_color.b != color.b || last_color.a != color.a) {
            gDPSetPrimColor(db->p++, 0, 0, color.r, color.g, color.b, color.a);
        }
        sprite_draw(db, &song_note_sprite, 0, get_left(data->pos), get_top(data->pos), MUSIC_WIDTH, MUSIC_HEIGHT);

        bits >>= 1;
        ++data;
        last_color = color;
    }
}

// Draw button tiles
static void draw_buttons(z64_disp_buf_t* db, const button_tile_info_t* buttons, uint8_t alpha) {
    uint16_t bits = buttons->bits;
    const button_tile_data_t* data = button_note_data;
    sprite_load(db, &ocarina_button_sprite, 0, 5);

    uint8_t bright_alpha = color_product(WHITE.a, alpha);
    uint8_t dim_alpha = color_product(DIM.a, alpha);

    colorRGBA8_t last_color = {0x00, 0x00, 0x00, 0x00};
    uint8_t button_index = 0;
    while (data != button_note_data + NUM_BUTTONS) {
        colorRGBA8_t color;
        color.color = data->color;
        color.a = bright_alpha;
        if ((bits & 0x1) == 0) {
            // Dim color
            color.r = color_product(color.r, DIM.r);
            color.g = color_product(color.g, DIM.g);
            color.b = color_product(color.b, DIM.b);
            color.a = dim_alpha;
        }

        if (last_color.r != color.r || last_color.g != color.g || last_color.b != color.b || last_color.a != color.a) {
            gDPSetPrimColor(db->p++, 0, 0, color.r, color.g, color.b, color.a);
        }
        sprite_draw(db, &ocarina_button_sprite, button_index, get_left(data->pos), get_top(data->pos), BUTTON_WIDTH, BUTTON_HEIGHT);

        bits >>= 1;
        ++data;
        last_color = color;
        button_index++;
    }
}


// Draw counter numbers
// note: must load item_digit_sprite before calling this function
static void draw_digits(z64_disp_buf_t* db, const uint8_t* digits, const counter_tile_data_t* data) {
    int digit_left[4] = {0, 0, 0, 0}; // last element is total width

    for (int i = 0; i < 3; ++i) {
        int digit_width = 6;
        if (digits[i] == 1) {
            --digit_left[i];
            digit_width = 5; // "1" sprite is narrower
        }
        else if (digits[i] > 9) {
            digit_width = 0; // empty
        }
        digit_left[i+1] = digit_left[i] + digit_width;
    }

    int left = get_left(data->pos) + data->counter_hoffset;
    if (data->align_center) {
        left -= digit_left[3] / 2;
    }
    int top = get_top(data->pos) + data->counter_voffset;

    for (int i = 0; i < 3; ++i) {
        if (digits[i] <= 9) {
            sprite_draw(db, &item_digit_sprite, digits[i], left + digit_left[i], top, 8, 8);
        }
    }
}

static void draw_triforce_count_fileselect(z64_disp_buf_t* db, const uint8_t* digitsCurrent, const uint8_t* digitsTotal,
 const counter_tile_data_t* dataCurrent, const counter_tile_data_t* dataTotal, uint8_t bright_alpha) {
    int digit_left[4] = {0, 0, 0, 0}; // last element is total width

    for (int i = 0; i < 3; ++i) {
        int digit_width = 6;
        if (digitsCurrent[i] == 1) {
            --digit_left[i];
            digit_width = 5; // "1" sprite is narrower
        }
        else if (digitsCurrent[i] > 9) {
            digit_width = 0; // empty
        }
        digit_left[i+1] = digit_left[i] + digit_width;
    }

    int left = get_left(dataCurrent->pos) + dataCurrent->counter_hoffset;
    left -= digit_left[3];

    int top = get_top(dataCurrent->pos) + dataCurrent->counter_voffset;

    // If the goal has been reached, color current number in yellow instead of white.
    if (hasTriforceGoalBeenReached) {
        gDPSetPrimColor(db->p++, 0, 0, 0xF4, 0xEC, 0x30, bright_alpha);
    }

    for (int i = 0; i < 3; ++i) {
        if (digitsCurrent[i] <= 9) {
            sprite_draw(db, &item_digit_sprite, digitsCurrent[i], left + digit_left[i], top, 8, 8);
        }
    }

    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, bright_alpha);
    text_print_size(db, "/", get_left(dataCurrent->pos) + 4, top, 8, 8);

    sprite_load(db, &item_digit_sprite, 0, 10);
    // Triforce goal number is always in yellow.
    gDPSetPrimColor(db->p++, 0, 0, 0xF4, 0xEC, 0x30, bright_alpha);

    for (int i = 0; i < 3; ++i) {
        int digit_width = 6;
        if (digitsTotal[i] == 1) {
            --digit_left[i];
            digit_width = 5; // "1" sprite is narrower
        }
        else if (digitsTotal[i] > 9) {
            digit_width = 0; // empty
        }
        digit_left[i+1] = digit_left[i] + digit_width;
    }

    left = get_left(dataTotal->pos) + dataTotal->counter_hoffset;
    top = get_top(dataTotal->pos) + dataTotal->counter_voffset;

    for (int i = 0; i < 3; ++i) {
        if (digitsTotal[i] <= 9) {
            sprite_draw(db, &item_digit_sprite, digitsTotal[i], left + digit_left[i], top, 8, 8);
        }
    }
    sprite_load(db, &item_digit_sprite, 0, 10);
    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, bright_alpha);
}


// Draw counter tiles
static void draw_counts(z64_disp_buf_t* db, const counter_tile_info_t* info, uint8_t alpha) {
    const counter_tile_data_t* const data = counter_positions;

    uint8_t bright_alpha = color_product(WHITE.a, alpha);

    // Rupee
    colorRGB8_t rupee_color = rupee_colors[info->wallet];
    gDPSetPrimColor(db->p++, 0, 0, rupee_color.r, rupee_color.g, rupee_color.b, bright_alpha);
    draw_square_sprite(db, &key_rupee_clock_sprite, 1, data[SLOT_RUPEES].pos, COUNTER_ICON_SIZE);

    // Heart, Skulltula, and Deaths use WHITE
    gDPSetPrimColor(db->p++, 0, 0, WHITE.r, WHITE.g, WHITE.b, bright_alpha);

    // Heart
    sprite_load(db, &quest_items_sprite, 12, 1);
    if (!info->double_defense) {
        sprite_draw(db, &quest_items_sprite, 0, get_left(data[SLOT_HEARTS].pos), get_top(data[SLOT_HEARTS].pos), COUNTER_ICON_SIZE, COUNTER_ICON_SIZE);
    }
    else {
        sprite_draw(db, &quest_items_sprite, 0, get_left(data[SLOT_HEARTS].pos)-2, get_top(data[SLOT_HEARTS].pos), COUNTER_ICON_SIZE, COUNTER_ICON_SIZE);
        sprite_draw(db, &quest_items_sprite, 0, get_left(data[SLOT_HEARTS].pos)+2, get_top(data[SLOT_HEARTS].pos), COUNTER_ICON_SIZE, COUNTER_ICON_SIZE);
    }

    // Deaths
    if (info->digits[SLOT_DEATHS][2] <= 9) {
        draw_square_sprite(db, &linkhead_skull_sprite, 1, data[SLOT_DEATHS].pos, 0x0A);
    }

    // Skulltula
    sprite_load(db, &quest_items_sprite, 11, 1);
    sprite_draw(db, &quest_items_sprite, 0, get_left(data[SLOT_SKULLTULLAS].pos), get_top(data[SLOT_SKULLTULLAS].pos), COUNTER_ICON_SIZE, COUNTER_ICON_SIZE);

    // Triforce
    if (TRIFORCE_HUNT_ENABLED && info->digits[SLOT_TRIFORCE_CURRENT][2] <= 9) {
        static uint8_t frame_counter = 0;
        gDPSetPrimColor(db->p++, 0, 0, 0xF4, 0xEC, 0x30, bright_alpha);
        draw_square_sprite(db, &triforce_sprite, (frame_counter++ >> 2) % 16, data[SLOT_TRIFORCE_CURRENT].pos, COUNTER_ICON_SIZE);
    }

    // Draw digits
    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, bright_alpha);
    sprite_load(db, &item_digit_sprite, 0, 10);
    for (int i = 0; i < NUM_COUNTER; ++i) {
        // Special case for Triforce current / total
        if (i == 3 && TRIFORCE_HUNT_ENABLED) {
            draw_triforce_count_fileselect(db, info->digits[i], info->digits[i + 1], &data[i], &data[i + 1], bright_alpha);
            i++;
            continue;
        }
        draw_digits(db, info->digits[i], &data[i]);
    }
}


// Get alpha level based on menu transition frame
static uint8_t get_alpha(const z64_menudata_t* menu_data) {
    uint8_t value = (uint8_t)menu_data->menu_transition;
    if (value == 0x00) {
        value = 0x80 | (uint8_t)menu_data->alt_transition;
    }
    switch (value) {
        case 0x03:
        case 0x06:
        case 0x87:
        case 0x98:
            return 0xC8;
            break;
        case 0x02:
        case 0x86:
        case 0x97:
        case 0x8D:
            return (uint8_t)(((8 - menu_data->transition_frame) * 0xC8) / 8);
            break;
        case 0x04:
        case 0x88:
        case 0x99:
        case 0x8A:
            return (uint8_t)((menu_data->transition_frame * 0xC8) / 8);
            break;
        default:
            return 0x00;
    }
}


/*=============================================================================
Entry point
=============================================================================*/


void draw_file_icons(z64_disp_buf_t* db, const z64_menudata_t* menu_data) {
    if (menu_data->transition_frame == 8) {
        if ((menu_data->menu_transition == 0x00 && menu_data->menu_depth == 0x02)
                || menu_data->alt_transition == 0x05
                || menu_data->alt_transition == 0x16) {
            read_file_data(&menu_data->sram_buffer->primary_saves[menu_data->selected_file].original_save);
            return;
        }
    }
    uint8_t icon_alpha = get_alpha(menu_data);

    if (icon_alpha) {

        gDPPipeSync(db->p++);
        gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);

        draw_fixed(db, &draw_data.fixed, icon_alpha);
        draw_variable(db, &draw_data.variable, icon_alpha);
        draw_songs(db, &draw_data.songs, icon_alpha);
        if (SHUFFLE_OCARINA_BUTTONS) {
            draw_buttons(db, &draw_data.buttons, icon_alpha);
        }
        draw_counts(db, &draw_data.counters, icon_alpha);
    }
}


/*=============================================================================
Helper functions
=============================================================================*/

static void make_digits(uint8_t* digits, int16_t value) {
    digits[0] = digits[1] = digits[2] = 0xFF;
    if (value < 0) {
        return;
    }
    else if (value > 999) {
        value = 999;
    }

    for (int idx = 2; idx >= 0; --idx) {
        digits[idx] = value % 10;
        value /= 10;
        if (value == 0) break;
    }
}


static void populate_upgrade_item(const z64_file_t* file, variable_tile_t* tile, uint8_t slot, uint8_t base_item) {
    uint8_t item = file->items[slot];
    if (item == base_item || item == base_item + 1) {
        tile->enabled = 1;
        tile->tile_index = item;
    }
    else {
        tile->enabled = 0;
        tile->tile_index = base_item;
    }
}


static const uint8_t MASK_LOOKUP[16] = {
    Z64_ITEM_MASK_OF_TRUTH, // 0x00
    Z64_ITEM_KEATON_MASK,   // 0x01
    Z64_ITEM_SKULL_MASK,    // 0x02
    Z64_ITEM_SKULL_MASK,
    Z64_ITEM_SPOOKY_MASK,   // 0x04
    Z64_ITEM_SPOOKY_MASK,
    Z64_ITEM_SPOOKY_MASK,
    Z64_ITEM_SPOOKY_MASK,
    Z64_ITEM_BUNNY_HOOD,    // 0x08
    Z64_ITEM_BUNNY_HOOD,
    Z64_ITEM_BUNNY_HOOD,
    Z64_ITEM_BUNNY_HOOD,
    Z64_ITEM_BUNNY_HOOD,
    Z64_ITEM_BUNNY_HOOD,
    Z64_ITEM_BUNNY_HOOD,
    Z64_ITEM_BUNNY_HOOD
};


static void populate_child_trade(const z64_file_t* file, variable_tile_t* tile) {
    uint8_t item_child = file->items[Z64_SLOT_CHILD_TRADE];
    uint16_t mask_bits = (file->item_get_inf[2] >> 3) & 0x8F;
    uint16_t itemdata3 = file->item_get_inf[3];
    uint16_t infdata7 = file->inf_table[7];
    if (itemdata3 & 0x8000 || mask_bits > 0x0F) {
        tile->tile_index = Z64_ITEM_MASK_OF_TRUTH;
        tile->enabled = 1;
    }
    else if (mask_bits > 0) {
        tile->tile_index = MASK_LOOKUP[mask_bits];
        tile->enabled = 1;
    }
    else if (Z64_ITEM_WEIRD_EGG <= item_child && item_child <= Z64_ITEM_ZELDAS_LETTER) {
        if (item_child == Z64_ITEM_ZELDAS_LETTER && (file->event_chk_inf[0x05] & 0x0200) == 0) {
            // haven't learned Song from Impa, letter will revert on load
            tile->tile_index = Z64_ITEM_CHICKEN;
        } else {
            tile->tile_index = item_child;
        }
        tile->enabled = 1;
    }
    else {
        tile->tile_index = Z64_ITEM_MASK_OF_TRUTH;
        tile->enabled = 0;
    }
}


extern uint8_t DISABLE_TIMERS;
static void populate_adult_trade(const z64_file_t* file, variable_tile_t* tile) {
    uint8_t item_adult = file->items[Z64_SLOT_ADULT_TRADE];
    if (!DISABLE_TIMERS) {
        switch (item_adult) {
            case Z64_ITEM_ODD_MUSHROOM:
                item_adult = Z64_ITEM_COJIRO;
                break;
            case Z64_ITEM_EYEBALL_FROG:
            case Z64_ITEM_EYE_DROPS:
                item_adult = Z64_ITEM_PRESCRIPTION;
                break;
        }
    }
    if (Z64_ITEM_POCKET_EGG <= item_adult && item_adult <= Z64_ITEM_CLAIM_CHECK) {
        tile->tile_index = item_adult;
        tile->enabled = 1;
    }
    else {
        tile->tile_index = Z64_ITEM_CLAIM_CHECK;
        tile->enabled = 0;
    }
}


static void populate_magic(const z64_file_t* file, variable_tile_t* tile) {
    if (file->magic_capacity) {
        tile->tile_index = 19;
        tile->enabled = 1;
    }
    else {
        tile->tile_index = 18;
        tile->enabled = file->magic_acquired;
    }
}


static void populate_upgrade_equip(const z64_file_t* file, variable_tile_t* tile, uint8_t value, uint8_t max, uint8_t base_tile) {
    if (value > max) value = max;
    if (!value) {
        tile->enabled = 0;
        tile->tile_index = base_tile;
    }
    else {
        tile->enabled = 1;
        tile->tile_index = base_tile + (value - 1);
    }
}
