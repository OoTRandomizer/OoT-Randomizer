#ifndef GROTTO_H
#define GROTTO_H

#include "z64.h"

typedef struct GrottoTableEntry {
    /* 0x00 */ uint16_t entranceIndex;
    /* 0x02 */ uint8_t sceneLayer;
    /* 0x03 */ uint8_t content_id;
} GrottoTableEntry; // size = 0x4

#define GROTTO_TABLE_SIZE 33

extern GrottoTableEntry gGrottoTable[];
extern uint8_t CURRENT_GROTTO_ID;

struct DoorAna;

typedef void (*DoorAnaActionFunc)(struct DoorAna*, z64_game_t*);

typedef struct DoorAna {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x014C */ ColliderCylinder collider;
    /* 0x0198 */ DoorAnaActionFunc actionFunc;
} DoorAna; // size = 0x019C

// Moves the value `p` to bit position `s` for building actor parameters by OR-ing these together.
#define PARAMS_PACK_NOMASK(p, s) \
    ((p) << (s))

// Converts a number of bits to a bitmask, helper for params macros
// e.g. 3 becomes 0b111 (7)
#define NBITS_TO_MASK(n) \
    ((1 << (n)) - 1)

// Extracts the `n`-bit value at position `s` in `p`, masks then shifts
// Signed variant, possibility of sign extension
#define PARAMS_GET_S(p, s, n) \
    (((p) & (NBITS_TO_MASK(n) << (s))) >> (s))

#define PLAYER_PARAMS(startMode, startBgCamIndex) (PARAMS_PACK_NOMASK(startMode, 8) | PARAMS_PACK_NOMASK(startBgCamIndex, 0))

// Determines behavior when spawning. See `PlayerStartMode`.
#define PLAYER_GET_START_MODE(thisx) PARAMS_GET_S((thisx)->common.variable, 8, 4)

// Sets initial `bgCamIndex`, which determines camera behavior.
// The value is used to index a list of `BgCamInfo` contained within the scene's collision data.
// See `PLAYER_START_BG_CAM_DEFAULT` for what a value of -1 does.
#define PLAYER_GET_START_BG_CAM_INDEX(thisx) PARAMS_GET_S((thisx)->common.variable, 0, 8)

// A value of -1 for `startBgCamIndex` indicates that default behavior should be used.
// This means the `bgCamIndex` will be read from the current floor polygon.
#define PLAYER_START_BG_CAM_DEFAULT ((uint8_t)-1)

#define GET_PLAYER(play) ((z64_link_t*)(play)->actor_list[ACTORCAT_PLAYER].first)

typedef enum PlayerStartMode {
    /*  0 */ PLAYER_START_MODE_NOTHING, // Update is empty and draw function is NULL, nothing occurs. Useful in cutscenes, for example.
    /*  1 */ PLAYER_START_MODE_TIME_TRAVEL, // Arriving from time travel. Automatically adjusts by age.
    /*  2 */ PLAYER_START_MODE_BLUE_WARP, // Arriving from a blue warp.
    /*  3 */ PLAYER_START_MODE_DOOR, // Unused. Use a door immediately if one is nearby. If no door is in usable range, a softlock occurs.
    /*  4 */ PLAYER_START_MODE_GROTTO, // Arriving from a grotto, launched upward from the ground.
    /*  5 */ PLAYER_START_MODE_WARP_SONG, // Arriving from a warp song.
    /*  6 */ PLAYER_START_MODE_FARORES_WIND, // Arriving from a Farores Wind warp.
    /*  7 */ PLAYER_START_MODE_KNOCKED_OVER, // Knocked over on the ground and flashing red.
    /*  8 */ PLAYER_START_MODE_UNUSED_8,  // Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.
    /*  9 */ PLAYER_START_MODE_UNUSED_9,  // Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.
    /* 10 */ PLAYER_START_MODE_UNUSED_10, // Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.
    /* 11 */ PLAYER_START_MODE_UNUSED_11, // Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.
    /* 12 */ PLAYER_START_MODE_UNUSED_12, // Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.
    /* 13 */ PLAYER_START_MODE_IDLE, // Idle standing still, or swim if in water.
    /* 14 */ PLAYER_START_MODE_MOVE_FORWARD_SLOW, // Take a few steps forward at a slow speed (2.0f), or swim if in water.
    /* 15 */ PLAYER_START_MODE_MOVE_FORWARD, // Take a few steps forward, using the speed from the last exit (gSaveContext.entranceSpeed), or swim if in water.
    /* 16 */ PLAYER_START_MODE_MAX // Note: By default, this param has 4 bits allocated. The max value is 16.
} PlayerStartMode;

#endif
