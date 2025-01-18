agony_distance_hook:
    ; called as SoA code computes distance from Link to grotto
    addiu   sp, sp, -0x30
    sw      ra, 0x001C(sp)
    sw      a0, 0x0020(sp)
    sw      a1, 0x0024(sp)
    swc1    f0, 0x0028(sp)
    c.lt.s  f0, f2 ; check if close to grotto
    nop
    bc1t    @@outside_radius
    nop
@@inside_radius:
    jal     agony_inside_radius_setup
    nop
    b       @@done
    nop
@@outside_radius:
    jal     agony_outside_radius_setup
    nop
@@done:
    ; reset registers
    li      a2, 0x0014
    li      a3, 0x000A
    mtc1    r0, f2
    lwc1    f0, 0x0028(sp)
    lw      a1, 0x0024(sp)
    lw      a0, 0x0020(sp)
    lw      ra, 0x001C(sp)
    c.lt.s  f0, f2 ; displaced
    addiu   sp, sp, 0x30
    jr      ra
    nop


agony_vibrate_hook:
    ; called when SoA code checks to see if it should command a vibration
    addiu   sp, sp, -0x30
    sw      ra, 0x001C(sp)
    sw      a0, 0x0020(sp)
    sw      a1, 0x0024(sp)
    swc1    f4, 0x0028(sp)
    swc1    f6, 0x002C(sp)
    c.lt.s  f4, f6
    nop
    bc1f    @@done ; check 4000000.0 < agony vibe counter
    nop
    jal     agony_vibrate_setup
    nop
@@done:
    ; reset registers
    li      a2, 0x0014
    li      a3, 0x000A
    mtc1    r0, f2
    lwc1    f6, 0x002C(sp)
    lwc1    f4, 0x0028(sp)
    lw      a1, 0x0024(sp)
    lw      a0, 0x0020(sp)
    lw      ra, 0x001C(sp)
    c.lt.s  f4, f6 ; displaced
    addiu   sp, sp, 0x30
    jr      ra
    nop


agony_post_hook:
    ; called every frame at the end of SoA code
    jal     draw_agony
    nop
    lw      ra, 0x001C(sp)
    addiu   sp, sp, 0x0020 ; displaced
    jr      ra
    nop
