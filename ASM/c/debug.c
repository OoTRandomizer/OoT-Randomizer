#include "debug.h"
#include "objects.h"
#include "item_effects.h"
#include "actor.h"

const int8_t debug_text_width = 16;
const int8_t debug_text_height = 16;
colorRGB8_t debug_text_color = { 0xE0, 0xE0, 0x10 }; // Yellow
int8_t float_precision = 5;
bool show_clock = false;

menu_category_t menu_categories[] = {
    {  0, "Dungeons"},
    {  1, "Overworld"},
    {  2, "Bosses"},
    {  3, "Items"},
    {  4, "Switch Age"},
    {  5, "Bunny Hood"},
    {  6, "Display clock"},
    {  7, "Actor table"},
    {  8, "Overlay table"},
};

warp_t dungeon_warps[] = {
    {  0, 0x00, "Deku"},
    {  1, 0x04, "Dodongo"},
    {  2, 0x28, "Jabu"},
    {  3, 0x169, "Forest"},
    {  4, 0x165, "Fire"},
    {  5, 0x10, "Water"},
    {  6, 0x37, "Shadow"},
    {  7, 0x82, "Spirit"},
    {  8, 0x98, "BotW"},
    {  9, 0x88, "Ice"},
    { 10, 0x486, "Hideout"},
    { 11, 0x08, "GTG"},
    { 12, 0x467, "Ganon Castle"},
};

room_t deku_rooms[6] = {
    {  0x0, 0, { -4, 0, 554 }, 32768, "Entrance"},
    {  0x0, 2, { -1002, 400, 1000 }, 57436, "Slingshot room"},
    {  0x0, 10, { -651, 800, -1 }, 49050, "Compass room"},
    {  0x0, 3, { -198, -845, -285 }, 48980, "Basement"},
    {  0x0, 5, { -428, -880, 961 }, 49050, "Log Spike"},
    {  0x0, 9, { -614, -1881, -388 }, 34300, "231 Scrubs"},
};

room_t dc_rooms[] = {
    {  0x04, 0, { -3, 0, 369 }, 32768, "Entrance"},
    {  0x04, 2, { -927, 0, -1525 }, 49050, "Bomb Flower Staircase"},
    {  0x04, 9, { 1392, 531, -316 }, 16384, "Bomb Bag room"},
    {  0x04, 7, { 7, 76, -2057 }, 32768, "Floor switch room before Boss"},
};

room_t jabu_rooms[] = {
    {  0x28, 0, { -3, -226, 369 }, 32768, "Entrance"},
    {  0x28, 3, { 231, -1113, -3228}, 29920, "B1 Main"},
    {  0x28, 7, { 6, -340, -4074 }, 32666, "Branching Hallways"},
};

room_t forest_rooms[] = {
    {  0x169, 0, { 110, 309, 641 }, 32768, "Entrance"},
    {  0x169, 2, { 118, 383, -660 }, 32768, "Main Chamber"},
    {  0x169, 11, { -1447, 383, -1439 }, 49152, "Block Puzzle room"},
    {  0x169, 12, { -1328, 1228, -3326 }, 16282, "Red Poe"},
    {  0x169, 13, { 586, 827, -3322 }, 16282, "Blue Poe"},
    {  0x169, 15, { 1979, 403, -3404 }, 16282, "Checkerboard Ceiling"},
};

room_t fire_rooms[] = {
    {  0x165, 0, { 5, 0, 846 }, 32768, "Entrance"},
    {  0x165, 4, { 2989, 2060, 0 }, 49152, "Shortcut room"},
    {  0x165, 5, { 2660, 2800, 0 }, 16384, "Boulder maze (down)"},
    {  0x165, 5, { 1540, 2940, -630 }, 16384, "Boulder maze (up)"},
    {  0x165, 8, { 1580, 4400, -509 }, 0, "Scarecrow room"},
    {  0x165, 10, { -640, 2940, 190 }, 49152, "Fire wall maze"},
    {  0x165, 13, { -2289, 4400, 19 }, 16384, "Hammer room"},
};

room_t water_rooms[] = {
    {  0x10, 0, { -184, 780, 759 }, 32768, "Entrance"},
    {  0x10, 17, { 987, 780, 181 }, 16384, "First ZL water level switch"},
    {  0x10, 12, { -180, 0, -1870 }, 32768, "Pool of tektites and boulders"},
    {  0x10, 8, { -1140, 60, -1810 }, 32768, "Dragon room"},
    {  0x10, 13, { -3124, 1060, -1747 }, 32666, "Dark link room"},
    {  0x10, 21, { -3113, 380, -4222 }, 4759, "River"},
};

room_t shadow_rooms[] = {
    {  0x37, 2, { -254, -63, 594 }, 32768, "Entrance"},
    {  0x37, 8, { 4164, -983, 1366 }, 49152, "Before huge room"},
    {  0x37, 16, { 4677, -1143, 2474 }, 32768, "Invisible scythes"},
    {  0x37, 10, { 1227, -1343, 3853 }, 49152, "Stone umbrella"},
    {  0x37, 11, { 2477, -1343, 1393 }, 32666, "Invisible spikes"},
    {  0x37, 21, { 4387, -1363, -1486 }, 32768, "Before boat"},
    {  0x37, 15, { -3662, -1363, -1585 }, 49152, "Invisible wall maze"},
};

