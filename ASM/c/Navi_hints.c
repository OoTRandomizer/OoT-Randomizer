//Accept86 Navi Hints
//==================================================================================================
#include "z64.h"

const uint32_t C_Navi_Hints_Save_Offset = 0xD4 + (52 * 0x1C) +0x10; 


struct stLookupTableElement
{
    uint16_t SaveDataOffset; 
    uint8_t SaveDataBitoffset;
    uint8_t IsDone;
    uint16_t SavedataMask;
    uint8_t ItemID; //only for required progressables and Rutos Letter
    uint8_t Sphere;
};

struct stNaviHintCyclicGlobals
{
    uint32_t Timer1;
    uint32_t showTextFlag; 
    uint32_t MaxTime; // value comes from python patched ROM Patches.py
    struct stLookupTableElement* LastLookupTableAddress; 
    uint32_t LastTextIDOffset;
    uint32_t Timer2;  // only for reducing CPU Load
};
    

uint8_t CheckByItemID(uint16_t MaskedSaveDataHalfWord, uint8_t ItemID);
uint8_t Navi_SaveProgress(struct stLookupTableElement* pLookupTableBase, struct stNaviHintCyclicGlobals* pNaviHintCyclicGlobals);

extern const uint32_t C_SAVE_CONTEXT;  
extern uint32_t WNAVI_CL_SAVEPROGRESS();

