; Hacks in en_ssh (Cursed Skulltula Family)
.headersize(0x80B25590 - 0x00EA0CC0)

;Replace Text ID's for 100 Skulltula Cursed Man, to misc hint if the setting is on.

.org 0x80B26F90
    addiu   t0, $zero, 0x9009    ;Replace Text ID 0x0026

.org 0x80B26F8C
    addiu   t9, $zero, 0x9009    ;Replace Text ID 0x0027

.org 0x80B26F34
    addiu   t2, $zero, 0x9009    ;Replace Text ID 0x0029

.org 0x80B26F64
    addiu   t5, $zero, 0x9009    ;Replace Text ID 0x0024

.org 0x80B26F68
    addiu   t6, $zero, 0x9009    ;Replace Text ID 0x0025

; Give each remaining cursed skulltula house resident a different text ID, for skulltula reward hints

.org 0x80B26F34
    addiu   t1, t1, 0x9003
