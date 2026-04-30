EnBox_CallLoadObject:
    addiu   sp,sp,-8
    sw      ra,4(sp)
    jal     EnBox_LoadObject    ; a0 EnBox*, a1 play*
    move    s1,a1               ; displaced
    lw      ra,4(sp)
    move    a1,s1               ; might not be needed but for safety
    jr      ra
    addiu   sp,sp,8
