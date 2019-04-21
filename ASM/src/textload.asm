;Accept86 WorkingNavi / Saria Repeats hints
;==================================================================================================

TABLE_START  equ 0xB849EC
TABLE_START_RAM  equ 0x8010EA8C
TEXT_START  equ 0x92D000

TextLoadLogic_HOOK:
    addiu   sp, sp, -0x1c
    sw      ra, 0x0014(sp)
    sw      a2, 0x0018(sp)
    
;====Saria Repeats Hints==== ;TBD only if activated
;I want to make sure the Saria Texts get actually displayed before saving the id
;The Textpointer borders can change on every seed/version, so I have to dynamicly read them


    ori a2, r0, 0x0401                  ;gossip index low
    jal @get_TextTablePointer_ByIndex
    nop      
    slt t1, t3, a1         
    lui t2, 0x0000          ;just 0 in T2 for using with compares    
 
 beq t1, t2, @@TEXTLOAD_WNAVI      ;BRANCH if reqested Textpointer A1 < Min
    nop
    
    ori a2, r0, 0x04FF                  ;gossip index high
    jal @get_TextTablePointer_ByIndex
    nop
    slt t1, a1, t3          ;A1 < T3 (Max) req Textpointer A1 < Max 
    lui t2, 0x0000          ;just 0 in T2 for using with compares    
 
 beq t1, t2, @@TEXTLOAD_WNAVI      ;BRANCH if Textpointer < Max 
    nop
    
;=>Gossip Text, save for saria
    jal SARIA_HINTS_GOSSIP_READING
    nop
    J @@TLL_LOAD_TEXT
    nop
    
    
@@TEXTLOAD_WNAVI:    
;====Working Navi=====   ;TBD only if activated
    lui t3, 0x0093          ; TBD why did this value change since Rando 1.0?
    ori t3, t3, 0x2ea0      ;TextLoadPointerMin old: 0x4af0
    slt t1, t3, a1          ;comparison, A1 = requested Textloadpointer of the game
    lui t2, 0x0000          ;just 0 in T2 for using with compares    
 
 beq t1, t2, @@TLL_LOAD_TEXT      ;BRANCH if reqested Textpointer A1 < Min NaviSection: Jump LOAD_TEXT
    nop
    
    lui t3, 0x0093          ; TBD why did this value change since Rando 1.0?
    ori t3, t3, 0x37ac      ; TextLoadPointer max old: 0x5400
    slt t1, a1, t3          ;A1 < T3 (Max) req Textpointer A1 < Max NaviSection
    lui t2, 0x0000          ;just 0 in T2 for using with compares    
 
 beq t1, t2, @@TLL_LOAD_TEXT      ;BRANCH if Textpointer < Max => Jump LOAD_TEXT
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
 beq t0, a1, @@TLL_LOAD_TEXT
    nop
    
    sw t3, 0x0000 (t2) ;Timer1 Reset


;=======Load Text=======
    
@@TLL_LOAD_TEXT:        ;TARGET LOAD_TEXT
    lw      a2, 0x0018(sp)
    jal 0x80000DF0          ;DMALoad Text in
    nop
    
         
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x1c
    jr      ra
    nop

;==================================================================================================


@get_TextTablePointer_ByIndex:

    li t1, TABLE_START_RAM
    ori t2, r0, 0x0008
    
@@get_TextTablePointer_ByIndex_inc:
    addiu t1, t1, 8 
    lh t3, 0x0000 (t1)
 bne t3, a2, @@get_TextTablePointer_ByIndex_inc 
    nop

    lw t3, 0x0004 (t1)
    lui t5, 0x00ff
    ori t5, t5, 0xffff
    and t3, t3, t5
    li t4, TEXT_START
    addu t3, t3, t4
    
    jr ra
    nop
    
    
    

