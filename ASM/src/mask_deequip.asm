; Check if equipped mask = item in child trade slot before de-equipping mask.
mask_check_trade_slot:
    lui     v1, 0x8012          ; Save Context pt. 1
    lbu     t7, 0x014F(t0)      ; Equipped Mask Param
    addiu   v1, v1, 0xA5D0      ; Save Context pt. 2
    addiu   t7, t7, 0x23        ; Add 0x23 to equipped mask param to get item number.
    lbu     t8, 0x8B(v1)        ; Item in Child Trade Slot
    nop
    beq     t7, t8, @@return    ; If they are equal, skip de-equipping the mask.
    nop
    jr      ra
    sb      zero, 0x014F(t0)    ; De-equip Mask
    @@return:
    jr      ra
    nop
