.headersize (0x80b5c930 - 0x00ed8060)

; Zero slash status on damage/stun taken (PAL 1.0 fix)
; Replaces: lbu     v0,177(s0)
;           li      at,1
.org 0x80b5fdb8     ; in EnWf_UpdateDamage
    jal     EnWf_ZeroSlashStatus
    lbu     v0,177(s0)      ; displaced
