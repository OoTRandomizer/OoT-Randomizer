#include "model_text.h"
#include <stdbool.h>
#include "music.h"

uint16_t illegal_model = false;

bool adult_safe = false;
bool child_safe = false;

bool missing_dlist = false;

extern uint8_t CFG_SONG_NAME_STATE;

const int text_width = 5;
const int text_height = 10;

void draw_illegal_model_text(z64_disp_buf_t* db) {

    // Only draw when paused
    if (!(illegal_model && z64_game.pause_ctxt.state == PAUSE_STATE_MAIN)) {
        return;
    }

    // If custom music songs are displayed, only show the text in the inventory screen.
    if (CFG_SONG_NAME_STATE > SONG_NAME_NONE && z64_game.pause_ctxt.screen_idx != 0) {
        return;
    }

    int str_len = 41;
    if (missing_dlist) {
        str_len = 45;
    }

    // Setup draw location
    int total_w = str_len * text_width;
    int draw_x = (Z64_SCREEN_WIDTH * .5) - total_w / 2;
    int draw_y_text = 9;

    // Create collected/required string
    char text[str_len + 1];
    if (missing_dlist) {
        strncpy(text, "Racing advisory: model skeleton missing dlist\0", str_len + 1);
    } else {
        strncpy(text, "Racing advisory: irregular model skeleton\0", str_len + 1);
    }

    // Call setup display list
    gSPDisplayList(db->p++, &setup_db);
    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    gDPSetPrimColor(db->p++, 0, 0, 0xD7, 0x16, 0x0D, 0xFF);

    //Set text to print and flush it
    text_print_size(db, text, draw_x, draw_y_text, text_width, text_height);
}

typedef struct Limb {
    int x;
    int y;
    int z;
} Limb;

Limb adultSkeleton[] = {
    {0xFFC7, 0x0D31, 0x0000}, // Limb 0
    {0x0000, 0x0000, 0x0000}, // Limb 1
    {0x03B1, 0x0000, 0x0000}, // Limb 2
    {0xFE71, 0x0045, 0xFF07}, // Limb 3
    {0x051A, 0x0000, 0x0000}, // Limb 4
    {0x04E8, 0x0005, 0x000B}, // Limb 5
    {0xFE74, 0x004C, 0x0108}, // Limb 6
    {0x0518, 0x0000, 0x0000}, // Limb 7
    {0x04E9, 0x0006, 0x0003}, // Limb 8
    {0x0000, 0x0015, 0xFFF9}, // Limb 9
    {0x0570, 0xFEFD, 0x0000}, // Limb 10
    {0xFED6, 0xFD44, 0x0000}, // Limb 11
    {0x0000, 0x0000, 0x0000}, // Limb 12
    {0x040F, 0xFF54, 0x02A8}, // Limb 13
    {0x0397, 0x0000, 0x0000}, // Limb 14
    {0x02F2, 0x0000, 0x0000}, // Limb 15
    {0x040F, 0xFF53, 0xFD58}, // Limb 16
    {0x0397, 0x0000, 0x0000}, // Limb 17
    {0x02F2, 0x0000, 0x0000}, // Limb 18
    {0x03D2, 0xFD4C, 0x0156}, // Limb 19
    {0x0000, 0x0000, 0x0000}, // Limb 20
};

Limb childSkeleton[] = {
    {0x0000, 0x0948, 0x0000}, // Limb 0
    {0xFFFC, 0xFF98, 0x0000}, // Limb 1
    {0x025F, 0x0000, 0x0000}, // Limb 2
    {0xFF54, 0x0032, 0xFF42}, // Limb 3
    {0x02B9, 0x0000, 0x0000}, // Limb 4
    {0x0339, 0x0005, 0x000B}, // Limb 5
    {0xFF56, 0x0039, 0x00C0}, // Limb 6
    {0x02B7, 0x0000, 0x0000}, // Limb 7
    {0x0331, 0x0008, 0x0004}, // Limb 8
    {0x0000, 0xFF99, 0xFFF9}, // Limb 9
    {0x03E4, 0xFF37, 0xFFFF}, // Limb 10
    {0xFE93, 0xFD62, 0x0000}, // Limb 11
    {0x0000, 0x0000, 0x0000}, // Limb 12
    {0x02B8, 0xFF51, 0x01D2}, // Limb 13
    {0x0245, 0x0000, 0x0000}, // Limb 14
    {0x0202, 0x0000, 0x0000}, // Limb 15
    {0x02B8, 0xFF51, 0xFE2E}, // Limb 16
    {0x0241, 0x0000, 0x0000}, // Limb 17
    {0x020D, 0x0000, 0x0000}, // Limb 18
    {0x0291, 0xFDF5, 0x016F}, // Limb 19
    {0x0000, 0x0000, 0x0000}, // Limb 20
};

// Gets the model data
z64_mem_obj_t FindModelData() {
    for (int i = 0; i < 19; i++) {
        z64_mem_obj_t obj = z64_game.obj_ctxt.objects[i];
        // 0x14 = obj_link_boy, 0x15 = obj_link_child
        if (obj.id == 0x14) {
            return obj;
        } else if (obj.id == 0x15) {
            return obj;
        }
    }
    return z64_game.obj_ctxt.objects[0]; //Will be checked and rejected in calling function
}

