ObjSyokudai_CallRotateFlameCollider:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    sw      a0,20(sp)
    sw      a1,24(sp)
    sw      v0,472(s0)      ; displaced

    move    a0,s0
    jal     ObjSyokudai_RotateFlameCollider
    move    a1,s1

    lw      ra,16(sp)
    lw      a0,20(sp)
    lw      a1,24(sp)
    addiu   sp,sp,24
    jr      ra
    lh      v1,28(s0)       ; displaced
