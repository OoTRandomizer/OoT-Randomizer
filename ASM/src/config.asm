;==================================================================================================
; Settings and tables which the front-end may write
;==================================================================================================

; Initial Save Data table:
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

BOMBCHUS_IN_LOGIC:
.word 0x00

RAINBOW_BRIDGE_CONDITION:
.word 0x00
; 0 = Open
; 1 = Medallions
; 2 = Dungeons
; 3 = Stones
; 4 = Vanilla
; 5 = Tokens

GOSSIP_HINT_CONDITION:
.word 0x00
; 0 = Mask of Truth
; 1 = Stone of Agony
; 2 = No Requirements

FREE_SCARECROW_ENABLED:
.word 0x00

RAINBOW_SWORD_ENABLED:
.byte 0x00

JABU_ELEVATOR_ENABLED:
.byte 0x00
OCARINAS_SHUFFLED:
.byte 0x00
FAST_CHESTS:
.byte 0x01
.align 4
