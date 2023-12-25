#include "triforce.h"

static uint32_t frames = 0;
static uint32_t render_triforce_flag = 0;
#define FRAMES_PER_CYCLE 2
#define TRIFORCE_SPRITE_FRAMES 16
#define TRIFORCE_FRAMES_VISIBLE 100 // 20 Frames seems to be about 1 second
#define TRIFORCE_FRAMES_FADE_AWAY 80
#define TRIFORCE_FRAMES_FADE_INTO 5

void set_triforce_render() {
    render_triforce_flag = 1;
    frames = frames > TRIFORCE_FRAMES_FADE_INTO ? TRIFORCE_FRAMES_FADE_INTO : frames;
}

void draw_triforce_count(z64_disp_buf_t* db) {

    // Must be triforce hunt and triforce should be drawable, and we should either be on the pause screen or the render triforce flag should be set
    if (!(TRIFORCE_HUNT_ENABLED && CAN_DRAW_TRIFORCE && (render_triforce_flag == 1 || z64_game.pause_ctxt.state == 6))) {
        return;
    }

    uint8_t alpha;
    // In the pause screen always draw
    if (z64_game.pause_ctxt.state == 6) {
        alpha = 255;
        frames = frames % (TRIFORCE_SPRITE_FRAMES * FRAMES_PER_CYCLE);
    } else {
        // Do a fade in/out effect if not in pause screen
        if ( frames <= TRIFORCE_FRAMES_FADE_INTO ) {
            alpha = frames * 255 / TRIFORCE_FRAMES_FADE_INTO;
        } else if (frames <= TRIFORCE_FRAMES_FADE_INTO + TRIFORCE_FRAMES_VISIBLE ) {
            alpha = 255;
        } else if (frames <= TRIFORCE_FRAMES_FADE_INTO + TRIFORCE_FRAMES_VISIBLE + TRIFORCE_FRAMES_FADE_AWAY) {
            alpha = (frames - TRIFORCE_FRAMES_FADE_INTO - TRIFORCE_FRAMES_VISIBLE) * 255 /  TRIFORCE_FRAMES_FADE_AWAY;
            alpha = 255 - alpha;
        } else {
            render_triforce_flag = 0;
            frames = 0;
            return;
        }
    }

    frames++;

    int pieces = z64_file.scene_flags[0x48].unk_00_; //Unused word in scene x48.

    // Get length of string to draw
    // Theres probably a better way to do this, log 10 wasnt working though
    int pieces_digits = 0;
    int pieces_copy = pieces;
    while(pieces_copy >= 1) {
        pieces_digits++;
        pieces_copy /= 10;
    }
    pieces_digits = pieces_digits == 0 ? 1 : pieces_digits;
    int required_digits = 0;
    int required_copy = TRIFORCE_PIECES_REQUIRED;
    while(required_copy >= 1) {
        required_digits++;
        required_copy /= 10;
    }
    required_digits = required_digits == 0 ? 1 : required_digits;

    // Setup draw location
    int str_len = required_digits + pieces_digits + 1;
    int total_w = str_len * font_sprite.tile_w + triforce_sprite.tile_w;
    int draw_x = Z64_SCREEN_WIDTH / 2 - total_w / 2;
    int draw_y_text = Z64_SCREEN_HEIGHT - (font_sprite.tile_h * 1.5) + 1;
    int draw_y_triforce = Z64_SCREEN_HEIGHT - (triforce_sprite.tile_h * 1.5) + 3 + 1;

    // Create collected/required string
    char text[str_len + 1];
    text[str_len] = 0;
    pieces_copy = pieces;
    for(int i = pieces_digits - 1; i >= 0; i--) {
        text[i] = (pieces_copy % 10) + '0';
        pieces_copy /= 10;
    }
    text[pieces_digits] = 0x2F; // writes a slash (/)
    required_copy = TRIFORCE_PIECES_REQUIRED;
    for(int i = str_len - 1; i > pieces_digits; i--) {
        text[i] = (required_copy % 10) + '0';
        required_copy /= 10;
    }

    // Call setup display list
    gSPDisplayList(db->p++, &setup_db);
    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    gDPSetPrimColor(db->p++, 0, 0, 0xDA, 0xD3, 0x0B, alpha);

    text_print(text , draw_x, draw_y_text);
    draw_x += str_len * font_sprite.tile_w;

    gDPSetPrimColor(db->p++, 0, 0, 0xF4, 0xEC, 0x30, alpha);
    // Draw triforce
    int sprite = (frames / FRAMES_PER_CYCLE) % TRIFORCE_SPRITE_FRAMES;
    sprite_load(db, &triforce_sprite, sprite, 1);
    sprite_draw(db, &triforce_sprite, 0, draw_x, draw_y_triforce, triforce_sprite.tile_w, triforce_sprite.tile_h);

    text_flush(db);
}
