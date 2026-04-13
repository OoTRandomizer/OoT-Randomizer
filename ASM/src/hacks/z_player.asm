.headersize(0x808301c0 - 0xbcdb70)

;================================================================================
; Fixes softlock when starting cutscene while dismounting a ladder.
;================================================================================
; Replaces  lw  t8,1644(s0)
;           lui at,0xffdf
.org 0x8084a6c4         ; in Player_Action_DismountLadder (0x803a3064)
    jal  player_ladder_cutscene
    nop
