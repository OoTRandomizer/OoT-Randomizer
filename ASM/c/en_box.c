#include "z64.h"
#include "chests.h"
#include "object.h"
#include "get_items.h"
#include "debug.h"

// Macro for original get item id + if opened or not
#define ENBOX_GET_GET_ITEM_ID(thisx) ((thisx).variable >> 5) & ((1 << 7) - 1)
#define ENBOX_GET_TREASURE_FLAG(thisx) ((thisx).variable >> 0) & ((1 << 5) - 1)

#define OBJECT_FZ 0x114

// Get this chest's new randomized GI id
int16_t EnBox_GetNewGetItemId(EnBox* this, z64_game_t* play) {
    int16_t oldId = ENBOX_GET_GET_ITEM_ID(this->dyna.actor);
    override_t override = lookup_override(&this->dyna.actor, z64_game.scene_index, ABS(oldId));

    return override.value.base.item_id;
}

// Load the necessary extra object if new GI id is a trap
void EnBox_LoadObject(EnBox* this, z64_game_t* play) {
    int16_t giId = EnBox_GetNewGetItemId(this, play);
    bool opened = Flags_GetTreasure(play, ENBOX_GET_TREASURE_FLAG(this->dyna.actor));

    if(!opened) {
        if (giId == GI_ICE_TRAP) {
            Object_LoadExtra(play, OBJECT_FZ, 0);  // Freezard object
        }
    }
}
