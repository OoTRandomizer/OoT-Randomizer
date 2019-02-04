#include "ganon.h"

#include "z64.h"

uint8_t NO_ESCAPE_SEQUENCE = 0;

void check_ganon_entry() {
    if (NO_ESCAPE_SEQUENCE && z64_file.entrance_index == 0x0517) {
        z64_file.refill_hearts = 0x140;
        z64_file.magic = z64_file.magic_capacity_set * 0x30;
    }
}

