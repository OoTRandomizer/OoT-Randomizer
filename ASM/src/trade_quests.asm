ADULT_ANJU_ITEM_DIALOG:
    .word 0x00000000

;==================================================================================================

check_fado_spawn_flags:
    addiu   sp, sp, -0x18
    sw      ra, 0x14(sp)

    ; Only change behavior for Fado actor
    ; Vanilla EnKo_CanSpawn behavior checks if
    ; the scene is Lost Woods and does not
    ; check the EnKo type. No reason not to be
    ; more specific since we have the option.
    lh      t0, 0x1C(s0)    ; s0 = EnKo* this pointer, 0x1C = Actor.params
    andi    t1, t0, 0xFF    ; filter actor params to those used for ENKO_TYPE macro
    li      $at, 0xC        ; 0xC = ENKO_TYPE_CHILD_FADO
    bne     t1, $at, @@return_fado
    nop
    la      t0, GLOBAL_CONTEXT
    lh      t1, 0xA4(t0)    ; play->sceneId
    li      $at, 0x5B       ; 0x5B = Lost Woods scene ID
    bne     t1, $at, @@return_fado
    nop

    ; Spawns if Odd Potion owned but not turned in
    jal     SaveFile_TradeItemIsOwned
    ori     a0, $zero, 0x31
    beqz    v0, @@kill_fado
    nop

    jal     SaveFile_TradeItemIsTraded
    ori     a0, $zero, 0x31
    bnez    v0, @@kill_fado
    nop
    b       @@return_fado
    nop

@@kill_fado:      ; you monster D:
    ; Actor_Kill
    jal     0x80020EB4
    or      a0, s0, $zero
@@return_fado:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18

;==================================================================================================

check_grog_spawn_flags:
    addiu   sp, sp, -0x18
    sw      ra, 0x14(sp)

    ; displaced code
    lhu     t3, -0x4B3A(t3)

    ; Spawns if Cojiro owned but not turned in
    jal     SaveFile_TradeItemIsOwned
    ori     a0, $zero, 0x2F
    beqz    v0, @@return_grog
    ori     t4, $zero, 0x0001          ; don't spawn

    jal     SaveFile_TradeItemIsTraded
    ori     a0, $zero, 0x2F
    bnez    v0, @@return_grog
    ori     t4, $zero, 0x0001          ; don't spawn
    or      t4, $zero, $zero           ; spawn

@@return_grog:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18

;==================================================================================================

check_skull_kid_spawn_flags:
    addiu   sp, sp, -0x20
    sw      v0, 0x08(sp)
    sw      s0, 0x0C(sp)
    sw      v1, 0x10(sp)
    sw      a0, 0x14(sp)
    sw      a1, 0x18(sp)
    sw      ra, 0x1C(sp)

    jal     ShouldSkullKidSpawn
    nop
    or      t9, v0, $zero

    lw      v0, 0x08(sp)
    lw      s0, 0x0C(sp)
    lw      v1, 0x10(sp)
    lw      a0, 0x14(sp)
    lw      a1, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20

;==================================================================================================

check_if_biggoron_should_cry_eye_hook:
    addiu   sp, sp, -0x18
    sw      ra, 0x14(sp)
    lbu     v0, CFG_ADULT_TRADE_SHUFFLE
    beqz    v0, @@vanilla_eye_hook
    nop
    jal     check_if_biggoron_should_cry
    nop
    b       @@return_eye_hook
    nop
@@vanilla_eye_hook:
    ; displaced code
    lbu     v0, 0x0074(t4)
@@return_eye_hook:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18


check_if_biggoron_should_cry_anim_hook:
    addiu   sp, sp, -0x18
    sw      ra, 0x14(sp)
    lbu     v0, CFG_ADULT_TRADE_SHUFFLE
    beqz    v0, @@vanilla_anim_hook
    nop
    jal     check_if_biggoron_should_cry
    nop
    b       @@return_anim_hook
    nop
@@vanilla_anim_hook:
    ; displaced code
    lui     v0, 0x8012
    addu    v0, v0, t8
    lbu     v0, -0x59BC(v0)
@@return_anim_hook:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18


