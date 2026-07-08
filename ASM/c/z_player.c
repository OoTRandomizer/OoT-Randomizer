#include "z64.h"
#include "actor.h"
#include "player.h"

#define SCENE_HYRULE_FIELD      0x51
#define SCENE_LAKE_HYLIA        0x57
#define SCENE_GERUDO_VALLEY     0x5A
#define SCENE_GERUDOS_FORTRESS  0x5D
#define SCENE_LON_LON_RANCH     0x63

extern int32_t BgCheck_AnyLineTest1(CollisionContext* colCtx, z64_xyzf_t* posA, z64_xyzf_t* posB,
                                    z64_xyzf_t* posResult, z64_col_poly_t** outPoly, int32_t chkOneFace);

/**
 * Do a line intersect test between player position and waterbox surface Y position
 * If resulting Y position is less than or equal to waterbox surface, player is either
 * in water (eg. Zora's River water- > Hyrule Field) or directly above water surface
 * (Gerudo Valley -> Lake Hylia), so should not spawn Epona.
 * float ySurface is $f12 = (waterbox Y surface - player Y position)
 */
void Player_CheckEponaWater(volatile float ySurface) {
    // Exited riding into an Epona allowed scene
    if(R_EXITED_SCENE_RIDING_HORSE == true &&
        (z64_game.scene_index == SCENE_HYRULE_FIELD || z64_game.scene_index == SCENE_LAKE_HYLIA ||
        z64_game.scene_index == SCENE_GERUDO_VALLEY || z64_game.scene_index == SCENE_GERUDOS_FORTRESS ||
        z64_game.scene_index == SCENE_LON_LON_RANCH)) {

        z64_col_poly_t* floorPoly;
        z64_xyzf_t pos = (z64_xyzf_t){z64_link.common.pos_world.x, ySurface, z64_link.common.pos_world.z};
        z64_xyzf_t posResult;

        // Check line intersection: player position vs player-waterbox Y position "pos"
        // Intersect position is stored in "posResult"
        BgCheck_AnyLineTest1(&z64_game.colCtx, &z64_link.common.pos_world, &pos, &posResult, &floorPoly, false);

        // If the water surface is either higher than resulting Y position (= is above floor),
        // or same height (= is waterbox itself), water is higher than the floor
        if((posResult.y <= ySurface)) {
            // Dismount in all areas, except Lake Hylia warp entrance (X pos -1045).
            // (That waterbox has Y surface -90 for one frame, so special X-based fix is needed)
            if((z64_game.scene_index != SCENE_LAKE_HYLIA) || (z64_game.scene_index == SCENE_LAKE_HYLIA &&
            !(z64_link.common.pos_world.x > -1050.0f && z64_link.common.pos_world.x < -1040.0f))) {
                R_EXITED_SCENE_RIDING_HORSE = false;
            }
        }
    }
}
