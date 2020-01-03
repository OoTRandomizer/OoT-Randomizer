; Door_Ana - VROM 0xCF7710, VRAM 0x80959A10

@AGONY_BYTE              equ SAVE_CONTEXT + 0xA5
@AGONY_MASK              equ 0x20

door_ana_update_invisible_pre:
    ; displaced code
    or      s0, a0, r0

    ; a0 points to z_Actor struct
    lb      t0, @AGONY_BYTE
    andi    t0, @AGONY_MASK
    beqz    t0, @@done ; do nothing without stone of agony
    nop
    addiu   sp, -0x0010
    sw      ra, 0x0004(sp)
    jal     update_agony_distance
    nop
    lw      ra, 0x0004(sp)
    addiu   sp, 0x0010 
@@done:
    jr      ra
    nop