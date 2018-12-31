item_menu_prevent_empty_equip:
    ; t1 = item under cursor
    bne     t1, 0xFF, @@return
    lbu     v0, 0x00 (s1) ; Load from usability table

    li      v0, 0xFF ; Prevent equip

@@return:
    jr      ra
    li      at, 9 ; Restore value expected by caller

;==================================================================================================

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
    addiu   sp, sp, -0x18
    sw      s0, 0x10 (sp)
    sw      s1, 0x14 (sp)

    li      v0, SAVE_CONTEXT
    lhu     v0, 0x9C (v0) ; v0 = obtained equipment
    li      s0, SUBSCREEN_CONTEXT
    lhu     s1, 0x232 (s0) ; s1 = cursor vertical position
    sll     s1, s1, 2 ; s1 = s1 * 4
    srlv    v0, v0, s1 ; shift flags for this row to least significant 4 bits
    lhu     s1, 0x228 (s0) ; s1 = cursor horizontal position
    addiu   s1, s1, -1
    li      s0, 1
    sllv    s1, s0, s1 ; s1 = mask for this equipment column
    and     v0, v0, s1

    lw      s0, 0x10 (sp)
    lw      s1, 0x14 (sp)
    jr      ra
    addiu   sp, sp, 0x18
