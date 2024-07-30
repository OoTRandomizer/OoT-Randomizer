#include "file_select.h"

#include "audio.h"
#include "file_icons.h"
#include "file_message.h"
#include "gfx.h"
#include "music.h"
#include "text.h"
#include "util.h"
#include "save.h"

sprite_t* hash_sprites[2] = {
    &items_sprite,
    &quest_items_sprite,
};

typedef struct {
    uint8_t sprite_index;
    uint8_t tile_index;
} hash_symbol_t;

hash_symbol_t hash_symbols[32] = {
    { 0,  0 }, // Deku Stick
    { 0,  1 }, // Deku Nut
    { 0,  3 }, // Bow
    { 0,  6 }, // Slingshot
    { 0,  7 }, // Fairy Ocarina
    { 0,  9 }, // Bombchu
    { 0, 11 }, // Longshot
    { 0, 14 }, // Boomerang
    { 0, 15 }, // Lens of Truth
    { 0, 16 }, // Beans
    { 0, 17 }, // Megaton Hammer
    { 0, 25 }, // Bottled Fish
    { 0, 26 }, // Bottled Milk
    { 0, 43 }, // Mask of Truth
    { 0, 44 }, // SOLD OUT
    { 0, 46 }, // Cucco
    { 0, 48 }, // Mushroom
    { 0, 50 }, // Saw
    { 0, 53 }, // Frog
    { 0, 60 }, // Master Sword
    { 0, 64 }, // Mirror Shield
    { 0, 65 }, // Kokiri Tunic
    { 0, 70 }, // Hover Boots
    { 0, 81 }, // Silver Gauntlets
    { 0, 84 }, // Gold Scale
    { 1,  9 }, // Stone of Agony
    { 1, 11 }, // Skull Token
    { 1, 12 }, // Heart Container
    { 1, 14 }, // Boss Key
    { 1, 15 }, // Compass
    { 1, 16 }, // Map
    { 1, 19 }, // Big Magic
};

extern uint8_t CFG_FILE_SELECT_HASH[5];

int8_t password_index = -1;
uint16_t tentatives = 0;
uint16_t cooldown = 0;
static const uint8_t TEXT_WIDTH = 8;
static const uint8_t TEXT_HEIGHT = 9;
static const uint8_t BUTTON_WIDTH = 12;
static const uint8_t BUTTON_HEIGHT = 12;
extern uint8_t PASSWORD[PASSWORD_LENGTH];
uint8_t buffer_password[PASSWORD_LENGTH] = {0, 0, 0, 0, 0, 0};

bool is_saved_password_clear(z64_menudata_t* menu_data) {
    // Player can save in file 1 and use file 2 later, so we look at both of them.
    bool fileOkPassword[2] = {true, true};
    for (uint8_t slotFile = 0; slotFile < 2; slotFile++) {
        z64_file_t* file = &menu_data->sram_buffer->primary_saves[slotFile].original_save;
        extended_savecontext_static_t* extended = &(((extended_sram_file_t*)file)->additional_save_data.extended);
        for (uint8_t i = 0 ; i < PASSWORD_LENGTH; i++) {
            if (extended->password[i] != PASSWORD[i]) {
                fileOkPassword[slotFile] = false;
                break;
            }
        }
    }
    return fileOkPassword[0] || fileOkPassword[1];
}

bool is_buffer_password_clear() {
    for (uint8_t i = 0 ; i < PASSWORD_LENGTH; i++) {
        if (buffer_password[i] != PASSWORD[i]) {
            return false;
        }
    }
    return true;
}

void reset_buffer() {
    // Don't reset if it's already the right one.
    if (is_buffer_password_clear()) {
        return;
    }
    password_index = -1;
    for (uint8_t i = 0 ; i < PASSWORD_LENGTH; i++) {
        buffer_password[i] = 0;
    }
}

