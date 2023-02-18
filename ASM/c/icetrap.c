#include "icetrap.h"
#include "z64.h"

_Bool ice_trap_is_pending() {
    return z64_file.scene_flags[0x49].unk_00_ > 0; //Unused word in scene x49.
}

void push_pending_ice_trap() {
    z64_file.scene_flags[0x49].unk_00_++;
}

void give_ice_trap() {
    if (z64_file.scene_flags[0x49].unk_00_) {
        z64_file.scene_flags[0x49].unk_00_--;
        z64_LinkInvincibility(&z64_link, 0x14);
        z64_LinkDamage(&z64_game, &z64_link, 0x03, 0, 0, 0x14);
    }
}
