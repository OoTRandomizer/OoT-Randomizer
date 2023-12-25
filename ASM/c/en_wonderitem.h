#ifndef Z_EN_WONDER_ITEM_H
#define Z_EN_WONDER_ITEM_H

#include <stdint.h>
#include "z64.h"

struct EnWonderItem;

typedef void (*EnWonderItemUpdateFunc)(struct EnWonderItem*, z64_game_t*);

void EnWonderitem_AfterInitHack(z64_actor_t* actor, z64_game_t* game);

typedef struct EnWonderItem {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x013C */ EnWonderItemUpdateFunc updateFunc;
    /* 0x0140 */ float unkHeight; // sets height of dummied out mode 4
    /* 0x0144 */ int16_t wonderMode;
    /* 0x0146 */ int16_t itemDrop;
    /* 0x0148 */ int16_t numTagPoints;
    /* 0x014A */ int16_t dropCount;
    /* 0x014C */ int16_t timer;
    /* 0x014E */ int16_t tagFlags;
    /* 0x014A */ int16_t tagCount;
    /* 0x0152 */ int16_t switchFlag;
    /* 0x0154 */ char unk_164[4];
    /* 0x0158 */ int16_t nextTag;
    /* 0x015A */ int16_t timerMod;
    /* 0x015C */ z64_xyzf_t unkPos; // set to initial position by mode bomb soldier, then never used.
    /* 0x0168 */ char unk_178[8];
    /* 0x0170 */ char collider[0x4C];
    /* 0x01BC */ char unk_1CC[4];
    /* 0x01C0 */ uint8_t overridden;
    /* 0x01C1 */ uint8_t spare[15];
} EnWonderItem; // size = 0x01D0

typedef enum {
    /* 0 */ WONDERITEM_MULTITAG_FREE,
    /* 1 */ WONDERITEM_TAG_POINT_FREE,
    /* 2 */ WONDERITEM_PROXIMITY_DROP,
    /* 3 */ WONDERITEM_INTERACT_SWITCH,
    /* 4 */ WONDERITEM_UNUSED,
    /* 5 */ WONDERITEM_MULTITAG_ORDERED,
    /* 6 */ WONDERITEM_TAG_POINT_ORDERED,
    /* 7 */ WONDERITEM_PROXIMITY_SWITCH,
    /* 8 */ WONDERITEM_BOMB_SOLDIER,
    /* 9 */ WONDERITEM_ROLL_DROP
} EnWonderItemMode;

typedef enum {
    /* 0 */ WONDERITEM_DROP_NUTS,
    /* 1 */ WONDERITEM_DROP_HEART_PIECE,
    /* 2 */ WONDERITEM_DROP_MAGIC_LARGE,
    /* 3 */ WONDERITEM_DROP_MAGIC_SMALL,
    /* 4 */ WONDERITEM_DROP_HEART,
    /* 5 */ WONDERITEM_DROP_ARROWS_SMALL,
    /* 6 */ WONDERITEM_DROP_ARROWS_MEDIUM,
    /* 7 */ WONDERITEM_DROP_ARROWS_LARGE,
    /* 8 */ WONDERITEM_DROP_GREEN_RUPEE,
    /* 9 */ WONDERITEM_DROP_BLUE_RUPEE,
    /* A */ WONDERITEM_DROP_RED_RUPEE,
    /* B */ WONDERITEM_DROP_FLEXIBLE,
    /* C */ WONDERITEM_DROP_RANDOM
} EnWonderItemDrop;

#endif
