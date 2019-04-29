#include "z64.h"


extern const uint32_t SARIA_HINTS_CONDITION;  
extern const uint32_t NAVI_HINTS_CONDITION;  

extern uint32_t SARIA_HINTS_GOSSIP_READING(uint32_t unknown, uint32_t TextAddress, uint32_t TextID);

extern const uint32_t C_TABLE_START;  
extern const uint32_t C_TABLE_START_RAM;  
extern const uint32_t C_TEXT_START;  

extern uint32_t CyclicLogic_ResetText();

uint16_t get_TextID_ByTextPointer(uint32_t TextAddress);


uint8_t TextLoadLogic_handling(uint32_t unknown, uint32_t TextAddress, uint32_t TextLength)
{
    
    if(SARIA_HINTS_CONDITION)
    {
        uint16_t TextID = get_TextID_ByTextPointer(TextAddress);
    
        if((TextID>=0x0401) && (TextID<=0x04FF))        // gossip hints TextID-Borders
        {
            SARIA_HINTS_GOSSIP_READING(0, TextAddress, TextID);
        }
    }
    
    if(NAVI_HINTS_CONDITION)
    {
        uint16_t TextID = get_TextID_ByTextPointer(TextAddress);
    
        if((TextID>=0x0141) && (TextID<=0x015f) )       // Navi Text TextID-Borders
        {
            //The TextOutput is handled normally  
            //Reset TextIDOffset stuff(cyclic logic), so the message isnt shown twice 
            //Store TextIDOffset (Reset) 
            //ShowTextFlag (Reset)  
            //if Text says 'I have faith in you..' Textpointer is on base, dont reset timer 
            //Timer1 Reset <= TBD test this  
            CyclicLogic_ResetText();
        }
    }
    
}






uint16_t get_TextID_ByTextPointer(uint32_t TextAddress)
{
    uint8_t* curTableAddress = (uint8_t*)(uint32_t)C_TABLE_START_RAM;

    while(1)
    {
        uint32_t TextOffset = (uint32_t)(*(uint32_t*)(curTableAddress+4));
        TextOffset &= 0xffffff;
        
        if((TextOffset+(uint32_t)C_TEXT_START)==(TextAddress&0xffffffff))
            break;
        
        curTableAddress += 8;
    }
    
    uint32_t TextID = (uint32_t)(*(uint16_t*)(curTableAddress));

    return TextID;
}



    
