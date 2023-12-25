#ifndef DPAD_H
#define DPAD_H

#include "dungeon_info.h"
#include "z64.h"
#include <stdbool.h>
#include "ocarina_buttons.h"
#include "item_draw_functions.h"
extern uint8_t CFG_DPAD_ON_THE_LEFT;
#include "debug.h"

// PLAYER_STATE1_0 : Scene transition
// PLAYER_STATE1_SWINGING_BOTTLE
// PLAYER_STATE1_7 : Death
// PLAYER_STATE1_10 : Get an item
// PLAYER_STATE1_28 : Using Non-Weapon Item
// PLAYER_STATE1_29 : Environment Frozen/Invulnerability
#define BLOCK_DPAD (0x00000001 | \
                    0x00000002 | \
                    0x00000080 | \
                    0x00000400 | \
                    0x10000000 | \
                    0x20000000)

// PLAYER_STATE1_23 : Riding Epona
// PLAYER_STATE1_11 : Link holding something over his head
// PLAYER_STATE1_21 : Climbing walls
// PLAYER_STATE1_27 : Swimming
#define BLOCK_ITEMS (0x00800000 | \
                     0x00000800 | \
                     0x00200000 | \
                     0x08000000)

extern uint16_t CFG_ADULT_TRADE_SHUFFLE;
extern uint16_t CFG_CHILD_TRADE_SHUFFLE;

#define CAN_DRAW_TRADE_DPAD (z64_game.pause_ctxt.state == 6 && \
                            z64_game.pause_ctxt.screen_idx == 0 && \
                            (!z64_game.pause_ctxt.changing || z64_game.pause_ctxt.changing == 3) && \
                            ((z64_game.pause_ctxt.item_cursor == Z64_SLOT_ADULT_TRADE && CFG_ADULT_TRADE_SHUFFLE) || \
                            (z64_game.pause_ctxt.item_cursor == Z64_SLOT_CHILD_TRADE && CFG_CHILD_TRADE_SHUFFLE)))

#define CAN_DRAW_OCARINA_BUTTONS (z64_game.pause_ctxt.state == 6 && \
                            z64_game.pause_ctxt.screen_idx == 0 && \
                            (!z64_game.pause_ctxt.changing || z64_game.pause_ctxt.changing == 3) && \
                            (z64_game.pause_ctxt.item_cursor == Z64_SLOT_OCARINA && SHUFFLE_OCARINA_BUTTONS))

#define CAN_USE_TRADE_DPAD  (CAN_DRAW_TRADE_DPAD && z64_game.pause_ctxt.changing != 3)

#define DISPLAY_DPAD        ((((z64_file.iron_boots || z64_file.hover_boots) && z64_file.link_age == 0) || \
                            ((z64_file.items[Z64_SLOT_CHILD_TRADE] >= Z64_ITEM_WEIRD_EGG && z64_file.items[Z64_SLOT_CHILD_TRADE] <= Z64_ITEM_MASK_OF_TRUTH) && z64_file.link_age == 1) || \
                            z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_FAIRY_OCARINA || z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_OCARINA_OF_TIME) && \
                            !CAN_DRAW_TRADE_DPAD)

#define CAN_USE_DPAD        (((z64_link.state_flags_1 & BLOCK_DPAD) == 0) && \
                            ((uint32_t)z64_ctxt.state_dtor==z64_state_ovl_tab[3].vram_dtor) && \
                            (z64_file.game_mode == 0) && \
                            ((z64_event_state_1 & 0x20) == 0) && \
                            (!CAN_DRAW_DUNGEON_INFO || !CFG_DPAD_DUNGEON_INFO_ENABLE) && \
                            !(debug_menu_is_drawn()))
// Not in pause menu
// Ocarina in inventory
// Scenes ocarina restrictions, specific to each scene
// BLOCK_ITEMS above
// Not getting pulled by hookshot
// Not playing Bombchu bowling
// Not playing Shooting Gallery
#define CAN_USE_OCARINA     (z64_game.pause_ctxt.state == 0 && \
                            (z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_FAIRY_OCARINA || z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_OCARINA_OF_TIME) && \
                            !z64_game.restriction_flags.ocarina && \
                            ((z64_link.state_flags_1 & BLOCK_ITEMS) == 0) && \
                            (!(z64_link.state_flags_3 & (1 << 7))) && \
                            z64_game.bombchuBowlingStatus == 0 && \
                            z64_game.shootingGalleryStatus == 0)

#define CAN_USE_CHILD_TRADE (z64_game.pause_ctxt.state == 0 && z64_file.items[Z64_SLOT_CHILD_TRADE] >= Z64_ITEM_WEIRD_EGG && z64_file.items[Z64_SLOT_CHILD_TRADE] <= Z64_ITEM_MASK_OF_TRUTH && !z64_game.restriction_flags.trade_items && ((z64_link.state_flags_1 & BLOCK_ITEMS) == 0))

void handle_dpad();
void draw_dpad_and_menu_utilities();

#endif
