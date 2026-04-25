EnGo2_TalkstateUpdate:
    lw      a0,32(sp)           ; EnGo2 actor
    lh      v0,388(a0)          ; interactInfo.talkState
    li      t6,1                ; NPC_TALK_STATE_TALKING
    bnel    t6,v0,@@EnGo2Return ; if not talking, continue as usual
    lw      v0,384(a0)          ; displaced
    addi    ra,0x24             ; if talking, go 0x80b58f3c to run update talkstate
@@EnGo2Return:
    jr      ra
    lw      a1,36(sp)           ; playstate, needed for func_80A44790
