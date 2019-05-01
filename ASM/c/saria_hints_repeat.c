//Accept86 Navi Hints
//==================================================================================================
#include "z64.h"

const uint32_t C_Saria_Save_Offset = 0x73C;//(0xD4 + (58 * 0x1C) +0x10); 

uint16_t get_TextID_ByTextPointer(uint32_t TextAddress);
extern const uint32_t C_SAVE_CONTEXT;  


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
    uint32_t* pAddress = (uint32_t*)((uint32_t)pSaveDataBase + C_Saria_Save_Offset);
    pAddress = (uint32_t*)((uint32_t)pAddress + (uint32_t)AddressOffset);
    
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
    

uint16_t get_Next_Gossip_TextID(struct stSariaHintGlobals* pstSariaHintGlobals, uint16_t* pSaria_Gossip_TextID_Table)
{
    const uint8_t* pSaveDataBase = (uint8_t*)C_SAVE_CONTEXT; 
    //C_Saria_Save_Offset
    
    uint8_t* pCurrentAddress = (uint8_t*)(pSaveDataBase + C_Saria_Save_Offset);
    
    uint8_t CurByteIndex = 0;
    uint8_t CurBitIndex = 0;
    
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
            if(i >= pstSariaHintGlobals->intGossipTextIndex)
            {
                pstSariaHintGlobals->intGossipTextIndex = i+1;
                
                return pSaria_Gossip_TextID_Table[i];
            }   //TBD reset on Saveload
            
        }
        
        CurBitIndex++;
    }
    
    
    // End of TextLoop => reset globals
    pstSariaHintGlobals->Activation = 0;
    pstSariaHintGlobals->intGossipTextIndex = 0;
    pstSariaHintGlobals->justDeactivated = 1;

    return 0x00e3;  //TextID - Do you want to talk to Saria again?
}