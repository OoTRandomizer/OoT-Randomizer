#include "music.h"

extern uint8_t CFG_SPEEDUP_MUSIC_FOR_LAST_TRIFORCE_PIECE;
extern uint8_t CFG_SLOWDOWN_MUSIC_WHEN_LOWHP;
extern char CFG_SONG_NAMES[];
extern uint8_t CFG_SONG_NAME_STATE;

static uint16_t previousSeqIndexChange = 0;
static uint8_t isSlowedDown = 0;
static uint8_t isSpeedup = 0;

void manage_music_changes() {
    if (CFG_SPEEDUP_MUSIC_FOR_LAST_TRIFORCE_PIECE && !isSlowedDown) {
        if (z64_file.scene_flags[0x48].unk_00_ == TRIFORCE_PIECES_REQUIRED - 1 &&
            z64_Audio_GetActiveSeqId(0) != previousSeqIndexChange) {
            // One tone up : 2^(2/12)
            z64_ScalePitchAndTempo(1.12246f, 0);
            previousSeqIndexChange = z64_Audio_GetActiveSeqId(0);
            isSpeedup = 1;
        }
    }
    if (CFG_SLOWDOWN_MUSIC_WHEN_LOWHP) {
        if (Health_IsCritical()) {
            if (z64_Audio_GetActiveSeqId(0) != previousSeqIndexChange || isSpeedup) {
                // One tone down : 2^(-2/12)
                z64_ScalePitchAndTempo(0.89089f, 0);
                previousSeqIndexChange = z64_Audio_GetActiveSeqId(0);
                isSlowedDown = 1;
                isSpeedup = 0;
            }
        } else if (isSlowedDown) {
            z64_ScalePitchAndTempo(1.0f, 0);
            isSlowedDown = 0;
            previousSeqIndexChange = 0;
        }
    }
}

_Bool Health_IsCritical(void) {
    int16_t criticalHealth;

    if (z64_file.energy_capacity <= 0x50) {
        criticalHealth = 0x10;
    } else if (z64_file.energy_capacity <= 0xA0) {
        criticalHealth = 0x18;
    } else if (z64_file.energy_capacity <= 0xF0) {
        criticalHealth = 0x20;
    } else {
        criticalHealth = 0x2C;
    }

    if (criticalHealth >= z64_file.energy && z64_file.energy > 0) {
        return true;
    } else {
        return false;
    }
}

int bgm_sequence_ids[47] = {
    0x02, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2C, 0x2D,
    0x2E, 0x2F, 0x30, 0x38, 0x3A, 0x3C, 0x3E, 0x3F, 0x40, 0x42, 0x4A, 0x4B, 0x4C, 0x4E, 0x4F, 0x50,
    0x55, 0x56, 0x58, 0x5A, 0x5B, 0x5C, 0x5F, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x6B, 0x6C,
};

static const uint8_t TEXT_WIDTH = 6;
static const uint8_t TEXT_HEIGHT = 11;
static const uint8_t SONG_NAME_FRAMES_VISIBLE = 100;
static const uint8_t SONG_NAME_FRAMES_FADE_AWAY = 80;
static const uint8_t SONG_NAME_FRAMES_FADE_INTO = 5;
static uint32_t frames = 0;
static uint32_t display_song_name_flag = 0;
static uint16_t previousSeqIndexName = 0;

