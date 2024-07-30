#include "text.h"

#include "gfx.h"
#include "util.h"
#include "z64.h"

const int FONT_CHAR_TEX_WIDTH = 16;
const int FONT_CHAR_TEX_HEIGHT = 16;
const int NUM_FONT_CHARS = 95;

typedef struct {
    uint32_t c : 8;
    uint32_t left : 12;
    uint32_t top : 12;
} text_char_t;

void print_char(z64_disp_buf_t* db, char c, int x, int y, int width, int height) {
    sprite_texture(db, &font_sprite, (c - ' '), x, y, width, height);
}

int text_print_size(z64_disp_buf_t* db, const char* s, int left, int top, int width, int height) {
    while (*s != 0x00) {
        print_char(db, *s, left, top, width, height);
        left += width;
        s++;
    }

    return left;
}

int text_print(z64_disp_buf_t* db, const char* s, int left, int top) {
    return text_print_size(db, s, left, top, font_sprite.tile_w, font_sprite.tile_h);
}

int draw_int(z64_disp_buf_t* db, int32_t number, int16_t left, int16_t top, colorRGBA8_t color) {
    draw_int_size(db, number, left, top, color, 8, 16);
}

// Helper function for drawing numbers to the HUD.
int draw_int_size(z64_disp_buf_t* db, int32_t number, int16_t left, int16_t top, colorRGBA8_t color, int16_t width, int16_t height) {
    int isNegative = 0;
    if (number < 0) {
        number *= -1;
        isNegative = 1;
    }

    uint8_t digits[10];
    uint8_t j = 0;
    // Extract each digit. They are added, in reverse order, to digits[]
    do {
        digits[j] = number % 10;
        number = number / 10;
        j++;
    } while (number > 0);
    // This combiner mode makes it look like the rupee count
    gDPSetCombineLERP(db->p++, 0, 0, 0, PRIMITIVE, TEXEL0, 0, PRIMITIVE, 0, 0, 0, 0, PRIMITIVE,
        TEXEL0, 0, PRIMITIVE, 0);

    // Set the color
    gDPSetPrimColor(db->p++, 0, 0, color.r, color.g, color.b, color.a);
    if (isNegative) {
        text_print_size(db, "-", left - rupee_digit_sprite.tile_w, top, width, height);
    }
    // Draw each digit
    for (uint8_t c = j; c > 0; c--) {
        sprite_texture(db, &rupee_digit_sprite, digits[c-1], left, top, width, height);
        left += width;
    }
    return j;
}
