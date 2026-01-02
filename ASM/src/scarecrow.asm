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
