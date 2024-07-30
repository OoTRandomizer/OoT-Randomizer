#include "debug.h"

const int8_t debug_text_width = 16;
const int8_t debug_text_height = 16;
colorRGB8_t debug_text_color = { 0xE0, 0xE0, 0x10 }; // Yellow
int8_t float_precision = 5;
int8_t menu_not_on_dup = 0;

menu_category_t menu_categories[] = {
    {  0, "Dungeons"},
    {  1, "Overworld"},
    {  2, "Bosses"},
    {  3, "Items"},
    {  4, "Switch Age"},
    {  5, "Bunny Hood"},
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

warp_t overworld_warps[] = {
    {  0, 0x443, "KF"},
    {  1, 0x11E, "LW"},
    {  2, 0xFC, "SFM"},
    {  3, 0x157, "LLR"},
    {  4, 0xB1, "Market"},
    {  5, 0x138, "HC/OGC"},
    {  6, 0xDB, "Kak"},
    {  7, 0xE4, "GY"},
    {  8, 0x13D, "DMT (Kak)"},
    {  9, 0x1BD, "DMT (Crater)"},
    { 10, 0x14D, "Goron City"},
    { 11, 0xEA, "ZR"},
    { 12, 0x108, "ZD"},
    { 13, 0x225, "ZF"},
    { 14, 0x102, "LH"},
    { 15, 0x117, "GV"},
    { 16, 0x129, "GF"},
    { 17, 0x130, "HW"},
    { 18, 0x123, "Colossus"},
};

warp_t bosses_warps[] = {
    {  0, 0x40F, "Gohma"},
    {  1, 0x40B, "KD"},
    {  2, 0x301, "Bari"},
    {  3, 0x0C, "PG"},
    {  4, 0x305, "Volv"},
    {  5, 0x417, "Morph"},
    {  6, 0x413, "Bongo"},
    {  7, 0x8D, "Twin"},
    {  8, 0x41F, "Ganondorf"},
    {  9, 0x517, "Ganon"},
};

item_t items_debug[] = {
    {  0, Z64_ITEM_HOOKSHOT, "Hookshot"},
    {  1, Z64_ITEM_LONGSHOT, "Longshot"},
    {  2, Z64_ITEM_BOW, "Bow"},
    {  3, Z64_ITEM_BOMB_BAG_20, "Bomb bag"},
    {  4, Z64_ITEM_DEKU_SHIELD, "Deku Shield"},
    {  5, Z64_ITEM_HYLIAN_SHIELD, "Hylian Shield"},
    {  6, Z64_ITEM_MIRROR_SHIELD, "Mirror Shield"},
    {  7, Z64_ITEM_FAIRY_OCARINA, "Ocarina"},
    {  8, Z64_ITEM_BOMBCHU, "Bombchu"},
    {  9, Z64_ITEM_BOOMERANG, "Boomerang"},
    {  10, Z64_ITEM_HAMMER, "Hammer"},
    {  11, Z64_ITEM_BOTTLE, "Bottle"},
    {  12, Z64_ITEM_KOKIRI_SWORD, "KS"},
    {  13, Z64_ITEM_BIGGORON_SWORD, "BGS"},
    {  14, Z64_ITEM_IRON_BOOTS, "Irons"},
    {  15, Z64_ITEM_HOVER_BOOTS, "Hovers"},
    {  16, Z64_ITEM_GORONS_BRACELET, "Str1"},
    {  17, Z64_ITEM_SILVER_GAUNTLETS, "Str2"},
    {  18, Z64_ITEM_GOLDEN_GAUNTLETS, "Str3"},
    {  19, Z64_ITEM_SILVER_SCALE, "Scale"},
    {  20, Z64_ITEM_FOREST_MEDALLION, "Forest Med"},
    {  21, Z64_ITEM_FIRE_MEDALLION, "Fire Med"},
    {  22, Z64_ITEM_WATER_MEDALLION, "Water Med"},
    {  23, Z64_ITEM_SPIRIT_MEDALLION, "Spirit Med"},
    {  24, Z64_ITEM_SHADOW_MEDALLION, "Shadow Med"},
    {  25, Z64_ITEM_LIGHT_MEDALLION, "Light Med"},
    {  26, Z64_ITEM_KOKIRIS_EMERALD, "Emerald"},
    {  27, Z64_ITEM_GORONS_RUBY, "Ruby"},
    {  28, Z64_ITEM_ZORAS_SAPPHIRE, "Sapphire"},
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

void debug_utilities(z64_disp_buf_t *db)
{
    // Press L to levitate
    // Shoutouts to glankk
    if (z64_game.common.input[0].raw.pad.l) {
        z64_link.common.vel_1.y = 6.34375f;
    }

    draw_debug_menu(db);
    draw_debug_numbers(db);
}

int debug_menu_is_drawn() {
    return show_warp_menu;
}

void draw_debug_menu(z64_disp_buf_t *db) {
    if (menu_not_on_dup) {
        if (z64_game.common.input[0].pad_pressed.l && z64_game.common.input[0].pad_pressed.r) {
            show_warp_menu = show_warp_menu ? 0 : 1;
        }
    }
    else {
        if (z64_game.common.input[0].pad_pressed.du) {
            show_warp_menu = show_warp_menu ? 0 : 1;
        }
    }

    if (show_warp_menu) {

        if (current_menu_indexes.sub_menu_index == 0) {

            if (z64_game.common.input[0].pad_pressed.dr) {
                current_menu_indexes.main_index++;
                if (current_menu_indexes.main_index > 5) {
                    current_menu_indexes.main_index = 0;
                }
            }
            if (z64_game.common.input[0].pad_pressed.dl) {
                if (current_menu_indexes.main_index == 0) {
                    current_menu_indexes.main_index = 5;
                }
                else {
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
                    z64_file.void_flag = 2;

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
            if (current_menu_indexes.main_index < 4){
                if (z64_game.common.input[0].pad_pressed.a) {
                    current_menu_indexes.sub_menu_index++;
                }
            }
        }
        else { // in a sub menu

            if (z64_game.common.input[0].pad_pressed.b) {
                current_menu_indexes.sub_menu_index--;
            }

            switch (current_menu_indexes.main_index)
            {
                case 0: // Dungeons
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
                    if (z64_game.common.input[0].pad_pressed.a) {
                        warp_t *d = &(dungeon_warps[current_menu_indexes.dungeon_index]);
                        z64_file.entrance_index = d->entrance_index;
                        z64_game.entrance_index = d->entrance_index;
                        z64_game.scene_load_flag = 0x14;
                        z64_game.fadeout_transition = 0x02;
                        show_warp_menu = 0;
                    }
                    break;
                case 1: // Overworld
                    if (z64_game.common.input[0].pad_pressed.dr) {
                        current_menu_indexes.overworld_index++;
                        if (current_menu_indexes.overworld_index > 18) {
                            current_menu_indexes.overworld_index = 0;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.dl) {
                        current_menu_indexes.overworld_index--;
                        if (current_menu_indexes.overworld_index < 0) {
                            current_menu_indexes.overworld_index = 18;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.a) {
                        warp_t *d = &(overworld_warps[current_menu_indexes.overworld_index]);
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
                        if (current_menu_indexes.item_index > 28) {
                            current_menu_indexes.item_index = 0;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.dl) {
                        current_menu_indexes.item_index--;
                        if (current_menu_indexes.item_index < 0) {
                            current_menu_indexes.item_index = 28;
                        }
                    }
                    if (z64_game.common.input[0].pad_pressed.a) {
                        item_t *d = &(items_debug[current_menu_indexes.item_index]);
                        // Songs don't work somehow? So use the rando function instead.
                        if ((d->item_index >= ITEM_SONG_MINUET) && (d->item_index <= ITEM_SONG_STORMS)) {
                            give_quest_item(&z64_file, d->item_index - 0x54, 0);
                        }
                        else {
                            if (d->item_index == Z64_ITEM_BIGGORON_SWORD) {
                                z64_file.bgs_flag = 1;
                            }
                            z64_GiveItem(&z64_game, d->item_index);
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

        if (current_menu_indexes.sub_menu_index == 0) {
            gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
            for (int i = 0; i < 6; i++) {
                menu_category_t *d = &(menu_categories[i]);
                int top = start_top + ((icon_size + padding) * i) + 1;
                if (i != current_menu_indexes.main_index) {
                    text_print_size(db, d->name, left, top, font_width, font_height);
                }
            }

            gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10 , 0xFF);
            menu_category_t *d = &(menu_categories[current_menu_indexes.main_index]);
            int top = start_top + ((icon_size + padding) * current_menu_indexes.main_index) + 1;
            text_print_size(db, d->name, left, top, font_width, font_height);
        }
        else {
            switch (current_menu_indexes.main_index)
            {
                case 0: // Dungeons
                    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
                    for (int i = 0; i < 13; i++) {
                        warp_t *d = &(dungeon_warps[i]);
                        int top = start_top + ((icon_size + padding) * i) + 1;
                        if (i != current_menu_indexes.dungeon_index) {
                            text_print_size(db, d->name, left, top, font_width, font_height);
                        }
                    }

                    gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 0xFF);
                    warp_t *d = &(dungeon_warps[current_menu_indexes.dungeon_index]);
                    int top = start_top + ((icon_size + padding) * current_menu_indexes.dungeon_index) + 1;
                    text_print_size(db, d->name, left, top, font_width, font_height);
                    break;

                case 1: // Overworld
                    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
                    if (current_menu_indexes.overworld_index < 10) {
                        for (int i = 0; i < 10; i++) {
                            warp_t *d = &(overworld_warps[i]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i != current_menu_indexes.overworld_index) {
                                text_print_size(db, d->name, left, top, font_width, font_height);
                            }
                        }
                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 0xFF);
                        d = &(overworld_warps[current_menu_indexes.overworld_index]);
                        top = start_top + ((icon_size + padding) * current_menu_indexes.overworld_index) + 1;
                        text_print_size(db, d->name, left, top, font_width, font_height);
                    }
                    else {
                        for (int i = 0; i < 9; i++) {
                            warp_t *d = &(overworld_warps[i + 10]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i + 10 != current_menu_indexes.overworld_index) {
                                text_print_size(db, d->name, left, top, font_width, font_height);
                            }
                        }

                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 0xFF);
                        d = &(overworld_warps[current_menu_indexes.overworld_index]);
                        top = start_top + ((icon_size + padding) * (current_menu_indexes.overworld_index - 10)) + 1;
                        text_print_size(db, d->name, left, top, font_width, font_height);
                    }
                    break;
                case 2: // Bosses
                    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
                    for (int i = 0; i < 10; i++) {
                        warp_t *d = &(bosses_warps[i]);
                        int top = start_top + ((icon_size + padding) * i) + 1;
                        if (i != current_menu_indexes.boss_index) {
                            text_print_size(db, d->name, left, top, font_width, font_height);
                        }
                    }

                    gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 0xFF);
                    d = &(bosses_warps[current_menu_indexes.boss_index]);
                    top = start_top + ((icon_size + padding) * current_menu_indexes.boss_index) + 1;
                    text_print_size(db, d->name, left, top, font_width, font_height);
                    break;
                case 3: // Items
                    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
                    if (current_menu_indexes.item_index < 10) {
                        for (int i = 0; i < 10; i++) {
                            item_t *dd = &(items_debug[i]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i != current_menu_indexes.item_index) {
                                text_print_size(db, dd->name, left, top, font_width, font_height);
                            }
                        }

                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10, 0xFF);
                        item_t *dd = &(items_debug[current_menu_indexes.item_index]);
                        top = start_top + ((icon_size + padding) * current_menu_indexes.item_index) + 1;
                        text_print_size(db, dd->name, left, top, font_width, font_height);
                    }
                    if (current_menu_indexes.item_index > 9 && current_menu_indexes.item_index < 20) {
                        for (int i = 0; i < 10; i++) {
                            item_t *dd = &(items_debug[i + 10]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i + 10 != current_menu_indexes.item_index) {
                                text_print_size(db, dd->name, left, top, font_width, font_height);
                            }
                        }

                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10 , 0xFF);
                        item_t *dd = &(items_debug[current_menu_indexes.item_index]);
                        top = start_top + ((icon_size + padding) * (current_menu_indexes.item_index - 10)) + 1;
                        text_print_size(db, dd->name, left, top, font_width, font_height);
                    }
                    if (current_menu_indexes.item_index > 19 && current_menu_indexes.item_index < 28) {
                        for (int i = 0; i < 9; i++) {
                            item_t *dd = &(items_debug[i + 20]);
                            int top = start_top + ((icon_size + padding) * i) + 1;
                            if (i + 20 != current_menu_indexes.item_index) {
                                text_print_size(db, dd->name, left, top, font_width, font_height);
                            }
                        }

                        gDPSetPrimColor(db->p++, 0, 0, 0xE0, 0xE0, 0x10 , 0xFF);
                        item_t *dd = &(items_debug[current_menu_indexes.item_index]);
                        top = start_top + ((icon_size + padding) * (current_menu_indexes.item_index - 20)) + 1;
                        text_print_size(db, dd->name, left, top, font_width, font_height);
                    }
                    break;
                default:
                    break;
            }
        }
    }
}

// Helper function for drawing numbers to the HUD.
int draw_int_helper(z64_disp_buf_t *db, int32_t number, int16_t left, int16_t top, colorRGBA8_t color) {

    int isNegative = 0;
    if (number < 0) {
        number *= -1;
        isNegative = 1;
    }

    uint8_t digits[10];
    uint8_t j = 0;
    // Extract each digit. They are added, in reverse order, to digits[]
    do {
        digits[j] = number % 10;
        number = number / 10;
        j++;
    }
    while ( number > 0 );
    // This combiner mode makes it look like the rupee count
    gDPSetCombineLERP(db->p++, 0, 0, 0, PRIMITIVE, TEXEL0, 0, PRIMITIVE, 0, 0, 0, 0, PRIMITIVE,
                            TEXEL0, 0, PRIMITIVE, 0);

    // Set the color
    gDPSetPrimColor(db->p++, 0, 0, color.r, color.g, color.b, color.a);
    if (isNegative) {
        text_print_size(db, "-", left - rupee_digit_sprite.tile_w, top, 8, 16);
    }
    // Draw each digit
    for (uint8_t c = j; c > 0; c--) {
        sprite_texture(db, &rupee_digit_sprite, digits[c-1], left, top, 8, 16);
        left += 8;
    }
    return j;
}


void draw_debug_numbers(z64_disp_buf_t *db) {

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
        draw_int_helper(db, numberToShow, debug_text_x_placement, height + offsetY, color);
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
        int numberDigit = draw_int_helper(db, entireValue, debug_text_x_placement, height + offsetY, color);
        text_print_size(db, ".", debug_text_x_placement + numberDigit * rupee_digit_sprite.tile_w, height + offsetY, rupee_digit_sprite.tile_w, rupee_digit_sprite.tile_h);
        draw_int_helper(db, decimalValue, debug_text_x_placement + numberDigit * rupee_digit_sprite.tile_w + font_sprite.tile_w,
                        height + offsetY, color);
    }
}
