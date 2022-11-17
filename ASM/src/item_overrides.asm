inventory_check:
    andi    a0, a0, 0xFF
    li      t0, SAVE_CONTEXT

    beq     a0, 0x8C, @@return ; Deku Nuts (5)
    lbu     v0, 0x75 (t0)

    beq     a0, 0x8D, @@return ; Deku Nuts (10)
    lbu     v0, 0x75 (t0)

    beq     a0, 0x00, @@return ; Deku Stick
    lbu     v0, 0x74 (t0)

    beq     a0, 0x8A, @@return ; Deku Sticks (5)
    lbu     v0, 0x74 (t0)

    beq     a0, 0x8B, @@return ; Deku Sticks (10)
    lbu     v0, 0x74 (t0)

    beq     a0, 0x58, @@return ; Deku Seeds (5)
    li      v0, 0x00

    beq     a0, 0x78, @@return ; Small Magic Jar
    li      v0, 0x00

    beq     a0, 0x79, @@return ; Large Magic Jar
    li      v0, 0x00

    li      v0, 0xFF

@@return:
    jr      ra
    nop

;==================================================================================================

override_object_npc:
    lw      a2, 0x0030 (sp)
    j       override_object
    lh      a1, 0x0004 (a2)

override_object_chest:
    lw      t9, 0x002C (sp)
    j       override_object
    lh      a1, 0x0004 (t9)

override_object:
    li      t2, active_item_row
    lw      t2, 0x00 (t2)
    beqz    t2, @@return
    nop

    ; Override Object ID
    li      a1, active_item_object_id
    lw      a1, 0x00 (a1)

@@return:
    jr      ra
    nop

;==================================================================================================

override_graphic:
    li      t0, active_item_row
    lw      t0, 0x00 (t0)
    beqz    t0, @@return
    nop

    ; Override Graphic ID
    li      v1, active_item_graphic_id
    lw      v1, 0x00 (v1)

@@return:
    ; Displaced code
    abs     t0, v1
    sb      t0, 0x0852 (a0)
    jr      ra
    nop

;==================================================================================================

override_chest_speed:
    li      t0, FAST_CHESTS
    lbu     t0, 0x00 (t0)
    bnez    t0, @@return
    li      t3, -1 ; Always use fast animation

    li      t0, active_item_row
    lw      t0, 0x00 (t0)
    beqz    t0, @@return
    move    t3, t2 ; If no active override, use original value

    li      t0, active_item_fast_chest
    lw      t0, 0x00 (t0)
    bnez    t0, @@return
    li      t3, -1 ; Active override uses fast animation

    li      t3, 1 ; Default case, use long animation

@@return:
    bltz    t3, @@no_call
    nop
     ; Displaced function call
    addiu   sp, sp, -0x18
    sw      t3, 0x10 (sp)
    sw      ra, 0x14 (sp)
    jal     0x80071420
    nop
    lw      t3, 0x10 (sp)
    lw      ra, 0x14 (sp)
    addiu   sp, sp, 0x18
@@no_call:

    jr      ra
    nop

;==================================================================================================

override_text:
    lbu     a1, 0x03 (v0) ; Displaced code

    li      t0, active_item_row
    lw      t0, 0x00 (t0)
    beqz    t0, @@return
    nop

    ; Override Text ID
    li      a1, active_item_text_id
    lw      a1, 0x00 (a1)

@@return:
    jr      ra
    nop

;==================================================================================================

override_action:
    addiu   sp, sp, -0x18
    sw      s0, 0x10 (sp)
    sw      ra, 0x14 (sp)

    li      t0, active_override_is_outgoing
    lw      t0, 0x00 (t0)
    andi    t0, t0, 0x01
    bnez    t0, @@return
    li      s0, 0x41 ; Outgoing co-op item, do nothing for this player

    li      a0, active_item_row
    lw      a0, 0x00 (a0)
    beqz    a0, @@return
    lbu     s0, 0x00 (v0) ; No active override, load non-override action ID

    ; Override Action ID
    li      t0, active_item_action_id
    lw      s0, 0x00 (t0)

    ; a0 = item row
    jal     call_effect_function
    nop

