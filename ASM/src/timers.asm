disable_trade_timers:
    sw      r0, 0x753C(at) ; displaced
    la      at, DISABLE_TIMERS
    lbu     at, 0(at)
    beqz    at, @@return
    nop
    j       0x80073930 ; skip storing new timer state
    nop
@@return:
    j       0x80073914 ; back to the normal code. 
    nop

disable_collapse_timer:
    la      at, DISABLE_TIMERS
    lbu     at, 0x00(at)
    beqz    at, @@return
    sw      r0, 0x0018(sp) ; displaced
    addiu   ra, ra, 0x08
    nop
@@return:
    jr      ra
    swc1    f2, 0x0010(sp) ; displaced