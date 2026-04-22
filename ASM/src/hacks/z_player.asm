.headersize(0x808301c0 - 0xbcdb70)

;================================================================================
; Check if D-pad item should be used, after B and C buttons were not pressed
; but before checking if any button is held. If so, uses D-pad item
;================================================================================
; Replaces  move    a3,zero
;           li      a1,4
.org 0x808320b8             ; in Player_ProcessItemButtons
    jal     Player_CallUseDpadItem
    nop

; Make D-pad down (0x400) cancel first person mode
; Replaces  andi    t8,t7,0xc01f
.org 0x80849394             ; in Player_Action_InFirstPerson
    andi    t8,t7,0xc41f
