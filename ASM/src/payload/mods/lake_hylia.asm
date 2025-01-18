                      ; ID      x       y       z       xrot    yrot    zrot    var
Gossip_Actor: .halfword 0x01B9, 0xFCD5, 0xFB25, 0x1AD2, 0x0000, 0xF2DC, 0x0000, 0x8022


Hit_Gossip_Stone:
    addi    sp, sp, -0x14
    sw      ra, 0x10(sp)

    ; If special flag is not set, then display time as normal
    lhu     t0, 0x001C(s0)
    andi    t0, t0, 0x8000
    beqz    t0, @@show_time
    nop

    ; Check if control over lake is enabled
    ; If morpha is alive, do nothing
    li      v1, SAVE_CONTEXT
    lhu     t5, 0x0EDC(v1)
    andi    t5, t5, 0x0400     ;t5 = morpha flag
    beqz    t5, @@return
    nop

    ; Only Adult has control
    lw      t6, 0x0004(v1)
    bnez    t6, @@return
    nop

@@trigger_fill:
    ; Set switch flag #0
    lhu     t5, 0x01D2A(a0)     ;t5 = switch flags
    ori     t6, t5, 0x0001
    sh      t6, 0x01D2A(a0)     ; clear switch flag #0
    b       @@return
    nop

@@show_time:
    jal     0x800DCE14
    nop

@@return:
    lw      ra, 0x10(sp)
    addi    sp, sp, 0x14
    jr      ra
    nop


Check_Fill_Lake:
    lw      t6, 0x0004(v1)     ; otherwise return if age is child
    jr      ra
    nop


Fill_Lake_Destroy:
    ; If this is the water plane, setup the
    ; fill code instead of destroying
    lh  t0, 0x001C(a0)
    li  at, 0x0002
    bne t0, at, @@destroy
    nop

    ; if child then destroy
    li      v0, SAVE_CONTEXT
    lw      t3, 0x0004(v0)
    bnez    t3, @@return
    nop

@@setup_fill_control:
    ; Set fill code for main loop
    lui     t1, hi(Fill_Lake)
    addiu   t1, t1, lo(Fill_Lake)
    sw      t1, 0x0154(a0)

    ; Spawn relevant actors
    addiu   sp, sp, -0x20
    sw      ra, 0x10(sp)
    sw      a1, 0x14(sp)

    ; Spawn gossip stone
    lw      a2, 0x14(sp)
    li      a1, Gossip_Actor
    jal 0x800255C4
    addiu   a0, a2, 0x1C24

    lw      ra, 0x10(sp)
    addiu   sp, sp, 0x20
    b       @@return
    nop

@@destroy:
    sw  a0, 0x0000(sp)
    sw  a1, 0x0004(sp)

@@return:
    jr  $ra
    nop


Fill_Lake:
    addiu   sp, sp, -0x28
    sw      s0, 0x0020(sp)
    sw      ra, 0x0024(sp)
    sw      a1, 0x002C(sp)
    or      s0, a0, zero       ;s0 = actor*

    lwc1    f0, 0x015C(s0)     ; f0 = water displacement

    li      at, 0xC4A42000      ;at = water offset (-1313.0)
    mtc1    at, f2

    ; if morpha is not dead, then return
    li      v0, SAVE_CONTEXT
    lhu     t3, 0x0EDC(v0)
    andi    t4, t3, 0x0400     ;t4 = morpha flag
    lhu     t3, 0x0EE0(v0)
    beqz    t4, @@return
    nop
    addiu   t7, zero, 0xFBA7   ;t7 = FFFFFBA7 (-0x0459)

@@morpha_dead:
    ; toggle the fill flag if the ocarina spot switch flag was set
    lhu     t5, 0x01D2A(a1)     ;t5 = switch flags
    andi    t6, t5, 0x0001
    beqz    t6, @@no_trigger    ; switch flag #0
    nop
    andi    t5, t5, 0xFFFE
    sh      t5, 0x01D2A(a1)     ; clear switch flag #0
    li      at, 0x0200
    xor     t3, t3, at
    sh      t3, 0x0EE0(v0)      ; toggle fill flag

@@no_trigger:
    ; set target to fill or drain
    andi    t4, t3, 0x0200     ;t3 = lake filled flag
    beqz    t4, @@draining
    nop

@@filling:
    li     at, 0x00000000
    mtc1   at, f4              ;f4 = target displacement [0.00]
    lui    a2, 0x4080
    mtc1   a2, f6              ;f6 = fill speed [4.00]
    nop
    add.s  f8, f0, f6
    c.lt.s f8, f4
    nop
    b      @@check_fill_max
    nop

@@draining:
    li     at, 0xC42A0000
    mtc1   at, f4              ;f4 = target displacement [-680.00]
    lui    a2, 0xC080
    mtc1   a2, f6              ;f6 = fill speed [-4.00]
    nop
    add.s  f8, f0, f6
    c.lt.s f4, f8
    nop
    addiu   t7, zero, 0xFB57   ;t7 = FFFFFB57 (-0x04A9)

@@check_fill_max:
    ; if next fill level would pass the taget, then set to target
    ; this will skip the audio as well
    bc1f    @@skip_fill_update
    nop

    ; update the fill level with the new value
    mov.s   f4, f8
    ; Play sound
    jal     0x80023108
    li      a1, 0x205E
    or      a0, s0, zero

@@skip_fill_update:
    swc1    f4, 0x015C(s0)

    ; update water planes
    add.s   f4, f4, f2
    swc1    f4, 0x0028(s0)
    trunc.w.s   f16, f4
    mfc1    t1, f16            ;t1 = actor y-pos

    lw      v0, 0x002C(sp)     ;v0 = global_context
    lw      t8, 0x07C0(v0)     ;t8 = col_hdr
    lw      t9, 0x0028(t8)     ;t9 = col_hdr.water

    sh      t7, 0x0012(t9)     ;Water level when coming from Gerudo Valley
    sh      t1, 0x0022(t9)     ;col_hdr.water[2].pos.y = actor y-pos
    sh      t1, 0x0032(t9)     ;col_hdr.water[3].pos.y = actor y-pos

@@return:
    lw      ra, 0x0024(sp)
    lw      s0, 0x0020(sp)
    addiu   sp, sp, 0x0028
    jr      ra
    nop
