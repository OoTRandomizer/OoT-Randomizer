Player_CallCheckEponaWater:
    addiu   sp,sp,-8    ; Because Player_CheckEponaWater will decrease 64 but sw at 64(sp)
    sw      ra,4(sp)
    jal     Player_CheckEponaWater
    nop
    lw      ra,4(sp)
    addiu   sp,sp,8
    move    a0,s1
    move    a1,s0       ; Restore displaced a0 and a1 (z64_game and z64_link),
    move    a2,s7       ; address to Player_Action_StartModeWater to a2,
    jr      ra
    lwc1    $f10,40(sp) ; and ySurface as $f10 (for c.le.s after return)
