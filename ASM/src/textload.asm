;Accept86 WorkingNavi / Saria Repeats hints
;==================================================================================================

TextLoadLogic_HOOK:
    addiu   sp, sp, -0x1c
    sw      ra, 0x0014(sp)
    sw      a2, 0x0018(sp)
    
;====Saria Repeats Hints==== ;TBD only if activated
;I want to make sure the Saria Texts get actually displayed before saving the id
;The Textpointer borders can change on every seed/version, so I have to dynamicly read them


    jal @checkGossipText
    nop
    
 beq v0, r0, @@TEXTLOAD_WNAVI      ;BRANCH if Textpointer < Max 
    nop
    
;=>Gossip Text, save for saria
    jal SARIA_HINTS_GOSSIP_READING
    nop
    J @@TLL_LOAD_TEXT
    nop
    
    
@@TEXTLOAD_WNAVI:    
;====Working Navi=====   ;TBD only if activated
    ori a2, r0, 0x0141                  ;navi Text ID low
    jal @get_TextTablePointer_ByID
    nop      
    slt t1, t3, a1          ;comparison, A1 = requested Textloadpointer of the game

 beq t1, r0, @@TLL_LOAD_TEXT      ;BRANCH if reqested Textpointer A1 < Min NaviSection: Jump LOAD_TEXT
    nop
    
    ori a2, r0, 0x015f                  ;navi Text ID high
    jal @get_TextTablePointer_ByID
    nop      
    slt t1, a1, t3          ;A1 < T3 (Max) req Textpointer A1 < Max NaviSection

 beq t1, r0, @@TLL_LOAD_TEXT      ;BRANCH if Textpointer < Max => Jump LOAD_TEXT
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


@get_TextTablePointer_ByID:     ;arguments: a2 is the Text ID

    li t1, TABLE_START_RAM
    
@@get_TextTablePointer_ByID_inc:
    addiu t1, t1, 8 
    lh t3, 0x0000 (t1)
 bne t3, a2, @@get_TextTablePointer_ByID_inc 
    nop

    lw t3, 0x0004 (t1)
    lui t5, 0x00ff
    ori t5, t5, 0xffff
    and t3, t3, t5
    li t4, TEXT_START
    addu t3, t3, t4
    
    jr ra
    nop
    
    
    

    
get_TextID_ByTextPointer: ; arguments: a1 is Textpointer to find

    li t1, TABLE_START_RAM

    lui t7, 0x0000
    j @@get_SariaIndexOffset_ByID_initjump
    nop
@@get_TextID_ByTextPointer_inc2:
    addiu t1, t1, 8 
@@get_SariaIndexOffset_ByID_initjump:
    lw t3, 0x0004 (t1)
    lui t5, 0x00ff
    ori t5, t5, 0xffff
    and t3, t3, t5
    li t4, TEXT_START
    addu t3, t3, t4
    
 bne t3, a1, @@get_TextID_ByTextPointer_inc2 
    nop
    
    ;we found our table entry
    lh t3, 0x0000 (t1)
    
    
    jr ra
    nop
    
    
    
@checkGossipText:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)

    lui v0, 0x0000
    
    jal get_TextID_ByTextPointer
    nop      
    move a2, t3                         ;a2 has the textID
    
    ori t2, r0, 0x0401                  ;gossip Text ID low
    slt t1, t2, t3        

 beq t1, r0, @@checkGossipText_NOK      ;BRANCH if reqested Textpointer A1 < Min
    nop
    
    ori t2, r0, 0x04FF                  ;gossip Text ID high    
    slt t1, t3, t2   
    
  beq t1, r0, @@checkGossipText_NOK      ;BRANCH if reqested Textpointer A1 < Min
    nop     

    ori v0, r0, 0x0001
@@checkGossipText_NOK:

    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop




