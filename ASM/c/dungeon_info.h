#ifndef DUNGEON_INFO_H
#define DUNGEON_INFO_H

#include "util.h"
#include "z64.h"

typedef struct {
    uint8_t index;
    struct {
        uint8_t has_keys : 1;
        uint8_t has_boss_key : 1;
        uint8_t has_card : 1;
        uint8_t has_map : 1;
    };
    uint8_t skulltulas;
    char name[11];
    uint8_t silver_rupee_puzzles_vanilla[4];
    uint8_t silver_rupee_puzzles_mq[4];
} dungeon_entry_t;

extern int dungeon_count;
extern dungeon_entry_t dungeons[14];

void draw_dungeon_info(z64_disp_buf_t* db);
void draw_silver_rupee_count(z64_game_t* globalCtx, z64_disp_buf_t* db);

extern unsigned char CFG_DUNGEON_IS_MQ[14];
extern uint32_t CFG_DUNGEON_INFO_ENABLE;
extern uint8_t CFG_DPAD_DUNGEON_INFO_ENABLE;

#define CAN_DRAW_DUNGEON_INFO (CFG_DUNGEON_INFO_ENABLE != 0 && \
        z64_game.pause_ctxt.state == 6 && \
        z64_game.pause_ctxt.screen_idx == 0 && \
        (!z64_game.pause_ctxt.changing || \
        z64_game.pause_ctxt.changing == 3))

#endif
