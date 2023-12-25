#include "z64.h"
#include "save.h"

#define SRAM_BASE 0x08000000
#define SRAM_SIZE 0x8000
#define SLOT_COUNT 4
#define SRAM_NEWDATA_START 0x5160
#define SRAM_ORIGINAL_SLOT_SIZE 0x1450
#define SAVE_SIZE 0x1354
#define SLOT_SIZE SRAM_SIZE/SLOT_COUNT - 0x20
#define CHECKSUM_SIZE 0x9AA
#define CHECKSUM_OFFSET 0x1352/2
#define DEATHS_OFFSET OFFSETOF(z64_file_t, deaths)
#define NAME_OFFSET OFFSETOF(z64_file_t, file_name)
#define HEALTH_CAP_OFFSET OFFSETOF(z64_file_t, energy_capacity)
#define QUEST_OFFSET OFFSETOF(z64_file_t, quest_items)
#define N64DD_OFFSET OFFSETOF(z64_file_t, n64dd_flag)
#define DEFENSE_OFFSET OFFSETOF(z64_file_t, defense_hearts)
#define HEALTH_OFFSET OFFSETOF(z64_file_t, energy )


extern uint8_t* collectible_override_flags;
extern uint16_t num_override_flags;
extern uint16_t SRAM_SLOTS[6];

typedef void (*Sram_InitNewSave_Func)(void);
Sram_InitNewSave_Func Sram_InitNewSave = (Sram_InitNewSave_Func)(0x8008FFC0);
extended_savecontext_static_t extended_savectx;

void SsSram_ReadWrite_Safe(uint32_t addr, void* dramAddr, size_t size, uint32_t direction);

// Override Sram_WriteSave to include the collectible flags in the checksum calculation.
void Sram_WriteSave(SramContext* sramCtx) {
    uint16_t offset;
    uint16_t checksum;
    uint16_t* ptr;

    z64_file.checksum = 0;

    ptr = (uint16_t*)&z64_file;
    checksum = 0;

    // Checksum calculation for original SaveContext data
    for (offset = 0; offset < CHECKSUM_SIZE; offset++) {
        checksum += *ptr++;
    }

    ptr = (uint16_t*)&extended_savectx;
    for (offset = 0; offset < sizeof(extended_savectx) / 2; offset++) {
        checksum += *ptr++;
    }

    // Calculate the collectible flags in the checksum
    ptr = (uint16_t*)collectible_override_flags;
    for (offset = 0; offset < num_override_flags / 2; offset++) {
        checksum += *ptr++;
    }
    z64_file.checksum = checksum;

    // Write the base SaveContext data to the main slot
    offset = SRAM_SLOTS[z64_file.file_index];
    SsSram_ReadWrite_Safe(SRAM_BASE + offset, &z64_file, SRAM_ORIGINAL_SLOT_SIZE, OS_WRITE);

    // Write the base SaveContext data to the backup slot
    offset = SRAM_SLOTS[z64_file.file_index + 3];
    SsSram_ReadWrite_Safe(SRAM_BASE + offset, &z64_file, SRAM_ORIGINAL_SLOT_SIZE, OS_WRITE);

    // Write the collectible flags to the back of the main slot
    uint16_t slot_offset = SRAM_SLOTS[z64_file.file_index] + SLOT_SIZE - (num_override_flags);
    SsSram_ReadWrite_Safe(SRAM_BASE + slot_offset, collectible_override_flags, num_override_flags, OS_WRITE);

    // Write the extended Save Context data to the main slot
    offset = SRAM_SLOTS[z64_file.file_index] + SRAM_ORIGINAL_SLOT_SIZE;
    SsSram_ReadWrite_Safe(SRAM_BASE + offset, &extended_savectx, sizeof(extended_savecontext_static_t), OS_WRITE);

    // Write the collectible flags to the back of the backup slot
    slot_offset = SRAM_SLOTS[z64_file.file_index + 3] + SLOT_SIZE - (num_override_flags);
    SsSram_ReadWrite_Safe(SRAM_BASE + slot_offset, collectible_override_flags, num_override_flags, OS_WRITE);

    // Write the extended Save Context data to the backup slot
    offset = SRAM_SLOTS[z64_file.file_index + 3] + SRAM_ORIGINAL_SLOT_SIZE;
    SsSram_ReadWrite_Safe(SRAM_BASE + offset, &extended_savectx, sizeof(extended_savecontext_static_t), OS_WRITE);
}

