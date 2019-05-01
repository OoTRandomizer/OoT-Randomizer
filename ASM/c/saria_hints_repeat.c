//Accept86 Navi Hints
//==================================================================================================
#include "z64.h"

const uint32_t C_Saria_Save_Offset = 0xD4 + (58 * 0x1C) +0x10; 

uint16_t get_TextID_ByTextPointer(uint32_t TextAddress);



uint8_t get_SariaIndexOffset_ByTextAddress(uint16_t* pSaria_Gossip_TextID_Table, uint32_t ROMTextAddress)
{
    uint16_t TextID = get_TextID_ByTextPointer(ROMTextAddress);

    uint16_t i;
    for(i=0;i<42;i++)
    {
        if(pSaria_Gossip_TextID_Table[i] == TextID)
            break;
    }
    
    return i;
}


uint8_t Saria_Gossip_Saveprogress(uint32_t IndexOffset)
{
    const uint32_t* pSaveDataBase = (uint32_t*)C_SAVE_CONTEXT; 
    //C_Saria_Save_Offset
    
    uint8_t PageOffset = IndexOffset >> 5; // equals /32
    uint8_t BitOffset = IndexOffset & 0x1F;  // equals % 32
    
    //calc byte to save
    uint16_t AddressOffset = PageOffset * 0x1C;
    uint32_t* pAddress = (uint32_t*)(pSaveDataBase + C_Saria_Save_Offset + AddressOffset);
    
    *pAddress = *pAddress | (0x80000000 >> BitOffset);  
    
    return 0;    
}


struct stSariaHintGlobals
{
    uint32_t lastTextID; 
    uint32_t intGossipTextIndex;
    uint32_t Activation;
    uint32_t justDeactivated;
};
    

uint16_t get_Next_Gossip_TextID(struct stSariaHintGlobals* pstSariaHintGlobals)
{
    const uint8_t* pSaveDataBase = (uint32_t*)C_SAVE_CONTEXT; 
    //C_Saria_Save_Offset
    
    uint8_t* pCurrentAddress = (uint8_t*)(pSaveDataBase + C_Saria_Save_Offset);
    
    uint8_t CurByteIndex = 0;
    uint8_t CurBitIndex = 0;
    
    uint8_t CurIntGossipTextIndex;
    
    uint16_t i;
    for(i=0;i<42;i++)
    {    
        if(CurBitIndex >= 8)
        {
            CurBitIndex = 0;
            CurByteIndex++;   
        }
        
        if(CurByteIndex >= 4)
        {
            CurByteIndex = 0;
            pCurrentAddress = (uint8_t*)(0x1C + pCurrentAddress); //Next Unused Element
        }
        
        if(pCurrentAddress[CurByteIndex] & (0x80 >> CurBitIndex))
        {
            CurIntGossipTextIndex++;
            
            if(CurIntGossipTextIndex > pstSariaHintGlobals->intGossipTextIndex)
            {
                pstSariaHintGlobals->intGossipTextIndex = CurIntGossipTextIndex;
                
                return pSaria_Gossip_TextID_Table[CurIntGossipTextIndex];
            }   //TBD reset on Saveload
        }
        
        CurBitIndex++;
    }
    
    
    ;set TextID
    ori v0, r0, 0x00e3  ;Do you want to talk to Saria again?
    sw r0, 0x0008 (t1)  ;reset activation
    sw r0, 0x0004 (t1)  ;reset lastIndex
    ori t2, r0, 0x0001
    sw t2, 0x000C (t1)  ;set just deactiveted
    


    return 0;
}