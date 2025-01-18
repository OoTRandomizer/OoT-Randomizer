SHUFFLE_CARPET_SALESMAN:
.byte 0x00
.align 4

; Override the inital message based on whether the player should be able to buy or not
carpet_inital_message:
    lb      t0, SHUFFLE_CARPET_SALESMAN
    beqz    t0, @@return        ; use the default message if the salesman isn't randomized

    la      t1, GLOBAL_CONTEXT
    lw      t0, 0x1D44(t1)      ; load scene collectible flags (Haunted Wasteland)
    andi    t0, t0, 0x2         ; check flag 1 (normally unused flag)
    beqz    t0, @@return        ; if the flag is not set, continue with the default message
    nop
    li      a2, 0x9100          ; else, display a sold out message

@@return:
    jr      ra
    sw      a2, 0x0020(sp)      ; displaced code

; Set the salesman scene collectible flag on purchase if the salesman is randomized
carpet_buy_item_hook:
    lb      t0, SHUFFLE_CARPET_SALESMAN
    beqz    t0, @@return        ; skip if the salesman isn't randomized

    la      t1, GLOBAL_CONTEXT
    lw      t0, 0x1D44(t1)      ; load scene collectible flags (Haunted Wasteland)
    ori     t0, t0, 0x2         ; set flag 1 (custom carpet salesman flag)
    sw      t0, 0x1D44(t1)

@@return:
    jr      ra
    ori     a3, a3, 0x4000      ; displaced code
