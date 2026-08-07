.headersize (0x808137c0 - 0x00bb11e0)

; Prevent empty equipment equip + allow unequipping sword
; Replaces: beq     v1,at,80818dc8
;           nop
;           lw      t3,4(t1)
;           lui     a1,0x8010
;           addiu   a1,a1,17300
;           bne     v1,t3,80818ebc
;           li      a2,4
.org 0x80818dac     ; KaleidoScope_DrawEquipment
    jal     KaleidoScope_PreventEmptyUnequipSword
    nop
    li      at,2
    beql    t7,at,0x80818ee0    ; don't run equip, don't play error sound
    nop                         ; = unequipped sword
    beqz    t7,0x80818ebc       ; don't run equip, play error sound
    li      a2,4                ; else, run normal equipping