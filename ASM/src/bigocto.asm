drop_ruto:
    addiu   sp, sp, -0x30
    sw      ra, 0x14(sp)
    sw      t0, 0x18(sp)
    sw      t1, 0x1C(sp)
    sw      t2, 0x20(sp)
    sw      t3, 0x24(sp)
    sw      t4, 0x28(sp)
    sw      t5, 0x2C(sp)
    la      t0, SAVE_CONTEXT
    lh      t1, 0x0F20(t0)   ;infTable+0x28
    andi    t1, t1, 0x0040   ;big octo visited bit
    beqz    t1, @@return     ;return if flag is not set
    la      t0, PLAYER_ACTOR
    lw      t1, 0x039C(t0)   ;held actor
    beqz    t1, @@return     ;return if held actor is null
    li      t2, 0xA1         ;ruto ID
    lh      t3, 0x00(t1)     ;held actor ID
    bne     t2, t3, @@return ;return if ruto isnt the held actor
    li      t4, 0xFFFFF7FF   ;held actor state flag bitmask
    lw      t5, 0x066C(t0)   ;state flags 1
    and     t5, t4, t5
    sw      t5, 0x066C(t0)   ;unset held actor state flag
    sw      r0, 0x039C(t0)   ;null held actor
    sw      r0, 0x011C(t0)   ;null link attachedB
    sw      r0, 0x0118(t1)   ;null ruto attachedA
@@return:
    sw      t5, 0x2C(sp)
    sw      t4, 0x28(sp)
    sw      t3, 0x24(sp)
    sw      t2, 0x20(sp)
    sw      t1, 0x1C(sp)
    sw      t0, 0x18(sp)
    sw      ra, 0x14(sp)
    lh      t6, 0x1C(s0)     ;displaced
    jr      ra
    addiu   sp, sp, 0x30

check_kill_demoeffect:
    addiu   sp, sp, -0x30
    sw      ra, 0x14(sp)
    sw      t0, 0x18(sp)
    sw      t1, 0x1C(sp)
    sw      t2, 0x20(sp)
    lh      t0, 0xA4(a1)     ;current scene
    li      t1, 0x02         ;jabu
    bne     t0, t1, @@return
    li      t2, 0x06         ;room 6
    lb      t0, 0x03(a0)     ;current room
    bne     t0, t2, @@return ;return if not jabu room 6
    nop
    la      t0, SAVE_CONTEXT
    lh      t1, 0x0F20(t0)   ;infTable+0x28
    andi    t1, t1, 0x0040   ;big octo visited bit
    beqz    t1, @@return     ;return if flag is not set
    nop
    jal     0x80020EB4       ;Actor_Kill
    nop
@@return:
    lw      t2, 0x20(sp)
    lw      t1, 0x1C(sp)
    lw      t0, 0x18(sp)
    lw      ra, 0x14(sp)
    lh      v0, 0x1C(s0)     ;displaced
    jr      ra
    addiu   sp, sp, 0x30
