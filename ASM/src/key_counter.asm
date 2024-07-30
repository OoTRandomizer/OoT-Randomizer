move_key_icon:
    ; displaced code
    addiu   t8, $zero, 0x00BE

    li      s0, bk_display
    lw      s0, 0x00 (s0)
    beqz    s0, @@return_icon
    nop

    addiu   t7, t7, 0x000E ; If BK icon is displayed, move X coordinate

@@return_icon:
    jr      ra
    nop

move_key_counter:
    ; displaced code
    addiu   t8, $zero, 0x00BE

    li      s0, bk_display
    lw      s0, 0x00 (s0)
    beqz    s0, @@return_counter
    nop

    addiu   s2, s2, 0x000E ; If BK icon is displayed, move X coordinate

@@return_counter:
    jr      ra
    nop
