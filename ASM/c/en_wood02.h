#ifndef EN_WOOD02_H
#define EN_WOOD02_H

#include "actor.h"

#define EN_WOOD02 0x0077

xflag_t EnWood02_NormalizeFlag(xflag_t flag);

void EnWood02_AfterInitHack(z64_actor_t* actor, z64_game_t* game);

#endif
