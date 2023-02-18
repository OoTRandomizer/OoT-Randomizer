; goron spinning pot hacks to drop override collectibles

; hack for when it drops 3 bombs
; Loop variable stored in s7
; Actor pointer is stored in s0 
bg_spot18_basket_bombs_hack:
    lh      a3, 0x18(s0)   ; get our new flag out of the z rotation
    beqz    a3, bg_spot18_basket_bombs_end
    nop
    add     a3, s7 ; add our loop index
    li      a1, drop_collectible_override_flag
    sh      a3, 0x00(a1)
bg_spot18_basket_bombs_end:
    jr      ra
    or      a1, s3, r0

; hack for when it drops 3 rupees
; Loop variable stored in s7
; Actor pointer is stored in s0 hopefully
bg_spot18_basket_rupees_hack:
    lh      a3, 0x18(s0)   ; get our new flag out of the z rotation
    ori     a2, r0, 0x0000 ; clear a2. this is also exactly what it needs to be if we dont hack.
    beqz    a3, bg_spot18_basket_rupees_end
    nop
    add     a3, s7 ; add our loop index
    addiu   a3, a3, 3 ; add 3 flag because we used 3 for the bomb hack.
    li      a1, drop_collectible_override_flag
    sh      a3, 0x00(a1)
bg_spot18_basket_rupees_end:
    addiu   s3, sp, 0x0044
    jr      ra
    addiu   s1, r0, 0x0003

; hack for the rupees that drop w/ the heart piece
bg_spot18_basket_drop_heartpiece_rupees:
    addiu   sp, sp, -0x0020
    sw      ra, 0x0010(sp)
    or      a0, s4, r0
    addiu   a2, r0, 0x0002
    lh      a3, 0x18(s0)   ; get our new flag out of the z rotation
    beqz    a3, bg_spot18_basket_drop_heartpiece_redrupee_end
    nop
    addiu   a3, a3, 6 ; add 6 because we used 3 for the bomb hack and 3 for the rupees
    li      a1, drop_collectible_override_flag
    sh      a3, 0x00(a1)
bg_spot18_basket_drop_heartpiece_redrupee_end:
    jal     0x80013678 ; call dropcollectible
    or      a1, s3, r0
    beqz    v0, bg_spot18_basket_drop_heartpiece_bluerupee
    or      a0, s4, r0
    swc1    f20, 0x0060(v0)
    lh      t6, 0x0000(s2)
    sh      t6, 0x0032(v0)
bg_spot18_basket_drop_heartpiece_bluerupee:
    addiu   a2, r0, 0x0001
    lh      a3, 0x18(s0)   ; get our new flag out of the z rotation
    beqz    a3, bg_spot18_basket_drop_heartpiece_bluerupee_end
    addiu   a3, a3, 7 ; add one more to a3 for the other rupee
    li      a1, drop_collectible_override_flag
    sh      a3, 0x00(a1)
bg_spot18_basket_drop_heartpiece_bluerupee_end:
    jal     0x80013678 ; call dropcollectible
    or      a1, s3, r0
    beqz    v0, bg_spot18_basket_drop_heartpiece_rupees_end
    or      a0, s4, r0
    swc1    f20, 0x0060(v0)
    lh      t6, 0x0004(s2)
    sh      t6, 0x0032(v0)
bg_spot18_basket_drop_heartpiece_rupees_end:
    lw      ra, 0x0010(sp)
    jr      ra
    addiu   sp, sp, 0x0020
