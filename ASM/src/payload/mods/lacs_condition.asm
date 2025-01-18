lacs_condition_check:
    lw      t1, LACS_CONDITION
    li      t2, 1
    beq     t1, t2, @@medallions
    li      t2, 2
    beq     t1, t2, @@dungeons
    li      t2, 3
    beq     t1, t2, @@stones
    li      t2, 4
    beq     t1, t2, @@tokens
    li      t2, 5
    beq     t1, t2, @@hearts
    nop

@@vanilla:
    li      t3, 0x0018 ; shadow and spirit medallions
    and     t2, v0, t3
    bne     t3, t2, @@return_vanilla
    li      v1, 0
    li      v1, 1
@@return_vanilla:
    jr      ra
    nop

@@medallions:
    li      at, 0x3F ; medallions
    and     t2, v0, at
    li      t4, 0
    andi    t3, t2, 0x01
    beqz    t3, @@medallions_1
    nop
    addiu   t4, 1
@@medallions_1:
    andi    t3, t2, 0x02
    beqz    t3, @@medallions_2
    nop
    addiu   t4, 1
@@medallions_2:
    andi    t3, t2, 0x04
    beqz    t3, @@medallions_3
    nop
    addiu   t4, 1
@@medallions_3:
    andi    t3, t2, 0x08
    beqz    t3, @@medallions_4
    nop
    addiu   t4, 1
@@medallions_4:
    andi    t3, t2, 0x10
    beqz    t3, @@medallions_5
    nop
    addiu   t4, 1
@@medallions_5:
    andi    t3, t2, 0x20
    beqz    t3, @@medallions_6
    nop
    addiu   t4, 1
@@medallions_6:
    b       @@count
    nop

@@dungeons:
    li      at, 0x1C003F ; stones and medallions
    and     t2, v0, at
    li      t4, 0
    andi    t3, t2, 0x01
    beqz    t3, @@dungeons_1
    nop
    addiu   t4, 1
@@dungeons_1:
    andi    t3, t2, 0x02
    beqz    t3, @@dungeons_2
    nop
    addiu   t4, 1
@@dungeons_2:
    andi    t3, t2, 0x04
    beqz    t3, @@dungeons_3
    nop
    addiu   t4, 1
@@dungeons_3:
    andi    t3, t2, 0x08
    beqz    t3, @@dungeons_4
    nop
    addiu   t4, 1
@@dungeons_4:
    andi    t3, t2, 0x10
    beqz    t3, @@dungeons_5
    nop
    addiu   t4, 1
@@dungeons_5:
    andi    t3, t2, 0x20
    beqz    t3, @@dungeons_6
    nop
    addiu   t4, 1
@@dungeons_6:
    lui     t3, 0x04
    and     t3, t2, t3
    beqz    t3, @@dungeons_7
    nop
    addiu   t4, 1
@@dungeons_7:
    lui     t3, 0x08
    and     t3, t2, t3
    beqz    t3, @@dungeons_8
    nop
    addiu   t4, 1
@@dungeons_8:
    lui     t3, 0x10
    and     t3, t2, t3
    beqz    t3, @@dungeons_9
    nop
    addiu   t4, 1
@@dungeons_9:
    b       @@count
    nop

@@stones:
    li      at, 0x1C0000 ; stones
    and     t2, v0, at
    li      t4, 0
    lui     t3, 0x04
    and     t3, t2, t3
    beqz    t3, @@stones_1
    nop
    addiu   t4, 1
@@stones_1:
    lui     t3, 0x08
    and     t3, t2, t3
    beqz    t3, @@stones_2
    nop
    addiu   t4, 1
@@stones_2:
    lui     t3, 0x10
    and     t3, t2, t3
    beqz    t3, @@stones_3
    nop
    addiu   t4, 1
@@stones_3:
    b       @@count
    nop

@@tokens:
    lh      t4, 0xD0(s0) ; Gold Skulltulas
    b       @@count
    nop

@@hearts:
    lh      t4, 0x2E(s0) ; Heart Containers * 0x10

@@count:
    li      at, 0
    lh      t3, LACS_CONDITION_COUNT
    slt     t4, t4, t3
    bnez    t4, @@return_count
    li      v1, 0
    li      v1, 1
@@return_count:
    jr      ra
    nop