@@return:
    jal     after_item_received
    nop

    move    a1, s0 ; Base game expects this value in a1

    lw      s0, 0x10 (sp)
    lw      ra, 0x14 (sp)
    jr      ra
    addiu   sp, sp, 0x18

;==================================================================================================

get_item_hook:
    addiu   sp, sp, -0x20
    sw      a3, 0x10 (sp)
    sw      v0, 0x14 (sp)
    sw      v1, 0x18 (sp)
    sw      ra, 0x1C (sp)

    ; a0 = actor giving item
    ; a2 = incoming item id
    jal     get_item
    move    a1, a3 ; a1 = player instance

    lw      a3, 0x10 (sp)
    lw      v0, 0x14 (sp)
    lw      v1, 0x18 (sp)
    lw      ra, 0x1C (sp)
    jr      ra
    addiu   sp, sp, 0x20

; Set actors dropFlag to indicate that it was dropped from something.
item00_init_hook:
    andi    T9, V0, 0x00FF   ; replaced code
    jr      ra
    sh      T9, 0x001c(S0)   ; replaced code

; hooks Item_DropCollectible to store flag data in the variables passed to the EnItem00 spawn.
; Put the flag data into the y rotation paramter of the EnItem00 because its unused.
drop_collectible_hook:
    li      t0, drop_collectible_override_flag	
    lh      t1, 0x00(t0) ; get the current override flag
    sh      r0, 0x00(t0) ; clear the override_flag
    jr      ra
    sw      t1, 0x1C(sp) ; put the flag in the y rotation parameter which is at 0x1C(sp)

; Hook Item_DropCollectible to not set the room to -1 if we are going to be overriding the collectible.
; This will cause overridden collectibles to despawn when switching rooms. 
drop_collectible_room_hook:
    addiu   sp, sp, -0x20
    sw      a0, 0x10(sp)
    sw      ra, 0x14(sp)
    jal     Item_DropCollectible_Room_Hack
    or      a0, r0, s2

    lw      a0, 0x10(sp)
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x20

EnItem00_DropCollectibleFallAction_Hack:
    lh      t6, 0x014A(s0)
    bltz    t6, @@return
    addiu   t6, t6, 0x0001
    sh      t6, 0x014A(s0)
@@return:
    jr      ra
    nop

drop_collectible2_hook:
    li      t0, drop_collectible_override_flag	
    lh      t1, 0x00(t0) ; get the current override flag
    sh      r0, 0x00(t0) ; clear the override_flag
    jr      ra
    sw      t1, 0x1C(sp) ; put the flag in the y rotation parameter which is at 0x1C(sp)

item_give_hook:
    addiu sp, sp, -0x80
    sw      ra, 0x10(sp)
    sw      v0, 0x14(sp)
    sw      v1, 0x18(sp)
    sw      a0, 0x1C(sp)
    sw      a1, 0x20(sp)
    sw      a2, 0x24(sp)
    sw      a3, 0x28(sp)
    sw      s0, 0x2c(sp)
    sw      s1, 0x30(sp)
    sw      at, 0x34(sp)
    or      A0, v1, R0
    or      A1, S2, R0 ; pass player pointer to function
    jal     item_give_collectible ; if it was overridden, result will be stored in v0 as a 1. otherwise 0
    nop
    bgtz    v0, exit_func ; if we overrode, return to our new function, otherwise return to the original
    nop
return_to_func:
    lw      ra, 0x10(sp)
    lw      v0, 0x14(sp)
    lw      v1, 0x18(sp)
    lw      a0, 0x1C(sp)
    lw      a1, 0x20(sp)
    lw      a2, 0x24(sp)
    lw      a3, 0x28(sp)
    lw      s0, 0x2c(sp)
    lw      s1, 0x30(sp)
    lw      at, 0x34(sp)
    lw      t0, 0x003C(sp) ; this is what they do after the branch in the OG function
    j       0x80012E28 ; jump back where the OG function would have
    addiu   sp, sp, 0x80
