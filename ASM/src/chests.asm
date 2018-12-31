CHEST_SIZE_MATCH_CONTENTS:
	.word   0x00000000

GET_CHEST_OVERRIDE_SIZE_WRAPPER:
    addiu   sp, sp, -0x10
    sw      ra, 0x04 (sp)
    sw      a0, 0x08 (sp)
    sw      at, 0x0C (sp)

    jal     get_chest_override_size
    move    a0, s0

    lw      ra, 0x04 (sp)
    lw      a0, 0x08 (sp)
    lw      at, 0x0C (sp)
    jr      ra
    addiu   sp, sp, 0x10


GET_CHEST_OVERRIDE_COLOR_WRAPPER:
    addiu   sp, sp, -0x20
    sw      ra, 0x04 (sp)
    sw      at, 0x08 (sp)
    sw      v0, 0x0C (sp)
    sw      v1, 0x10 (sp)
    sw      t4, 0x14 (sp)

    jal     get_chest_override_color
    move    a0, t8
    move    t9, v0

    lw      ra, 0x04 (sp)
    lw      at, 0x08 (sp)
    lw      v0, 0x0C (sp)
    lw      v1, 0x10 (sp)
    lw      t4, 0x14 (sp)
    jr      ra
    addiu   sp, sp, 0x20
