#include "inputviewer.h"

extern uint8_t CFG_INPUT_VIEWER;

const int8_t input_icon_width = 13;
const int8_t input_icon_height = 13;
const int8_t input_number_width = 6;
const int8_t input_number_height = 12;
const int16_t left_alignment = Z64_SCREEN_WIDTH / 12;
const int16_t top_alignment = 11 * Z64_SCREEN_HEIGHT / 12 + 2;

void draw_x_stick(z64_disp_buf_t* db) {
    colorRGBA8_t color = {0xF4, 0xEC, 0x30, 0xFF};
    draw_int_size(db, z64_game.common.input[0].raw.x, left_alignment, top_alignment, color, input_number_width, input_number_height);
}

void draw_y_stick(z64_disp_buf_t* db) {
    colorRGBA8_t color = {0xF4, 0xEC, 0x30, 0xFF};
    int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w;
    draw_int_size(db, z64_game.common.input[0].raw.y, left_alignment + xy_stick_length, top_alignment, color, input_number_width, input_number_height);
}

void draw_a(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.a) {
        gDPSetPrimColor(db->p++, 0, 0, CFG_A_BUTTON_COLOR.r, CFG_A_BUTTON_COLOR.g, CFG_A_BUTTON_COLOR.b, 0xFF);
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 0, left_alignment + 2 * xy_stick_length, top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_b(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.b) {
        gDPSetPrimColor(db->p++, 0, 0, CFG_B_BUTTON_COLOR.r, CFG_B_BUTTON_COLOR.g, CFG_B_BUTTON_COLOR.b, 0xFF);
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 1, left_alignment + 2 * xy_stick_length + input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_start(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.s) {
        gDPSetPrimColor(db->p++, 0, 0, 0xDC, 0xDC, 0xDC, 0xFF); // grey
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        text_print_size(db, "S", left_alignment + 2 * xy_stick_length + buttons_sprite.tile_w, top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_cdown(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.cd) {
        gDPSetPrimColor(db->p++, 0, 0, CFG_C_BUTTON_COLOR.r, CFG_C_BUTTON_COLOR.g, CFG_C_BUTTON_COLOR.b, 0xFF);
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 7, left_alignment + 2 * xy_stick_length + 2 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_cup(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.cu) {
        gDPSetPrimColor(db->p++, 0, 0, CFG_C_BUTTON_COLOR.r, CFG_C_BUTTON_COLOR.g, CFG_C_BUTTON_COLOR.b, 0xFF);
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 6, left_alignment + 2 * xy_stick_length + 5 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}


void draw_cleft(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.cl) {
        gDPSetPrimColor(db->p++, 0, 0, CFG_C_BUTTON_COLOR.r, CFG_C_BUTTON_COLOR.g, CFG_C_BUTTON_COLOR.b, 0xFF);
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 8, left_alignment + 2 * xy_stick_length + 4 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_cright(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.cr) {
        gDPSetPrimColor(db->p++, 0, 0, CFG_C_BUTTON_COLOR.r, CFG_C_BUTTON_COLOR.g, CFG_C_BUTTON_COLOR.b, 0xFF);
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 9, left_alignment + 2 * xy_stick_length + 3 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_z(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.z) {
        gDPSetPrimColor(db->p++, 0, 0, 0xDC, 0xDC, 0xDC, 0xFF); // grey
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 5, left_alignment + 2 * xy_stick_length + 6 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_l(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.l) {
        gDPSetPrimColor(db->p++, 0, 0, 0xDC, 0xDC, 0xDC, 0xFF); // grey
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 3, left_alignment + 2 * xy_stick_length + 7 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_r(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.r) {
        gDPSetPrimColor(db->p++, 0, 0, 0xDC, 0xDC, 0xDC, 0xFF); // grey
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 4, left_alignment + 2 * xy_stick_length + 8 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_ddown(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.dd) {
        gDPSetPrimColor(db->p++, 0, 0, 0xDC, 0xDC, 0xDC, 0xFF); // grey
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 7, left_alignment + 2 * xy_stick_length + 9 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_dup(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.du) {
        gDPSetPrimColor(db->p++, 0, 0, 0xDC, 0xDC, 0xDC, 0xFF); // grey
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 6, left_alignment + 2 * xy_stick_length + 12 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}


void draw_dleft(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.dl) {
        gDPSetPrimColor(db->p++, 0, 0, 0xDC, 0xDC, 0xDC, 0xFF); // grey
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 8, left_alignment + 2 * xy_stick_length + 11 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_dright(z64_disp_buf_t* db) {
    if (z64_game.common.input[0].raw.pad.dr) {
        gDPSetPrimColor(db->p++, 0, 0, 0xDC, 0xDC, 0xDC, 0xFF); // grey
        int8_t xy_stick_length = 3 * rupee_digit_sprite.tile_w + font_sprite.tile_w - 2;
        sprite_texture_4b(db, &buttons_sprite, 9, left_alignment + 2 * xy_stick_length + 10 * input_icon_width,
            top_alignment, input_icon_width, input_icon_height);
    }
}

void draw_input_viewer(z64_disp_buf_t* db) {
    if (CFG_INPUT_VIEWER) {
        gSPDisplayList(db->p++, &setup_db);
        gDPPipeSync(db->p++);
        draw_a(db);
        draw_b(db);
        draw_cup(db);
        draw_cdown(db);
        draw_cleft(db);
        draw_cright(db);

        draw_z(db);
        draw_l(db);
        draw_r(db);

        draw_dup(db);
        draw_ddown(db);
        draw_dleft(db);
        draw_dright(db);

        draw_x_stick(db);
        draw_y_stick(db);
    }
}
