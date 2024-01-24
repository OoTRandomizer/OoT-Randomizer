#ifndef OCARINA_BUTTONS_H
#define OCARINA_BUTTONS_H
#include "z64.h"
#include "text.h"
#include "color.h"

uint8_t c_block_ocarina();
int8_t can_spawn_epona();

extern uint8_t SHUFFLE_OCARINA_BUTTONS;

void draw_ocarina_melodies(z64_disp_buf_t* db);
#endif
