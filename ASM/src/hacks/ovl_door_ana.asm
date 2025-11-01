.headersize(0x80959A10 - 0x00CF70A0)

; 0xCF737C
; Remove grotto respawn system function call to Play_SetupRespawnPoint()
.org 0x80959CEC
    nop

; Remove saving respawn data to save context
; 0xCF7390
.org 0x80959D00
    nop
; 0xCF73A0
.org 0x80959D10
    nop
; 0xCF73B0
.org 0x80959D20
    nop

; 0xCF73E0
; Remove setting the next entrance index
.org 0x80959D50
    nop

; Hook to set play->nextEntranceIndex using the extended entrance table
; Replaces instructions used to set up setting the next entrance index,
; which is no longer needed as the hook handles it.
.org 0x80959D38
    jal     set_grotto_entrance_hook
    nop

.headersize(0)
