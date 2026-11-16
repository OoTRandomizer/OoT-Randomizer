#include "z64.h"
#include "door_of_time.h"
#include "en_okarina_tag.h"
#include "util.h"

extern EnOkarinaTagActionFunc OVL_EnOkarinaTag_Action1;
extern EnOkarinaTagActionFunc OVL_EnOkarinaTag_Action2;

void EnOkarinaTag_ActionHook(EnOkarinaTag* this, z64_game_t* play) {
    if (play->msgContext.ocarinaMode == 3 && this->type == 4 && !has_items_for_door_of_time()) {
        play->msgContext.ocarinaMode = 4;
        this->actionFunc = resolve_overlay_addr(&OVL_EnOkarinaTag_Action1, this->actor.actor_id);
        return;
    }
    EnOkarinaTagActionFunc EnOkarinaTag_Action = resolve_overlay_addr(&OVL_EnOkarinaTag_Action2, this->actor.actor_id);
    EnOkarinaTag_Action(this, play);
}
