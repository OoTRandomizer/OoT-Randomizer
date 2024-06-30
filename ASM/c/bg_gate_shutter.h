#include "z64.h"

typedef struct BgGateShutter {
    /* 0x0000 */ DynaPolyActor dyna;
    /* 0x0154 */ void* actionFunc;
    /* 0x0158 */ int16_t openingState; // 1 if gate is opening
    /* 0x015C */ z64_xyzf_t somePos;
    /* 0x0168 */ int16_t unk_168;
} BgGateShutter; // size = 0x016C
