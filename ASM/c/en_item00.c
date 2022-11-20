#include "get_items.h"

void EnItem00_Init_Hack(EnItem00* this, z64_game_t* game){
    this->override = lookup_override(this, game->scene_index,0);
    if(Get_CollectibleOverrideFlag(this))
        this->override = (override_t) { 0 };
}