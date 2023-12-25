#ifndef UTIL_H
#define UTIL_H

#include <n64.h>

#define array_size(a) (sizeof(a) / sizeof(a[0]))

void heap_init();
void* heap_alloc(int bytes);

typedef struct {
    uint8_t* buf;
    uint32_t vrom_start;
    uint32_t size;
} file_t;

typedef void (*read_file_fn)(void* mem_addr, uint32_t vrom_addr,
        uint32_t size);
#define read_file ((read_file_fn)0x80000DF0)

void file_init(file_t* file);

#endif