void manage_password(z64_disp_buf_t* db, z64_menudata_t* menu_data) {
    if (cooldown > 0) {
        cooldown--;
    }
    // Draw "Password locked" at the place of the Controls texture, and a key on the OK button, to display the lock.
    if (!is_saved_password_clear(menu_data) && !is_buffer_password_clear()) {
        int left = 90;
        int top = 204;
        int padding = 8;

        gDPPipeSync(db->p++);
        if (cooldown > 0) {
            colorRGBA8_t color = {0xFF, 0xFF, 0xFF, 0xFF};
            draw_int_size(db, 1 + cooldown / 60, left - 2 * padding, top, color, 6, 12);
        }
        gDPPipeSync(db->p++);
        gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
        sprite_load(db, &quest_items_sprite, 17, 1);
        sprite_draw(db, &quest_items_sprite, 0, left, top - 2, BUTTON_WIDTH, BUTTON_HEIGHT);
        text_print_size(db, "Password locked", left + TEXT_HEIGHT + padding, top, TEXT_WIDTH, TEXT_HEIGHT);
        sprite_draw(db, &quest_items_sprite, 0, left + TEXT_WIDTH + 2 * padding + 15 * font_sprite.tile_w, top - 2, BUTTON_WIDTH, BUTTON_HEIGHT);
    }
    if (menu_data->menu_transition == SM_CONFIRM_FILE) {
        if (password_index < 0) {
            if (menu_data->selected_sub_item == FS_BTN_CONFIRM_YES) {
                if (z64_game.common.input[0].pad_pressed.a || z64_game.common.input[0].pad_pressed.s) {
                    if (is_saved_password_clear(menu_data) || is_buffer_password_clear()) {
                        // Load the game.
                        z64_PlaySFXID(NA_SE_SY_FSEL_DECIDE_L);
                        menu_data->menu_transition = SM_FADE_OUT;
                        Audio_StopCurrentMusic(0xF);
                    } else {
                        if (cooldown == 0) {
                            // Go to password screen.
                            password_index++;
                            return;
                        } else {
                            // Play an error sound until cooldown is finished.
                            z64_PlaySFXID(NA_SE_SY_ERROR);
                        }
                    }
                }
                // Go back one screen.
                if (z64_game.common.input[0].pad_pressed.b) {
                    z64_PlaySFXID(NA_SE_SY_FSEL_CLOSE);
                    menu_data->menu_transition++;
                }
            }
        }
        if (menu_data->selected_sub_item == FS_BTN_CONFIRM_QUIT) { // On the Cancel option, reproduce vanilla behaviour and reset the buffer password.
            if (z64_game.common.input[0].pad_pressed.a || z64_game.common.input[0].pad_pressed.s || z64_game.common.input[0].pad_pressed.b) {
                z64_PlaySFXID(NA_SE_SY_FSEL_CLOSE);
                menu_data->menu_transition++;
                reset_buffer();
            }
        }
        // Password screen.
        if (password_index > -1) {
            uint8_t left_password = 0x37;
            uint8_t top_password = 0x5C;

            gDPPipeSync(db->p++);
            gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
            gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
            text_print_size(db, "Enter Password", left_password, top_password, TEXT_WIDTH, TEXT_HEIGHT);

            if (is_buffer_password_clear()) {
                password_index = -1;
                z64_PlaySFXID(NA_SE_SY_CORRECT_CHIME);
                // Write the password in save context.
                extended_sram_file_t* file = &(menu_data->sram_buffer->primary_saves[menu_data->selected_file]);
                extended_savecontext_static_t* extended = &(file->additional_save_data.extended);
                for (uint8_t i = 0 ; i < PASSWORD_LENGTH; i++) {
                    extended->password[i] = buffer_password[i];
                }
                Sram_WriteSave(NULL, file);
                return;
            } else {
                if (z64_game.common.input[0].pad_pressed.a) {
                    if (menu_data->selected_sub_item == FS_BTN_CONFIRM_YES) {
                        buffer_password[password_index] = 1;
                        password_index++;
                    } else {
                        z64_PlaySFXID(NA_SE_SY_FSEL_CLOSE);
                        menu_data->menu_transition++;
                    }
                }
                if (z64_game.common.input[0].pad_pressed.cd) {
                    buffer_password[password_index] = 2;
                    password_index++;
                }
                if (z64_game.common.input[0].pad_pressed.cr) {
                    buffer_password[password_index] = 3;
                    password_index++;
                }
                if (z64_game.common.input[0].pad_pressed.cl) {
                    buffer_password[password_index] = 4;
                    password_index++;
                }
                if (z64_game.common.input[0].pad_pressed.cu) {
                    buffer_password[password_index] = 5;
                    password_index++;
                }
                if (z64_game.common.input[0].pad_pressed.b) {
                    password_index--;
                    if (password_index < 0) {
                        z64_PlaySFXID(NA_SE_SY_FSEL_CLOSE);
                        reset_buffer();
                    } else {
                        buffer_password[password_index] = 0;
                    }
                }
                if (password_index > 5 && !is_buffer_password_clear()) {
                    tentatives++;
                    // Penalty cooldown every 3 tries, starting from the 6th one.
                    // File select is 60 fps, so 10sec.
                    if (tentatives > 5 && (tentatives % 3) == 0) {
                        cooldown = 600;
                    }
                    z64_PlaySFXID(NA_SE_SY_ERROR);
                    reset_buffer();
                }
            }
            // Draw the password buttons.
            sprite_load(db, &ocarina_button_sprite, 0, 5);
            for (uint8_t i = 0 ; i < password_index + 1; i++) {
                gDPSetPrimColor(db->p++, 0, 0, 0xF4, 0xEC, 0x30, 0xFF); // Yellow C buttons
                if (buffer_password[i] - 1 == 0) { // A is blue
                    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0xFF, 0xFF);
                }
                sprite_draw(db, &ocarina_button_sprite, buffer_password[i] - 1,
                    left_password + i * (BUTTON_WIDTH + 5), top_password + 0x0C, BUTTON_WIDTH, BUTTON_HEIGHT);
            }
        }
    }
}

void draw_file_select_hash(uint32_t fade_out_alpha, z64_menudata_t* menu_data) {
    z64_disp_buf_t* db = &(z64_ctxt.gfx->poly_opa);

    // Call setup display list
    gSPDisplayList(db->p++, &setup_db);

    int icon_count = 5;
    int icon_size = 24;
    int padding = 8;
    int width = (icon_count * icon_size) + ((icon_count - 1) * padding);
    int left = (Z64_SCREEN_WIDTH - width) / 2;
    int top = 12;

    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

    for (int i = 0; i < icon_count; i++) {
        uint8_t sym_index = CFG_FILE_SELECT_HASH[i];
        hash_symbol_t* sym_desc = &(hash_symbols[sym_index]);
        sprite_t* sym_sprite = hash_sprites[sym_desc->sprite_index];

        sprite_load(db, sym_sprite, sym_desc->tile_index, 1);
        sprite_draw(db, sym_sprite, 0, left, top, icon_size, icon_size);

        left += icon_size + padding;
    }

    draw_file_message(db, menu_data);
    if (password_index < 0) {
        draw_file_icons(db, menu_data);
    }
    display_song_name_on_file_select(db);
    manage_password(db, menu_data);
    // Fade out once a file is selected

    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, fade_out_alpha);
    gSPTextureRectangle(db->p++,
            0, 0,
            Z64_SCREEN_WIDTH<<2, Z64_SCREEN_HEIGHT<<2,
            0,
            0, 0,
            1<<10, 1<<10);
}
