kill_door_of_time_col:
    sw      zero, 0x130(a0) ; update = NULL
    sw      zero, 0x134(a0) ; draw = NULL
    la      at, SAVE_CONTEXT
    lb      t0, 0x0EDC(at)
    ori     t0, t0, 0x08 ; "Opened the Door of Time" Flag
    sb      t0, 0x0EDC(at)
    lui     at, 0x3F80 ; displaced instruction
    jr      ra
    mtc1    at, f6 ; displaced instruction
