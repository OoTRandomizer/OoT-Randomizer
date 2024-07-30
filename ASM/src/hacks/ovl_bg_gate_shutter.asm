; Hacks in bg_gate_shutter (Kakariko Village Gate)

.headersize(0x80A50A70 - 0xDD34B0)

; Make the Kak gate open based on the setting. Removes the master sword check
; In BgGateShutter_Init where it checks the master sword EVENTINF flag
.org 0x80A50AF4
; Replaces
;   lhu     t8, 0xedc(v1)
;   andi    t9, t8, 0x20
    jal     bg_gate_shutter_open_hack
    nop


;==================================================================================================
; Speed Up Gate in Kakariko
;==================================================================================================
; gate opening x
; Replaces: lui     at, 0x4000 ;2.0f
.orga 0x80A50C2C
    lui     at, 0x40D0 ;6.5f

; gate opening z
; Replaces: lui     a2, 0x3F4C
;           sub.s   f8, f4, f6
;           lui     a3, 0x3E99
;           ori     a3, a3, 0x999A
;           ori     a2, a2, 0xCCCD
.orga 0x80A50C3C
    lui     a2, 0x4000
    sub.s   f8, f4, f6
    lui     a3, 0x4000
    nop
    nop

; gate closing x
; Replaces: lui     at, 0x4000 ;2.0f
.orga 0x80A50D04
    lui     at, 0x40D0 ;6.5f

; gate closing z
; Replaces: lui     a2, 0x3F4C
;           add.s   f8, f4, f6
;           lui     a3, 0x3E99
;           ori     a3, a3, 0x999A
;           ori     a2, a2, 0xCCCD
.orga 0x80A50D14
    lui     a2, 0x4000
    add.s   f8, f4, f6
    lui     a3, 0x4000
    nop
    nop
