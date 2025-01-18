.definelabel Shop_Item_Save_Offset, 0xD4 + (0x2C * 0x1C) + 0x10

CFG_MASK_SHOP_HINT:
    .word 0x00000000

Shop_Check_Sold_Out:
    lhu  t6, 0x1c(a0)

    ; if var is under 0x32, never sell out
    addi t5, t6, -0x32
    bltz t5, @@return
    li   v0, 0

    ; t2 = bit mask
    andi t1, t5, 0x07
    li   t2, 1
    sllv t2, t2, t1

    ; t1 = byte offset
    srl  t1, t5, 3

    ; load byte from save
    li   t4, SAVE_CONTEXT
    add  t4, t4, t1
    lbu  t3, (Shop_Item_Save_Offset)(t4)

    ; mask out the bit flag
    and  t3, t3, t2

    ; if not set then, do nothing
    li  v0, 0
    beqz t3, @@return
    nop

    ; Else, change to sold out
    li  t5, 0x26
    sh  t5, 0x1c(a0)       ; set item to SOLD OUT
    li  v0, 1              ; return 1

@@return:
    jr  ra
    nop


Shop_Set_Sold_Out:
    lhu  t6, 0x1c(a1)

    ; if var is under 0x32, never sell out
    addi t5, t6, -0x32
    bltz t5, @@return
    li   v0, 0

    ; t2 = bit mask
    andi t1, t5, 0x07
    li   t2, 1
    sllv t2, t2, t1

    ; t1 = byte offset
    srl  t1, t5, 3

    ; load byte from save
    li   t4, SAVE_CONTEXT
    add  t4, t4, t1
    lbu  t3, (Shop_Item_Save_Offset)(t4)

    ; set and save the bit flag
    or   t3, t3, t2
    sb   t3, (Shop_Item_Save_Offset)(t4)

@@return:
    jr  ra
    nop


Shop_Keeper_Init_ID:
    addiu   sp, sp, -0x20
    sw      a1, 0x10 (sp)
    sw      a2, 0x14 (sp)
    sw      a3, 0x18 (sp)
    sw      ra, 0x1c (sp)

    slti    at, a0, 0x32
    beqz    at, @@mask_shop_shuffle
    move    v0, a0

    jalr    t9
    nop
    b       @@return
    nop

@@mask_shop_shuffle:
    or      a1, s4, $zero
    or      a2, s2, $zero
    or      a3, s6, $zero
    jal     mask_shop_display
    nop

@@return:
    lw      a1, 0x10 (sp)
    lw      a2, 0x14 (sp)
    lw      a3, 0x18 (sp)
    lw      ra, 0x1c (sp)
    jr      ra
    addiu   sp, sp, 0x20


Shop_Keeper_Update_ID:
    addiu   sp, sp, -0x20
    sw      a1, 0x10 (sp)
    sw      a2, 0x14 (sp)
    sw      a3, 0x18 (sp)
    sw      ra, 0x1c (sp)

    slti    at, a0, 0x32
    beqz    at, @@mask_shop_shuffle
    move    v0, a0

    jalr    t9
    nop
    b       @@return
    nop

@@mask_shop_shuffle:
    or      a1, s3, $zero
    or      a2, s1, $zero
    or      a3, s5, $zero
    jal     mask_shop_display
    nop

@@return:
    lw      a1, 0x10 (sp)
    lw      a2, 0x14 (sp)
    lw      a3, 0x18 (sp)
    lw      ra, 0x1c (sp)
    jr      ra
    addiu   sp, sp, 0x20


mask_shop_display:
    addiu   sp, sp, -0x20
    sw      a0, 0x18 (sp)
    sw      ra, 0x1c (sp)

    lh      t4, 0x001C(a1)     ; actor params
    addiu   at, $zero, 0x000A  ; OSSAN_TYPE_MASK
    bne     t4, at, @@return   ; skip if current actor is not the mask salesman
    move    v0, a0
    addiu   at, $zero, 0x0004  ; branch based on shelf slot
    beq     a2, at, @@skull_mask
    addiu   at, $zero, 0x0005
    beq     a2, at, @@keaton_mask
    addiu   at, $zero, 0x0006
    beq     a2, at, @@bunny_hood
    addiu   at, $zero, 0x0007
    beq     a2, at, @@spooky_mask
    addiu   at, $zero, 0x0002
    beq     a2, at, @@mask_of_truth
    nop
    ; rest of the slots are right side masks
    lw      at, CFG_MASK_SHOP_HINT
    bnez    at, @@mask_of_truth
    nop
    b       @@display_func
    ori     a0, $zero, 0x0023

