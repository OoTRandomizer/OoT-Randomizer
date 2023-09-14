#include "triforce.h"

static uint32_t frames = 0;
static uint32_t render_triforce_flag = 0;
#define FRAMES_PER_CYCLE 2
#define TRIFORCE_SPRITE_FRAMES 16
#define TRIFORCE_FRAMES_VISIBLE 100 // 20 Frames seems to be about 1 second
#define TRIFORCE_FRAMES_FADE_AWAY 80
#define TRIFORCE_FRAMES_FADE_INTO 5
uint8_t minimap_triforce_state = 0;

void set_triforce_render() {
    render_triforce_flag = 1;
    frames = frames > TRIFORCE_FRAMES_FADE_INTO ? TRIFORCE_FRAMES_FADE_INTO : frames;
}

void handle_lbutton_and_minimap_state()
{
    switch (minimap_triforce_state)
    {
        case MINIMAP_ON_SCREEN:
            R_MINIMAP_DISABLED = render_triforce_flag == 1;
            break;
        case TRIFORCE_OR_SKULL_ON_SCREEN:
            R_MINIMAP_DISABLED = 1;
            break;
        case NONE_ON_SCREEN:
            R_MINIMAP_DISABLED = 1;
            break;
        default:
            break;
    }

    if (z64_game.common.input[0].pad_pressed.l) {
        minimap_triforce_state++;
        if (minimap_triforce_state > NONE_ON_SCREEN) {
            minimap_triforce_state = MINIMAP_ON_SCREEN;
        }
        switch (minimap_triforce_state)
        {
            case MINIMAP_ON_SCREEN:
                R_MINIMAP_DISABLED = 0;
                PlaySFX(0x4814); //NA_SE_SY_CAMERA_ZOOM_DOWN
                break;
            case TRIFORCE_OR_SKULL_ON_SCREEN:
                R_MINIMAP_DISABLED = 1;
                PlaySFX(0x4845); //NA_SE_SY_CARROT_RECOVER
                break;
            case NONE_ON_SCREEN:
                R_MINIMAP_DISABLED = 1;
                PlaySFX(0x4813); //NA_SE_SY_CAMERA_ZOOM_UP
                break;
            default:
                break;
        }
    }
}

void draw_skull_count(z64_disp_buf_t *db) {

    if (!CAN_DRAW_TRIFORCE || !(minimap_triforce_state == TRIFORCE_OR_SKULL_ON_SCREEN)) {
        return;
    }

    int pieces = z64_file.gs_tokens;

    int pieces_digits = 0;
    int pieces_copy = pieces;
    while(pieces_copy >= 1) {
        pieces_digits++;
        pieces_copy /= 10;
    }
    pieces_digits = pieces_digits == 0 ? 1 : pieces_digits;

    // Setup draw location
    int str_len = pieces_digits;
    int total_w = str_len * font_sprite.tile_w + triforce_sprite.tile_w * 0.9;
    // Draw the counter symmetric to the rupee icon at (left, top) = (26, 206)
    int draw_x = (Z64_SCREEN_WIDTH - 26) - total_w - 1;
    int draw_y_text = 206;
    int draw_y_skull = 206;
    // Above Triforce counter if there is one.
    if (TRIFORCE_HUNT_ENABLED) {
        draw_y_text -= font_sprite.tile_h + 1;
        draw_y_skull -= font_sprite.tile_h + 1;
    }

    // Call setup display list
    gSPDisplayList(db->p++, &setup_db);
    gDPPipeSync(db->p++);

    //text_print(text, draw_x, draw_y_text);
    //text_flush(db);
    colorRGBA8_t color = { 0xFF, 0xFF, 0xFF, 0xFF};
    draw_int(db, z64_file.gs_tokens, draw_x, draw_y_text, color);
    draw_x += str_len * font_sprite.tile_w + 1;

    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
    sprite_load(db, &quest_items_sprite, 11, 1);
    sprite_draw(db, &quest_items_sprite, 0, draw_x, draw_y_skull, triforce_sprite.tile_w * 0.9, triforce_sprite.tile_h * 0.9);
}

void draw_triforce_count(z64_disp_buf_t *db) {

    // Must be triforce hunt and triforce should be drawable, and we should either be on the pause screen or the render triforce flag should be set
    if (!(TRIFORCE_HUNT_ENABLED && CAN_DRAW_TRIFORCE &&
        (render_triforce_flag == 1 || z64_game.pause_ctxt.state == 6 || minimap_triforce_state == TRIFORCE_OR_SKULL_ON_SCREEN))) {
        return;
    }

    uint8_t alpha;
    // In the pause screen always draw
    if (z64_game.pause_ctxt.state == 6 || minimap_triforce_state == TRIFORCE_OR_SKULL_ON_SCREEN) {
        alpha = 255;
        frames = frames % (TRIFORCE_SPRITE_FRAMES * FRAMES_PER_CYCLE);
    } else {
        // Do a fade in/out effect if not in pause screen
        if (frames <= TRIFORCE_FRAMES_FADE_INTO) {
            // Disable minimap until the counter is faded out.
            if (minimap_triforce_state == MINIMAP_ON_SCREEN) {
                R_MINIMAP_DISABLED = 1;
            }
            alpha = frames * 255 / TRIFORCE_FRAMES_FADE_INTO;
        } else if (frames <= TRIFORCE_FRAMES_FADE_INTO + TRIFORCE_FRAMES_VISIBLE ) {
            alpha = 255;
        } else if (frames <= TRIFORCE_FRAMES_FADE_INTO + TRIFORCE_FRAMES_VISIBLE + TRIFORCE_FRAMES_FADE_AWAY) {
            alpha = (frames - TRIFORCE_FRAMES_FADE_INTO - TRIFORCE_FRAMES_VISIBLE) * 255 /  TRIFORCE_FRAMES_FADE_AWAY;
            alpha = 255 - alpha;
        } else {
            if (minimap_triforce_state == MINIMAP_ON_SCREEN) {
                R_MINIMAP_DISABLED = 0;
            }
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
    // Draw the counter symmetric to the rupee icon at (left, top) = (26, 206)
    int draw_x = (Z64_SCREEN_WIDTH - 26) - total_w;
    int draw_y_text = 206;
    int draw_y_triforce = 206;

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

    text_print(text, draw_x, draw_y_text);
    draw_x += str_len * font_sprite.tile_w;

    gDPSetPrimColor(db->p++, 0, 0, 0xF4, 0xEC, 0x30, alpha);
    // Draw triforce
    int sprite = (frames / FRAMES_PER_CYCLE) % TRIFORCE_SPRITE_FRAMES;
    sprite_load(db, &triforce_sprite, sprite, 1);
    sprite_draw(db, &triforce_sprite, 0, draw_x, draw_y_triforce, triforce_sprite.tile_w, triforce_sprite.tile_h);

    text_flush(db);
}
