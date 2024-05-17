#ifndef INPUTVIEWER_H
#define INPUTVIEWER_H

#include "z64.h"
#include "gfx.h"
#include "text.h"

extern colorRGB16_t CFG_A_BUTTON_COLOR;
extern colorRGB16_t CFG_B_BUTTON_COLOR;
extern colorRGB16_t CFG_C_BUTTON_COLOR;

void draw_input_viewer(z64_disp_buf_t* db);

#endif
