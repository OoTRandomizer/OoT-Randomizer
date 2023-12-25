#include "music.h"

extern uint8_t CFG_SPEEDUP_MUSIC_FOR_LAST_TRIFORCE_PIECE;
extern uint8_t CFG_SLOWDOWN_MUSIC_WHEN_LOWHP;

static uint16_t previousSeqIndexChange = 0;
static uint8_t isSlowedDown = 0;
static uint8_t isSpeedup = 0;

void manage_music_changes() {
    if (CFG_SPEEDUP_MUSIC_FOR_LAST_TRIFORCE_PIECE && !isSlowedDown) {
        if (z64_file.scene_flags[0x48].unk_00_ == TRIFORCE_PIECES_REQUIRED - 1 &&
            z64_Audio_GetActiveSeqId(0) != previousSeqIndexChange) {
            // One tone up : 2^(2/12)
            z64_ScalePitchAndTempo(1.12246f, 0);
            previousSeqIndexChange = z64_Audio_GetActiveSeqId(0);
            isSpeedup = 1;
        }
    }
    if (CFG_SLOWDOWN_MUSIC_WHEN_LOWHP) {
        if (Health_IsCritical()) {
            if (z64_Audio_GetActiveSeqId(0) != previousSeqIndexChange || isSpeedup) {
                // One tone down : 2^(-2/12)
                z64_ScalePitchAndTempo(0.89089f, 0);
                previousSeqIndexChange = z64_Audio_GetActiveSeqId(0);
                isSlowedDown = 1;
                isSpeedup = 0;
            }
        } else if (isSlowedDown) {
            z64_ScalePitchAndTempo(1.0f, 0);
            isSlowedDown = 0;
            previousSeqIndexChange = 0;
        }
    }
}

_Bool Health_IsCritical(void) {
    int16_t criticalHealth;

    if (z64_file.energy_capacity <= 0x50) {
        criticalHealth = 0x10;
    } else if (z64_file.energy_capacity <= 0xA0) {
        criticalHealth = 0x18;
    } else if (z64_file.energy_capacity <= 0xF0) {
        criticalHealth = 0x20;
    } else {
        criticalHealth = 0x2C;
    }

    if (criticalHealth >= z64_file.energy && z64_file.energy > 0) {
        return true;
    } else {
        return false;
    }
}
