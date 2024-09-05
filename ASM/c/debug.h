#ifndef DEBUG_H
#define DEBUG_H

#define DEBUG_MODE 0

#include "z64.h"
#include "gfx.h"
#include "text.h"
#include "item_effects.h"

extern uint8_t SKIP_N64_LOGO;
void Actor_SetColorFilter(z64_actor_t* actor, int16_t colorFlag, int16_t colorIntensityMax, int16_t bufFlag, int16_t duration);

typedef struct {
    int8_t main_index;
    int8_t sub_menu_index;
    int8_t dungeon_index;
    int8_t room_index;
    int8_t overworld_index;
    int8_t boss_index;
    int8_t item_index;
    int8_t actor_index;
    int8_t specific_actor_index;
    int8_t overlay_index;
} menu_index_t;

typedef struct {
    uint8_t index;
    char name[15];
} menu_category_t;

typedef struct {
    uint8_t index;
    uint16_t entrance_index;
    char name[30];
} warp_t;

typedef struct {
    int32_t scene_index;
    int32_t room_index;
    z64_xyzf_t pos;
    uint16_t yaw;
    char name[30];
} room_t;

typedef struct {
    uint8_t number_of_rooms;
    room_t* room;
} rooms_t;


typedef struct {
    uint8_t index;
    uint16_t item_index;
    char name[30];
} item_t;

typedef enum
{
  DEBUG_NUMBER_NONE,
  DEBUG_NUMBER_INT,
  DEBUG_NUMBER_FLOAT,
} debug_number_type;

static uint8_t debugNumberIsInUsage[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
static int32_t debugNumbers[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
static float debugNumbersFloat[10] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
static menu_index_t current_menu_indexes = {0, 0, 0, 0, 0, 0, 0, 0};
static uint8_t show_warp_menu = 0;

typedef void(*usebutton_t)(z64_game_t *game, z64_link_t *link, uint8_t item, uint8_t button);
#define z64_usebutton ((usebutton_t)    0x8038C9A0)

void debug_utilities(z64_disp_buf_t *db);
void draw_debug_menu(z64_disp_buf_t *db);
void draw_debug_numbers(z64_disp_buf_t *db);
int debug_menu_is_drawn();
void draw_debug_int(int whichNumber, int numberToShow);
void draw_debug_float(int whichNumber, float numberToShow);

#endif
