KaleidoSetup_Update_HasPressedStart_Hook:
    addiu   sp, sp, -0x20
    sw      ra, 0x0014 (sp)
    sw      a2, 0x0018 (sp)

    jal     KaleidoSetup_Update_HasPressedStart
    sw      a3, 0x001C (sp)

    lui     a0, 0x8012

    lw      a3, 0x001C (sp)
    lw      a2, 0x0018 (sp)
    lw      ra, 0x0014 (sp)
    jr      ra
    addiu   sp, sp, 0x20
