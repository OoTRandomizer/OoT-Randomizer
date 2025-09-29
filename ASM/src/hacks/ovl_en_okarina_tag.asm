; Hacks in en_okarina_tag (ocarina spot) actor for door of time condition

.headersize(0x80A86C00 - 0xE09540)

.org 0x80a87260
; Replaces:
;   lui     t4,0x80a8
;   or      t3,t2,at
;   sw      t3,0x670(t0)
;   addiu   t4,t4,0x72d0
    or      t3, t2, at
    sw      t3, 0x670(t0)
    li      t4, EnOkarinaTag_ActionHook

; Patch relocs
.org 0x80a8806c
    nop
    nop
