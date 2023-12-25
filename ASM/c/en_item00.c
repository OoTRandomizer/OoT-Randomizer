#include "z64.h"
#include "en_item00.h"
#include "get_items.h"

// EnItem00 Action Function used for sending outgoing junk overrides collected from enitem00 collectibles
void EnItem00_OutgoingAction(EnItem00* this, z64_game_t* globalCtx) {
    z64_link_t* player = &z64_link;

    if (this->timeToLive == 0) {
        z64_ActorKill(&this->actor);
        return;
    }

    this->actor.pos_world = player->common.pos_world;

    this->actor.rot_2.y += 960;

    this->actor.pos_world.y += 40.0f + (15 - this->timeToLive) * 5.0;

    if (LINK_IS_ADULT) {
        this->actor.pos_world.y += 20.0f;
    }
}

// Hack to EnItem00_Update when it is checking if the player is in proximity to give the item.
// With silver rupee shuffle, silver rupees actors (En_G_Switch) are replaced by En_Item00 actors.
// These actors perform their proximity checks slightly different from one another.
// This function checks whether or not the EnItem00 is a hacked silver rupee and performs the appropriate proximity check.
// Returns true if the player is within proximity to collect the item.
bool EnItem00_ProximityCheck_Hack(EnItem00* this, z64_game_t* GlobalCtx) {
    if (this->is_silver_rupee) {
        if (this->actor.distsq_from_link <= 900.0) {
            return true;
        }
    } else {
        if (this->actor.xzdist_from_link <= 30.0f && this->actor.ydist_from_link >= -50.0f && this->actor.ydist_from_link <= 50.0f) {
            return true;
        }
    }
    return false;
}
