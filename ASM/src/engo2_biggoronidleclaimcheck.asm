EnGo2_BiggoronIdleClaimCheck:
    lh      v1,28(s0)       ; displaced
    move    v0,zero         ; default return is not reverse
    lh      t8,28(a0)       ; actor params/variable
    li      at,2            ; Biggoron
    andi    t8,t8,0x1f
    bne     at,t8,@@Return  ; only check if Biggoron
    li      at,1
    lb      t8,510(a0)      ; EnGo2->reverse
    bne     at,t8,@@Return
    li      at,0
    sb      at,510(a0)      ; if set, unset reverse flag
    li      v0,1            ; and branch to end in caller
@@Return:
    jr      ra
    li      at,1            ; displaced
