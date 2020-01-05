#include "gfx.h"
#include "agony.h"

static signed char amp[20] =  {1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1};
static signed char sign[20] = {1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1};

#define DIST_THRESHOLD 190
#define DIST_MULT (0xFFFFFFFF / DIST_THRESHOLD)
#define ALPHA_STEP 0x10

static unsigned int best_dist = DIST_THRESHOLD + 1;
static unsigned char agony_ticks = 0;
static unsigned char agony_alpha = 0;

void update_agony_distance(z64_actor_t* grotto) {
    unsigned int xzdist = (unsigned int)grotto->xzdist_from_link;
    unsigned int distsq = (unsigned int)grotto->distsq_from_link;
    if (xzdist < best_dist && distsq <= DIST_THRESHOLD * DIST_THRESHOLD) {
        best_dist = xzdist;
    }
}

static void draw_agony_graphic(int offset) {
    uint16_t maxalpha = z64_game.hud_alpha_channels.minimap;
    if (maxalpha == 0xAA) maxalpha = 0xFF;
    if (agony_alpha > maxalpha) agony_alpha = (unsigned char)maxalpha;

    z64_disp_buf_t *db = &(z64_ctxt.gfx->overlay);
    gSPDisplayList(db->p++, &setup_db);
    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, agony_alpha);
    sprite_load(db, &quest_items_sprite, 9, 1);
    sprite_draw(db, &quest_items_sprite, 0, 26+offset, 190, 16, 16);

    gDPPipeSync(db->p++);
}

static void increase_alpha() {
    int alpha = (int)agony_alpha;
    alpha += ALPHA_STEP;
    if (alpha > 0xFF) {
        alpha = 0xFF;
    }
    agony_alpha = (unsigned char)alpha;
}

static void decrease_alpha() {
    int alpha = (int)agony_alpha;
    alpha -= ALPHA_STEP;
    if (alpha < 0) {
        alpha = 0;
    }
    agony_alpha = (unsigned char)alpha;
}

void draw_agony() {
    if (best_dist <= DIST_THRESHOLD) {
        increase_alpha();
        unsigned int amp_reduction = (best_dist * DIST_MULT) >> 29; // 0-7
        int amplitude = amp[agony_ticks] - amp_reduction;
        if (amplitude < 0) {
            amplitude = 0;
        }
        else {
            amplitude = (int)(((unsigned int)amplitude + 1) >> 1);
            amplitude *= sign[agony_ticks];
        }
        draw_agony_graphic(amplitude);
        best_dist = DIST_THRESHOLD + 1;
        ++agony_ticks;
        if (agony_ticks >= 20) {
            agony_ticks = 0;
        }
    }
    else {
        agony_ticks = 0;
        decrease_alpha();
        if (agony_alpha > 0) {
            draw_agony_graphic(0);
        }
    }
}

