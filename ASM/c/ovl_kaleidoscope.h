#ifndef OVL_KALEIDOSCOPE_H
#define OVL_KALEIDOSCOPE_H

#include "z64.h"


#define FONT_CHAR_TEX_WIDTH 16
#define FONT_CHAR_TEX_HEIGHT 16
#define NUM_FONT_CHARS 95


typedef void(*kaleido_handler)(struct menu_ctx* menu, z64_game_t* globalCtx, z64_gfx_t* gfx);

typedef struct menu_ctx {
    int8_t curr_line;
    uint8_t total_lines;
    uint8_t curr_min_line;
    uint8_t cursor_delay;
    kaleido_handler handler;
    void* extra;
} menu_ctx;

typedef void(*kaleido_base_handler)(z64_game_t* globalCtx, z64_gfx_t* gfx);
typedef void(*pause_mapmark_draw_func)(z64_game_t* globalCtx);


typedef enum {
    MENU_PAGE_MAP = 0x00,
    MENU_PAGE_SOULS,
    MENU_PAGE_MAX
} MENU_PAGE;

void init_new_menus();
void soul_menu_handler(menu_ctx* menu_ctx, z64_game_t* globalCtx, z64_gfx_t* gfx);
int print_string(z64_game_t* globalCtx, char* str, int x, int y, float scale);

extern void* KaleidoManager_GetRamAddr(void* vram);

#endif
