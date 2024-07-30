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
