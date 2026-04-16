.headersize(0x808301c0 - 0xbcdb70)

;================================================================================
; Remote Hookshot part 1/2. Make player keep holding bottle after drinking full
; milk with empty bottle equipped like in Majora's Mask
;================================================================================
; Replaces  li      t7,2
;           sh      t7,2112(s0)
;           lw      a0,52(sp)
;           move    a1,s0
;           li      a2,20
.org 0x8084cd30         ; in Player_Action_DrinkBottle
    jal     PlayerMilkDrinkBottle
    li      t7,2
    li      a2,20       ; Set next item to empty bottle
    lw      a0,52(sp)   ; Load play
    move    a1,s0       ; Load player
