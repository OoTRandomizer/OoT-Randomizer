BunnyMatrixPush:
    addiu   sp,sp,-12
    sw      ra,4(sp)
    sw      a0,8(sp)    ; Matrix_Push uses a0, a1, need to save them
    jal     Matrix_Push
    sw      a1,12(sp)
    lw      ra,4(sp)
    lw      a0,8(sp)
    lw      a1,12(sp)
    lui     t8,0xdb06   ; Displaced
    lw      v0,704(s1)  ; Displaced
    jr      ra
    addiu   sp,sp,12

BunnyMatrixPop:
    addiu   sp,sp,-4
    sw      ra,4(sp)    ; No need to save registers here
    jal     Matrix_Pop
    nop
    lw      ra,4(sp)
    lw      v0,704(s1)  ; Displaced
    jr      ra
    addiu   sp,sp,4

HoverMatrixPush:
    addiu   sp,sp,-12
    sw      ra,4(sp)
    sw      a0,8(sp)    ; Matrix_Push uses a0, a1, need to save them
    jal     Matrix_Push
    sw      a1,12(sp)
    lw      ra,4(sp)
    lw      a0,8(sp)
    lw      a1,12(sp)
    lwc1    $f12,36(s0) ; Displaced
    lw      a2,44(s0)   ; Displaced
    jr      ra
    addiu   sp,sp,12

HoverMatrixPop:
    addiu   sp,sp,-4
    sw      ra,4(sp)    ; No need to save registers here
    jal     Matrix_Pop
    nop
    lw      ra,4(sp) 
    lw      v1,720(s1)  ; Displaced
    jr      ra
    addiu   sp,sp,4
