#include "z64.h"
#include "actor.h"
#include "minimap.h"
#include "gfx.h"

int16_t tempX;
int16_t tempZ;

uint8_t blank_texture[] = {255, 0, 0, 255};
extern uint8_t CFG_MINIMAP_ENEMY_TRACKER;

void MiniMap_Draw_Hack(z64_game_t* globalCtx)
{
    if(CFG_MINIMAP_ENEMY_TRACKER && !R_MINIMAP_DISABLED && globalCtx->pause_ctxt.state <= 3 && globalCtx->hud_alpha_channels.minimap >= 0xAA) {
        // Need to actually do all of the actor lists
        z64_actor_t* curr = globalCtx->actorLists[0x05].head;
        //int16_t tempX, tempZ;

        z64_disp_buf_t* db = &rando_overlay_db;
        gSPDisplayList(db->p++, 0x800F84A0); // Call setup DLIST 39 again
        gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
        gDPPipeSync(db->p++);
        gDPSetTextureLUT(db->p++, G_TT_NONE);
        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0x00, 0x00, 0xFF);

        int32_t rectLeft, rectTop;
        //int32_t minimap_center_x = 272;
        //int32_t minimap_center_z = 195;
        int32_t minimap_center_x = 160;
        int32_t minimap_center_z = 120;
        //int32_t minimap_center_x = 0;
        //int32_t minimap_center_z = 0;

        // Get the minimap scale/offset parameters. What if the room doesn't have a minimap, ex. grottos?
        uint16_t x_scale = *((uint16_t*)(0x801C6E90 + 0xF30));
        uint16_t y_scale = *((uint16_t*)(0x801C6E90 + 0xF32));
        int16_t x_compass_offset = *((uint16_t*)(0x801C6E90 + 0xF34));
        int16_t y_compass_offset = *((uint16_t*)(0x801C6E90 + 0xF36));
        int16_t x_offset = *((uint16_t*)(0x801C6E90 + 0xDCE));
        int16_t y_offset = *((uint16_t*)(0x801C6E90 + 0xDD0));
        //gSPTextureRectangle(db->p++, minimap_center_x << 2, minimap_center_z << 2, (minimap_center_x + 2) << 2,
        //                (minimap_center_z + 2) << 2, G_TX_RENDERTILE, 0, 0, 0, 0);

        // For some reason dungeon minimaps cause them not to draw?
        while(curr != NULL)
        {
            // Check if the actor has a newflag override (no because otherwise we would have to do this every frame).
            // Just check if the flag is set.
            if (Actor_GetAdditionalData(curr)->minimap_draw_flags & MINIMAP_FLAGS_DRAW)
            {
                tempX = ((int16_t)curr->pos_world.x);
                tempZ = ((int16_t)curr->pos_world.z);
                tempX /= R_COMPASS_SCALE_X;
                tempZ /= R_COMPASS_SCALE_Y;
                //tempX /= x_scale;
                //tempZ /= y_scale;

                db = &rando_overlay_db;

                gDPPipeSync(db->p++);
                gDPLoadTextureBlock(db->p++, &blank_texture, G_IM_FMT_RGBA, G_IM_SIZ_32b,
                                            1, 1, 0, G_TX_NOMIRROR | G_TX_WRAP,
                                            G_TX_NOMIRROR | G_TX_WRAP, G_TX_NOMASK, G_TX_NOMASK, G_TX_NOLOD, G_TX_NOLOD);
                rectLeft = minimap_center_x + ((R_COMPASS_OFFSET_X + tempX) / 10.0);
                rectTop =  minimap_center_z + ((tempZ - R_COMPASS_OFFSET_Y) / 10.0);
                gSPTextureRectangle(db->p++, (rectLeft-1) << 2, (rectTop-1) << 2, (rectLeft + 1) << 2,
                                            (rectTop + 1) << 2, G_TX_RENDERTILE, 0, 0, 0,
                                            0);
            }

            curr = curr->next;
        }
    }

}
