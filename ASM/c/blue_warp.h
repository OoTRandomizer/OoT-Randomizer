#ifndef DOOR_WARP1_H
#define DOOR_WARP1_H

#include "z64.h"

int32_t DoorWarp1_PlayerInRange_Overwrite(z64_actor_t* actor, z64_game_t* game);

int32_t DoorWarp1_IsSpiritRewardObtained(void);
int32_t DoorWarp1_IsShadowRewardObtained(void);

void DoorWarp1_KokiriEmerald_Overwrite(void);
void DoorWarp1_GoronRuby_Overwrite(void);
void DoorWarp1_ZoraSapphire_Overwrite(void);
void DoorWarp1_ForestMedallion_Overwrite(void);
void DoorWarp1_FireMedallion_Overwrite(void);
void DoorWarp1_WaterMedallion_Overwrite(void);
void DoorWarp1_SpiritMedallion_Overwrite(void);
void DoorWarp1_ShadowMedallion_Overwrite(void);

#endif
