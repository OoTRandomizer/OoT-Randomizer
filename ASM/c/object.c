#include "z64.h"
#include "object.h"

#define ARRAY_COUNT(arr) (int32_t)(sizeof(arr) / sizeof(arr[0]))

// Function that adds an object to an object slot and sets up data for the object
// to be loaded by Object_UpdateEntries() (run every frame).
extern void* func_800982FC(z64_obj_ctxt_t* objectCtx, int32_t slot, int16_t objectId);

// Loads an extra object that an actor does not have a dependency on.
// Will get deloaded upon room/scene change, as it is not part of the object list
bool Object_LoadExtra(z64_game_t* play, int16_t objectId) {
    int32_t i;
    int32_t slot = -1;

    // Check all object slots if object is already loaded, and for first available slot
    // Checking all is probably not needed as objects get unloaded on room/scene change
    for (i = 0; i < ARRAY_COUNT(play->obj_ctxt.objects); i++) {
        // abs is needed, negative id if object not yet DMA:ed
        if (ABS((play->obj_ctxt.objects[i].id)) == objectId) {
            return true;
        } else if (slot == -1 && play->obj_ctxt.objects[i].id == 0) {
            slot = i;
        }
    }

    if(slot != -1) {
        // Take the found slot
        func_800982FC(&play->obj_ctxt, slot, objectId);
        play->obj_ctxt.n_objects++;
        return true;
    }

    return false;
}
