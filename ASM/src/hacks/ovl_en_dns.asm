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
; Replaces  lh      t6,182(s0)
;           move    a0,s0
.org 0x80a75504                   ; in EnDns_Idle
    jal     EnDns_CheckYDist
    lh      t6,182(s0)
