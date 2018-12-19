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
