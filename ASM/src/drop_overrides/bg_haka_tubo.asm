; Hack for shadow temple spinning pot to drop a flagged collectible
; Actor is in s4
; Loop index is in s0

bg_haka_tubo_drop_params_hack: ; Hack when setting up the params
    addiu   a1, sp, 0x5C ; Replaced code
    or      a0, s4, r0 ; Put the actor pointer into a0 instead of PlayState
    jr      ra
    or      a3, s0, r0 ; Put the loop index into a3
