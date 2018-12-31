DEBUG_OFFSET:
.word 0

.macro debug_print,reg
    addi    sp, sp, -0x20
    sw      t0, 0x04(sp)
    sw      t1, 0x08(sp)
    sw      t2, 0x0C(sp)
    sw      t3, 0x10(sp)
    sw      at, 0x14(sp)

    ori     t3, reg, 0

    li      t0, DEBUG_OFFSET
    lw      t1, 0x00 (t0)

    li      t2, DEBUG_BUFFER
    addu    t2, t2, t1
    sw      t3, 0x00 (t2)

    addiu   t1, t1, 4
    andi    t1, t1, 0xFFF ; Assumes buffer length is 0x1000
    sw      t1, 0x00 (t0)

    lw      t0, 0x04(sp)
    lw      t1, 0x08(sp)
    lw      t2, 0x0C(sp)
    lw      t3, 0x10(sp)
    lw      at, 0x14(sp)
    addi    sp, sp, 0x20
.endmacro

.macro debug_printi,val
    addi    sp, sp, -0x10
    sw      at, 0x04(sp)
    sw      t4, 0x08(sp)

    li      t4, val
    debug_print t4

    lw      at, 0x04(sp)
    lw      t4, 0x08(sp)
    addi    sp, sp, 0x10
.endmacro
