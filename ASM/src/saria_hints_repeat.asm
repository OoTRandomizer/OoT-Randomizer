;Accept86 Saria hints repeat
;==================================================================================================


saria_hints_Button_Hook:
    addiu   sp, sp, -0x24
    sw      ra, 0x0014(sp)
    sw      t2, 0x0018(sp)
    sw      at, 0x001C(sp)
    sw      t8, 0x0020(sp)
    
    ; displaced code
 beq t8, at, @@saria_hints_Button_jump    
    lw t1, 0x0004 (t9)
    sll t2, t1, 15
    sw t2, 0x0018(sp)
 bgez t2, @@saria_hints_Button_END
    nop
    
@@saria_hints_Button_jump:    
    jal @SARIA_HINTS_GOSSIP_READING
    nop
    
    
@@saria_hints_Button_END:
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    lw      t2, 0x0018(sp)
    lw      at, 0x001C(sp)
    lw      t8, 0x0020(sp)
    addiu   sp, sp, 0x24
    jr ra
    nop
    
    
    
    
    
@SARIA_HINTS_GOSSIP_READING:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    ; Get Message ID
    lh      t7, 0x001C(s0)
    andi    t8, t7, 0x00FF
    nop
    

    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop    