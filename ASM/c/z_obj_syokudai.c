#include "z64.h"

typedef struct ObjSyokudai {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x014C */ ColliderCylinder standCollider;
    /* 0x0198 */ ColliderCylinder flameCollider;
    /* 0x01E4 */ int16_t litTimer;
    /* 0x01E6 */ uint8_t flameTexScroll;
    /* 0x01E8 */ void* lightNode;
    /* 0x01EC */ char lightInfo[0xE];
} ObjSyokudai;

extern void SkinMatrix_Vec3fMtxFMultXYZW(MtxF* mf, z64_xyzf_t* src, z64_xyzf_t* xyzDest, float* wDest);
extern void Matrix_SetTranslateRotateYXZ(float translateX, float translateY, float translateZ, z64_rot_t* rot);
extern void Matrix_Scale(float x, float y, float z, uint8_t mode);
extern void Matrix_MultVec3f(z64_xyzf_t* src, z64_xyzf_t* dest);
extern void Matrix_Push(void);
extern void Matrix_Pop(void);
extern void Lights_PointGlowSetInfo(char* info, int16_t x, int16_t y, int16_t z,
                                        uint8_t r, uint8_t g, uint8_t b, int16_t radius);

// Rotate the torch flame collider to make hitting slanted torches easier
void ObjSyokudai_RotateFlameCollider(ObjSyokudai* this, z64_game_t* play) {

    // Only rotate if actually X/Z rotated, otherwise use already set cylinder data
    if (this->actor.rot_2.x != 0 || this->actor.rot_2.z != 0) {
        z64_xyzf_t posVector = { 0.0, 45.0, 0.0 };    // "Vertex" at top of torch
        z64_xyzf_t lightVector = { 0.0, 79.0, 0.0 };    // "Vertex" above for light
        z64_xyzf_t posResult;
        z64_xyzf_t lightResult;

        // Do transformations that are applied to the torch model for drawing, but apply to vertex
        Matrix_Push();
        SkinMatrix_Vec3fMtxFMultXYZW(&play->viewProjectionMtxF, &this->actor.pos_world, &this->actor.projectedPos,
                                                &this->actor.projectedW);
        Matrix_SetTranslateRotateYXZ(this->actor.pos_world.x, this->actor.pos_world.y,
                                        this->actor.pos_world.z, &this->actor.rot_2);  // shape.rot
        Matrix_Scale(this->actor.scale.x, this->actor.scale.y, this->actor.scale.z, 1); // 1 = MTXMODE_APPLY
        Matrix_MultVec3f(&posVector, &posResult);
        Matrix_MultVec3f(&lightVector, &lightResult);
        Matrix_Pop();

        // Vertex becomes base point for the collider
        this->flameCollider.dim.yShift = 0; // Normally Y shift +45
        this->flameCollider.dim.pos.x = posResult.x;
        this->flameCollider.dim.pos.y = posResult.y - 5.0f;
        this->flameCollider.dim.pos.z = posResult.z;
        // Re-set point glow location
        Lights_PointGlowSetInfo((void*)&this->lightInfo, lightResult.x, lightResult.y, lightResult.z, 255, 255, 180, -1);

    } else {
        // Set regular torch flame collider
        this->flameCollider.dim.pos.x = this->actor.pos_world.x;
        this->flameCollider.dim.pos.y = this->actor.pos_world.y;
        this->flameCollider.dim.pos.z = this->actor.pos_world.z;
    }
}
