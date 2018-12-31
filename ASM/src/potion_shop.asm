potion_shop_fix:
    lbu		t9, 0x008A(v0) ; Load adult trade item slot
	li      t1, 0xFF
	beq     t1, t9, @@no_potion
	nop

	slti    t1, t9, 0x31
	bnez    t1, @@return
	li      t9, 0x00

	li      t9, 0x01
	b       @@return
	nop

@@no_potion:
	li      t9, 0x00

@@return:
    jr      ra
	nop