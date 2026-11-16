#ifndef MESSAGE_H
#define MESSAGE_H

#include "z64.h"

extern uint16_t current_textbox_id;
void Message_OpenText(z64_game_t* play, uint16_t textId);
void display_misc_messages();

#endif
