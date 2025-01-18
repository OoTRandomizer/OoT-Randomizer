; 0x00E2D714 (bombchu bowling hook)

logic_chus__bowling_lady_1:
; Change Bowling Alley check to Bombchus or Bomb Bag (Part 1)

    lw      at, FREE_BOMBCHU_DROPS
    beq     at, r0, @@has_chus_false
    nop

    lb      at, lo(0x8011A64C)(t7)
    li      t8, 0x09; Bombchus

    bne     at, t8, @@has_chus_false
    nop
    li      t8, 1
    jr      ra
    nop

@@has_chus_false:
    lw      t7, lo(0x8011A670)(t7)
    andi    t8, t7, 0x18
    jr      ra
    nop


logic_chus__bowling_lady_2:
; Change Bowling Alley check to bombchus or Bomb Bag (Part 2)

    lw      at, FREE_BOMBCHU_DROPS
    beq     at, r0, @@has_chus_false
    nop

    lb      at, lo(0x8011A64C)(t3)
    li      t4, 0x09; Bombchus

    bne     at, t4, @@has_chus_false
    nop
    li      t4, 1
    jr      ra
    nop

@@has_chus_false:
    lw      t3, lo(0x8011A670)(t3)
    andi    t4, t3, 0x18
    jr      ra
    nop

logic_chus__shopkeeper:
; Cannot buy bombchu refills without Bomb Bag

    lw      at, FREE_BOMBCHU_DROPS
    beq     at, r0, @@logic_chus_false
    nop

@@logic_chus_true:
    lui     t1, hi(SAVE_CONTEXT + 0x7C)
    lb      t2, lo(SAVE_CONTEXT + 0x7C)(t1) ; bombchu item
    li      t3, 9
    beq     t2, t3, @@return ; if has bombchu, return 0 (can buy)
    li      v0, 0
    jr      ra
    li      v0, 2 ; else, return 2 (can't buy)

@@logic_chus_false:
    lui     t1, hi(SAVE_CONTEXT + 0xA3)
    lb      t2, lo(SAVE_CONTEXT + 0xA3)(t1) ; bombbag size
    andi    t2, t2, 0x38
    bnez    t2, @@return       ; If has bombbag, return 0 (can buy)
    li      v0, 0
    li      v0, 2              ; else, return 2, (can't buy)

@@return:
    jr      ra
    nop


logic_chus__carpet_dude_1:
    ; don't do anything if carpet dude is shuffled
    lb      t0, SHUFFLE_CARPET_SALESMAN
    lb      t7, -0x59B4(t6)     ; bombchu inventory slot item
    bnez    t0, @@return        ; skip if the salesman is randomized
    lh      t6, -0x59FC(t6)     ; displaced code

    bgtz    t7, @@return    ; allow purchase if bombchu slot isn't empty
    nop

    lw      at, FREE_BOMBCHU_DROPS
    beq     at, r0, @@return    ; allow purchase if bombchu bag is disabled
    nop

    ; Simulate empty wallet to prevent giving bombchus.
    ; Text ID is modified in logic_chus__carpet_dude_2 to
    ; clarify a bombchu bag is needed
    ori     t6, $zero, 0x0000

@@return:
    jr      $ra
    nop


logic_chus__carpet_dude_2:
    addiu   $sp, $sp, -0x18
    sw      $ra, 0x0014($sp)
    ; don't do anything if carpet dude is shuffled
    lb      t0, SHUFFLE_CARPET_SALESMAN
    bnez    t0, @@not_enough_rupees   ; skip if the salesman is randomized
    nop

    bgtz    t7, @@not_enough_rupees   ; bombchu inventory slot isn't empty
    nop

    lw      at, FREE_BOMBCHU_DROPS
    beq     at, r0, @@not_enough_rupees    ; bombchu inventory slot is empty
    nop                                    ; but bombchu bag is disabled

    jal     0x800DCE80
    addiu   a1, $zero, 0x901A   ; custom text ID for missing bombchu bag
    b       @@return
    nop

@@not_enough_rupees:
    jal     0x800DCE80
    addiu   a1, $zero, 0x6075
@@return:
    lw      $ra, 0x0014($sp)
    jr      $ra
    addiu   $sp, $sp, 0x18

; Override the segment offset to use to draw bombchu drops (Collectible 05)
; a1 = drop icon segment offset to use for this collectible
chu_drop_draw:
    lw      v1, 0x0038(sp)
    lh      v1, 0x001C(v1)      ; actor variable (collectible id)
    li      t0, 0x0005
    bne     v1, t0, @@return    ; if not a bombchu drop, return
    nop
    li      a1, 0x0403FD80      ; else, override the icon segment offset with bombchu drop icon

@@return:
    jr      ra
    lui     at, 0x00FF          ; displaced code
