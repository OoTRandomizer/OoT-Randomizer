MiniMap_Draw_Hook:
    addiu   sp, sp, -0x30
    sw      ra, 0x10(sp)
    sw      a0, 0x14(sp)
    jal     0x8006CA64
    nop
    jal     MiniMap_Draw_Hack
    lw      a0, 0x14(sp)
    lw      ra, 0x10(sp)
    jr      ra
    addiu   sp, sp, 0x30
