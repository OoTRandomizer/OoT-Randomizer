#pragma once

#include "z64.h"

typedef signed char s8;
typedef short s16;
typedef int s32;
typedef long long s64;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef float f32;
typedef double f64;

extern void Audio_PlaySfxGeneral(u16 sfxId, Vec3f* pos, u8 token, f32* freqScale, f32* vol, s8* reverbAdd);
extern void Sram_WriteSave_call(void* sramCtx);
extern void Play_SaveSceneFlags(z64_game_t* play);
extern void Interface_SetDoAction(z64_game_t* play, u16 action);
extern void Interface_ChangeHudVisibilityMode(u16 hudVisibilityMode);
extern void func_800F64E0(u8 arg0);

typedef enum DoAction {
    /* 0x00 */ DO_ACTION_ATTACK,
    /* 0x01 */ DO_ACTION_CHECK,
    /* 0x02 */ DO_ACTION_ENTER,
    /* 0x03 */ DO_ACTION_RETURN,
    /* 0x04 */ DO_ACTION_OPEN,
    /* 0x05 */ DO_ACTION_JUMP,
    /* 0x06 */ DO_ACTION_DECIDE,
    /* 0x07 */ DO_ACTION_DIVE,
    /* 0x08 */ DO_ACTION_FASTER,
    /* 0x09 */ DO_ACTION_THROW,
    /* 0x0A */ DO_ACTION_NONE, // in do_action_static, the texture at this position is NAVI, however this value is in practice the "No Action" value
    /* 0x0B */ DO_ACTION_CLIMB,
    /* 0x0C */ DO_ACTION_DROP,
    /* 0x0D */ DO_ACTION_DOWN,
    /* 0x0E */ DO_ACTION_SAVE,
    /* 0x0F */ DO_ACTION_SPEAK,
    /* 0x10 */ DO_ACTION_NEXT,
    /* 0x11 */ DO_ACTION_GRAB,
    /* 0x12 */ DO_ACTION_STOP,
    /* 0x13 */ DO_ACTION_PUTAWAY,
    /* 0x14 */ DO_ACTION_REEL,
    /* 0x15 */ DO_ACTION_1,
    /* 0x16 */ DO_ACTION_2,
    /* 0x17 */ DO_ACTION_3,
    /* 0x18 */ DO_ACTION_4,
    /* 0x19 */ DO_ACTION_5,
    /* 0x1A */ DO_ACTION_6,
    /* 0x1B */ DO_ACTION_7,
    /* 0x1C */ DO_ACTION_8,
    /* 0x1D */ DO_ACTION_MAX
} DoAction;

typedef enum HudVisibilityMode {
    /*  0 */ HUD_VISIBILITY_NO_CHANGE,
    /*  1 */ HUD_VISIBILITY_NOTHING,
    /*  2 */ HUD_VISIBILITY_NOTHING_ALT, // Identical to HUD_VISIBILITY_NOTHING
    /*  3 */ HUD_VISIBILITY_HEARTS_FORCE, // See above
    /*  4 */ HUD_VISIBILITY_A,
    /*  5 */ HUD_VISIBILITY_A_HEARTS_MAGIC_FORCE, // See above
    /*  6 */ HUD_VISIBILITY_A_HEARTS_MAGIC_MINIMAP_FORCE, // See above
    /*  7 */ HUD_VISIBILITY_ALL_NO_MINIMAP_BY_BTN_STATUS, // Only raises button alphas if not disabled
    /*  8 */ HUD_VISIBILITY_B,
    /*  9 */ HUD_VISIBILITY_HEARTS_MAGIC,
    /* 10 */ HUD_VISIBILITY_B_ALT, // Identical to HUD_VISIBILITY_B
    /* 11 */ HUD_VISIBILITY_HEARTS,
    /* 12 */ HUD_VISIBILITY_A_B_MINIMAP,
    /* 13 */ HUD_VISIBILITY_HEARTS_MAGIC_FORCE, // See above
    /* 50 */ HUD_VISIBILITY_ALL = 50, // Only raises button alphas if not disabled
    /* 52 */ HUD_VISIBILITY_NOTHING_INSTANT = 52
} HudVisibilityMode;
