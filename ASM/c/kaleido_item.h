#ifndef KALEIDO_ITEM_H
#define KALEIDO_ITEM_H

#include "z64.h"
#include "kaleido.h"

#define PAUSE_ITEM_NONE 999

#define PAUSE_CURSOR_TRANSITIONING_FROM_PAGE 9
#define PAUSE_CURSOR_PAGE_LEFT 10
#define PAUSE_CURSOR_PAGE_RIGHT 11

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
