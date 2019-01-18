#ifndef ICETRAP_H
#define ICETRAP_H

#include "z64.h"

void push_pending_ice_trap();
void give_ice_trap();
_Bool ice_trap_is_pending();

#endif