room_t spirit_rooms[] = {
    {  0x82, 1, { -768, -50, -1 }, 49152, "After crawlspace (child)"},
    {  0x82, 0, { 868, -50, 2 }, 16384, "After silver block (adult)"},
    {  0x82, 15, { 1126, 480, -1281 }, 16384, "Spinning cobra room"},
    {  0x82, 5, { 692, 480, -838 }, 49152, "Main room"},
    {  0x82, 18, { 1787, 843, 152 }, 16282, "Armos room"},
    {  0x82, 25, { 268, 1733, -828 }, 49152, "Ceiling mirror"},
};

room_t botw_rooms[] = {
    {  0x98, 0, { 0, -12, 117 }, 32768, "Main room"},
    {  0x98, 2, { -1650, 0, -739 }, 49152, "Coffin room"},
    {  0x98, 3, { 1140, 0, -1339 }, 0, "Beamos room"},
};

room_t ice_rooms[] = {
    {  0x88, 0, { 16, 0, 2678 }, 32768, "Entrance"},
    {  0x88, 3, { 285, 38, 63 }, 32768, "Spinning scythe"},
    {  0x88, 9, { 662, 52, -1656 }, 32768, "Worst room"},
    {  0x88, 5, { -720, 60, -960 }, 49152, "Pushblock room"},
    {  0x88, 6, { -1384, 277, 686 }, 8192, "Before wolfos room"},
};

room_t hideout_rooms[] = {
    {  0x486, 2, { -296, 0, -2951 }, 16384, "Red cell 1 torch"},
    {  0x486, 4, { -105, 0, -335 }, 16384, "Green cell 4 torches"},
    {  0x486, 5, { 1102, 120, 30 }, 0, "Blue cell 2 torches"},
    {  0x486, 1, { 1061, 0, -2037 }, 32768, "Green cell 3 torches"},
};

room_t gtg_rooms[] = {
    {  0x08, 0, { -61, -160, 182 }, 32768, "Entrance"},
    {  0x08, 2, { -1583, -80, -707 }, 32768, "Flame wall maze"},
    {  0x08, 3, { -1579, 160, -2254 }, 32768, "Pushblock room"},
    {  0x08, 4, { -689, 239, -2751 }, 16282, "Rotating statue room"},
    {  0x08, 6, { 1448, -81, -2320 }, 65434, "Lava room"},
    {  0x08, 9, { 2009, -240, -1463 }, 16282, "Toilet"},
};

room_t ganon_rooms[] = {
    {  0x467, 0, { -9, 420, 2283 }, 32768, "Entrance"},
    {  0x467, 17, { -647, 150, 277 }, 60074, "Spirit Trial"},
    {  0x467, 9, { -1406, -240, -840 }, 49050, "Light Trial"},
    {  0x467, 14, { -648, 150, -1990 }, 38151, "Fire Trial"},
    {  0x467, 12, { 660, 150, -1982 }, 27385, "Shadow Trial"},
    {  0x467, 2, { 1319, -240, -835 }, 16282, "Water Trial"},
    {  0x467, 5, { 662, 150, 302 }, 5383, "Forest Trial"},
};

rooms_t dungeon_rooms[13] = {
                            {6, deku_rooms}, {4, dc_rooms}, {3, jabu_rooms},
                            {6, forest_rooms}, {7, fire_rooms}, {6, water_rooms},
                            {7, shadow_rooms}, {6, spirit_rooms}, {3, botw_rooms},
                            {5, ice_rooms}, {4, hideout_rooms}, {6, gtg_rooms}, {7, ganon_rooms},
                        };

warp_t overworld_warps[] = {
    {  0, 0x443, "Kokiri Forest"},
    {  1, 0x11E, "Lost Woods"},
    {  2, 0xFC, "Sacred Forest Meadow"},
    {  3, 0x157, "Lon Lon Ranch"},
    {  4, 0x1FD, "Hyrule Field (from Market)"},
    {  5, 0x181, "Hyrule Field (from River)"},
    {  6, 0x189 , "Hyrule Field (from Lake)"},
    {  7, 0xB1, "Market"},
    {  8, 0x138, "Hyrule Castle/OGC"},
    {  9, 0xDB, "Kakariko"},
    {  10, 0xE4, "Graveyard"},
    {  11, 0x13D, "DMT (from Kak)"},
    {  12, 0x1BD, "DMT (from Crater)"},
    { 13, 0x14D, "Goron City"},
    { 14, 0x246, "DMC (from Goron City)"},
    { 15, 0xEA, "Zora's River"},
    { 16, 0x108, "Zora's Domain"},
    { 17, 0x225, "Zora's Fountain"},
    { 18, 0x102, "Lake Hylia"},
    { 19, 0x117, "Gerudo Valley"},
    { 20, 0x129, "Gerudo Fortress"},
    { 21, 0x130, "Haunted Wastelands"},
    { 22, 0x123, "Colossus"},
};

