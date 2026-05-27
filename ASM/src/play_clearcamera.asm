Play_ClearCameraAvoidMain:             ; camId a1 (-1 = NONE, 0 = MAIN)
    sll     a1,a1,0x10                 ; displaced
    sra     a1,a1,0x10                 ; displaced
    li      at,-1                      ; displaced
    li      t0,0                       ; return value because v0 is in use

    beq     a1,at,@@Return             ; If camId = NONE, just continue as usual
    sll     v0,a1,0x10                 ; displaced
    li      at,1                       ; for beq in caller
    beqzl   a1,@@Return                ; If camId = MAIN, skip to end and don't set pointer null
    li      t0,1
    li      at,2                       ; for beq in caller
    b       @@Return                   ; If not MAIN/NONE, remove pointer
    li      t0,2
@@Return:
    jr      ra
    nop
