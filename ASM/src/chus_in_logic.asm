; 0x00E2D714 (bombchu bowling hook)

logic_chus__bowling_lady_1:
; Change Bowling Alley check to Bombchus or Bomb Bag (Part 1)

    lw      at, BOMBCHUS_IN_LOGIC
    beq     at, r0, @@logic_chus_false
    nop

@@logic_chus_true:
    lb      t7, lo(0x8011A64C)(t7)
    li      t8, 0x09; Bombchus

    beq     t7, t8, @@return
    li      t8, 1
    li      t8, 0

@@return:
    jr      ra
    nop

@@logic_chus_false:
    lw      t7, lo(0x8011A670)(t7)
    andi    t8, t7, 0x18
    jr      ra
    nop


logic_chus__bowling_lady_2:
; Change Bowling Alley check to bombchus or Bomb Bag (Part 2)

    lw      at, BOMBCHUS_IN_LOGIC
    beq     at, r0, @@logic_chus_false
    nop

@@logic_chus_true:
    lb      t3, lo(0x8011A64C)(t3)
    li      t4, 0x09; Bombchus

    beq     t3, t4, @@return
    li      t4, 1
    li      t4, 0

@@return:
    jr      ra
    nop
    
@@logic_chus_false:
    lw      t3, lo(0x8011A670)(t3)
    andi    t4, t3, 0x18
    jr      ra
    nop

logic_chus__shopkeeper:
; Cannot buy bombchu refills without Bomb Bag

    lw      at, BOMBCHUS_IN_LOGIC
    beq     at, r0, @@logic_chus_false
    nop
    
@@logic_chus_true:
    lui     t1, hi(SAVE_CONTEXT + 0x7C)
    lb      t2, lo(SAVE_CONTEXT + 0x7C)(t1) ; bombchu item
    li      t3, 9
    beq     t2, t3, @@return ; if has bombchu, return 1 (can buy)
    li      v0, 0
    li      v0, 2 ; else, return 2 (can't buy)

@@logic_chus_false:
    lui     t1, hi(SAVE_CONTEXT + 0xA3)
    lb      t2, lo(SAVE_CONTEXT + 0xA3)(t1) ; bombbag size
    andi    t2, t2, 0x38
    bnez    t2, @@return       ; If has bombbag, return 1 (can buy)
    li      v0, 0
    li      v0, 2              ; else, return 2, (can't buy)

@@return:
    jr      ra
    nop
