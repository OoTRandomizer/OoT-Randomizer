#include "z64.h"
#include "gfx.h"
#include "text.h"
#include "displaygrottoname.h"

uint8_t DISPLAY_GROTTO_TIMER = 0;

const char grottoNames[][28] = {
  "Colossus Grotto",
  "LH Grotto",
  "ZR Storms Grotto",
  "ZR Fairy Grotto",
  "ZR Open Grotto",
  "DMC Hammer Grotto",
  "DMC Upper Grotto",
  "GC Grotto",
  "DMT Storms Grotto",
  "DMT Cow Grotto",
  "Kak Open Grotto",
  "Kak Redead Grotto",
  "HC Storms Grotto",
  "HF Tektite Grotto",
  "HF Near Kak Grotto",
  "HF Fairy Grotto",
  "HF Near Market Grotto",
  "HF Cow Grotto",
  "HF Inside Fence Grotto",
  "HF Open Grotto",
  "HF Southeast Grotto",
  "LLR Grotto",
  "SFM Wolfos Grotto",
  "SFM Storms Grotto",
  "SFM Fairy Grotto",
  "LW Scrubs Grotto",
  "LW Near Shortcuts Grotto",
  "KF Storms Grotto",
  "ZD Storms Grotto",
  "GF Storms Grotto",
  "GV Storms Grotto",
  "GV Octorok Grotto",
  "Deku Theater",
};

const char fairyNames[][24] = {
    "Colossus GF",
    "Hyrule Castle GF",
    "Ganon's Castle GF",
    "DM Crater GF",
    "DM Trail GF",
    "Zora's Fountain GF",
};

void DisplayGrottoName(z64_disp_buf_t* db) {
    if (!CFG_DISPLAY_GROTTO_NAMES) {
        return;
    }

    if (DISPLAY_GROTTO_TIMER != 0 || (z64_game.pause_ctxt.state == PAUSE_STATE_MAIN)) {
        const char* text;
        uint8_t alpha = 0xFF;

        if (CURRENT_GROTTO_ID != 255) {
            text = grottoNames[CURRENT_GROTTO_ID];
        } else {
            switch (z64_file.entrance_index) {
                case 0x588:
                    text = fairyNames[0];
                    break;
                case 0x578:
                    text = fairyNames[1];
                    break;
                case 0x4C2:
                    text = fairyNames[2];
                    break;
                case 0x4BE:
                    text = fairyNames[3];
                    break;
                case 0x315:
                    text = fairyNames[4];
                    break;
                case 0x371:
                    text = fairyNames[5];
                    break;
                default:
                    return; // paused probably
            }
        }

        if (z64_game.pause_ctxt.state != PAUSE_STATE_MAIN) {
            DISPLAY_GROTTO_TIMER--;
            if (DISPLAY_GROTTO_TIMER < 80) {
                alpha = DISPLAY_GROTTO_TIMER * 3 + 10;
                if (DISPLAY_GROTTO_TIMER < 60) {
                    DISPLAY_GROTTO_TIMER -= 3; // for alpha
                }
            }
        }

        gSPDisplayList(db->p++, &setup_db);
        gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
        gDPSetPrimColor(db->p++, 0, 0, 0, 0, 0, alpha);
        text_print_size(db, text, 11, 226, 10, 10);
        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha);
        text_print_size(db, text, 10, 225, 10, 10);
    }
}
