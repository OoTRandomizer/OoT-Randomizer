;Accept86 Saria hints repeat
;==================================================================================================
    
    
SARIA_HINTS_GOSSIP_READING:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    ; Get Message ID
    la t1, gossip_Globals   ;accept86 needed for saria
    lw t8, 0x0000 (t1)
    nop


    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop    