; Pointers to game state
.definelabel SAVE_CONTEXT,      0x8011A5D0
.definelabel GLOBAL_CONTEXT,    0x801C84A0
.definelabel SUBSCREEN_CONTEXT, 0x801D8C00
.definelabel PLAYER_ACTOR,      0x801DAA30
.definelabel GET_ITEMTABLE,     0x803A9E7E

; Extended memory map:
ASM_MEM equ 0x80480000
C_MEM   equ 0x80500000

.definelabel DEBUG_BUFFER, ASM_MEM + 0 ; Size 0x1000

.definelabel C_HEAP, C_MEM + 0
