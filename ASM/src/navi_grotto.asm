; Door_Ana - VROM 0xCF7710, VRAM 0x80959A10

@NAVI_GROTTO_ATTRACTION  equ 3
@ATTRACT_NAVI_BITS       equ 0x08000009
@ATTRACT_NAVI_BITS_COMPL equ 0xF7FFFFF6
@AGONY_BYTE              equ SAVE_CONTEXT + 0xA5
@AGONY_MASK              equ 0x20

; NAVI_GROTTO_ATTRACTION values
; value             0    1    2    3    4    5    6    7    8
; attract distance 70  170  280  350  700 1000  100  140  240
; These values (distance^2) are located in an array at 800E8288,
; of type float32, with entries every 8 bytes. The loading
; code for these values is at 8002282C.

; The grotto update function at 80959C4C (update for visible grotto)
; uses the 0x1F byte of the z_Actor struct as a flag during collision
; detection. This byte is reused from the Navi attract distance byte.
; Since we only use this value when the grotto is hidden, the grotto
; will behave normally if this byte is reset to 0x00 when a hidden
; grotto becomes visible.

door_ana_becomes_visible_hook:
    ; dispaced code
    sw      t8, 0x0014(sp)
    sw      a3, 0x0010(sp)
    ; a0 points to z_Actor struct
    lw      t6, 0x0004(a0) ; flags
    li      t5, @ATTRACT_NAVI_BITS_COMPL
    and     t6, t6, t5 ; clear "attract Navi" bits
    sw      t6, 0x0004(a0)
    jr      ra
    sb      r0, 0x001F(a0) ; clear Navi attraction distance (re-used as a flag once visible)


door_ana_update_invisible_pre:
    ; a0 points to z_Actor struct
    lb      t0, @AGONY_BYTE
    andi    t0, @AGONY_MASK
    beqz    t0, @@done ; do nothing without stone of agony
    ori     t0, r0, @NAVI_GROTTO_ATTRACTION
    sb      t0, 0x001F(a0) ; set Navi attraction distance
    lw      t1, 0x0004(a0) ; flags
    li      t0, @ATTRACT_NAVI_BITS
    or      t1, t0, t1     ; set attract Navi bits
    sw      t1, 0x0004(a0) ; write flags
@@done:
    jr      ra
    ; displaced code
    or      s0, a0, r0