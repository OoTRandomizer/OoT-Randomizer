Player_UpperBodyCheckParent:  ; t8 player actor parent
    addiu   sp,sp,-24
    sw      ra,16(sp)
    lh      t8,(t8)         ; parent actor id
    li      at,0x66         ; ACTOR_ARMS_HOOK id
    bnel    t8,at,@@Return  ; if parent not Hookshot, don't fly
    move    v0,zero
    jal     Player_HoldsHookshot
    nop
    lw      ra,16(sp)
@@Return:
    jr      ra
    addiu   sp,sp,24
