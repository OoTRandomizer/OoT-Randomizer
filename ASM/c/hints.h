#ifndef HINTS_H
#define HINTS_H

#include "debug.h"
#include "util.h"
#include "z64.h"

extern uint8_t CFG_HINTS_IDS_AND_TYPES[80];

static uint8_t current_hint_cat_index = 0;
static bool show_hint_info = 0;

void init_hints_ids();
void update_hints();

void draw_hints(z64_disp_buf_t* db);
bool hint_menu_is_drawn();
void message_id_check(z64_game_t* play, uint16_t textId);

void Message_OpenText(z64_game_t* play, uint16_t textId);

#endif
