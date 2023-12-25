#include "ocarina_buttons.h"

uint8_t c_block_ocarina() {
    uint8_t res = 0;
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 0)) { // A
        res |= 1 << 0;
    }
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 1)) { // C up
        res |= 1 << 1;
    }
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 2)) { // C down
        res |= 1 << 2;
    }
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 3)) { // C left
        res |= 1 << 3;
    }
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 4)) { // C right
        res |= 1 << 4;
    }
    return res;
}
extern uint8_t EPONAS_SONG_NOTES;
int8_t can_spawn_epona() {
    if (!SHUFFLE_OCARINA_BUTTONS) {
        return 1;
    }
    return (c_block_ocarina() & EPONAS_SONG_NOTES) ? 0 : 1;
}
