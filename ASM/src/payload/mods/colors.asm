magic_colors:
    lhu   t8, CFG_MAGIC_COLOR+0
    sh    t8, 0x0794 (t6)
    lhu   t8, CFG_MAGIC_COLOR+2
    sh    t8, 0x0796 (t6)
    lhu   t8, CFG_MAGIC_COLOR+4
    sh    t8, 0x0798 (t6)
    addu  t8, r0, t6
    jr    ra
    nop

; Set dynamic shop cursor colors
; a0 = shop actor instance
; a1 = color delta 1 (for extreme colors)
; a2 = color delta 2 (for general colors)
shop_cursor_colors:
    addiu   sp, sp, -0x18
    sw      ra, 0x04(sp)
    sw      s0, 0x08(sp)
    move    s0, a0              ; shop actor instance

    lhu     a0, CFG_SHOP_CURSOR_COLOR+0
    jal     apply_color_delta   ; shop cursor red intensity
    nop
    sw      v0, 0x022C(s0)      ; set new red intensity in the actor instance

    lhu     a0, CFG_SHOP_CURSOR_COLOR+2
    jal     apply_color_delta   ; shop cursor green intensity
    nop
    sw      v0, 0x0230(s0)      ; set new green intensity in the actor instance

    lhu     a0, CFG_SHOP_CURSOR_COLOR+4
    jal     apply_color_delta   ; shop cursor blue intensity
    nop
    sw      v0, 0x0234(s0)      ; set new green intensity in the actor instance

    jal     apply_color_delta   ; shop cursor alpha
    li      a0, 0x00FF
    sw      v0, 0x0238(s0)      ; set new alpha in the actor instance

    lw      ra, 0x04(sp)
    lw      s0, 0x08(sp)
    jr      ra
    addiu   sp, sp, 0x18

; Apply the proper delta to a given color intensity
; a0 = u16 base color
; a1 = small delta (to apply if the base color is lower than 0x20 or higher than 0xE0)
; a2 = normal delta (to apply otherwise)
; returns v0 = color with delta applied capped at 0xFF
apply_color_delta:
    slti    at, a0, 0x0020
    bnez    at, @@small_delta
    slti    at, a0, 0x00E0
    beqz    at, @@small_delta
    nop
    b       @@after_delta
    subu    v0, a0, a2
@@small_delta:
    subu    v0, a0, a1
@@after_delta:
    jr      ra
    andi    v0, v0, 0x00FF