warp_t bosses_warps[] = {
    {  0, 0x40F, "Gohma"},
    {  1, 0x40B, "King Dodongo"},
    {  2, 0x301, "Barinade"},
    {  3, 0x0C, "Phantom Ganon"},
    {  4, 0x305, "Volvagia"},
    {  5, 0x417, "Morpha"},
    {  6, 0x413, "Bongo Bongo"},
    {  7, 0x8D, "Twinrova"},
    {  8, 0x41F, "Ganondorf"},
    {  9, 0x517, "Ganon"},
};

item_t items_debug[] = {
    {  0, Z64_ITEM_HOOKSHOT, "Hookshot"},
    {  1, Z64_ITEM_LONGSHOT, "Longshot"},
    {  2, Z64_ITEM_SLINGSHOT, "Slingshot"},
    {  3, Z64_ITEM_BOW, "Bow"},
    {  4, Z64_ITEM_BOMB_BAG_20, "Bomb bag"},
    {  5, Z64_ITEM_DEKU_SHIELD, "Deku Shield"},
    {  6, Z64_ITEM_HYLIAN_SHIELD, "Hylian Shield"},
    {  7, Z64_ITEM_MIRROR_SHIELD, "Mirror Shield"},
    {  8, Z64_ITEM_FAIRY_OCARINA, "Ocarina"},
    {  9, Z64_ITEM_BOMBCHU, "Bombchu"},
    {  10, Z64_ITEM_BOOMERANG, "Boomerang"},
    {  11, Z64_ITEM_HAMMER, "Hammer"},
    {  12, Z64_ITEM_BOTTLE, "Bottle"},
    {  13, Z64_ITEM_KOKIRI_SWORD, "Kokiri Sword"},
    {  14, Z64_ITEM_BIGGORON_SWORD, "Biggoron Sword"},
    {  15, Z64_ITEM_IRON_BOOTS, "Iron boots"},
    {  16, Z64_ITEM_HOVER_BOOTS, "Hover boots"},
    {  17, Z64_ITEM_GORONS_BRACELET, "Strength 1"},
    {  18, Z64_ITEM_SILVER_GAUNTLETS, "Strength 2"},
    {  19, Z64_ITEM_GOLDEN_GAUNTLETS, "Strength 3"},
    {  20, Z64_ITEM_SILVER_SCALE, "Scale"},
    {  21, Z64_ITEM_NULL, "Magic"},
    {  22, Z64_ITEM_FOREST_MEDALLION, "Forest Med"},
    {  23, Z64_ITEM_FIRE_MEDALLION, "Fire Med"},
    {  24, Z64_ITEM_WATER_MEDALLION, "Water Med"},
    {  25, Z64_ITEM_SPIRIT_MEDALLION, "Spirit Med"},
    {  26, Z64_ITEM_SHADOW_MEDALLION, "Shadow Med"},
    {  27, Z64_ITEM_LIGHT_MEDALLION, "Light Med"},
    {  28, Z64_ITEM_KOKIRIS_EMERALD, "Emerald"},
    {  29, Z64_ITEM_GORONS_RUBY, "Ruby"},
    {  30, Z64_ITEM_ZORAS_SAPPHIRE, "Sapphire"},
};

menu_category_t actor_categories[] = {
    {  0, "SWITCH"},
    {  1, "BG"},
    {  2, "PLAYER"},
    {  3, "EXPLOSIVES"},
    {  4, "NPC"},
    {  5, "ENEMY"},
    {  6, "PROP"},
    {  7, "ITEMACTION"},
    {  8, "MISC"},
    {  9, "BOSS"},
    {  10, "DOOR"},
    {  11, "CHEST"},
};

void draw_debug_int(int whichNumber, int numberToShow) {
    if (whichNumber < 0 || whichNumber > 9) {
        return;
    }
    debugNumberIsInUsage[whichNumber] = DEBUG_NUMBER_INT;
    debugNumbers[whichNumber] = numberToShow;
}

void draw_debug_float(int whichNumber, float numberToShow) {
    if (whichNumber < 0 || whichNumber > 9) {
        return;
    }
    debugNumberIsInUsage[whichNumber] = DEBUG_NUMBER_FLOAT;
    debugNumbersFloat[whichNumber] = numberToShow;
}

#define CLOCK_TIME(hr, min) ((int32_t)(((hr) * 60 + (min)) * (float)0x10000 / (24 * 60) + 0.5f))

