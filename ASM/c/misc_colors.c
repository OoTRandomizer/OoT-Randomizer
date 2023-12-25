#include <stdint.h>
#include "misc_colors.h"
#include "rainbow.h"
#include "z64.h"

#define SWORD_CYCLE_FRAMES_OUTER 10
#define SWORD_CYCLE_FRAMES_INNER 12

static uint32_t frames = 0;

extern uint8_t CFG_RAINBOW_SWORD_INNER_ENABLED;
extern uint8_t CFG_RAINBOW_SWORD_OUTER_ENABLED;

void update_sword_trail_colors()
{
    colorRGBA8_t* sword_trail_colors = (colorRGBA8_t*)0x80115DCE;

    if (CFG_RAINBOW_SWORD_INNER_ENABLED)
    {
        colorRGB8_t color_inner = get_rainbow_color(frames, SWORD_CYCLE_FRAMES_INNER);
        sword_trail_colors[1].color = color_inner;
        sword_trail_colors[3].color = color_inner;
    }

    if (CFG_RAINBOW_SWORD_OUTER_ENABLED)
    {
        colorRGB8_t color_outer = get_rainbow_color(frames, SWORD_CYCLE_FRAMES_OUTER);
        sword_trail_colors[0].color = color_outer;
        sword_trail_colors[2].color = color_outer;
    }
}

#define BOOM_CYCLE_FRAMES_OUTER 5
#define BOOM_CYCLE_FRAMES_INNER 6

extern colorRGB8_t CFG_BOOM_TRAIL_INNER_COLOR;
extern colorRGB8_t CFG_BOOM_TRAIL_OUTER_COLOR;

extern uint8_t CFG_RAINBOW_BOOM_TRAIL_INNER_ENABLED;
extern uint8_t CFG_RAINBOW_BOOM_TRAIL_OUTER_ENABLED;

void update_boomerang_trail_colors()
{
    z64_actor_t* boomerang = z64_link.boomerang_actor;
    if (boomerang != NULL && boomerang->main_proc != NULL)
    {
        uint32_t effect_index = *((uint32_t*)(((uint32_t)boomerang) + 0x1C8));

        if (effect_index < 31)
        {
            z64_trail_t* trail = ((z64_trail_t*)0x80115C3C) + effect_index - 3;

            if (CFG_RAINBOW_BOOM_TRAIL_INNER_ENABLED)
            {
                trail->fx.p1_start.color = get_rainbow_color(frames, BOOM_CYCLE_FRAMES_INNER);
                trail->fx.p1_end.color = get_rainbow_color(frames + 2 * BOOM_CYCLE_FRAMES_INNER, BOOM_CYCLE_FRAMES_INNER);
            }
            else
            {
                trail->fx.p1_start.color = CFG_BOOM_TRAIL_INNER_COLOR;
                trail->fx.p1_end.color = CFG_BOOM_TRAIL_INNER_COLOR;
            }

            if (CFG_RAINBOW_BOOM_TRAIL_OUTER_ENABLED)
            {
                trail->fx.p2_start.color = get_rainbow_color(frames, BOOM_CYCLE_FRAMES_OUTER);
                trail->fx.p2_end.color = get_rainbow_color(frames + 2 * BOOM_CYCLE_FRAMES_OUTER, BOOM_CYCLE_FRAMES_OUTER);
            }
            else
            {
                trail->fx.p2_start.color = CFG_BOOM_TRAIL_OUTER_COLOR;
                trail->fx.p2_end.color = CFG_BOOM_TRAIL_OUTER_COLOR;
            }
        }
    }
}

#define BOMBCHU_CYCLE_FRAMES_OUTER 7
#define BOMBCHU_CYCLE_FRAMES_INNER 9

extern colorRGB8_t CFG_BOMBCHU_TRAIL_INNER_COLOR;
extern colorRGB8_t CFG_BOMBCHU_TRAIL_OUTER_COLOR;

extern uint8_t CFG_RAINBOW_BOMBCHU_TRAIL_INNER_ENABLED;
extern uint8_t CFG_RAINBOW_BOMBCHU_TRAIL_OUTER_ENABLED;

