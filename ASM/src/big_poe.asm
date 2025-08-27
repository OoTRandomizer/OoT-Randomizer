; Since we changed the ocflags collision to be able to interact with everything, check if the actor the big poe soul
; has collided with either Link or Epona, to avoid weird interactions like throwing a bomb at the soul to collect it.
big_poe_soul_collision:
    andi    t1, t0, 0x0002             ; vanilla condition. if t1 = 0, then the soul won't interact with whatever was colliding.
    beq     t1, $zero, @@no_collision
    nop

    lw      t2, 0x0240(s0)
    lh      t3, 0x0000(t2)             ; t3 = this->collider.base.oc->id, so the id of the actor that collided with the soul

    beqz    t3, @@collision            ; compare to 0, the id of Player actor
    nop

    addiu   t2, $zero, 0x0014          ; 0014 is the horse actor
    bne     t2, t3, @@no_collision     ; if epona is colliding, check if Link is indeed riding
    nop

    lw      t2, 0x34(sp)               ; t2 = Playstate
    lw      v0, 0x1C44(t2)             ; v0 = Player
    lw      t2, 0x066C(v0)             ; t2 = player->stateFlags1
    sll     t3, t2,  8                 ; t3 = (player->stateFlags1 & PLAYER_STATE1_23), the riding state
    bltzl   t3, @@collision
    nop

@@no_collision:
    jr      ra
    addiu   t1, $zero, 0x0000

@@collision:
    jr      ra
    addiu   t1, $zero, 0x0001
