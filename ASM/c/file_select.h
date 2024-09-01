#ifndef FILE_SELECT_H
#define FILE_SELECT_H

#include "z64.h"
#define PASSWORD_LENGTH 6

typedef enum {
    /* 0 */ SM_FADE_MAIN_TO_SELECT,
    /* 1 */ SM_MOVE_FILE_TO_TOP,
    /* 2 */ SM_FADE_IN_FILE_INFO,
    /* 3 */ SM_CONFIRM_FILE,
    /* 4 */ SM_FADE_OUT_FILE_INFO,
    /* 5 */ SM_MOVE_FILE_TO_SLOT,
    /* 6 */ SM_FADE_OUT,
    /* 7 */ SM_LOAD_GAME,
} SelectMode;

typedef enum {
    /* 0 */ FS_BTN_CONFIRM_YES,
    /* 1 */ FS_BTN_CONFIRM_QUIT,
} ConfirmButtonIndex;

void draw_file_select_hash(uint32_t fade_out_alpha, z64_menudata_t* menu_data);

void Audio_StopCurrentMusic(uint16_t arg0);

#endif
