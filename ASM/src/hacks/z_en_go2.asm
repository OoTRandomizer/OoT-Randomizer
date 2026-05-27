.headersize (0x80b56910 - 0x00ed2040)

;================================================================================
; Prevent Goron Link first talk softlock if out of range. Add talkState ==
; NPC_TALK_STATE_TALKING as a condition by itself to update talkState and set textId
;================================================================================
; Replaces: jal Npc_TrackPoint
;           sw  a0,32(sp)
;           lw  a0,32(sp)
;           lw  v0,384(a0)
.org 0x80b58f08         ; in func_80A45288
    jal     EnGo2_TalkstateUpdate
    sw      a0,32(sp)       ; displaced
    bnez    t0,0x80b58f3c   ; if talking, run update talkstate
    nop
