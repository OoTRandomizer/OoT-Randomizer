.headersize (0x808301c0 - 0xbcdb70)

;================================================================================
; Remote Hookshot part 1/2. Make player keep holding bottle after drinking full
; milk with empty bottle equipped like in Majora's Mask
;================================================================================
; Replaces: move    a1,s0
;           li      a2,20
.org 0x8084cd3c         ; in Player_Action_DrinkBottle
    jal     Player_DrinkBottle_FullMilk
    move    a1,s0           ; displaced
