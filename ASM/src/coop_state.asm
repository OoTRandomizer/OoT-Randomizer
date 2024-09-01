COOP_CONTEXT:

COOP_VERSION:
.word 7 ; Increment this if layout of co-op state changes

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
MW_PROGRESSIVE_ITEMS_ENABLE:
; Written by multiworld plugin. If nonzero, item upgrades for outgoing items
; will be based on MW_PROGRESSIVE_ITEMS_STATE.
.byte 0x00
.align 4

.word 0x00000000 ; Padding where OUTGOING_KEY used to be.
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

.area 4*256, 0x00
MW_PROGRESSIVE_ITEMS_STATE:
.endarea

.align 4
OUTGOING_KEY:
.word 0x00000000
.word 0x00000000

.align 4
