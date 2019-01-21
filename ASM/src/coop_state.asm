COOP_VERSION:
.word 1 ; Increment this if layout of co-op state changes

PLAYER_ID:
.byte 0x00 ; Written by frontend
PLAYER_NAME_ID:
.byte 0x00
INCOMING_ITEM:
.halfword 0x0000
.align 4

OUTGOING_KEY:
.word 0x00000000
OUTGOING_ITEM:
.halfword 0x0000
OUTGOING_PLAYER:
.halfword 0x0000

.area 8*256, 0xDF
PLAYER_NAMES:
.endarea
