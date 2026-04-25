.headersize(0x80b56910 - 0x00ed2040)

;================================================================================
; Prevent Goron Link first talk softlock if out of range. Add talkState ==
; NPC_TALK_STATE_TALKING as a condition by itself to update talkState and set textId
;================================================================================
; Replaces  lw  a0,32(sp)
;           lw  v0,384(a0)
.org 0x80b58f10         ; in func_80A45288
    jal     EnGo2_TalkstateUpdate
    nop
