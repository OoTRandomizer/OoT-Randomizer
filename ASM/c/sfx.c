#include "z64.h"
#include "audio.h"

extern float CFG_ADULT_VOLUME;
extern float CFG_CHILD_VOLUME;

void Player_PlaySfxWithVolume(z64_link_t* this, uint16_t sfxId) {
    float* ageVolume = &CFG_ADULT_VOLUME;
    ageVolume += z64_game.link_age;
    Audio_PlaySfxGeneral(sfxId, &this->common.projectedPos, 4, &z64_SfxDefaultFreqAndVolScale, ageVolume, &z64_SfxDefaultReverb);
}