// Override the Sram_VerifyAndLoadAllSaves function. Only check our new 2 slots (and their backups).
// And include the collectible flags in the checksum.
void Sram_VerifyAndLoadAllSaves(z64_FileChooseContext_t* fileChooseCtx, SramContext* sramCtx) {
    uint16_t i;
    uint16_t newChecksum;
    uint16_t slotNum;
    uint16_t offset;
    uint16_t j;
    uint16_t oldChecksum;
    uint16_t* ptr;
    uint16_t dayTime;

    // Read SRAM to RAM buffer
    z64_bzero(sramCtx->readBuff, SRAM_SIZE);
    SsSram_ReadWrite_Safe(SRAM_BASE, sramCtx->readBuff, SRAM_SIZE, OS_READ);

    dayTime = ((void)0, z64_file.day_time);

    // Loop through each slot and check the checksums
    for (slotNum = 0; slotNum < 2; slotNum++) {
        offset = SRAM_SLOTS[slotNum];
        z64_memcopy(&z64_file, sramCtx->readBuff + offset, SAVE_SIZE);
        z64_memcopy(&extended_savectx, sramCtx->readBuff + offset + SRAM_ORIGINAL_SLOT_SIZE, sizeof(extended_savecontext_static_t));
        z64_memcopy(collectible_override_flags, sramCtx->readBuff + offset + SLOT_SIZE - (num_override_flags),  num_override_flags);
        oldChecksum = z64_file.checksum;
        z64_file.checksum = 0;
        ptr = (uint16_t*)&z64_file;

        for (i = newChecksum = j = 0; i < CHECKSUM_SIZE; i++) {
            newChecksum += *ptr++;
        }
        // Calculate the extended savectx in the checksum
        ptr = (uint16_t*)&extended_savectx;
        for (i = 0; i < sizeof(extended_savectx) / 2; i++) {
            newChecksum += *ptr++;
        }
        // Calculate the collectible flags in the checksum
        ptr = (uint16_t*)collectible_override_flags;
        for (i = 0; i < num_override_flags / 2; i++) {
            newChecksum += *ptr++;
        }

        // "SAVE checksum calculation"

        if (newChecksum != oldChecksum) {
            // checksum didnt match, try backup save
            offset = SRAM_SLOTS[slotNum + 3];
            z64_memcopy(&z64_file, sramCtx->readBuff + offset, SAVE_SIZE);
            z64_memcopy(collectible_override_flags, sramCtx->readBuff + offset + SLOT_SIZE - num_override_flags, num_override_flags);
            oldChecksum = z64_file.checksum;
            z64_file.checksum = 0;
            ptr = (uint16_t*)&z64_file;

            for (i = newChecksum = j = 0; i < CHECKSUM_SIZE; i++) {
                newChecksum += *ptr++;
            }
            // Calculate the collectible flags in the checksum
            ptr = (uint16_t*)collectible_override_flags;
            for (i = 0; i < num_override_flags / 2; i++) {
                newChecksum += *ptr++;
            }
            // "(B) SAVE checksum calculation"

            if (newChecksum != oldChecksum) {
                // backup save didnt work, make new save
                z64_bzero(&z64_file.entrance_index, sizeof(int32_t));
                z64_bzero(&z64_file.link_age, sizeof(int32_t));
                z64_bzero(&z64_file.cutscene_index, sizeof(int32_t));
                // note that z64_file.dayTime is not actually the sizeof(int32_t)
                z64_bzero(&z64_file.day_time, sizeof(int32_t));
                z64_bzero(&z64_file.night_flag, sizeof(int32_t));
                z64_bzero(&z64_file.total_days, sizeof(int32_t));
                z64_bzero(&z64_file.bgs_day_count, sizeof(int32_t));

                Sram_InitNewSave();

                ptr = (uint16_t*)&z64_file;

                for (i = newChecksum = j = 0; i < CHECKSUM_SIZE; i++) {
                    newChecksum += *ptr++;
                }
                z64_file.checksum = newChecksum;

                i = SRAM_SLOTS[slotNum + 3];
                SsSram_ReadWrite_Safe(SRAM_BASE + i, &z64_file, SRAM_ORIGINAL_SLOT_SIZE, OS_WRITE);
                z64_bzero(collectible_override_flags, num_override_flags);
            }

            i = SRAM_SLOTS[slotNum];
            SsSram_ReadWrite_Safe(SRAM_BASE + i, &z64_file, SRAM_ORIGINAL_SLOT_SIZE, OS_WRITE);

            uint16_t slot_offset = i + SLOT_SIZE - (num_override_flags);
            SsSram_ReadWrite_Safe(SRAM_BASE + slot_offset, collectible_override_flags, num_override_flags, OS_WRITE);
        }
    }

    z64_bzero(sramCtx->readBuff, SRAM_SIZE);
    SsSram_ReadWrite_Safe(SRAM_BASE, sramCtx->readBuff, SRAM_SIZE, OS_READ);
    z64_file.day_time = dayTime;

    z64_memcopy(&fileChooseCtx->deaths[0], sramCtx->readBuff + SRAM_SLOTS[0] + DEATHS_OFFSET, sizeof(fileChooseCtx->deaths[0]));
    z64_memcopy(&fileChooseCtx->deaths[1], sramCtx->readBuff + SRAM_SLOTS[1] + DEATHS_OFFSET, sizeof(fileChooseCtx->deaths[0]));
    z64_memcopy(&fileChooseCtx->deaths[2], sramCtx->readBuff + SRAM_SLOTS[0] + DEATHS_OFFSET, sizeof(fileChooseCtx->deaths[0]));

    z64_memcopy(&fileChooseCtx->fileNames[0], sramCtx->readBuff + SRAM_SLOTS[0] + NAME_OFFSET, sizeof(fileChooseCtx->fileNames[0]));
    z64_memcopy(&fileChooseCtx->fileNames[1], sramCtx->readBuff + SRAM_SLOTS[1] + NAME_OFFSET, sizeof(fileChooseCtx->fileNames[0]));
    z64_memcopy(&fileChooseCtx->fileNames[2], sramCtx->readBuff + SRAM_SLOTS[0] + NAME_OFFSET, sizeof(fileChooseCtx->fileNames[0]));

    z64_memcopy(&fileChooseCtx->healthCapacities[0], sramCtx->readBuff + SRAM_SLOTS[0] + HEALTH_CAP_OFFSET, sizeof(fileChooseCtx->healthCapacities[0]));
    z64_memcopy(&fileChooseCtx->healthCapacities[1], sramCtx->readBuff + SRAM_SLOTS[1] + HEALTH_CAP_OFFSET, sizeof(fileChooseCtx->healthCapacities[0]));
    z64_memcopy(&fileChooseCtx->healthCapacities[2], sramCtx->readBuff + SRAM_SLOTS[0] + HEALTH_CAP_OFFSET, sizeof(fileChooseCtx->healthCapacities[0]));

    z64_memcopy(&fileChooseCtx->questItems[0], sramCtx->readBuff + SRAM_SLOTS[0] + QUEST_OFFSET, sizeof(fileChooseCtx->questItems[0]));
    z64_memcopy(&fileChooseCtx->questItems[1], sramCtx->readBuff + SRAM_SLOTS[1] + QUEST_OFFSET, sizeof(fileChooseCtx->questItems[0]));
    z64_memcopy(&fileChooseCtx->questItems[2], sramCtx->readBuff + SRAM_SLOTS[0] + QUEST_OFFSET, sizeof(fileChooseCtx->questItems[0]));

    z64_memcopy(&fileChooseCtx->n64ddFlags[0], sramCtx->readBuff + SRAM_SLOTS[0] + N64DD_OFFSET, sizeof(fileChooseCtx->n64ddFlags[0]));
    z64_memcopy(&fileChooseCtx->n64ddFlags[1], sramCtx->readBuff + SRAM_SLOTS[1] + N64DD_OFFSET, sizeof(fileChooseCtx->n64ddFlags[0]));
    z64_memcopy(&fileChooseCtx->n64ddFlags[2], sramCtx->readBuff + SRAM_SLOTS[0] + N64DD_OFFSET, sizeof(fileChooseCtx->n64ddFlags[0]));

    z64_memcopy(&fileChooseCtx->defense[0], sramCtx->readBuff + SRAM_SLOTS[0] + DEFENSE_OFFSET, sizeof(fileChooseCtx->defense[0]));
    z64_memcopy(&fileChooseCtx->defense[1], sramCtx->readBuff + SRAM_SLOTS[1] + DEFENSE_OFFSET, sizeof(fileChooseCtx->defense[0]));
    z64_memcopy(&fileChooseCtx->defense[2], sramCtx->readBuff + SRAM_SLOTS[0] + DEFENSE_OFFSET, sizeof(fileChooseCtx->defense[0]));
}

