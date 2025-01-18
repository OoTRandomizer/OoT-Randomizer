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


save_scarecrow_song:
; 80057030
; A0 = Scarecrow Song save address (copy to)
; A1 = Scarecrow Song live location (copy from)
; A2 = 0x80
    addiu   sp, sp, -0x18
    sw      a1, 0x0(sp)
    sw      a2, 0x4(sp)
    sw      a3, 0x8(sp)
    sw      ra, 0x10(sp)
    lb      t0, 0x0000(a1)
    addiu   t1, t0, 1
    bne     t1, zero, @@copy_song ; if scarecrow song doesn't begin with a rest, copy it to the save data
    nop
    or      a0, zero, a1
    addiu   a1, a1, 8
    jal     0x57030             ; shift scarecrow song over by 1 note
    addiu   a2, a2, -8

@@copy_song:
    jal     store_scarecrow_fix
    nop
    lw      ra, 0x10(sp)
    lw      a3, 0x8(sp)
    lw      a2, 0x4(sp)
    lw      a1, 0x0(sp)
    j       0x57030
    addiu   sp,sp,0x18
