#include "gfx.h"
#include "util.h"
#include "z64.h"
#include "rainbow_sword.h"

// Massive thanks to Krimtonz for the coding help, and MZX for the tweening function!~

uint32_t frames = 0;

const uint32_t CYCLE_FRAMES = 0x30;

extern uint8_t RAINBOW_SWORD_ENABLED;

typedef struct
{
    uint8_t r;
    uint8_t g;
    uint8_t b;
} colorRGB_t;


colorRGB_t colors[] =
{
    { 0xE0, 0x10, 0x10 }, //red
    { 0xE0, 0xE0, 0x10 }, //yellow
    { 0x10, 0xE0, 0x10 }, //green
    { 0x10, 0xE0, 0xE0 }, //cyan
    { 0x10, 0x10, 0xE0 }, //blue
    { 0xE0, 0x10, 0xE0 }, //purple
    { 0xE0, 0x10, 0x10 }, //red
};

colorRGB_t set_sword_trail_color(int index, int f)
{
    float tweenA, tweenB;

    tweenB = ((float)f / CYCLE_FRAMES);
    tweenA = 1 - tweenB;

    uint8_t r, g, b;

    colorRGB_t cA = colors[index];
    colorRGB_t cB = colors[index + 1];

    r = (uint8_t)((cA.r * tweenA) + (cB.r * tweenB));
    g = (uint8_t)((cA.g * tweenA) + (cB.g * tweenB));
    b = (uint8_t)((cA.b * tweenA) + (cB.b * tweenB));
    colorRGB_t ret;
    ret.r = r;
    ret.g = g;
    ret.b = b;
    return ret;
}

void update_color()
{
    if(RAINBOW_SWORD_ENABLED) {
        frames+=5;
        if (frames >= CYCLE_FRAMES * 6)
            frames = 0;
            
        int index = frames / CYCLE_FRAMES;
        int f = frames % CYCLE_FRAMES;
    
        colorRGB_t color = set_sword_trail_color(index, f);
        uint8_t *sword_trail = (uint8_t*)0x80115DCE;
        for (int i = 0; i < 16 ; i+=4) {
            sword_trail[i] = color.r;
            sword_trail[i + 1] = color.g;
            sword_trail[i + 2] = color.b;
        }
    }
}