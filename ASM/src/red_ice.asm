red_ice_alpha:
    ; set initial red ice opacity
    ; a0 = red ice actor
    lw      t0, CHEST_TEXTURE_MATCH_CONTENTS
    lw      t1, CHEST_SIZE_MATCH_CONTENTS
    or      t3, t0, t1
    lw      t2, CHEST_SIZE_TEXTURE
    or      t3, t3, t2
    beqz    t3, @@return            ; keep opaque if chest appearance matches contents is disabled
    li      t7, 0xFF                ; fully opaque by default
    lhu     t0, 0x001C(a0)          ; actor params
    andi    t0, t0, 0x0700          ; red ice type
    beq     t0, 0x0300, @@return    ; keep type 3 (red ice wall) opaque
    nop
    ; make other types semitransparent
    li      t7, 0x7F                ; 50% opacity
@@return:
    jr      ra
    sh      t7, 0x01F0(a0)
