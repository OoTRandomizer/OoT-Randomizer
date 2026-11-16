#ifndef Z_EN_OKARINA_TAG_H
#define Z_EN_OKARINA_TAG_H

#include "z64.h"

struct EnOkarinaTag;

typedef void (*EnOkarinaTagActionFunc)(struct EnOkarinaTag*, z64_game_t*);

typedef struct EnOkarinaTag {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x014C */ EnOkarinaTagActionFunc actionFunc;
    /* 0x0150 */ int16_t type;
    /* 0x0152 */ int16_t ocarinaSong;
    /* 0x0154 */ int16_t switchFlag;
    /* 0x0156 */ char unk_156[0x2];
    /* 0x0158 */ int16_t unk_158;
    /* 0x015A */ int16_t unk_15A;
    /* 0x015C */ float interactRange;
} EnOkarinaTag; // size = 0x0160

#endif
