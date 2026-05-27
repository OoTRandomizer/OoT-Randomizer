; King Zora Hacks

.headersize(0x80AD5D60 - 0x00E55BA0)

;===================================================================================================
; Prevent the trade quest timer to start if you get the Zora Tunic item from King Zora with
; Eyeball Frog in inventory.
;===================================================================================================

; First, keep track that we're trading the eyeball frog
.org 0x80ad63dc
; Replaces:
;   sh      t7, 0x10e(s0)
;   sb      r0, 0x1f8(s0)
    jal     kz_store_is_trading
    sh      t7, 0x10e(s0) ; Replaced code

; Check the flag when starting the timer

; Replaces
;   li      at, 0x35
;   li      a0, 0xb4
.org 0x80ad6d20
    jal     kz_no_timer
    li      at, 0x35 ; Replaced code

; Reset the flag after setting the timer
.org 0x80ad6d58
; Replaces
;   sh      r0, 0x1d0(a1)
;   sw      t2, 0x180(a1)
    jal     kz_reset_trade_flag
    sh      r0, 0x1d0(a1) ; Replaced code

;================================================================================
; Prevent King Zora from stopping talking if moving out of angle when starting
;================================================================================
; Moved upstateTalkState call + yaw check function
; Replaces: move    a1,s0
;           addiu   a2,sp,42
;           jal     Actor_GetScreenPos
;           addiu   a3,sp,40
.org 0x80ad6188     ; in EnKz_UpdateTalking
    jal     EnKz_UpdateTalkingYawFix
    nop
    beqz    v0,0x80ad6254   ; don't continue function if talking
    nop

; Skip previous updateTalkState call
.org 0x80ad61cc     ; in EnKz_UpdateTalking
    b       0x80ad61f4
    nop

; Removing previous yaw check function, but
; need to retain some instructions for future calls
.org 0x80ad6284     ; in func_80A9CB18
    b       0x80ad6298
    nop
.skip 12
    lw      t0,7236(s1)     ; 0x80ad6298, s1 play
    sw      t0,44(sp)       ; player address
    lui     at,0x80ad       ; ok to keep
    move    a1,s0           ; actor
    addiu   a2,s0,464       ; talkstate
    lwc1    $f16,28936(at)  ; ok to keep
.skip 12                    ; passing on the stack
    b       0x80ad62f8      ; continue after what previously was yaw check
    lui     a3,0x43aa       ; 340.0f
