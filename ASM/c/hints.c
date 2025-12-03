#include <stdbool.h>
#include "dungeon_info.h"
#include "gfx.h"
#include "text.h"
#include "z64.h"
#include "dpad.h"
#include "hints.h"

bool update_first_time = false;
uint8_t current_hint_index = 0;
uint8_t menu_hint_cooldown = 20;
uint32_t hint_textbox_ids[40];
int8_t hint_textbox_types[40];

uint32_t *current_hints_array = NULL;
uint32_t hint_always_ids[10];
uint32_t hint_foolish_ids[10];
uint32_t hint_goals_ids[10];
uint32_t hint_sometimes_ids[10];
uint8_t hint_total_found[4];

menu_category_t menu_hints_categories[] = {
    {  0, "Always"},
    {  1, "Foolish"},
    {  2, "Goals"},
    {  3, "Sometimes"},
};

bool hint_menu_is_drawn() {
    return show_hint_info;
}

void init_hints_ids() {
    for (uint8_t i = 0; i < 40; i++) {
        hint_textbox_ids[i] = CFG_HINTS_IDS_AND_TYPES[2*i] + 1000;
        hint_textbox_types[i] = CFG_HINTS_IDS_AND_TYPES[2*i + 1];
    }
}

bool flags_get_hint(int hint_index) {
    return (extended_savectx.hints[hint_index / 8] & (1 << (hint_index % 8))) > 0;
}

void flags_set_hint(int hint_index) {
    //draw_debug_int(4, hint_index);
    extended_savectx.hints[hint_index / 8] |= 1 << (hint_index % 8);
}

void update_hints()
{
    uint8_t iAlways = 0;
    uint8_t iFoolish = 0;
    uint8_t iGoals = 0;
    uint8_t iSometimes = 0;
    for (uint8_t i = 0; i < 40; i++) {
        if (flags_get_hint(i) && hint_textbox_types[i] < 20) {
            switch (hint_textbox_types[i]) {
                case 2: {
                    hint_always_ids[iAlways] = hint_textbox_ids[i];
                    iAlways++;
                    break;
                }
                case 3: {
                    hint_foolish_ids[iFoolish] = hint_textbox_ids[i];
                    iFoolish++;
                    break;
                }
                case 4: {
                    hint_goals_ids[iGoals] = hint_textbox_ids[i];
                    iGoals++;
                    break;
                }
                case 5: {
                    hint_sometimes_ids[iSometimes] = hint_textbox_ids[i];
                    iSometimes++;
                    break;
                }
            }
        }
    }
    hint_total_found[0] = iAlways;
    hint_total_found[1] = iFoolish;
    hint_total_found[2] = iGoals;
    hint_total_found[3] = iSometimes;
}

void message_id_check(z64_game_t* play, uint16_t textId)
{
    // Displaced code
    Message_OpenText(play, textId);

    //draw_debug_int(0, textId);
    for (uint8_t i = 0; i < 40; i++) {
        if (hint_textbox_ids[i] == textId && !(flags_get_hint(i))) {
            flags_set_hint(i);
            // Update the duplicate if there is one.
            if (hint_textbox_types[i] > 20 && i > 0) {
                flags_set_hint(i - 1);
            }
            if (i < 39 && hint_textbox_types[i + 1] > 20) {
                flags_set_hint(i + 1);
            }
            update_hints();
            break;
        }
    }
}