void update_bombchu_trail_colors()
{
    int inner_enabled = !(CFG_BOMBCHU_TRAIL_INNER_COLOR.r == 0xFA &&
                          CFG_BOMBCHU_TRAIL_INNER_COLOR.g == 0x00 &&
                          CFG_BOMBCHU_TRAIL_INNER_COLOR.b == 0x00);
    int outer_enabled = !(CFG_BOMBCHU_TRAIL_OUTER_COLOR.r == 0xFA &&
                          CFG_BOMBCHU_TRAIL_OUTER_COLOR.g == 0x00 &&
                          CFG_BOMBCHU_TRAIL_OUTER_COLOR.b == 0x00);

    colorRGB8_t rainbow_color_inner_start = get_rainbow_color(frames, BOMBCHU_CYCLE_FRAMES_INNER);
    colorRGB8_t rainbow_color_inner_end = get_rainbow_color(frames + 2 * BOMBCHU_CYCLE_FRAMES_INNER, BOMBCHU_CYCLE_FRAMES_INNER);
    colorRGB8_t rainbow_color_outer_start = get_rainbow_color(frames, BOMBCHU_CYCLE_FRAMES_OUTER);
    colorRGB8_t rainbow_color_outer_end = get_rainbow_color(frames + 2 * BOMBCHU_CYCLE_FRAMES_OUTER, BOMBCHU_CYCLE_FRAMES_OUTER);

    z64_actor_t* explosive = z64_game.actor_list[ACTORTYPE_EXPLOSIVES].first;
    while (explosive != NULL)
    {
        if (explosive->main_proc != NULL && explosive->actor_id == 0xDA) // En_Bom_Chu
        {
            uint32_t effect_index_1 = *((uint32_t*)(((uint32_t)explosive) + 0x16C));
            uint32_t effect_index_2 = *((uint32_t*)(((uint32_t)explosive) + 0x170));

            z64_trail_t* trail_1 = ((z64_trail_t*)0x80115C3C) + effect_index_1 - 3;
            z64_trail_t* trail_2 = ((z64_trail_t*)0x80115C3C) + effect_index_2 - 3;

            if (CFG_RAINBOW_BOMBCHU_TRAIL_INNER_ENABLED)
            {
                trail_1->fx.p1_start.color = rainbow_color_inner_start;
                trail_2->fx.p1_start.color = rainbow_color_inner_start;
                trail_1->fx.p1_end.color = rainbow_color_inner_end;
                trail_2->fx.p1_end.color = rainbow_color_inner_end;
            }
            else if (inner_enabled)
            {
                trail_1->fx.p1_start.color = CFG_BOMBCHU_TRAIL_INNER_COLOR;
                trail_2->fx.p1_start.color = CFG_BOMBCHU_TRAIL_INNER_COLOR;
                trail_1->fx.p1_end.color = CFG_BOMBCHU_TRAIL_INNER_COLOR;
                trail_2->fx.p1_end.color = CFG_BOMBCHU_TRAIL_INNER_COLOR;
            }

            if (CFG_RAINBOW_BOMBCHU_TRAIL_OUTER_ENABLED)
            {
                trail_1->fx.p2_start.color = rainbow_color_outer_start;
                trail_2->fx.p2_start.color = rainbow_color_outer_start;
                trail_1->fx.p2_end.color = rainbow_color_outer_end;
                trail_2->fx.p2_end.color = rainbow_color_outer_end;
            }
            else if (outer_enabled)
            {
                trail_1->fx.p2_start.color = CFG_BOMBCHU_TRAIL_OUTER_COLOR;
                trail_2->fx.p2_start.color = CFG_BOMBCHU_TRAIL_OUTER_COLOR;
                trail_1->fx.p2_end.color = CFG_BOMBCHU_TRAIL_OUTER_COLOR;
                trail_2->fx.p2_end.color = CFG_BOMBCHU_TRAIL_OUTER_COLOR;
            }
        }

        explosive = explosive->next;
    }
}

uint32_t get_bombchu_back_color(float brightness)
{
    colorRGB8_t color;

    if (CFG_RAINBOW_BOMBCHU_TRAIL_INNER_ENABLED)
        color = get_rainbow_color(frames, BOMBCHU_CYCLE_FRAMES_INNER);
    else
        color = CFG_BOMBCHU_TRAIL_INNER_COLOR;

    if (color.r == 0xFA && color.g == 0x00 && color.b == 0x00)
    {
        color.r = 9.0f + brightness * 209.0f;
        color.g = 9.0f + brightness * 34.0f;
        color.b = 35.0f + brightness * -35.0f;
    }
    else
    {
        color.r *= brightness;
        color.g *= brightness;
        color.b *= brightness;
    }

    return (color.r << 24) | (color.g << 16) | (color.b << 8) | 0xFF;
}

typedef struct
{
    colorRGBA8_t inner;
    colorRGBA8_t outer;
} navi_color_t;

#define NAVI_CYCLE_FRAMES_OUTER 12
#define NAVI_CYCLE_FRAMES_INNER 14

