; Nintendo Logo title screen

.headersize(0x80800000 - 0x00B9DA40)

.org 0x80800700
; Replaces:
;   lbu     t3, 0x01E1(s0)
;   lui     v0, 0x8012
    jal     skip_nintendo_logo
    lbu     t3, 0x01E1(s0)