// returns: 0xff End of LookupTable; 0:SaveData does not have item; 1: SaveData has item
uint8_t Navi_CheckSaveData(struct stLookupTableElement* pLookupTableElement)
{
    uint8_t IsDone = pLookupTableElement->IsDone;
    
    if(IsDone==0xff)        // End of LookupTable?
        return 0xff;
        
    uint16_t SaveDataByteOffset = pLookupTableElement->SaveDataOffset;

    if(!SaveDataByteOffset) // If SaveDataOffset not there just continue (shouldn't happen)
        return 1;
        
    uint8_t SaveDataBitOffset = pLookupTableElement->SaveDataBitoffset;

    const uint32_t SaveDataBase = (uint32_t)C_SAVE_CONTEXT; 
    uint8_t* pSaveData = (uint8_t*)(SaveDataBase + SaveDataByteOffset);

    uint32_t SaveDataWord = (uint32_t)*(uint32_t*)pSaveData;
    SaveDataWord = SaveDataWord >> SaveDataBitOffset;
    uint16_t SaveDataMask = pLookupTableElement->SavedataMask;
    
    if((SaveDataWord & 0xff) == (0xff))     // SaveData doesn't have Element because its ff?
    {
        return 0;
    }
    
    uint16_t MaskedSaveDataHalfWord = SaveDataWord & SaveDataMask;
    
    
    //ItemID checks are only for required progressables and Rutos Letter
    uint8_t ItemID = pLookupTableElement->ItemID;
    if(ItemID)
    {
        return CheckByItemID(MaskedSaveDataHalfWord, ItemID);
    }
    
    if(MaskedSaveDataHalfWord)      // The normal check by Masked Savedata
        return 1;
    
    return (MaskedSaveDataHalfWord != SaveDataMask) && (SaveDataMask==0xffff); // if mask ffff and its not the same as mask, item there 
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


    
uint8_t Navi_has_any_progress_been_made(struct stLookupTableElement* pLookupTableBase, struct stNaviHintCyclicGlobals* pNaviHintCyclicGlobals)
{
    pNaviHintCyclicGlobals->Timer2 = 0;
    
    struct stLookupTableElement* pLookupTableCur = pLookupTableBase;
    
    for(;; pLookupTableCur++ )
    {
        uint8_t IsDone = pLookupTableCur->IsDone;
    
        if(IsDone==0xff)        // End of LookupTable?
        {
            Navi_SaveProgress(pLookupTableBase,pNaviHintCyclicGlobals);
            return 0;
        }
        
        if(Navi_CheckSaveData(pLookupTableCur)==1)  // Item there?
        {
            pLookupTableCur->IsDone |= 1;
        
            if(pLookupTableCur->IsDone == 1)
            {
                //Reset ShowText, Reset Timer, if Item is newly gotten
                pLookupTableCur->IsDone |= 3;
                pNaviHintCyclicGlobals->Timer1 = 0;
                pNaviHintCyclicGlobals->showTextFlag = 0;
            }

        }
    }
    

    return 0;    
}   
    
    
uint8_t Navi_LoadProgress(struct stLookupTableElement* pLookupTableBase, struct stNaviHintCyclicGlobals* pNaviHintCyclicGlobals)
{
    const uint8_t* pSaveDataBase = (uint8_t*)C_SAVE_CONTEXT; 
    uint8_t* pSaveContext_UnusedData_NaviElement = (uint8_t*)(pSaveDataBase + C_Navi_Hints_Save_Offset);
    
    // Load Timer and ShowTextFlag
    pNaviHintCyclicGlobals->Timer1 = *(uint32_t*)pSaveContext_UnusedData_NaviElement;
    pSaveContext_UnusedData_NaviElement = (uint8_t*)(0x1C + pSaveContext_UnusedData_NaviElement); //Next Unused Element
    pNaviHintCyclicGlobals->showTextFlag = pSaveContext_UnusedData_NaviElement[0];
    
    uint8_t CurByteIndex = 1;
    uint8_t CurBitIndex = 0;
    
    //Load Progress
    struct stLookupTableElement* pLookupTableCur = pLookupTableBase;
    
    for(;; pLookupTableCur++ )
    {
        uint8_t IsDone = pLookupTableCur->IsDone;
    
        if(IsDone==0xff)        // End of LookupTable?
        {
            return 0;
        }
            
        if(CurBitIndex >= 8)
        {
            CurBitIndex = 0;
            CurByteIndex++;   
        }
        
        if(CurByteIndex >= 4)
        {
            CurByteIndex = 0;
            pSaveContext_UnusedData_NaviElement = (uint8_t*)(0x1C + pSaveContext_UnusedData_NaviElement); //Next Unused Element
        }
        
        if(pSaveContext_UnusedData_NaviElement[CurByteIndex] & (1 << CurBitIndex))
        {
            pLookupTableCur->IsDone |= 3;
        }
        
        CurBitIndex++;
        
    }
    
    return 0;
}  


uint8_t Navi_SaveProgress(struct stLookupTableElement* pLookupTableBase, struct stNaviHintCyclicGlobals* pNaviHintCyclicGlobals)
{
    const uint8_t* pSaveDataBase = (uint8_t*)C_SAVE_CONTEXT; 
    uint8_t* pSaveContext_UnusedData_NaviElement = (uint8_t*)(pSaveDataBase + C_Navi_Hints_Save_Offset);
    
    // Load Timer and ShowTextFlag
    *(uint32_t*)pSaveContext_UnusedData_NaviElement = pNaviHintCyclicGlobals->Timer1;
    pSaveContext_UnusedData_NaviElement = (uint8_t*)(0x1C + pSaveContext_UnusedData_NaviElement); //Next Unused Element
    pSaveContext_UnusedData_NaviElement[0] = pNaviHintCyclicGlobals->showTextFlag;
    
    uint8_t CurByteIndex = 1;
    uint8_t CurBitIndex = 0;
    
    //Load Progress
    struct stLookupTableElement* pLookupTableCur = pLookupTableBase;
    
    for(;; pLookupTableCur++ )
    {
        uint8_t IsDone = pLookupTableCur->IsDone;
    
        if(IsDone==0xff)        // End of LookupTable?
        {
            return 0;
        }
            
        if(CurBitIndex >= 8)
        {
            CurBitIndex = 0;
            CurByteIndex++;   
        }
        
        if(CurByteIndex >= 4)
        {
            CurByteIndex = 0;
            pSaveContext_UnusedData_NaviElement = (uint8_t*)(0x1C + pSaveContext_UnusedData_NaviElement); //Next Unused Element
        }
        
        if(pLookupTableCur->IsDone)
        {
             pSaveContext_UnusedData_NaviElement[CurByteIndex] |= (1 << CurBitIndex);
        }
        
        CurBitIndex++;
        
    }
    
    return 0;
}  


uint8_t Navi_CyclicLogic(struct stLookupTableElement* pLookupTableBase, struct stNaviHintCyclicGlobals* pNaviHintCyclicGlobals, uint32_t* pTextIDOffset)
{
    pNaviHintCyclicGlobals->Timer2++;
    
    if(pNaviHintCyclicGlobals->Timer2 >= 0xD0)      // about 5s, only to reduce CPU Load
    {
        Navi_has_any_progress_been_made(pLookupTableBase, pNaviHintCyclicGlobals);  // Reset Timer if progress made
    }

    //Timercheck (Timer 1) => otherwise say "I have faith in you..." 
    pNaviHintCyclicGlobals->Timer1++;
    
    if(pNaviHintCyclicGlobals->Timer1 >= pNaviHintCyclicGlobals->MaxTime)      // Max Time is generated from Python part
    {
        // Check Progress made by Timer1, too (since possibly desynced)
        Navi_has_any_progress_been_made(pLookupTableBase, pNaviHintCyclicGlobals);  // Reset Timer if progress made
    }
    
    
    if(pNaviHintCyclicGlobals->Timer1 >= pNaviHintCyclicGlobals->MaxTime)
    {
        //Ok, Timer ok, no progress since a while
        pNaviHintCyclicGlobals->Timer1 = 0;
        
        // Restore
        *pTextIDOffset = pNaviHintCyclicGlobals->LastTextIDOffset;
        pNaviHintCyclicGlobals->showTextFlag = 1;
        
        
        //Manipulate OOT Navi Timer
        uint8_t* pOOTNaviTimer = (uint8_t*)0x8011A608;
        *pOOTNaviTimer = 9; 
        
        struct stLookupTableElement* pLookupTableElementCur = pLookupTableBase;
        uint32_t curTextIDOffset = 1;
        
        for(;; pLookupTableElementCur++ )
        {
            uint8_t IsDone = pLookupTableElementCur->IsDone;
        
            if(IsDone==0 || IsDone==0xFF)        // End of LookupTable or item not got?
            {
                break;
            }
            
            curTextIDOffset++;
        }
        
        if(curTextIDOffset != pNaviHintCyclicGlobals->LastTextIDOffset) // If TextID Changed
        {
            *pTextIDOffset = curTextIDOffset;
            pNaviHintCyclicGlobals->LastTextIDOffset = curTextIDOffset;
            pNaviHintCyclicGlobals->LastLookupTableAddress = pLookupTableElementCur;
        }
        
    }
    else
    {
        // Timer not ok:
        if(pNaviHintCyclicGlobals->showTextFlag == 0)
        {
            *pTextIDOffset = 0;
        }
        
    }
    
    return 0;
}  