void draw_hints(z64_disp_buf_t* db) {

    db->p = db->buf;
    if ((z64_game.common.input[0].raw.pad.du || z64_game.common.input[0].raw.pad.l) && z64_game.common.input[0].raw.pad.a) {
        if (menu_hint_cooldown == 20) {
            show_hint_info = show_hint_info ? false : true;
        }

        if (menu_hint_cooldown > 0) {
            menu_hint_cooldown--;
        }
    }
    if (menu_hint_cooldown < 20) {
        menu_hint_cooldown--;
        if (menu_hint_cooldown == 0) {
            menu_hint_cooldown = 20;
        }
    }

    gSPDisplayList(db->p++, &setup_db);
    if (show_hint_info) {

        if (!update_first_time) {
            update_hints();
            update_first_time = true;
        }

        if (z64_game.common.input[0].pad_pressed.dr) {
                current_hint_cat_index++;
                if (current_hint_cat_index > 3) {
                    current_hint_cat_index = 0;
                }
        }
        if (z64_game.common.input[0].pad_pressed.dl) {
            if (current_hint_cat_index == 0) {
                current_hint_cat_index = 3;
            } else {
                current_hint_cat_index--;
            }
        }

        switch (current_hint_cat_index) {
            case 0: {
                current_hints_array = hint_always_ids;
                break;
            }
            case 1: {
                current_hints_array = hint_foolish_ids;
                break;
            }
            case 2: {
                current_hints_array = hint_goals_ids;
                break;
            }
            case 3: {
                current_hints_array = hint_sometimes_ids;
                break;
            }
        }

        // Set up dimensions
        int font_width = 6;
        int font_height = 11;
        int padding = 2;
        int rows = 7;
        int bg_width = 30 * font_width;
        int bg_height = (rows * font_height) + ((rows + 1) * padding);
        int bg_left = 30;
        int bg_top = 30;

        int start_top = bg_top + padding + 1;
        uint16_t left = bg_left + padding;

        // Draw background
        gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
        for (int i = 0; i < rows; i++) {
            uint16_t line_top = bg_top + i * (font_height + padding) + padding;
            gDPPipeSync(db->p++);
            if (i % 2) {
                gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xD0);
            }
            else {
                gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xDA);
            }
            gSPTextureRectangle(db->p++,
                bg_left<<2, line_top<<2,
                (bg_left + bg_width)<<2, (line_top + font_height + padding)<<2,
                0,
                0, 0,
                1<<10, 1<<10);
        }

        gDPPipeSync(db->p++);
        gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
        gDPSetPrimColor(db->p++, 0, 0, 120, 255, 100, 0xFF);

        text_print_size(db, "HINTS", left + bg_width / 2 - 3 * font_width, start_top, font_width, font_height);
        gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
        colorRGBA8_t white = { 255, 255, 255, 255};
        for (int i = 0; i < 4; i++) {
            menu_category_t *d = &(menu_hints_categories[i]);
            int top = start_top + ((font_height + padding) * (i + 1)) + 1;
            if (i != current_hint_cat_index) {
                text_print_size(db, d->name, left, top + 5, font_width, font_height);
                text_print_size(db, "Found : ", left + 10 * font_width, top + 5, font_width, font_height);
                draw_int_size(db, hint_total_found[i], left + 20*font_width, top + 5, white, font_width, font_height);
            }
        }
        menu_category_t* d = &(menu_hints_categories[current_hint_cat_index]);
        int top = start_top + ((font_height + padding) * (current_hint_cat_index + 1)) + 1;
        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
        colorRGBA8_t yellow = { 0xE0, 0xE0, 0x10, 255};
        text_print_size(db, d->name, left, top + 5, font_width, font_height);
        text_print_size(db, "Found : ", left + 10 * font_width, top + 5, font_width, font_height);
        draw_int_size(db, hint_total_found[current_hint_cat_index], left + 20 * font_width, top + 5, yellow, font_width, font_height);

        if (current_hints_array != NULL && hint_total_found[current_hint_cat_index] > 0) {
            if (z64_ctxt.input[0].pad_pressed.dd) {
                current_hint_index++;
                if (current_hint_index > hint_total_found[current_hint_cat_index] - 1) {
                    current_hint_index = 0;
                }
                z64_DisplayTextbox(&z64_game, current_hints_array[current_hint_index], 0);
            }
        }
    }
}
