#include "audio.h"
#include "gfx.h"
#include "kaleido_item.h"

void KaleidoScope_DrawItemSelect(z64_game_t* play) {
    static int16_t magic_arrow_effects_r[] = {255, 100, 255 };
    static int16_t magic_arrow_effects_g[] = {0, 100, 255 };
    static int16_t magic_arrow_effects_b[] = {0, 255, 100 };
    z64_input_t* input = &play->common.input[0];
    z64_pause_ctxt_t* pause_ctxt = &play->pause_ctxt;
    uint16_t i;
    uint16_t j;
    uint16_t cursor_item;
    uint16_t cursor_slot;
    uint16_t index;
    int16_t cursor_point;
    int16_t cursor_x;
    int16_t cursor_y;
    int16_t old_cursor_point;
    int16_t move_cursor_result;

    OPEN_DISPS(play->common.gfx);

    z64_Gfx_SetupDL_42Opa(play->common.gfx);

    gDPSetCombineMode(POLY_OPA_DISP++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);

    pause_ctxt->cursor_color_set = 0;
    pause_ctxt->name_color_set = 0;

    if ((pause_ctxt->state == PAUSE_STATE_MAIN) && (pause_ctxt->changing == PAUSE_MAIN_STATE_IDLE) &&
        (pause_ctxt->screen_idx == PAUSE_ITEM)) {
        move_cursor_result = 0;
        old_cursor_point = pause_ctxt->cursor_point[PAUSE_ITEM];

        cursor_item = pause_ctxt->cursor_item[PAUSE_ITEM];
        cursor_slot = pause_ctxt->cursor_slot[PAUSE_ITEM];

        if (pause_ctxt->cursor_special_pos == 0) {
            pause_ctxt->cursor_color_set = 4;

            if (cursor_item == PAUSE_ITEM_NONE) {
                pause_ctxt->stick_movement_x = 40;
            }

            // Code for ensuring an empty deku stick slot isn't selected when entering the screen for the first time
            // has been removed for randomizer. It's a valid position for the cursor to start and empty slots can't equip
            // items so there is no need for this.

            if (ABS(pause_ctxt->stick_movement_x) > 30) {
                cursor_point = pause_ctxt->cursor_point[PAUSE_ITEM];
                cursor_x = pause_ctxt->cursor_x[PAUSE_ITEM];
                cursor_y = pause_ctxt->cursor_y[PAUSE_ITEM];

                while (move_cursor_result == 0) {
                    // From the current position, checks the columns to the left until it finds an item, or reaches the far left.
                    // Then it checks the leftmost column down, then loops back to the top until it reaches the same Y position
                    // again. At this point no more items could be found, so it changes `cursor_special_pos` to the left screen
                    // change cursor.
                    if (pause_ctxt->stick_movement_x < -30) {
                        if (pause_ctxt->cursor_x[PAUSE_ITEM] != 0) {
                            pause_ctxt->cursor_x[PAUSE_ITEM]--;
                            pause_ctxt->cursor_point[PAUSE_ITEM] -= 1;

                            // Randomizer needs X navigation to be unlimited to avoid impossible menu configurations
                            move_cursor_result = 1;
                        } else {
                            pause_ctxt->cursor_x[PAUSE_ITEM] = cursor_x;
                            pause_ctxt->cursor_y[PAUSE_ITEM]++;

                            if (pause_ctxt->cursor_y[PAUSE_ITEM] >= 4) {
                                pause_ctxt->cursor_y[PAUSE_ITEM] = 0;
                            }

                            pause_ctxt->cursor_point[PAUSE_ITEM] =
                                    pause_ctxt->cursor_x[PAUSE_ITEM] + (pause_ctxt->cursor_y[PAUSE_ITEM] * 6);

                            if (pause_ctxt->cursor_point[PAUSE_ITEM] >= 24) {
                                pause_ctxt->cursor_point[PAUSE_ITEM] = pause_ctxt->cursor_x[PAUSE_ITEM];
                            }

                            // No item found
                            if (cursor_y == pause_ctxt->cursor_y[PAUSE_ITEM]) {
                                pause_ctxt->cursor_x[PAUSE_ITEM] = cursor_x;
                                pause_ctxt->cursor_point[PAUSE_ITEM] = cursor_point;

                                KaleidoScope_MoveCursorToSpecialPos(play, PAUSE_CURSOR_PAGE_LEFT);

                                move_cursor_result = 2;
                            }
                        }
                    } else if (pause_ctxt->stick_movement_x > 30) {
                        // This does the same thing, but checks the columns to the right and sets the `cursor_special_pos`
                        // the right screen change cursor.
                        if (pause_ctxt->cursor_x[PAUSE_ITEM] < 5) {
                            pause_ctxt->cursor_x[PAUSE_ITEM]++;
                            pause_ctxt->cursor_point[PAUSE_ITEM] += 1;

                            // Randomizer needs X navigation to be unlimited to avoid impossible menu configurations
                            move_cursor_result = 1;
                        } else {
                            pause_ctxt->cursor_x[PAUSE_ITEM] = cursor_x;
                            pause_ctxt->cursor_y[PAUSE_ITEM]++;

                            if (pause_ctxt->cursor_y[PAUSE_ITEM] >= 4) {
                                pause_ctxt->cursor_y[PAUSE_ITEM] = 0;
                            }

                            pause_ctxt->cursor_point[PAUSE_ITEM] =
                                    pause_ctxt->cursor_x[PAUSE_ITEM] + (pause_ctxt->cursor_y[PAUSE_ITEM] * 6);

                            if (pause_ctxt->cursor_point[PAUSE_ITEM] >= 24) {
                                pause_ctxt->cursor_point[PAUSE_ITEM] = pause_ctxt->cursor_x[PAUSE_ITEM];
                            }

                            // No item found
                            if (cursor_y == pause_ctxt->cursor_y[PAUSE_ITEM]) {
                                pause_ctxt->cursor_x[PAUSE_ITEM] = cursor_x;
                                pause_ctxt->cursor_point[PAUSE_ITEM] = cursor_point;

                                KaleidoScope_MoveCursorToSpecialPos(play, PAUSE_CURSOR_PAGE_RIGHT);

                                move_cursor_result = 2;
                            }
                        }
                    }
                }

                // Updates the inventory item pointed to if an item was found. Otherwise, it retains a now stale value.
                if (move_cursor_result == 1) {
                    cursor_item = z64_file.items[pause_ctxt->cursor_point[PAUSE_ITEM]];
                }
            }
        } else if (pause_ctxt->cursor_special_pos == PAUSE_CURSOR_PAGE_LEFT) {
            // On Page Left special position going Right
            if (pause_ctxt->stick_movement_x > 30) {
                pause_ctxt->name_display_timer = 0;
                pause_ctxt->cursor_special_pos = 0;

                z64_Audio_PlaySoundGeneral(NA_SE_SY_CURSOR, &z64_SfxDefaultPos, 4, &z64_SfxDefaultFreqAndVolScale,
                                     &z64_SfxDefaultFreqAndVolScale, &z64_SfxDefaultReverb);

                cursor_point = cursor_x = cursor_y = 0;
                while (1) {
                    // Searches for an item. Checks top to bottom one column at a time. If it finds one it tries to reset
                    // state, but it forgets to unset cursor_item so the stale item remains when you switch back
                    // to this screen.
                    if (z64_file.items[cursor_point] != ITEM_NONE) {
                        pause_ctxt->cursor_point[PAUSE_ITEM] = cursor_point;
                        pause_ctxt->cursor_x[PAUSE_ITEM] = cursor_x;
                        pause_ctxt->cursor_y[PAUSE_ITEM] = cursor_y;
                        move_cursor_result = 1;
                        break;
                    }

                    cursor_y = cursor_y + 1;
                    cursor_point = cursor_point + 6;
                    if (cursor_y < 4) {
                        continue;
                    }

                    cursor_y = 0;
                    cursor_point = cursor_x + 1;
                    cursor_x = cursor_point;
                    if (cursor_x < 6) {
                        continue;
                    }

                    // There were no items on the screen, switch to the other special pos.
                    KaleidoScope_MoveCursorToSpecialPos(play, PAUSE_CURSOR_PAGE_RIGHT);
                    break;
                }
            }
        } else {
            // On Page Right special position going Left
            if (pause_ctxt->stick_movement_x < -30) {
                pause_ctxt->name_display_timer = 0;
                pause_ctxt->cursor_special_pos = 0;

                z64_Audio_PlaySoundGeneral(NA_SE_SY_CURSOR, &z64_SfxDefaultPos, 4, &z64_SfxDefaultFreqAndVolScale,
                                           &z64_SfxDefaultFreqAndVolScale, &z64_SfxDefaultReverb);

                cursor_point = cursor_x = 5;
                cursor_y = 0;
                while (1) {
                    // Searches for an item. Checks top to bottom one column at a time. If it finds one it tries to reset
                    // state, but it forgets to unset cursor_item so the stale item remains when you switch back
                    // to this screen.
                    if (z64_file.items[cursor_point] != ITEM_NONE) {
                        pause_ctxt->cursor_point[PAUSE_ITEM] = cursor_point;
                        pause_ctxt->cursor_x[PAUSE_ITEM] = cursor_x;
                        pause_ctxt->cursor_y[PAUSE_ITEM] = cursor_y;
                        move_cursor_result = 1;
                        break;
                    }

                    cursor_y = cursor_y + 1;
                    cursor_point = cursor_point + 6;
                    if (cursor_y < 4) {
                        continue;
                    }

                    cursor_y = 0;
                    cursor_point = cursor_x - 1;
                    cursor_x = cursor_point;
                    if (cursor_x >= 0) {
                        continue;
                    }

                    // There were no items on the screen, switch to the other special pos.
                    KaleidoScope_MoveCursorToSpecialPos(play, PAUSE_CURSOR_PAGE_LEFT);
                    break;
                }
            }
        }

        if (pause_ctxt->cursor_special_pos == 0) { // Now we handle vertical input
            if (cursor_item != PAUSE_ITEM_NONE) { // When we're not trying to move off of a page cursor. (if we've gone
                                                 // through this loop at least once since the screen rotated back to this
                                                 // screen)
                if (ABS(pause_ctxt->stick_movement_y) > 30) {
                    cursor_point = pause_ctxt->cursor_point[PAUSE_ITEM];
                    cursor_y = pause_ctxt->cursor_y[PAUSE_ITEM];
                    move_cursor_result = 0;

                    while (move_cursor_result == 0) {
                        if (pause_ctxt->stick_movement_y > 30) {
                            if (pause_ctxt->cursor_y[PAUSE_ITEM] != 0) {
                                pause_ctxt->cursor_y[PAUSE_ITEM]--;
                                pause_ctxt->cursor_point[PAUSE_ITEM] -= 6;

                                if(z64_file.items[pause_ctxt->cursor_point[PAUSE_ITEM]] != ITEM_NONE
                                   || pause_ctxt->cursor_x[PAUSE_ITEM] > 0 && pause_ctxt->cursor_x[PAUSE_ITEM] < 5) {
                                    move_cursor_result = 1;
                                }
                            } else { // Nothing fancy if we've reached the vertical bounds.
                                pause_ctxt->cursor_y[PAUSE_ITEM] = cursor_y;
                                pause_ctxt->cursor_point[PAUSE_ITEM] = cursor_point;

                                move_cursor_result = 2;
                            }
                        } else if (pause_ctxt->stick_movement_y < -30) {
                            if (pause_ctxt->cursor_y[PAUSE_ITEM] < 3) {
                                pause_ctxt->cursor_y[PAUSE_ITEM]++;
                                pause_ctxt->cursor_point[PAUSE_ITEM] += 6;

                                if(z64_file.items[pause_ctxt->cursor_point[PAUSE_ITEM]] != ITEM_NONE
                                   || pause_ctxt->cursor_x[PAUSE_ITEM] > 0 && pause_ctxt->cursor_x[PAUSE_ITEM] < 5) {
                                    move_cursor_result = 1;
                                }
                            } else { // Nothing fancy if we've reached the vertical bounds.
                                pause_ctxt->cursor_y[PAUSE_ITEM] = cursor_y;
                                pause_ctxt->cursor_point[PAUSE_ITEM] = cursor_point;

                                move_cursor_result = 2;
                            }
                        }
                    }
                }
            }

            cursor_slot = pause_ctxt->cursor_point[PAUSE_ITEM];

            pause_ctxt->cursor_color_set = 4;

            // Update the item the cursor is pointing to if you have made a valid menu move. If you have not enjoy quick swap
            if (move_cursor_result == 1) {
                cursor_item = z64_file.items[pause_ctxt->cursor_point[PAUSE_ITEM]];
            } else if (move_cursor_result != 2) {
                cursor_item = z64_file.items[pause_ctxt->cursor_point[PAUSE_ITEM]];
            }

            pause_ctxt->cursor_item[PAUSE_ITEM] = cursor_item;
            pause_ctxt->cursor_slot[PAUSE_ITEM] = cursor_slot;

            // Darken the name of the item if current age can't equip it
            // Randomizer also checks to see if the item under the cursor has been obtained. Setting name color to 1 is
            // a quick hack to prevent the name texture from switching to the equip textures, and an item you haven't
            // obtained yet doesn't display any name at all so the info display stays blank. Essentially a port of wulfy83's
            // ASM hack that did this same thing to the original kaleido_item.
            if (!CHECK_AGE_REQ_SLOT(cursor_slot) || cursor_item == ITEM_NONE) {
                pause_ctxt->name_color_set = 1;
            }

            // Are not on one of the special positions, or have not finished this control loop once yet.
            if (cursor_item != PAUSE_ITEM_NONE) {
                index = cursor_slot * 4;
                KaleidoScope_SetCursorVtx(pause_ctxt, index, pause_ctxt->item_vtx);

                if ((pause_ctxt->debugState == 0) && (pause_ctxt->state == PAUSE_STATE_MAIN) &&
                    (pause_ctxt->changing == PAUSE_MAIN_STATE_IDLE)) {
                    if (input->pad_pressed.cl || input->pad_pressed.cd || input->pad_pressed.cr) {
                        if (CHECK_AGE_REQ_SLOT(cursor_slot) && (cursor_item != ITEM_SOLD_OUT)
                            && cursor_item != ITEM_NONE) {
                            if (input->pad_pressed.cl) {
                                pause_ctxt->equip_target_c_btn = 0;
                            } else if (input->pad_pressed.cd) {
                                pause_ctxt->equip_target_c_btn = 1;
                            } else if (input->pad_pressed.cr) {
                                pause_ctxt->equip_target_c_btn = 2;
                            }

                            pause_ctxt->equip_target_item = cursor_item;
                            pause_ctxt->equip_target_slot = cursor_slot;
                            pause_ctxt->changing = PAUSE_MAIN_STATE_3;
                            pause_ctxt->equip_anim_x = pause_ctxt->item_vtx[index].v.ob[0] * 10;
                            pause_ctxt->equip_anim_y = pause_ctxt->item_vtx[index].v.ob[1] * 10;
                            pause_ctxt->equip_anim_alpha = 255;
                            z64_sEquipAnimTimer = 0;
                            z64_sEquipState = 3;
                            z64_sEquipMoveTimer = 10;
                            if ((pause_ctxt->equip_target_item == ITEM_ARROW_FIRE) ||
                                (pause_ctxt->equip_target_item == ITEM_ARROW_ICE) ||
                                (pause_ctxt->equip_target_item == ITEM_ARROW_LIGHT)) {
                                index = 0;
                                if (pause_ctxt->equip_target_item == ITEM_ARROW_ICE) {
                                    index = 1;
                                }
                                if (pause_ctxt->equip_target_item == ITEM_ARROW_LIGHT) {
                                    index = 2;
                                }
                                z64_Audio_PlaySoundGeneral(NA_SE_SY_SET_FIRE_ARROW + index, &z64_SfxDefaultPos, 4,
                                                     &z64_SfxDefaultFreqAndVolScale, &z64_SfxDefaultFreqAndVolScale,
                                                     &z64_SfxDefaultReverb);
                                pause_ctxt->equip_target_item = 0xBF + index;
                                z64_sEquipState = 0;
                                pause_ctxt->equip_anim_alpha = 0;
                                z64_sEquipMoveTimer = 6;
                            } else {
                                z64_Audio_PlaySoundGeneral(NA_SE_SY_DECIDE, &z64_SfxDefaultPos, 4, &z64_SfxDefaultFreqAndVolScale,
                                                     &z64_SfxDefaultFreqAndVolScale, &z64_SfxDefaultReverb);
                            }
                        } else {
                            z64_Audio_PlaySoundGeneral(NA_SE_SY_ERROR, &z64_SfxDefaultPos, 4, &z64_SfxDefaultFreqAndVolScale,
                                                 &z64_SfxDefaultFreqAndVolScale, &z64_SfxDefaultReverb);
                        }
                    }
                }
            } else {
                pause_ctxt->cursor_vtx[0].v.ob[0] = pause_ctxt->cursor_vtx[2].v.ob[0] = pause_ctxt->cursor_vtx[1].v.ob[0] =
                pause_ctxt->cursor_vtx[3].v.ob[0] = 0;

                pause_ctxt->cursor_vtx[0].v.ob[1] = pause_ctxt->cursor_vtx[1].v.ob[1] = pause_ctxt->cursor_vtx[2].v.ob[1] =
                pause_ctxt->cursor_vtx[3].v.ob[1] = -200;
            }
        } else {
            pause_ctxt->cursor_item[PAUSE_ITEM] = PAUSE_ITEM_NONE;
        }

        if (old_cursor_point != pause_ctxt->cursor_point[PAUSE_ITEM]) {
            z64_Audio_PlaySoundGeneral(NA_SE_SY_CURSOR, &z64_SfxDefaultPos, 4, &z64_SfxDefaultFreqAndVolScale,
                                 &z64_SfxDefaultFreqAndVolScale, &z64_SfxDefaultReverb);
        }
    } else if ((pause_ctxt->changing == PAUSE_MAIN_STATE_3) && (pause_ctxt->screen_idx == PAUSE_ITEM)) {
        KaleidoScope_SetCursorVtx(pause_ctxt, cursor_slot * 4, pause_ctxt->item_vtx);
        pause_ctxt->cursor_color_set = 4;
    }


    gDPSetCombineLERP(OVERLAY_DISP++, PRIMITIVE, ENVIRONMENT, TEXEL0, ENVIRONMENT, TEXEL0, 0, PRIMITIVE, 0, PRIMITIVE,
                      ENVIRONMENT, TEXEL0, ENVIRONMENT, TEXEL0, 0, PRIMITIVE, 0);
    gDPSetPrimColor(POLY_OPA_DISP++, 0, 0, 255, 255, 255, pause_ctxt->alpha);
    gDPSetEnvColor(POLY_OPA_DISP++, 0, 0, 0, 0);

    // Draw outline around equipped items
    for (i = 0, j = 24 * 4; i < 3; i++, j += 4) {
        if (z64_file.button_items[i + 1] != ITEM_NONE) {
            gSPVertex(POLY_OPA_DISP++, &pause_ctxt->item_vtx[j], 4, 0);
            POLY_OPA_DISP = KaleidoScope_QuadTextureIA8(POLY_OPA_DISP, z64_EquippedItemOutlineTex, 32, 32, 0);
        }
    }

    gDPPipeSync(POLY_OPA_DISP++);
    gDPSetCombineMode(POLY_OPA_DISP++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);

    // Draw the item icons in the menu
    for (i = j = 0; i < 24; i++, j += 4) {
        gDPSetPrimColor(POLY_OPA_DISP++, 0, 0, 255, 255, 255, pause_ctxt->alpha);

        if (z64_file.items[i] != ITEM_NONE) { // Only if you've obtained it
            if ((pause_ctxt->changing == PAUSE_MAIN_STATE_IDLE) && (pause_ctxt->screen_idx == PAUSE_ITEM) &&
                (pause_ctxt->cursor_special_pos == 0)) { // Cursor is over an item
                if (CHECK_AGE_REQ_SLOT(i)) { // Item can be equipped as current age
                    // In vanilla there is code here that is supposed to tint the bow icon when equipping magic arrows
                    // however it either doesn't work, or is only visible for a frame so has been removed from here.
                    if (i == cursor_slot) { // Draw the item the cursor is over slightly larger
                        pause_ctxt->item_vtx[j + 0].v.ob[0] = pause_ctxt->item_vtx[j + 2].v.ob[0] =
                                pause_ctxt->item_vtx[j + 0].v.ob[0] - 2;

                        pause_ctxt->item_vtx[j + 1].v.ob[0] = pause_ctxt->item_vtx[j + 3].v.ob[0] =
                                pause_ctxt->item_vtx[j + 0].v.ob[0] + 32;

                        pause_ctxt->item_vtx[j + 0].v.ob[1] = pause_ctxt->item_vtx[j + 1].v.ob[1] =
                                pause_ctxt->item_vtx[j + 0].v.ob[1] + 2;

                        pause_ctxt->item_vtx[j + 2].v.ob[1] = pause_ctxt->item_vtx[j + 3].v.ob[1] =
                                pause_ctxt->item_vtx[j + 0].v.ob[1] - 32;
                    }
                }
            }

            gSPVertex(POLY_OPA_DISP++, &pause_ctxt->item_vtx[j + 0], 4, 0);
            KaleidoScope_DrawQuadTextureRGBA32(play->common.gfx,
                                               z64_ItemIcons[z64_file.items[i]], ITEM_ICON_WIDTH,
                                               ITEM_ICON_HEIGHT, 0);
        }
    }

    if (pause_ctxt->cursor_special_pos == 0) {
        KaleidoScope_DrawCursor(play, PAUSE_ITEM);
    }

    gDPPipeSync(POLY_OPA_DISP++);
    gDPSetCombineLERP(POLY_OPA_DISP++, PRIMITIVE, ENVIRONMENT, TEXEL0, ENVIRONMENT, TEXEL0, 0, PRIMITIVE, 0, PRIMITIVE,
                      ENVIRONMENT, TEXEL0, ENVIRONMENT, TEXEL0, 0, PRIMITIVE, 0);

    // Draw the current ammo amounts
    for (i = 0; i < 15; i++) {
        if ((z64_AmmoItems[i] != ITEM_NONE) && (z64_file.items[i] != ITEM_NONE)) {
            KaleidoScope_DrawAmmoCount(pause_ctxt, play->common.gfx, z64_file.items[i]);
        }
    }

    CLOSE_DISPS(play->common.gfx);
}
