.headersize(0x80B1ED70 - 0xE9A4A0)

; EnTorch_Init()
; Change the source of the grotto content data from the save context respawn
; data to the new grotto entrance table. Fully re-implemented the function
; based on decomp.
.org 0x80B1ED70
    j       EnTorch_Init
    nop

.headersize(0)
