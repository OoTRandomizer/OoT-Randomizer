#include "bombchu_bowling.h"
#include "z64.h"

extern uint32_t FREE_BOMBCHU_DROPS;
uint32_t EXTRA_BOWLING_SHUFFLE = 0;

/*
    Only the vanilla bomb bag and heart piece have flags tied to them.
    This function uses chu bowling scene flags instead of the vanilla
    inf_table flags to determine if a prize has already been obtained,
    and extends it to the other bowling prizes (1 bomb or 10 bombchus).
    Once exhausted, the reward becomes a purple rupee. The vanilla
    purple rupee reward remains unshuffled to provide a repeatable prize,
    but it could be shuffled if the exhausted prize were changed to an
    unshuffled item for the scene. This requires expanding the prize
    selection array size in en_bom_bowl_man and en_bom_bowl_pit.
*/

int16_t select_bombchu_bowling_prize(int16_t prizeSelect) {
    int16_t prizeTemp;

    uint32_t prizeFlag = (1 << prizeSelect);

    if (!(z64_file.scene_flags[0x4B].unk_00_ & prizeFlag)) {
        switch(prizeSelect) {
            case 0:
                prizeTemp = EXITEM_BOMB_BAG_BOWLING;
                break;
            case 1:
                prizeTemp = EXITEM_HEART_PIECE_BOWLING;
                break;
            case 2:
                // Default prize is renewable bombchus. If a shuffled
                // Bombchu Bag has not been found, override to the 1
                // Bomb prize if bomb bag is found, else the purple
                // rupee prize.
                if (!EXTRA_BOWLING_SHUFFLE && z64_file.items[Z64_SLOT_BOMBCHU] == ITEM_NONE && FREE_BOMBCHU_DROPS) {
                    prizeTemp = z64_file.bomb_bag ? EXITEM_BOMBS_BOWLING : EXITEM_PURPLE_RUPEE_BOWLING;
                } else {
                    prizeTemp = EXITEM_BOMBCHUS_BOWLING;
                }
                break;
            case 3:
                // Prevent giving the player a bomb if a bomb bag has not
                // been found yet.
                if (!EXTRA_BOWLING_SHUFFLE && !z64_file.bomb_bag) {
                    prizeTemp = EXITEM_PURPLE_RUPEE_BOWLING;
                } else {
                    prizeTemp = EXITEM_BOMBS_BOWLING;
                }
                break;
            case 4:
                // Kept here in case this is shuffled in the future,
                // currently functionally redundant when the flag is set.
                prizeTemp = EXITEM_PURPLE_RUPEE_BOWLING;
                break;
        }
    } else {
        // maintain renewable bombchus/bombs if extra shuffle is disabled
        if (!EXTRA_BOWLING_SHUFFLE) {
            switch(prizeSelect) {
                case 2:
                    if (z64_file.items[Z64_SLOT_BOMBCHU] == ITEM_NONE && FREE_BOMBCHU_DROPS) {
                        prizeTemp = z64_file.bomb_bag ? EXITEM_BOMBS_BOWLING : EXITEM_PURPLE_RUPEE_BOWLING;
                    } else {
                        prizeTemp = EXITEM_BOMBCHUS_BOWLING;
                    }
                    break;
                case 3:
                    if (!z64_file.bomb_bag) {
                        prizeTemp = EXITEM_PURPLE_RUPEE_BOWLING;
                    } else {
                        prizeTemp = EXITEM_BOMBS_BOWLING;
                    }
                    break;
                default:
                    prizeTemp = EXITEM_PURPLE_RUPEE_BOWLING;
                    break;
            }
        } else {
            prizeTemp = EXITEM_PURPLE_RUPEE_BOWLING;
        }
    }

    return prizeTemp;
}

void set_bombchu_bowling_prize_flag(int16_t prizeIndex) {
    // swap the purple rupee with the replacement item if
    // the purple rupee prize is ever shuffled
    if (prizeIndex != EXITEM_PURPLE_RUPEE_BOWLING ||
            (!EXTRA_BOWLING_SHUFFLE && prizeIndex <= EXITEM_HEART_PIECE_BOWLING)) {
        z64_file.scene_flags[0x4B].unk_00_ |= (1 << prizeIndex);
    }
}
