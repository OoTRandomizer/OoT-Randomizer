EnGe1_GTGCheckPermGateOpen:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    sw      a0,20(sp)       ; save EnGe1 and play
    sw      a1,24(sp)
    move    a0,a1
    la      a1,DUNGEONS_SHUFFLED    ; Check setting and return if not set
    lb      a1,(a1)
    beqzl   a1,@@Return
    li      v0,0            ; Continue main function

    jal     Flags_GetSwitch ; Permanent open flag check
    li      a1,4
    beqz    v0,@@Return     ; If not set, continue main function as usual
    lw      a0,20(sp)
    la      a1,gActorOverlayTable   ; If set, set talk action function
    lw      a1,0x2710(a1)           ; EnGe1 loaded address
    addiu   a1,0x071C               ; EnGe1_SetNormalText address
    sw      a1,0x02A4(a0)           ; Set as action function

@@Return:
    lui     t6,0x8010       ; displaced
    lui     t7,0x8012       ; displaced
    lw      t7,-22924(t7)   ; displaced
    lw      t6,-29624(t6)   ; displaced
    lw      ra,16(sp)
    lw      a0,20(sp)
    lw      a1,24(sp)
    jr      ra
    addiu   sp,sp,24


EnGe1_GTGSetPermGateOpen:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    jal     Flags_SetSwitch     ; Set vanilla temp flag
    nop
    la      a1,DUNGEONS_SHUFFLED    ; Check setting and return if not set
    lb      a1,(a1)
    beqz    a1,@@Return
    nop
    jal     Flags_SetSwitch     ; Set new permanent flag 4
    li      a1,4
@@Return:
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24
