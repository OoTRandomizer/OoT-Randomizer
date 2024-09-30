#include "file_message.h"

#include "text.h"

extern uint8_t CFG_SHOW_SETTING_INFO;
extern char WEB_ID_STRING_TXT[];
extern char WORLD_STRING_TXT[];
extern char CFG_CUSTOM_MESSAGE_1[];
extern char CFG_CUSTOM_MESSAGE_2[];
extern char VERSION_STRING_TXT[];
extern char TIME_STRING_TXT[];
extern uint8_t SPOILER_AVAILABLE;
extern uint8_t PLANDOMIZER_USED;

#define TEXT_WIDTH 8
#define TEXT_HEIGHT 9

static int string_length(const char* txt) {
    const char* pos = txt;
    while (*pos) ++pos;
    return pos - txt;
}

static uint8_t get_alpha(const z64_menudata_t* menu_data) {
    uint8_t alt_tr = (uint8_t)menu_data->alt_transition;
    if (0x20 <= alt_tr && alt_tr <= 0x27) {
        return 0;
    }

    if (menu_data->file_message != -1) {
        return 0;
    }

    unsigned int alpha = menu_data->alpha_levels.copy_button * 0x00FF / 0x00C8;
    return (uint8_t)(alpha <= 0xFF ? alpha : 0xFF);
}

static void print_msg(z64_disp_buf_t* db, const char* s, int* top) {
    if (*s != '\0') {
        text_print_size(db, s, 0x80, *top, TEXT_WIDTH, TEXT_HEIGHT);
        *top += TEXT_HEIGHT + 1;
    }
    else {
        *top += TEXT_HEIGHT / 2 + 1;
    }
}

void draw_file_message(z64_disp_buf_t* db, const z64_menudata_t* menu_data) {
    if (WEB_ID_STRING_TXT[0] != '\0') {
        gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
        int icon_count = 5;
        int icon_size = 24;
        int padding = 8;
        int width = (icon_count * icon_size) + ((icon_count - 1) * padding);
        int right = (Z64_SCREEN_WIDTH - width) / 2 - padding;
        int left = right - 10 * TEXT_WIDTH;

        text_print_size(db, "   Seed ID", left, 24 - TEXT_HEIGHT, TEXT_WIDTH, TEXT_HEIGHT);
        text_print_size(db, WEB_ID_STRING_TXT, left, 24, TEXT_WIDTH, TEXT_HEIGHT);
    }

    if (WORLD_STRING_TXT[0] != '\0') {
        gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
        int icon_count = 5;
        int icon_size = 24;
        int padding = 8;
        int width = (icon_count * icon_size) + ((icon_count - 1) * padding);
        int left = (Z64_SCREEN_WIDTH + width) / 2 + padding;

        text_print_size(db, "World", left, 24 - TEXT_HEIGHT, TEXT_WIDTH, TEXT_HEIGHT);
        text_print_size(db, WORLD_STRING_TXT, left, 24, TEXT_WIDTH, TEXT_HEIGHT);
    }

    if (CFG_SHOW_SETTING_INFO) {
        uint8_t alpha = get_alpha(menu_data);
        if (alpha > 0) {
            gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, alpha);
            int top = 0x71;
            int doblank = 0;
            if (*CFG_CUSTOM_MESSAGE_1) {
                print_msg(db, CFG_CUSTOM_MESSAGE_1, &top);
                doblank = 1;
            }
            if (*CFG_CUSTOM_MESSAGE_2) {
                print_msg(db, CFG_CUSTOM_MESSAGE_2, &top);
                doblank = 1;
            }
            if (doblank) {
                print_msg(db, "",                   &top);
            }
            print_msg(db, "Generated with OoTR",    &top);
            print_msg(db, VERSION_STRING_TXT,       &top);
            print_msg(db, TIME_STRING_TXT,          &top);
            print_msg(db, "",                       &top);

            if (SPOILER_AVAILABLE) {
                print_msg(db, "Spoiler available",  &top);
            }
            if (PLANDOMIZER_USED) {
                print_msg(db, "Plandomizer",        &top);
            }

        }
    }
}
