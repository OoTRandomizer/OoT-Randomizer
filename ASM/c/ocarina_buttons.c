#include "ocarina_buttons.h"
#include "gfx.h"

uint8_t has_a_button() {
    return !SHUFFLE_OCARINA_BUTTONS || z64_file.scene_flags[0x50].unk_00_ & 1 << 0;
}

uint8_t has_cup_button() {
    return !SHUFFLE_OCARINA_BUTTONS || z64_file.scene_flags[0x50].unk_00_ & 1 << 1;
}

uint8_t has_cdown_button() {
    return !SHUFFLE_OCARINA_BUTTONS || z64_file.scene_flags[0x50].unk_00_ & 1 << 2;
}

uint8_t has_cleft_button() {
    return !SHUFFLE_OCARINA_BUTTONS || z64_file.scene_flags[0x50].unk_00_ & 1 << 3;
}

uint8_t has_cright_button() {
    return !SHUFFLE_OCARINA_BUTTONS || z64_file.scene_flags[0x50].unk_00_ & 1 << 4;
}

uint8_t c_block_ocarina() {
    uint8_t res = 0;
    if (!(has_a_button())) { // A
        res |= 1 << 0;
    }
    if (!(has_cup_button())) { // C up
        res |= 1 << 1;
    }
    if (!(has_cdown_button())) { // C down
        res |= 1 << 2;
    }
    if (!(has_cleft_button())) { // C left
        res |= 1 << 3;
    }
    if (!(has_cright_button())) { // C right
        res |= 1 << 4;
    }
    return res;
}
extern uint8_t EPONAS_SONG_NOTES;
int8_t can_spawn_epona() {
    if (!SHUFFLE_OCARINA_BUTTONS) {
        return 1;
    }
    return (c_block_ocarina() & EPONAS_SONG_NOTES) ? 0 : 1;
}

extern uint8_t SHOW_OCARINA_MELODIES;
void print_ocarina_a(z64_disp_buf_t* db, uint8_t left, uint8_t top) {
    int icon_width = 8;
    int icon_height = 8;
    gDPSetPrimColor(db->p++, 0, 0, 0x5A, 0x5A, 0xFF, 0xFF);
    if (!(has_a_button())) {
        gDPSetPrimColor(db->p++, 0, 0, 0x40, 0x40, 0x40, 0x90);
    }
    sprite_draw(db, &ocarina_button_sprite, 0, left, top, icon_width, icon_height);
}

void print_ocarina_cup(z64_disp_buf_t* db, uint8_t left, uint8_t top) {
    int icon_width = 8;
    int icon_height = 8;
    gDPSetPrimColor(db->p++, 0, 0, 0xFA, 0xA0, 0x00, 0xFF);
    if (!(has_cup_button())) {
        gDPSetPrimColor(db->p++, 0, 0, 0x40, 0x40, 0x40, 0x90);
    }
    sprite_draw(db, &ocarina_button_sprite, 4, left, top, icon_width, icon_height);
}

void print_ocarina_cdown(z64_disp_buf_t* db, uint8_t left, uint8_t top) {
    int icon_width = 8;
    int icon_height = 8;
    gDPSetPrimColor(db->p++, 0, 0, 0xFA, 0xA0, 0x00, 0xFF);
    if (!(has_cdown_button())) {
        gDPSetPrimColor(db->p++, 0, 0, 0x40, 0x40, 0x40, 0x90);
    }
    sprite_draw(db, &ocarina_button_sprite, 1, left, top, icon_width, icon_height);
}

void print_ocarina_cleft(z64_disp_buf_t* db, uint8_t left, uint8_t top) {
    int icon_width = 8;
    int icon_height = 8;
    gDPSetPrimColor(db->p++, 0, 0, 0xFA, 0xA0, 0x00, 0xFF);
    if (!(has_cleft_button())) {
        gDPSetPrimColor(db->p++, 0, 0, 0x40, 0x40, 0x40, 0x90);
    }
    sprite_draw(db, &ocarina_button_sprite, 3, left, top, icon_width, icon_height);
}

void print_ocarina_cright(z64_disp_buf_t* db, uint8_t left, uint8_t top) {
    int icon_width = 8;
    int icon_height = 8;
    gDPSetPrimColor(db->p++, 0, 0, 0xFA, 0xA0, 0x00, 0xFF);
    if (!(has_cright_button())) {
        gDPSetPrimColor(db->p++, 0, 0, 0x40, 0x40, 0x40, 0x90);
    }
    sprite_draw(db, &ocarina_button_sprite, 2, left, top, icon_width, icon_height);
}

