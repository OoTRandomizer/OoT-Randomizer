#include "gfx.h"
#include "agony.h"
#include "dpad.h"

static signed char amp[20] =  {0, 1, 2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 6, 5, 4, 3, 2, 1, 0};
static signed char sign[20] = {1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1};

#define DIST_THRESHOLD 300
#define DIST_MULT (0xFFFFFFFF / DIST_THRESHOLD)

static unsigned int best_dist = DIST_THRESHOLD + 1;
static unsigned int agony_ticks = 0;

//unknown 00 is a pointer to some vector transformation when the sound is tied to an actor. actor + 0x3E, when not tied to an actor (map), always 80104394
//unknown 01 is always 4 in my testing
//unknown 02 is a pointer to some kind of audio configuration Always 801043A0 in my testing
//unknown 03 is always a3 in my testing
//unknown 04 is always a3 + 0x08 in my testing (801043A8)
typedef void(*playsfx_t)(uint16_t sfx, z64_xyzf_t *unk_00_, int8_t unk_01_ , float *unk_02_, float *unk_03_, float *unk_04_);

#define z64_playsfx   ((playsfx_t)      0x800C806C)

void update_agony_distance(z64_actor_t* grotto) {
    unsigned int dist = (unsigned int)grotto->xzdist_from_link;
    if (dist < best_dist) {
        best_dist = dist;
    }
}

static void draw_agony_graphic(int offset) {
    z64_disp_buf_t *db = &(z64_ctxt.gfx->overlay);
    gSPDisplayList(db->p++, &setup_db);
    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    uint16_t alpha = z64_game.hud_alpha_channels.minimap;
    
    if (alpha == 0xAA) alpha = 0xFF;
    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha);
    sprite_load(db, &dpad_sprite, 0, 1);
    sprite_draw(db, &dpad_sprite, 0, 13, 206+offset, 16, 16);

    gDPPipeSync(db->p++);
}

void draw_agony() {
    if (best_dist <= DIST_THRESHOLD) {
        unsigned int amp_reduction = (best_dist * DIST_MULT) >> 29;
        int amplitude = amp[agony_ticks] - amp_reduction;
        if (amplitude < 0) {
            amplitude = 0;
        }
        draw_agony_graphic(amplitude * sign[agony_ticks]); 
        best_dist = DIST_THRESHOLD + 1;
        ++agony_ticks;
        if (agony_ticks >= 20) {
            agony_ticks = 0;
        }
    }
    else {
        agony_ticks = 0;
    }
}