@@mask_of_truth:
@@keaton_mask:
    b       @@return
    move    v0, a0
@@skull_mask:
    b       @@display_func
    ori     a0, $zero, 0x0020
@@bunny_hood:
    b       @@display_func
    ori     a0, $zero, 0x0021
@@spooky_mask:
    ori     a0, $zero, 0x001F
@@display_func:
    sll     t6, a0,  2
    addu    t7, a3, t6
    lw      t9, 0x0000(t7)
    jalr    t9
    nop
    bltz    v0, @@return
    nop
    lw      a0, 0x18 (sp)
    move    v0, a0

@@return:
    lw      a0, 0x18 (sp)
    lw      ra, 0x1c (sp)
    jr      ra
    addiu   sp, sp, 0x20

; override the EnGirlA draw function for
; shuffled one-time purchases
shop_draw_hook:
    lw      a0, 0x0018($sp)
    jal     shop_draw
    lw      a1, 0x001C($sp)
    lw      $ra, 0x0014($sp)
    jr      $ra
    addiu   $sp, $sp, 0x0018

;==================================================================================================

Deku_Check_Sold_Out:
    li      t0, GLOBAL_CONTEXT
    li      t1, SAVE_CONTEXT

    lhu     t2, 0xA4(t0)     ; current scene number
    li      at, 0x3E         ; Grotto Scene
    bne     t2, at, @@continue ; If in grotto, use a free scene

    lbu     t3, 0x1397(t1)   ; Grotto ID
    addi    t2, t3, -0xD6

@@continue:
    lhu     t3, 0x1C(s0)     ; var
    addi    t3, t3, 1
    li      t4, 1
    sllv    t4, t4, t3       ; saleman item bitmask

    li      at, 0x1C         ; Permanant flag entry size
    mult    t2, at
    mflo    t5               ; Permanant flag entry offset

    add     t6, t1, t5
    lw      t7, 0xE4(t6)     ; Saleman bitflag (originally unused)

    and     v0, t4, t7       ; return if flag is set

    jr      ra
    nop


Deku_Set_Sold_Out:
    li      t0, GLOBAL_CONTEXT
    li      t1, SAVE_CONTEXT

    lhu     t2, 0xA4(t0)     ; current scene number
    li      at, 0x3E         ; Grotto Scene
    bne     t2, at, @@continue ; If in grotto, use a free scene

    lbu     t3, 0x1397(t1)   ; Grotto ID
    addi    t2, t3, -0xD6

@@continue:
    lh      t3, 0x1C(a0)     ; var
    addi    t3, t3, 1
    li      t4, 1
    sllv    t4, t4, t3       ; saleman item bitmask

    li      at, 0x1C         ; Permanant flag entry size
    mult    t2, at
    mflo    t5               ; Permanant flag entry offset

    add     t6, t1, t5
    lw      t7, 0xE4(t6)     ; Saleman bitflag [0xD0 (PFlag Table) + 0x10 (unused offself)]

    or      t7, t4, t7       ; return if flag is set
    sw      t7, 0xE4(t6)

    jr      ra
    nop

;==================================================================================================

set_mask_text_hook:
    addiu   sp, sp, -0x20
    sw      a0, 0x10(sp)
    sw      v1, 0x14(sp)
    sw      ra, 0x18(sp)

    lbu     v0, CFG_CHILD_TRADE_SHUFFLE
    beqz    v0, @@return_mask_text
    nop
    jal     SaveFile_TradeItemIsOwned
    or      a0, t9, $zero
    beqz    v0, @@return_mask_text
    or      t7, $zero, $zero
    or      t7, t9, $zero

@@return_mask_text:
    lw      a0, 0x10(sp)
    lw      v1, 0x14(sp)
    lw      ra, 0x18(sp)
    jr      ra
    addiu   sp, sp, 0x20


set_mask_sold_out:
    addiu   sp, sp, -0x20
    sw      t1, 0x10(sp)
    sw      a1, 0x14(sp)
    sw      ra, 0x1C(sp)

    lbu     v0, CFG_CHILD_TRADE_SHUFFLE
    beqz    v0, @@return_mask_so
    nop

    sll     t2, t1,  2
    addu    t3, s0, t2
    jal     Shop_Set_Sold_Out
    lw      a1, 0x01F0(t3)

@@return_mask_so:
    lw      t1, 0x10(sp)
    ; displaced code
    sll     t2, t1,  2
    addu    t3, s0, t2

    lw      a1, 0x14(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20
