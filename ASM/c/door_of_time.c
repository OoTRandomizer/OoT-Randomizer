#include "door_of_time.h"
#include "z64.h"

extern uint8_t DOT_CONDITION;

int32_t DemoKankyo_CutsceneFlags_Get_Hook(void* play, int16_t flag) {
    switch (DOT_CONDITION) {
        case 0: // open
        case 3: // stones
            return has_items_for_door_of_time();
        case 1: // sot
        case 2: // oot_sot
        case 4: // stones_sot
        case 5: // stones_oot_sot
            return has_items_for_door_of_time() && CutsceneFlags_Get(play, flag);
    }
}

bool has_items_for_door_of_time() {
    switch (DOT_CONDITION) {
        case 0: // open
        case 1: // sot
            return true;
        case 2: // oot_sot
            return z64_file.items[Z64_SLOT_OCARINA] == 0x08;
        case 3: // stones
        case 4: // stones_sot
            return (z64_file.quest_items & 0x1C0000) == 0x1C0000;
        case 5: // stones_oot_sot
            return (z64_file.quest_items & 0x1C0000) == 0x1C0000 && z64_file.items[Z64_SLOT_OCARINA] == 0x08;
    }
}
