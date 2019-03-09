#include "lake.h"

#include "z64.h"

void check_lake_fill() {
    if (z64_file.event_chk_inf[4] & 0x400) {
        z64_file.event_chk_inf[6] |= 0x200;
    }
}

