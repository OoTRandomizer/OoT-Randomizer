//Accept86 Navi Hints
//==================================================================================================
#include "z64.h"

uint8_t CheckByItemID(uint16_t MaskedSaveDataHalfWord, uint8_t ItemID);

extern const uint32_t C_SAVE_CONTEXT;  
//uint32_t SaveDataBase = (uint32_t)SAVE_CONTEXT;  //RAM Address NTSC1.0 0x8011A5D0 https://wiki.cloudmodding.com/oot/Save_Format#Save_File_Validation 
//uint8_t* SaveDataBottleBasePointer = (uint8_t*)(SAVE_CONTEXT + 0x86);


// returns: 0xff End of LookupTable; 0:SaveData does not have item; 1: SaveData has item
uint8_t Navi_CheckSaveData(uint32_t LookupTablePointer)
{
    uint8_t* pLookupTableElement = (uint8_t*)(uint32_t)LookupTablePointer;
    uint8_t IsDone = pLookupTableElement[3];
    
    if(IsDone==0xff)        // End of LookupTable?
        return 0xff;
        
    uint16_t SaveDataByteOffset = *(uint16_t*)pLookupTableElement;

    if(!SaveDataByteOffset) // If SaveDataOffset not there just continue (shouldn't happen)
        return 1;
        
    uint8_t SaveDataBitOffset = pLookupTableElement[2];

    const uint32_t SaveDataBase = (uint32_t)C_SAVE_CONTEXT; 
    uint8_t* pSaveData = (uint8_t*)(SaveDataBase + SaveDataByteOffset);

    uint32_t SaveDataWord = (uint32_t)*(uint32_t*)pSaveData;
    SaveDataWord = SaveDataWord >> SaveDataBitOffset;
    uint16_t SaveDataMask = *(uint16_t*)(pLookupTableElement + 4);
    
    if((SaveDataWord & 0xff) == (0xff))     // SaveData doesn't have Element because its ff?
    {
        return 0;
    }
    
    uint16_t MaskedSaveDataHalfWord = SaveDataWord & SaveDataMask;
    
    
    //ItemID checks are only for required progressables and Rutos Letter
    uint8_t ItemID = pLookupTableElement[6];
    if(ItemID)
    {
        return CheckByItemID(MaskedSaveDataHalfWord, ItemID);
    }
    
    
    if(MaskedSaveDataHalfWord)      // The normal check by Masked Savedata
        return 1;
    
    
    return (MaskedSaveDataHalfWord != SaveDataMask) && (SaveDataMask==0xffff); // if its not the same as mask, item there 
                    //value could be 0, but if savemask ix 0xffff thats ok and item there
    

    return 0;
}



//ItemID checks of SaveData for Navi are only for required progressables and Rutos Letter
uint8_t CheckByItemID(uint16_t MaskedSaveDataHalfWord, uint8_t ItemID)
{
    if(ItemID == 0x1B)  // Rutos Letter to check
    {
        const uint8_t* SaveDataBottleBasePointer = (uint8_t*)(C_SAVE_CONTEXT + 0x86);
        // Does any Bottle have this?
        if( (SaveDataBottleBasePointer[0]==0x1B) || (SaveDataBottleBasePointer[1]==0x1B) ||
                (SaveDataBottleBasePointer[2]==0x1B) ||(SaveDataBottleBasePointer[3]==0x1B) )
            return 1;
            
        return 0;
    }
    
    //required Progressables
    if( (MaskedSaveDataHalfWord & 0xff) >= ItemID )
        return 1;

     return 0;
}

    
    