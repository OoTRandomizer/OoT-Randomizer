CHAIN_HBA_REWARDS:
.byte 0x00
.align 4

; Runs when checking the end of the dialog after giving a horseback archery reward
; Should return: v0 = return value of 0x80022AD0 / v1 = routine function to run during the next actor update
handle_hba_rewards_chain:
    addiu   sp, sp, -0x18
    sw      ra, 0x14(sp)
    jal     0x80022AD0          ; displaced call
    nop
    lw      ra, 0x14(sp)
    addiu   sp, sp, 0x18

    lw      a0, 0x0018(sp)
    lw      t2, 0x138(a0)       ; pointer to actor overlay table entry
    lw      t2, 0x10(t2)        ; actor loaded ram address
    addiu   v1, t2, 0x1618      ; default routine to end the dialog (80A90718)

    lb      t0, CHAIN_HBA_REWARDS
    beqz    t0, @@return        ; use the default routine if rewards shouldn't be chained
    la      t1, SAVE_CONTEXT
    lhu     t0, 0x1406(t1)      ; current score
    slti    at, t0, 1500
    bnez    at, @@return        ; use the default routine if the score is < 1500
    lhu     t0, 0x29C(a0)
    andi    t0, t0, 0x0002
    bnez    t0, @@return        ; use the default routine if we just received the 2nd reward
    nop

    addiu   v1, t2, 0x14D0      ; routine to chain rewards and give the 2nd reward instantly (80A905D0)

@@return:
    jr      ra
    nop
