Play_ClearCameraAvoidMain:             ; camId a1 (-1 = NONE, 0 = MAIN), at = -1
    beq     a1,at,@@Return             ; If camId = NONE, just continue as usual
    sll     v0,a1,0x10                 ; displaced
    beqzl   a1,@@Return                ; If camId = MAIN, skip to end and don't set pointer null
    addi    ra,0x34                    ; 0x8009d274
    b       @@Return
    addi    ra,0x8                     ; If not MAIN/NONE, remove pointer 0x8009d248
@@Return:
    jr      ra                         ; 0x8009d240
    nop
