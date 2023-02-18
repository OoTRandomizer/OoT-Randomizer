#include "gfx.h"
#include "dpad.h"
#include "trade_quests.h"

extern uint8_t CFG_DISPLAY_DPAD;

//unknown 00 is a pointer to some vector transformation when the sound is tied to an actor. actor + 0x3E, when not tied to an actor (map), always 80104394
//unknown 01 is always 4 in my testing
//unknown 02 is a pointer to some kind of audio configuration Always 801043A0 in my testing
//unknown 03 is always a3 in my testing
//unknown 04 is always a3 + 0x08 in my testing (801043A8)
typedef void(*playsfx_t)(uint16_t sfx, z64_xyzf_t *unk_00_, int8_t unk_01_ , float *unk_02_, float *unk_03_, float *unk_04_);
typedef void(*usebutton_t)(z64_game_t *game, z64_link_t *link, uint8_t item, uint8_t button);

#define z64_playsfx   ((playsfx_t)      0x800C806C)
#define z64_usebutton ((usebutton_t)    0x8038C9A0)

void handle_dpad() {

    pad_t pad_pressed = z64_game.common.input[0].pad_pressed;
    pad_t pad_held = z64_ctxt.input[0].raw.pad;

    if (CAN_USE_TRADE_DPAD) {
        uint8_t current_trade_item = z64_file.items[z64_game.pause_ctxt.item_cursor];
        if (IsTradeItem(current_trade_item)) {
            uint8_t potential_trade_item = current_trade_item;

            if (pad_pressed.dl) {
                potential_trade_item = SaveFile_PrevOwnedTradeItem(current_trade_item);
            }

            if (pad_pressed.dr) {
                potential_trade_item = SaveFile_NextOwnedTradeItem(current_trade_item);
            }

            if (current_trade_item != potential_trade_item) {
                UpdateTradeEquips(potential_trade_item, z64_game.pause_ctxt.item_cursor);
                PlaySFX(0x4809); // cursor move sound effect NA_SE_SY_CURSOR
            }
        }
    } else if (CAN_USE_DPAD && DISPLAY_DPAD && (!pad_held.a || !CAN_DRAW_DUNGEON_INFO)) {
        if (z64_file.link_age == 0) {
            if (pad_pressed.dl && z64_file.iron_boots) {
                if (z64_file.equip_boots == 2) z64_file.equip_boots = 1;
                else z64_file.equip_boots = 2;
                z64_UpdateEquipment(&z64_game, &z64_link);
                z64_playsfx(0x835, (z64_xyzf_t*)0x80104394, 0x04, (float*)0x801043A0, (float*)0x801043A0, (float*)0x801043A8);
            }

            if (pad_pressed.dr && z64_file.hover_boots) {
                if (z64_file.equip_boots == 3) z64_file.equip_boots = 1;
                else z64_file.equip_boots = 3;
                z64_UpdateEquipment(&z64_game, &z64_link);
                z64_playsfx(0x835, (z64_xyzf_t*)0x80104394, 0x04, (float*)0x801043A0, (float*)0x801043A0, (float*)0x801043A8);
            }
        }

        if (z64_file.link_age == 1) {
            if (pad_pressed.dr && CAN_USE_CHILD_TRADE) {
                z64_usebutton(&z64_game,&z64_link,z64_file.items[Z64_SLOT_CHILD_TRADE], 2);
            }
        }

        if (pad_pressed.dd && CAN_USE_OCARINA) {
            z64_usebutton(&z64_game,&z64_link,z64_file.items[Z64_SLOT_OCARINA], 2);
        }
    }
}

