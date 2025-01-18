ocarina_buttons:
    addiu   sp, sp, -0x20
    sw      v0, 0x10(sp)
    sw      ra, 0x14(sp)
    lb      t0, SHUFFLE_OCARINA_BUTTONS
    beqz    t0, @@return
    nop


    jal     c_block_ocarina
    mov.s   f12, f0
    move    t5, v0

    li      v1, 0x0001
    and     v1, v1, v0
    beq     v1, $0, @@button_cup

    ; BTN_A => 0x8000
    lui     t1, 0xFFFF
    ori     t1, t1, 0x7FFF
    and     t7, t7, t1

@@button_cup:
    li      v1, 0x0002
    and     v1, v1, v0
    beq     v1, $0, @@button_cdown

    ; BTN_CUP => 0x0008
    lui     t1, 0xFFFF
    ori     t1, t1, 0xFFF7
    and     t7, t7, t1

@@button_cdown:
    li      v1, 0x0004
    and     v1, v1, v0
    beq     v1, $0, @@button_cleft

    ; BTN_CDOWN => 0x0004
    lui     t1, 0xFFFF
    ori     t1, t1, 0xFFFB
    and     t7, t7, t1

@@button_cleft:
    li      v1, 0x0008
    and     v1, v1, v0
    beq     v1, $0, @@button_cright

    ; BTN_CLEFT => 0x0002
    lui     t1, 0xFFFF
    ori     t1, t1, 0xFFFD
    and     t7, t7, t1

@@button_cright:
    li      v1, 0x0010
    and     v1, v1, v0
    beq     v1, $0, @@return

    ; BTN_CRIGHT => 0x0001
    lui     t1, 0xFFFF
    ori     t1, t1, 0xFFFE
    and     t7, t7, t1

@@return:
    lw      v0, 0x10(sp)
    lw      ra, 0x14(sp)

    ; Replaced code
    lui     at, 0x8012
    sw      t7, 0x1F24(at)

    ; Displaced code

    addiu   sp, sp, 0x20
    jr      ra
    nop