check_if_biggoron_should_cry_sfx_hook:
    addiu   sp, sp, -0x18
    sw      a3, 0x10(sp)
    sw      ra, 0x14(sp)
    lbu     v0, CFG_ADULT_TRADE_SHUFFLE
    beqz    v0, @@vanilla_sfx_hook
    nop
    jal     check_if_biggoron_should_cry
    nop
    b       @@return_sfx_hook
    nop
@@vanilla_sfx_hook:
    ; displaced code
    lui     v0, 0x8012
    addu    v0, v0, t6
    lbu     v0, -0x59BC(v0)
@@return_sfx_hook:
    lw      a3, 0x10(sp)
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18


; Why let smoke irritate your eyes when you're big enough to eat the volcano?
check_if_biggoron_should_cry:
    addiu   sp, sp, -0x20
    sw      s0, 0x0C(sp)
    sw      v1, 0x10(sp)
    sw      a0, 0x14(sp)
    sw      a1, 0x18(sp)
    sw      ra, 0x1C(sp)

    ; Don't change behavior if trade shuffle is off
    lbu     at, CFG_ADULT_TRADE_SHUFFLE
    beqz    at, @@return_crybaby
    nop

    jal     SetBiggoronAnimationState
    nop

@@return_crybaby:
    lw      s0, 0x0C(sp)
    lw      v1, 0x10(sp)
    lw      a0, 0x14(sp)
    lw      a1, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20

;==================================================================================================

check_claim_check_traded:
    addiu   sp, sp, -0x20
    sw      v1, 0x10(sp)
    sw      a0, 0x14(sp)
    sw      a1, 0x18(sp)
    sw      ra, 0x1C(sp)

    jal     IsClaimCheckTraded
    nop
    ; override BGS flag with result
    ; Safe for both calls to this hook.
    ; First uses t8
    ; Second uses v0 and hasn't set/used t8 yet
    ; t8 is repurposed in the second hook to check
    ; both claim check in inventory and traded
    or      t8, v0, $zero

    ; The first hook doesn't normally check for claim
    ; check, but it's impossible to get there without
    ; presenting the claim check. However, the second hook
    ; needs to check for claim check to allow other trade
    ; items to be turned in after the claim check traded
    ; flag is set.
    ; Code is copied from func_80B58C8C / EnGo2_BiggoronSetTextId
    lui     t3, 0x8012
    addiu   t3, t3, 0xA5D0
    lui     t2, 0x8010
    lbu     t2, -0x709F(t2)
    addiu   $at, $zero, 0x0037
    addu    t3, t3, t2
    lbu     t4, 0x0074(t3)
    beq     t4, $at, @@return_claim_check
    nop
    or      t8, $zero, $zero ; adult trade item is not claim check

@@return_claim_check:
    lw      v1, 0x10(sp)
    lw      a0, 0x14(sp)
    lw      a1, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20

;==================================================================================================

check_trade_item_traded:
    addiu   sp, sp, -0x20
    sw      t3, 0x10(sp)
    sw      s0, 0x14(sp)
    sw      v0, 0x18(sp)
    sw      ra, 0x1C(sp)

    ; displaced code
    lw      v1, 0x0684(s0)

    ; Default behavior if Adult and Child
    ; Trade Quest Shuffles Off
    lbu     t3, CFG_ADULT_TRADE_SHUFFLE
    bnez    t3, @@check_trade_flags
    lbu     t3, CFG_CHILD_TRADE_SHUFFLE
    beqz    t3, @@return_traded
    nop

@@check_trade_flags:
    ; v1 = player->targetActor
    lb      a0, 0x0144(s0)
    jal     IsTradeItemTraded
    or      a1, v1, $zero
    ; Update targetActor if modified
    or      v1, v0, $zero
    bnez    v1, @@return_traded
    nop
    lw      s0, 0x14(sp)
    sw      $zero, 0x0684(s0)

@@return_traded:
    lw      t3, 0x10(sp)
    lw      s0, 0x14(sp)
    lw      v0, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20

;==================================================================================================

update_shiftable_trade_item_egg_hook:
    addiu   sp, sp, -0x18
    sw      ra, 0x14(sp)

    jal     Inventory_ReplaceItem_Override
    nop

    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18

