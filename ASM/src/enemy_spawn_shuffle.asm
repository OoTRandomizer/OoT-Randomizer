Actor_UpdateAll_ClearRoomEnemyInhibit:

    lui     t6, hi(curr_room_enemies_inhibited)
    sb      r0, lo(curr_room_enemies_inhibited)(t6)
    ; Replaced code
    lw      v0, 0x0004(a1); rest of replaced code
    lui     t0, 0x8012
    lui     at, 0x00FF
    sll     t7, v0, 4
    srl     t8, t7, 28
    jr      ra
    nop
