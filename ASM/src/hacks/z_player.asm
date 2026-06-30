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

;================================================================================
; Prevent softlock if Hookshot actor cannot spawn when equipping
; (memory shortage due to Hyrule Field glitch, child equip etc)
;================================================================================
; Replaces  lw      a1,60(sp)
;           sw      v0,924(a1)
.org 0x808319d4         ; in Player_InitHookshotIA (0x8038a374)
     jal     Player_HookshotCheckActorSpawn
     lw      a1,60(sp)       ; displaced (loads player)

;================================================================================
; Bomb OI
;================================================================================
; Replaces: move    s0,a0
;           move    s1,a1
;           sw      ra,28(sp)
.org 0x8083377c     ; Player_UpperAction_CarryActor
    sw      ra,28(sp)   ; displaced
    jal     Player_CarryActorSetUpperIA
    move    s0,a0       ; displaced

; Replaces: sw      a0,40(sp)
;           lw      v1,924(s0)
;           move    a0,s0
;           beqzl   v1,808303fc
;           lw      ra,28(sp)
;           jal     Player_HoldsHookshot
;           sw      v1,36(sp)
;           bnez    v0,808303f8
.org 0x80830390     ; Player_DetachHeldActor
    jal     Player_DetachActorCheckBomb
    sw      a0,40(sp)       ; displaced
    bnez    v0,@@Branch
    nop
    b       0x808303b4      ; run function normally
    nop
@@Branch:
    jr      t9      ; branch to explosives check or return depending on setting
    nop

; Replaces: li      at,-2049
;           move    a0,s0
;           and     t7,t6,at
;           jal     Player_GetExplosiveHeld
;           sw      t7,1644(s0)
.org 0x808303c8     ; Player_DetachHeldActor
    li      at,-2049    ; change order of instructions to allow branching from higher up
    and     t7,t6,at
    sw      t7,1644(s0)
    jal     Player_GetExplosiveHeld
    move    a0,s0
