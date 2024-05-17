#ifndef KALEIDO_ITEM_H
#define KALEIDO_ITEM_H

#include "z64.h"
#include "kaleido.h"

#define PAUSE_ITEM_NONE 999

#define PAUSE_CURSOR_TRANSITIONING_FROM_PAGE 9
#define PAUSE_CURSOR_PAGE_LEFT 10
#define PAUSE_CURSOR_PAGE_RIGHT 11

typedef enum {
    /*  0 */ PAUSE_STATE_OFF,
    /*  1 */ PAUSE_STATE_WAIT_LETTERBOX, // Request no letterboxing and wait for it.
    /*  2 */ PAUSE_STATE_WAIT_BG_PRERENDER, // Wait for the pause background prerender to be done.
    /*  3 */ PAUSE_STATE_INIT, // Load data and initialize/setup various things.
    /*  4 */ PAUSE_STATE_OPENING_1, // Animate the pause menu coming together with rotations and other animations.
    /*  5 */ PAUSE_STATE_OPENING_2, // Finish some animations for opening the menu.
    /*  6 */ PAUSE_STATE_MAIN, // Pause menu ready for player inputs.
    /*  7 */ PAUSE_STATE_SAVE_PROMPT,  // Save prompt in the pause menu
    /*  8 */ PAUSE_STATE_8,
    /*  9 */ PAUSE_STATE_9,
    /* 10 */ PAUSE_STATE_10,
    /* 11 */ PAUSE_STATE_11,
    /* 12 */ PAUSE_STATE_12,
    /* 13 */ PAUSE_STATE_13,
    /* 14 */ PAUSE_STATE_14,
    /* 15 */ PAUSE_STATE_15,
    /* 16 */ PAUSE_STATE_16,
    /* 17 */ PAUSE_STATE_17,
    /* 18 */ PAUSE_STATE_CLOSING, // Animate the pause menu closing
    /* 19 */ PAUSE_STATE_RESUME_GAMEPLAY // Handles returning to normal gameplay once the pause menu is visually closed
} PauseState;

// Sub-states of PAUSE_STATE_MAIN
typedef enum {
    /* 0 */ PAUSE_MAIN_STATE_IDLE,
    /* 1 */ PAUSE_MAIN_STATE_1,
    /* 2 */ PAUSE_MAIN_STATE_2,
    /* 3 */ PAUSE_MAIN_STATE_3,
    /* 4 */ PAUSE_MAIN_STATE_4,
    /* 5 */ PAUSE_MAIN_STATE_5,
    /* 6 */ PAUSE_MAIN_STATE_6,
    /* 7 */ PAUSE_MAIN_STATE_7,
    /* 8 */ PAUSE_MAIN_STATE_8,
    /* 9 */ PAUSE_MAIN_STATE_9
} PauseMainState;

extern uint8_t z64_AmmoItems[16];
extern void* z64_EquippedItemOutlineTex[0x400];

/* Reimplemented */
void KaleidoScope_DrawItemSelect(z64_game_t* play);

/* Referenced */
void KaleidoScope_DrawAmmoCount(z64_pause_ctxt_t* pause_ctxt, z64_gfx_t* gfx_ctxt, int16_t item);
void KaleidoScope_SetCursorVtx(z64_pause_ctxt_t* pause_ctxt, uint16_t index, Vtx* vtx);
Gfx* KaleidoScope_QuadTextureIA8(Gfx* gfx_ctx, void* texture, int16_t width, int16_t height, uint16_t point);
void KaleidoScope_MoveCursorToSpecialPos(z64_game_t* play, uint16_t special_position);
void KaleidoScope_DrawQuadTextureRGBA32(z64_gfx_t* gfx_ctxt, void* texture, uint16_t width, uint16_t height, uint16_t point);
void KaleidoScope_DrawCursor(z64_game_t* play, int16_t page_index);

#endif //KALEIDO_ITEM_H
