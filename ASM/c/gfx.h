#ifndef GFX_H
#define GFX_H

#include "z64.h"

extern Gfx setup_db[];
extern Gfx empty_dlist[];
extern void* z64_ItemIcons[130];

#define WORK_DISP __gfxCtx->work.p
#define POLY_OPA_DISP __gfxCtx->poly_opa.p
#define POLY_XLU_DISP __gfxCtx->poly_xlu.p
#define OVERLAY_DISP __gfxCtx->overlay.p
#define DEBUG_DISP __gfxCtx->debug.p

// __gfxCtx shouldn't be used directly.
// Use the DISP macros defined above when writing to display buffers.
#define OPEN_DISPS(gfxCtx)                  \
    {                                       \
        z64_gfx_t* __gfxCtx = gfxCtx; \
        int32_t __dispPad

#define CLOSE_DISPS(gfxCtx) \
    (void)0;                \
    }                       \
    (void)0

typedef struct {
    uint8_t* buf;
    uint16_t tile_w;
    uint16_t tile_h;
    uint16_t tile_count;
    uint8_t im_fmt;
    uint8_t im_siz;
    uint8_t bytes_per_texel;
} sprite_t;

extern sprite_t stones_sprite;
extern sprite_t medals_sprite;
extern sprite_t items_sprite;
extern sprite_t quest_items_sprite;
extern sprite_t font_sprite;
extern sprite_t dpad_sprite;
extern sprite_t triforce_sprite;
extern sprite_t song_note_sprite;
extern sprite_t key_rupee_clock_sprite;
extern sprite_t rupee_digit_sprite;
extern sprite_t item_digit_sprite;
extern sprite_t linkhead_skull_sprite;
extern sprite_t heart_sprite;
extern sprite_t ocarina_button_sprite;
extern sprite_t buttons_sprite;

void gfx_init();

void sprite_load(z64_disp_buf_t* db, sprite_t* sprite,
        int start_tile, int tile_count);
void sprite_draw(z64_disp_buf_t* db, sprite_t* sprite, int tile_index,
        int left, int top, int width, int height);

void sprite_texture(z64_disp_buf_t* db, sprite_t* sprite, int tile_index,
        int16_t left, int16_t top, int16_t width, int16_t height);
void sprite_texture_4b(z64_disp_buf_t* db, sprite_t* sprite, int tile_index,
        int16_t left, int16_t top, int16_t width, int16_t height);

void z64_Gfx_SetupDL_42Opa(z64_gfx_t* gfx_ctxt);

#endif
