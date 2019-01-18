cow_item_hook:
    lw      a0, 0x0020 (sp)
    nop
    lh      a2, 0x014 (a0) ; Load cow id (1 or 2)
    lb      t0, 0x1D44 (a1) ; Load scene collect flag
    and     at, a2, t0
    bnezl    at, @@return
    addiu   a2, r0, 0x50 ; Give milk if scene flag is set
    or      t0, t0, a2
    sb      t0, 0x1D44 (a1)
    addiu   a2, a2, 0x0014 ; give item id = cow id + milk
@@return:
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
