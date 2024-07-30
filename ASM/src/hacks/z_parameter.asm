.headersize(0x8006D8E0 - 0x00AE3840)

;=============================================================
; Move the small key counter horizontally if we have boss key.
;=============================================================

.org 0x8007594C
    ; Replaces addiu   t7, $zero, 0x001A
    ;          addiu   t8, $zero, 0x00BE
    jal     move_key_icon
    addiu   t7, $zero, 0x001A

.org 0x80075A38
    ; Replaces addiu   s2, $zero, 0x002A
    ;          addiu   t8, $zero, 0x00BE
    jal     move_key_counter
    addiu   s2, $zero, 0x002A
