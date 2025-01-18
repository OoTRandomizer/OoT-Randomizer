START_TWINROVA_FIGHT:
.byte 0x00
.align 4

TWINROVA_ACTION_TIMER:
.word 0x00
.align 4

rova_check_pos:
    sw      s0, 0x3C(sp)   ;displaced
    addiu   sp, sp, -0x20
    sw      ra, 0x14(sp)
    la      t1, START_TWINROVA_FIGHT
    lb      t2, 0x00(t1)
    bnez    t2, @@return
    nop
    lw      t3, 0x28(s2)   ;links height
    li      t4, 0x43700000 ;240.0f
    blt     t3, t4, @@return
    li      t5, 0x01
    sb      t5, 0x00(t1)
    li      a0, 0x1B
    jal     0x800CAA70     ;set background music
    nop
@@return:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x20

;============================================

twinrova_displaced:
    lw      s2, 0x1C44(s3)
    addiu   t6, r0, 0x03
    sb      t6, 0x05B0(s1)
    lbu     t7, 0x07AF(s3)
    mfc1    a2, f22
    mfc1    a3, f20
    jr      ra
    nop

;============================================

rova_portal:
    lbu     t8, 0x00(v0)  ;displaced
    addiu   sp, sp, -0x30
    sw      ra, 0x14(sp)
    sw      a0, 0x18(sp)
    sw      a1, 0x1C(sp)
    sw      a2, 0x20(sp)
    sw      a3, 0x24(sp)
    lb      a0, START_TWINROVA_FIGHT
    beqz    a0, @@return
    nop
    lw      a0, TWINROVA_ACTION_TIMER
    slti    a1, a0, 30
    bnez    a1, @@return
    nop
    slti    a1, a0, 80
    beqz    a1, @@disappear
    nop
    li      a0, 0x3D4CCCCD
    sw      a0, 0x4D0(s2)
    or      a0, s2, r0
    addiu   a0, a0, 0x4C8
    li      a1, 0x437F0000 ;255.0f
    li      a2, 0x3F800000 ;1.0f
    li      a3, 0x41200000 ;10.0f
    jal     0x80064280     ;Math_SmoothScaleMaxF
    nop
    b       @@return

@@disappear:
    or      a0, s2, r0
    addiu   a0, a0, 0x4C8
    li      a1, 0x00000000 ;255.0f
    li      a2, 0x3F800000 ;1.0f
    li      a3, 0x41200000 ;10.0f
    jal     0x80064280     ;Math_SmoothScaleMaxF
    nop

@@return:
    lw      ra, 0x14(sp)
    lw      a0, 0x18(sp)
    lw      a1, 0x1C(sp)
    lw      a2, 0x20(sp)
    lw      a3, 0x24(sp)
    jr      ra
    addiu   sp, sp, 0x30

;============================================

twinrova_set_action_ice:
    lh     t0, 0xB6(s0)
    addiu  t0, t0, 0x4000
    sh     t0, 0xB6(s0)
    li     t0, 1
    sb     t0, 0x5E8(s0)
    sb     r0, 0x554(s0)
    lw     t1, 0x4(s0)
    li     t2, 0xFFFFFFFE
    and    t3, t2, t1
    sw     t3, 0x4(s0)
    la     t0, twinrova_rise
    jr     ra
    sw     t0, 0x13C(s0)

twinrova_set_action_fire:
    lh     t0, 0xB6(s0)
    addiu  t0, t0, 0xC000
    sh     t0, 0xB6(s0)
    li     t0, 1
    sb     t0, 0x5E8(s0)
    sb     r0, 0x554(s0)
    lw     t1, 0x4(s0)
    li     t2, 0xFFFFFFFE
    and    t3, t2, t1
    sw     t3, 0x4(s0)
    la     t0, twinrova_rise
    jr     ra
    sw     t0, 0x13C(s0)

;============================================

twinrova_rise:
    addiu   sp, sp, -0x30
    sw      ra, 0x14(sp)
    sw      a0, 0x18(sp)
    sw      a1, 0x1C(sp)
    li      t0, 1
    sb      t0, 0x554(a0)
    lh      t0, 0x1C(a0)
    beqz    t0, @@skip_incr
    nop
    lw      a0, TWINROVA_ACTION_TIMER
    addiu   a1, a0, 1
    sw      a1, TWINROVA_ACTION_TIMER
@@skip_incr:
    lw      a0, TWINROVA_ACTION_TIMER
    li      a1, 3
    bne     a0, a1, @@no_laugh
    nop
    lw      a0, 0x18(sp)
    lh      t0, 0x1C(a0)
    li      t1, 1
    beq     t0, t1, @@rova1
    addiu   a1, r0, 0x39B0 ;NA_SE_EN_TWINROBA_LAUGH
    addiu   a1, r0, 0x39B1 ;NA_SE_EN_TWINROBA_LAUGH2
@@rova1:
    jal     0x80022FD0     ;Audio_PlayActorSound2
    nop

@@no_laugh:
    slti    a1, a0, 40
    bnez    a1, @@return
    nop
    lw      a0, 0x18(sp)
    addiu   a0, a0, 0x28
    li      a1, 0x43C80000 ;400.0f
    li      a2, 0x3F800000 ;1.0f
    li      a3, 0x40C00000 ;6.0f
    jal     0x80064280     ;Math_SmoothScaleMaxF
    nop
    lw      a0, 0x18(sp)
    addiu   a0, a0, 0x558  ;&this->skelanime
    jal     0x8008C9C0     ;Skelanime_FrameUpdateMatrix
    nop
    lw      a0, 0x18(sp)
    jal     0x80022FD0     ;Audio_PlayActorSound2
    addiu   a1, r0, 0x311F ;NA_SE_EN_TWINROBA_FLY - SFX_FLAG
    lw      a0, TWINROVA_ACTION_TIMER
    li      t0, 97
    bne     a0, t0, @@return
    nop

@@start_fight:
    lw      a0, 0x18(sp)
    lw      a1, 0x1C(sp)
    lw      t3, 0x138(a0)  ;overlay table entry
    lw      t3, 0x10(t3)   ;overlay address
    addiu   t1, t3, 0x13EC ;"decide next action" func offset
    sw      t1, 0x13c(a0)


@@return:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x30

;============================================

ice_pos:
    lui     at, 0xC416
    mtc1    at, f12
    jr      ra
    or      a2, r0, r0

fire_pos:
    lui     at, 0x4416
    mtc1    at, f12
    jr      ra
    or      a2, r0, r0
