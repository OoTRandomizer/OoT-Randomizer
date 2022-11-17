#ifndef RNG_H
#define RNG_H 

#include "z64.h"

extern uint32_t SEED;
extern uint32_t RANDOMIZER_RNG_SEED;
extern uint32_t RNG_SEED_INT;

uint32_t Seeded_Rand_Next();
void Seeded_Rand_Seed(uint32_t seed);
void Seeded_Reset();
float Seeded_Rand_ZeroOne();
float Seeded_Rand_Centered();
void seed_rng();

#endif
