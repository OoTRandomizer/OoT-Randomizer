adapt_scarecrow:
    lw   at, (FREE_SCARECROW_ENABLED)
    beqz at, @@default_behavior
    nop

; If free_scarecrow
    lhu  t0, 0x670 (v0)         ; Load Link's StateII
    andi at, t0, 0x0800         ; Mask it with playing_ocarina bit
    li   t0, 0x0800
    jr   ra
    nop

@@default_behavior:             ; If not free_scarecrow
    lhu  t0, 0x04C6 (t0)        ; Load last played song id or w/e
    li   at, 0x0B               ; This is the code for scs
    jr   ra
    nop
; Now we can continue with our comparison between t0 and at
; If at != t0, following code will branch to ignore


scarecrow_vibrato_fix:
    ; Displaced code
    sb      $zero, 0x0000(v1)          ; sCurOcarinaBendIndex = 0;
    lui     $at, 0x8010

    lui     v0, 0x8010
    addiu   v0, v0, 0x2230
    jr      ra
    sb      $zero, 0x0000(v0)          ; sCurOcarinaVibrato = 0
