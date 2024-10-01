#ifndef OCARINA_BUTTONS_H
#define OCARINA_BUTTONS_H
#include "z64.h"
#include "text.h"
#include "color.h"

uint8_t c_block_ocarina();
int8_t can_spawn_epona();
bool has_ocarina_button(uint8_t button);

extern uint8_t SHUFFLE_OCARINA_BUTTONS;

typedef enum {
    OCARINA_A_BUTTON = 1 << 0,
    OCARINA_C_UP_BUTTON = 1 << 1,
    OCARINA_C_DOWN_BUTTON = 1 << 2,
    OCARINA_C_LEFT_BUTTON = 1 << 3,
    OCARINA_C_RIGHT_BUTTON = 1 << 4,
} OcarinaButtons;
void draw_ocarina_melodies(z64_disp_buf_t* db);
#endif
