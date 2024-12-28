#include "z64.h"
#include "get_items.h"
#include "en_bb.h"
#include "actor.h"

static colorRGBA8_t sEffectPrimColor = { 255, 255, 127, 0 };
static colorRGBA8_t sEffectEnvColor = { 255, 255, 255, 0 };
static z64_xyzf_t sEffectVelocity = { 0.0f, 0.1f, 0.0f };
static z64_xyzf_t sEffectAccel = { 0.0f, 0.01f, 0.0f };

extern uint8_t ENEMY_DROP_SHUFFLE;

void bb_red_wait_hack(EnBb* bubble)
{
    if(ENEMY_DROP_SHUFFLE && bubble->overridden) {
        z64_xyzf_t pos;
        pos.x = bubble->actor.pos_init.x;
        pos.y = bubble->actor.pos_init.y + 150.0;
        pos.z = bubble->actor.pos_init.z;
        z64_EffectSsKiraKira_SpawnSmall(&z64_game, &pos, &sEffectVelocity, &sEffectAccel, &sEffectPrimColor, &sEffectEnvColor );
    }
}

void bb_after_init_hack(z64_actor_t* this, z64_game_t* globalCtx)
{
    if(this->actor_id != 0x0069)
        return;

    EnBb* bubble = (EnBb*)this;
    bubble->overridden = 0;
    if(ENEMY_DROP_SHUFFLE)
    {
        xflag_t flag = Actor_GetAdditionalData(this)->flag;
        if(flag.all && !(Get_NewFlag(&flag)))
        {
            bubble->overridden = 1;
        }
    }
}
