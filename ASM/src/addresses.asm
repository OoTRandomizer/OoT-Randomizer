; Pointers to game state
.definelabel SAVE_CONTEXT,      0x8011A5D0
.definelabel GLOBAL_CONTEXT,    0x801C84A0
.definelabel SUBSCREEN_CONTEXT, 0x801D8C00
.definelabel PLAYER_ACTOR,      0x801DAA30
.definelabel GET_ITEMTABLE,     0x803A9E7E

; Extended memory map:
//AUDIO_THREAD_FREE             0x8018EE60 ; size 0x37F00
.definelabel DEBUG_BUFFER,      0x80600000 ; size 0x1000
.definelabel C_HEAP,            0x80601000
