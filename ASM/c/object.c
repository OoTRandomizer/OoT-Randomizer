#include "z64.h"
#include "object.h"

// Function that adds an object to an object slot and sets up data for the object
// to be loaded by Object_UpdateEntries() (which is run every frame).
extern void* func_800982FC(z64_obj_ctxt_t* objectCtx, int32_t slot, int16_t objectId);
extern int32_t DmaMgr_RequestSync(void* ram, uintptr_t vrom, size_t size);

/**
 * Loads an extra object that no previously loaded actor has a dependency on.
 * Will get deloaded upon room/scene change, as it is not part of the room object list.
 * @param syncDma true if the object should be synchronously DMA transferred this frame.
 * Otherwise, it is loaded asynchronously on next frame by Object_UpdateEntries.
 * @return: Slot number (if already loaded, or loaded into a new slot), else -1
 * NOTE:
 * - Crash risk if trying to sync DMA during En_Holl room transition, if an actor
 * in the previous room depends on object data that will be overwritten by the DMA
 * before the actor is properly deleted (see: GTG Lava room to Chest maze with SoT block).
 * Async DMA is OK because of the extra frame delay.
 * - Objects are otherwise not unloaded/loaded on demand, so extra loading is OK.
 * - If crashing, if async DMA ensure that the object is loaded before the actor
 * is trying to draw (try sync DMA). Ensure that there is actually object slot and space
 * available for new object before drawing or doing anything else that requires object.
 *
 */
int16_t Object_LoadExtra(z64_game_t* play, int16_t objectId, uint8_t syncDma) {
    uint8_t i;
    int16_t slot = -1;

    // Check if object is already loaded, and for first available slot
    for (i = 0; i < ARRAY_COUNT(play->obj_ctxt.objects); i++) {

        // Already loaded (abs is needed - negative id if object not yet DMA:ed)
        if (ABS((play->obj_ctxt.objects[i].id)) == objectId) {
            return i;

        } else if (slot == -1 && play->obj_ctxt.objects[i].id == 0) {
            slot = i;
            break;
        }
    }

    if (slot != -1) {
        // Take the found slot
        z64_mem_obj_t* newEntry = &play->obj_ctxt.objects[slot];    // The new object
        z64_mem_obj_t* lastEntry = &play->obj_ctxt.objects[play->obj_ctxt.n_objects-1]; // Previous last added object
        RomFile* lastObjectFile = &gObjectTable[ABS(lastEntry->id)];    // Get previous object start pointer and size
        uint32_t lastSize = lastObjectFile->vromEnd - lastObjectFile->vromStart;
        newEntry->data = (void*)ALIGN16((uintptr_t)lastEntry->data + lastSize); // Gives pointer to start for the new object data

        // Set up data for adding the object to the slot on next update or now
        if (func_800982FC(&play->obj_ctxt, slot, objectId) != NULL) {
            play->obj_ctxt.n_objects++;

            if (syncDma) {
                play->obj_ctxt.objects[slot].id = objectId;    // Uninvert the id because it will get loaded now
                RomFile* objectFile = &gObjectTable[objectId];    // Get object start pointer and size
                uint32_t size = objectFile->vromEnd - objectFile->vromStart;
                DmaMgr_RequestSync(newEntry->data, objectFile->vromStart, size);
            }

        } else { // Loading new object would exceed object space
            #ifdef DEBUG_MODE
                char msg[256];
                sprintf(msg, "Obj %d slot %d", objectId, slot);
                Fault_AddHungupAndCrashImpl("Object_LoadExtra: No memory", msg);
            #endif

            return -1;  // Don't crash non-debug mode for now but this should not happen!
        }
    }

    return slot;
}
