easier_fishing:
    lw      t2, (SAVE_CONTEXT+4)
    bne     t2, r0, @@L_C24
    andi    t8, t3, 0x0001
    bne     t8, r0, @@return
    lui     t8, 0x4230
    lui     t8, 0x4250
    jr      ra
    nop

@@L_C24:
    bne     t8, r0, @@return
    lui     t8, 0x4210
    lui     t8, 0x4238
@@return:
    jr      ra
    nop

keep_fishing_rod_equipped: 
    lbu     t6, 0x13E2(v1)  ; Temp B/Can Use B Action
    lbu     v0, 0x0068(v1)  ; B button
    li      at, 0x59        ; fishing rod C item
    beq     v0, at, @@return
    li      at, 0xFFF       ; dummy to force always branch
    li      at, 0xFF
@@return:
    jr      ra
    nop

cast_fishing_rod_if_equipped:
    li      a0, SAVE_CONTEXT
    lbu     t6, 0x13E2(a0)  ; Temp B/Can Use B Action
    lbu     v0, 0x0068(a0)  ; B button
    li      at, 0x59        ; fishing rod C item
    beq     v0, at, @@return
    li      at, 0xFFF;
    li      at, 0xFF
@@return:
    jr      ra
    nop