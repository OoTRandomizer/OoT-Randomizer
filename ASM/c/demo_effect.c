#include "z64.h"
#include "util.h"
#include "demo_effect.h"
#include "models.h"

extern void DemoEffect_DrawJewel(DemoEffect* this, z64_game_t* globalCtx, void* func);
extern void* DemoEffect_DrawJewel_AfterHook;

extern override_key_t CFG_BIGOCTO_OVERRIDE_KEY;

// Overrides the item model for the dungeon reward shown before the Big Octo fight
void DemoEffect_DrawJewel_Hook(DemoEffect* this, z64_game_t* globalCtx) {
    if (!this->override_initialized) {
        if (globalCtx->scene_index == 0x02) {
            if (CFG_BIGOCTO_OVERRIDE_KEY.all) {
                this->override = lookup_override_by_key(CFG_BIGOCTO_OVERRIDE_KEY);
            }
            if (this->override.key.all) {
                this->actor.rot_2.x = 0;
                this->actor.scale = (z64_xyzf_t) { 0.02f, 0.02f, 0.02f };
            }
        }

        this->override_initialized = true;
    }
    if (this->override.key.all) {
        model_t model;
        lookup_model_by_override(&model, this->override);
        draw_model(model, &this->actor, globalCtx, 5.0);
    } else {
        DemoEffect_DrawJewel(this, globalCtx, resolve_overlay_addr(&DemoEffect_DrawJewel_AfterHook, 0x008B));
    }
}
