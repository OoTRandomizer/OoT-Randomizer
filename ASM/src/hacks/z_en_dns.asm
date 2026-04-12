.headersize(0x80a74c60 - 0x00df75a0)

;================================================================================
; Adds Y distance check to talking with business Deku Scrub (prevents buying in
; Deku Tree from the water, but not being able to get the item)
;================================================================================
; Replaces  lh      t6,182(s0)
;           move    a0,s0
.org 0x80a75504                   ; in EnDns_Idle
    jal     EnDns_CheckYDist      ; endns_checkydist.s
    lh      t6,182(s0)
