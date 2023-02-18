;==================================================================================================
; Fixes songs in certain scenes to allow for various song learning function to properly play
; through their scripts.
;==================================================================================================
suns_song_fix_event:
    addu    at, at, s3
    addi    t7, r0, 0x0047
    bne     t7, t2, @@return
    lui     v0, 0x8012
    lw      v0, 0xA5D4(v0)
    lw      t7, 0x00A4(s3)
    sra     t7, t7, 8
    bnez    v0, @@child
    li      v0, 0x4830
    bne     t7, v0, @@return
    nop
    addiu   t9, r0, 0x0003
    b       @@return

@@child:
    li  v0, 0x6311
    bne     t7, v0, @@return
    nop
    addiu   t9, r0, 0x0003

@@return:
    jr      ra
    nop

;==================================================================================================
warp_song_fix:
    addu    at, at, s3
    lui     v0, 0x8012
    lw      v0, 0xA5D4(v0)
    lw      t7, 0x00A4(s3)
    sra     t7, t7, 8
    bnez    v0, @@child
    li      v0, 0x4830
    bne     t7, v0, @@return
    nop
    addiu   t9, r0, 0x0003
    b       @@return

@@child:
    li  v0, 0x6311
    bne     t7, v0, @@return
    nop
    addiu   t9, r0, 0x0003

@@return:
    jr      ra
    nop

;==================================================================================================
; Change Epona check for owning or being able to play the song
;==================================================================================================
Check_Has_Epona_Song:
    ; If not Epona owned flag, then return result
    li      at, 0x18
    bne     a0, at, @@return
    nop

    ; If epona is owned, then return True
    bnez    v0, @@return
    nop

    li      t2, SAVE_CONTEXT

    ; Check if has Epona's Song
    lb      t0, 0xA6(t2)
    andi    t0, t0, 0x20
    beqz    t0, @@return     ; Return False if no song
    li      v0, 0

    ; Check if has Ocarina
    lb      t0, 0x7B(t2)
    li      t1, 0x07         ; Fairy ocarina
    beq     t0, t1, @@has_ocarina
    li      t1, 0x08         ; Ocarina of Time
    beq     t0, t1, @@has_ocarina
    nop

    ; Else False
    j       @@return
    li      v0, 0

@@has_ocarina:
    ; Set has Epona flag and return True
    lb      t0, 0xED6(t2)
    ori     t0, t0, 0x01
    sb      t0, 0xED6(t2)
    li      v0, 1

@@return:
    jr      ra
    nop
