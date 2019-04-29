;Accept86 WorkingNavi / Saria Repeats hints
;==================================================================================================

;.global TABLE_START     
;.global TABLE_START_RAM   
;.global TEXT_START    
;.global Navi_Hints_TextID_Base
;.global SARIA_HINTS_CONDITION  
;.global NAVI_HINTS_CONDITION     
;.global SARIA_HINTS_GOSSIP_READING  
;.global CyclicLogic_ResetText
;.global navi_hints_TextIDOffsetGlobal    ;for use in C
;.global Navi_Hints_cyclicLogicGlobals    ;for use in C




;TextTables for NaviHints / Saria
TABLE_START  equ 0xB849EC
C_TABLE_START:
.word TABLE_START

TABLE_START_RAM  equ 0x8010EA8C
C_TABLE_START_RAM:
.word TABLE_START_RAM

TEXT_START  equ 0x92D000
C_TEXT_START:
.word TEXT_START

Navi_Hints_TextID_Base equ 0x7400
C_Navi_Hints_TextID_Base:
.word Navi_Hints_TextID_Base




TextLoadLogic_HOOK:
    addiu   sp, sp, -0x24
    sw      ra, 0x0014(sp)
    sw      a2, 0x0018(sp)
    sw      a1, 0x001c(sp)
    sw      a0, 0x0020(sp)
    
    jal     TextLoadLogic_handling  ; done in C
    nop
    
    
    lw      a2, 0x0018(sp)
    lw      a1, 0x001c(sp)
    lw      a0, 0x0020(sp)
    jal 0x80000DF0          ;DMALoad Text in
    nop
     
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x24
    jr      ra
    nop

    
    
CyclicLogic_ResetText:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    ;The TextOutput is handled normally  
    ;Reset TextIDOffset stuff(cyclic logic), so the message isnt shown twice 
    ;Store TextIDOffset (Reset) 
    ;ShowTextFlag (Reset)  
     
    la t1, navi_hints_TextIDOffsetGlobal
    sw r0, 0x0000 (t1)                  
                                         
    la t2, navi_hints_cyclicLogicGlobals 
    sw r0, 0x0004 (t2)                   
                                         
    jal get_TextID_ByTextPointer        
    li t0, Navi_Hints_TextID_Base   
    
    ;if Text says 'I have faith in you..' Textpointer is on base, dont reset timer 
    ;Timer1 Reset <= TBD test this      
                             
    sw t3, 0x0000 (t2)                  
                                        
                
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr      ra
    nop



