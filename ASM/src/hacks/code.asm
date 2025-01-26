.headersize(0x800110A0 - 0xA87000)

; New Actor_Kill function
; Jump from the start of the original function
.org 0x80020eb4
    j   Actor_Kill_New
    nop
