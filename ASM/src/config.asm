;==================================================================================================
; Settings and tables which the front-end may write
;==================================================================================================

; 0x03481000: Item override table:
;
; This table changes the meaning of a given item ID within a given scene. It must be terminated with
; four 0x00 bytes (which will happen by default as long as you don't fill the allotted space).
;
; Row format (4 bytes):
; SSTTIINN
; SS = Scene
; TT = Override Type (0x00 = base item, 0x01 = chest, 0x02 = collectable)
; II = Override ID (base item or flag)
; NN = New item ID

.area 0x800, 0
ITEM_OVERRIDES:
.endarea

; 0x03481800: Initial Save Data table:
;
; This table describes what extra data should be written when a new save file is created. It must be terminated with
; four 0x00 bytes (which will happen by default as long as you don't fill the allotted space).
;
; Row format (4 bytes):
; AAAATTVV
; AAAA = Offset from the start of the save data
; TT = Type (0x00 = or value with current value, 0x01 = set the byte to the given value)
; VV = Value to write to the save

.area 0x400, 0
INITIAL_SAVE_DATA:
.endarea

PLAYER_ID:
.byte 0x00

; 0x03481C00: Special items

LIGHT_ARROW_ITEM:
.byte 0x5A
FAIRY_OCARINA_ITEM:
.byte 0x3B
FAIRY_ITEMS:
.byte 0x5D ; Zora's Domain
.byte 0x5C ; Hyrule Castle
.byte 0x5E ; Desert Colossus
.byte 0x51 ; Mountain Summit
.byte 0x52 ; Crater
.byte 0x53 ; Ganon's Castle
.align 4
