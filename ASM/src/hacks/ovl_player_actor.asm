.headersize(0x808301C0 - 0x00BCDB70)

; Move references for the old entrance table to the extended one

; Player_Init()
; Check if we're on the title screen

.org 0x808450DA
.halfword hi(gExtendedEntranceTable)
.org 0x808450EA
.halfword lo(gExtendedEntranceTable) + 2

; Prevent respawns from grotto actor trigger
.org 0x8084DA04
    nop
.org 0x8084DA28
    nop
;; Prevent void out from grotto actor trigger
;.org 0x8084DA38
;    nop
; Remove transition trigger on grotto trigger
;.org 0x8084DA87
;.byte 0

; Maintain grotto start mode in respawn flags
.org 0x808451A8
    jal     override_respawn_params_hook
    nop

; Player_HandleExitsAndVoids()
; Skip check for ENTR_RETURN_GROTTO by converting bne to b
; Bytes written directly to avoid messing with the relocation address
.org 0x808372BC
; equivalent of beq $zero, $zero, ...
.halfword 0x1000

.headersize(0)
