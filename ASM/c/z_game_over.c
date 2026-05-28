#include "z64.h"

/**
 * Fixes child Link getting adult sword equipped when dying, if adult Link set temp B
 * (buttonStatus[0]) to adult sword before going back in time and child doesn't have
 * Kokiri sword equipped.
 */
void GameOver_RestoreBButton() {
    if (LINK_IS_ADULT) {
        // If current B item isn't an adult sword, and temp B is not 0 or Kokiri
        if (z64_file.button_items[0] != ITEM_SWORD_MASTER &&
            z64_file.button_items[0] != ITEM_SWORD_BGS &&
            z64_file.button_items[0] != ITEM_SWORD_KNIFE) {

            if (z64_file.buttonStatus[0] != 0 &&    // BTN_ENABLED
                z64_file.buttonStatus[0] != ITEM_SWORD_KOKIRI) {

                // Then, set temp B to B - else, no item
                z64_file.button_items[0] = z64_file.buttonStatus[0];
            } else {
                z64_file.button_items[0] = ITEM_NONE;
            }
        }
    } else {
        // If current B item isn't Kokiri sword, and temp B is not 0 or adult sword
        if (z64_file.button_items[0] != ITEM_SWORD_KOKIRI) {

            if (z64_file.buttonStatus[0] != 0 &&
                z64_file.buttonStatus[0] != ITEM_SWORD_MASTER &&
                z64_file.buttonStatus[0] != ITEM_SWORD_BGS &&
                z64_file.buttonStatus[0] != ITEM_SWORD_KNIFE) {

                z64_file.button_items[0] = z64_file.buttonStatus[0];
            } else {
                z64_file.button_items[0] = ITEM_NONE;
            }
        }
    }
}
