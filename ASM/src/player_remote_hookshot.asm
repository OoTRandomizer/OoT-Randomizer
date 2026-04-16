PlayerMilkDrinkBottle:
    la      t8,REMOTE_HOOKSHOT_ENABLED
    lb      at,(t8)
    beqz    at,@@MilkReturn       ; Don't change behavior if remote hookshot not enabled
    nop
    lb      t8,324(s0)            ; player->itemAction
    li      at,40                 ; Full milk bottle IA
    bne     t8,at,@@MilkReturn    ; If not drinking full milk, return
    nop
    li      a2,31                 ; Else, set half milk bottle to next item
    addi    ra,4                  ; Don't overwrite next item
@@MilkReturn:
    jr      ra
    sh      t7,2112(s0)           ; actionVar2
