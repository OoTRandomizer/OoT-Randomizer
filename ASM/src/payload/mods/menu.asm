equipment_menu_prevent_empty_equip:
    addiu   sp, sp, -0x18
    sw      v0, 0x10 (sp)
    sw      ra, 0x14 (sp)

    jal     equipment_menu_slot_filled
    nop

    bnez    v0, @@return
    lbu     v1, 0x00 (t4) ; Load from usability table

    li      v1, 0xFF ; Prevent equip

@@return:
    lw      v0, 0x10 (sp)
    lw      ra, 0x14 (sp)
    addiu   sp, sp, 0x18
    jr      ra
    li      at, 9 ; Restore value expected by caller

;==================================================================================================

menu_use_blank_description:
    addiu   sp, sp, -0x18
    sw      v0, 0x10 (sp)
    sw      ra, 0x14 (sp)

    lhu     v0, 0x1E8 (s0) ; v0 = menu screen
    bne     v0, 3, @@not_equip_menu
    nop
    ; Check whether the equipment under the cursor has been obtained
    jal     equipment_menu_slot_filled
    nop
    bnez    v0, @@return ; Use default behavior if the equipment is obtained
    nop
    b       @@return
    li      v1, 0x7A ; 0x7A = index of texture that we made blank
@@not_equip_menu:

    ; Item menu: check whether the slot under the cursor is empty
    ; 0x17A is an invalid texture index, used if item ID = 0xFF
    bne     v1, 0x17A, @@return
    nop
    li      v1, 0x7A ; 0x7A = index of texture that we made blank

@@return:
    ; Displaced code
    sll     t4, v1, 10
    addu    a1, t4, t5

    lw      v0, 0x10 (sp)
    lw      ra, 0x14 (sp)
    jr      ra
    addiu   sp, sp, 0x18

;==================================================================================================

equipment_menu_slot_filled:
    addiu   sp, sp, -0x10
    sw      ra, 0x00 (sp)
    sw      v1, 0x04 (sp)
    sw      a0, 0x08 (sp)

    jal c_equipment_menu_slot_filled
    nop

    lw      ra, 0x00 (sp)
    lw      v1, 0x04 (sp)
    lw      a0, 0x08 (sp)
    jr      ra
    addiu   sp, sp, 0x10

equipment_menu_fix:
    and     t6, v1, t5
    bnez    t6, @@return
    lbu     t4, 0x0000 (t7) ; displaced
    addiu   ra, ra, 0x003C

@@return:
    jr      ra
    nop
