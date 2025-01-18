bombchu_back_color:
    addiu   sp, sp, -0x18
    sw      v0, 0x10(sp)
    sw      ra, 0x14(sp)
    jal     get_bombchu_back_color
    mov.s   f12, f0
    move    t5, v0
    lw      v0, 0x10(sp)
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18
