offer_jail_hook:
    lui     t6, hi(org(offer_jail_normal_white_guard))
    addiu   t6, t6, lo(org(offer_jail_normal_white_guard))

    ; Displaced code, conveniently what we need to edit for our hook
    sw      t6, 0x0010($sp)
    addiu   a2, $zero, 0x6013

    jr      $ra
    nop

offer_jail_normal_white_guard:
    addiu   $sp, $sp, 0xFFE0
    sw      s1, 0x0018($sp)
    sw      s0, 0x0014($sp)
    or      s0, a1, $zero
    or      s1, a0, $zero
    sw      $ra, 0x001C($sp)           ; guard stateFlags |= GE1_STATE_TALKING
    lhu     t6, 0x029C(s1)
    addiu   a0, s0, 0x20D8
    ori     t7, t6, 0x0001
    jal     0x800DD464                 ; Message_GetState
    sh      t7, 0x029C(s1)
    addiu   $at, $zero, 0x0004         ; TEXT_STATE_CHOICE == 4
    bnel    v0, $at, @@return
    lw      $ra, 0x001C($sp)
    jal     0x800D6110                 ; Message_ShouldAdvance
    or      a0, s0, $zero
    beql    v0, $zero, @@return
    lw      $ra, 0x001C($sp)
    jal     0x800D6218                 ; Message_CloseTextbox
    or      a0, s0, $zero
    lui     v0, 0x0001
    addu    v0, v0, s0
    lbu     v0, 0x04BD(v0)             ; Message Context->choiceIndex

    ; Load En_Ge1 (white-clothed guards) actor location in RAM
    lui     t8, hi(0x800E8530)
    addiu   t8, lo(0x800E8530)         ; actor overlay table
    lw      t8, 0x2710(t8)             ; actor overlay loaded ram address (0x138 * 0x20 + 0x10)

    ; Handle player response to text box
    addiu   $at, $zero, 0x0001
    beq     v0, $zero, @@first_response
    nop
    beq     v0, $at, @@second_response
    nop
    b       @@return
    lw      $ra, 0x001C($sp)
@@first_response:
    addiu   t9, t8, 0x071C             ; offset from actor overlay start to EnGe1_SetNormalText
    sw      t9, 0x02A4(s1)
    addiu   t9, t8, 0x03D0             ; offset from actor overlay start to EnGe1_SetAnimationIdle
    jalr    t9
    or      a0, s1, $zero
    b       @@end_switch
    nop
@@second_response:
    addiu   t9, t8, 0x074C             ; offset from actor overlay start to EnGe1_WatchForAndSensePlayer
    sw      t9, 0x02A4(s1)
    addiu   t9, t8, 0x03D0             ; offset from actor overlay start to EnGe1_SetAnimationIdle
    jalr    t9
    or      a0, s1, $zero
@@end_switch:
    lw      $ra, 0x001C($sp)
@@return:
    lw      s0, 0x0014($sp)
    lw      s1, 0x0018($sp)
    jr      $ra
    addiu   $sp, $sp, 0x0020
