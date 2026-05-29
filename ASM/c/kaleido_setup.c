#include "kaleido_setup.h"

static bool sHoldingStart = false;

bool KaleidoSetup_Update_HasPressedStart(z64_game_t* play) {
    pad_t pressed_input = play->common.input[0].pad_pressed;
    pad_t held_input = play->common.input[0].raw.pad;

    if (pressed_input.s) {
        return true;
    }

    if (EASY_FRAME_BY_FRAME) {
        if (held_input.s) {
            if (sHoldingStart) {
                sHoldingStart = false;
                return true;
            }
            sHoldingStart = true;
        } else {
            sHoldingStart = false;
        }
    }

    return false;
}
