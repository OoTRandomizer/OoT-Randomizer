//Accept86 Navi Hints
//==================================================================================================
#include "z64.h"

uint8_t CheckByItemID(uint16_t MaskedSaveDataHalfWord, uint8_t ItemID);

extern const uint32_t C_SAVE_CONTEXT;  



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

    
    
uint8_t Navi_has_any_progress_been_made()
{

    return 0;    
}   
    
 
    
    
/*
;_______Subroutine2_______
@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE:
    addiu   sp, sp, -0x1c
    sw      ra, 0x0014(sp)
    


    la t1, Navi_Hints_cyclicLogicGlobals
    lui t3, 0x0000
    sw t3, 0x0014 (t1)       ;Reset global variable 6 (Timer2)
    
    la t7, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM

    J @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_INITJUMP
    nop
    
    
    
@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_GOT_ITEM:  
    lui t6, 0x0000
    lb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    ori t6, t6, 0x0001       ;Save Flag for gotten Item
    sb t6, 0x0003 (t7)
    
    ori t3, r0, 0x0001
    
; Reset ShowText, Reset Timer, if Item is newly gotten
 bne t6, t3, @@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_NO_TIMERRESET
    nop
    ori t6, t6, 0x0003       ;Save Flag for gotten Item "before"
    sb t6, 0x0003 (t7)
    
    la t4, Navi_Hints_cyclicLogicGlobals
    lui t3, 0x0000
    sw t3, 0x0004 (t4) ;Reset ShowTextFlag
    sw t3, 0x0000 (t4) ;Reset Timer1 (NaviDelay)
@@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_NO_TIMERRESET:    
    
@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_ITEM_NOT_GOTTEN:
    addiu t7, t7, 0x0008     ; 0x0004     ;Increment LookupTablePointer
    
@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_INITJUMP:     

    ori t3, r0, 0x00ff
    lb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    andi t6, t6, 0x00ff      ;BitMaskFilter
    
 beq t3, t6, @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_END ; Escape at end of loop <= THIS IS THE RETURN OUT
    nop
    

    ;li a1, @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_GOT_ITEM     ; A1: Item Got Jump Address
    move a0, t7                                 ; t7 LookupTablePointer
    sw      t7, 0x0018(sp)
    JAL @WNAVI_CL_CHECKSAVEDATA                  ;checks save Data for LookupTableEntry
    nop
    lw      t7, 0x0018(sp)
    
 beq r0, v0, @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_ITEM_NOT_GOTTEN
    nop
    
    ori t9, r0, 1
 beq t9, v0, @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_GOT_ITEM
    nop
    
@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_END:  

    jal @WNAVI_CL_SAVEPROGRESS       ; <== Save progress in save, this is called every minute
    nop
    
    
    
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x1c
    
    J  @WNAVI_AFTER_CL_HAS_ANY_PROGRESS_BEEN_MADE
    nop
*/
    