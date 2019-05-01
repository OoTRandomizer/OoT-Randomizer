;Accept86 WorkingNavi / Saria Repeats hints
;==================================================================================================


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

;other Navi/Saria constant words
NAVI_HINTS_TEXTID_BASE:
.word 0         ;coming from python

C_SAVE_CONTEXT:
.word SAVE_CONTEXT


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
    sw r0, 0x0000 (t1)                      ;Reset TextID              
                                         
    la t2, navi_hints_cyclicLogicGlobals 
    sw r0, 0x0004 (t2)                      ;Reset showTextFlag              
                          
                          
    ;if Text says 'I have faith in you..' Textpointer is on base, dont reset timer 
    ;Timer1 Reset                           
    lw t0, Navi_Hints_TextID_Base     
 beq t0, a0, @@DONT_RESET_TIMER   
    nop
                          
    sw r0, 0x0000 (t2)  
    lui t2, 0x8011
    ori t2, 0xA608
    ori t3, r0, 0x000D   ;Manipulate OOT Navi Timer
    sb t3, 0x0000 (t2)                
    
    @@DONT_RESET_TIMER:
                                        
                
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr      ra
    nop



