; Hacks in en_dns (friendly Deku Scrub salesman)
.headersize(0x80A74C60 - 0x00DF75A0)

; Hack EnDns_SetupSale to take the payment before giving the item
.org 0x80a75834
; Replaces
;   jal     Message_CloseTextBox
;   lw      a0, 0x1c(sp)

    jal     EnDns_TakePayment
    nop

; Nop out where it normally takes the payment
.org 0x80a75958
    nop

.org 0x80a7590c
    nop

;================================================================================
; Adds Y distance check to talking with business Deku Scrub (prevents buying in
; MQ Deku Tree from the water, but not being able to get the item)
;================================================================================
; Replaces jal     Math_SmoothStepToS
;          li      a3,2000
;          lh      t6,182(s0)
;          move    a0,s0
.org 0x80a754fc                 ; in EnDns_Idle
    jal     EnDns_CheckYDist
    nop
    beqz    v0,0x80a75598       ; EnDns_Idle function return
    move    a0,s0               ; displaced
