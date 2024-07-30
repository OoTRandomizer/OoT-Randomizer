#ifndef SYS_MATRIX_H
#define SYS_MATRIX_H

#include "z64.h"

typedef void (*duplicate_sys_matrix_fn)(void);
typedef void (*pop_sys_matrix_fn)(void);
typedef void (*translate_sys_matrix_fn)(float x, float y, float z, int32_t in_place_flag);
typedef void (*scale_sys_matrix_fn)(float x, float y, float z, int32_t in_place_flag);
typedef void (*rotate_Z_sys_matrix_fn)(float z, int32_t in_place_flag);
typedef void (*update_sys_matrix_fn)(float mf[4][4]);
typedef Mtx* (*append_sys_matrix_fn)(z64_gfx_t* gfx);
typedef void (*convert_matrix_fn)(const float* in, uint16_t* out);

#define duplicate_sys_matrix ((duplicate_sys_matrix_fn)0x800AA6EC)
#define pop_sys_matrix ((pop_sys_matrix_fn)0x800AA724)
#define translate_sys_matrix ((translate_sys_matrix_fn)0x800AA7F4)
#define scale_sys_matrix ((scale_sys_matrix_fn)0x800AA8FC)
#define rotate_Z_sys_matrix ((rotate_Z_sys_matrix_fn)0x800AAD4C)
#define update_sys_matrix ((update_sys_matrix_fn)0x800ABE54)
#define append_sys_matrix ((append_sys_matrix_fn)0x800AB900)
#define convert_matrix ((convert_matrix_fn)0x800AB6BC)

#endif
