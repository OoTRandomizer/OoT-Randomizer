EnGo2_BiggoronIdleClaimCheck:
    lh      t8,28(a0)       ; actor params/variable
    li      at,2            ; Biggoron
    andi    t8,t8,0x1f
    bne     at,t8,@@Return  ; only check if Biggoron
    li      at,1
    lb      t8,510(a0)      ; EnGo2->reverse
    bne     at,t8,@@Return
    li      at,0
    sb      at,510(a0)      ; if set, unset reverse flag
    addi    ra,0x164        ; to 0x80b5a8d8/end function
@@Return:
    jr      ra
    li      at,1            ; displaced
