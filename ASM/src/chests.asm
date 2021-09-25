CHEST_SIZE_MATCH_CONTENTS:
	.word   0x00000000


GET_CHEST_OVERRIDE_WRAPPER:
    sb  t9,0x01E9(s0)

    addiu   sp, sp, -0x20
    sw      ra, 0x04 (sp)
    sw      a0, 0x08 (sp)
    sw      a1, 0x0C (sp)
    sw      t0, 0x10 (sp)
    swc1    $f10, 0x14 (sp)
    swc1    $f16, 0x18 (sp)

    jal     get_chest_override
    move    a0, s0

    lw      ra, 0x04 (sp)
    lw      a0, 0x08 (sp)
    lw      a1, 0x0C (sp)
    lw      t0, 0x10 (sp)
    lwc1    $f10, 0x14 (sp)
    lwc1    $f16, 0x18 (sp)
    jr      ra
    addiu   sp, sp, 0x20
