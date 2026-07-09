#ifndef Z_EN_COW_H
#define Z_EN_COW_H

#include "z64.h"
#include "actor.h"
#include "z64collision_check.h"
#include "stdint.h"

typedef enum CowCollider {
    /*  0 */ COW_COLLIDER_FRONT,
    /*  1 */ COW_COLLIDER_REAR,
    /*  2 */ COW_COLLIDER_MAX
} CowCollider;
struct EnCow;

typedef void (*EnCowActionFunc)(struct EnCow*, struct z64_game_t*);

typedef enum CowLimb {
    /*  0 */ COW_LIMB_NONE,
    /*  1 */ COW_LIMB_ROOT,
    /*  2 */ COW_LIMB_HEAD,
    /*  3 */ COW_LIMB_JAW,
    /*  4 */ COW_LIMB_NOSE,
    /*  5 */ COW_LIMB_NOSE_RING,
    /*  6 */ COW_LIMB_MAX
} CowLimb;

typedef struct EnCow {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x014C */ ColliderCylinder colliders[COW_COLLIDER_MAX];
    /* 0x01E4 */ SkelAnime skelAnime;
    /* 0x0228 */ z64_xyz_t jointTable[COW_LIMB_MAX];
    /* 0x024C */ z64_xyz_t morphTable[COW_LIMB_MAX];
    /* 0x0270 */ z64_xyz_t headRot;
    /* 0x0276 */ uint16_t cowFlags;
    /* 0x0278 */ uint16_t animationTimer;
    /* 0x027A */ uint16_t breathTimer;
    /* 0x027C */ EnCowActionFunc actionFunc;
} EnCow; // size = 0x0280

#endif