// Overrides the original Sram_CopySave function.
// SRAM is now split into 4 equal size slots, instead of the original 6 slots of sizeof(SaveContext).
// So instead of just copying the data for the SaveContext, we just copy the whole slot
void Sram_CopySave(z64_FileChooseContext_t* fileChooseCtx, SramContext* sramCtx) {
    int32_t src_offset = SRAM_SLOTS[fileChooseCtx->selectedFileIndex];
    int32_t dst_offset = SRAM_SLOTS[fileChooseCtx->copyDestFileIndex];

    // Copy the entire slot
    z64_memcopy(sramCtx->readBuff + dst_offset, sramCtx->readBuff + src_offset, SLOT_SIZE);
    dst_offset = SRAM_SLOTS[fileChooseCtx->copyDestFileIndex + 3];
    z64_memcopy(sramCtx->readBuff + dst_offset,sramCtx->readBuff + src_offset, SLOT_SIZE);

    SsSram_ReadWrite_Safe(SRAM_BASE, sramCtx->readBuff, SRAM_SIZE, OS_WRITE);

    dst_offset = SRAM_SLOTS[fileChooseCtx->copyDestFileIndex];

    z64_memcopy(&fileChooseCtx->deaths[fileChooseCtx->copyDestFileIndex], sramCtx->readBuff + dst_offset + DEATHS_OFFSET,
            sizeof(fileChooseCtx->deaths[0]));
    z64_memcopy(&fileChooseCtx->fileNames[fileChooseCtx->copyDestFileIndex], sramCtx->readBuff + dst_offset + NAME_OFFSET,
            sizeof(fileChooseCtx->fileNames[0]));
    z64_memcopy(&fileChooseCtx->healthCapacities[fileChooseCtx->copyDestFileIndex], sramCtx->readBuff + dst_offset + HEALTH_CAP_OFFSET,
            sizeof(fileChooseCtx->healthCapacities[0]));
    z64_memcopy(&fileChooseCtx->questItems[fileChooseCtx->copyDestFileIndex], sramCtx->readBuff + dst_offset + QUEST_OFFSET,
            sizeof(fileChooseCtx->questItems[0]));
    z64_memcopy(&fileChooseCtx->n64ddFlags[fileChooseCtx->copyDestFileIndex], sramCtx->readBuff + dst_offset + N64DD_OFFSET,
            sizeof(fileChooseCtx->n64ddFlags[0]));
    z64_memcopy(&fileChooseCtx->defense[fileChooseCtx->copyDestFileIndex], sramCtx->readBuff + dst_offset + DEFENSE_OFFSET,
            sizeof(fileChooseCtx->defense[0]));

}

