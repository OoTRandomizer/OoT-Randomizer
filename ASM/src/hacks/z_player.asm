.headersize(0x808301c0 - 0xbcdb70)

;================================================================================
; Fixes Epona spawning on water when exiting into a water entrance while riding.
;================================================================================
; Replaces      sub.s   $f10,$f6,$f8
;               move    a0,s1
;               move    a1,s0
;               swc1    $f10,40(sp)
.org 0x8083aa1c                     ; in Player_SetStartingMovement (start at 0x80393360)
    sub.s   $f12,$f6,$f8            ; (waterbox Y surface - player Y) = ySurface
    move    s7,a2                   ; store Player_Action_StartModeWater address
    jal     Player_CheckEponaWater
    swc1    $f12,40(sp)             ; store new ySurface (restored in end of jal to $f10)
