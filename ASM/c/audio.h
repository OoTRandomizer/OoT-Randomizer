#ifndef AUDIO_H
#define AUDIO_H

#include "z64_math.h"
#include <stdint.h>

extern Vec3f z64_SfxDefaultPos;
extern float z64_SfxDefaultFreqAndVolScale;
extern uint8_t z64_SfxDefaultReverb;
extern void Audio_PlaySfxGeneral(uint16_t sfxId, Vec3f* pos, uint8_t token, float* freqScale, float* vol, int8_t* reverbAdd);

#endif //AUDIO_H
