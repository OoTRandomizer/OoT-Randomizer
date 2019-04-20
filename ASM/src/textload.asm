;Accept86 WorkingNavi / Saria Repeats hints
;==================================================================================================


TextLoadLogic_HOOK:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    lui t2, 0x0000          ;just 0 in T2 for using with compares    
 
;====Saria Repeats Hints==== ;TBD only if activated
;TEXT_START = 0x92D000
;TABLE_SIZE_LIMIT = 0x43A8  

    lui t3, 0x0092         
    ori t3, t3, 0xD000      
    slt t1, t3, a1         
    
 beq t1, t2, @@TEXTLOAD_WNAVI      ;BRANCH if reqested Textpointer A1 < Min
    nop
    
    lui t3, 0x0093         
    ori t3, t3, 0x13A8     
    slt t1, a1, t3          ;A1 < T3 (Max) req Textpointer A1 < Max 

 beq t1, t2, @@TEXTLOAD_WNAVI      ;BRANCH if Textpointer < Max 
    nop
    
;=>Gossip Text, save for saria
    jal SARIA_HINTS_GOSSIP_READING
    nop
    J @@WNAVI_TLL_LOAD_TEXT
    nop
    
    
@@TEXTLOAD_WNAVI:    
;====Working Navi=====   ;TBD only if activated
    lui t3, 0x0093          ; TBD why did this value change since Rando 1.0?
    ori t3, t3, 0x2ea0      ;TextLoadPointerMin old: 0x4af0
    slt t1, t3, a1          ;comparison, A1 = requested Textloadpointer of the game
    
 beq t1, t2, @@WNAVI_TLL_LOAD_TEXT      ;BRANCH if reqested Textpointer A1 < Min NaviSection: Jump LOAD_TEXT
    nop
    
    lui t3, 0x0093          ; TBD why did this value change since Rando 1.0?
    ori t3, t3, 0x37ac      ; TextLoadPointer max old: 0x5400
    slt t1, a1, t3          ;A1 < T3 (Max) req Textpointer A1 < Max NaviSection

 beq t1, t2, @@WNAVI_TLL_LOAD_TEXT      ;BRANCH if Textpointer < Max => Jump LOAD_TEXT
    nop
    
                            ; T7 Global Variable 5 Textpointer
    la t7, working_navi_TextPointerGlobal
    lw a1, 0x0000 (t7)      ; IF req Textpointer A1 in NaviSection => Load GlobalVar with Text of workingNavi in A1
    ;set dmaloadsize to textsize
    ori a2, r0, WORKING_NAVI_DATA_GENERATED_TEXT_INCREMENT_SYM
    
    ; Reset Textpointer stuff(cyclic logic), so the message isnt shown twice
    la t1, working_navi_TextPointerGlobal
    li t0, WORKING_NAVI_DATA_GENERATED_TEXT_ROM
    sw t0, 0x0000 (t1)       ;Store T0 in Global Variable  Textpointer (Reset)
    la t2, working_navi_cyclicLogicGlobals
    lui t3, 0x0000
    sw t3, 0x0004 (t2) ;ShowTextFlag Reset
    
    
    
    li t0, WORKING_NAVI_DATA_GENERATED_TEXT_ROM     ; if Text says "You are doing so well..." / Textpointer is on base, dont reset timer
 beq t0, a1, @@WNAVI_TLL_LOAD_TEXT
    nop
    
    sw t3, 0x0000 (t2) ;Timer1 Reset



;=======Load Text=======
    
@@WNAVI_TLL_LOAD_TEXT:        ;TARGET LOAD_TEXT
    jal 0x80000DF0          ;DMALoad Text in
    nop
    
         
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr      ra
    nop

;==================================================================================================

