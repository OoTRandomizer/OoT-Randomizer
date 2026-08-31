KaleidoScope_PreventEmptyUnequipSword:  ; t1 savectx t8 age req table s6 pausectx
    addiu   sp,sp,-24
    sw      ra,24(sp)
    sw      v0,28(sp)

    jal     equipment_menu_slot_filled  ; prevent empty slots from being equipped
    nop
    bnezl   v0,@@CheckUse
    lbu     v1,(t8)         ; load age req from usability table
    li      v1,255          ; prevent equip (set wrong age)
    lui     a1,0x8010       ; displaced error setup
    addiu   a1,a1,17300     ; displaced error setup
    b       @@Return
    move    t7,zero         ; don't equip, run error after

@@CheckUse:
    li      at,9            ; usable all ages
    beq     v1,at,@@CheckSwordRow  ; displaced age check
    lw      t3,4(t1)        ; link age
    beql    v1,t3,@@CheckSwordRow  ; displaced age check
    nop
    lui     a1,0x8010       ; displaced error setup
    addiu   a1,a1,17300     ; displaced error setup
    b       @@Return
    move    t7,zero         ; don't equip, run error after

@@CheckSwordRow:    ; check if current row/Y is sword row
    bnezl   a0,@@Return     ; cursorY
    li      t7,1            ; if not, run regular equip

    lui     t0,0x8010
    lhu     t3,-29584(t0)   ; gEquipMasks
    lhu     t6,112(t1)      ; equips equipment
    and     t6,t6,t3        ; equips & gEquipMasks
    lh      at,552(s6)      ; cursorX
    bnel    at,t6,@@Return  ; if cursor sword != equipped sword,
    li      t7,1            ; equip sword

    lhu     t4,-29576(t0)   ; gEquipNegMasks
    lhu     t6,112(t1)      ; equips equipment
    and     t4,t6,t4
    sh      t4,112(t1)      ; remove equipped bit for current sword

    li      t0,1
    sh      t0,3890(t1)     ; set swordless flag
    li      t0,255          ; item_none
    sb      t0,104(t1)      ; button item b
    sb      t0,5090(t1)     ; button status b

    li      a0,18440        ; setup play equip sfx
    lui     a1,0x8010
    addiu   a1,a1,17300
    li      a2,4
    move    a3,s4
    lui     t4,0x8010
    addiu   t4,t4,17320
    sw      t4,20(sp)
    jal     Audio_PlaySfxGeneral
    sw      s4,16(sp)

    lui     t0,hi(gKaleidoMgrCurOvl)    ; load player-kaleido overlay manager
    lw      t0,lo(gKaleidoMgrCurOvl)(t0)
    lw      t0,0x14(t0)         ; load offset
    la      t9,0x808296f4       ; sEquipTimer
    addu    t9,t0               ; resulting address with offset
    li      t3,10
    sh      t3,(t9)             ; 10 frames timer
    li      t0,7
    sh      t0,484(s6)          ; set pause main state
    li      t7,2                ; don't run equip + don't run error
@@Return:
    lw      ra,24(sp)
    lw      v0,28(sp)
    jr      ra                  ; return value in t7
    addiu   sp,sp,24
