#include "z64.h"
#include "player.h"

extern uint16_t QuestHint_GetNaviTextId(z64_game_t* play);
extern uint8_t CFG_ENABLE_NAVI_BELL;

// Flags are set no matter settings, but this is only run if bell is enabled
void Player_UseNaviBell(z64_game_t* play, z64_link_t* this) {
    uint16_t textId = QuestHint_GetNaviTextId(play);

    // Don't use if no text available
    if (textId == 0 || textId == 0x15f) {
        return;

    } else if (this->focusActor == NULL && this->navi_actor != NULL) {
        this->naviTextId = textId;
        z64_file.navi_timer = 600;
    }
}

// Using an item that should not go through the usual UseItem pathway
void Player_UseItemCustom(z64_game_t* play, z64_link_t* this, int32_t item) {
    if (CFG_ENABLE_NAVI_BELL && item == ITEM_NAVI_BELL) {
        Player_UseNaviBell(play, this);
    } else {
        Player_UseItem(play, this, item);
    }
}
