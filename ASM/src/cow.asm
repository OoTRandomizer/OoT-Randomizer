cow_item_hook:
    lw      a0, 0x0020 (sp)
    nop
    lh      a2, 0x014 (a0) ; Load cow id
    addiu   a2, a2, 0x0014 ; give item id = cow id + milk:q
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