;==================================================================================================

update_shiftable_trade_item_save_hook:
    addiu   sp, sp, -0x40
    sw      ra, 0x10(sp)
    sw      a0, 0x14(sp)
    sw      a1, 0x18(sp)
    sw      a2, 0x1C(sp)
    sw      a3, 0x20(sp)
    sw      t0, 0x24(sp)
    sw      t1, 0x28(sp)
    sw      t2, 0x2C(sp)
    sw      t3, 0x30(sp)
    sw      t9, 0x34(sp)
    sw      s0, 0x38(sp)
    sw      v1, 0x3C(sp)

    ; a0/a1 conveniently already set to old/new item
    jal     SaveFile_UpdateShiftableItem
    nop

    lw      ra, 0x10(sp)
    lw      a0, 0x14(sp)
    lw      a1, 0x18(sp)
    lw      a2, 0x1C(sp)
    lw      a3, 0x20(sp)
    lw      t0, 0x24(sp)
    lw      t1, 0x28(sp)
    lw      t2, 0x2C(sp)
    lw      t3, 0x30(sp)
    lw      t9, 0x34(sp)
    lw      s0, 0x38(sp)
    lw      v1, 0x3C(sp)

    ; Displaced code
    lbu     t4, 0x0000(t9)
    addu    t5, s0, t4

    jr      ra
    addiu   sp, sp, 0x40

;==================================================================================================

check_if_mask_sells_out:

    ; displaced code
    lui     t0, 0x8012
    addiu   t0, t0, 0xA5D0
    addu    v0, t0, t4
    lbu     a1, 0x0074(v0)
    lbu     t8, 0x0037($sp)

    ; Only alter behavior if given trade item is SOLD OUT
    ori     at, $zero, 0x002C
    bne     t8, at, @@return_sold_out
    or      v1, $zero, $zero

    ; Skip giving item if partial/full mask shuffle enabled
    lbu     v1, CFG_CHILD_TRADE_SHUFFLE

@@return_sold_out:
    jr      ra
    nop

;==================================================================================================

check_cucco_lady_talk_exch_hook:
    addiu   sp, sp, -0x18
    sw      at, 0x0C(sp)
    sw      v0, 0x10(sp)
    sw      ra, 0x14(sp)

    ; displaced code
    sh      t4, 0x0252(s0)

    ori     v0, $zero, 0x0001
    sw      v0, ADULT_ANJU_ITEM_DIALOG
    lw      at, 0x0C(sp)
    lw      v0, 0x10(sp)
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18


check_cucco_lady_talk_none_hook:
    addiu   sp, sp, -0x18
    sw      at, 0x0C(sp)
    sw      v0, 0x10(sp)
    sw      ra, 0x14(sp)

    ; displaced code
    lh      t1, 0x026A(s0)

    ori     v0, $zero, 0x0000
    sw      v0, ADULT_ANJU_ITEM_DIALOG
    lw      at, 0x0C(sp)
    lw      v0, 0x10(sp)
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18


check_cucco_lady_exchange_id_hook:
    addiu   sp, sp, -0x18
    sw      at, 0x0C(sp)
    sw      v0, 0x10(sp)
    sw      ra, 0x14(sp)

    lw      t9, ADULT_ANJU_ITEM_DIALOG

    lw      at, 0x0C(sp)
    lw      v0, 0x10(sp)
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18


check_cucco_lady_flag_hook:
    addiu   sp, sp, -0x18
    sw      at, 0x0C(sp)
    sw      v0, 0x10(sp)
    sw      ra, 0x14(sp)

    ; displaced code
    lhu     v1, 0x0EF4(v0)

    lw      t7, ADULT_ANJU_ITEM_DIALOG

    lw      at, 0x0C(sp)
    lw      v0, 0x10(sp)
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x18

;==================================================================================================

set_keaton_mask_traded_flag:
    addiu   sp, sp, -0x20
    sw      v0, 0x10(sp)
    sw      v1, 0x14(sp)
    sw      a0, 0x18(sp)
    sw      ra, 0x1C(sp)

    jal     SaveFile_SetTradeItemAsTraded
    ori     a0, $zero, 0x0024

    ; displaced code
    lbu     t1, 0x02FA(s0)

    lw      v0, 0x10(sp)
    lw      v1, 0x14(sp)
    lw      a0, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20


