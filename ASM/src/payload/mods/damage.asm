CFG_DAMAGE_MULTIPLYER:
    .byte 0x00
EXTERN_DAMAGE_MULTIPLYER:
    .byte 0x00
    .align 4

Apply_Damage_Multiplier:
    li      t7, CFG_DAMAGE_MULTIPLYER
    lb      t7, 0x00(t7)
    li      t8, EXTERN_DAMAGE_MULTIPLYER
    lb      t8, 0x00(t8)
    add     t7, t7, t8

    bltz    t7, @@DivDamage
    li      at, 3
    bge     t7, at, @@ohko
    nop

@@MulDamage:
    b       @@DoubleDefence
    sllv    s0, s0, t7     ; damage multiplier

@@ohko:
    b       @@return
    sh      zero, 0x30(a1)

@@DivDamage:
    sub     t7, zero, t7
    srav    s0, s0, t7     ; damage multiplier

@@DoubleDefence:
    lbu     t7, 0x3D(a1)   ; check if has double defense
    beq     t7, zero, @@return
    nop

    sra     s0, s0, 1    ; double defense
    sll     s0, s0, 0x10
    sra     s0, s0, 0x10 ; s0 = damage

@@return:
    jr      ra
    nop
