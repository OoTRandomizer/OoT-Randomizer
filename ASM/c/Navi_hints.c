//Accept86 Navi Hints
//==================================================================================================
#include "z64.h"

uint8_t CheckByItemID(uint16_t MaskedSaveDataHalfWord, uint8_t ItemID);

extern const uint32_t C_SAVE_CONTEXT;  
extern uint32_t WNAVI_CL_SAVEPROGRESS();

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

    
struct stNaviHintCyclicGlobals
{
    uint32_t Timer1;
    uint32_t showTextFlag; 
    uint32_t MaxTime; // value comes from python patched ROM Patches.py
    uint32_t LastLookupTablePointer; 
    uint32_t LastTextTablePointer;
    uint32_t Timer2;  // only for reducing CPU Load
};
    
    
uint8_t Navi_has_any_progress_been_made(struct stLookupTableElement* pLookupTableBase, struct stNaviHintCyclicGlobals* pNaviHintCyclicGlobals)
{
    pNaviHintCyclicGlobals->Timer2 = 0;
    
    struct stLookupTableElement* pLookupTableCur = pLookupTableBase;
    
    for(;; pLookupTableCur++ )
    {
        uint8_t IsDone = pLookupTableCur->IsDone;
    
        if(IsDone==0xff)        // End of LookupTable?
        {
            WNAVI_CL_SAVEPROGRESS();
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
  
    
/*
@WNAVI_CL_LOADPROGRESS:
                                             ;global variable 1 (Timer), 2 (showTextFlag), 
    la t1, Navi_Hints_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    
    li   t4, SAVE_CONTEXT 
    
    ; load timer from save  
    lw  t6, (Navi_Hints_Save_Offset)(t4)
    sw t6, 0x0000 (t1)       ;save global variable timer
    ;addiu t4, t4, 4
    ;here we go to the next unused savedata section
    addiu t4, t4, 0x1C  
    
    ; store show text flag
    lbu  t6, (Navi_Hints_Save_Offset)(t4)
    sw t6, 0x0004 (t1)
    addiu t4, t4, 1
    
    
    ;load progress bits    
    la t7, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM
    lui t5, 0x0000
    lb  t8, (Navi_Hints_Save_Offset)(t4)
    
    J @WNAVI_CL_LOADPROGRESS_INITJUMP
    nop
    
    
@WNAVI_CL_LOADPROGRESS_NEXT:    
    
    addiu t7, t7, 0x0008     ; 0x0004     ;Increment LookupTablePointer
    addiu t5, t5, 1
    
@WNAVI_CL_LOADPROGRESS_INITJUMP:     

    ori t3, r0, 0x00ff
    lb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    andi t6, t6, 0x00ff
    
 beq t3, t6, @WWNAVI_CL_LOADPROGRESS_END ; Escape at end of loop <= THIS IS THE RETURN OUT
    nop
    
    lui t6, 0x0000
    sb t6, 0x0003 (t7)       ;Reset "IsDone" Part of LookupTable-Element
    
; here we load our progress
   slti t3, t5, 8     ; t5 bitindex still ok?
 bne t3, r0, @@WNAVI_CL_LOADPROGRESS_NO_NEXTBYTE
   nop
   
   ; if a byte is complete, next one
   lui t5, 0x0000
   addiu t4, t4, 1
   
   andi t9, t4, 0x0003
 bne t9, r0, @@WNAVI_CL_LOADPROGRESS_NO_NEXTBYTE    ; if t4 bytecount modulo 4 is 0 => next unused savedata section
   nop
   ;here we go to the next unused savedata section
   addiu t4, t4, (0x1C-4)  
   
@@WNAVI_CL_LOADPROGRESS_NO_NEXTBYTE:

   lb  t8, (Navi_Hints_Save_Offset)(t4)

;here we check our t8 progress-saveflag-bits
    ori t9, r0, 1
    sllv t9, t9, t5
    and t8, t8, t9

 beq r0, t8, @WNAVI_CL_LOADPROGRESS_NEXT  
    nop
;bit set for this lookuptableentry
    ori t6, r0, 0x0003
    sb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    
    J @WNAVI_CL_LOADPROGRESS_NEXT
    nop
   
@WWNAVI_CL_LOADPROGRESS_END: 

    ;dont overwrite ff end of lookuptable
    ;andi t8, t8, 0x00ff      ;BitMaskFilter
    ;sb t8, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    
    

    jr ra
    nop    
*/
 
    