set_skull_mask_traded_flag:
    addiu   sp, sp, -0x20
    sw      v0, 0x10(sp)
    sw      v1, 0x14(sp)
    sw      a0, 0x18(sp)
    sw      ra, 0x1C(sp)

    jal     SaveFile_SetTradeItemAsTraded
    ori     a0, $zero, 0x0025

    lw      v0, 0x10(sp)
    lw      v1, 0x14(sp)
    lw      a0, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20


set_spooky_mask_traded_flag:
    addiu   sp, sp, -0x20
    sw      v0, 0x10(sp)
    sw      v1, 0x14(sp)
    sw      a0, 0x18(sp)
    sw      ra, 0x1C(sp)

    jal     SaveFile_SetTradeItemAsTraded
    ori     a0, $zero, 0x0026

    ; displaced code
    addiu   a0, $zero, 0x001E

    lw      v0, 0x10(sp)
    lw      v1, 0x14(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20


set_bunny_hood_traded_flag:
    addiu   sp, sp, -0x20
    sw      v0, 0x10(sp)
    sw      v1, 0x14(sp)
    sw      a0, 0x18(sp)
    sw      ra, 0x1C(sp)

    jal     SaveFile_SetTradeItemAsTraded
    ori     a0, $zero, 0x0027

    ; displaced rando code, always fill wallet on turn in
    li      a0, 999

    lw      v0, 0x10(sp)
    lw      v1, 0x14(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20

;==================================================================================================

handle_child_zelda_savewarp:
    lbu     v0, CFG_CHILD_TRADE_SHUFFLE
    bnez    v0, @@return
    nop

@@revert_child_trade_item:
    addu    t4, s0, t9
    sb      a0, 0x0074(t4)
    addiu   v1, $zero, 0x0001
    addiu   a1, $zero, 0x0023
    addu    v0, s0, v1
@@c_button_loop:
    lbu     t5, 0x0068(v0)
    addiu   v1, v1, 0x0001
    andi    v1, v1, 0xFFFF
    bne     a1, t5, @@skip_c_button
    slti    at, v1, 0x0004
    sb      a0, 0x0068(v0)
@@skip_c_button:
    bnel    at, $zero, @@c_button_loop
    addu    v0, s0, v1

@@return:
    jr      ra
    nop


check_zelda_cutscene_watched:
    addiu   sp, sp, -0x20
    sw      a0, 0x18(sp)
    sw      ra, 0x1C(sp)

    jal     SaveFile_TradeItemIsTraded
    ori     a0, $zero, 0x0021           ; ITEM_WEIRD_EGG
    bnez    v0, @@skip_letter
    nop

@@give_letter:
    jal     SaveFile_SetTradeItemAsTraded
    ori     a0, $zero, 0x0021           ; ITEM_WEIRD_EGG

    ; displaced code
    or      a1, s1, $zero
    add.s   $f14, $f16, $f14
    mfc1    a3, $f18
    addiu   a2, $zero, 0x000B
    ;lh      t4, 0x07A0(s1)
    ;addiu   a1, $zero, 0x0001
    ;sll     t5, t4,  2
    ;addu    t6, s1, t5

    b       @@return
    or      v0, $zero, $zero

@@skip_letter:
    ; skipped code
    lui     $at, 0x0001
    addu    $at, $at, s1
    addiu   t8, $zero, 0x0004
    sb      t8, 0x04BF($at)
    lui     $at, 0x0001
    addu    $at, $at, s1
    addiu   t0, $zero, 0x0036
    sb      t0, 0x03DC($at)

    ; free Link from cutscene
    lui    t0, 0x801E
    sb     r0, 0x887C(t0) ;store 0x36 to msg_state_1
    sb     r0, 0x895F(t0) ;store 0x02 to msg_state_3
    lui    t0, 0x801F
    sb     r0, 0x8D38(t0) ;store 0x00 to msg_state_2

@@return:
    lw      a0, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20
