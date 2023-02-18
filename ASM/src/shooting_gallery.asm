shooting_gallery_init:
    li      t0, SAVE_CONTEXT
    lw      t2, 0x04(t0)       ; Link's age

    beq     t2, r0, @@adult
    lw      t1, 0x00(t0)       ; Entrance Idx

@@child:
    li      at, 0x003B         ; Kakariko Shooting Gallery
    bne     t1, at, @@return
    nop
    li      t3, 0xC47A0000     ; -1000.0
    sw      t3, 0x28(a0)       ; Y-Position

@@adult:
    li      at, 0x0016D        ; Market Shooting Gallery
    bne     t1, at, @@return
    nop
    li      t3, 0xC47A0000     ; -1000.0
    sw      t3, 0x28(a0)       ; Y-Position

@@return:
    ; Displaced Code
    jr      ra
    li      t6, 0x0001
