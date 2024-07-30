#ifndef EN_ITEM00_H
#define EN_ITEM00_H

#include "models.h"
#include "override.h"
#include <stdbool.h>

struct EnItem00;

typedef void (*EnItem00ActionFunc)(struct EnItem00*, z64_game_t*);
typedef struct EnItem00 {
    z64_actor_t actor;              // 0x0000
    EnItem00ActionFunc actionFunc;  // 0x013C
    uint16_t collectibleFlag;       // 0x0140
    uint16_t getItemId;             // 0x0142
    uint16_t unk_154;               // 0x0144
    uint16_t unk_156;               // 0x0146
    uint16_t unk_158;               // 0x0148
    int16_t timeToLive;             // 0x014A
    float scale;                    // 0x014C
    ColliderCylinder collider;      // 0x0150 size = 4C
    override_t override;            // 0x019C
    bool is_silver_rupee;           // 0x????
    bool dropped;
    model_t model;
} EnItem00;

void EnItem00_OutgoingAction(EnItem00* this, z64_game_t* globalCtx);

typedef void (*z64_EnItem00ActionFunc)(struct EnItem00*, z64_game_t*);
typedef EnItem00*(*z64_Item_DropCollectible_proc)(z64_game_t* globalCtx, z64_xyzf_t* spawnPos, int16_t params);
typedef EnItem00*(*z64_Item_DropCollectibleRandom_proc)(z64_game_t* globalCtx, z64_actor_t* fromActor, z64_xyzf_t* spawnPos, int16_t params);

#endif
