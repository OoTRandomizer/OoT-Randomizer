EnDntN_SlingshotFix:
    li      t3,1                        ; t2 is EnDnNomal->spawnedItem
    beql    t2,t3,@@EnDntSlingshotRet   ; If already spawned item,
    addi    ra,0xC4                     ; 0x80b4f7d0 to exit function
    lhu     t2,3826(v0)                 ; displaced
@@EnDntSlingshotRet:
    jr      ra                          ; Else, continue check at 0x80b4f70c
    andi    t3,t2,0x2000                ; displaced
