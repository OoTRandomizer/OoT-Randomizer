#ifndef BGTREEMOUTH_H
#define BGTREEMOUTH_H

#include "z64.h"

struct BgTreemouth;

typedef void (*BgTreemouthActionFunc)(struct BgTreemouth*, z64_game_t*);

typedef struct BgTreemouth {
    /* 0x0000 */ DynaPolyActor dyna;
    /* 0x0154 */ char unk_164[0x4];
    /* 0x0158 */ float unk_168;
    /* 0x015C */ BgTreemouthActionFunc actionFunc;
} BgTreemouth; // size = 0x0160

#endif
