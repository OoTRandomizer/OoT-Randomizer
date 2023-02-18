
blue_fire_arrows:
    addiu   at, zero, 0x0016 ; sets at to arrow actor id
    bne     t9, at, @@return ; return if actor isn't an arrow
    addiu   at, zero, 0x0004 ; sets at to arrow type for ice arrows
    jr ra
    lh      t9, 0x1C(v1) ; load arrow type from actor - 4 for ice arrows

@@return:
    jr ra
    addiu at, zero, 0x00F0 ; set at to blue fire actor id
