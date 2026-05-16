.headersize (0x809bba50 - 0x00d4bbd0)

; Jabu-Jabu dungeon objects overlay

;==================================================================================================
; Make player drop Ruto when opening a door to the Big Octo room if "visited Big Octo" flag set
;==================================================================================================
; Replaces: lui     a0,0x601
;           addiu   a0,a0,-29472
.org 0x809bbb94         ; in BgBdanObjects_Init
    jal     JabuObjects_DropRutoBigOcto
    lui     a0,0x601        ; displaced
