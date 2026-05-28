EnDns_CheckYDist:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    jal     Math_SmoothStepToS  ; displaced call
    li      a3,2000

    lui     at,0x42c8           ; 100.0f
    mtc1    at,$f4              ; Load 100.0f to float register
    lwc1    $f0,148(s0)         ; EnDns Y distance to player
    abs.s   $f0,$f0             ; Absolute EnDns-player Y distance
    c.lt.s  $f0,$f4             ; Y distance < 100.0f?
    bc1tl   @@Return            ; If yes, continue function
    li      v0,1
    li      v0,0                ; Else, to return in caller
@@Return:
    lh      t6,182(s0)          ; displaced
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24
