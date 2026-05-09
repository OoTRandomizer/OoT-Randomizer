.headersize(0x808301c0 - 0xbcdb70)

;================================================================================
; Fixes softlock when starting cutscene while dismounting a ladder.
;================================================================================
; Replaces  lw  t8,1644(s0)
;           lui at,0xffdf
.org 0x8084a6c4         ; in Player_Action_DismountLadder (0x803a3064)
    jal     Player_LadderCutsceneFix
    nop

;================================================================================
; Prevent softlock if Hookshot actor cannot spawn when equipping
; (memory shortage due to Hyrule Field glitch, child equip etc)
;================================================================================
; Replaces  lw      a1,60(sp)
;           sw      v0,924(a1)
.org 0x808319d4         ; in Player_InitHookshotIA (0x8038a374)
     jal     Player_HookshotCheckActorSpawn
     lw      a1,60(sp)       ; displaced (loads player)
