cow_item_hook:
    lw      a0, 0x0020 (sp)
    lb      t0, SHUFFLE_COWS
    addiu   a2, r0, 0x50 ; Give milk if cows are not randomized
    beqz    t0, @@return
    nop
    lh      a2, 0x014 (a0) ; Load cow id (1 or 2)
    lb      t0, 0x1D44 (a1) ; Load scene collect flag
    and     t3, a2, t0
    bnezl   t3, @@return
    addiu   a2, r0, 0x50 ; Give milk if scene flag is set
    or      t0, t0, a2
    sb      t0, 0x1D44 (a1)
    addiu   a2, a2, 0x0014 ; give item id = cow id + milk
@@return:
    jr      ra
    nop

cow_bottle_check:
    addiu   sp, sp, -0x10
    sw      ra, 0x04 (sp)
    sw      t0, 0x08 (sp)
    sw      t1, 0x0C (sp)

    lb      t0, SHUFFLE_COWS
    beqz    t0, @@bottle_check
    nop
    lh      t0, 0x014 (s0)
    lb      t1, 0x1D44 (s1)
    and     t0, t0, t1 ; Get flag for cow
    addiu     v0, r0, 0x1 ; Default to has a bottle
    beqz    t0, @@return ; Dont check for bottle if the collect flag is not set
    nop
@@bottle_check:
    jal     0x80071A94
    nop
@@return:
    lw      ra, 0x04 (sp)
    lw      t0, 0x08 (sp)
    lw      t1, 0x0C (sp)
    addiu   sp, sp, 0x10
    jr      ra
    nop

cow_after_init:
    lw      s0, 0x0034 (sp) ; Displaced
    lh      t0, 0xB4 (a0)
    beqz    t0, @@return
    nop
    sh      t0, 0x4A8 (a0)
    sh      r0, 0xB0 (a0)
@@return:
    jr      ra
    nop
