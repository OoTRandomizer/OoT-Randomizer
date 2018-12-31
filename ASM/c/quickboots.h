#ifndef QUICKBOOTS_H
#define QUICKBOOTS_H

#include "z64.h"

#define BLOCK_QUICK_BOOTS (0x00000001 | \
	0x00000002 | \
    0x00000080 | \
    0x00000400 | \
    0x10000000 | \
    0x20000000)

#define DISPLAY_QUICKBOOTS ((z64_file.link_age==0) && \
                           (z64_file.iron_boots || z64_file.hover_boots))

#define CAN_USE_QUICKBOOTS (((z64_link.state_flags_1 & BLOCK_QUICK_BOOTS) == 0) && \
                           ((uint32_t)z64_ctxt.state_dtor==z64_state_ovl_tab[3].vram_dtor) && \
                           (z64_file.file_index!=0xFF) && \
                           ((z64_event_state_1 & 0x20)==0) && \
                            DISPLAY_QUICKBOOTS)
#define DPAD_L 0x0200
#define DPAD_R 0x0100
#define DPAD_D 0x0400

void handle_quickboots();
void draw_quickboots();
void quickboots_init();

#endif