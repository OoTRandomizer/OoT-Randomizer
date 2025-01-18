init:
    addiu   sp, sp, -0x18
    sw      ra, 0x10 (sp)

    jal     c_init
    nop

    ; Displaced code
    lui     v0, 0x8012
    addiu   v0, v0, 0xD2A0
    addiu   t6, r0, 0x0140
    lui     at, 0x8010
    sw      t6, 0xE500 (at)
    addiu   t7, r0, 0x00F0

    lw      ra, 0x10 (sp)
    jr      ra
    addiu   sp, sp, 0x18


Static_ctxt_Init:
    li      t0, RANDO_CONTEXT
    sw      t0, 0x15D4(v0)
    jr      ra
    ; Displaced code
    li      v0, 0x15C0
