Kaleido_GameOverFillMagic:
    lh	    t6,5104(t1)             ; magic state
    li      at,9                    ; If current magic state is FILL
    beq     at,t6,@@PreserveFill
    li      at,8                    ; or STEP_CAPACITY
    beq     at,t6,@@PreserveFill    ; preserve current fill target
    lh      at,50(t1)               ; If current magic level is zero
    bnezl   at,@@Return             ; also preserve fill target
    nop
@@PreserveFill:
    sh	    zero,5108(t1)           ; Zero capacity here
    addi    ra,8                    ; to skip zeroing fill target
@@Return:
    jr      ra
    sh	    zero,5104(t1)           ; displaced
