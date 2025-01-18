;load zeldas current animation to check it
;also move link a little bit forward out of talk range
zelda_check_anim:
    addiu    a1, a1, 0x6F04 ;displaced, wait animation seg address
    lw       t0, 0x144(a0)  ;current animation
    beq      t0, a1, @@return
    la       t1, PLAYER_ACTOR
    li       t2, 0x4469C000 ;935.0f
    li       t3, 0xC3240000 ;-164.0f
    sw       t2, 0x24(t1)   ;x
    sw       t3, 0x2C(t1)   ;z
@@return:
    jr       ra
    nop