extern int8_t SONG_MELODIES[0x60];
typedef struct {
    colorRGBA8_t color;
    uint8_t pos;
} song_color_and_position;
const song_color_and_position songs_colors_and_positions[12] = {
    {{0x97, 0xFF, 0x63, 0xFF}, 6}, // Minuet
    {{0xFF, 0x50, 0x28, 0xFF}, 7}, // Bolero
    {{0x63, 0x97, 0xFF, 0xFF}, 8}, // Serenade
    {{0xFF, 0x63, 0xFF, 0xFF}, 10}, // Nocturne
    {{0xFF, 0x9F, 0x00, 0xFF}, 9}, // Requiem
    {{0xFF, 0xF0, 0x63, 0xFF}, 11},// Prelude
    {{0xFF, 0x50, 0x28, 0xFF}, 0}, // ZL
    {{0xFF, 0x9F, 0x00, 0xFF}, 1}, // Epona
    {{0x97, 0xFF, 0x63, 0xFF}, 2}, // Saria
    {{0xFF, 0xF0, 0x63, 0xFF}, 3}, // Suns
    {{0x63, 0x97, 0xFF, 0xFF}, 4}, // SoT
    {{0xFF, 0x63, 0xFF, 0xFF}, 5}, // SoS
};

uint8_t ocarina_action_ok(uint16_t ocarinaAction) {

    if (ocarinaAction == 1) { // OCARINA_ACTION_FREE_PLAY
        return 1;
    }
    if (ocarinaAction >= 0x1C && // OCARINA_ACTION_CHECK_MINUET
        ocarinaAction <= 0x27) { // OCARINA_ACTION_CHECK_STORMS
        return 1;
    }
    if (ocarinaAction == 0x30) { // OCARINA_ACTION_CHECK_NOWARP
        return 1;
    }
    return 0;
}

void draw_ocarina_melodies(z64_disp_buf_t* db) {

    if (!SHOW_OCARINA_MELODIES) {
        return;
    }

    MessageContext *msgCtx = &(z64_game.msgContext);
    if (!(z64_link.state_flags_2 & 0x8000000) ||
        !ocarina_action_ok(msgCtx->ocarinaAction)) {
        return;
    }

    gSPDisplayList(db->p++, &setup_db);

    // Set up dimensions
    int icon_size = 8;
    int font_width = 6;
    int font_height = 11;
    int rows = 12;
    int bg_width = 9 * icon_size;
    int bg_height = rows * icon_size;
    int bg_left = 30;
    int bg_top = 30;

    gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xD0);
    gSPTextureRectangle(db->p++,
            bg_left<<2, bg_top<<2,
            (bg_left + bg_width)<<2, (bg_top + bg_height)<<2,
            0,
            0, 0,
            1<<10, 1<<10);

    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    uint16_t songsBits = (uint16_t)((z64_file.quest_items >> 6) & 0x0FFF);

    for (int i = 0; i < 12; i++) {
        // Check if we have the song
        if ((songsBits & 0x1) == 0) {
            songsBits >>= 1;
            continue;
        }
        songsBits >>= 1;

        // Draw a colored note sprite.
        colorRGBA8_t color = songs_colors_and_positions[i].color;
        uint8_t position = songs_colors_and_positions[i].pos;
        gDPSetPrimColor(db->p++, 0, 0, color.r, color.g, color.b, color.a);
        sprite_load(db, &song_note_sprite, 0, 1);
        sprite_draw(db, &song_note_sprite, 0, bg_left, bg_top + position * icon_size, icon_size, icon_size);
        uint8_t song_sprite_length = icon_size;

        sprite_load(db, &ocarina_button_sprite, 0, 5);
        for (int j = 0; j < 8; j++) {
            switch (SONG_MELODIES[position * 8 + j])
            {
                case 0:
                    print_ocarina_a(db, bg_left + song_sprite_length + j * icon_size, bg_top + position * icon_size);
                    break;
                case 1:
                    print_ocarina_cup(db, bg_left + song_sprite_length + j * icon_size, bg_top + position * icon_size);
                    break;
                case 2:
                    print_ocarina_cdown(db, bg_left + song_sprite_length + j * icon_size, bg_top + position * icon_size);
                    break;
                case 3:
                    print_ocarina_cleft(db, bg_left + song_sprite_length + j * icon_size, bg_top + position * icon_size);
                    break;
                case 4:
                    print_ocarina_cright(db, bg_left + song_sprite_length + j * icon_size, bg_top + position * icon_size);
                    break;
                default:
                    break;
            }
        }
    }
    gDPPipeSync(db->p++);
}
