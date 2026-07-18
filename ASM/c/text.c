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
// Both narrow and wide languages use the game's normal 16x16 message font.
// LANG_DPAD_TEXT_WIDE only selects how a u16 code is decoded and loaded:
//   0: low byte is a normal message-font character (Font_LoadChar)
//   1: value is a Shift-JIS character (Font_LoadCharWide)
//
// Width has two independent parts:
//   * CHAR_WIDTHS supplies the natural per-character advance.
//   * LANG_DPAD_FONT_WIDTH_SCALE_Q8_8 applies one horizontal multiplier.
//
// 1.0 therefore means the unmodified normal font for every language. The same
// calculated advance is used by drawing, measurement, and D-pad layout code.
// LANG_DPAD_FONT_INTENSITY_BOOST separately raises non-zero I4 texels after a
// glyph is loaded, improving white/opacity without changing its dimensions.

extern uint8_t LANG_DPAD_TEXT_WIDE;
extern uint16_t LANG_DPAD_FONT_WIDTH_SCALE_Q8_8;
extern uint8_t LANG_DPAD_FONT_INTENSITY_BOOST;
extern float LANG_CHAR_WIDTHS[144];
extern uint16_t LANG_WIDE_CHAR_WIDTH_COUNT;
extern language_wide_char_width_t LANG_WIDE_CHAR_WIDTH_OVERRIDES[];

#define DPAD_FONT_CACHE_SIZE 120
#define DPAD_NARROW_FIRST_CHAR 0x20
#define DPAD_NARROW_CHAR_COUNT 144
#define DPAD_NARROW_SPACE 0x20
#define DPAD_WIDE_SPACE 0x8140
#define NORMAL_FONT_TEXTURE_SIZE 16

#define DPAD_SMALL_FONT_LINE_HEIGHT 11
#define DPAD_SMALL_FONT_LAYOUT_HEIGHT 10

static uint16_t sDpadFontCodes[DPAD_FONT_CACHE_SIZE];
static uint8_t sDpadFontCount = 0;
static uint8_t sDpadFontPauseActive = 0;

static sprite_t sDpadFontSprite = {
    NULL, 16, 16, DPAD_FONT_CACHE_SIZE,
    G_IM_FMT_I, G_IM_SIZ_4b, 1
};

static void text_language_cache_reset(void) {
    sDpadFontCount = 0;
}

void text_language_cache_tick(void) {
    uint8_t pauseActive = (z64_game.pause_ctxt.state == PAUSE_STATE_MAIN);

    // Message rendering reuses MessageContext.font.charTexBuf while the pause menu is closed.
    // Reset the D-pad glyph index whenever the pause menu opens or closes so cached indices
    // never refer to textures loaded by the normal message renderer.
    if (!pauseActive || !sDpadFontPauseActive) {
        text_language_cache_reset();
    }
    sDpadFontPauseActive = pauseActive;
}

static int text_language_layout_height(int lineHeight) {
    // Keep the compact 11-pixel table's established 10-pixel horizontal
    // sizing. Other line heights use their requested height for width layout.
    if (lineHeight == DPAD_SMALL_FONT_LINE_HEIGHT) {
        return DPAD_SMALL_FONT_LAYOUT_HEIGHT;
    }
    return lineHeight > 0 ? lineHeight : 1;
}

static uint16_t text_language_width_scale(void) {
    // Old or partially-built patches may leave this field zero. Treat that as
    // the neutral 1.0 scale rather than making every glyph one pixel wide.
    return LANG_DPAD_FONT_WIDTH_SCALE_Q8_8 != 0 ?
        LANG_DPAD_FONT_WIDTH_SCALE_Q8_8 : 0x0100;
}

int text_language_wide_source_width(uint16_t code) {
    for (uint16_t i = 0; i < LANG_WIDE_CHAR_WIDTH_COUNT; i++) {
        if (LANG_WIDE_CHAR_WIDTH_OVERRIDES[i].code == code) {
            return LANG_WIDE_CHAR_WIDTH_OVERRIDES[i].width;
        }
    }
    return NORMAL_FONT_TEXTURE_SIZE;
}

static float text_language_source_width(uint16_t code) {
    if (LANG_DPAD_TEXT_WIDE) {
        return (float)text_language_wide_source_width(code);
    }

    if (code < DPAD_NARROW_FIRST_CHAR ||
        code >= DPAD_NARROW_FIRST_CHAR + DPAD_NARROW_CHAR_COUNT) {
        return (float)NORMAL_FONT_TEXTURE_SIZE;
    }
    return LANG_CHAR_WIDTHS[code - DPAD_NARROW_FIRST_CHAR];
}

