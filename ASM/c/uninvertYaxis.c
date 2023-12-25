#include "uninvertYaxis.h"

extern uint8_t CFG_UNINVERT_YAXIS_IN_FIRST_PERSON_CAMERA;

void manage_uninvert_yaxis() {

    if (CFG_UNINVERT_YAXIS_IN_FIRST_PERSON_CAMERA) {
        // Never if a choice textbox is on screen.
        if (z64_MessageGetState(((uint8_t*)(&z64_game)) + 0x20D8) == 4) {
            return;
        }
        if (z64_game.camera_mode == CAM_MODE_FIRST_PERSON ||
            z64_game.camera_mode == CAM_MODE_AIM_ADULT ||
            z64_game.camera_mode == CAM_MODE_AIM_BOOMERANG ||
            z64_game.camera_mode == CAM_MODE_AIM_CHILD) {
            z64_game.common.input[0].raw.y = -z64_game.common.input[0].raw.y;
            z64_game.common.input[0].y_diff = -z64_game.common.input[0].y_diff;
            z64_game.common.input[0].adjusted_y = -z64_game.common.input[0].adjusted_y;
        }
    }
}
