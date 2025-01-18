dampe_fix:
    lw      t2, 0x1D44(s1) ; Scene Collection Flags
    andi    t2, t2, 0x0100
    bnez    t2, @@received_hp
    nop
    lw      t2, 0x1D48(s1) ; Temporary Collection Flags
    andi    t2, t2, 0x0100
    bnez    t2, @@no_hp
    nop
    lw      at, 0x1d48(s1)
    ori     t2, at, 0x0100
    sw      t2, 0x1d48(s1)
    b       @@return
    and     t2, r0, r0

@@received_hp:
    addiu   t4, r0, 0x0000

@@no_hp:
    ori     t2, r0, 0x0001

@@return:
    jr      ra
    nop
