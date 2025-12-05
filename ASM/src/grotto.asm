; Temporary byte used when loading inside grottos to indicate which grotto we are in when exiting
CURRENT_GROTTO_ID:
.byte 0xFF
.align 4


set_grotto_scene_layer_hook:
    ; Displaced code
    lb      a1, 0x0000(v0)

    addiu   sp, sp, -0x20
    sw      ra, 0x04(sp)
    sw      a1, 0x08(sp)
    sw      a2, 0x0C(sp)
    sw      v0, 0x10(sp)
    sw      v1, 0x14(sp)
    jal     SetGrottoSceneLayer
    nop
    lw      a1, 0x08(sp)
    lw      a2, 0x0C(sp)
    lw      v0, 0x10(sp)
    lw      v1, 0x14(sp)
    lw      ra, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x20


set_grotto_entrance_hook:
    addiu   sp, sp, -0x10
    sw      ra, 0x04(sp)
    sw      a0, 0x08(sp)
    sw      a1, 0x0C(sp)
    addu    a0, s0, $zero
    addu    a1, a3, $zero
    jal     SetGrottoEntranceIndex
    nop
    lw      a1, 0x0C(sp)
    lw      a0, 0x08(sp)
    lw      ra, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x10


override_respawn_params_hook:
    addiu   sp, sp, -0x20
    sw      ra, 0x04(sp)
    sw      a0, 0x08(sp)
    sw      a1, 0x0C(sp)
    sw      s0, 0x10(sp)
    sw      s1, 0x14(sp)
    sw      s2, 0x18(sp)
    sw      t6, 0x1C(sp)
    addu    a0, s0, $zero
    jal     OverrideRespawnPlayerParams
    nop
    lw      t6, 0x1C(sp)
    lw      s0, 0x10(sp)
    lw      s1, 0x14(sp)
    lw      s2, 0x18(sp)
    lw      a1, 0x0C(sp)
    lw      a0, 0x08(sp)
    lw      ra, 0x04(sp)
    sb      t6, 0x137B(s2)
    lh      v0, 0x00A4(s1)
    jr      ra
    addiu   sp, sp, 0x20
