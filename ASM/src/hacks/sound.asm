.headersize(0x800B0280 - 0x00B261E0)

.org 0x800C2BB8
; Replaces
;    sb      $zero, 0x0000(v1)
;    lui     $at, 0x8010
    jal     scarecrow_vibrato_fix
    nop
