#include "gfx.h"

#include "util.h"
#include "z64.h"

void disp_buf_init(z64_disp_buf_t *db, Gfx *buf, int size) {
    db->size = size;
    db->buf = buf;
    db->p = buf;
    db->d = (Gfx *)((char *)buf + size);
}

sprite_t stones_sprite = {
    NULL, 16, 16, 3,
    G_IM_FMT_RGBA, G_IM_SIZ_32b, 4
};

sprite_t medals_sprite = {
    NULL, 16, 16, 6,
    G_IM_FMT_IA, G_IM_SIZ_8b, 1
};

sprite_t items_sprite = {
    NULL, 32, 32, 90,
    G_IM_FMT_RGBA, G_IM_SIZ_32b, 4
};

sprite_t quest_items_sprite = {
    NULL, 24, 24, 20,
    G_IM_FMT_RGBA, G_IM_SIZ_32b, 4
};

sprite_t font_sprite = {
    NULL, 8, 14, 95,
    G_IM_FMT_IA, G_IM_SIZ_8b, 1
};

sprite_t dpad_sprite = {
    NULL, 32, 32, 1,
    G_IM_FMT_IA, G_IM_SIZ_16b, 2
};  

int sprite_bytes_per_tile(sprite_t *sprite) {
    return sprite->tile_w * sprite->tile_h * sprite->bytes_per_texel;
}

int sprite_bytes(sprite_t *sprite) {
    return sprite->tile_count * sprite_bytes_per_tile(sprite);
}

void sprite_load(z64_disp_buf_t *db, sprite_t *sprite,
        int start_tile, int tile_count) {
    int width = sprite->tile_w;
    int height = sprite->tile_h * tile_count;
    gDPLoadTextureTile(db->p++,
            sprite->buf + (start_tile * sprite_bytes_per_tile(sprite)),
            sprite->im_fmt, sprite->im_siz,
            width, height,
            0, 0,
            width - 1, height - 1,
            0,
            G_TX_WRAP, G_TX_WRAP,
            G_TX_NOMASK, G_TX_NOMASK,
            G_TX_NOLOD, G_TX_NOLOD);
}

void sprite_draw(z64_disp_buf_t *db, sprite_t *sprite, int tile_index,
        int left, int top, int width, int height) {
    int width_factor = (1<<10) * sprite->tile_w / width;
    int height_factor = (1<<10) * sprite->tile_h / height;

    gSPTextureRectangle(db->p++,
            left<<2, top<<2,
            (left + width)<<2, (top + height)<<2,
            0,
            0, (tile_index * sprite->tile_h)<<5,
            width_factor, height_factor);
}

z64_disp_buf_t setup_db = {};

void draw_setup(z64_disp_buf_t *db) {
    gDPPipeSync(db->p++);

    gSPLoadGeometryMode(db->p++, 0);
    gDPSetScissor(db->p++, G_SC_NON_INTERLACE,
                  0, 0, Z64_SCREEN_WIDTH, Z64_SCREEN_HEIGHT);
    gDPSetAlphaDither(db->p++, G_AD_DISABLE);
    gDPSetColorDither(db->p++, G_CD_DISABLE);
    gDPSetAlphaCompare(db->p++, G_AC_NONE);
    gDPSetDepthSource(db->p++, G_ZS_PRIM);
    gDPSetCombineKey(db->p++, G_CK_NONE);
    gDPSetTextureConvert(db->p++, G_TC_FILT);
    gDPSetTextureDetail(db->p++, G_TD_CLAMP);
    gDPSetTexturePersp(db->p++, G_TP_NONE);
    gDPSetTextureLOD(db->p++, G_TL_TILE);
    gDPSetTextureLUT(db->p++, G_TT_NONE);
    gDPPipelineMode(db->p++, G_PM_NPRIMITIVE);

    gDPSetCycleType(db->p++, G_CYC_1CYCLE);
    gDPSetRenderMode(db->p++, G_RM_XLU_SURF, G_RM_XLU_SURF2);
    gDPSetTextureFilter(db->p++, G_TF_BILERP);

    gSPEndDisplayList(db->p++);
}

extern char FONT_TEXTURE;
extern char DPAD_TEXTURE;
#define font_texture_raw ((uint8_t *)&FONT_TEXTURE)
#define dpad_texture_raw ((uint8_t *)&DPAD_TEXTURE)

void gfx_init() {
    file_t title_static = {
        NULL, z64_file_select_static_vaddr, z64_file_select_static_vsize
    };
    file_init(&title_static);

    file_t icon_item_24_static = {
        NULL, z64_icon_item_24_static_vaddr, z64_icon_item_24_static_vsize
    };
    file_init(&icon_item_24_static);

    file_t icon_item_static = {
        NULL, z64_icon_item_static_vaddr, z64_icon_item_static_vsize
    };
    file_init(&icon_item_static);

    stones_sprite.buf = title_static.buf + 0x2A300;
    medals_sprite.buf = title_static.buf + 0x2980;
    items_sprite.buf = icon_item_static.buf;
    quest_items_sprite.buf = icon_item_24_static.buf;
    dpad_sprite.buf = dpad_texture_raw;

    int font_bytes = sprite_bytes(&font_sprite);
    font_sprite.buf = heap_alloc(font_bytes);
    for (int i = 0; i < font_bytes / 2; i++) {
        font_sprite.buf[2*i] = (font_texture_raw[i] >> 4) | 0xF0;
        font_sprite.buf[2*i + 1] = font_texture_raw[i] | 0xF0;
    }

    int setup_size = 32 * sizeof(Gfx);
    Gfx *setup_buf = heap_alloc(setup_size);
    disp_buf_init(&setup_db, setup_buf, setup_size);
    draw_setup(&setup_db);
}
