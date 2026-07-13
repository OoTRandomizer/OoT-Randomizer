Player_DetachActorCheckBomb:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    lw      v1,924(s0)          ; displaced, heldActor
    lb      at,CFG_BOMB_OI      ; check if bomb OI enabled
    bnez    at,@@SetBombJump    ; see hack for jump destinations/background
    lui     t9,0x8083
    b       @@CheckConditions
    addi    t9,0x03f8           ; address for function return "1.0"
@@SetBombJump:
    addi    t9,0x03d4           ; address for explosives check "1.1"
@@CheckConditions:
    lui     t0,hi(gKaleidoMgrCurOvl)    ; load player-kaleido overlay manager
    lw      t0,lo(gKaleidoMgrCurOvl)(t0)
    lw      t0,0x14(t0)         ; player load offset
    addu    t9,t0               ; resulting address with offset

    beqz    v1,@@SetBranch      ; if no heldActor, branch
    sw      v1,60(sp)           ; 36+24(sp), heldactor will be set null in function = save
    jal     Player_HoldsHookshot
    move    a0,s0
    bnez    v0,@@SetBranch      ; if heldActor is Hookshot, branch
    lw      v1,60(sp)
    b       @@Return            ; otherwise,
    move    v0,zero             ; don't branch, run whole function
@@SetBranch:
    li      v0,1                ; branch to only do explosives check if bomb OI, or return
@@Return:
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24


Player_CarryActorSetUpperIA:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    lb      at,CFG_BOMB_OI      ; check if bomb OI enabled
    beqz    at,@@Return         ; return if not, this is entirely 1.0 code
    move    s1,a1               ; displaced
    lw      v0,924(s0)          ; heldActor
    bnez    v0,@@Return         ; if no heldActor, check held item action for explosive
    nop

    jal     Player_GetExplosiveHeld
    move    a1,a0
    bltz    v0,@@Return         ; return if not explosive
    move    a0,s1
    lui     t0,hi(gKaleidoMgrCurOvl)    ; load player-kaleido overlay manager
    lw      t0,lo(gKaleidoMgrCurOvl)(t0)
    lw      t0,0x14(t0)         ; player load offset
    la      t9,0x808326a0       ; Player_SetUpperIA
    addu    t9,t0               ; resulting address with offset
    jalr    t9                  ; run function
    move    a1,s0
@@Return:
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24
