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

// ============================================================================
// Localized D-pad text renderer
// ============================================================================
// Narrow languages use the existing font sprite. JP/wide languages lazily load
// Shift-JIS glyphs into the message font buffer while the pause menu is open.

extern uint8_t LANG_DPAD_TEXT_WIDE;

#define DPAD_WIDE_FONT_CACHE_SIZE 120
#define DPAD_WIDE_SPACE 0x8140

static uint16_t sDpadWideFontCodes[DPAD_WIDE_FONT_CACHE_SIZE];
static uint8_t sDpadWideFontCount = 0;
static uint8_t sDpadWideFontPauseActive = 0;

static sprite_t sDpadWideFontSprite = {
    NULL, 16, 16, DPAD_WIDE_FONT_CACHE_SIZE,
    G_IM_FMT_I, G_IM_SIZ_4b, 1
};

static void text_language_cache_reset(void) {
    sDpadWideFontCount = 0;
}

void text_language_cache_tick(void) {
    uint8_t pauseActive = (z64_game.pause_ctxt.state == PAUSE_STATE_MAIN);

    // Message rendering reuses MessageContext.font.charTexBuf while the pause menu is closed.
    // Reset the D-pad glyph index whenever the pause menu opens or closes so cached indices
    // never refer to textures loaded by the normal message renderer.
    if (!pauseActive || !sDpadWideFontPauseActive) {
        text_language_cache_reset();
    }
    sDpadWideFontPauseActive = pauseActive;
}

static int text_language_get_wide_glyph(uint16_t code) {
    for (uint8_t i = 0; i < sDpadWideFontCount; i++) {
        if (sDpadWideFontCodes[i] == code) {
            return i;
        }
    }

    if (sDpadWideFontCount >= DPAD_WIDE_FONT_CACHE_SIZE) {
        return -1;
    }

    uint8_t index = sDpadWideFontCount++;
    sDpadWideFontCodes[index] = code;
    Font_LoadCharWide(&z64_game.msgContext.font, code, index * FONT_CHAR_TEX_SIZE);
    return index;
}

int text_print_lang_size(z64_disp_buf_t* db, const uint16_t* s, int left, int top, int width, int height) {
    if (!LANG_DPAD_TEXT_WIDE) {
        while (*s != 0x0000) {
            uint8_t c = (uint8_t)(*s & 0xFF);
            if (c >= ' ' && c <= '~') {
                print_char(db, c, left, top, width, height);
            }
            left += width;
            s++;
        }
        return left;
    }

    sDpadWideFontSprite.buf = z64_game.msgContext.font.charTexBuf;
    while (*s != 0x0000) {
        uint16_t code = *s++;
        if (code != DPAD_WIDE_SPACE) {
            int glyph = text_language_get_wide_glyph(code);
            if (glyph >= 0) {
                sprite_texture_4b(db, &sDpadWideFontSprite, glyph, left, top, width, height);
            }
        }
        left += width;
    }

    // sprite_texture_4b selects an I4-specific combiner. Restore the combiner expected by
    // the remaining D-pad overlay elements before returning to the caller.
    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    return left;
}

int text_print_lang(z64_disp_buf_t* db, const uint16_t* s, int left, int top) {
    return text_print_lang_size(db, s, left, top, font_sprite.tile_w, font_sprite.tile_h);
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
