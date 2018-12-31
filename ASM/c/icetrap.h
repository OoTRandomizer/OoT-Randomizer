#ifndef ICETRAP_H
#define ICETRAP_H

#include "z64.h"

uint32_t ice_trap_is_pending();
void push_pending_ice_trap();
void try_ice_trap();

#endif
