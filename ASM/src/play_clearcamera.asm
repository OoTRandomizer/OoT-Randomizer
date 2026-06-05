Play_ClearCameraAvoidMain:             ; camId a1 (-1 = NONE, 0 = MAIN)
    sll     a1,a1,0x10                 ; displaced
    sra     a1,a1,0x10                 ; displaced
    li      at,-1                      ; If camId = NONE, set it to activeCamId and check if MAIN
    bne     a1,at,@@CheckMain          ; Else, check if MAIN
    sll     t1,a1,0x10                 ; displaced (v0 -> t1)
    lh      a1,1952(a2)                ; activeCamId
@@CheckMain:
    li      t3,1                       ; for branching in caller
    beqzl   a1,@@Return                ; If camId = MAIN, skip to end and don't set pointer null
    li      v0,1
    li      t4,2                       ; for branching in caller
    b       @@Return                   ; If not MAIN, remove pointer
    li      v0,2
@@Return:
    jr      ra
    nop
