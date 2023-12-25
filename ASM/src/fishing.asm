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

fishing_bite_when_stable:
    lui     t0, 0x801F
    addiu   t0, t0, 0x5DE0  ; BSS fishing data pointer
    lw      at, 0x009C(t0)  ; at = current hook movement
    bnez    at, @@return
    mul.s   f4, f10, f2     ; if the hook is not stable, use the default code (set bite chance)
    lui     t0, 0x3F80      ; else, guarantee bite
    mtc1    t0, f4          ; f4 = 1.00
@@return:
    jr      ra
    nop

give_loach_reward:
    la      at, SAVE_CONTEXT
    lw      v1, 0x0EC0(at)  ; HIGH_SCORE(HS_FISHING)
    andi    t4, v1, 0x8000
    sltiu   t9, t4, 1
    addiu   t9, t9, 0x55    ; set item id for loach reward

    ori     v1, v1, 0x8000
    sw      v1, 0x0EC0(at)  ; set loach reward flag

    jr      ra
    mtc1    zero, f18       ; replaced code

increment_sSinkingLureLocation:
    beq     t2, zero, @@return  ; loads unused byte in fishing overlay
    nop                         ; loach setting uses this as a flag to indicate setting is enabled

    addiu   v1, v1, 1
    addiu   t2, zero, 0x0004
    sltu    t2, t2, v1      ; if sSinkingLureLocation > 4
    sll     t2, t2, 1       ; set sSinkingLureLocation = 1
    srlv    v1, v1, t2
    sb      v1, 0x0000(a0)

@@return:
    sll     t2, v1, 2
    subu    t2, t2, v1 ; replaced code
    jr      ra
    sll     t2, t2, 1  ; replaced code

make_loach_follow_lure:
    addiu   sp, sp, 0xFFEC
    sw      ra, 0x0010 (sp)

    lbu     t1, 0x7AE6(t8)      ; load value of D_80B7E0B6
    addiu   at, zero, 0x0002    ; which has a value of 2 if sinking lure is equipped
    bne     t1, at, @@return    ; if not using sinking lure
    addiu   at, zero, 0xFFFE    ; unset ACTOR_FLAG_0

    lbu     t1, 0x7AE7(t8)      ; loads unused byte in fishing overlay
    beq     t1, zero, @@return  ; loach setting uses this as a flag to indicate setting is enabled
    addiu   at, zero, 0xFFFE    ; unset ACTOR_FLAG_0

    or      a0, s0, zero
    addiu   t1, t8, 0xB288
    jalr    t1              ; func_80B70ED4
    addiu   a1, s1, 0x0014

    addiu   at, zero, 0xFFFF    ; preserve current actor flags
@@return:
    lw      t1, 0x0004(s0)
    and     t1, t1, at
    lw      ra, 0x0010 (sp)
    jr      ra
    addiu   sp, sp, 0x0014
