.headersize(0x800110A0 - 0xA87000)

; Hook EnItem00_Init
.org 0x80011b4c
; Replaces:
;   addiu   sp, sp, -0x40
;   sw      s0, 0x18(sp)
    j       EnItem00_Init_Hook
    nop
EnItem00_Init_Continue:
