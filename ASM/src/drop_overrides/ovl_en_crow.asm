; Hack Guays to not respawn when enemy drop shuffle is enabled
;A0 contains the actor
; actionFunc is at 0x01B0(A0) if we care.
; 0x10(sp) contains the original return address that needs to be stored on the stack if we're continuing in the function.
; 0x14(sp) contains the return address in the function after our hack.
en_crow_respawn_hack:
    sw      ra, 0x14(sp) ; store other return address
    sw      a0, 0x18(sp)
    sw      a1, 0x1C(sp)
    sw      v0, 0x20(sp)

; Check if the setting is enabled.
    lb      a1, CFG_PREVENT_GUAY_RESPAWNS
    beqz    a1, @en_crow_return_to_func
    nop
    ; Setting is enabled so kill the guay.
@en_crow_kill:
    jal     0x80020EB4 ; Actor_Kill
    nop
    ; And just return from the function
    lw      ra, 0x10(sp)
    jr      ra
    addiu   sp, sp, 0x30

@en_crow_return_to_func:
; Continue on in the function. Need to set up RAs on the stack properly.
    lw      at, 0x10(sp) ; Get the original return address from the stack
    lw      ra, 0x14(sp) ; And get the return address after our hack. This is where we actually return
    lw      a0, 0x18(sp) ; Restore other registers
    lw      a1, 0x1C(sp)
    lw      v0, 0x20(sp)

    addiu   sp, sp, 0x30
    ; Replaced code
    addiu   sp, sp, -0x18
    sw      at, 0x14(sp) ; Put the original return address in the right place on the stack.
    or      a2, a0, r0
    lw      t6, 0x0000(v0)
    jr      ra
    nop
