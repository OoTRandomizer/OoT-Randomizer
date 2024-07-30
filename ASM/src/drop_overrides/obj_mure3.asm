; Hacks for rupee towers to drop flagged collectibles

; obj_mure3 pointer should be in s2
; index of the for loop is in s0
obj_mure3_drop_params_hack:
    or      a0, s2, r0 ; Store the actor pointer into a0 instead of PlayState
    jr      ra
    or      a3, s0, r0 ; Store the loop index into a3

; S0 should still have our loop index and it should be 6 when we call here
obj_mure3_redrupee_hack:
    lh      a3, 0x18(s2) ; get our new flag out of the z rotation
    beqz    a3, obj_mure3_redrupee_hack_end
    nop
    add     a3, s0 ; add the loop index
    li      a2, drop_collectible_override_flag ; activate the override
    sh      a3, 0x00(a2)
obj_mure3_redrupee_hack_end:
    jr      ra
    addiu   a2, r0, 0x4002 ; replaced code
