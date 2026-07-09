#include "z_en_cow.h"
#include "models.h"
#include "z64_math.h"
#include "z64.h"
#include "util.h"

int32_t EnCow_OverrideLimbDrawNew(z64_game_t* play, int32_t limbIndex, Gfx** dList, z64_xyz_t* Vec3f, z64_xyz_t* rot, void* thisx) 
    {
    EnCow* this = (EnCow*)thisx;

    if (limbIndex == COW_LIMB_HEAD) {
        rot->y += this->headRot.y;
        rot->x += this->headRot.x;
    }
    return false;
    }  