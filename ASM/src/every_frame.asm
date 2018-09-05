every_frame:
    sw      a0, 0x68 (sp)
    sw      a1, 0x6C (sp)
    sw      a2, 0x70 (sp)
    sw      a3, 0x74 (sp)
    addiu   sp, sp, -0x18
    sw      v1, 0x10 (sp)
    sw      ra, 0x14 (sp)

    ; Don't give pending item during cutscene. This can lead to a crash when giving an item
    ; during another item cutscene.
    li      t2, PLAYER_ACTOR
    lb      t0, 0x066C (t2)    ;link's state
    andi    t0, 0x20           ;cutscene
    bnez    t0, @@no_pending_item
    nop

    ; clear pending item index
    li      t1, PENDING_SPECIAL_ITEM_END
    li      t2, 0xFF
    sb      t2, 0x00 (t1)

    ; If there is a pending item, try to make the player instance receive it. If the player has
    ; control on this frame, they will receive the item. Otherwise nothing will happen, and
    ; we try again next frame.
    li      t1, PENDING_SPECIAL_ITEM 
    li      t2, -1
    li      t4, (PENDING_SPECIAL_ITEM_END - PENDING_SPECIAL_ITEM) ; max number of entries
@@loop:
    addi    t2, t2, 0x01
    beq     t2, t4, @@no_pending_item ; stop if end of list
    add     t3, t1, t2

    lb      t0, 0x00 (t3)
    beqz    t0, @@loop ; loop if index is empty
    nop

    ; Store index of pending item to be given
    li      t1, PENDING_SPECIAL_ITEM_END
    sb      t2, 0x00 (t1)

    ; Disable warping when there is a pending item. Currently this code is only used in places
    ; where warping is allowed, so warping can always be re-enabled after the item is received.
    li      t1, GLOBAL_CONTEXT + 0x104E4
    li      t2, 1
    sh      t2, 0x00 (t1)
    ; PLAYER_ACTOR+0x0424 holds the item to be received. +0x0428 holds a pointer to the actor
    ; giving the item. The game is not picky about this actor, it just needs to read a non-zero
    ; value at actor+0x0130, and it overwrites actor+0x0118. Construct a dummy actor in an usused
    ; memory area to satisfy these requirements.
    li      t1, DUMMY_ACTOR
    li      t2, 1
    sw      t2, 0x130 (t1)
    li      t2, PLAYER_ACTOR
    sb      t0, 0x0424 (t2)
    sw      t1, 0x0428 (t2)
    jal     store_item_data
    nop
@@no_pending_item:

    lw      v1, 0x10 (sp)
    lw      ra, 0x14 (sp)
    addiu   sp, sp, 0x18
    lw      a0, 0x68 (sp)
    lw      a1, 0x6C (sp)
    lw      a2, 0x70 (sp)
    lw      a3, 0x74 (sp)

    lh      t6, 0x13C4 (v1) ; Displaced code

    jr      ra
    nop
