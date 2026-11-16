Player_BunnyMatrixPush:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    sw      a0,20(sp)    ; Matrix_Push uses a0, a1, need to save them
    jal     Matrix_Push
    sw      a1,24(sp)
    lw      ra,16(sp)
    lw      a0,20(sp)
    lw      a1,24(sp)
    lui     t8,0xdb06   ; Displaced
    lw      v0,704(s1)  ; Displaced
    jr      ra
    addiu   sp,sp,24

Player_BunnyMatrixPop:
    addiu   sp,sp,-24
    sw      ra,16(sp)    ; No need to save registers here
    jal     Matrix_Pop
    nop
    lw      ra,16(sp)
    lw      v0,704(s1)  ; Displaced
    jr      ra
    addiu   sp,sp,24

Player_HoverMatrixPush:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    sw      a0,20(sp)    ; Matrix_Push uses a0, a1, need to save them
    jal     Matrix_Push
    sw      a1,24(sp)
    lw      ra,16(sp)
    lw      a0,20(sp)
    lw      a1,24(sp)
    lwc1    $f12,36(s0) ; Displaced
    lw      a2,44(s0)   ; Displaced
    jr      ra
    addiu   sp,sp,24

Player_HoverMatrixPop:
    addiu   sp,sp,-24
    sw      ra,16(sp)    ; No need to save registers here
    jal     Matrix_Pop
    nop
    lw      ra,16(sp)
    lw      v1,720(s1)  ; Displaced
    jr      ra
    addiu   sp,sp,24
