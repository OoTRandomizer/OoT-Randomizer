#include <stdint.h>
#include "rainbow_sword.h"

// Massive thanks to Krimtonz for the coding help, and MZX for the tweening function!~

static uint32_t frames = 0;

#define CYCLE_FRAMES_OUTER 10
#define CYCLE_FRAMES_INNER 12

uint8_t cfg_rainbow_sword_inner_enabled = 0;
uint8_t cfg_rainbow_sword_outer_enabled = 0;

typedef struct
{
    uint8_t r;
    uint8_t g;
    uint8_t b;
} colorRGB_t;

typedef struct
{
    union
    {
        struct
        {
            uint8_t r;
            uint8_t g;
            uint8_t b;
        };
        colorRGB_t color;
    };
    uint8_t a;
} colorRGBA_t;


static colorRGB_t colors[] =
{
    { 0xE0, 0x10, 0x10 }, //red
    { 0xE0, 0xE0, 0x10 }, //yellow
    { 0x10, 0xE0, 0x10 }, //green
    { 0x10, 0xE0, 0xE0 }, //cyan
    { 0x10, 0x10, 0xE0 }, //blue
    { 0xE0, 0x10, 0xE0 }, //purple
    { 0xE0, 0x10, 0x10 }, //red
};

static colorRGB_t get_color(uint32_t f, uint32_t step_frames)
{
    int index;
    float tweenA, tweenB;

    index = (f / step_frames) % 6;

    tweenB = ((float)(f % step_frames) / step_frames);
    tweenA = 1 - tweenB;

    colorRGB_t cA = colors[index];
    colorRGB_t cB = colors[index + 1];

    colorRGB_t ret;
    ret.r = (uint8_t)((cA.r * tweenA) + (cB.r * tweenB));
    ret.g = (uint8_t)((cA.g * tweenA) + (cB.g * tweenB));
    ret.b = (uint8_t)((cA.b * tweenA) + (cB.b * tweenB));
    return ret;
}

void update_color()
{
    frames++;
    colorRGBA_t *sword_trail = (colorRGBA_t*)0x80115DCE;

    if (cfg_rainbow_sword_inner_enabled)
    {
        colorRGB_t colorInner = get_color(frames, CYCLE_FRAMES_INNER);
        sword_trail[1].color = colorInner;
        sword_trail[3].color = colorInner;
    }

    if (cfg_rainbow_sword_outer_enabled)
    {
        colorRGB_t colorOuter = get_color(frames, CYCLE_FRAMES_OUTER);
        sword_trail[0].color = colorOuter;
        sword_trail[2].color = colorOuter;
    }
}