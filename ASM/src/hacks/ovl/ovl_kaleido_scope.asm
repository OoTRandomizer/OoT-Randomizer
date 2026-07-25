; KaleidoScope Overlay (Menu) hacks
; ovl_kaleido_scope:
;   VRAM Start - 0x808137C0
;   VROM Start - 0xBB11E0
;   Size - 0x1C990

; Hack calls to KaleidoScope_DrawWorldMap and KaleidoScope_DrawDungeonMap

.headersize(0x808137C0 - 0xBB11E0)

.org 0x80820850 ; offset 0xD090
;   Replaces
;   jal KaleidoScope_DrawWorldMap
    jal KaleidoScope_DrawWorldMap_CallHook

.org 0x80820b48 ; offset 0xD388
;   Replaces
;   jal KaleidoScope_DrawWorldMap
    jal KaleidoScope_DrawWorldMap_CallHook

.org 0x808207E4 ; offset 0xD024
;   Replaces
;   jal KaleidoScope_DrawDungeonMap
    jal KaleidoScope_DrawDungeonMap_CallHook

.org 0x80820AC4 ; offset 0xD304
;   Replaces
;   jal KaleidoScope_DrawDungeonMap
    jal KaleidoScope_DrawDungeonMap_CallHook

; Hack calls to PauseMapMark_Draw because for some reason it isn't part of DrawDungeonMap...
.org 0x80820840 ; offset 0xD080
    jal PauseMapMark_Draw_CallHook

.org 0x80820b38 ; offset 0xD378
    jal PauseMapMark_Draw_CallHook

; Relocs
; 0xD090
.org 0x8082f62c
    nop
; 0xD388
.org 0x8082f698
    nop
; 0xD024
.org 0x8082f624
    nop
; 0xD304
.org 0x8082f68c
    nop
; 0xD080
.org 0x8082f628
    nop
; 0xD378
.org 0x8082f694
    nop