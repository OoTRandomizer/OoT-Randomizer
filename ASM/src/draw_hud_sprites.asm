draw_hud_sprites:
    addiu   sp, sp, -0x10
    sw      ra, 0(sp)
    jal     draw_dpad
    nop
    jal     draw_agony
    nop
    lw      t6, 0x1C44(s6) ; displaced code
    lui     t8, 0xDB06     ; displaced code
    lw      ra, 0(sp)
    jr      ra
    addiu   sp,sp, 0x10