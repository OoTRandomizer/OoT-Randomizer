#ifndef TRIFORCE_H
#define TRIFORCE_H

#include "z64.h"
#include "gfx.h"
#include "text.h"
#include "util.h"
#include "model_text.h"

extern uint16_t TRIFORCE_HUNT_ENABLED;
extern uint16_t TRIFORCE_PIECES_REQUIRED;

void draw_triforce_count(z64_disp_buf_t* db);
void set_triforce_render();

#define BLOCK_TRIFORCE (0x00000001 | \
                    0x00000002 | \
                    0x00000080 | \
                    0x00000400 | \
                    0x10000000 | \
                    0x20000000)

#define CAN_DRAW_TRIFORCE   (((z64_link.state_flags_1 & BLOCK_TRIFORCE ) == 0) && \
                            ((uint32_t)z64_ctxt.state_dtor==z64_state_ovl_tab[3].vram_dtor) && \
                            (z64_file.game_mode == 0) && \
                            ((z64_event_state_1 & 0x20) == 0))

#endif
