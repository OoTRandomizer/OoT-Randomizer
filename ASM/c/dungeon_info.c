#include <stdbool.h>
#include "dungeon_info.h"
#include "gfx.h"
#include "text.h"
#include "z64.h"
#include "trade_quests.h"
#include "dpad.h"
#include "item_effects.h"
#include "save.h"

int dungeon_count = 13;

dungeon_entry_t dungeons[] = {
    {  0, 0, 0, 0, 1, 0x0F, "Deku",      {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    {  1, 0, 0, 0, 1, 0x1F, "Dodongo",   {-1, -1, -1, -1}, { 0, -1, -1, -1} },
    {  2, 0, 0, 0, 1, 0x0F, "Jabu",      {-1, -1, -1, -1}, {-1, -1, -1, -1} },

    {  3, 1, 1, 0, 1, 0x1F, "Forest",    {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    {  4, 1, 1, 0, 1, 0x1F, "Fire",      {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    {  5, 1, 1, 0, 1, 0x1F, "Water",     {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    {  7, 1, 1, 0, 1, 0x1F, "Shadow",    { 4,  6,  7, -1}, { 4,  5,  6,  7} },
    {  6, 1, 1, 0, 1, 0x1F, "Spirit",    {11, 14, 12, -1}, {13, 15, -1, -1} },

    {  8, 1, 0, 0, 1, 0x07, "BotW",      { 3, -1, -1, -1}, {-1, -1, -1, -1} },
    {  9, 0, 0, 0, 1, 0x07, "Ice",       { 1,  2, -1, -1}, {-1, -1, -1, -1} },
    { 12, 1, 0, 1, 0, 0x00, "Hideout",   {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    { 11, 1, 0, 0, 0, 0x00, "GTG",       { 8,  9, 10, -1}, { 8,  9, 10, -1} },
    { 13, 1, 1, 0, 0, 0x00, "Ganon",     {16, 17, 18, 21}, {18, 19, 20, -1} },
    { 16, 1, 0, 0, 0, 0x00, "Chest Game",{-1, -1, -1, -1}, {-1, -1, -1, -1 }},
};

typedef struct {
    uint8_t idx;
    uint8_t r;
    uint8_t g;
    uint8_t b;
} medal_t;

medal_t medals[] = {
    { 5, 0xC8, 0xC8, 0x00 }, // Light
    { 0, 0x00, 0xFF, 0x00 }, // Forest
    { 1, 0xFF, 0x3C, 0x00 }, // Fire
    { 2, 0x00, 0x64, 0xFF }, // Water
    { 4, 0xC8, 0x32, 0xFF }, // Shadow
    { 3, 0xFF, 0x82, 0x00 }, // Spirit
};

uint8_t reward_rows[] = { 0, 1, 2, 8, 3, 4, 5, 7, 6 };

extern uint32_t CFG_DUNGEON_INFO_MQ_ENABLE;
extern uint32_t CFG_DUNGEON_INFO_MQ_NEED_MAP;
extern uint32_t CFG_DUNGEON_INFO_REWARD_ENABLE;
extern uint32_t CFG_DUNGEON_INFO_REWARD_NEED_COMPASS;
extern uint32_t CFG_DUNGEON_INFO_REWARD_NEED_ALTAR;
extern uint32_t CFG_DUNGEON_INFO_REWARD_SUMMARY_ENABLE;

extern uint8_t SHUFFLE_CHEST_GAME;

extern int8_t CFG_DUNGEON_REWARDS[14];
extern char CFG_DUNGEON_REWARD_AREAS[9][0x17];

extern uint8_t CFG_DUNGEON_INFO_SILVER_RUPEES;

extern extended_savecontext_static_t extended_savectx;
extern silver_rupee_data_t silver_rupee_vars[0x16][2];

void draw_background(z64_disp_buf_t* db, int bg_left, int bg_top, int bg_width, int bg_height) {
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
}

// skip dungeons with no keys or silver rupees
int d_right_dungeon_idx(int i) {
    int dungeon_idx = i + 1; // skip Deku
    if (!CFG_DUNGEON_INFO_SILVER_RUPEES || !CFG_DUNGEON_IS_MQ[DODONGO_ID]) dungeon_idx++; // skip DC
    if (dungeon_idx >= 2) dungeon_idx++; // skip Jabu
    if (dungeon_idx >= 9 && (!CFG_DUNGEON_INFO_SILVER_RUPEES || CFG_DUNGEON_IS_MQ[ICE_ID])) dungeon_idx++; // skip Ice
    return dungeon_idx;
}

// Helper function for drawing numbers to the HUD.
void draw_int(z64_disp_buf_t* db, uint16_t number, int16_t left, int16_t top, colorRGBA8_t color) {
    uint8_t digits[10];
    uint8_t j = 0;
    // Extract each digit. They are added, in reverse order, to digits[]
    do {
        digits[j] = number % 10;
        number = number / 10;
        j++;
    }
    while (number > 0);
    // This combiner mode makes it look like the rupee count
    gDPSetCombineLERP(db->p++, 0, 0, 0, PRIMITIVE, TEXEL0, 0, PRIMITIVE, 0, 0, 0, 0, PRIMITIVE,
        TEXEL0, 0, PRIMITIVE, 0);

    // Set the color
    gDPSetPrimColor(db->p++, 0, 0, color.r, color.g, color.b, color.a);
    // Draw each digit
    for (uint8_t c = j; c > 0; c--) {
        sprite_texture(db, &rupee_digit_sprite, digits[c-1], left, top, 8, 16);
        left += 8;
    }
}

// When in a silver rupee room, draw the silver rupee count for that room.
void draw_silver_rupee_count(z64_game_t* globalCtx, z64_disp_buf_t* db) {
    if (!CFG_DUNGEON_INFO_SILVER_RUPEES) return;

    uint8_t scene = globalCtx->scene_index;
    uint8_t room = globalCtx->room_index;

    for (int i = 0; i < dungeon_count; i++) {
        if (scene != dungeons[i].index) continue;

        dungeon_entry_t dungeon = dungeons[i];
        uint8_t* silver_rupee_puzzles = CFG_DUNGEON_IS_MQ[dungeon.index] ? dungeon.silver_rupee_puzzles_mq : dungeon.silver_rupee_puzzles_vanilla;
        for (int puzzle_idx = 0; puzzle_idx < 4; puzzle_idx++) {
            if (silver_rupee_puzzles[puzzle_idx] == (uint8_t) -1) break;
            silver_rupee_data_t silver_rupee_info = silver_rupee_vars[silver_rupee_puzzles[puzzle_idx]][CFG_DUNGEON_IS_MQ[dungeon.index]];
            if (silver_rupee_info.room == room) {
                // Draw silver rupee icon
                int scene_index = z64_game.scene_index;
                int voffset = 0;
                if (scene_index < 0x11 && z64_file.dungeon_keys[scene_index] >= 0) {
                    voffset -= 17;
                }
                gDPPipeSync(db->p++);
                gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
                gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, globalCtx->hud_alpha_channels.rupees_keys_magic);
                gDPPipeSync(db->p++);
                sprite_texture(db, &key_rupee_clock_sprite, 1, 26, 189 + voffset, 16, 16);

                uint8_t count = extended_savectx.silver_rupee_counts[silver_rupee_puzzles[puzzle_idx]];
                // Draw silver rupee count
                gDPPipeSync(db->p++);

                // Draw the count white if we have less than the required amount
                colorRGBA8_t color = { 0xFF, 0xFF, 0xFF, globalCtx->hud_alpha_channels.rupees_keys_magic};

                // Draw the count green (same color as max rupees) if we have the required amount
                if (count >= silver_rupee_info.needed_count) {
                    color.r = 120;
                    color.g = 255;
                    color.b = 0;
                }
                draw_int(db, count, 42, 189 + voffset, color);

                break;
            }
        }
    }
}

void draw_dungeon_info(z64_disp_buf_t* db) {
    pad_t pad_held = z64_ctxt.input[0].raw.pad;
    int draw = CAN_DRAW_DUNGEON_INFO && !CAN_DRAW_TRADE_DPAD && (
        ((pad_held.dl || pad_held.dr || pad_held.dd) && CFG_DPAD_DUNGEON_INFO_ENABLE) ||
        ((pad_held.dl || pad_held.dr || pad_held.dd) && !CFG_DPAD_DUNGEON_INFO_ENABLE && pad_held.a) ||
        pad_held.a);
    if (!draw) {
        return;
    }

    db->p = db->buf;

    // Call setup display list
    gSPDisplayList(db->p++, &setup_db);

    if (pad_held.a && !((pad_held.dl || pad_held.dr || pad_held.dd) && !CFG_DPAD_DUNGEON_INFO_ENABLE)) {
        uint16_t altar_flags = z64_file.inf_table[27];
        int show_medals = CFG_DUNGEON_INFO_REWARD_ENABLE && (!CFG_DUNGEON_INFO_REWARD_NEED_ALTAR || (altar_flags & 1)) && CFG_DUNGEON_INFO_REWARD_SUMMARY_ENABLE;
        int show_stones = CFG_DUNGEON_INFO_REWARD_ENABLE && (!CFG_DUNGEON_INFO_REWARD_NEED_ALTAR || (altar_flags & 2)) && CFG_DUNGEON_INFO_REWARD_SUMMARY_ENABLE;
        int show_keys = 1;
        int show_map_compass = 1;
        int show_skulls = 1;
        int show_mq = CFG_DUNGEON_INFO_MQ_ENABLE;
        int non_chest_game_dungeon_count = 13;

        // Set up dimensions

        int icon_size = 12;
        int font_width = 6;
        int font_height = 11;
        int padding = 1;
        int rows = SHUFFLE_CHEST_GAME == 1 ? 14 : 13;
        int mq_width = show_mq ?
            ((6 * font_width) + padding) :
            0;
        int silver_width = CFG_DUNGEON_INFO_SILVER_RUPEES ?
            icon_size + (7 * font_width) + (12 * padding) :
            0;
        int bg_width =
            (6 * icon_size) +
            ((SHUFFLE_CHEST_GAME == 1 ? 14 : 11) * font_width) +
            (8 * padding) +
            mq_width +
            silver_width;
        int bg_height = (rows * icon_size) + ((rows + 1) * padding);
        int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
        int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

        int left = bg_left + padding;
        int start_top = bg_top + padding;

        // Draw background

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

        // Draw medals

        if (show_medals) {
            sprite_load(db, &medals_sprite, 0, medals_sprite.tile_count);

            for (int i = 0; i < non_chest_game_dungeon_count; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                if (CFG_DUNGEON_INFO_REWARD_NEED_COMPASS && !z64_file.dungeon_items[d->index].compass) {
                    continue;
                }
                int reward = CFG_DUNGEON_REWARDS[d->index];
                if (reward < 3) continue;
                reward -= 3;

                // Medal color index was changed to hint order,
                // moving Light from the end to the beginning.
                // Spirit/Shadow are also swapped.
                int reward_index;
                if (reward < 3) {
                    reward_index = reward + 1;
                } else if (reward == 3) {
                    reward_index = 5;
                } else if (reward == 4) {
                    reward_index = 4;
                } else if (reward == 5) {
                    reward_index = 0;
                }
                medal_t* c = &(medals[reward_index]);
                gDPSetPrimColor(db->p++, 0, 0, c->r, c->g, c->b, 0xFF);

                int top = start_top + ((icon_size + padding) * i);
                sprite_draw(db, &medals_sprite, reward,
                        left, top, icon_size, icon_size);
            }
        }

        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

        // Draw stones

        if (show_stones) {
            sprite_load(db, &stones_sprite, 0, stones_sprite.tile_count);

            for (int i = 0; i < non_chest_game_dungeon_count; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                if (CFG_DUNGEON_INFO_REWARD_NEED_COMPASS && !z64_file.dungeon_items[d->index].compass) {
                    continue;
                }
                int reward = CFG_DUNGEON_REWARDS[d->index];
                if (reward < 0 || reward >= 3) continue;

                int top = start_top + ((icon_size + padding) * i);
                sprite_draw(db, &stones_sprite, reward,
                        left, top, icon_size, icon_size);
            }
        }

        left += icon_size + padding;

        // Draw dungeon names

        for (int i = 0; i < rows; i++) {
            dungeon_entry_t* d = &(dungeons[i]);
            int top = start_top + ((icon_size + padding) * i) + 1;
            text_print_size(d->name, left, top, font_width);
        }
        text_flush_size(db, font_width, font_height, 0, 0);

        left += ((SHUFFLE_CHEST_GAME == 1 ? 11 : 8) * font_width) + padding;

        // Draw keys

        if (show_keys) {
            // Draw small key counts
            sprite_load(db, &quest_items_sprite, 17, 1);

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                if (!d->has_keys) continue;

                int8_t current_keys = z64_file.dungeon_keys[d->index];
                if (current_keys < 0) current_keys = 0;
                if (current_keys > 9) current_keys = 9;

                int8_t total_keys = z64_file.scene_flags[d->index].unk_00_ >> 0x10;
                if (total_keys < 0) total_keys = 0;
                if (total_keys > 9) total_keys = 9;

                char count[5] = "O(O)";
                if (current_keys > 0) count[0] = current_keys + '0';
                if (total_keys > 0) count[2] = total_keys + '0';
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print_size(count, left, top, font_width);
            }
            text_flush_size(db, font_width, font_height, 0, 0);

            left += (4 * font_width) + padding;

            // Draw boss keys

            sprite_load(db, &quest_items_sprite, 14, 1);

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                // Replace index 13 (Ganon's Castle) with 10 (Ganon's Tower)
                int index = d->index == 13 ? 10 : d->index;

                if (d->has_boss_key && z64_file.dungeon_items[index].boss_key) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            // Draw gerudo card

            sprite_load(db, &quest_items_sprite, 10, 1);

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                if (d->has_card && z64_file.gerudos_card) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        // Draw maps and compasses

        if (show_map_compass) {
            // Draw maps

            sprite_load(db, &quest_items_sprite, 16, 1);

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                if (d->has_map && z64_file.dungeon_items[d->index].map) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;

            // Draw compasses

            sprite_load(db, &quest_items_sprite, 15, 1);

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                if (d->has_map && z64_file.dungeon_items[d->index].compass) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        if (show_skulls) {
            // Draw skulltula icon

            sprite_load(db, &quest_items_sprite, 11, 1);

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                if (d->skulltulas && z64_file.gs_flags[d->index ^ 0x03] == d->skulltulas) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        // Draw master quest dungeons

        if (show_mq) {
            for (int i = 0; i < non_chest_game_dungeon_count; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                if (CFG_DUNGEON_INFO_MQ_NEED_MAP && d->has_map &&
                        !z64_file.dungeon_items[d->index].map) {
                    continue;
                }
                char* str = CFG_DUNGEON_IS_MQ[d->index] ? "MQ" : "Normal";
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print_size(str, left, top, font_width);
            }

            left += (6 * font_width) + padding;
        }
        text_flush_size(db, font_width, font_height, 0, 0);

        if (CFG_DUNGEON_INFO_SILVER_RUPEES) {
            // Draw silver rupee icons

            sprite_load(db, &key_rupee_clock_sprite, 1, 1);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                bool show_silver_rupees = false;
                uint8_t* silver_rupee_puzzles = CFG_DUNGEON_IS_MQ[d->index] ? d->silver_rupee_puzzles_mq : d->silver_rupee_puzzles_vanilla;
                for (int puzzle_idx = 0; puzzle_idx < 4; puzzle_idx++) {
                    if (silver_rupee_puzzles[puzzle_idx] == (uint8_t) -1) break;
                    uint8_t count = extended_savectx.silver_rupee_counts[silver_rupee_puzzles[puzzle_idx]];
                    if (count > 0) {
                        show_silver_rupees = true;
                        break;
                    }
                }
                if (show_silver_rupees) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &key_rupee_clock_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;

            // Draw silver rupee counts
            sprite_load(db, &font_sprite, 16, 10); // load characters 0 through 9

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t* d = &(dungeons[i]);
                bool show_silver_rupees = false;
                uint8_t* silver_rupee_puzzles = CFG_DUNGEON_IS_MQ[d->index] ? d->silver_rupee_puzzles_mq : d->silver_rupee_puzzles_vanilla;
                for (int puzzle_idx = 0; puzzle_idx < 4; puzzle_idx++) {
                    if (silver_rupee_puzzles[puzzle_idx] == (uint8_t) -1) break;
                    uint8_t rupee_count = extended_savectx.silver_rupee_counts[silver_rupee_puzzles[puzzle_idx]];
                    if (rupee_count > 0) {
                        show_silver_rupees = true;
                        break;
                    }
                }
                if (show_silver_rupees) {
                    int top = start_top + ((icon_size + padding) * i) + 1;
                    for (int puzzle_idx = 0; puzzle_idx < 4; puzzle_idx++) {
                        if (silver_rupee_puzzles[puzzle_idx] == (uint8_t) -1) break;
                        silver_rupee_data_t var = silver_rupee_vars[silver_rupee_puzzles[puzzle_idx]][CFG_DUNGEON_IS_MQ[d->index]];
                        uint8_t rupee_count = extended_savectx.silver_rupee_counts[silver_rupee_puzzles[puzzle_idx]];
                        int puzzle_left = left + font_width * (2 * puzzle_idx) + padding * 3 * puzzle_idx;
                        // draw text manually instead of going through text_print/text_flush to get the right text colors
                        gDPSetPrimColor(db->p++, 0, 0, var.r, var.g, var.b, 0xFF);
                        if(rupee_count >= 10) {
                            sprite_draw(db, &font_sprite, rupee_count / 10, puzzle_left, top, font_width, font_height);
                        }
                        int tile_index = rupee_count % 10 > 0 ? rupee_count % 10 : 0;
                        if (tile_index == 0) {
                            sprite_load(db, &font_sprite, 47, 1); // load letter O
                        }
                        sprite_draw(db, &font_sprite, tile_index, puzzle_left + font_width, top, font_width, font_height);
                        if (tile_index == 0) {
                            sprite_load(db, &font_sprite, 16, 10); // load numbers 0 through 9
                        }
                    }
                }
            }

            gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
        }

        // Finish

    } else if (pad_held.dd) {
        uint16_t altar_flags = z64_file.inf_table[27];
        int show_medals = CFG_DUNGEON_INFO_REWARD_ENABLE && (!CFG_DUNGEON_INFO_REWARD_NEED_ALTAR || (altar_flags & 1));
        int show_stones = CFG_DUNGEON_INFO_REWARD_ENABLE && (!CFG_DUNGEON_INFO_REWARD_NEED_ALTAR || (altar_flags & 2));

        // Set up dimensions

        int icon_size = 16;
        int padding = 1;
        int rows = 9;
        int bg_width =
            (1 * icon_size) +
            (0x16 * font_sprite.tile_w) +
            (3 * padding);
        int bg_height = (rows * icon_size) + ((rows + 1) * padding);
        int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
        int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

        int left = bg_left + padding;
        int start_top = bg_top + padding;

        draw_background(db, bg_left, bg_top, bg_width, bg_height);

        // Draw medals

        sprite_load(db, &medals_sprite, 0, medals_sprite.tile_count);

        for (int i = 3; i < 9; i++) {
            medal_t* medal = &(medals[i - 3]);
            gDPSetPrimColor(db->p++, 0, 0, medal->r, medal->g, medal->b, 0xFF);

            int top = start_top + ((icon_size + padding) * i);
            sprite_draw(db, &medals_sprite, medal->idx,
                    left, top, icon_size, icon_size);
        }

        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

        // Draw stones

        sprite_load(db, &stones_sprite, 0, stones_sprite.tile_count);

        for (int i = 0; i < 3; i++) {
            int top = start_top + ((icon_size + padding) * i);
            sprite_draw(db, &stones_sprite, i,
                    left, top, icon_size, icon_size);
        }

        left += icon_size + padding;

        // Draw dungeon names

        for (int i = 0; i < 9; i++) {
            if (i < 3 ? show_stones : show_medals) {
                uint8_t reward = reward_rows[i];
                bool display_area = true;
                switch (CFG_DUNGEON_INFO_REWARD_NEED_COMPASS) {
                    case 1:
                        for (int j = 0; j < 8; j++) {
                            uint8_t dungeon_idx = dungeons[j].index;
                            if (CFG_DUNGEON_REWARDS[dungeon_idx] == reward) {
                                if (!z64_file.dungeon_items[dungeon_idx].compass) {
                                    display_area = false;
                                }
                                break;
                            }
                        }
                        break;
                    case 2:
                        if (i != 3) { // always display Light Medallion
                            dungeon_entry_t* d = &(dungeons[i - (i < 3 ? 0 : 1)]); // vanilla location of the reward
                            display_area = z64_file.dungeon_items[d->index].compass;
                        }
                        break;
                }
                if (!display_area) {
                    continue;
                }
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print(CFG_DUNGEON_REWARD_AREAS[i], left, top);
            }
        }

        left += (0x16 * font_sprite.tile_w) + padding;
    } else if (pad_held.dr) {
        // Set up dimensions

        int icon_size = 16;
        int padding = 1;
        int rows = SHUFFLE_CHEST_GAME == 1 ? 10 : 9;
        int bg_width =
            (1 * icon_size) +
            ((SHUFFLE_CHEST_GAME ? 15 : 12) * font_sprite.tile_w) +
            (4 * padding);
        if (CFG_DUNGEON_INFO_SILVER_RUPEES) {
            bg_width += icon_size + (8 * font_sprite.tile_w) + (16 * padding);
            if (CFG_DUNGEON_IS_MQ[DODONGO_ID]) rows++;
            if (!CFG_DUNGEON_IS_MQ[ICE_ID]) rows++;
        }
        int bg_height = (rows * icon_size) + ((rows + 1) * padding);
        int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
        int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

        int left = bg_left + padding;
        int start_top = bg_top + padding;

        draw_background(db, bg_left, bg_top, bg_width, bg_height);
        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

        // Draw dungeon names

        for (int i = 0; i < rows; i++) {
            dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice dynamically
            int top = start_top + ((icon_size + padding) * i) + 1;
            text_print(d->name, left, top);
        }

        left += ((SHUFFLE_CHEST_GAME == 1 ? 11 : 8) * font_sprite.tile_w) + padding;

        // Draw keys

        // Draw small key counts

        sprite_load(db, &quest_items_sprite, 17, 1);

        for (int i = 0; i < rows; i++) {
            dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice dynamically
            if (!d->has_keys) continue;

            int8_t current_keys = z64_file.dungeon_keys[d->index];
            if (current_keys < 0) current_keys = 0;
            if (current_keys > 9) current_keys = 9;

            int8_t total_keys = z64_file.scene_flags[d->index].unk_00_ >> 0x10;
            if (total_keys < 0) total_keys = 0;
            if (total_keys > 9) total_keys = 9;

            char count[5] = "O(O)";
            if (current_keys > 0) count[0] = current_keys + '0';
            if (total_keys > 0) count[2] = total_keys + '0';
            int top = start_top + ((icon_size + padding) * i) + 1;
            text_print(count, left, top);
        }

        left += (4 * font_sprite.tile_w) + padding;

        // Draw boss keys

        sprite_load(db, &quest_items_sprite, 14, 1);

        for (int i = 0; i < rows; i++) {
            dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice dynamically
            // Replace index 13 (Ganon's Castle) with 10 (Ganon's Tower)
            int index = d->index == 13 ? 10 : d->index;

            if (d->has_boss_key && z64_file.dungeon_items[index].boss_key) {
                int top = start_top + ((icon_size + padding) * i);
                sprite_draw(db, &quest_items_sprite, 0,
                        left, top, icon_size, icon_size);
            }
        }

        // Draw Gerudo card

        sprite_load(db, &quest_items_sprite, 10, 1);

        for (int i = 0; i < rows; i++) {
            dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice dynamically
            if (d->has_card && z64_file.gerudos_card) {
                int top = start_top + ((icon_size + padding) * i);
                sprite_draw(db, &quest_items_sprite, 0,
                        left, top, icon_size, icon_size);
            }
        }

        left += icon_size + padding;

        if (CFG_DUNGEON_INFO_SILVER_RUPEES) {
            // Draw silver rupee icons

            sprite_load(db, &key_rupee_clock_sprite, 1, 1);

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice dynamically
                bool show_silver_rupees = false;
                uint8_t* silver_rupee_puzzles = CFG_DUNGEON_IS_MQ[d->index] ? d->silver_rupee_puzzles_mq : d->silver_rupee_puzzles_vanilla;
                for (int puzzle_idx = 0; puzzle_idx < 4; puzzle_idx++) {
                    if (silver_rupee_puzzles[puzzle_idx] == (uint8_t) -1) break;
                    uint8_t count = extended_savectx.silver_rupee_counts[silver_rupee_puzzles[puzzle_idx]];
                    if (count > 0) {
                        show_silver_rupees = true;
                        break;
                    }
                }
                if (show_silver_rupees) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &key_rupee_clock_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;

            // Draw silver rupee counts
            sprite_load(db, &font_sprite, 16, 10); // load characters 0 through 9

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]);
                bool show_silver_rupees = false;
                uint8_t* silver_rupee_puzzles = CFG_DUNGEON_IS_MQ[d->index] ? d->silver_rupee_puzzles_mq : d->silver_rupee_puzzles_vanilla;
                for (int puzzle_idx = 0; puzzle_idx < 4; puzzle_idx++) {
                    if (silver_rupee_puzzles[puzzle_idx] == (uint8_t) -1) break;
                    uint8_t count = extended_savectx.silver_rupee_counts[silver_rupee_puzzles[puzzle_idx]];
                    if (count > 0) {
                        show_silver_rupees = true;
                        break;
                    }
                }
                if (show_silver_rupees) {
                    int top = start_top + ((icon_size + padding) * i) + 1;
                    for (int puzzle_idx = 0; puzzle_idx < 4; puzzle_idx++) {
                        if (silver_rupee_puzzles[puzzle_idx] == (uint8_t) -1) break;
                        silver_rupee_data_t var = silver_rupee_vars[silver_rupee_puzzles[puzzle_idx]][CFG_DUNGEON_IS_MQ[d->index]];
                        uint8_t count = extended_savectx.silver_rupee_counts[silver_rupee_puzzles[puzzle_idx]];
                        int puzzle_left = left + font_sprite.tile_w * (2 * puzzle_idx) + padding * 4 * puzzle_idx;
                        // draw text manually instead of going through text_print/text_flush to get the right text colors
                        gDPSetPrimColor(db->p++, 0, 0, var.r, var.g, var.b, 0xFF);
                        if(count >= 10) {
                            sprite_draw(db, &font_sprite, count / 10, puzzle_left, top, font_sprite.tile_w, font_sprite.tile_h);
                        }
                        int tile_index = count % 10;
                        if (tile_index == 0) {
                            sprite_load(db, &font_sprite, 47, 1); // load letter O
                        }
                        sprite_draw(db, &font_sprite, tile_index, puzzle_left + font_sprite.tile_w, top, font_sprite.tile_w, font_sprite.tile_h);
                        if (tile_index == 0) {
                            sprite_load(db, &font_sprite, 16, 10); // load numbers 0 through 9
                        }
                    }
                }
            }

            gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
        }
    } else { // pad_held.dl
        int show_map_compass = 1;
        int show_skulls = 1;
        int show_mq = CFG_DUNGEON_INFO_MQ_ENABLE;

        // Set up dimensions

        int icon_size = 16;
        int padding = 1;
        int rows = 12;
        int mq_width = show_mq ?
            ((6 * font_sprite.tile_w) + padding) :
            0;
        int bg_width =
            (3 * icon_size) +
            (8 * font_sprite.tile_w) +
            (8 * padding) +
            mq_width;
        int bg_height = (rows * icon_size) + ((rows + 1) * padding);
        int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
        int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

        int left = bg_left + padding;
        int start_top = bg_top + padding;

        draw_background(db, bg_left, bg_top, bg_width, bg_height);
        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

        // Draw dungeon names

        for (int i = 0; i < 12; i++) {
            dungeon_entry_t* d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
            int top = start_top + ((icon_size + padding) * i) + 1;
            text_print(d->name, left, top);
        }

        left += (8 * font_sprite.tile_w) + padding;

        // Draw maps and compasses

        if (show_map_compass) {
            // Draw maps

            sprite_load(db, &quest_items_sprite, 16, 1);

            for (int i = 0; i < 12; i++) {
                dungeon_entry_t* d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
                if (d->has_map && z64_file.dungeon_items[d->index].map) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;

            // Draw compasses

            sprite_load(db, &quest_items_sprite, 15, 1);

            for (int i = 0; i < 12; i++) {
                dungeon_entry_t* d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
                if (d->has_map && z64_file.dungeon_items[d->index].compass) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        if (show_skulls) {
            // Draw skulltula icon

            sprite_load(db, &quest_items_sprite, 11, 1);

            for (int i = 0; i < 12; i++) {
                dungeon_entry_t* d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
                if (d->skulltulas && z64_file.gs_flags[d->index ^ 0x03] == d->skulltulas) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        // Draw master quest dungeons

        if (show_mq) {
            for (int i = 0; i < 12; i++) {
                dungeon_entry_t* d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
                if (CFG_DUNGEON_INFO_MQ_NEED_MAP && d->has_map &&
                        !z64_file.dungeon_items[d->index].map) {
                    continue;
                }
                char* str = CFG_DUNGEON_IS_MQ[d->index] ? "MQ" : "Normal";
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print(str, left, top);
            }

            left += icon_size + padding;
        }
    }

    // Finish
    text_flush(db);
}
