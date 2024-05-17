#include "z64.h"
#include "kaleido.h"

_Bool c_equipment_menu_slot_filled() {
    if (z64_game.pause_ctxt.cursor_x[PAUSE_EQUIP] == 0) {
        if (z64_game.pause_ctxt.cursor_y[PAUSE_EQUIP] == 0) {
            if (z64_file.link_age == 0 && (z64_file.bullet_bag || z64_file.quiver)) return 1;
            else return z64_file.bullet_bag;
        }
        return (z64_file.equipment_items >> (3 * z64_game.pause_ctxt.cursor_y[PAUSE_EQUIP])) & 0x07;
    }
    if (z64_game.pause_ctxt.cursor_y[PAUSE_EQUIP] == 0) {
        if (z64_game.pause_ctxt.cursor_x[PAUSE_EQUIP] != 3)  goto retnormal;
        return z64_file.broken_giants_knife || z64_file.giants_knife;
    }
retnormal:
    return (z64_file.equipment >> ((4 * z64_game.pause_ctxt.cursor_y[PAUSE_EQUIP]) + (z64_game.pause_ctxt.cursor_x[PAUSE_EQUIP] - 1))) & 0x01;
}
