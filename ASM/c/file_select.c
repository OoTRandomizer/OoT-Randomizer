#include "file_select.h"

#include "file_icons.h"
#include "file_message.h"
#include "gfx.h"
#include "text.h"
#include "util.h"
#include "z64.h"


sprite_t *hash_sprites[2] = {
    &items_sprite,
    &quest_items_sprite,
};

typedef struct {
    uint8_t sprite_index;
    uint8_t tile_index;
} hash_symbol_t;

hash_symbol_t hash_symbols[32] = {
    { 0,  0 }, // Deku Stick
    { 0,  1 }, // Deku Nut
    { 0,  3 }, // Bow
    { 0,  6 }, // Slingshot
    { 0,  7 }, // Fairy Ocarina
    { 0,  9 }, // Bombchu
    { 0, 11 }, // Longshot
    { 0, 14 }, // Boomerang
    { 0, 15 }, // Lens of Truth
    { 0, 16 }, // Beans
    { 0, 17 }, // Megaton Hammer
    { 0, 25 }, // Bottled Fish
    { 0, 26 }, // Bottled Milk
    { 0, 43 }, // Mask of Truth
    { 0, 44 }, // SOLD OUT
    { 0, 46 }, // Cucco
    { 0, 48 }, // Mushroom
    { 0, 50 }, // Saw
    { 0, 53 }, // Frog
    { 0, 60 }, // Master Sword
    { 0, 64 }, // Mirror Shield
    { 0, 65 }, // Kokiri Tunic
    { 0, 70 }, // Hover Boots
    { 0, 81 }, // Silver Gauntlets
    { 0, 84 }, // Gold Scale
    { 1,  9 }, // Stone of Agony
    { 1, 11 }, // Skull Token
    { 1, 12 }, // Heart Container
    { 1, 14 }, // Boss Key
    { 1, 15 }, // Compass
    { 1, 16 }, // Map
    { 1, 19 }, // Big Magic
};

extern uint8_t CFG_FILE_SELECT_HASH[5];

void draw_file_select_hash(uint32_t fade_out_alpha, z64_menudata_t* menu_data) {
    z64_disp_buf_t *db = &(z64_ctxt.gfx->poly_opa);

    // Call setup display list
    gSPDisplayList(db->p++, &setup_db);

    int icon_count = 5;
    int icon_size = 24;
    int padding = 8;
    int width = (icon_count * icon_size) + ((icon_count - 1) * padding);
    int left = (Z64_SCREEN_WIDTH - width) / 2;
    int top = 12;

    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

    for (int i = 0; i < icon_count; i++) {
        uint8_t sym_index = CFG_FILE_SELECT_HASH[i];
        hash_symbol_t *sym_desc = &(hash_symbols[sym_index]);
        sprite_t *sym_sprite = hash_sprites[sym_desc->sprite_index];

        sprite_load(db, sym_sprite, sym_desc->tile_index, 1);
        sprite_draw(db, sym_sprite, 0, left, top, icon_size, icon_size);

        left += icon_size + padding;
    }

    draw_file_message(db, menu_data);
    draw_file_icons(db, menu_data);

    // Fade out once a file is selected

    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, fade_out_alpha);
    gSPTextureRectangle(db->p++,
            0, 0,
            Z64_SCREEN_WIDTH<<2, Z64_SCREEN_HEIGHT<<2,
            0,
            0, 0,
            1<<10, 1<<10);
}
