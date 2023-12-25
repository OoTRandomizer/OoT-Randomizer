#ifndef CHESTS_H
#define CHESTS_H

#include "item_table.h"
#include "get_items.h"
#include "z64.h"

extern uint32_t CHEST_SIZE_MATCH_CONTENTS;
extern uint32_t CHEST_TEXTURE_MATCH_CONTENTS;
extern uint32_t CHEST_SIZE_TEXTURE;
extern uint32_t CHEST_LENS_ONLY;

struct EnBox;

typedef void (*EnBoxActionFunc)(struct EnBox*, z64_game_t*);

typedef struct EnBox
{
    /* 0x0000 */ DynaPolyActor dyna;
    /* 0x0154 */ uint8_t skelanime[0x44];
    /* 0x0198 */ int32_t unk_198; // related to animation delays for types 3 and 8
    /* 0x019C */ int32_t sub_cam_id;
    /* 0x01A0 */ float unk_1A0; // 0-1, rotation-related, apparently unused (in z_en_box.c at least)
    /* 0x01A4 */ EnBoxActionFunc action_func;
    /* 0x01A8 */ z64_xyz_t joint_table[5];
    /* 0x01C6 */ z64_xyz_t morph_table[5];
    /* 0x01E4 */ int16_t unk_1E4; // probably a frame count? set by player code
    /* 0x01E6 */ uint8_t movement_flags;
    /* 0x01E7 */ uint8_t alpha;
    /* 0x01E8 */ uint8_t switch_flag;
    /* 0x01E9 */ uint8_t type;
    /* 0x01EA */ uint8_t ice_smoke_timer;
    /* 0x01EB */ uint8_t unk_1EB;
} EnBox; // size = 0x01EC

// Chest structure encapsulating EnBox with added randomizer fields
typedef struct Chest
{
    /* 0x0000 */ EnBox en_box;
    /* 0x01EC */ uint8_t size;  // added for rando
    /* 0x01ED */ uint8_t color; // added for rando
} Chest;                        // size = 0x01EE

void get_chest_override(z64_actor_t* actor);
void draw_chest(z64_game_t* game, int32_t part, void* unk, void* unk2, z64_actor_t* actor, Gfx** opa_ptr);
_Bool should_draw_forest_hallway_chest(z64_actor_t* actor, z64_game_t* game);
void draw_forest_hallway_chest_base();
void draw_forest_hallway_chest_lid();

#endif