void display_song_name(z64_disp_buf_t* db) {
    if (CFG_SONG_NAME_STATE > SONG_NAME_NONE &&
        !dungeon_info_is_drawn() && // Don't display if the custom rando pause screen if displayed.
        !(z64_link.state_flags_2 & 0x8000000)) { // Don't display if Link is playing the Ocarina.

        uint8_t alpha;
        if (z64_Audio_GetActiveSeqId(0) != previousSeqIndexName) {
            display_song_name_flag = 1;
            previousSeqIndexName = z64_Audio_GetActiveSeqId(0);
            alpha = 255;
            frames = 0;
        }
        if (!(display_song_name_flag == 1 || z64_game.pause_ctxt.state == PAUSE_STATE_MAIN)) {
            return;
        }

        // If model text is displayed, don't show the names in inventory screen.
        if (illegal_model && z64_game.pause_ctxt.state == 6 && z64_game.pause_ctxt.screen_idx == 0) {
            return;
        }

        if (z64_game.pause_ctxt.state == PAUSE_STATE_MAIN) {
            alpha = 255;
            frames = 0;
        }
        else if (CFG_SONG_NAME_STATE == SONG_NAME_PAUSE) {
            return;
        }
        else {
            // Do a fade in/out effect if not in pause screen
            if (frames <= SONG_NAME_FRAMES_FADE_INTO) {
                alpha = frames * 255 / SONG_NAME_FRAMES_FADE_INTO;
            } else if (frames <= SONG_NAME_FRAMES_FADE_INTO + SONG_NAME_FRAMES_VISIBLE) {
                alpha = 255;
            } else if (frames <= SONG_NAME_FRAMES_FADE_INTO + SONG_NAME_FRAMES_VISIBLE + SONG_NAME_FRAMES_FADE_AWAY) {
                alpha = (frames - SONG_NAME_FRAMES_FADE_INTO - SONG_NAME_FRAMES_VISIBLE) * 255 /  SONG_NAME_FRAMES_FADE_AWAY;
                alpha = 255 - alpha;
            } else {
                frames = 0;
                display_song_name_flag = 0;
                return;
            }
        }

        frames++;
        uint8_t top = 7;
        uint8_t left = 7;
        int8_t bgm_found = -1;
        for (uint8_t i = 0; i < 47; i++) {
            if (z64_Audio_GetActiveSeqId(0) == bgm_sequence_ids[i]) {
                bgm_found = i;
                break;
            }
            // In case the active sequence was not listed.
            bgm_found = -1;
        }
        if (bgm_found > -1 && bgm_found < 47) {
            char subStringName[50];
            uint8_t subStringNameLength = 0;
            for (uint8_t j = 0; j < 50; j++) {
                subStringName[j] = CFG_SONG_NAMES[j + bgm_found * 50];
                if (subStringName[j] == '\0') {
                    break;
                }
                subStringNameLength++;
            }
            gSPDisplayList(db->p++, &setup_db);
            gDPPipeSync(db->p++);
            gDPSetPrimColor(db->p++, 0, 0, 0, 0, 0, alpha);
            text_print_size(db, subStringName, left + 1, top + 1, TEXT_WIDTH, TEXT_HEIGHT);
            gDPPipeSync(db->p++);
            gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, alpha);
            text_print_size(db, subStringName, left, top, TEXT_WIDTH, TEXT_HEIGHT);
            gDPPipeSync(db->p++);
        }
    }
}

void display_song_name_on_file_select(z64_disp_buf_t* db) {
    if (CFG_SONG_NAME_STATE > SONG_NAME_NONE) {
        uint8_t top = 7;
        uint8_t left = 7;
        uint8_t alpha = 255;
        uint8_t bgm_fileselect = 11;  // ("Fairy Fountain", 0x28)
        char subStringName[50];
        uint8_t subStringNameLength = 0;
        for (uint8_t j = 0; j < 50; j++) {
            subStringName[j] = CFG_SONG_NAMES[j + 11 * 50];
            if (subStringName[j] == '\0') {
                break;
            }
            subStringNameLength++;
        }
        gSPDisplayList(db->p++, &setup_db);
        gDPPipeSync(db->p++);
        gDPSetPrimColor(db->p++, 0, 0, 0, 0, 0, alpha);
        text_print_size(db, subStringName, left + 1, top + 1, TEXT_WIDTH, TEXT_HEIGHT);
        gDPPipeSync(db->p++);
        gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, alpha);
        text_print_size(db, subStringName, left, top, TEXT_WIDTH, TEXT_HEIGHT);
    }
}
