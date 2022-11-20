CURR_ACTOR_SPAWN_INDEX:
.halfword 0x0000
.halfword 0x0000

Actor_SetWorldToHome_Hook:
    addiu   sp, sp, -0x20
    sw      ra, 0x1C (sp)
    jal     Actor_SetWorldToHome_End
    nop
    lw      ra, 0x1C (sp)
    jr      ra
    addiu   sp, sp, 0x20

Actor_UpdateAll_Hook: 
;A0 - Actor Context
;A1 - Actor Entry
;A2 - Global Context
;S0 - Actor Index
;V0 - after the call to Actor_Spawn will contain the address of the actor
    addiu   sp, sp, -0x50
    sw      t0, 0x20(sp)
    sw      t1, 0x24(sp)
    sw      t2, 0x28(sp)
    sw      a0, 0x2C(sp)
    sw      a1, 0x30(sp)
    sw      a2, 0x34(sp)
    sw      s0, 0x38(sp)
    sw      s1, 0x3C(sp)
    sw      ra, 0x40(sp)

    sh      s0, CURR_ACTOR_SPAWN_INDEX

    jal     0x800255C4 ; Call Actor_Spawn
    nop

    lw      a1, 0x30(sp)

    ; Make sure the actor was spawned
    beqz    v0, @@end
    nop
    ; Check if the actor is a Pot
    lh      t0, 0x00(v0) ; Get actor ID
    li      t1, 0x0111 ; Pot ID
    beq     t0, t1, @@set_flag_in_z_rot
    nop
    ; Check if the actor is a flying pot
    li      t1, 0x011D ; Flying Pot ID
    beq     t0, t1, @@set_flag_in_z_rot
    nop
    ; Check if the actor is a Crate
    li      t1, 0x01A0 ; Crate ID
    beq     t0, t1, @@set_flag_in_y_rot
    nop
    ; Check if the actor is a small wooden crate
    li      t1, 0x0110
    beq     t0, t1, @@set_flag_in_z_rot
    nop
    ; Check if the actor is a beehive
    li      t1, 0x019E
    beq     t0, t1, @@set_flag_in_z_rot
    ; Check if the actor is a En_Item00 collectible
    li      t1, 0x0015 ; Check for collectible spawn
    beq     t0, t1, @@set_flag_in_y_rot
    nop
    b       @@call_hack
    nop
    @@set_flag_in_y_rot:
    ; Set the actors home y rotation to the index in the actor list + 1
    lw      s0, 0x38(sp)
    addiu   s0, s0, 0x01
    lb      s1, 0x03(v0) ; get actors room
    sll     s1, s1, 8
    or      s0, s0, s1
    sh      s0, 0x16(v0)
    b		@@call_hack
    nop
    @@set_flag_in_z_rot:
    ; Set the actors home z rotation to the index in the actor list + 1
    lw      s0, 0x38(sp)
    addiu   s0, s0, 0x01
    lb      s1, 0x03(v0) ; get actors room
    sll     s1, s1, 8
    or      s0, s0, s1
    sh      s0, 0x18(v0)
    b       @@call_hack
    nop
    @@call_hack:
    or      a0, r0, v0 ;move the actor pointer to a0
    lw      a1, 0x34(sp)
    jal     Actor_After_UpdateAll_Hack
    nop
    @@end:
    lw      t0, 0x20(sp)
    lw      t1, 0x24(sp)
    lw      t2, 0x28(sp)
    lw      a0, 0x2C(sp)
    lw      a1, 0x30(sp)
    lw      a2, 0x34(sp)
    lw      s0, 0x38(sp)
    lw      s1, 0x3C(sp)
    lw      ra, 0x40(sp)
    jr      ra
    addiu   sp, sp, 0x50 
