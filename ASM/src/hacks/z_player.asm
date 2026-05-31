.headersize (0x808301c0 - 0xbcdb70)

;================================================================================
; Fixes softlock when starting cutscene while dismounting a ladder.
;================================================================================
; Replaces  lw      t8,1644(s0)
;           lui     at,0xffdf
;           ori     at,at,0xffff
;           and     t9,t8,at
.org 0x8084a6c4         ; in Player_Action_DismountLadder (0x803a3064)
    jal     Player_LadderCutsceneFix
    lw      t8,1644(s0)     ; displaced
    bnez    v0,0x8084a6e0   ; branch to load LinkAnimation argument if in CS/using CS item
    nop

;================================================================================
; Call Matrix_Push() and Matrix_Pop() when drawing Bunny Hood and Hover Boots
; hover effect, to avoid very big frozen drawing if frozen
;================================================================================
; Replaces lw      v0,704(s1)
;          lui     t8,0xdb06
.org 0x808482f8
    jal     Player_BunnyMatrixPush
    nop

; Replaces lw      v0,704(s1)
.org 0x808483b4
    jal     Player_BunnyMatrixPop
    ;lui    t3,0xde00          ; Needs to be here because it's a branch target address

; Replaces lwc1    $f12,36(s0)
;          lw      a2,44(s0)
.org 0x8084852c
    jal     Player_HoverMatrixPush
    nop

; Replaces sw      v0,4(s0)
;          lw      v1,720(s1)
.org 0x80848578
    jal     Player_HoverMatrixPop
    sw      v0,4(s0)
