dpad_draw:
    addiu   sp, sp, -0x10
    sw      ra, 0(sp)
    jal     draw_dpad_and_menu_utilities
    nop
    lw      t6, 0x1C44(s6)
    lui     t8, 0xDB06
    lw      ra, 0(sp)
    jr      ra
    addiu   sp,sp, 0x10
