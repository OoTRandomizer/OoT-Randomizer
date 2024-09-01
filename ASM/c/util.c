#include "util.h"
#include "z64.h"
#include "actor.h"

extern char C_HEAP[];
void* heap_next = NULL;

void heap_init() {
    heap_next = &C_HEAP[0];
}

void* heap_alloc(int bytes) {
    int rem = bytes % 16;
    if (rem) bytes += 16 - rem;

    void* result = heap_next;
    heap_next = (char*)heap_next + bytes;
    return result;
}

void file_init(file_t* file) {
    file->buf = heap_alloc(file->size);
    read_file(file->buf, file->vrom_start, file->size);
}

void* resolve_overlay_addr(void* addr, uint16_t overlay_id) {
    ActorOverlay overlay = gActorOverlayTable[overlay_id];
    if (overlay.loadedRamAddr) {
        return addr - overlay.vramStart + overlay.loadedRamAddr;
    }
    return NULL;
}
