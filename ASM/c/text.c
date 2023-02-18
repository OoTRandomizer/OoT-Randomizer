#include "text.h"

#include "gfx.h"
#include "util.h"
#include "z64.h"

#define text_max_chars 256
#define text_bucket_count 6
#define text_bucket_size 18

typedef struct {
    uint32_t c : 8;
    uint32_t left : 12;
    uint32_t top : 12;
} text_char_t;

static text_char_t *text_end = NULL;
static text_char_t *text_buf = NULL;

void text_init() {
    text_buf = heap_alloc(text_max_chars * sizeof(text_char_t));
    text_end = text_buf;
}

int text_print_size(const char *s, int left, int top, int width) {
    char c;
    int count = 0;
    while (c = *(s++)) {
        if (text_end >= text_buf + text_max_chars) break;
        text_end->c = c;
        text_end->left = left;
        text_end->top = top;
        text_end++;
        left += width;
        count++;
    }
    return count;
}

int text_print(const char* s, int left, int top) {
    return text_print_size(s, left, top, font_sprite.tile_w);
}

void text_flush_size(z64_disp_buf_t *db, int width, int height, int hoffset, int voffset) {
    for (int i = 0; i < text_bucket_count; i++) {
        sprite_load(db, &font_sprite,
                i * text_bucket_size, text_bucket_size);

        text_char_t *text_p = text_buf;
        while (text_p < text_end) {
            char c = text_p->c;
            int left = text_p->left + hoffset;
            int top = text_p->top + voffset;
            text_p++;

            int bucket = (c - 32) / text_bucket_size;
            if (bucket != i) continue;

            int tile_index = (c - 32) % text_bucket_size;
            sprite_draw(db, &font_sprite, tile_index,
                    left, top, width, height);
        }
    }

    text_end = text_buf;
}

void text_flush(z64_disp_buf_t *db) {
    text_flush_size(db, font_sprite.tile_w, font_sprite.tile_h, 0, 0);
}