int text_language_glyph_draw_width(int height) {
    int layoutHeight = text_language_layout_height(height);
    int width = ((layoutHeight * text_language_width_scale()) + 0x80) >> 8;
    return width > 0 ? width : 1;
}

int text_language_glyph_advance(uint16_t code, int height) {
    int layoutHeight = text_language_layout_height(height);
    float sourceWidth = text_language_source_width(code);
    float scaledWidth = sourceWidth * (float)layoutHeight *
        (float)text_language_width_scale() /
        (float)(NORMAL_FONT_TEXTURE_SIZE * 0x100);
    int advance = (int)(scaledWidth + 0.5f);
    return advance > 0 ? advance : 1;
}

int text_measure_lang_size(const uint16_t* s, int height) {
    int width = 0;
    while (*s != 0x0000) {
        width += text_language_glyph_advance(*s, height);
        s++;
    }
    return width;
}

static uint8_t text_language_boost_intensity(uint8_t intensity) {
    if (intensity == 0 || LANG_DPAD_FONT_INTENSITY_BOOST == 0) {
        return intensity;
    }

    int boosted = intensity + LANG_DPAD_FONT_INTENSITY_BOOST;
    return boosted > 0x0F ? 0x0F : (uint8_t)boosted;
}

static void text_language_apply_intensity_boost(uint8_t glyphIndex) {
    uint8_t* texture = &z64_game.msgContext.font.charTexBuf[glyphIndex * FONT_CHAR_TEX_SIZE];

    // Each byte contains two I4 pixels. Keep zero fully transparent so this
    // adjustment changes intensity/opacity without growing the glyph outline.
    for (int i = 0; i < FONT_CHAR_TEX_SIZE; i++) {
        uint8_t high = text_language_boost_intensity(texture[i] >> 4);
        uint8_t low = text_language_boost_intensity(texture[i] & 0x0F);
        texture[i] = (high << 4) | low;
    }
}

static int text_language_get_glyph(uint16_t code) {
    if (!LANG_DPAD_TEXT_WIDE &&
        (code < DPAD_NARROW_FIRST_CHAR ||
         code >= DPAD_NARROW_FIRST_CHAR + DPAD_NARROW_CHAR_COUNT)) {
        return -1;
    }

    for (uint8_t i = 0; i < sDpadFontCount; i++) {
        if (sDpadFontCodes[i] == code) {
            return i;
        }
    }

    if (sDpadFontCount >= DPAD_FONT_CACHE_SIZE) {
        return -1;
    }

    uint8_t index = sDpadFontCount++;
    sDpadFontCodes[index] = code;
    if (LANG_DPAD_TEXT_WIDE) {
        Font_LoadCharWide(&z64_game.msgContext.font, code, index * FONT_CHAR_TEX_SIZE);
    } else {
        Font_LoadChar(
            &z64_game.msgContext.font,
            (uint8_t)(code - DPAD_NARROW_FIRST_CHAR),
            index * FONT_CHAR_TEX_SIZE
        );
    }
    text_language_apply_intensity_boost(index);
    return index;
}

int text_print_lang_height(z64_disp_buf_t* db, const uint16_t* s, int left, int top, int height) {
    int drawHeight = height > 0 ? height : 1;
    int drawWidth = text_language_glyph_draw_width(height);
    uint16_t space = LANG_DPAD_TEXT_WIDE ? DPAD_WIDE_SPACE : DPAD_NARROW_SPACE;

    sDpadFontSprite.buf = z64_game.msgContext.font.charTexBuf;
    while (*s != 0x0000) {
        uint16_t code = *s++;
        if (code != space) {
            int glyph = text_language_get_glyph(code);
            if (glyph >= 0) {
                sprite_texture_4b(
                    db, &sDpadFontSprite, glyph, left,
                    top,
                    drawWidth, drawHeight
                );
            }
        }
        left += text_language_glyph_advance(code, height);
    }

    // sprite_texture_4b selects an I4-specific combiner. Restore the combiner expected by
    // the remaining D-pad overlay elements before returning to the caller.
    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    return left;
}

int text_print_lang(z64_disp_buf_t* db, const uint16_t* s, int left, int top) {
    return text_print_lang_height(db, s, left, top, font_sprite.tile_h);
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
