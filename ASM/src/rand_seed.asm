rand_seed_truth_spinner:
    addiu   sp, sp, -0x20
    sw      a0, 0x18(sp)
    sw      ra, 0x1C(sp)
    
    jal     Seeded_Rand_ZeroOne
    nop

    lw      a0, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20