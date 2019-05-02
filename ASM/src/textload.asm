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



NaviSaria_Hints_Extended_Init_On_Saveloads_HOOK: ;<= Hook on Saveloads
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    lw t2, NAVI_HINTS_CONDITION
 beq t2, r0, @@SARIA_CHECK
    nop
    
    ; Init global variables (for cyclic logic)
    la t1, Navi_Hints_TextIDOffsetGlobal
    sw r0, 0x0000 (t1)       ;Store T0 in Global Variable 5 TextID-Offset
   
    la t7, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE
                                    ;global variable 1 (Timer), 2 (showtextflag), 
    la t1, Navi_Hints_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    ori t0, r0, 1  ;The TextID-Offset Backup is not on "I have faith in you..." but on the first real hint
    sw t0, 0x0010 (t1)
    sw t7, 0x000C (t1)
    sw r0, 0x0014 (t1)       ;reset global variable 6 (Timer2)
    
    
    jal WNAVI_CL_LOADPROGRESS  ; Load progress from save
    nop
    
    
@@SARIA_CHECK:    
    lw t2, SARIA_HINTS_CONDITION
 beq t2, r0, @@EXTENDED_INIT_END
    nop
    
    la a0, Saria_Hints_Globals
    jal Saria_ResetOnSaveload
    nop
    
    
@@EXTENDED_INIT_END:
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop

