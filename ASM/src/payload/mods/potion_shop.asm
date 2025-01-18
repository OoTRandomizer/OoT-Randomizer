.definelabel Granny_Item_Save_Offset, 0xD4 + (0x4E * 0x1C) + 0x10

SHUFFLE_GRANNYS_POTION_SHOP:
.byte 0x00
.align 4

potion_shop_fix:
    addiu   sp, sp, -0x20
    sw      v0, 0x08(sp)
    sw      s0, 0x0C(sp)
    sw      v1, 0x10(sp)
    sw      a0, 0x14(sp)
    sw      a1, 0x18(sp)
    sw      ra, 0x1C(sp)

    jal     SaveFile_TradeItemIsTraded
    ori     a0, $zero, 0x30
    lb      v1, SHUFFLE_GRANNYS_POTION_SHOP
    beqz    v1, @@return
    la      v1, SAVE_CONTEXT
    lw      v1, (Granny_Item_Save_Offset)(v1)
    andi    v1, v1, 0x0001
    beqz    v1, @@return
    nop
    ori     v0, $zero, 0x0000

@@return:
    or      t9, v0, $zero

    lw      v0, 0x08(sp)
    lw      s0, 0x0C(sp)
    lw      v1, 0x10(sp)
    lw      a0, 0x14(sp)
    lw      a1, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20


potion_shop_buy_hook:
    ; displaced code
    sw      a1, 0x24(sp)
    lw      a1, 0x24(sp)

    ; set flag if purchasing shuffled item to prevent duping
    lb      v1, SHUFFLE_GRANNYS_POTION_SHOP
    beqz    v1, @@return_buy_hook
    la      v1, SAVE_CONTEXT
    lw      v0, (Granny_Item_Save_Offset)(v1)
    ori     v0, v0, 0x0001
    sw      v0, (Granny_Item_Save_Offset)(v1)

@@return_buy_hook:
    jr      ra
    nop


potion_shop_check_empty_bottle:
    addiu   sp, sp, -0x20
    sw      ra, 0x1C(sp)

    ; don't check for bottle if blue potion item is shuffled
    lb      v0, SHUFFLE_GRANNYS_POTION_SHOP
    bnez    v0, @@return_bottle
    nop

    ; vanilla behavior, refuses sale if player does
    ; not have an empty bottle
    jal     0x80071A94
    nop

@@return_bottle:
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20
