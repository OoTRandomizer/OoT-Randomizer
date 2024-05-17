#ifndef AUDIO_H
#define AUDIO_H

#include <stdint.h>

typedef struct {
    float x, y, z;
} Vec3f; // move this if needed elsewhere

extern Vec3f z64_SfxDefaultPos;
extern float z64_SfxDefaultFreqAndVolScale;
extern uint8_t z64_SfxDefaultReverb;

#endif //AUDIO_H
