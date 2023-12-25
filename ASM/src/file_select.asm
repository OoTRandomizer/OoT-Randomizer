;If the cursor value is 2, skip up or down depending on the direction
;Each direction for each screen is handled seperatley so this is mostly duplicated code with different registers
skip_3_up_main:
    addiu   sp, sp, -0x18
    sw      t2, 0x04(sp)
    lh      t7, 0x4A2A(v1)
    li      t2, 0x02
    bne     t7, t2, @@return
    li      t2, 0x01
    sh      t2, 0x4A2A(v1)
@@return:
    lh      t7, 0x4A2A(v1)
    lw      t2, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x18

skip_3_down_main:
    addiu   sp, sp, -0x18
    sw      t2, 0x04(sp)
    lh      t6, 0x4A2A(v1)
    li      t2, 0x02
    bne     t6, t2, @@return
    li      t2, 0x03
    sh      t2, 0x4A2A(v1)
@@return:
    lh      t6, 0x4A2A(v1)
    lw      t2, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x18

skip_3_up_copy_from:
    addiu   sp, sp, -0x18
    sw      t2, 0x04(sp)
    lh      v1, 0x4A2A(t0)
    li      t2, 0x02
    bne     v1, t2, @@return
    li      t2, 0x01
    sh      t2, 0x4A2A(t0)
@@return:
    lh      v1, 0x4A2A(t0)
    lw      t2, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x18

skip_3_down_copy_from:
    addiu   sp, sp, -0x18
    sw      t2, 0x04(sp)
    lh      v1, 0x4A2A(t0)
    li      t2, 0x02
    bne     v1, t2, @@return
    li      t2, 0x03
    sh      t2, 0x4A2A(t0)
@@return:
    lh      v1, 0x4A2A(t0)
    lw      t2, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x18

skip_3_up_copy_to:
    addiu   sp, sp, -0x18
    sw      t2, 0x04(sp)
    lh      v1, 0x4A2A(t0)
    li      t2, 0x02
    bne     v1, t2, @@return
    li      t2, 0x01
    sh      t2, 0x4A2A(t0)
@@return:
    lh      v1, 0x4A2A(t0)
    lw      t2, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x18

skip_3_down_copy_to:
    addiu   sp, sp, -0x18
    sw      t2, 0x04(sp)
    lh      v1, 0x4A2A(t0)
    li      t2, 0x02
    bne     v1, t2, @@return
    li      t2, 0x03
    sh      t2, 0x4A2A(t0)
@@return:
    lh      v1, 0x4A2A(t0)
    lw      t2, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x18

skip_3_down_copy_to_2:
    addiu   sp, sp, -0x18
    sw      t2, 0x04(sp)
    sh      t3, 0xCA2A(at)
    li      t2, 0x02
    bne     t3, t2, @@return
    li      t2, 0x03
    sh      t2, 0x4A2A(t0)
@@return:
    lh      v1, 0x4A2A(t0)
    lw      t2, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x18

skip_3_up_erase:
    addiu   sp, sp, -0x18
    sw      t2, 0x04(sp)
    lh      v1, 0x4A2A(t0)
    li      t2, 0x02
    bne     v1, t2, @@return
    li      t2, 0x01
    sh      t2, 0x4A2A(t0)
@@return:
    lh      v1, 0x4A2A(t0)
    lw      t2, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x18

skip_3_down_erase:
    addiu   sp, sp, -0x18
    sw      t2, 0x04(sp)
    lh      v1, 0x4A2A(t0)
    li      t2, 0x02
    bne     v1, t2, @@return
    li      t2, 0x03
    sh      t2, 0x4A2A(t0)
@@return:
    lh      v1, 0x4A2A(t0)
    lw      t2, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x18

;Set file 3 offset to 0xF000, pushing it off screen
move_file_3:
    la      t0, 0x801E4EE8
    li      t1, 0xF000
    sh      t1, 0x00(t0)
    jr      ra
    lh      t3, 0x4A2E(a2)
