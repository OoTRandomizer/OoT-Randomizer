;==================================================================================================
; Global variable storage for new code
;==================================================================================================

; Stores the item and player to give to
PLAYER_OVERRIDE_DATA:
.word 0x00000000, 0x00000000

; Stores the ITEM_DATA row of the current extended item.
EXTENDED_ITEM_DATA:
.word 0x00000000, 0x00000000, 0x00000000, 0x00000000

PENDING_SPECIAL_ITEM:
.byte 0x00
.byte 0x00
.byte 0x00
PENDING_SPECIAL_ITEM_END:
.byte 0x00
.align 4

TIME_TRAVEL_SAVED_EQUIPS:
.word 0x00000000 ; B and C buttons
.word 0x00000000 ; C button indexes
.halfword 0x0000 ; Equipment
.halfword 0x0000 ; Owned equipment
.align 4