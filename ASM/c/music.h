#ifndef MUSIC_H
#define MUSIC_H

#include <stdbool.h>
#include "z64.h"
#include "triforce.h"
#include "dungeon_info.h"
#include "model_text.h"

void manage_music_changes();
_Bool Health_IsCritical();
void display_song_name(z64_disp_buf_t* db);
void display_song_name_on_file_select(z64_disp_buf_t* db);

typedef enum {
    /* 0 */ SONG_NAME_NONE, // Never displayed.
    /* 1 */ SONG_NAME_TOP, // Top of the screen.
    /* 2 */ SONG_NAME_PAUSE, // Pause screen only.
} SongNamePosition;


#endif