// Hook the Save Write function to write the flags to SRAM
void Save_Write_Hook(uint32_t addr, void* dramAddr, size_t size, uint32_t direction) {
    // Save the original data to SRAM
    SsSram_ReadWrite_Safe(addr, dramAddr, size, direction);

    // Save some additional data to the end of the slot SRAM
    uint16_t slot_offset = SRAM_SLOTS[z64_file.file_index] + SLOT_SIZE - (num_override_flags);
    SsSram_ReadWrite_Safe(SRAM_BASE + slot_offset, collectible_override_flags, num_override_flags, direction);
}

// Hook the Save open function to load the saved collectible flags
void Save_Open(char* sramBuffer) {
    uint16_t slot_offset = SRAM_SLOTS[z64_file.file_index] + SLOT_SIZE - (num_override_flags);
    z64_memcopy(collectible_override_flags, sramBuffer + slot_offset, num_override_flags);

    // Copy extended savectx
    z64_memcopy(&extended_savectx, sramBuffer + SRAM_SLOTS[z64_file.file_index] + SRAM_ORIGINAL_SLOT_SIZE, sizeof(extended_savecontext_static_t));
}

// Hook the init save function's call to SsSram_ReadWrite in order to zeroize the the collectible flags.
void Save_Init_Write_Hook(uint32_t addr, void* dramAddr, size_t size, uint32_t direction) {
    // zeroize the new collectible flags in the sram buffer (dramAddr)
    // zeroize the free space in the sram buffer (after the original slot up to the end of the slot)

    uint16_t slot_offset = SRAM_SLOTS[z64_file.file_index];
    z64_bzero(dramAddr + slot_offset + SRAM_ORIGINAL_SLOT_SIZE, SLOT_SIZE - SRAM_ORIGINAL_SLOT_SIZE);

    // write initial extended save data.
    uint8_t* extended_slot = dramAddr + slot_offset + SRAM_ORIGINAL_SLOT_SIZE;
    extended_initial_save_entry* entry = &EXTENDED_INITIAL_SAVE_DATA;
    while (entry->all != 0) {
        extended_slot[entry->offset] = entry->value;
        entry++;
    }

    // write to sram
    SsSram_ReadWrite_Safe(SRAM_BASE, dramAddr, SRAM_SIZE, direction);
}

void SsSram_ReadWrite_Safe(uint32_t addr, void* dramAddr, size_t size, uint32_t direction) {
    if (size > 0) {
        SsSram_ReadWrite(addr, dramAddr, size, direction);
    }
}
