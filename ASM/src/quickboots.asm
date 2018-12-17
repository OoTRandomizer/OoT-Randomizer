qb_draw:
    addiu   sp, sp, -0x10
    sw      ra, 0(sp)
    jal     draw_quickboots
    nop
    lw      s4, 0x0000(s6)
    lw      s1, 0x02b0(s4)
    lw      ra, 0(sp)
    jr      ra
    addiu   sp,sp, 0x10