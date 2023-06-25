#include "ocarina_buttons.h"

uint8_t c_block_ocarina() {
    uint8_t res = 0;
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 0)) {
        res |= 1 << 0;
    }
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 1)) {
        res |= 1 << 1;
    }
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 2)) {
        res |= 1 << 2;
    }
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 3)) {
        res |= 1 << 3;
    }
    if (!(z64_file.scene_flags[0x50].unk_00_ & 1 << 4)) {
        res |= 1 << 4;
    }
    return res;
}
