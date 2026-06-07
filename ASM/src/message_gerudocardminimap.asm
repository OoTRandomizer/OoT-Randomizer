Message_GerudoCardMinimap:
    bnez    t4,@@Return         ; displaced branching
    li      at,0x007B           ; Gerudo Card textId, v0 current textId
    bnel    v0,at,@@Return      ; If not card, continue as usual
    nop

    addiu   sp,sp,-24           ; If card, continue to C to check scene
    sw      ra,16(sp)           ; + possibly load extended minimap
    sw      t1,20(sp)
    sw      a1,24(sp)

    jal     GerudoCard_ChangeMinimap
    nop

    lw      a1,24(sp)
    lw      t1,20(sp)
    lw      ra,16(sp)
    addiu   sp,sp,24
@@Return:
    lhu     v0,25336(t1)    ; displaced
    jr      ra
    li      at,8289         ; displaced
