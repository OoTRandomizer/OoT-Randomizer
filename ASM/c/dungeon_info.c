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
    {  0, 0, 0, 0, 1, 0x0F, "Deku",       "Deku Tree",          {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    {  1, 0, 0, 0, 1, 0x1F, "Dodongo",    "Dodongo's Cavern",   {-1, -1, -1, -1}, { 0, -1, -1, -1} },
    {  2, 0, 0, 0, 1, 0x0F, "Jabu",       "Jabu Jabu's Belly",  {-1, -1, -1, -1}, {-1, -1, -1, -1} },

    {  3, 1, 1, 0, 1, 0x1F, "Forest",     "Forest Temple",      {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    {  4, 1, 1, 0, 1, 0x1F, "Fire",       "Fire Temple",        {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    {  5, 1, 1, 0, 1, 0x1F, "Water",      "Water Temple",       {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    {  7, 1, 1, 0, 1, 0x1F, "Shadow",     "Shadow Temple",      { 4,  6,  7, -1}, { 4,  5,  6,  7} },
    {  6, 1, 1, 0, 1, 0x1F, "Spirit",     "Spirit Temple",      {11, 14, 12, -1}, {13, 15, -1, -1} },

    {  8, 1, 0, 0, 1, 0x07, "BotW",       "Bottom of the Well", { 3, -1, -1, -1}, {-1, -1, -1, -1} },
    {  9, 0, 0, 0, 1, 0x07, "Ice",        "Ice Cavern",         { 1,  2, -1, -1}, {-1, -1, -1, -1} },
    { 12, 1, 0, 1, 0, 0x00, "Hideout",    "Thieves' Hideout",   {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    { 11, 1, 0, 0, 0, 0x00, "GTG",        "GTG",                { 8,  9, 10, -1}, { 8,  9, 10, -1} },
    { 10, 0, 0, 0, 0, 0x00, "Tower",      "Ganon's Tower",      {-1, -1, -1, -1}, {-1, -1, -1, -1} },
    { 13, 1, 1, 0, 0, 0x00, "Ganon",      "Ganon's Castle",     {16, 17, 18, 21}, {18, 19, 20, -1} },
    { 16, 1, 0, 0, 0, 0x00, "Chest Game", "Treasure Box Shop",  {-1, -1, -1, -1}, {-1, -1, -1, -1} },
};

boss_entry_t bosses[] = {
    {  0, 1, "Gohma"},
    {  1, 1, "KD"},
    {  2, 1, "Bari"},
    {  3, 1, "PG"},
    {  4, 1, "Volv"},
    {  5, 1, "Morpha"},
    {  7, 1, "Bongo"},
    {  6, 1, "Twin"},
    { 13, 0, "Ganon"}
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
uint8_t bk_display = 0;
bool world_display = false;
bool boss_display = false;

extern uint32_t CFG_DUNGEON_INFO_MQ_ENABLE;
extern uint32_t CFG_DUNGEON_INFO_MQ_NEED_MAP;
extern uint32_t CFG_DUNGEON_INFO_REWARD_ENABLE;
extern uint32_t CFG_DUNGEON_INFO_REWARD_NEED_COMPASS;
extern uint32_t CFG_DUNGEON_INFO_REWARD_NEED_ALTAR;
extern uint32_t CFG_DUNGEON_INFO_REWARD_SUMMARY_ENABLE;
extern bool CFG_DUNGEON_INFO_REWARD_WORLDS_ENABLE;

extern uint8_t SHUFFLE_CHEST_GAME;

extern int8_t CFG_DUNGEON_REWARDS[14];
extern char CFG_DUNGEON_REWARD_AREAS[9][0x17];
extern uint8_t CFG_DUNGEON_REWARD_WORLDS[9];

extern uint8_t CFG_DUNGEON_INFO_SILVER_RUPEES;

extern int8_t CFG_DUNGEON_PRECOMPLETED[14];

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
    if (dungeon_idx > 11) dungeon_idx++; // skip Tower
    return dungeon_idx;
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
                if (scene_index < 0x11 && (z64_file.dungeon_keys[scene_index] >= 0 || bk_display)) {
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
void is_bk_displayed() {
    uint8_t scene = z64_game.scene_index;
    if ((scene > 2 && scene < 8) || // Adult temples
        scene == 10 || // Ganon's Tower
        scene == 13) { // Ganon's Castle

        int index = scene == 13 ? 10 : scene;
        if (z64_file.dungeon_items[index].boss_key) {
            bk_display++;
            bk_display = bk_display > 1 ? 2 : bk_display;
            return;
        }
    }
    bk_display = 0;
}

// Draw a boss key icon in dungeons.
void draw_boss_key(z64_game_t* globalCtx, z64_disp_buf_t* db) {
    is_bk_displayed();
    if (bk_display > 1) { // Delay by one frame to let other counters move first.
        gDPPipeSync(db->p++);
        gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, globalCtx->hud_alpha_channels.rupees_keys_magic);
        gDPPipeSync(db->p++);
        sprite_load(db, &quest_items_sprite, 14, 1);
        sprite_draw(db, &quest_items_sprite, 0, 26, 190, 16, 16);
    }
}

void draw_world_info(z64_disp_buf_t* db) {
    if (!CAN_DRAW_WORLD_INFO) {
        return;
    }
    show_dungeon_info = 0;
    bool show_dungeons = CFG_DUNGEON_BOSS_INFO[0] > 0;
    bool show_bosses = CFG_DUNGEON_BOSS_INFO[1] > 0;
    // If neither setting is on, don't display this menu at all.
    if (!show_dungeons && !show_bosses) {
        return;
    }

    bool mixed_dungeons = CFG_DUNGEON_BOSS_INFO[0] > 1;
    bool mixed_bosses = CFG_DUNGEON_BOSS_INFO[1] > 1;
    bool mixed = mixed_dungeons || mixed_bosses;

    db->p = db->buf;

    // Call setup display list
    gSPDisplayList(db->p++, &setup_db);

    if (!mixed) {

        if ((z64_ctxt.input[0].pad_pressed.dl || z64_ctxt.input[0].pad_pressed.a) && show_dungeons) {
            world_display = world_display ? false : true;
            boss_display = false;
        }
        if (z64_ctxt.input[0].pad_pressed.dr && show_bosses) {
            boss_display = boss_display ? false : true;
            world_display = false;
        }

        if (world_display) {
            show_dungeon_info = 1;

            // Set up dimensions
            int font_width = 6;
            int font_height = 11;
            int padding = 1;
            int rows = 13;
            int boss_width = show_bosses ?
                ((8 * font_width) + padding) :
                0;
            int bg_width = show_dungeons ?
                10 * 2 * font_width + boss_width :
                10 * font_width + boss_width;
            int bg_height = (rows * font_height) + ((rows + 1) * padding);
            int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
            int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

            int start_top = bg_top + padding + 1;
            uint16_t left = bg_left + padding;
            uint16_t left_dungeon = 0;
            if (show_dungeons) {
                left_dungeon = left + 60;
            }
            uint16_t left_boss = show_dungeons ? left + 2*60 : left + 60;

            // Draw background
            gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
            for (int i = 0; i < rows; i++) {
                uint16_t line_top = bg_top + i * (font_height + padding) + padding;
                gDPPipeSync(db->p++);
                if (i % 2) {
                    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xD0);
                }
                else {
                    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xDA);
                }
                gSPTextureRectangle(db->p++,
                    bg_left<<2, line_top<<2,
                    (bg_left + bg_width)<<2, (line_top + font_height + padding)<<2,
                    0,
                    0, 0,
                    1<<10, 1<<10);
            }

            gDPPipeSync(db->p++);
            gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
            gDPSetPrimColor(db->p++, 0, 0, 120, 255, 100, 0xFF);

            // Draw the legend at the top.
            text_print_size(db, "Entrance", left, start_top, font_width, font_height);
            if (show_dungeons) {
                text_print_size(db, "Dungeon", left_dungeon, start_top, font_width, font_height);
            }
            if (show_bosses) {
                text_print_size(db, "Boss", left_boss, start_top, font_width, font_height);
            }
            gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
            // Draw the list of dungeons entrances.
            uint16_t top = start_top;
            for (uint8_t i = 0; i < rows; i++) {
                // Skip Hideout for this menu.
                if (i == 10) {
                    continue;
                }
                gDPPipeSync(db->p++);
                dungeon_entry_t dungeon = i == 12 ? dungeons[i + 1] : dungeons[i];
                top += font_height + padding;
                text_print_size(db, dungeon.short_name, left, top, font_width, font_height);
            }

            // Draw the list of dungeons interiors.
            if (show_dungeons) {
                for (uint8_t i = 0; i < rows - 1; i++) {
                    uint16_t top = start_top + ((font_height + padding) * (i + 1)) + 1;
                    if (CFG_DUNGEON_BOSS_INFO[i + 2] > 10 || z64_file.dungeon_items[CFG_DUNGEON_BOSS_INFO[i + 2]].map) {
                        gDPPipeSync(db->p++);
                        text_print_size(db, CFG_DUNGEON_ENTRANCES[i], left_dungeon, top, font_width, font_height);
                        // If boss ER is also on, display the boss on the same line as the actual dungeon.
                        if (show_bosses) {
                            if (CFG_DUNGEON_BOSS_INFO[i + 2] > 10 || z64_file.dungeon_items[CFG_DUNGEON_BOSS_INFO[i + 2]].compass) {
                                gDPPipeSync(db->p++);
                                text_print_size(db, CFG_BOSSES[i], left_boss, top, font_width, font_height);
                            }
                        }
                    }
                }
            }
        }
        if (boss_display) {
            show_dungeon_info = 1;

            // Set up dimensions
            int font_width = 6;
            int font_height = 11;
            int padding = 1;
            int rows = 10;
            int bg_width = 10 * 2 * font_width;
            int bg_height = (rows * font_height) + ((rows + 1) * padding);
            int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
            int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

            int start_top = bg_top + padding + 1;
            uint16_t left = bg_left + padding;
            uint16_t left_area = left + 60;

            // Draw background
            gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
            for (int i = 0; i < rows; i++) {
                uint16_t line_top = bg_top + i * (font_height + padding) + padding;
                gDPPipeSync(db->p++);
                if (i % 2) {
                    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xD0);
                }
                else {
                    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xDA);
                }
                gSPTextureRectangle(db->p++,
                    bg_left<<2, line_top<<2,
                    (bg_left + bg_width)<<2, (line_top + font_height + padding)<<2,
                    0,
                    0, 0,
                    1<<10, 1<<10);
            }

            gDPPipeSync(db->p++);
            gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
            gDPSetPrimColor(db->p++, 0, 0, 120, 255, 100, 0xFF);

            // Draw the legend at the top.
            text_print_size(db, "Dungeon", left, start_top, font_width, font_height);
            text_print_size(db, "Boss", left_area, start_top, font_width, font_height);
            gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
            // Draw the list of dungeons entrances.
            uint16_t top = start_top;
            for (uint8_t i = 0; i < 13; i++) {
                // Skip BotW/Ice/Hideout/GTG.
                if (i > 7 && i < 12) {
                    continue;
                }
                gDPPipeSync(db->p++);
                dungeon_entry_t dungeon = i == 12 ? dungeons[i + 1] : dungeons[i];
                top += font_height + padding;
                text_print_size(db, dungeon.short_name, left, top, font_width, font_height);
            }
            // List of bosses, located in CFG_BOSSES after the first list of 12 for the dpad left menu.
            for (uint8_t i = 0; i < rows - 1; i++) {
                boss_entry_t boss = bosses[i];
                if (boss.has_map && !z64_file.dungeon_items[boss.index].compass) {
                    continue;
                }
                gDPPipeSync(db->p++);
                uint16_t top = start_top + ((font_height + padding) * (i + 1));
                text_print_size(db, CFG_BOSSES[12 + i], left_area, top, font_width, font_height);
            }
        }
    }
    else { // if mixed dungeons or bosses

        if (z64_ctxt.input[0].pad_pressed.dl) {
            world_display = world_display ? false : true;
            boss_display = false;
        }
        if (z64_ctxt.input[0].pad_pressed.dr) {
            boss_display = boss_display ? false : true;
            world_display = false;
        }

        if (world_display) {
            show_dungeon_info = 1;

            // Set up dimensions
            int font_width = 6;
            int font_height = 11;
            int padding = 1;
            int rows = 13;
            int bg_width = 10 * 2 * font_width;
            int bg_height = (rows * font_height) + ((rows + 1) * padding);
            int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
            int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

            int start_top = bg_top + padding + 1;
            uint16_t left = bg_left + padding;
            uint16_t left_area = left + 60;

            // Draw background
            gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
            for (int i = 0; i < rows; i++) {
                uint16_t line_top = bg_top + i * (font_height + padding) + padding;
                gDPPipeSync(db->p++);
                if (i % 2) {
                    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xD0);
                }
                else {
                    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xDA);
                }
                gSPTextureRectangle(db->p++,
                    bg_left<<2, line_top<<2,
                    (bg_left + bg_width)<<2, (line_top + font_height + padding)<<2,
                    0,
                    0, 0,
                    1<<10, 1<<10);
            }

            gDPPipeSync(db->p++);
            gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
            gDPSetPrimColor(db->p++, 0, 0, 120, 255, 100, 0xFF);

            // Draw the legend at the top.
            text_print_size(db, "Dungeon", left, start_top, font_width, font_height);
            text_print_size(db, "Area", left_area, start_top, font_width, font_height);
            gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
            // Draw the list of dungeons.
            uint16_t top = start_top;
            for (uint8_t i = 0; i < rows; i++) {
                gDPPipeSync(db->p++);
                // Skip Hideout.
                if (i == 10) {
                    continue;
                }
                dungeon_entry_t dungeon = dungeons[i];
                top += font_height + padding;
                text_print_size(db, dungeon.short_name, left, top, font_width, font_height);
            }
            // Draw the area each dungeon is located in.
            for (uint8_t i = 0; i < rows - 1; i++) {
                gDPPipeSync(db->p++);
                dungeon_entry_t dungeon = dungeons[i];
                if (dungeon.has_map && !z64_file.dungeon_items[dungeon.index].map) {
                    continue;
                }
                uint16_t top = start_top + ((font_height + padding) * (i + 1)) + 1;
                text_print_size(db, CFG_DUNGEON_ENTRANCES[i], left_area, top, font_width, font_height);
            }
        }
        if (boss_display) {
            show_dungeon_info = 1;

            // Set up dimensions
            int font_width = 6;
            int font_height = 11;
            int padding = 1;
            int rows = 10;
            int bg_width = 10 * 2 * font_width;
            int bg_height = (rows * font_height) + ((rows + 1) * padding);
            int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
            int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

            int start_top = bg_top + padding + 1;
            uint16_t left = bg_left + padding;
            uint16_t left_area = left + 60;

            // Draw background
            gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
            for (int i = 0; i < rows; i++) {
                uint16_t line_top = bg_top + i * (font_height + padding) + padding;
                gDPPipeSync(db->p++);
                if (i % 2) {
                    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xD0);
                }
                else {
                    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xDA);
                }
                gSPTextureRectangle(db->p++,
                    bg_left<<2, line_top<<2,
                    (bg_left + bg_width)<<2, (line_top + font_height + padding)<<2,
                    0,
                    0, 0,
                    1<<10, 1<<10);
            }

            gDPPipeSync(db->p++);
            gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
            gDPSetPrimColor(db->p++, 0, 0, 120, 255, 100, 0xFF);

            // Draw the legend at the top.
            text_print_size(db, "Boss", left, start_top, font_width, font_height);
            text_print_size(db, "Area", left_area, start_top, font_width, font_height);
            gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
            // Draw the list of bosses.
            uint16_t top = start_top;
            for (uint8_t i = 0; i < rows - 1; i++) {
                gDPPipeSync(db->p++);
                boss_entry_t boss = bosses[i];
                top += font_height + padding;
                text_print_size(db, boss.name, left, top, font_width, font_height);
            }
            // Draw the area each boss is located in.
            for (uint8_t i = 0; i < rows - 1; i++) {
                gDPPipeSync(db->p++);
                boss_entry_t boss = bosses[i];
                if (boss.has_map && !z64_file.dungeon_items[boss.index].compass) {
                    continue;
                }
                uint16_t top = start_top + ((font_height + padding) * (i + 1));
                text_print_size(db, CFG_BOSSES[i], left_area, top, font_width, font_height);
            }
        }
    }
}

void draw_dungeon_info(z64_disp_buf_t* db) {
    show_dungeon_info = 0;
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
        show_dungeon_info = 1;
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

        uint16_t left = bg_left + padding;
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

        // Draw the list of dungeons.
        // Pre completed dungeons are grayed and crossed out.
        for (int i = 0; i < rows; i++) {
            gDPPipeSync(db->p++);
            dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
            bool empty = CFG_DUNGEON_PRECOMPLETED[d->index];
            int top = start_top + ((icon_size + padding) * i) + 1;
            if (empty) {
                gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0x7F);
                uint16_t sizeRectangle = text_print_size(db, d->short_name, left, top, font_width, font_height) - left;
                gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xBF);
                gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
                gSPTextureRectangle(db->p++,
                        left * 4, (top + 5) * 4,
                        (left + sizeRectangle) * 4, ((top + 5) + 1) * 4,
                        0,
                        0, 0,
                        1024, 1024);
                gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
            } else {
                gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
                text_print_size(db, d->short_name, left, top, font_width, font_height);
            }
        }

        left += ((SHUFFLE_CHEST_GAME == 1 ? 11 : 8) * font_width) + padding;

        // Draw keys

        if (show_keys) {
            // Draw small key counts
            sprite_load(db, &quest_items_sprite, 17, 1);

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
                if (!d->has_keys) continue;

                int8_t current_keys = z64_file.dungeon_keys[d->index];
                if (current_keys < 0) current_keys = 0;
                if (current_keys > 9) current_keys = 9;

                int8_t total_keys = z64_file.scene_flags[d->index].unk_00_ >> 0x10;
                if (total_keys < 0) total_keys = 0;
                if (total_keys > 9) total_keys = 9;

                char count[5] = "O(O)"; // we use O instead of 0 because it's easier to distinguish from 8
                if (current_keys > 0) count[0] = current_keys + '0';
                if (total_keys > 0) count[2] = total_keys + '0';
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print_size(db, count, left, top, font_width, font_height);
            }

            left += (4 * font_width) + padding;

            // Draw boss keys

            sprite_load(db, &quest_items_sprite, 14, 1);

            for (int i = 0; i < rows; i++) {
                dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
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
                dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
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
                dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
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
                dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
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
                dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
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
                dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
                if (CFG_DUNGEON_INFO_MQ_NEED_MAP && d->has_map &&
                        !z64_file.dungeon_items[d->index].map) {
                    continue;
                }
                char* str = CFG_DUNGEON_IS_MQ[d->index] ? "MQ" : "Normal";
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print_size(db, str, left, top, font_width, font_height);
            }

            left += (6 * font_width) + padding;
        }

        if (CFG_DUNGEON_INFO_SILVER_RUPEES) {
            // Draw silver rupee icons

            sprite_load(db, &key_rupee_clock_sprite, 1, 1);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
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
                dungeon_entry_t* d = &(dungeons[i + (i > 11 ? 1 : 0)]); // skip Tower
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
        show_dungeon_info = 1;
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
        if (CFG_DUNGEON_INFO_REWARD_WORLDS_ENABLE) {
            bg_width += 5 * font_sprite.tile_w;
        }
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

        // Draw reward world numbers

        if (CFG_DUNGEON_INFO_REWARD_WORLDS_ENABLE) {
            for (int i = 0; i < 9; i++) {
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
                uint8_t world = CFG_DUNGEON_REWARD_WORLDS[i];
                char world_text[5] = "WOOO"; // we use O instead of 0 because it's easier to distinguish from 8
                if (world < 100) {
                    world_text[0] = ' ';
                    world_text[1] = 'W';
                }
                if (world < 10) {
                    world_text[1] = ' ';
                    world_text[2] = 'W';
                }
                if (world / 100) {
                    world_text[1] = world / 100 + '0';
                }
                if ((world % 100) / 10) {
                    world_text[2] = (world % 100) / 10 + '0';
                }
                if (world % 10) {
                    world_text[3] = world % 10 + '0';
                }
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print(db, world_text, left, top);
            }
            left += 5 * font_sprite.tile_w;
        }

        // Draw reward locations

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
                text_print(db, CFG_DUNGEON_REWARD_AREAS[i], left, top);
            }
        }

        left += (0x16 * font_sprite.tile_w) + padding;
    } else if (pad_held.dr) {
        show_dungeon_info = 1;
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
            dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice/Tower dynamically
            int top = start_top + ((icon_size + padding) * i) + 1;
            text_print(db, d->short_name, left, top);
        }

        left += ((SHUFFLE_CHEST_GAME == 1 ? 11 : 8) * font_sprite.tile_w) + padding;

        // Draw keys

        // Draw small key counts

        sprite_load(db, &quest_items_sprite, 17, 1);

        for (int i = 0; i < rows; i++) {
            dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice/Tower dynamically
            if (!d->has_keys) continue;

            int8_t current_keys = z64_file.dungeon_keys[d->index];
            if (current_keys < 0) current_keys = 0;
            if (current_keys > 9) current_keys = 9;

            int8_t total_keys = z64_file.scene_flags[d->index].unk_00_ >> 0x10;
            if (total_keys < 0) total_keys = 0;
            if (total_keys > 9) total_keys = 9;

            char count[5] = "O(O)"; // we use O instead of 0 because it's easier to distinguish from 8
            if (current_keys > 0) count[0] = current_keys + '0';
            if (total_keys > 0) count[2] = total_keys + '0';
            int top = start_top + ((icon_size + padding) * i) + 1;
            text_print(db, count, left, top);
        }

        left += (4 * font_sprite.tile_w) + padding;

        // Draw boss keys

        sprite_load(db, &quest_items_sprite, 14, 1);

        for (int i = 0; i < rows; i++) {
            dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice/Tower dynamically
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
            dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice/Tower dynamically
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
                dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice/Tower dynamically
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
                dungeon_entry_t* d = &(dungeons[d_right_dungeon_idx(i)]); // skip Deku/DC/Jabu/Ice/Tower dynamically
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
        show_dungeon_info = 1;
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

        // Draw dungeon names

        int d_idx = 0;

        for (int i = 0; i < 12; i++) {
            // skip Hideout and Tower
            if (d_idx == 10 || (d_idx == 12)) {
                d_idx++;
            }
            dungeon_entry_t* d = &(dungeons[d_idx]);
            d_idx++;

            bool empty = CFG_DUNGEON_PRECOMPLETED[d->index];
            int top = start_top + ((icon_size + padding) * i) + 1;
            if (empty) {
                gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0x7F);
                uint16_t sizeRectangle = text_print(db, d->short_name, left, top) - left;
                gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xBF);
                gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
                gSPTextureRectangle(db->p++,
                        left * 4, (top + 6) * 4,
                        (left + sizeRectangle) * 4, (top + 6 + 2) * 4,
                        0,
                        0, 0,
                        1024, 1024);
                gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
            } else {
                gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
                text_print(db, d->short_name, left, top);
            }
        }

        left += (8 * font_sprite.tile_w) + padding;

        // Draw maps and compasses

        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
        if (show_map_compass) {
            // Draw maps

            sprite_load(db, &quest_items_sprite, 16, 1);

            d_idx = 0;
            for (int i = 0; i < 12; i++) {
                // skip Hideout and Tower
                if (d_idx == 10 || (d_idx == 12)) {
                    d_idx++;
                }
                dungeon_entry_t* d = &(dungeons[d_idx]);
                d_idx++;

                if (d->has_map && z64_file.dungeon_items[d->index].map) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;

            // Draw compasses

            sprite_load(db, &quest_items_sprite, 15, 1);

            d_idx = 0;
            for (int i = 0; i < 12; i++) {
                // skip Hideout and Tower
                if (d_idx == 10 || (d_idx == 12)) {
                    d_idx++;
                }
                dungeon_entry_t* d = &(dungeons[d_idx]);
                d_idx++;

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

            d_idx = 0;
            for (int i = 0; i < 12; i++) {
                // skip Hideout and Tower
                if (d_idx == 10 || (d_idx == 12)) {
                    d_idx++;
                }
                dungeon_entry_t* d = &(dungeons[d_idx]);
                d_idx++;

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
            d_idx = 0;
            for (int i = 0; i < 12; i++) {
                // skip Hideout and Tower
                if (d_idx == 10 || (d_idx == 12)) {
                    d_idx++;
                }
                dungeon_entry_t* d = &(dungeons[d_idx]);
                d_idx++;

                if (CFG_DUNGEON_INFO_MQ_NEED_MAP && d->has_map &&
                        !z64_file.dungeon_items[d->index].map) {
                    continue;
                }
                char* str = CFG_DUNGEON_IS_MQ[d->index] ? "MQ" : "Normal";
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print(db, str, left, top);
            }

            left += icon_size + padding;
        }
    }

    // Finish
}

int dungeon_info_is_drawn() {
    return show_dungeon_info;
}
