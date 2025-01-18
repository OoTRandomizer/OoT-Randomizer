clear_boomerang_pointer:
    sw      a0, 0x18(sp)  ;displaced
    la      t0, PLAYER_ACTOR
    jr      ra
    sw      r0, 0x678(t0) ;pointer to boomerang in Links instance