void draw_timeofday(z64_disp_buf_t* db) {

    if (!show_clock) {
        return;
    }

    int16_t digits[4];
    digits[0] = 0;
    double timeInSeconds = z64_file.day_time * (24.0f * 60.0f / 0x10000);
    digits[1] = timeInSeconds / 60.0f;
    while (digits[1] >= 10) {
        digits[0]++;
        digits[1] -= 10;
    }
    digits[2] = 0;
    digits[3] = (int16_t)timeInSeconds % 60;
    while (digits[3] >= 10) {
        digits[2]++;
        digits[3] -= 10;
    }
    int16_t hours = digits[0] * 10 + digits[1];
    colorRGBA8_t color = { 0xFF, 0xFF, 0xFF, 0xFF};
    int total_w = 4 * rupee_digit_sprite.tile_w + font_sprite.tile_w;
    int draw_x = Z64_SCREEN_WIDTH / 2 - total_w / 2;
    int draw_y_text = Z64_SCREEN_HEIGHT - (rupee_digit_sprite.tile_h * 1.5) + 1;
    if (digits[0] == 0) {
        draw_x += rupee_digit_sprite.tile_w;
    }
    draw_int(db, hours, draw_x, draw_y_text, color);
    if (digits[0] == 0) {
        draw_x -= rupee_digit_sprite.tile_w;
    }
    text_print_size(db, ":", draw_x + 2*rupee_digit_sprite.tile_w, draw_y_text, 8, 8);
    int16_t minutes = digits[2] * 10 + digits[3];
    if (digits[2] == 0) {
        draw_int(db, 0, draw_x + 2*rupee_digit_sprite.tile_w + font_sprite.tile_w, draw_y_text, color);
        draw_x += rupee_digit_sprite.tile_w;
    }
    draw_int(db, minutes, draw_x + 2*rupee_digit_sprite.tile_w + font_sprite.tile_w, draw_y_text, color);
}

void debug_utilities(z64_disp_buf_t* db)
{
    // Press L to levitate
    // Shoutouts to glankk
    if (z64_game.common.input[0].pad_pressed.l) {
        z64_link.common.vel_1.y = 6.34375f;
    }

    draw_debug_menu(db);
    draw_debug_numbers(db);
    draw_timeofday(db);
}

int debug_menu_is_drawn() {
    return show_warp_menu;
}

void decimal_to_hex(uint32_t decimalValue, char* hexValue) {
    uint8_t hexSize = 0;
    char hexValueInvert[10];
    while (decimalValue > 0) {
        uint8_t remainder = decimalValue % 16;
        hexValueInvert[hexSize++] = "0123456789ABCDEF"[remainder];
        decimalValue /= 16;
    }
    hexValue[0] = '0';
    hexValue[1] = 'x';
    for (int i = 0; i < hexSize; i++) {
        hexValue[2 + i] = hexValueInvert[hexSize - 1 - i];
    }
    hexValue[hexSize + 2] = '\0';
}

