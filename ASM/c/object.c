#include "z64.h"
#include "object.h"

// Function that adds an object to an object slot and sets up data for the object
// to be loaded by Object_UpdateEntries() (which is run every frame).
extern void* func_800982FC(z64_obj_ctxt_t* objectCtx, int32_t slot, int16_t objectId);

/**
 * Loads an extra object that an actor does not have a dependency on.
 * Will get deloaded upon room/scene change, as it is not part of the object list.
 * @return 0 if no slot, 1 if loaded into new slot, 2 if already loaded
 */
int16_t Object_LoadExtra(z64_game_t* play, int16_t objectId) {
    int32_t i;
    int32_t slot = -1;

    // Check if object is already loaded, and for first available slot
    for (i = 0; i < ARRAY_COUNT(play->obj_ctxt.objects); i++) {

        // Already loaded (abs is needed - negative id if object not yet DMA:ed)
        if (ABS((play->obj_ctxt.objects[i].id)) == objectId) {
            return 2;

        } else if (slot == -1 && play->obj_ctxt.objects[i].id == 0) {
            slot = i;
            break;
        }
    }

    if(slot != -1) {
        // Take the found slot
        z64_mem_obj_t* newEntry = &play->obj_ctxt.objects[slot];    // The new object
        z64_mem_obj_t* lastEntry = &play->obj_ctxt.objects[play->obj_ctxt.n_objects-1]; // Previous last added object
        RomFile* lastObjectFile = &gObjectTable[ABS(lastEntry->id)];    // Get previous object start pointer and size
        uint32_t lastSize = lastObjectFile->vromEnd - lastObjectFile->vromStart;
        newEntry->data = (void*)ALIGN16((uintptr_t)lastEntry->data + lastSize); // Gives pointer to start for the new object data

        func_800982FC(&play->obj_ctxt, slot, objectId); // Set up data for adding the object to the slot on next update
        play->obj_ctxt.n_objects++;
        return 1;
    }
    return 0;
}
