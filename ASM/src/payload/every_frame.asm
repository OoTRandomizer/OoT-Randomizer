before_game_state_update_hook:
    addiu   sp, sp, -0x18
    sw      ra, 0x10 (sp)

    jal     before_game_state_update
    nop

    lw      ra, 0x10 (sp)
    addiu   sp, sp, 0x18

    ; Displaced code
    lw      t6, 0x0018 (sp)
    jr      ra
    lui     at, 0x8010
