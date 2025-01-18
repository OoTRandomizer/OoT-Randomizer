gossip_hints:
    addiu   sp, sp, -0x1C
    sw      s1, 0x0014(sp)
    sw      ra, 0x0018(sp)

    li      v1, SAVE_CONTEXT

    ; Get Message ID
    lh      t7, 0x001C(s0)
    andi    t8, t7, 0x00FF
    li      at, 0xFF
    bne     t8, at, @@not_grotto
    addiu   s1, t8, 0x0400

    lbu     t8, 0x1397(v1)       ; Grotto ID
    andi    t8, t8, 0x1F
    addiu   s1, t8, 0x0430
@@not_grotto:

    ; If Special flag is set, always display message
    andi    at, t7, 0x8000
    bnez    at, @@return
    nop

    ; Switch case
    lw      t0, GOSSIP_HINT_CONDITION
    beq     t0, r0, @@default
    li      at, 1
    beq     t0, at, @@stone_of_agony
    nop

@@always_hint:
    ; Always show message
    b       @@return
    nop

@@stone_of_agony:
    ; Show message only if stone of agony is obtained
    lb      at, 0xA5(v1)
    andi    at, at, 0x0020 ; Stone of Agony
    beqz    at, @@no_hint
    nop
    b       @@return
    nop

@@default:
    ; Show message only if worn mask is the mask of truth
    jal     0x79B44
    nop
    li      at, 0x0008
    beq     v0, at, @@return
    nop

@@no_hint:
    ; Change message to no response message id
    li      s1, 0x2053
@@return:
    ; Set the message id to play and return
    sh      s1, 0x010E(s0)
    lw      ra, 0x0018(sp)
    lw      s1, 0x0014(sp)
    jr      ra
    addiu   sp, sp, 0x1C
