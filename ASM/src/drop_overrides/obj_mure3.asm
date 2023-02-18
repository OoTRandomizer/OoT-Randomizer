; Hacks for rupee towers to drop flagged collectibles

; Set drop_collectible_override_flag to z rotation + loop index.
; obj_mure3 pointer should be in s2
; index of the for loop is in s0
obj_mure3_hack:
    lh      a3, 0x18(s2)   ; get our new flag out of the z rotation
    beqz    a3, obj_mure3_hack_end
    nop
    add     a3, s0 ; add our loop index
    li      a2, drop_collectible_override_flag ;activate the override
    sh      a3, 0x00(a2)
obj_mure3_hack_end:
    addiu   a2, r0, 0x4000 ; replaced code
    jr      ra
    or      a1, s6, r0 ; replaced code

; S0 should still have our loop index and it should be 6 when we call here
obj_mure3_redrupee_hack:
    lh      a3, 0x18(s2) ; get our new flag out of the z rotation
    beqz    a3, obj_mure3_redrupee_hack_end
    nop
    add     a3, s0 ; add the loop index
    li      a2, drop_collectible_override_flag ;activate the override
    sh      a3, 0x00(a2)
obj_mure3_redrupee_hack_end:
    jr      ra
    addiu   a2, r0, 0x4002 ; replaced code