//Search the model for the playas footer to find its stopping point
//This tells us where to stop searching for the hierarchy pointer
int FindSize(z64_mem_obj_t model, int maxsize) {
    char* data = (char*)model.data;
    const char* searchString = "!PlayAsManifest0";
    const int searchLen = 16;
    int searchIndex = 0;

    for (int i = 0; i < maxsize; i++) {
        // Byte matches next byte in string
        if (data[i] == searchString[searchIndex]) {
            searchIndex += 1;

            // All bytes have been found, so a match
            if (searchIndex == searchLen) {
                return i; //Return the address of the footer within the model data
            }
        } else {
            // Match has been broken, reset to start of string
            searchIndex = 0;
        }
    }

    // If the footer was not found, then return max size (should only happen with a vanilla model)
    return maxsize;
}

// Finds the address of the model's hierarchy so we can write the hierarchy pointer
// Based on
// https://github.com/hylian-modding/Z64Online/blob/master/src/Z64Online/common/cosmetics/UniversalAliasTable.ts
// function findHierarchy()
int FindHierarchy(z64_mem_obj_t model, int size) {
    // Scan until we find a segmented pointer which is 0x0C or 0x10 more than
    // the preceeding data and loop until something that's not a segmented pointer is found
    // then return the position of the last segemented pointer.
    char* data = (char*)model.data;
    for (int i = 0; i < size; i += 4) {
        if (data[i] == 0x06) {
            int possible = *(int*)(data + i) & 0x00FFFFFF;

            if (possible < size) {
                int possible2 = *(int*)(data + i - 4) & 0x00FFFFFF;
                int diff = possible - possible2;
                if (diff == 0x0C || diff == 0x10) {
                    int pos = i + 4;
                    int count = 1;
                    while (data[pos] == 0x06) {
                        pos += 4;
                        count += 1;
                    }
                    uint8_t a = data[pos];
                    if (a != count) {
                        continue;
                    }

                    return pos - 4;
                }
            }
        }
    }
    return -1;
}

bool check_skeleton(z64_mem_obj_t model, int hierarchy, Limb* skeleton) {
    char* data = (char*)model.data;
    // Get what the hierarchy pointer points to (pointer to limb 0)
    int limbPointer = *(int*)(data + hierarchy) & 0x00FFFFFF;
    // Get the limb this points to
    int limb = *(int*)(data + limbPointer) & 0x00FFFFFF;
    // Go through each limb in the table
    bool hasVanillaSkeleton = true;
    for (int i = 1; i < 21; i++) {
        int offset = limb + i * 0x10;
        // X, Y, Z components are 2 bytes each
        int limbX = *(uint16_t*)(data + offset);
        int limbY = *(uint16_t*)(data + offset + 2);
        int limbZ = *(uint16_t*)(data + offset + 4);
        int skeletonX = skeleton[i].x;
        int skeletonY = skeleton[i].y;
        int skeletonZ = skeleton[i].z;
        // Check if the X, Y, and Z components all match
        if (limbX != skeletonX || limbY != skeletonY || limbZ != skeletonZ) {
            return false;
        }
        int dlistPointer = *(uint8_t*)(data + offset + 8);
        // If this model should have a dlist, check that it does
        if (i != 2 && i != 9 && dlistPointer != 0x06) {
            // Set this variable so a special message will be displayed if the xyz coords are correct but a dlist is missing
            missing_dlist = true;
            return false;
        }
    }
    return true;
}

void check_model_skeletons() {
    // If it's already been marked illegal, no need to run code again
    // Or, if both models have been found to be safe, no need to check either
    if (illegal_model || (adult_safe && child_safe)) {
        return;
    }

    // Get the model's data
    z64_mem_obj_t model = FindModelData();

    // Decide which skeleton to use
    Limb* skeleton;
    if (model.id == 0x14) {
        skeleton = adultSkeleton;
        // If we already know adult is safe, no need to continue
        if (adult_safe) {
            return;
        }
    } else if (model.id == 0x15) {
        skeleton = childSkeleton;
        // If we already know child is safe, no need to continue
        if (child_safe) {
            return;
        }
    } else { // Safety if model file isn't found for some reason
        return;
    }

    // Get the maximum possible size of the object file by checking the object table
    z64_object_table_t obj_file = z64_object_table[model.id];
    int maxsize = obj_file.vrom_end - obj_file.vrom_start;

    // Get the actual length of the model data by checking for the footer (or lack thereof)
    int size = FindSize(model, maxsize);

    // Get the hierarchy pointer
    int hierarchy = FindHierarchy(model, size);
    if (hierarchy == -1) { // Safety if hierarchy is not found
        return;
    }

    // Check if the skeleton matches vanilla
    if (!check_skeleton(model, hierarchy, skeleton)) {
        illegal_model = 1;
    } else if (model.id == 0x14) {
        adult_safe = true;
    } else if (model.id == 0x15) {
        child_safe = true;
    }
}
