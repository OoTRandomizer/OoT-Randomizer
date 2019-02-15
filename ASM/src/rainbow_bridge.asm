rainbow_bridge:
    lw        t2, RAINBOW_BRIDGE_CONDITION
    beq       t2, r0, @@rainbow_bridge_open
    li        at, 1
    beq       t2, at, @@return
    li        at, 0x3F ; medallions

    li        at, 2
    beq       t2, at, @@rainbow_bridge_dungeons
    nop     

    li        at, 3
    beq       t2, at, @@return
    lui       at, 0x1C ; stones 0x1C0000

    li        at, 4
    beq       t2, at, @@rainbow_bridge_vanilla
    li        at, 0x18 ; shadow and spirit medallions

    li        at, 5
    beq       t2, at, @@rainbow_bridge_tokens
    nop

@@rainbow_bridge_dungeons:
    li        at, 0x1C003F ; stones and medallions
    jr        ra
    and       t2, v0, at

@@rainbow_bridge_vanilla:
    and       t2, v0, at
    bne       t2, at, @@return
    nop
    lbu       t7, 0x84(a3) ; Light arrow slot
    li        t2, 0x12 ; light arrow item id
    beq       t2, t7, @@return
    nop
    li        at, 0xFFFF

@@return:
    jr        ra
    and       t2, v0, at

@@rainbow_bridge_tokens:
    li        at, 0
    lh        t7, 0xD0(a3) ; Gold Skulltulas
    jr        ra
    slti      t2, t7, 0x64

@@rainbow_bridge_open:
    li        t2, 0
    jr        ra
    li        at, 0
