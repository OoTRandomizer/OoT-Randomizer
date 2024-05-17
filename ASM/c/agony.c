#include "agony.h"
#include "dungeon_info.h"
#include "gfx.h"
#include "item_effects.h"
#include "z64.h"

extern uint8_t CFG_DUNGEON_INFO_SILVER_RUPEES;

typedef struct {
    unsigned char alpha_level : 8;
    signed char   pos         : 2;
    unsigned char next        : 6;
} alpha_data_t;

static const alpha_data_t ALPHA_DATA[] = {
    {0x00,  0,  0}, // 0 - Zero
    {0x33, -1,  2}, // 1 - Fade in from zero
    {0x66,  1,  3}, // 2
    {0x99, -1,  4}, // 3
    {0xCC,  1,  5}, // 4
    {0xFF, -1,  6}, // 5 - Full intensity
    {0xFF,  1,  7}, // 6
    {0xFF, -1,  8}, // 7
    {0xFF,  1,  9}, // 8
    {0xE0, -1, 10}, // 9 - Fade out to hold
    {0xC2,  1, 11}, // 10
    {0xA3, -1, 12}, // 11
    {0x85,  1, 13}, // 12
    {0x66,  0, 13}, // 13 - Hold
    {0x44,  0, 15}, // 14 - Fade out
    {0x22,  0,  0}, // 15
    {0x85, -1, 17}, // 16 - Fade in from hold
    {0xA3,  1, 18}, // 17
    {0xC2, -1, 19}, // 18
    {0xE0,  1,  5}  // 19
};

#define ALPHA_ANIM_TERMINATE  0
#define ALPHA_ANIM_START      1
#define ALPHA_ANIM_HOLD      13
#define ALPHA_ANIM_FADE      14
#define ALPHA_ANIM_INTERRUPT 16

static const alpha_data_t* alpha_frame = ALPHA_DATA + ALPHA_ANIM_TERMINATE;

void agony_inside_radius_setup() {
}

void agony_outside_radius_setup() {
    if (alpha_frame == ALPHA_DATA + ALPHA_ANIM_HOLD) {
        alpha_frame = ALPHA_DATA + ALPHA_ANIM_FADE;
    }
}

void agony_vibrate_setup() {
    if (alpha_frame == ALPHA_DATA + ALPHA_ANIM_TERMINATE) {
        alpha_frame = ALPHA_DATA + ALPHA_ANIM_START;
    }
    else {
        alpha_frame = ALPHA_DATA + ALPHA_ANIM_INTERRUPT;
    }
}

void draw_agony_graphic(int hoffset, int voffset, unsigned char alpha) {
    // terminate if alpha level prohibited (changed areas)
    unsigned char maxalpha = (unsigned char)z64_game.hud_alpha_channels.rupees_keys_magic;
    if (maxalpha == 0xAA) maxalpha = 0xFF;

    if (alpha > maxalpha) {
        alpha = maxalpha;
    }

    z64_disp_buf_t* db = &(z64_ctxt.gfx->overlay);
    gSPDisplayList(db->p++, &setup_db);
    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha);
    sprite_load(db, &quest_items_sprite, 9, 1);
    sprite_draw(db, &quest_items_sprite, 0, 27+hoffset, 189+voffset, 16, 16);
    gDPPipeSync(db->p++);
}

void draw_agony() {
    if (alpha_frame != ALPHA_DATA + ALPHA_ANIM_TERMINATE) {
        unsigned char alpha = alpha_frame->alpha_level;
        int hoffset = alpha_frame->pos;
        alpha_frame = ALPHA_DATA + alpha_frame->next;
        int scene_index = z64_game.scene_index;
        int room_index = z64_game.room_index;
        int voffset = 0;
        if (scene_index < 0x11 && (z64_file.dungeon_keys[scene_index] >= 0 || bk_display)) {
            // small keys or boss key displayed
            voffset -= 17;
        }
        if (CFG_DUNGEON_INFO_SILVER_RUPEES) {
            for (int i = 0; i < dungeon_count; i++) {
                if (scene_index != dungeons[i].index) continue;

                dungeon_entry_t dungeon = dungeons[i];
                uint8_t* silver_rupee_puzzles = CFG_DUNGEON_IS_MQ[dungeon.index] ? dungeon.silver_rupee_puzzles_mq : dungeon.silver_rupee_puzzles_vanilla;
                for (int puzzle_idx = 0; puzzle_idx < 4; puzzle_idx++) {
                    if (silver_rupee_puzzles[puzzle_idx] == (uint8_t) -1) break;
                    silver_rupee_data_t silver_rupee_info = silver_rupee_vars[silver_rupee_puzzles[puzzle_idx]][CFG_DUNGEON_IS_MQ[dungeon.index]];
                    if (silver_rupee_info.room == room_index) {
                        // silver rupees displayed
                        voffset -= 17;
                        break;
                    }
                }
            }
        }
        draw_agony_graphic(hoffset, voffset, alpha);
    }
}
