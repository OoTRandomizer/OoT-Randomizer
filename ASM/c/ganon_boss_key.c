#include <stdbool.h>
#include "get_items.h"
#include "z64.h"

int num_to_bits[16] = { 0, 1, 1, 2, 1, 2, 2, 3,
                        1, 2, 2, 3, 2, 3, 3, 4 };

// https://www.geeksforgeeks.org/count-set-bits-in-an-integer/
unsigned int countSetBitsRec(unsigned int num)
{
    int nibble = 0;
    if (0 == num)
        return num_to_bits[0];

    // Find last nibble
    nibble = num & 0xf;

    // Use pre-stored values to find count
    // in last nibble plus recursively add
    // remaining nibbles.
    return num_to_bits[nibble] + countSetBitsRec(num >> 4);
}

uint8_t GANON_BOSS_KEY_CONDITION = 0;
uint16_t GANON_BOSS_KEY_CONDITION_COUNT = 0;
void give_ganon_boss_key() {
    if (z64_file.file_index != 255 && GANON_BOSS_KEY_CONDITION && !z64_file.dungeon_items[10].boss_key) {
        bool give_boss_key = false;
        switch (GANON_BOSS_KEY_CONDITION) {
            case 1: // Medallions
                if (countSetBitsRec(z64_file.quest_items & 0x3F) >= GANON_BOSS_KEY_CONDITION_COUNT)
                    give_boss_key = true;
                break;
            case 2: // Dungeons
                if (countSetBitsRec(z64_file.quest_items & 0x1C003F) >= GANON_BOSS_KEY_CONDITION_COUNT)
                    give_boss_key = true;
                break;
            case 3: // Stones
                if (countSetBitsRec(z64_file.quest_items & 0x1C0000) >= GANON_BOSS_KEY_CONDITION_COUNT)
                    give_boss_key = true;
                break;
            case 4: // Tokens
                if (z64_file.gs_tokens >= GANON_BOSS_KEY_CONDITION_COUNT)
                    give_boss_key = true;
                break;
        }

        if (give_boss_key) {
            push_delayed_item(0x03);
        }
    }
}