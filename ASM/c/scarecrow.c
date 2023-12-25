#include <stdint.h>

void store_scarecrow_fix(uint16_t* from, uint16_t* song) {
    for (int i = 0; i < 0x40; i+=2) {
        if (song[i] == 0x5700 || song[i] == 0) continue;
        if (song[i + 1] < 4) song[i + 1] = 4;
    }
}
