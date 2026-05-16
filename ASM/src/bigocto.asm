JabuObjects_DropRutoBigOcto:
    la      t0, SAVE_CONTEXT
    lh      t0, 0x0F20(t0)   ; infTable+0x28
    andi    t0, t0, 0x0040   ; Big Octo visited bit
    beqz    t0, @@return     ; return if flag is not set
    li      t2, 0xA1         ; Ruto actor ID (fill delay slot)

    la      t0, PLAYER_ACTOR
    lw      t1, 0x039C(t0)   ; held actor
    beqz    t1, @@return     ; return if held actor is null
    li      t4, 0xFFFFF7FF   ; held actor state flag bitmask (fill delay slot)

    lh      t3, (t1)         ; held actor ID
    bne     t2, t3, @@return ; return if Ruto isn't the held actor
    lw      t5, 0x066C(t0)   ; player stateFlags1
    and     t5, t4, t5
    sw      t5, 0x066C(t0)   ; unset held actor state flag
    sw      r0, 0x039C(t0)   ; null held actor
    sw      r0, 0x011C(t0)   ; null player child
    sw      r0, 0x0118(t1)   ; null Ruto parent
@@return:
    jr      ra
    addiu   a0, a0, -29472    ; displaced

DemoEffect_KillAfterBigOcto:
    addiu   sp, sp, -24
    lh      v0, 0x1C(s0)     ; displaced
    lh      t0, 0xA4(a1)     ; current scene
    li      t1, 0x2          ; Jabu scene ID
    bne     t0, t1, @@return
    li      t2, 0x6          ; room 6
    lb      t0, 0x3(a0)      ; current room
    bne     t0, t2, @@return ; return if not Jabu room 6
    nop

    la      t0, SAVE_CONTEXT
    lh      t1, 0x0F20(t0)   ; infTable+0x28
    andi    t1, t1, 0x0040   ; Big Octo visited bit
    beqz    t1, @@return     ; return if flag is not set
    sw      ra, 16(sp)

    jal     Actor_Kill       ; else, kill Demo_Effect actor
    nop
    lw      ra, 16(sp)
@@return:
    jr      ra
    addiu   sp, sp, 24
