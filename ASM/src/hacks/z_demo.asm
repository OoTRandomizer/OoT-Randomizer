.headersize(0x80052310 - 0x00AC8270)

; Move references for the old entrance table to the extended one

; Cutscene_HandleConditionalTriggers()
; Check for current entrance index leads to SCENE_TEMPLE_OF_TIME

.org 0x80056F06
.halfword hi(gExtendedEntranceTable)
.org 0x80056F16
.halfword lo(gExtendedEntranceTable)

; Check for current entrance index leads to SCENE_GANON_BOSS

.org 0x80056F52
.halfword hi(gExtendedEntranceTable)
.org 0x80056F62
.halfword lo(gExtendedEntranceTable)

.headersize(0)
