#include <stdint.h>
#include "z64.h"
#include "en_wonderitem.h"
#include "get_items.h"
#include "actor.h"
#include "scene.h"

static colorRGBA8_t sEffectPrimColorRed = { 255, 0, 0, 0 };
static colorRGBA8_t sEffectPrimColorGreen = { 0, 255, 0, 0 };
static colorRGBA8_t sEffectPrimColorBlue = { 0, 0, 255, 0 };
static colorRGBA8_t sEffectPrimColorYellow = { 255, 255, 0, 0 };
static colorRGBA8_t sEffectPrimColoMagenta = { 255, 0, 255, 0 };
static colorRGBA8_t sEffectPrimColorCyan = {0, 255, 255, 0 };
static colorRGBA8_t sEffectEnvColor = { 255, 255, 255, 0 };
//static z64_xyzf_t sEffectVelocity = { 0.0f, 0.1f, 0.0f };
//static z64_xyzf_t sEffectAccel = { 0.0f, 0.01f, 0.0f };
static z64_xyzf_t sEffectVelocity = { 0.0f, 0.5f, 0.0f };
static z64_xyzf_t sEffectAccel = { 0.0f, 0.5f, 0.0f };

extern uint16_t CURR_ACTOR_SPAWN_INDEX;

void EnWonderitem_AfterInitHack(z64_actor_t* this, z64_game_t* globalCtx) {
    if (this->main_proc == NULL) return;
    if (this->actor_id != 0x112) return;

    EnWonderItem* wonderitem = (EnWonderItem*)this;
    wonderitem->overridden = 0;

    xflag_t flag = Actor_GetAdditionalData(this)->flag;

    // Check if the Wonderitem should be overridden
    if (flag.all && !Get_NewFlag(&flag)) {
        wonderitem->overridden = 1;
    }
}

void EnWonderItem_Multitag_DrawHack(z64_xyzf_t* tags, uint32_t index, EnWonderItem* this) {
    if (this->overridden) {
        colorRGBA8_t* color = &sEffectPrimColorBlue;
        if (this->wonderMode == WONDERITEM_MULTITAG_ORDERED) {
            color = &sEffectPrimColorCyan;
        }
        z64_xyzf_t pos = tags[index];
        z64_EffectSsKiraKira_SpawnSmall(&z64_game, &pos, &sEffectVelocity, &sEffectAccel, color, &sEffectEnvColor);
    }
}

void EnWonderItem_DropCollectible_Hack(EnWonderItem* this, z64_game_t* globalCtx, int32_t autoCollect) {
    static int16_t dropTable[] = {
        ITEM00_NUTS,        ITEM00_HEART_PIECE,  ITEM00_MAGIC_LARGE,   ITEM00_MAGIC_SMALL,
        ITEM00_HEART,       ITEM00_ARROWS_SMALL, ITEM00_ARROWS_MEDIUM, ITEM00_ARROWS_LARGE,
        ITEM00_RUPEE_GREEN, ITEM00_RUPEE_BLUE,   ITEM00_RUPEE_RED,     ITEM00_FLEXIBLE,
    };
    int16_t i;
    int16_t randomDrop;

    // Always play the SFX
    z64_PlaySFXID(NA_SE_SY_GET_ITEM);

    // Override behavior. Spawn an overridden collectible on link
    if (this->overridden) {
        xflag_t* flag = &(Actor_GetAdditionalData(&this->actor)->flag);
        drop_collectible_override_flag = *flag;
        if(autoCollect) {
            z64_Item_DropCollectible2(globalCtx, &(z64_link.common.pos_world), 0);
        } else {
            z64_Item_DropCollectible(globalCtx, &this->actor.pos_world, 0);
        }
        z64_bzero(&drop_collectible_override_flag, sizeof(drop_collectible_override_flag));
        if (this->switchFlag >= 0) {
            z64_Flags_SetSwitch(globalCtx, this->switchFlag);
        }
        z64_ActorKill(&this->actor);
        return;
    }

    // Not overridden so use vanilla behavior
    if (this->dropCount == 0) {
        this->dropCount++;
    }
    for (i = this->dropCount; i > 0; i--) {
        if (this->itemDrop < WONDERITEM_DROP_RANDOM) {
            if ((this->itemDrop == WONDERITEM_DROP_FLEXIBLE) || !autoCollect) {
                z64_Item_DropCollectible(globalCtx, &this->actor.pos_world, dropTable[this->itemDrop]);
            } else {
                z64_Item_DropCollectible(globalCtx, &this->actor.pos_world, dropTable[this->itemDrop] | 0x8000);
            }
        } else {
            randomDrop = this->itemDrop - WONDERITEM_DROP_RANDOM;
            if (!autoCollect) {
                z64_Item_DropCollectibleRandom(globalCtx, NULL, &this->actor.pos_world, randomDrop);
            } else {
                z64_Item_DropCollectibleRandom(globalCtx, NULL, &this->actor.pos_world, randomDrop | 0x8000);
            }
        }
    }
    if (this->switchFlag >= 0) {
        z64_Flags_SetSwitch(globalCtx, this->switchFlag);
    }
    z64_ActorKill(&this->actor);
}

void EnWonderItem_Update_Hack(EnWonderItem* this) {
    colorRGBA8_t* color = NULL;
    if (this->overridden) {
        switch (this->wonderMode) {
            case WONDERITEM_PROXIMITY_DROP:
            {
                color = &sEffectPrimColorYellow;
                break;
            }
            case WONDERITEM_INTERACT_SWITCH:
            case WONDERITEM_BOMB_SOLDIER:
            {
                color = &sEffectPrimColorRed;
                break;
            }
            default: {
                break;
            }
        }
        if (color) {
            z64_EffectSsKiraKira_SpawnSmall(&z64_game, &(this->actor.pos_world), &sEffectVelocity, &sEffectAccel, color, &sEffectEnvColor);
        }
    }
}

// Hack to not kill wonderitem when switch flag is set if we need to override still
uint32_t EnWonderItem_Kill_Hack(EnWonderItem* this) {
    xflag_t flag = { 0 };
    flag.flag = CURR_ACTOR_SPAWN_INDEX;
    flag.scene = z64_game.scene_index;
    flag.room = this->actor.room_index;
    flag.setup = curr_scene_setup;

    // Check if the Wonderitem should be overridden
    override_t override = lookup_override_by_newflag(&flag);

    if (override.key.all != 0 && !Get_NewFlag(&flag)) return 0;
    if ((this->switchFlag >= 0) && z64_Flags_GetSwitch(&z64_game, this->switchFlag)) return 1;
    return 0;
}
