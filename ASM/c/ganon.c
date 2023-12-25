#include "ganon.h"
#include "refill.h"

#include "z64.h"

uint8_t NO_ESCAPE_SEQUENCE = 0;

void check_ganon_entry() {
    if (NO_ESCAPE_SEQUENCE && z64_file.entrance_index == 0x0517) {
        health_and_magic_refill();
    }
}