exit_func:
    addiu   v1, r0, 0x03
    lw      ra, 0x10(sp)
    lw      a0, 0x1C(sp)
    lw      a1, 0x20(sp)
    lw      a2, 0x24(sp)
    lw      a3, 0x28(sp)
    lw      s0, 0x2c(sp)
    lw      s1, 0x30(sp)
    lw      at, 0x34(sp)
    beq     v0, v1, return_to_func_near_end ; check if our function returned 3. This means that it didnt play the fanfare. Jump back into function near the end so it sets up the proper animation
    nop
    lw      v0, 0x14(sp)
    lw      v1, 0x18(sp)
    j       0x80012FA4
    addiu   sp, sp, 0x80
return_to_func_near_end:
    lw      v0, 0x14(sp)
    lw      v1, 0x18(sp)
    j       0x80012F58
    addiu   sp, sp, 0x80

rupee_draw_hook:
; push things on the stack
    addiu   sp, sp, -0x80
    sw      ra, 0x10(sp)
    sw      v0, 0x14(sp)
    sw      v1, 0x18(sp)
    sw      a0, 0x1C(sp)
    sw      a1, 0x20(sp)
    sw      a2, 0x24(sp)
    sw      a3, 0x28(sp)
    sw      s0, 0x2c(sp)
    sw      s1, 0x30(sp)
    sw      at, 0x34(sp)

    jal     collectible_draw
    nop
; pop things off the stack
; put our return value somewhere
    bgtz    v0, @return
    nop
@rupee_draw_orig:
    lw      ra, 0x10(sp)
    lw      v0, 0x14(sp)
    lw      v1, 0x18(sp)
    lw      a0, 0x1C(sp)
    lw      a1, 0x20(sp)
    lw      a2, 0x24(sp)
    lw      a3, 0x28(sp)
    lw      s0, 0x2c(sp)
    lw      s1, 0x30(sp)
    lw      at, 0x34(sp)
    jal     0x80013150
    nop
@return:
    lw      ra, 0x10(sp)
    lw      v0, 0x14(sp)
    lw      v1, 0x18(sp)
    lw      a0, 0x1C(sp)
    lw      a1, 0x20(sp)
    lw      a2, 0x24(sp)
    lw      a3, 0x28(sp)
    lw      s0, 0x2c(sp)
    lw      s1, 0x30(sp)
    lw      at, 0x34(sp)
    jr      ra
    addiu   sp, sp, 0x80

recovery_heart_draw_hook:
; push things on the stack
    addiu   sp, sp, -0x80
    sw      ra, 0x10(sp)
    sw      v0, 0x14(sp)
    sw      v1, 0x18(sp)
    sw      a0, 0x1C(sp)
    sw      a1, 0x20(sp)
    sw      a2, 0x24(sp)
    sw      a3, 0x28(sp)
    sw      s0, 0x2c(sp)
    sw      s1, 0x30(sp)
    sw      at, 0x34(sp)

    jal     collectible_draw
    nop
; pop things off the stack
; put our return value somewhere
    beqz    v0, @return_to_func
    nop
@exit_func:
    lw      ra, 0x10(sp)
    lw      v0, 0x14(sp)
    lw      v1, 0x18(sp)
    lw      a0, 0x1C(sp)
    lw      a1, 0x20(sp)
    lw      a2, 0x24(sp)
    lw      a3, 0x28(sp)
    lw      s0, 0x2c(sp)
    lw      s1, 0x30(sp)
    lw      at, 0x34(sp)
    addiu   sp, sp, 0x80
    j       end_of_recovery_draw
    nop

@return_to_func:
    lw      ra, 0x10(sp)
    lw      v0, 0x14(sp)
    lw      v1, 0x18(sp)
    lw      a0, 0x1C(sp)
    lw      a1, 0x20(sp)
    lw      a2, 0x24(sp)
    lw      a3, 0x28(sp)
    lw      s0, 0x2c(sp)
    lw      s1, 0x30(sp)
    lw      at, 0x34(sp)
    addiu   sp, sp, 0x80
    LH      V0, 0x014a(A2)
    jr      ra
    addiu   at, r0, 0xFFFF
