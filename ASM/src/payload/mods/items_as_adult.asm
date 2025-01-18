stick_as_adult:
    la      t8, SAVE_CONTEXT
    lw      t8, 0x04(t8)       ; Link age
    bnez    t8, @@return       ; Return if child
    nop
    la      t2, empty_dlist    ; Load empty display list if adult
@@return:
    addiu   t8, v1, 0x0008     ; displaced code
    jr      ra
    sw      t8, 0x02C0(t7)     ; displaced code

masks_as_adult:
    la      t7, SAVE_CONTEXT
    lw      t7, 0x04(t7)       ; Link age
    bnez    t7, @@return       ; Return if child
    nop
    la      t6, empty_dlist    ; Load empty display list if adult
@@return:
    sw      t6, 0x0004(v0)
    jr      ra
    lb      t7, 0x013F(s0)
