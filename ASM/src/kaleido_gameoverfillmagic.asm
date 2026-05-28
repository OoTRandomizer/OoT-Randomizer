Kaleido_GameOverFillMagic:
    sh      zero,5156(t1)           ; displaced
    lh      t6,5104(t1)             ; magic state
    li      at,9                    ; If current magic state is FILL
    beq     at,t6,@@PreserveFill
    li      at,8                    ; or STEP_CAPACITY
    beq     at,t6,@@PreserveFill    ; preserve current fill target
    lh      at,50(t1)               ; If current magic level is zero,
    bnezl   at,@@Return             ; also preserve fill target
    move    v0,zero                 ; Else - zero fill target in caller
@@PreserveFill:
    sh      zero,5108(t1)           ; Preserve fill target: set zero capacity here
    li      v0,1                    ; and skip zero fill target in caller
@@Return:
    jr      ra
    sh      zero,5104(t1)           ; displaced
