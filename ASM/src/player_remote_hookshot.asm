Player_DrinkBottle_FullMilk:
    la      t8,REMOTE_HOOKSHOT_ENABLED
    lb      at,(t8)
    beqz    at,@@Return           ; Don't change behavior if remote Hookshot not enabled
    li      a2,20                 ; Set next item to empty bottle
    lb      t8,324(s0)            ; player->itemAction
    li      at,40                 ; Full milk bottle IA
    beql    t8,at,@@Return        ; If drinking full milk,
    li      a2,31                 ; Set half milk bottle to next item
@@Return:
    jr      ra
    nop
