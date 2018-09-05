.macro item_menu_description_id, dest_reg, base_reg
    lbu     dest_reg, 0x0074 (base_reg) ; Load the item ID at the selected menu slot
    bne     dest_reg, 0xFF, @@return ; If the slot is not empty, use default behavior
    nop
    li      dest_reg, 0x2C ; 0x2C = "SOLD OUT"
@@return:
.endmacro

item_menu_description_id_periodic:
    item_menu_description_id    t9, t8
    jr      ra
    sh      t9, 0x009A (sp)

item_menu_description_id_immediate_1:
    item_menu_description_id    t4, t9
    jr      ra
    nop

item_menu_description_id_immediate_2:
    item_menu_description_id    t6, t5
    jr      ra
    sh      t6, 0x009A (sp)

item_menu_description_id_immediate_3:
    item_menu_description_id    t7, t6
    jr      ra
    sh      t7, 0x009A (sp)
