open_save_hook:

; push the registers to the stack
    addiu   sp, sp, -0x40
    sw      ra, 0x00(sp)
    sw      v0, 0x04(sp)
    sw      v1, 0x08(sp)
    sw      a0, 0x0C(sp)
    sw      a1, 0x10(sp)
    sw      a2, 0x14(sp)
    sw      a3, 0x18(sp)
    sw      s0, 0x1c(sp)
    sw      s1, 0x20(sp)
    sw      at, 0x24(sp)

    lw      a0, 0x60(sp) ; get savecontext variable off the stack
    jal     Save_Open
    lw      a0, 0x00(a0) ; get the buffer pointer


    lw      v0, 0x04(sp)
    lw      v1, 0x08(sp)
    lw      a0, 0x0C(sp)
    lw      a1, 0x10(sp)
    lw      a2, 0x14(sp)
    lw      a3, 0x18(sp)
    lw      s0, 0x1c(sp)
    lw      s1, 0x20(sp)
    lw      at, 0x24(sp)

; Replaced code
    jal     0x80057030
    addu    A1, T9, A3

    lw      ra, 0x00(sp)
    jr      ra
    addiu   sp, sp, 0x40
