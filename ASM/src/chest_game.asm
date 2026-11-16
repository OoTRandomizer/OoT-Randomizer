SHUFFLE_CHEST_GAME:
.byte 0x00
TCG_REQUIRES_LENS:
.byte 0x00
.align 4

chestgame_buy_item_hook:
    lb      t0, SHUFFLE_CHEST_GAME
    beqz    t0, @@return        ; skip if the chest game isn't randomized

    la      t1, GLOBAL_CONTEXT
    lw      t0, 0x1D44(t1)      ; load scene collectible flags (Treasure Box House)
    ori     t0, t0, 0x2         ; set flag 1 (custom TCG salesman flag)
    sw      t0, 0x1D44(t1)

@@return:
    jr      ra
    sw      $zero, 0x0118(s0)   ; displaced code

chestgame_initial_message:
    lb      t0, SHUFFLE_CHEST_GAME
    beqz    t0, @@return        ; use the default message if the salesman isn't randomized

    la      t1, GLOBAL_CONTEXT
    lw      t0, 0x1D44(t1)      ; load scene collectible flags (Treasure Box Shop)
    andi    t0, t0, 0x2         ; check flag 1 (normally unused flag)
    beqz    t0, @@return        ; if the flag is not set, continue with the default message
    nop
    addiu   t8, $zero, 0x0001   ; set unk_214 = 1
    sh      t8, 0x0204(s0)      ; store value which is checked if key has already been purchased

@@return:
    jr      ra
    sw      t2, 0x0010($sp)     ; displaced code

chestgame_no_reset_flag:
    lhu     t0, 0x1402(v0)      ; removed code due to nop after jal
    lb      t1, SHUFFLE_CHEST_GAME
    bnez    t1, @@return        ; skip if chest game isn't randomized
    nop
    sw      $zero, 0x1D38(t8)   ; displaced code

@@return:
    jr      ra
    nop

chestgame_no_reset_keys:
    addiu   t2, s0, 0x0184      ; removed code due to nop after jal
    lb      t0, SHUFFLE_CHEST_GAME
    bnez    t0, @@return        ; skip if chest game isn't randomized
    nop
    sb      t9, 0x00BC(t1)      ; displaced code

@@return:
    jr      ra
    nop

chestgame_remove_chest_rng:
    mtc1    $at, $f8            ; Line replaced with jal
    lb      t1, SHUFFLE_CHEST_GAME
    beqz    t1, @@chestgame_run_chest_rng        ; skip if chest game isn't randomized and run rng
    nop
    mtc1    $zero, $f8          ; modify comparison registers
    ori     t2, $zero, 0x0001
    mtc1    t2, $f0

@@chestgame_run_chest_rng:
    jr      ra
    nop

; Show a key in the unopened chest regardless of chest
; contents if the tcg_requires_lens setting is enabled
chestgame_force_game_loss_left:
    ; displaced code
    lwc1    $f0, 0x0024($v1)
    lwc1    $f2, 0x0028($v1)
    ; check setting
    lb      $t7, TCG_REQUIRES_LENS
    beqz    $t7, @@return
    nop
    ; safety check to prevent simulated loss if keys are shuffled
    lb      $t7, SHUFFLE_CHEST_GAME
    bnez    $t7, @@return
    nop
    ; check if player has lens of truth
    lui     $t1, hi(SAVE_CONTEXT + 0x81)
    lb      $t2, lo(SAVE_CONTEXT + 0x81)($t1) ; lens item slot
    li      $t3, 15 ; lens item ID
    bne     $t2, $t3, @@force_loss
    nop
    ; check if player has magic
    lb      $t2, SAVE_CONTEXT + 0x3A ; magic_acquired
    beqz    $t2, @@force_loss
    nop
@@return:
    jr      $ra
    nop

@@force_loss:
    ; simulate lost game
    addiu   $t0, $zero, 0x0071
    j       chestgame_warn_player_of_rigged_game
    nop

chestgame_force_game_loss_right:
    ; displaced code
    lwc1    $f0, 0x0024($v0)
    lwc1    $f2, 0x0028($v0)
    ; check setting
    lb      $t7, TCG_REQUIRES_LENS
    beqz    $t7, @@return
    nop
    ; safety check to prevent simulated loss if keys are shuffled
    lb      $t7, SHUFFLE_CHEST_GAME
    bnez    $t7, @@return
    nop
    ; check if player has lens of truth
    lui     $t1, hi(SAVE_CONTEXT + 0x81)
    lb      $t2, lo(SAVE_CONTEXT + 0x81)($t1) ; lens item slot
    li      $t3, 15 ; lens item ID
    bne     $t2, $t3, @@force_loss
    nop
    ; check if player has magic
    lb      $t2, SAVE_CONTEXT + 0x3A ; magic_acquired
    beqz    $t2, @@force_loss
    nop
@@return:
    jr      $ra
    nop

@@force_loss:
    ; simulate lost game
    addiu   $v1, $zero, 0x0071
    j       chestgame_warn_player_of_rigged_game
    nop

; Add a helper message if the tcg_requires_lens
; setting is enabled and the player still attempts
; the game.
chestgame_warn_player_of_rigged_game:
    addiu   $sp, $sp, -0x20
    sw      $ra, 0x14($sp)
    sw      $v0, 0x18($sp)
    sw      $v1, 0x1C($sp)

    jal     treasure_chest_game_message
    nop

    lw      $ra, 0x14($sp)
    lw      $v0, 0x18($sp)
    lw      $v1, 0x1C($sp)
    jr      $ra
    addiu   $sp, $sp, 0x20
