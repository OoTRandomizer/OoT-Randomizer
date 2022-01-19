rainbow_bridge:
    lw        t2, RAINBOW_BRIDGE_CONDITION
    beq       t2, r0, @@open

    li        at, 1
    beq       t2, at, @@medallions

    li        at, 2
    beq       t2, at, @@dungeons

    li        at, 3
    beq       t2, at, @@stones

    li        at, 4
    beq       t2, at, @@vanilla

    li        at, 5
    beq       t2, at, @@tokens

@@open:
    li        at, 0
    jr        ra
    li        t2, 0

@@medallions:
    li        at, 0x3F ; medallions
    and       t2, v0, at
    li        t7, 0
    andi      t8, t2, 0x01
    beqz      t8, @@medallions_1
    nop
    addiu     t7, 1
@@medallions_1:
    andi      t8, t2, 0x02
    beqz      t8, @@medallions_2
    nop
    addiu     t7, 1
@@medallions_2:
    andi      t8, t2, 0x04
    beqz      t8, @@medallions_3
    nop
    addiu     t7, 1
@@medallions_3:
    andi      t8, t2, 0x08
    beqz      t8, @@medallions_4
    nop
    addiu     t7, 1
@@medallions_4:
    andi      t8, t2, 0x10
    beqz      t8, @@medallions_5
    nop
    addiu     t7, 1
@@medallions_5:
    andi      t8, t2, 0x20
    beqz      t8, @@medallions_6
    nop
    addiu     t7, 1
@@medallions_6:
    b         @@count
    nop

@@dungeons:
    li        at, 0x1C003F ; stones and medallions
    and       t2, v0, at
    li        t7, 0
    andi      t8, t2, 0x01
    beqz      t8, @@dungeons_1
    nop
    addiu     t7, 1
@@dungeons_1:
    andi      t8, t2, 0x02
    beqz      t8, @@dungeons_2
    nop
    addiu     t7, 1
@@dungeons_2:
    andi      t8, t2, 0x04
    beqz      t8, @@dungeons_3
    nop
    addiu     t7, 1
@@dungeons_3:
    andi      t8, t2, 0x08
    beqz      t8, @@dungeons_4
    nop
    addiu     t7, 1
@@dungeons_4:
    andi      t8, t2, 0x10
    beqz      t8, @@dungeons_5
    nop
    addiu     t7, 1
@@dungeons_5:
    andi      t8, t2, 0x20
    beqz      t8, @@dungeons_6
    nop
    addiu     t7, 1
@@dungeons_6:
    lui       t8, 0x04
    and       t8, t2, t8
    beqz      t8, @@dungeons_7
    nop
    addiu     t7, 1
@@dungeons_7:
    lui       t8, 0x08
    and       t8, t2, t8
    beqz      t8, @@dungeons_8
    nop
    addiu     t7, 1
@@dungeons_8:
    lui       t8, 0x10
    and       t8, t2, t8
    beqz      t8, @@dungeons_9
    nop
    addiu     t7, 1
@@dungeons_9:
    b         @@count
    nop

@@stones:
    li        at, 0x1C0000 ; stones
    and       t2, v0, at
    li        t7, 0
    lui       t8, 0x04
    and       t8, t2, t8
    beqz      t8, @@stones_1
    nop
    addiu     t7, 1
@@stones_1:
    lui       t8, 0x08
    and       t8, t2, t8
    beqz      t8, @@stones_2
    nop
    addiu     t7, 1
@@stones_2:
    lui       t8, 0x10
    and       t8, t2, t8
    beqz      t8, @@stones_3
    nop
    addiu     t7, 1
@@stones_3:
    b         @@count
    nop

@@tokens:
    lh        t7, 0xD0(a3) ; Gold Skulltulas

@@count:
    li        at, 0
    lh        t8, RAINBOW_BRIDGE_COUNT
    jr        ra
    slt       t2, t7, t8

@@vanilla:
    li        at, 0x18 ; shadow and spirit medallions
    and       t2, v0, at
    bne       t2, at, @@return
    nop
    lbu       t7, 0x84(a3) ; Light arrow slot
    li        t2, 0x12 ; light arrow item id
    beq       t2, t7, @@return
    nop
    li        at, 0xFFFFFFFF

@@return:
    jr        ra
    and       t2, v0, at
