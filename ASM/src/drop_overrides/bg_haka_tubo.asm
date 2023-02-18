; Hack for shadow temple spinning pot to drop a flagged collectible
; Actor is in s4
; Loop index is in s0
bg_haka_tubo_hack:
    lh      a3, 0x18(s4)   ; get our new flag out of the z rotation
    beqz    a3, bh_haka_tubo_hack_end
    nop
    add     a3, s0 ; add our loop index
    li      a1, drop_collectible_override_flag
    sh      a3, 0x00(a1)
bh_haka_tubo_hack_end:
    jr      ra
    addiu   a1, sp, 0x005c
