disable_trade_timers:
    sw      r0, 0x753C(at) ; displaced
    lbu     at, DISABLE_TIMERS
    beqz    at, @@return
    la      at, GLOBAL_CONTEXT
    lhu     at, 0x1D2C(at)
    andi    at, at, 0x00C0 ; temp switch flags 0x16 & 0x17
    bnez    at, @@return ; don't disable timers during collapse sequence
    nop
    j       0x80073930 ; skip storing new timer state
    nop
@@return:
    j       0x80073914 ; back to the normal code.
    nop
