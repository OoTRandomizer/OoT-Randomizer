EnGo2_TalkstateUpdate:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    jal     Npc_TrackPoint
    nop
    lw      a0,56(sp)           ; EnGo2 actor saved at old 32(sp)
    lh      v0,388(a0)          ; interactInfo.talkState
    li      t6,1                ; NPC_TALK_STATE_TALKING
    bnel    t6,v0,@@EnGo2Return ; if not talking, continue as usual
    li      t0,0                ; t0 because v0 is in use
    li      t0,1                ; else, update talkstate
@@EnGo2Return:
    lw      ra,16(sp)
    addiu   sp,sp,24
    lw      v0,384(a0)          ; displaced
    jr      ra
    lw      a1,36(sp)           ; playstate, needed for func_80A44790
