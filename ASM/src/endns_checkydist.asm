EnDns_CheckYDist:
    lui     at,0x42c8           ; 100.0f
    mtc1    at,$f4              ; Load 100.0f to float register
    lwc1    $f0,148(s0)         ; EnDns Y distance to player
    abs.s   $f0,$f0             ; Absolute EnDns-player Y distance
    c.lt.s  $f0,$f4             ; Y distance < 100.0f?
    bc1tl   @@EnDns_YReturn     ; If yes, continue function
    nop                         ; Else...
    addi    ra,ra,0x8c          ; Go to 0x80a7550c (EnDns_Idle function return)
@@EnDns_YReturn:
    jr      ra                  ; Unchanged ra at 0x80a75598
    move    a0,s0
