#include <stdint.h>

typedef struct OcarinaNote {
    /* 0x0 */ uint8_t pitch; // number of semitones above middle C
    /* 0x2 */ uint16_t length; // number of frames the note is sustained
    /* 0x4 */ uint8_t volume;
    /* 0x5 */ uint8_t vibrato;
    /* 0x6 */ int8_t bend; // frequency multiplicative offset from the pitch
    /* 0x7 */ uint8_t bFlat4Flag; // Flag for resolving whether (pitch = OCARINA_PITCH_BFLAT4) gets mapped to either C_RIGHT and C_LEFT
} OcarinaNote;  // size = 0x8

void* save_scarecrow_song(uint8_t* dest, uint8_t* src, int32_t len) {

    // Check if the first note is a rest, and shift the song to start to the next note if so.
    if (src[0] == 0xFF) {
        src += 8;
        len -= 8;
    }

    // Fix the length of each note to a minimum.
    OcarinaNote* scarecrow_song = (OcarinaNote*)src;
    uint8_t song_notes = 0;
    for (uint8_t i = 0; i < 20; i++) {
        if (scarecrow_song[i].length < 4 && scarecrow_song[i].pitch > 0) {
            scarecrow_song[i].length = 4;
        }

        // Determine position of eighth non-rest note
        if (scarecrow_song[i].pitch > 0 && scarecrow_song[i].pitch != 0xFF) {
            song_notes++;
        }
        // Ignore rests and notes after the eighth input
        if (song_notes > 8) {
            scarecrow_song[i].pitch = 0;
            scarecrow_song[i].length = 0;
            scarecrow_song[i].volume = 0;
            scarecrow_song[i].vibrato = 0;
            scarecrow_song[i].bend = 0;
            scarecrow_song[i].bFlat4Flag = 0;
        }
    }

    // Displaced Memcpy
    uint8_t* d = dest;
    const uint8_t* s = src;

    while (len > 0) {
        *d++ = *s++;
        len--;
    }

    return dest;
}
