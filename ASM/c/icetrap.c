#include "icetrap.h"

#include "z64.h"

uint8_t pending_freezes = 0;
uint8_t satisified_ice_trap_frames = 0;

void push_pending_ice_trap() {
    pending_freezes++;
}

uint32_t ice_trap_is_pending() {
    return pending_freezes > 0;
}

inline uint32_t ice_trap_allowed() {
    if ((z64_link.state_flags_1 & 0xFCAC2485) == 0 &&
        (z64_link.common.unk_flags_00 & 0x0001) &&
        (z64_link.state_flags_2 & 0x000C0000) == 0 &&
        (z64_event_state_1 & 0x20) == 0)   {
        satisified_ice_trap_frames++;
    }
    else {
        satisified_ice_trap_frames = 0;
    }
    if (satisified_ice_trap_frames >= 2) {
        satisified_ice_trap_frames = 0;
        return 1;
    }
    return 0;
}

void try_ice_trap() {
    if (pending_freezes && ice_trap_allowed()) {
        pending_freezes--;
        z64_LinkInvincibility(&z64_link, 0x14);
        z64_LinkDamage(&z64_game, &z64_link, 0x03, 0, 0, 0x14);
    }
}
