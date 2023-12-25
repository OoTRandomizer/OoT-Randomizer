#include "z64.h"

int8_t curr_scene_setup;

// Determine the current scene setup and set it in the curr_scene_setup global.
// See https://wiki.cloudmodding.com/oot/Scenes_and_Rooms#Alternate_Header_List:
void get_current_scene_setup_number() {
    z64_scene_command* cmd = z64_game.scene_segment;

    // If the scene_setup_index is 0 then we don't need to look any further.
    if (z64_file.scene_setup_index == 0) {
        curr_scene_setup = 0;
        return;
    }

    // If the scene_setup_index is > 3 then we're probably in a cutscene so just return -1.
    if (z64_file.scene_setup_index > 3) {
        curr_scene_setup = -1;
        return;
    }

    // Loop through the scene headers and look for alternate header lists.
    while (1) {
        if (cmd->code == 0x14) { // End of header command.
            break;
        }

        if (cmd->code == 0x18) { //Alternate header command
            // Get segment number from alternate header command
            uint8_t segment = (cmd->data2 << 4) >> 28;
            // Get segment offset from alternate header command
            uint32_t segment_offset = (cmd->data2 & 0x00FFFFFF);
            // Get a pointer to the alternate header list
            void** alternate_header = (void* *)(z64_game.scene_segment + segment_offset);
            uint8_t i = z64_file.scene_setup_index;
            // Starting, at scene_setup_index, scan towards the front of list to find the first non-null entry.
            while (i > 0) {
                if ((alternate_header)[i-1] != NULL) { // Found a non-null entry so use this as our setup.
                    curr_scene_setup = i;
                    return;
                }
                i--;
            }

        }
        cmd++;
    }
    curr_scene_setup = 0;
}
