;===========================================
; Writes extra data to the initial save file
;===========================================
write_initial_save:
    sb      a1, 33(s1)  ; this was the instruction we replaced to make room for the jump to this function
                        ; it is writing the Z at the end of ZELDAZ in the save file
    ; s1 = pointer to the start of the save file
    ; the only registers I have some confidence can be overridden here are:
    ; a0, a1, a3, t2, t7, t8, t9, v0, v1, s0

    ; loop over the save data table
    li      s0, (INITIAL_SAVE_DATA - 0x04)

@@save_data_loop:
    addiu   s0, s0, 0x04
    lw      t2, 0x00 (s0) ; t2 = override entry
    beqz    t2, @@return  ; Reached end of save data table
    nop
    srl     t7, t2, 16
    add     t7, t7, s1      ; t7 = save data address
    andi    t8, t2, 0xFF00
    srl     t8, t8, 8       ; t8 = write type
    bnez    t8, @@overwrite_type ; if type is 0, use 'or' type (set bits) otherwise use overwrite type (set byte)
    andi    t9, t2, 0xFF    ; t9 = value to write
    lb      t2, 0x00 (t7)   ; t2 = current saved value
    or      t9, t9, t2      ; t9 = given value | current saved value

@@overwrite_type:
    j       @@save_data_loop
    sb      t9, 0x00 (t7)   ; write the value into the save data

@@return:
    jr      ra
    nop
