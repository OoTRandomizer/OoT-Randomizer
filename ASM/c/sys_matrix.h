#ifndef SYS_MATRIX_H
#define SYS_MATRIX_H

#include "z64.h"

typedef void (*translate_sys_matrix_fn)(float x, float y, float z, int32_t in_place_flag);
typedef void (*rotate_Z_sys_matrix_fn)(float z, int32_t in_place_flag);
typedef void (*update_sys_matrix_fn)(float mf[4][4]);
typedef Mtx* (*append_sys_matrix_fn)(z64_gfx_t* gfx);
typedef void (*convert_matrix_fn)(const float* in, uint16_t* out);

#define translate_sys_matrix ((translate_sys_matrix_fn)0x800AA7F4)
#define rotate_Z_sys_matrix ((rotate_Z_sys_matrix_fn)0x800AAD4C)
#define update_sys_matrix ((update_sys_matrix_fn)0x800ABE54)
#define append_sys_matrix ((append_sys_matrix_fn)0x800AB900)
#define convert_matrix ((convert_matrix_fn)0x800AB6BC)

extern void Matrix_Pop(void);
extern void Matrix_Push(void);
extern void Matrix_Scale(float x, float y, float z, uint8_t mode);
extern void Matrix_MultVec3f(z64_xyzf_t* src, z64_xyzf_t* dest);
extern void SkinMatrix_Vec3fMtxFMultXYZW(MtxF* mf, z64_xyzf_t* src, z64_xyzf_t* xyzDest, float* wDest);
extern void Matrix_SetTranslateRotateYXZ(float translateX, float translateY, float translateZ, z64_rot_t* rot);

#endif
