#ifndef GET_ITEMS_H
#define GET_ITEMS_H

#include <stdbool.h>
#include "z64.h"

extern uint16_t CFG_ADULT_TRADE_SHUFFLE;
extern uint16_t CFG_CHILD_TRADE_SHUFFLE;

void item_overrides_init();
void handle_pending_items();
void push_delayed_item(uint8_t flag);
void pop_pending_item();
enum override_type {
    OVR_BASE_ITEM = 0,
    OVR_CHEST = 1,
    OVR_COLLECTABLE = 2,
    OVR_SKULL = 3,
    OVR_GROTTO_SCRUB = 4,
    OVR_DELAYED = 5,
    OVR_NEWFLAGCOLLECTIBLE = 6,
};


typedef union override_key_t {
    uint32_t all;
    struct {
        uint8_t scene;
        uint8_t type;
        uint16_t flag;
    };
} override_key_t;

// a type used when the cloak of an ice trap is irrelevant
typedef union override_value_base_t {
    uint32_t all;
    struct {
        uint16_t item_id;
        uint8_t player;
        uint8_t _pad;
    };
} override_value_base_t;

typedef struct {
    override_value_base_t base;
    uint16_t looks_like_item_id;
    uint16_t _pad;
} override_value_t;

typedef struct {
    override_key_t key;
    uint32_t _pad;
    override_value_t value;
} override_t;

typedef struct {
    override_key_t  alt;
    override_key_t  primary;
} alt_override_t;

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
} EnItem00;


typedef void (*z64_EnItem00ActionFunc)(struct EnItem00*, z64_game_t*);
typedef EnItem00* (*z64_Item_DropCollectible_proc)(z64_game_t* globalCtx, z64_xyzf_t* spawnPos, int16_t params);
typedef EnItem00* (*z64_Item_DropCollectibleRandom_proc)(z64_game_t *globalCtx, z64_actor_t *fromActor, z64_xyzf_t *spawnPos, int16_t params);

override_t lookup_override_by_key(override_key_t key);
override_t lookup_override(z64_actor_t* actor, uint8_t scene, uint8_t item_id);
override_key_t resolve_alternative_override(override_key_t override_key);
override_key_t get_override_search_key(z64_actor_t* actor, uint8_t scene, uint8_t item_id);
override_t get_override_if_collectible_flag_not_set(EnItem00* item00);
void Collectible_WaitForMessageBox(EnItem00* this, z64_game_t* game);
void reset_collectible_mutex();
void override_flags_init();
bool Get_CollectibleOverrideFlag(EnItem00* item00);

#endif
