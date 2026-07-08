.headersize(0x808301c0 - 0xbcdb70)

;==================================================================================
; 1. Fixes Epona spawning on water when exiting into a water entrance while riding.
; 2. Prevents Link from swimming when entering Domain to Lake when low water.
;==================================================================================
; Replaces      sub.s   $f10,$f6,$f8
;               move    a0,s1
;               move    a1,s0
;               swc1    $f10,40(sp)
;               lw      t8,1640(s0)
;               lwc1    $f16,36(t8)
.org 0x8083aa1c                     ; in Player_SetStartingMovement
    sub.s   $f12,$f6,$f8            ; (waterbox Y surface - player Y) = ySurface
    move    s7,a2                   ; store Player_Action_StartModeWater address
    jal     Player_CallCheckEponaWater
    swc1    $f12,40(sp)             ; store new ySurface (restored in end of jal to $f10)
    bnez    v0,0x8083aa98           ; not swim entry
    nop

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
