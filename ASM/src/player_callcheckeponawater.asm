Player_CallCheckEponaWater:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    jal     Player_CheckEponaWater
    nop
    lw      ra,16(sp)
    addiu   sp,sp,24
    move    a0,s1
    move    a1,s0       ; Restore displaced a0 and a1 (z64_game and z64_link),
    move    a2,s7       ; address to Player_Action_StartModeWater to a2,
    jr      ra
    lwc1    $f10,40(sp) ; and ySurface as $f10 (for c.le.s after return)
