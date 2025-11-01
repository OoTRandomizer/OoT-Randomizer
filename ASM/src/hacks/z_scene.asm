.headersize(0x800812F0 - 0x00AF7250)

; Move references for the old entrance table to the extended one

; Scene_SetTransitionForNextEntrance()
; Change transition type

.org 0x800826EA
.halfword hi(gExtendedEntranceTable)
.org 0x80082776
.halfword lo(gExtendedEntranceTable) + 2

.headersize(0)
