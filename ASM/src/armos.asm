en_am_calculation_1:
    lui     at, 0x3F81
    ori     at, at, 0x3F19
    mtc1    at, f8
    jr      ra
    nop

en_am_calculation_2:
    lui     at, 0x3F81
    ori     at, at, 0x3F19
    mtc1    at, f10
    jr      ra
    nop
