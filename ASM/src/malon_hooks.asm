malon_goto_item:
    lb      t2, SONGS_AS_ITEMS
    beqz    t2, @@return   ;if songs as items is not on then return normally
    lw      t3, 0x138(a2)  ;overlay table entry
    lw      t3, 0x10(t3)   ;overlay address
    addiu   t1, t3, 0x0ADC ;item actionFunc offset
@@return:
    jr      ra
    sw      t1, 0x0180(a2)

;============================================

;if songs as items is not on, show song staff
malon_handle_staff:
    addiu   sp, sp, -0x18
    sw      ra, 0x14(sp)
    lb      t2, SONGS_AS_ITEMS
    bnez    t2, @@return
    nop
    jal     0x800DD400 ;show staff
    nop
@@return:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18

;============================================

;displaced stuff to make room for saving ra
malon_ra_displaced:
    lui   at, 0x80
    lui   t8, 0x0001
    jr    ra
    lw    t6, 0x0670(v0)

;if song as items is on, dont wait for dialog state
malon_songs_as_items:
    lb      t2, SONGS_AS_ITEMS
    beqz    t2, @@return
    nop
    li      t8, 0x03 ;if songs as items is on, make t8 3 so it doesnt wait on dialog state
@@return:
    la      a3, SAVE_CONTEXT
    jr      ra
    addiu   at, r0, 0x0003 ;displaced

;if songs as items is on, give item and change dialog state. return
malon_check_give_item:
    lb      t2, SONGS_AS_ITEMS
    beqz    t2, @@return ;if songs as items is not on, reutrn
    nop
    jal     override_epona_song ;give item for songs as items
    nop
    la      t0, 0x801D8966 ;globalCtx->msgCtx.unk_E3EE
    li      t1, 0x0004
    sh      t1, 0x00(t0)
    nop
@@return:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18

;============================================
;if songs as items is not on, show a text box saying what song you got
malon_show_text:
    addiu   sp, sp, -0x20
    sw      ra, 0x14(sp)
    sw      at, 0x18(sp)
    sw      a0, 0x1C(sp)
    lb      t2, SONGS_AS_ITEMS
    bnez    t2, @@return ;if songs as items is on, reutrn
    nop
    la      a0, GLOBAL_CONTEXT
    lbu     a1, MALON_TEXT_ID
    li      a2, 0
    jal     0x800DCE14   ;show song text
    nop
    li      a0, 0x4802   ;NA_SE_SY_CORRECT_CHIME
    jal     0x800646F0   ;play "correct" sound
    nop
@@return:
    lw      a0, 0x1C(sp)
    lw      at, 0x18(sp)
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x20

;=============================================
MALON_GAVE_ICETRAP:
.byte 0x00
.align 4

;after item is given and text is closed, reload the scene
malon_reload:
    addiu   sp, sp, -0x20
    sw      ra, 0x14(sp)
    sw      a0, 0x18(sp)
    lb      t5, MALON_GAVE_ICETRAP
    bnez    t5, @@malon_gave_ice_trap
    nop
    la      t0, PLAYER_ACTOR
    lw      t1, 0x670(t0)    ;stateFlags2
    li      t2, 0x4000
    and     t3, t1, t2       ;stateFlags2 & 0x4000
    beqz    t3, @@check_text ;dont set flag if player is not frozen
    nop
    li      t0, 1
    sb      t0, MALON_GAVE_ICETRAP
    b       @@return

@@malon_gave_ice_trap:
    la      t0, PLAYER_ACTOR
    lw      t1, 0x670(t0)    ;stateFlags2
    li      t2, 0x4000
    and     t3, t1, t2       ;stateFlags2 & 0x4000
    beqz    t3, @@reload     ;reload if freeze is finished
    nop
    b       @@return

@@check_text:
    addiu   a0, a1, 0x20D8 ;msgCtx
    jal     0x800DD464     ;returns dialog state
    nop
    addiu   at, r0, 0x0002
    bne     v0, at, @@return
    nop
    la      t0, 0x801D8966 ;globalCtx->msgCtx.unk_E3EE
    li      t1, 0x0004
    sh      t1, 0x00(t0)
@@reload:
    la      t3, SAVE_CONTEXT
    lb      t4, 0xEDE(t3)
    ori     t4, t4, 0x01
    sb      t4, 0xEDE(t3)  ;set flag for learned song
    la      t1, 0x801DA2BA
    li      t0, 0x02AE
    sh      t0, 0x0(t1)    ;malon from eponas song entrance
    li      t0, 0x2A
    la      t1, 0x801DA2FE
    sb      t0, 0x0(t1)    ;transition type
    li      t0, 0x14
    la      t1, 0x801DA2B5
    sb      t0, 0x0(t1)    ;load flag
@@return:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x20
