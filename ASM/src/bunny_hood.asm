SPEED_MULTIPLIER:
    .float 1.0

bunny_hood :
    ori     t0, r0, 0x04
    la      t1, GLOBAL_CONTEXT
    lw      t1, 0x1C44(t1)  ; Player in actor instance table
    beqz    t1, @@return
    nop

    l.s     f22, SPEED_MULTIPLIER
    nop
    mul.s   f12, f12, f22

    lbu     t1, 0x14f(t1)   ; Worn Mask
    bne     t0, t1, @@return
    mtc1    t7, f4          ; Displaced
 
    lui     t0, 0x40B0
    bne     t0, a1, @@return
    nop

    lui     t0, 0x3fc0
    mtc1    t0, f22         ; f22 = 1.5
    nop
    mul.s   f12, f12, f22   ; f12 = 1.5 * horizontal velocity

@@return:
    nop
    mfc1    a1, f12; Displaced
    jr      ra
    nop