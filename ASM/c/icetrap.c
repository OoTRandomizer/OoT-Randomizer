#include "icetrap.h"
#include "z64.h"

uint8_t pending_freezes = 0;

_Bool ice_trap_is_pending() {
    return pending_freezes > 0;
}

void push_pending_ice_trap() {
    pending_freezes++;
}
void give_ice_trap() {
    if (pending_freezes) {
        pending_freezes--;
        z64_LinkInvincibility(&z64_link, 0x14);
        z64_LinkDamage(&z64_game, &z64_link, 0x03, 0, 0, 0x14);
    }
}
