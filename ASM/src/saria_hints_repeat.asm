;Accept86 Saria hints repeat
;==================================================================================================
    
    
SARIA_HINTS_GOSSIP_READING:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    ; Get Message Text Index offset
    move a2, a1
    jal @get_SariaIndexOffset_ByTextPointer
    nop


    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop    
    
    
    
@get_SariaIndexOffset_ByTextPointer: ; arguments: a2 is gossip Textpointer to find

    li t1, TABLE_START_RAM
    ori t2, r0, 0x0008
    ori t4, r0, 0x0401  ;TextStart GossipTexts
    
@@get_SariaIndexOffset_ByID_inc:
    addiu t1, t1, 8 
    lh t3, 0x0000 (t1)
 bne t3, t4, @@get_SariaIndexOffset_ByID_inc 
    nop
    
    lui t7, 0x0000
    j @@get_SariaIndexOffset_ByID_initjump
    nop
@@get_SariaIndexOffset_ByID_inc2:
    addiu t1, t1, 8 
@@get_SariaIndexOffset_ByID_initjump:
    lw t3, 0x0004 (t1)
    lui t5, 0x00ff
    ori t5, t5, 0xffff
    and t3, t3, t5
    li t4, TEXT_START
    addu t3, t3, t4
    addiu t7, t7, 0x0001
    
 bne t3, a2, @@get_SariaIndexOffset_ByID_inc2 
    nop
    
    ;now in t7 is the indexoffset
    
    jr ra
    nop
    
    