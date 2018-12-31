PLAYER_ID:
.byte 0x00 ; Written by frontend
PLAYER_NAME_ID:
.byte 0x00
INCOMING_ITEM:
.halfword 0x0000
.align 4

OUTGOING_OVERRIDE:
.word 0x00000000, 0x00000000

.area 8*256, 0xDF
PLAYER_NAMES:
.endarea
