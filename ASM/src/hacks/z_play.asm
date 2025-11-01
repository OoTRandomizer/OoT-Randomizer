.headersize(0x8009A170 - 0x00B100D0)

; Move references for the old entrance table to the extended one

; Play_Init()
; Check for current entrance index leads to SCENE_HYRULE_FIELD or SCENE_KOKIRI_FOREST
; Same register is later used for building arguments to Play_SpawnScene()

.org 0x8009AA32
.halfword hi(gExtendedEntranceTable)
.org 0x8009AA36
.halfword lo(gExtendedEntranceTable)

; Change transition type

.org 0x8009AD0E
.halfword hi(gExtendedEntranceTable)
.org 0x8009AD22
.halfword lo(gExtendedEntranceTable) + 2

; Play_Update()
; Lookup "continue background music" flag in entrance flags

.org 0x8009B0D6
.halfword hi(gExtendedEntranceTable)
.org 0x8009B0E6
.halfword lo(gExtendedEntranceTable) + 2

; Override scene layer for grotto scenes. Custom scene layers
; are used to change the exit list depending on entrance index,
; allowing the same scene load zone to be used to exit to multiple places.
.org 0x8009AB28
    jal     set_grotto_scene_layer_hook

; Play_SetupRespawnPoint()
; Remove exclusions for respawn point setup in fairy fountains and grottos
; Replaces
;   beq	    v0, at, 0x0EFE
;   li      at, 0x3E
;   beq	    v0, at, 0x0EFE
.org 0x8009D964
    nop
    nop
    nop

; Override Play_TriggerRespawn() to preserve grotto start mode on respawn,
; such as from lava in DMC
.org 0x8009DA10
    j       Play_TriggerRespawn
    nop

; Also override Play_SetupRespawnPoint()
.org 0x8009D94C
    j       Play_SetupRespawnPoint
    nop

.headersize(0)
