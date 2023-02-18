override_changelinkanimdefaultstop:
    addiu   sp, sp, -0x28
    sw      ra, 0x0024(sp)
    sw      a0, 0x0028(sp)
    sw      a1, 0x002C(sp)
    sw      a2, 0x0030(sp)
    jal     0x8008A194      ;SkelAnime_GetFrameCount
    lw      a0, 0x0030(sp)
    mtc1    v0, f4
    mtc1    zero, f0
    addiu   t6, zero, 0x0002
    cvt.s.w f6, f4
    sw      t6, 0x0018(sp)
    lw      a0, 0x0028(sp)
    lw      a1, 0x002C(sp)
    lw      a2, 0x0030(sp)
    lui     a3, 0x3F80

    li      t0, 0x040032B0
    bne     a2, t0, @@skip   ;if next animation is heavy rock pickup, change speed
    nop
    lui     a3, 0x4040       ;3.0f
    @@skip:
    swc1    f6, 0x0014(sp)
    swc1    f0, 0x0010(sp)
    jal     0x8008C000       ;SkelAnime_ChangeLinkAnim
    swc1    f0, 0x001C(sp)
    lw      ra, 0x0024(sp)
    lw      ra, 0x0024(sp)
    jr      ra
    addiu   sp, sp, 0x28