void draw_dpad() {
    z64_disp_buf_t *db = &(z64_ctxt.gfx->overlay);
    if (CAN_DRAW_DUNGEON_INFO || (DISPLAY_DPAD && CFG_DISPLAY_DPAD) || CAN_DRAW_TRADE_DPAD) {
        gSPDisplayList(db->p++, &setup_db);
        gDPPipeSync(db->p++);
        gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
        uint16_t alpha = z64_game.hud_alpha_channels.rupees_keys_magic;

        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha);
        sprite_load(db, &dpad_sprite, 0, 1);
        int left = 271;
        if (CAN_DRAW_TRADE_DPAD) {
            uint8_t current_trade_item = z64_file.items[z64_game.pause_ctxt.item_cursor];
            if (IsTradeItem(current_trade_item)) {
                uint8_t prev_trade_item = SaveFile_PrevOwnedTradeItem(current_trade_item);
                uint8_t next_trade_item = SaveFile_NextOwnedTradeItem(current_trade_item);

                if (current_trade_item != next_trade_item) {
                    // D-pad under selected trade item slot, if more than one trade item
                    left = (z64_game.pause_ctxt.item_cursor == Z64_SLOT_ADULT_TRADE) ? 197 : 230;
                    sprite_draw(db, &dpad_sprite, 0, left, 190, 24, 24);

                    // Previous trade quest item
                    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha);
                    sprite_load(db, &items_sprite, prev_trade_item, 1);
                    sprite_draw(db, &items_sprite, 0, left - 16, 194, 16, 16);

                    // Next trade quest item
                    gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha);
                    sprite_load(db, &items_sprite, next_trade_item, 1);
                    sprite_draw(db, &items_sprite, 0, left + 24, 194, 16, 16);
                }
            }
        }
        if (left == 271) {
            // D-pad under C buttons, if trade slot selector not drawn
            sprite_draw(db, &dpad_sprite, 0, left, 64, 16, 16);
        }

        if (CAN_DRAW_DUNGEON_INFO && CFG_DPAD_DUNGEON_INFO_ENABLE && left == 271) {
            // Zora sapphire on D-down
            sprite_load(db, &stones_sprite, 2, 1);
            sprite_draw(db, &stones_sprite, 0, 273, 77, 12, 12);

            // small key on D-right
            sprite_load(db, &quest_items_sprite, 17, 1);
            sprite_draw(db, &quest_items_sprite, 0, 285, 66, 12, 12);

            // map on D-left
            sprite_load(db, &quest_items_sprite, 16, 1);
            sprite_draw(db, &quest_items_sprite, 0, 260, 66, 12, 12);
        } else if (left == 271) {
            if (!CAN_USE_DPAD)
                gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha * 0x46 / 0xFF);

            if (z64_file.iron_boots && z64_file.link_age==0) {
                sprite_load(db, &items_sprite, 69, 1);
                if (z64_file.equip_boots == 2) {
                    sprite_draw(db, &items_sprite, 0, 258, 64, 16, 16);
                }
                else {
                    sprite_draw(db, &items_sprite, 0, 260, 66, 12, 12);
                }
            }

            if (z64_file.hover_boots && z64_file.link_age == 0) {
                sprite_load(db, &items_sprite, 70, 1);
                if (z64_file.equip_boots == 3) {
                    sprite_draw(db, &items_sprite, 0, 283, 64, 16, 16);
                }
                else {
                    sprite_draw(db, &items_sprite, 0, 285, 66, 12, 12);
                }
            }

            if (z64_file.items[Z64_SLOT_CHILD_TRADE] >= Z64_ITEM_WEIRD_EGG && z64_file.items[Z64_SLOT_CHILD_TRADE] <= Z64_ITEM_MASK_OF_TRUTH && z64_file.link_age == 1) {
                if(!CAN_USE_DPAD || !CAN_USE_CHILD_TRADE) gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha * 0x46 / 0xFF);
                else gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha);
                sprite_load(db, &items_sprite, z64_file.items[Z64_SLOT_CHILD_TRADE], 1);
                sprite_draw(db, &items_sprite, 0, 285, 66, 12, 12);
            }

            if (z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_FAIRY_OCARINA || z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_OCARINA_OF_TIME) {
                if(!CAN_USE_DPAD || !CAN_USE_OCARINA) gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha * 0x46 / 0xFF);
                else gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, alpha);
                sprite_load(db, &items_sprite, z64_file.items[Z64_SLOT_OCARINA], 1);
                sprite_draw(db, &items_sprite, 0, 273, 77, 12,12);
            }
        }

        gDPPipeSync(db->p++);
    }
}

