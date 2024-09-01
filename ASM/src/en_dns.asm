; Deku Scrub Salesman take payment before giving item
; dns actor at 0x18(sp)
EnDns_TakePayment:
    addiu   sp, sp, -0x20
    sw      ra, 0x10(sp)

    ; Call the payment function. It's stored in the actor
    ; (**(code **)(*(int *)(param_1 + 0x2b0) + 0xc))(param_1);
    lw      a1, 0x38(sp) ; get actor pointer off stack. Add 0x20 because we pushed the stack
    or      a0, a1, r0 ; move it into a0 for when we call the function
    lw      a1, 0x2b0(a1) ; Get dnsItemEntry pointer from actor
    lw      a1, 0x0c(a1) ; Get payment function pointer from dnsItemEntry
    jalr    a1 ; Call payment function
    nop

; Replaced code:
    jal     Message_CloseTextBox
    lw      a0, 0x3c(sp) ; Add 0x20 because we pushed the stack

    lw      ra, 0x10(sp)
    jr      ra
    addiu   sp, sp, 0x20
