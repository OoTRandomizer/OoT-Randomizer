#include "extern_ctxt.h"

typedef z64_actor_t* (*spawn_actor_fn)(void* actor_ctxt, void* actor_data, z64_game_t* game_ctxt);
#define spawn_actor ((spawn_actor_fn)0x800255C4)
typedef int (*get_object_index_fn)(z64_obj_ctxt_t* obj_ctxt, uint16_t object_id);
#define get_object_index ((get_object_index_fn)0x80081628)
typedef void (*spawn_object_fn)(z64_obj_ctxt_t* obj_ctxt, uint16_t object_id);
#define spawn_object ((spawn_object_fn)0x800812F0)

float scene_fog_distance = 10.0;
float last_fog_distance = 10.0;
extern float SPEED_MULTIPLIER;
extern int8_t EXTERN_DAMAGE_MULTIPLYER;

const uint8_t freecam_modes[0x42] = {
    0x01, // 00 NONE
    0x01, // 01 NORMAL0
    0x01, // 02 NORMAL1
    0x01, // 03 DUNGEON0
    0x01, // 04 DUNGEON1
    0x01, // 05 NORMAL3
    0x01, // 06 HORSE0
    0x01, // 07 BOSS_GOMA
    0x01, // 08 BOSS_DODO
    0x01, // 09 BOSS_BARI
    0x01, // 0A BOSS_FGANON
    0x01, // 0B BOSS_BAL
    0x01, // 0C BOSS_SHADES
    0x01, // 0D BOSS_MOFA
    0x01, // 0E BOSS_TWIN0
    0x01, // 0F BOSS_TWIN1
    0x01, // 10 BOSS_GANON1
    0x01, // 11 BOSS_GANON2
    0x01, // 12 TOWER0
    0x01, // 13 TOWER1
    0x00, // 14 FIXED0
    0x00, // 15 FIXED1
    0x00, // 16 CIRCLE0
    0x00, // 17 CIRCLE2
    0x00, // 18 CIRCLE3
    0x00, // 19 PREREND0
    0x00, // 1A PREREND1
    0x00, // 1B PREREND3
    0x00, // 1C DOOR0
    0x00, // 1D DOORC
    0x00, // 1E RAIL3
    0x00, // 1F START0
    0x00, // 20 START1
    0x00, // 21 FREE0
    0x00, // 22 FREE2
    0x00, // 23 CIRCLE4
    0x00, // 24 CIRCLE5
    0x00, // 25 DEMO0
    0x00, // 26 DEMO1
    0x00, // 27 MORI1
    0x00, // 28 ITEM0
    0x00, // 29 ITEM1
    0x00, // 2A DEMO3
    0x00, // 2B DEMO4
    0x01, // 2C UFOBEAN
    0x01, // 2D LIFTBEAN
    0x00, // 2E SCENE0
    0x00, // 2F SCENE1
    0x00, // 30 HIDAN1
    0x00, // 31 HIDAN2
    0x00, // 32 MORI2
    0x00, // 33 MORI3
    0x01, // 34 TAKO
    0x01, // 35 SPOT05A
    0x01, // 36 SPOT05B
    0x01, // 37 HIDAN3
    0x01, // 38 ITEM2
    0x00, // 39 CIRCLE6
    0x01, // 3A NORMAL2
    0x01, // 3B FISHING
    0x00, // 3C DEMOC
    0x01, // 3D UO_FIBER
    0x01, // 3E DUNGEON2
    0x01, // 3F TEPPEN
    0x00, // 40 CIRCLE7
    0x01, // 41 NORMAL4
};


struct extern_ctxt_t {
    uint32_t          version;         /* 0x0000 */
    float             fog_distance;    /* 0x0004 */
    float             speed_multiplier;/* 0x0008 */
    uint8_t           equip_boots;     /* 0x000C */
    uint8_t           topdown_cam;     /* 0x000D */
    int8_t            damage;          /* 0x000E */
    uint8_t           freeze;          /* 0x000F */
    uint8_t           no_z;            /* 0x0010 */
    uint8_t           reverse_controls;/* 0x0010 */
} extern_ctxt = {
    .version = 2,
    .speed_multiplier = 1.0
};


float interpolate(float value, float target, float speed) {
    float newValue;

    if (speed == 0) {
        return target;
    }

    newValue = value + speed;
    if (value < target) {
        if (newValue > target) {
            return target;
        }
    }
    else if (newValue < target) {
        return target;
    }

    return newValue;
}

void extern_scene_init() {
    scene_fog_distance = z64_game.fog_distance;
}

void process_extern_ctxt() {
    /* Equipment Boots */
    if (extern_ctxt.equip_boots != 0) {
        if (z64_file.equip_boots != extern_ctxt.equip_boots) {
            z64_file.equip_boots = extern_ctxt.equip_boots;
            z64_UpdateEquipment(&z64_game, &z64_link);
        }

        if (extern_ctxt.equip_boots == 1)
            extern_ctxt.equip_boots = 0;
    }

    /* Fog Distance */
    if (extern_ctxt.fog_distance != 0.0) {
        if (z64_game.fog_distance != extern_ctxt.fog_distance) {
            z64_game.fog_distance = interpolate(last_fog_distance, extern_ctxt.fog_distance, -0.1);
        }
    }
    else {
        if (z64_game.fog_distance != scene_fog_distance) {
            z64_game.fog_distance = interpolate(z64_game.fog_distance, scene_fog_distance, 0.1);
        }
    }
    last_fog_distance = z64_game.fog_distance;

    /* Top-Down Camera */
    if (extern_ctxt.topdown_cam == 1) {
        if (freecam_modes[z64_game.camera_setting]) {
            z64_game.camera_setting = 0x35;
        }
    }
    else if (extern_ctxt.topdown_cam == 2) {
        if (freecam_modes[z64_game.camera_setting]) {
            z64_game.camera_setting = 0x1F;
        }
        extern_ctxt.topdown_cam = 0;
    }

    /* Speed Multiplier */
    SPEED_MULTIPLIER = extern_ctxt.speed_multiplier;

    /* Damage Multiplier */
    EXTERN_DAMAGE_MULTIPLYER = extern_ctxt.damage;

    /* Freeze */
    if (extern_ctxt.freeze > 0) {
        extern_ctxt.freeze--;
        push_pending_ice_trap();
    }

    /* No Z */
    if (extern_ctxt.no_z) {
        z64_game.common.input[0].raw.pad.z = 0;
        z64_game.common.input[0].pad_pressed.z = 0;
    }

    /* Reverse Controls */
    if (extern_ctxt.reverse_controls) {
        z64_game.common.input[0].raw.x = -z64_game.common.input[0].raw.x;
        z64_game.common.input[0].raw.y = -z64_game.common.input[0].raw.y;
        z64_game.common.input[0].x_diff = -z64_game.common.input[0].x_diff;
        z64_game.common.input[0].y_diff = -z64_game.common.input[0].y_diff;
        z64_game.common.input[0].adjusted_x = -z64_game.common.input[0].adjusted_x;
        z64_game.common.input[0].adjusted_y = -z64_game.common.input[0].adjusted_y;
    }
}
