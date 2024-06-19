#ifndef _DEMO_EFFECT_H_
#define _DEMO_EFFECT_H_
#include "z64.h"
#include "get_items.h"

typedef struct {
    /* 0x00 */ uint8_t timer;
} DemoEffectFireBall;

typedef struct {
    /* 0x00 */ uint8_t alpha;
    /* 0x01 */ uint8_t scale;
    /* 0x02 */ uint8_t pad;
    /* 0x04 */ int16_t rotation;
} DemoEffectBlueOrb;

typedef struct {
    /* 0x00 */ uint8_t alpha;
    /* 0x01 */ uint8_t scaleFlag;
    /* 0x02 */ uint8_t flicker;
    /* 0x04 */ int16_t rotation;
} DemoEffectLight;

typedef struct {
    /* 0x00 */ uint8_t alpha;
} DemoEffectLgtShower;

typedef struct {
    /* 0x00 */ uint8_t type;
    /* 0x01 */ uint8_t lightRingSpawnDelay;
    /* 0x02 */ uint8_t rotation;
    /* 0x04 */ int16_t lightRingSpawnTimer;
} DemoEffectGodLgt;

typedef struct {
    /* 0x00 */ uint8_t timerIncrement;
    /* 0x01 */ uint8_t alpha;
    /* 0x02 */ uint8_t pad;
    /* 0x04 */ int16_t timer;
} DemoEffectLightRing;

typedef struct {
    /* 0x00 */ uint8_t triforceSpotOpacity;
    /* 0x01 */ uint8_t lightColumnOpacity;
    /* 0x02 */ uint8_t crystalLightOpacity;
    /* 0x04 */ int16_t rotation;
} DemoEffectTriforceSpot;

typedef struct {
    /* 0x00 */ uint8_t isPositionInit;
    /* 0x01 */ uint8_t isLoaded;
    /* 0x02 */ uint8_t drawId;
    /* 0x04 */ int16_t rotation;
} DemoEffectGetItem;

typedef struct {
    /* 0x00 */ uint8_t pad;
    /* 0x01 */ uint8_t pad2;
    /* 0x02 */ uint8_t pad3;
    /* 0x04 */ int16_t shrinkTimer;
} DemoEffectTimeWarp;

typedef struct {
    /* 0x00 */ uint8_t type;
    /* 0x01 */ uint8_t isPositionInit;
    /* 0x02 */ uint8_t alpha;
    /* 0x04 */ int16_t timer;
} DemoEffectJewel;

typedef struct {
    /* 0x00 */ uint8_t timer;
} DemoEffectDust;

struct DemoEffect;

typedef void (*DemoEffectFunc)(struct DemoEffect*, z64_game_t*);

typedef struct DemoEffect {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x013C */ uint8_t skelCurve[0x20]; // size = 0x20
    /* 0x015C */ uint8_t requiredObjectSlot;
    /* 0x0160 */ Gfx* jewelDisplayList;
    /* 0x0164 */ Gfx* jewelHolderDisplayList;
    /* 0x0168 */ uint8_t primXluColor[3];
    /* 0x016B */ uint8_t envXluColor[3];
    /* 0x016E */ uint8_t primOpaColor[3];
    /* 0x0171 */ uint8_t envOpaColor[3];
    /* 0x0174 */ union {
        DemoEffectFireBall fireBall;
        DemoEffectBlueOrb blueOrb;
        DemoEffectLight light;
        DemoEffectLgtShower lgtShower;
        DemoEffectGodLgt godLgt;
        DemoEffectLightRing lightRing;
        DemoEffectTriforceSpot triforceSpot;
        DemoEffectGetItem getItem;
        DemoEffectTimeWarp timeWarp;
        DemoEffectJewel jewel;
        DemoEffectDust dust;
    };
    /* 0x017A */ int16_t effectFlags;
    /* 0x017C */ int16_t cueChannel;
    /* 0x017E */ z64_xyz_t jewelCsRotation;
    /* 0x0184 */ DemoEffectFunc initUpdateFunc;
    /* 0x0188 */ ActorFunc initDrawFunc;
    /* 0x018C */ DemoEffectFunc updateFunc;
    // original size = 0x0190
    /* 0x0190 */ override_t override;
    /* 0x0xxx*/ bool override_initialized;
} DemoEffect;

#endif
