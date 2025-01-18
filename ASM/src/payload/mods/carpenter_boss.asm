;Manually set three variables needed to ensure correct dialog state when receiving item from the Carpenter Boss

prevent_carpenter_boss_softlock:
    la      t0, 0x801D2578   ;msgCtx+8000
    li      t1, 0x6C
    lw      t2, 0x6300(t0)
    beq     t1, t2, @@return ;if msgCtx+E300‬ is 0x6C its too early, return
    li      t2, 0x01
    li      t3, 0x36
    sw      t2, 0x6300(t0)   ;msgCtx+0xE300‬
    sb      t3, 0x6304(t0)   ;msgCtx+0xE304
    li      t4, 0xFFFFFFFF
    lb      t6, 0x63E7(t0)
    bne     t6, t4, @@return ;if msgCtx+0xE3E7‬ is 0xFF, set it to 0x02
    li      t5, 0x02
    sb      t5, 0x63E7(t0)   ;msgCtx+0xE3E7

    @@return:
    jr      ra
    addiu   a2, r0, 0x22     ;displaced
