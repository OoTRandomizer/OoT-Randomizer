#include "ovl_en_torch.h"
#include "grotto.h"
#include "item_table.h"

static uint8_t sChestContents[] = {
    GI_RUPEE_BLUE, GI_RUPEE_RED, GI_RUPEE_GOLD, GI_BOMBS_20, GI_BOMBS_1, GI_BOMBS_1, GI_BOMBS_1, GI_BOMBS_1,
};

void EnTorch_Init(z64_actor_t* thisx, z64_game_t* play) {
    EnTorch* this = (EnTorch*)thisx;
    int8_t returnData = gGrottoTable[CURRENT_GROTTO_ID].content_id;

    /* Spawn chest with desired contents.
       Contents are passed to en_torch from grotto params via rando's grotto
       table keyed on entrance index. */
    z64_SpawnActor(&play->actor_ctxt, play, ACTOR_EN_BOX, this->actor.pos_world.x, this->actor.pos_world.y,
                this->actor.pos_world.z, 0, this->actor.rot_2.y, 0,
                (sChestContents[(returnData >> 0x5) & 0x7] << 0x5) | 0x5000 | (returnData & 0x1F));

    z64_ActorKill(&this->actor);
}
