#ifndef OBJECT_H
#define OBJECT_H

#define ALIGN16(x) (((x) + 0xF) & ~0xF)
#define ARRAY_COUNT(arr) (int32_t)(sizeof(arr) / sizeof(arr[0]))

typedef struct RomFile {
    /* 0x00 */ uintptr_t vromStart;
    /* 0x04 */ uintptr_t vromEnd;
} RomFile; // size = 0x8

extern RomFile gObjectTable[];

int16_t Object_LoadExtra(z64_game_t* play, int16_t objectId);

#endif
