Player_HookshotCheckActorSpawn:
    bnez    v0,@@Return     ; If Hookshot actor spawned, 
    sw      v0,924(a1)      ; set it as heldActor and continue

    addiu   sp,sp,-24
    sw      ra,16(sp)
    move    a0,s1           ; Otherwise, use item none to avoid softlock
    jal     Player_UseItem  ; a0 play a1 player a2 item
    li      a2,255
    lw      ra,16(sp)
    addiu   sp,sp,24
@@Return:
    jr      ra
    nop
