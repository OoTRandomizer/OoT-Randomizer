COOP_CONTEXT:

COOP_VERSION:
.word 4 ; Increment this if layout of co-op state changes

PLAYER_ID:
.byte 0x00 ; Written by frontend
PLAYER_NAME_ID:
.byte 0x00
INCOMING_PLAYER:
.halfword 0x0000
INCOMING_ITEM:
.halfword 0x0000
MW_SEND_OWN_ITEMS:
; Written by multiworld plugin. If nonzero, the OUTGOING fields are set even if
; we find our own item, for the plugin's information.
.byte 0x00
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

.area 5, 0x00
CFG_FILE_SELECT_HASH:
.endarea
.align 4
