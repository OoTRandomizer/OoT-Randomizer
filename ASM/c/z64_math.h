#ifndef Z_MATH_H
#define Z_MATH_H

#include "stdint.h"

typedef struct z64_xyz_t
{
  int16_t x;
  int16_t y;
  int16_t z;
} z64_xyz_t;

typedef struct z64_xyzf_t
{
  float x;
  float y;
  float z;
} z64_xyzf_t;

typedef uint16_t z64_angle_t;
typedef struct
{
  z64_angle_t x;
  z64_angle_t y;
  z64_angle_t z;
} z64_rot_t;

typedef struct {
    float x, y, z;
} Vec3f; // move this if needed elsewhere

#endif
