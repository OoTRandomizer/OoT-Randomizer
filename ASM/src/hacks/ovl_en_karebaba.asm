; Hacks in en_karebaba (Whithered Deku Baba)

.headersize(0x809BA160 - 0xD4A2E0)

; Hack the call to EnKarebaba_SetupDeadItemDrop to drop an item.
.org 0x809bae34
; Replaces:
;   jal     EnKarebaba_SetupDeadItemDrop (reloc 0xCD4)
    jal     EnKarebaba_SetupDeadItemDropHack

; Relocs
.org 0x809bb954 ; (0xCD4)
    nop
