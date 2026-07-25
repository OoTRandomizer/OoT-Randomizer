bb_red_wait_hook:
addiu   sp, sp, -0x30
sw      ra, 0x20(sp)
sw      a0, 0x24(sp)
sw      a1, 0x28(sp)
jal     bb_red_wait_hack
nop
lw      a0, 0x24(sp)
lw      a1, 0x28(sp)
jal 0x800214AC ;replaced code
nop
lw      ra, 0x20(sp)
jr      ra
addiu   sp, sp, 0x30
