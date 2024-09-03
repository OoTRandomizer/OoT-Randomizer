.headersize(0x808CBDD0 - 0x00C69630)
;==================================================================================================
; Hooks new Audio_PlaySariaBgm function for lowhp music;
;==================================================================================================

.org 0x808CC5E4
    ; replaces
    ; jal     0x800C5FE0
    jal Audio_PlaySariaBgm

.org 0x808CC604
    ; replaces
    ; jal     0x800C5FE0
    jal Audio_PlaySariaBgm
