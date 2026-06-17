                                     ; ID      x       y       z       xrot    yrot    zrot    var
HyliaWater_GossipActorEntry: .halfword 0x01B9, 0xFCD5, 0xFB25, 0x1AD2, 0x0000, 0xF2DC, 0x0000, 0x8022

EnGs_HitGossipStone:
    lhu     t0,0x1C(s0)         ; s0 = this EnGs
    andi    t0,t0,0x8000        ; If actor variable/params is not set bit 0x8000,
    beqz    t0,@@ShowTime       ; then display time as normal
    nop

    la      v1,SAVE_CONTEXT
    lhu     t5,0x0EDC(v1)
    andi    t5,t5,0x0400        ; Morpha dead flag/used Water Temple blue warp
    beqz    t5,@@Return         ; If Morpha is not defeated, do nothing

    lb      t5,0x01D2A(a0)      ; Else, trigger water fill/drain
    ori     t6,t5,1             ; Set scene switch flag #0
    b       @@Return
    sb      t6,0x01D2A(a0)

@@ShowTime:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    jal     0x800DCE14          ; Message_StartTextbox
    nop
    lw      ra,16(sp)
    addiu   sp,sp,24

@@Return:
    jr      ra
    nop

HyliaWater_SetupWaterFunction:
    addiu   sp,sp,-24           ; Adult: spawn Gossip + set action function
    sw      ra,16(sp)
    sh      a0,50(t9)           ; displaced
    la      v1,SAVE_CONTEXT
    lhu     t5,0x0EDC(v1)       ; Check Morpha dead flag/used Water Temple blue warp
    andi    t5,t5,0x0400
    beqzl   t5,@@SpawnGossip    ; If Morpha not dead, still spawn Gossip +
    sw      t1,340(s0)          ; set DoNothing as action function (from t1 for adult)

    la      t2,HyliaWater_WaterFunction
    sw      t2,340(s0)          ; If defeated, set water level control action function
@@SpawnGossip:
    la      a1,HyliaWater_GossipActorEntry
    lw      a2,92(sp)           ; a2 play, old sp 68 + added 24
    jal     Actor_SpawnEntry
    addiu   a0,a2,0x1C24        ; a0 actorCtx
@@Return:
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24

HyliaWater_WaterFunction:
    addiu   sp, sp, -0x28
    sw      s0, 0x0020(sp)
    sw      ra, 0x0024(sp)
    sw      a1, 0x002C(sp)      ; a1 = play
    or      s0, a0, zero       ;s0 = actor
    la      v0, SAVE_CONTEXT

    ; toggle the fill flag if the ocarina spot switch flag was set
    lb      t5, 0x01D2A(a1)     ;t5 = switch flags
    andi    t6, t5, 0x0001
    beqz    t6, @@no_trigger    ; switch flag #0
    andi    t5, t5, 0xFE

    sb      t5, 0x01D2A(a1)     ; clear switch flag #0
    lhu     t3, 0x0EE0(v0)
    li      at, 0x0200
    xor     t3, t3, at
    sh      t3, 0x0EE0(v0)      ; toggle fill flag

    sw      a2,48(sp)           ; load new minimap
    sw      v0,0x28(sp)
    jal     LakeHylia_ChangeMinimap
    move    a0,a1               ; play
    move    a0,s0
    lw      a2,48(sp)
    lw      v0,0x28(sp)

    ; set target to fill or drain
@@no_trigger:
    lwc1    f0, 0x015C(s0)     ; f0 = water displacement
    li      at, 0xC4A42000     ; at = water offset (-1313.0)
    lhu     t3, 0x0EE0(v0)
    andi    t4, t3, 0x0200     ;t3 = lake filled flag
    lw      v0, 0x002C(sp)     ;v0 = global_context
    lw      t8, 0x07C0(v0)     ;t8 = col_hdr
    lw      t9, 0x0028(t8)     ;t9 = col_hdr.water
    beqz    t4, @@draining
    mtc1    at, f2

@@filling:
    li     at, 2203            ; set Gerudo waterbox zMin like vanilla
    sh     at, 0x0014(t9)      ; set to 0x89b
    move   at, zero
    mtc1   at, f4              ;f4 = target displacement [0.00]
    lui    a2, 0x4080
    mtc1   a2, f6              ;f6 = fill speed [4.00]
    nop
    add.s  f8, f0, f6
    c.lt.s f8, f4
    nop
    b      @@check_fill_max
    addiu   t7, zero, 0xFBA7   ;t7 = FFFFFBA7 (-0x0459) Gerudo water level

@@draining:
    li     at, 2153            ; set Gerudo waterbox zMin like vanilla
    sh     at, 0x0014(t9)      ; set to 0x869
    lui    at, 0xC42A
    addiu  at, 0x2000
    mtc1   at, f4              ;f4 = target displacement [-681.00]
    lui    a2, 0xC080
    mtc1   a2, f6              ;f6 = fill speed [-4.00]
    nop
    add.s  f8, f0, f6
    c.lt.s f4, f8
    nop
    addiu   t7, zero, 0xFB57   ;t7 = FFFFFB57 (-0x04A9) Gerudo water level

@@check_fill_max:
    ; if next fill level would pass the taget, then set to target
    ; this will skip the audio as well
    bc1f    @@skip_fill_update
    li      a1, 0x205E      ; argument to sound function, ok as delay

    ; Play sound
    jal     0x80023108
    mov.s   f4, f8          ; update the fill level with the new value
    or      a0, s0, zero    ; restore

@@skip_fill_update:
    swc1    f4,0x15c(s0)        ; set lake hylia water pos (separate actor variable)
    ; set water actor y pos depending on lowest level or not
    li      at,0xc42a2000       ; vanilla lowest water y position
    mtc1    at,f6
    c.eq.s  f4,f6               ; if water level = lowest
    bc1t    @@DontChangeWater   ; don't use offset for actor y pos
    add.s   f4,f4,f2            ; because this makes gerudo water not draw
    b       @@UpdateWaterPos    ; but otherwise, use to draw rising/lowering
    swc1    f4,0x28(s0)         ; actor y pos = offset waterbox surface pos
@@DontChangeWater:
    li      at,0xc4a42000       ; vanilla actor y pos
    mtc1    at,f6
    swc1    f6,0x28(s0)
@@UpdateWaterPos:
    ; update water planes
    trunc.w.s   f16, f4
    mfc1    t1, f16            ;t1 = actor y-pos
    lw      v0, 0x002C(sp)     ;v0 = global_context
    lw      t8, 0x07C0(v0)     ;t8 = col_hdr
    lw      t9, 0x0028(t8)     ;t9 = col_hdr.water
    sh      t7, 0x0012(t9)     ;Water level when coming from Gerudo Valley
    sh      t1, 0x0022(t9)     ;col_hdr.water[2].pos.y = main water surface1 = actor y-pos
    sh      t1, 0x0032(t9)     ;col_hdr.water[3].pos.y = main water surface2 = actor y-pos

@@return:
    lw      ra, 0x0024(sp)
    lw      s0, 0x0020(sp)
    jr      ra
    addiu   sp, sp, 0x0028
