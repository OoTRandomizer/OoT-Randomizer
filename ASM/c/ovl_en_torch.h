#ifndef Z_EN_TORCH_H
#define Z_EN_TORCH_H

#include "z64.h"

struct EnTorch;

typedef struct EnTorch {
    /* 0x0000 */ z64_actor_t actor;
} EnTorch; // size = 0x014C

#define ACTOR_EN_BOX 0x000A

#endif
