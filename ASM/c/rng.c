#include "rng.h"

uint32_t RANDOMIZER_RNG_SEED = 0;
uint32_t RNG_SEED_INT = 1;
static uint32_t RNG_SEED_FLOAT = 1;

/**
 * Gets the next integer in the sequence of pseudo-random numbers.
 */
uint32_t Seeded_Rand_Next() {
    return RNG_SEED_INT = (RNG_SEED_INT * 1664525) + 1013904223;
}

/**
 * Seeds the pseudo-random number generator by providing a starting value.
 */
void Seeded_Rand_Seed(uint32_t seed) {
    RNG_SEED_INT = seed;
}

/**
 * Seeds the pseudo-random number generator with the initial boot value.
 */
void Seeded_Reset() {
    RNG_SEED_INT = RANDOMIZER_RNG_SEED;
}

/**
 * Returns a pseudo-random floating-point number between 0.0f and 1.0f, by generating
 * the next integer and masking it to an IEEE-754 compliant floating-point number
 * between 1.0f and 2.0f, returning the result subtract 1.0f.
 */
float Seeded_Rand_ZeroOne() {
    RNG_SEED_INT = (RNG_SEED_INT * 1664525) + 1013904223;
    RNG_SEED_FLOAT = ((RNG_SEED_INT >> 9) | 0x3F800000);
    return *((float*)&RNG_SEED_FLOAT) - 1.0f;
}

/**
 * Returns a pseudo-random floating-point number between -0.5f and 0.5f by the same
 * manner in which Rand_ZeroOne generates its result.
 */
float Seeded_Rand_Centered() {
    RNG_SEED_INT = (RNG_SEED_INT * 1664525) + 1013904223;
    RNG_SEED_FLOAT = ((RNG_SEED_INT >> 9) | 0x3F800000);
    return *((float*)&RNG_SEED_FLOAT) - 1.5f;
}