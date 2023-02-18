#ifndef DUNGEON_INFO_H
#define DUNGEON_INFO_H

#include "util.h"

void draw_dungeon_info();

extern unsigned char CFG_DUNGEON_IS_MQ[14];
extern uint32_t CFG_DUNGEON_INFO_ENABLE;
extern uint8_t CFG_DPAD_DUNGEON_INFO_ENABLE;

#define CAN_DRAW_DUNGEON_INFO (CFG_DUNGEON_INFO_ENABLE != 0 && \
        z64_game.pause_ctxt.state == 6 && \
        z64_game.pause_ctxt.screen_idx == 0 && \
        (!z64_game.pause_ctxt.changing || \
        z64_game.pause_ctxt.changing == 3))

#endif
