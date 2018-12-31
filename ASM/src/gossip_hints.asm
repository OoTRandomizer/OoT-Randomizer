gossip_hints:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    lw      t0, GOSSIP_HINT_CONDITION
    beq     t0, r0, @@default
    li      at, 1
    beq     t0, at, @@stone_of_agony
    nop

@@always_hint:
    li      at, 0x0020
    b       @@return
    li      v0, 0x0020

@@stone_of_agony:
    lb      at, (SAVE_CONTEXT+0xA5)
    andi    at, at, 0x0020 ; Stone of Agony?
    b       @@return
    li      v0, 0x0020

@@default: 
; hints == masks or "none"
    jal     0x79B44
    nop
    li      at, 0x0008

@@return:
    lw      ra, 0x0014(sp)
    jr      ra
    addiu   sp, sp, 0x18