extern uint8_t CFG_RAINBOW_NAVI_IDLE_INNER_ENABLED;
extern uint8_t CFG_RAINBOW_NAVI_IDLE_OUTER_ENABLED;
extern uint8_t CFG_RAINBOW_NAVI_ENEMY_INNER_ENABLED;
extern uint8_t CFG_RAINBOW_NAVI_ENEMY_OUTER_ENABLED;
extern uint8_t CFG_RAINBOW_NAVI_NPC_INNER_ENABLED;
extern uint8_t CFG_RAINBOW_NAVI_NPC_OUTER_ENABLED;
extern uint8_t CFG_RAINBOW_NAVI_PROP_INNER_ENABLED;
extern uint8_t CFG_RAINBOW_NAVI_PROP_OUTER_ENABLED;

void update_navi_colors()
{
    int rainbow_inner_enabled = 0;
    int rainbow_outer_enabled = 0;

    switch (z64_game.target_actor_type)
    {
        case ACTORTYPE_PLAYER:
            rainbow_inner_enabled = CFG_RAINBOW_NAVI_IDLE_INNER_ENABLED;
            rainbow_outer_enabled = CFG_RAINBOW_NAVI_IDLE_OUTER_ENABLED;
            break;
        case ACTORTYPE_ENEMY:
        case ACTORTYPE_BOSS:
            rainbow_inner_enabled = CFG_RAINBOW_NAVI_ENEMY_INNER_ENABLED;
            rainbow_outer_enabled = CFG_RAINBOW_NAVI_ENEMY_OUTER_ENABLED;
            break;
        case ACTORTYPE_NPC:
            rainbow_inner_enabled = CFG_RAINBOW_NAVI_NPC_INNER_ENABLED;
            rainbow_outer_enabled = CFG_RAINBOW_NAVI_NPC_OUTER_ENABLED;
            break;
        default:
            rainbow_inner_enabled = CFG_RAINBOW_NAVI_PROP_INNER_ENABLED;
            rainbow_outer_enabled = CFG_RAINBOW_NAVI_PROP_OUTER_ENABLED;
            break;
    }

    if (!rainbow_inner_enabled && !rainbow_outer_enabled)
        return;

    colorRGB8_t color_inner = get_rainbow_color(frames, NAVI_CYCLE_FRAMES_INNER);
    colorRGB8_t color_outer = get_rainbow_color(frames, NAVI_CYCLE_FRAMES_OUTER);

    navi_color_t* navi_ref_colors = (navi_color_t*)0x800E8214;
    if (rainbow_inner_enabled)
        navi_ref_colors[z64_game.target_actor_type].inner.color = color_inner;
    if (rainbow_outer_enabled)
        navi_ref_colors[z64_game.target_actor_type].outer.color = color_outer;

    for (int i = 0; i < 3; i++)
    {
        if (rainbow_inner_enabled)
            z64_game.target_arr[i].color = color_inner;
    }

    z64_actor_t* navi = z64_link.navi_actor;
    if (navi != NULL && navi->main_proc != NULL)
    {
        colorRGBAf_t* navi_colors = (colorRGBAf_t*)(((uint32_t)navi) + 0x234);
        if (rainbow_inner_enabled)
        {
            navi_colors[0].r = color_inner.r;
            navi_colors[0].g = color_inner.g;
            navi_colors[0].b = color_inner.b;
        }
        if (rainbow_outer_enabled)
        {
            navi_colors[1].r = color_outer.r;
            navi_colors[1].g = color_outer.g;
            navi_colors[1].b = color_outer.b;
        }
    }
}

#define TUNIC_CYCLE_FRAMES 20
extern uint8_t CFG_RAINBOW_TUNIC_ENABLED;

extern colorRGB8_t CFG_TUNIC_COLORS[3];

#define CFG_RAINBOW_TUNIC_KOKIRI    0b00000001
#define CFG_RAINBOW_TUNIC_GORON     0b00000010
#define CFG_RAINBOW_TUNIC_ZORA      0b00000100

void update_tunic_colors()
{
    //colorRGB8_t* ptr_tunic_colors = (colorRGB8_t*)(0x800F7AD8);
    colorRGB8_t tunic_color = get_rainbow_color(frames, TUNIC_CYCLE_FRAMES);
    if(CFG_RAINBOW_TUNIC_ENABLED & CFG_RAINBOW_TUNIC_KOKIRI)
        CFG_TUNIC_COLORS[0] = tunic_color; //Update kokiri tunic color
    if(CFG_RAINBOW_TUNIC_ENABLED & CFG_RAINBOW_TUNIC_GORON)
        CFG_TUNIC_COLORS[1] = tunic_color; //Update goron tunic color
    if(CFG_RAINBOW_TUNIC_ENABLED & CFG_RAINBOW_TUNIC_ZORA)
        CFG_TUNIC_COLORS[2] = tunic_color; //Update zora tunic color
}

void update_misc_colors()
{
    frames++;
    update_sword_trail_colors();
    update_boomerang_trail_colors();
    update_bombchu_trail_colors();
    update_navi_colors();
    update_tunic_colors();
}
