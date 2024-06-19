#ifndef GET_ITEMS_H
#define GET_ITEMS_H

#include <stdbool.h>
#include "z64.h"
#include "en_item00.h"
#include "override.h"

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

typedef struct xflag_t {
    uint8_t set : 1;
    uint8_t scene : 7;
    union {
        uint32_t all;
        struct {
            uint8_t pad;
            uint8_t setup : 2;
            uint8_t room : 6;
            uint8_t flag;
            uint8_t subflag;
        };
        struct {
            uint32_t pad: 8;
            uint32_t grotto_id: 5;
            uint32_t room: 4;
            uint32_t flag: 7;
            uint32_t subflag: 8;
        } grotto;
    };

} xflag_t;

override_t lookup_override_by_key(override_key_t key);
override_t lookup_override_by_newflag(xflag_t* flag);
override_t lookup_override(z64_actor_t *actor, uint8_t scene, uint8_t item_id);
override_key_t resolve_alternative_override(override_key_t override_key);
xflag_t resolve_alternative_flag(xflag_t* flag);
override_key_t get_override_search_key(z64_actor_t *actor, uint8_t scene, uint8_t item_id);
void Collectible_WaitForMessageBox(EnItem00* this, z64_game_t* game);
void reset_collectible_mutex();
void override_flags_init();
bool Get_NewFlag(xflag_t* flag);

extern xflag_t drop_collectible_override_flag;
extern EnItem00* collectible_mutex;

#endif
