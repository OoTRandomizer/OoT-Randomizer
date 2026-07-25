#ifndef ACTOR_H
#define ACTOR_H

#include "z64.h"
#include "get_items.h"
#include <stdbool.h>
#include <stdint.h>

// New data added to the end of every actor.
// Make sure the size of this struct is equal to the amount of space added added in Actor_Spawn_Malloc_Hack from actor.asm
typedef struct {
    /* 0x00 */ uint16_t actor_id;
    /* 0x02 */ xflag_t flag;
    /* 0x04 */ uint8_t minimap_draw_flags;
} ActorAdditionalData;


// Converts a number of bits to a bitmask, helper for params macros
// e.g. 3 becomes 0b111 (7)
#define NBITS_TO_MASK(n) \
    ((1 << (n)) - 1)

// Extracts the `n`-bit value at position `s` in `p`, shifts then masks
// Unsigned variant, no possibility of sign extension
#define PARAMS_GET_U(p, s, n) \
    (((p) >> (s)) & NBITS_TO_MASK(n))

// Extracts the `n`-bit value at position `s` in `p`, masks then shifts
// Signed variant, possibility of sign extension
#define PARAMS_GET_S(p, s, n) \
    (((p) & (NBITS_TO_MASK(n) << (s))) >> (s))

// Extracts all bits past position `s` in `p`
#define PARAMS_GET_NOMASK(p, s) \
    ((p) >> (s))

// Extracts the `n`-bit value at position `s` in `p` without shifting it from its current position
#define PARAMS_GET_NOSHIFT(p, s, n) \
    ((p) & (NBITS_TO_MASK(n) << (s)))

// Moves the `n`-bit value `p` to bit position `s` for building actor parameters by OR-ing these together
#define PARAMS_PACK(p, s, n) \
    (((p) & NBITS_TO_MASK(n)) << (s))

// Moves the value `p` to bit position `s` for building actor parameters by OR-ing these together.
#define PARAMS_PACK_NOMASK(p, s) \
    ((p) << (s))

// Generates a bitmask for bit position `s` of length `n`
#define PARAMS_MAKE_MASK(s, n) PARAMS_GET_NOSHIFT(~0, s, n)

#define TRANSITION_ACTOR_PARAMS_INDEX_SHIFT 10
#define GET_TRANSITION_ACTOR_INDEX(actor) PARAMS_GET_NOMASK((u16)(actor)->params, 10)

void Actor_After_UpdateAll_Hack(z64_actor_t* actor, z64_game_t* game);
void Actor_StoreFlagByIndex(z64_actor_t* actor, z64_game_t* game, uint16_t actor_index);
void Actor_StoreFlag(z64_actor_t* actor, z64_game_t* game, xflag_t flag);
void Actor_StoreChestType(z64_actor_t* actor, z64_game_t *game);
z64_actor_t *Actor_SpawnEntry_Hack(void* actorCtx, ActorEntry* actorEntry, z64_game_t* globalCtx);
bool spawn_override_silver_rupee(ActorEntry* actorEntry, z64_game_t* globalCtx, bool* overridden);
void after_spawn_override_silver_rupee(z64_actor_t* actor, bool overridden);
void Actor_BuildFlag(z64_actor_t* actor, xflag_t* flag, uint16_t actor_index, uint8_t subflag);
z64_actor_t * Actor_SpawnAsChild_Hook(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params);
ActorAdditionalData* Actor_GetAdditionalData(z64_actor_t* actor);
override_t get_newflag_override(xflag_t* flag);
extern ActorOverlay gActorOverlayTable[];
extern z64_actor_t * Actor_SpawnAsChild(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params);
z64_actor_t * Actor_SpawnAsChildWithSubflag(void* actorCtx, z64_actor_t* parent, z64_game_t* globalCtx, int16_t actorId, float posX, float posY, float posZ, int16_t rotX, int16_t rotY, int16_t rotZ, int16_t params, uint8_t subflag);

#endif
