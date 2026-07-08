Player_CallCheckEponaWater:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    jal     Player_CheckEponaWater
    nop
    jal     Player_RemoveLakeHyliaSwimEntry
    lwc1    $f10,64(sp) ; 40 + 24
    move    a0,s1
    move    a2,s7       ; Restore address to Player_Action_StartModeWater to a2
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24

Player_RemoveLakeHyliaSwimEntry:    ; s0 player s1 playstate
    move    a1,s0           ; displaced
    move    v0,zero         ; assume return 0/false
    lh      t8,0xa4(s1)     ; sceneid
    li      at,0x57         ; lake hylia
    bne     at,t8,@@Return  ; not lake - keep swim entry
    lui     at,hi(SAVE_CONTEXT)
    addi    at,lo(SAVE_CONTEXT)
    lhu     t8,0x0ee0(at)   ; lake hylia water level switch flag
    andi    t8,t8,0x200
    bnez    t8,@@Return     ; if set - high water level, keep water
    lui     at,0xc4bb       ; -1500.0f
    addi    at,0x8000
    mtc1    at,$f16
    c.lt.s  $f8,$f16        ; $f8 = player y pos
    bc1f    @@Return        ; y pos higher than limit - keep swim
    lui     at,0xc4c8       ; -1600.0f
    mtc1    at,$f16
    c.lt.s  $f16,$f8
    bc1tl   @@Return        ; y pos between limits - no swim entry
    li      v0,1
@@Return:
    lw      t8,1640(s0)     ; displaced
    jr      ra
    lwc1    $f16,36(t8)     ; displaced
