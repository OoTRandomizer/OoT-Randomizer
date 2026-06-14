GTGGate_CheckPermOpen:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    lw      a0,60(sp)       ; play, original 36(sp) + 24 extra
    jal     Flags_GetSwitch ; Vanilla temp flag set check
    andi    a1,a1,0x3f
    bnezl   v0,@@Return     ; If temp flag set, no need to check perm flag
    nop
    la      a1,DUNGEONS_SHUFFLED    ; Check setting and return if not set
    lb      a1,(a1)
    beqzl   a1,@@Return
    nop
    la      a1,SAVE_CONTEXT
    lw      a1,4(a1)        ; Age
    bnezl   a1,@@Return     ; Don't open if child
    nop
    jal     Flags_GetSwitch ; Permanent flag set check
    li      a1,4
@@Return:
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24