void draw_debug_menu(z64_disp_buf_t* db) {

    if (z64_game.common.input[0].pad_pressed.du || z64_game.common.input[0].pad_pressed.l) {
        show_warp_menu = show_warp_menu ? 0 : 1;
    }

    if (show_warp_menu) {

        if (current_menu_indexes.sub_menu_index == 0) {
            if (z64_game.common.input[0].pad_pressed.dr) {
                current_menu_indexes.main_index++;
                if (current_menu_indexes.main_index > 8) {
                    current_menu_indexes.main_index = 0;
                }
            }
            if (z64_game.common.input[0].pad_pressed.dl) {
                if (current_menu_indexes.main_index == 0) {
                    current_menu_indexes.main_index = 8;
                } else {
                    current_menu_indexes.main_index--;
                }
            }
            if (current_menu_indexes.main_index == 4) {
                if (z64_game.common.input[0].pad_pressed.a) {
                    int age = z64_file.link_age;
                    z64_file.link_age = z64_game.link_age;
                    z64_game.link_age = !z64_game.link_age;
                    z64_file.link_age = age;
                    z64_game.entrance_index = z64_file.entrance_index;

                    // Shoutouts to OoTMM
                    z64_Play_SetupRespawnPoint(&z64_game, 1, 0xDFF);
                    z64_file.respawn_flag = 2;

                    z64_game.scene_load_flag = 0x14;
                    z64_game.fadeout_transition = 0x02;
                    show_warp_menu = 0;
                }
            }
            if (current_menu_indexes.main_index == 5) {
                if (z64_game.common.input[0].pad_pressed.a) {
                    z64_GiveItem(&z64_game, Z64_ITEM_BUNNY_HOOD);
                    z64_usebutton(&z64_game, &z64_link, Z64_ITEM_BUNNY_HOOD, 2);
                }
            }
            if (current_menu_indexes.main_index == 6) {
                if (z64_game.common.input[0].pad_pressed.a) {
                    show_clock = show_clock ? false : true;
                }
            }
            if (current_menu_indexes.main_index < 4 || current_menu_indexes.main_index > 6) {
                if (z64_game.common.input[0].pad_pressed.a && current_menu_indexes.sub_menu_index < 2) {
                    current_menu_indexes.sub_menu_index++;
                }
            }
        } else { // in a sub menu
            if (z64_game.common.input[0].pad_pressed.b && current_menu_indexes.sub_menu_index > -1) {
                current_menu_indexes.sub_menu_index--;
            }

            switch (current_menu_indexes.main_index)
            {
                case 0: // Dungeons
                    if (current_menu_indexes.sub_menu_index < 2) {
                        if (z64_game.common.input[0].pad_pressed.dr) {
                            current_menu_indexes.dungeon_index++;
                            if (current_menu_indexes.dungeon_index > 12) {
                                current_menu_indexes.dungeon_index = 0;
                            }
                        }
                        if (z64_game.common.input[0].pad_pressed.dl) {
                            current_menu_indexes.dungeon_index--;
                            if (current_menu_indexes.dungeon_index < 0) {
                                current_menu_indexes.dungeon_index = 12;
                            }
                        }
                        if (z64_game.common.input[0].pad_pressed.a && current_menu_indexes.sub_menu_index < 2) {
                            current_menu_indexes.sub_menu_index++;
                        }
                        current_menu_indexes.room_index = 0;
                    } else {
                        if (z64_game.common.input[0].pad_pressed.dr) {
                            current_menu_indexes.room_index++;
                            if (current_menu_indexes.room_index > dungeon_rooms[current_menu_indexes.dungeon_index].number_of_rooms - 1) {
                                current_menu_indexes.room_index = 0;
                            }
                        }
                        if (z64_game.common.input[0].pad_pressed.dl) {
                            current_menu_indexes.room_index--;
                            if (current_menu_indexes.room_index < 0) {
                                current_menu_indexes.room_index = dungeon_rooms[current_menu_indexes.dungeon_index].number_of_rooms - 1;
                            }
                        }
                        if (z64_game.common.input[0].pad_pressed.a) {
                            room_t* roomset = dungeon_rooms[current_menu_indexes.dungeon_index].room;
                            room_t* room = &(roomset[current_menu_indexes.room_index]);
                            z64_file.entrance_index = room->scene_index;
                            z64_game.entrance_index = room->scene_index;
                            z64_Play_SetupRespawnPoint(&z64_game, 0x01, 0xDFF);
                            z64_file.respawn[RESPAWN_MODE_RETURN].pos = room->pos;
                            z64_file.respawn[RESPAWN_MODE_RETURN].yaw = room->yaw;
                            z64_file.respawn[RESPAWN_MODE_RETURN].roomIndex = room->room_index;
                            z64_file.respawn_flag = 2;
                            z64_game.scene_load_flag = 0x14;
                            show_warp_menu = 0;
                        }
                    }
                    break;
                case 1: // Overworld
                    if (z64_game.common.input[0].pad_pressed.dr) {
                        current_menu_indexes.overworld_index++;
                        if (current_menu_indexes.overworld_index > 22) {
                            current_menu_indexes.overworld_index = 0;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.dl) {
                        current_menu_indexes.overworld_index--;
                        if (current_menu_indexes.overworld_index < 0) {
                            current_menu_indexes.overworld_index = 22;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.a) {
                        warp_t* d = &(overworld_warps[current_menu_indexes.overworld_index]);
                        z64_file.entrance_index = d->entrance_index;
                        z64_game.entrance_index = d->entrance_index;
                        z64_game.scene_load_flag = 0x14;
                        z64_game.fadeout_transition = 0x02;
                        show_warp_menu = 0;
                    }
                    break;
                case 2: // Bosses
                    if (z64_game.common.input[0].pad_pressed.dr) {
                        current_menu_indexes.boss_index++;
                        if (current_menu_indexes.boss_index > 9) {
                            current_menu_indexes.boss_index = 0;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.dl) {
                        current_menu_indexes.boss_index--;
                        if (current_menu_indexes.boss_index < 0) {
                            current_menu_indexes.boss_index = 9;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.a) {
                        warp_t *d = &(bosses_warps[current_menu_indexes.boss_index]);
                        z64_file.entrance_index = d->entrance_index;
                        z64_game.entrance_index = d->entrance_index;
                        z64_game.scene_load_flag = 0x14;
                        z64_game.fadeout_transition = 0x02;
                        show_warp_menu = 0;
                    }
                    break;
                case 3: // Items
                    if (z64_game.common.input[0].pad_pressed.dr) {
                        current_menu_indexes.item_index++;
                        if (current_menu_indexes.item_index > 30) {
                            current_menu_indexes.item_index = 0;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.dl) {
                        current_menu_indexes.item_index--;
                        if (current_menu_indexes.item_index < 0) {
                            current_menu_indexes.item_index = 30;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.a) {
                        item_t *d = &(items_debug[current_menu_indexes.item_index]);
                        // Songs don't work somehow? So use the rando function instead.
                        if ((d->item_index >= ITEM_SONG_MINUET) && (d->item_index <= ITEM_SONG_STORMS)) {
                            give_quest_item(&z64_file, d->item_index - 0x54, 0);
                        } else {
                            // Magic is not an item.
                            if (d->index == 21) {
                                if (z64_file.magic_capacity_set < 1) {
                                    give_magic(&z64_file, 0, 0);
                                } else {
                                    give_double_magic(&z64_file, 0, 0);
                                }
                            } else {
                                if (d->item_index == Z64_ITEM_BIGGORON_SWORD) {
                                    z64_file.bgs_flag = 1;
                                }
                                z64_GiveItem(&z64_game, d->item_index);
                            }
                        }
                    }
                case 7: // Actors
                    if (current_menu_indexes.sub_menu_index == 1) {
                        if (z64_game.common.input[0].pad_pressed.dr) {
                            current_menu_indexes.actor_index++;
                            if (current_menu_indexes.actor_index > 11) {
                                current_menu_indexes.actor_index = 0;
                            }
                        }
                        if (z64_game.common.input[0].pad_pressed.dl) {
                            current_menu_indexes.actor_index--;
                            if (current_menu_indexes.actor_index < 0) {
                                current_menu_indexes.actor_index = 11;
                            }
                        }
                        current_menu_indexes.specific_actor_index = 0;
                    }
                    if (current_menu_indexes.sub_menu_index == 2) {
                        if (z64_game.common.input[0].pad_pressed.dr) {
                            current_menu_indexes.specific_actor_index++;
                        }
                        if (z64_game.common.input[0].pad_pressed.dl) {
                            current_menu_indexes.specific_actor_index--;
                            if (current_menu_indexes.specific_actor_index < 0) {
                                current_menu_indexes.specific_actor_index = 0;
                            }
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.a && current_menu_indexes.sub_menu_index < 2) {
                        current_menu_indexes.sub_menu_index++;
                    }
                    break;
                case 8: // Overlay
                    if (current_menu_indexes.sub_menu_index == 1) {
                        if (z64_game.common.input[0].pad_pressed.dr) {
                            current_menu_indexes.overlay_index++;
                        }
                        if (z64_game.common.input[0].pad_pressed.dl) {
                            current_menu_indexes.overlay_index--;
                            if (current_menu_indexes.overlay_index < 0) {
                                current_menu_indexes.overlay_index = 0;
                            }
                        }
                    }
                    break;
                default:
                    break;
            }
        }

        // Call setup display list
        gSPDisplayList(db->p++, &setup_db);

        // Set up dimensions
        int icon_size = 12;
        int font_width = 6;
        int font_height = 11;
        int padding = 1;
        int rows = 13;
        int bg_width =
            (6 * icon_size) +
            (13 * font_width) +
            (8 * padding);
        int bg_height = (rows * icon_size) + ((rows + 1) * padding);
        int alphaBackground = 0xD0;

        // Need a bigger and clearer background for the actor menu.
        if (current_menu_indexes.main_index == 7 && current_menu_indexes.sub_menu_index > 1) {
            bg_width *= 1.5;
            alphaBackground = 0xB0;
        }

        int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
        int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;
        int left = bg_left + padding;
        int start_top = bg_top;

        // Draw background
        gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
        gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, alphaBackground);
        gSPTextureRectangle(db->p++,
                bg_left * 4, bg_top * 4,
                (bg_left + bg_width) * 4, (bg_top + bg_height) * 4,
                0, 0, 0, 1024, 1024);

        gDPPipeSync(db->p++);
        gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);

        if (current_menu_indexes.sub_menu_index == 0) {
            gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
            for (int i = 0; i < 9; i++) {
                menu_category_t *d = &(menu_categories[i]);
                int top = start_top + ((icon_size + padding) * i) + 1;
                if (i != current_menu_indexes.main_index) {
                    text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                }
            }
            menu_category_t* d = &(menu_categories[current_menu_indexes.main_index]);
            int top = start_top + ((icon_size + padding) * current_menu_indexes.main_index) + 1;
            gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
            text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
        }
        else {
            switch (current_menu_indexes.main_index)
            {
                case 0: // Dungeons
                    gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                    if (current_menu_indexes.sub_menu_index == 1) {
                        for (int i = 0; i < 13; i++) {
                            warp_t* d = &(dungeon_warps[i]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i != current_menu_indexes.dungeon_index) {
                                text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                            }
                        }

                        warp_t* d = &(dungeon_warps[current_menu_indexes.dungeon_index]);
                        int top = start_top + ((icon_size + padding) * current_menu_indexes.dungeon_index) + 1;
                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                        text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                    }
                    else {
                        gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                        room_t* roomset = dungeon_rooms[current_menu_indexes.dungeon_index].room;
                        for (int i = 0; i < dungeon_rooms[current_menu_indexes.dungeon_index].number_of_rooms; i++) {
                            room_t *room = &(roomset[i]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i != current_menu_indexes.room_index) {
                                text_print_size(db, room->name, left + 5, top + 5, font_width, font_height);
                            }
                        }
                        room_t* room = &(roomset[current_menu_indexes.room_index]);
                        int top = start_top + ((icon_size + padding) * current_menu_indexes.room_index) + 1;
                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                        text_print_size(db, room->name, left + 5, top + 5, font_width, font_height);
                    }
                    break;

                case 1: // Overworld
                    gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                    if (current_menu_indexes.overworld_index < 12) {
                        for (int i = 0; i < 12; i++) {
                            warp_t* d = &(overworld_warps[i]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i != current_menu_indexes.overworld_index) {
                                text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                            }
                        }
                        warp_t* d = &(overworld_warps[current_menu_indexes.overworld_index]);
                        int top = start_top + ((icon_size + padding) * current_menu_indexes.overworld_index) + 1;
                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                        text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                    }
                    else {
                        gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                        for (int i = 0; i < 12; i++) {
                            warp_t* d = &(overworld_warps[i + 12]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i + 12 != current_menu_indexes.overworld_index) {
                                text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                            }
                        }

                        warp_t* d = &(overworld_warps[current_menu_indexes.overworld_index]);
                        int top = start_top + ((icon_size + padding) * (current_menu_indexes.overworld_index - 12)) + 1;
                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                        text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                    }
                    break;
                case 2: // Bosses
                    gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                    for (int i = 0; i < 10; i++) {
                        warp_t* d = &(bosses_warps[i]);
                        int top = start_top + ((icon_size + padding) * i) + 1;
                        if (i != current_menu_indexes.boss_index) {
                            text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                        }
                    }

                    warp_t* d = &(bosses_warps[current_menu_indexes.boss_index]);
                    int top = start_top + ((icon_size + padding) * current_menu_indexes.boss_index) + 1;
                    gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                    text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                    break;
                case 3: // Items
                    gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                    if (current_menu_indexes.item_index < 11) {
                        for (int i = 0; i < 11; i++) {
                            item_t* dd = &(items_debug[i]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i != current_menu_indexes.item_index) {
                                text_print_size(db, dd->name, left + 5, top + 5, font_width, font_height);
                            }
                        }

                        item_t* dd = &(items_debug[current_menu_indexes.item_index]);
                        int top = start_top + ((icon_size + padding) * current_menu_indexes.item_index) + 1;
                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                        text_print_size(db, dd->name, left + 5, top + 5, font_width, font_height);
                    }
                    gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                    if (current_menu_indexes.item_index > 10 && current_menu_indexes.item_index < 22) {
                        for (int i = 0; i < 11; i++) {
                            item_t* dd = &(items_debug[i + 11]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i + 11 != current_menu_indexes.item_index) {
                                text_print_size(db, dd->name, left + 5, top + 5, font_width, font_height);
                            }
                        }

                        item_t *dd = &(items_debug[current_menu_indexes.item_index]);
                        int top = start_top + ((icon_size + padding) * (current_menu_indexes.item_index - 11)) + 1;
                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                        text_print_size(db, dd->name, left + 5, top + 5, font_width, font_height);
                    }
                    gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                    if (current_menu_indexes.item_index > 21 && current_menu_indexes.item_index < 31) {
                        for (int i = 0; i < 9; i++) {
                            item_t* dd = &(items_debug[i + 22]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i + 22 != current_menu_indexes.item_index) {
                                text_print_size(db, dd->name, left + 5, top + 5, font_width, font_height);
                            }
                        }

                        item_t *dd = &(items_debug[current_menu_indexes.item_index]);
                        int top = start_top + ((icon_size + padding) * (current_menu_indexes.item_index - 22)) + 1;
                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                        text_print_size(db, dd->name, left + 5, top + 5, font_width, font_height);
                    }
                    break;
                case 7: // Actor table
                    gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                    colorRGBA8_t color = { 0xFF, 0xFF, 0xFF, 0xFF};
                    if (current_menu_indexes.sub_menu_index == 1) {
                        for (int i = 0; i < ACTORTYPE_CHEST + 1; i++) {
                            menu_category_t* d = &(actor_categories[i]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i != current_menu_indexes.actor_index) {
                                text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                            }
                        }
                        menu_category_t* d = &(actor_categories[current_menu_indexes.actor_index]);
                        int top = start_top + ((icon_size + padding) * current_menu_indexes.actor_index) + 1;
                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                        text_print_size(db, d->name, left + 5, top + 5, font_width, font_height);
                    }
                    else {
                        int8_t nbActors = 0;
                        z64_actor_t* actor = z64_game.actor_list[current_menu_indexes.actor_index].first;
                        uint8_t currentActorPage = current_menu_indexes.specific_actor_index / 13;
                        // Display actor list in 13 by 13 pages.
                        while (actor != NULL) {
                            nbActors++;
                            if (nbActors - 1 < currentActorPage * 13 || nbActors - 1 >= (currentActorPage + 1) * 13) {
                                actor = actor->next;
                                continue;
                            }
                            // Color the actor in red when its line is highlighted.
                            if (nbActors == current_menu_indexes.specific_actor_index + 1) {
                                Actor_SetColorFilter(actor, 0x4000, 125, 0x0000, 5);
                                gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                            }
                            else {
                                gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                            }
                            top = start_top + ((icon_size + padding) * ((nbActors - 1) % 13)) + 1;
                            char idActor[10];
                            decimal_to_hex(actor->actor_id, idActor);
                            text_print_size(db, idActor, left + 5, top + 5, font_width, font_height);
                            uint32_t numberToConvert = (uintptr_t)actor;
                            char AddressActor[10];
                            decimal_to_hex(numberToConvert, AddressActor);
                            text_print_size(db, AddressActor, left + 7*font_width, top + 5, font_width, font_height);
                            draw_int_size(db, actor->pos_world.x, left + 20*font_width + 5, top + 5, color, font_width, font_height);
                            draw_int_size(db, actor->pos_world.y, left + 25*font_width + 5, top + 5, color, font_width, font_height);
                            draw_int_size(db, actor->pos_world.z, left + 30*font_width + 5, top + 5, color, font_width, font_height);
                            actor = actor->next;
                        }
                    }
                    break;
                case 8: // Overlay table
                    if (current_menu_indexes.sub_menu_index == 1) {
                        uint8_t currentOverlayTab = current_menu_indexes.overlay_index / 12;
                        // Display overlay list in 12 by 12 pages.
                        uint8_t nbOverlays, currentOverlayTabIndex = 0;
                        for (int overlay_id = 0; overlay_id < 0x0192; overlay_id++) {
                            ActorOverlay overlay = gActorOverlayTable[overlay_id];
                             if (overlay.loadedRamAddr) {
                                nbOverlays++;
                                if (nbOverlays > currentOverlayTab * 12 && nbOverlays < (currentOverlayTab + 1) * 12 + 1) {
                                    currentOverlayTabIndex++;
                                    if (nbOverlays == current_menu_indexes.overlay_index + 1) {
                                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 255);
                                    }
                                    else {
                                        gDPSetPrimColor(db->p++, 0, 0, 255, 255, 255, 255);
                                    }
                                    top = start_top + ((icon_size + padding) * ((currentOverlayTabIndex - 1) % 12)) + 1;
                                    char idActor[10];
                                    decimal_to_hex(overlay_id, idActor);
                                    text_print_size(db, idActor, left + 5, top + 5, font_width, font_height);
                                    char ramStartOverlay[10];
                                    uint32_t numberToConvert = (uintptr_t)overlay.loadedRamAddr;
                                    decimal_to_hex(numberToConvert, ramStartOverlay);
                                    text_print_size(db, ramStartOverlay, left + 10*font_width + 5, top + 5, font_width, font_height);
                                }
                            }
                        }
                    }
                    break;
                default:
                    break;
            }
        }
    }
}

void draw_debug_numbers(z64_disp_buf_t* db) {

    for (int i = 0; i < 10; i++) {

        int numberToShow = debugNumbers[i];
        if (debugNumberIsInUsage[i] != DEBUG_NUMBER_INT) {
            continue;
        }

        int debug_text_x_placement = Z64_SCREEN_WIDTH / 12;
        int debug_text_y_placement = rupee_digit_sprite.tile_h * 2.5;

        int offsetY = i * rupee_digit_sprite.tile_h;
        int height = debug_text_y_placement;
        // Move down if magic or 2nd row of hearts
        if (z64_file.magic_capacity_set > 0)
            height += rupee_digit_sprite.tile_h * 0.8;
        if (z64_file.energy_capacity > 10 * 0x10)
            height += rupee_digit_sprite.tile_h * 0.8;

        colorRGBA8_t color = { debug_text_color.r, debug_text_color.g, debug_text_color.b, 0xFF};
        draw_int(db, numberToShow, debug_text_x_placement, height + offsetY, color);
    }

    for (int i = 0; i < 10; i++) {

        float numberToShow = debugNumbersFloat[i];
        if (debugNumberIsInUsage[i] != DEBUG_NUMBER_FLOAT) {
            continue;
        }
        float decimalValue = 0;
        int32_t entireValue = (int32_t)(numberToShow);
        if (numberToShow > 0) {
            decimalValue = (numberToShow - entireValue);
        }
        else {
            decimalValue = (entireValue - numberToShow);
        }
        int precision_copy = float_precision;
        while(precision_copy) {
            decimalValue *= 10;
            precision_copy--;
        }

        int debug_text_x_placement = Z64_SCREEN_WIDTH / 12;
        int debug_text_y_placement = rupee_digit_sprite.tile_h * 2.5;

        int offsetY = i * rupee_digit_sprite.tile_h;
        int height = debug_text_y_placement;
        // Move down if magic or 2nd row of hearts
        if (z64_file.magic_capacity_set > 0)
            height += rupee_digit_sprite.tile_h * 0.8;
        if (z64_file.energy_capacity > 10 * 0x10)
            height += rupee_digit_sprite.tile_h * 0.8;

        colorRGBA8_t color = { debug_text_color.r, debug_text_color.g, debug_text_color.b, 0xFF};
        int numberDigit = draw_int(db, entireValue, debug_text_x_placement, height + offsetY, color);
        text_print_size(db, ".", debug_text_x_placement + numberDigit * rupee_digit_sprite.tile_w, height + offsetY, rupee_digit_sprite.tile_w, rupee_digit_sprite.tile_h);
        draw_int(db, decimalValue, debug_text_x_placement + numberDigit * rupee_digit_sprite.tile_w + font_sprite.tile_w,
                        height + offsetY, color);
    }
}
