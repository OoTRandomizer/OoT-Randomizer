CHEST_LENS_ONLY:
    .word   0x00000000


GET_CHEST_OVERRIDE_WRAPPER:
    sb  t9,0x01E9(s0)

    addiu   sp, sp, -0x20
    sw      ra, 0x04 (sp)
    sw      a0, 0x08 (sp)
    sw      a1, 0x0C (sp)
    sw      t0, 0x10 (sp)
    swc1    $f10, 0x14 (sp)
    swc1    $f16, 0x18 (sp)

    jal     get_chest_override
    move    a0, s0

    lw      ra, 0x04 (sp)
    lw      a0, 0x08 (sp)
    lw      a1, 0x0C (sp)
    lw      t0, 0x10 (sp)
    lwc1    $f10, 0x14 (sp)
    lwc1    $f16, 0x18 (sp)
    jr      ra
    addiu   sp, sp, 0x20


HIDE_CHEST_WITH_INVERTED_LENS:
    ; displaced code
    sll     t9, s2, 2
    addu    t0, s7, t9

    ; Do not draw chests if invisible chests setting is on and lens is not active
    ; If lens is active, bypass default actor lens draw logic for chests in rooms
    ; with inverted lens behavior (hide vs show actors).
    ; t5 holds if the room has inverted lens logic, branching at VRAM 0x80024BB4
    ; If the current actor is a chest with its lens flag active, and the
    ; invisible chests setting is on, override t5 to always hide the current actor

    ; Invisible Chests setting enabled
    lw      t2, CHEST_LENS_ONLY
    beqz    t2, @@return_draw
    nop

    ; Treasure Chest Minigame uses chests with type ID 4,
    ; same as normal invisible big chests.
    ; Lens behavior is inverted in this room for chests
    ; but regular for the key and rupee rewards.
    ; To keep the game beatable, always show the chests
    ; in the minigame if invisible chests are enabled.
    ; Since chests use the same type ID as elsewhere, hard code
    ; the scene ID for the minigame (16).
    lh      t2, 0x00A4(s1)
    ori     t1, $zero, 0x0010
    beq     t2, t1, @@return_draw
    nop

    ; actor->id == ACTOR_EN_BOX
    lh      t2, 0x0000(s0)
    ori     t1, $zero, 0x000A
    bne     t2, t1, @@return_draw
    nop

    ; actor->flags & ACTOR_FLAG_7
    lw      t2, 0x0004(s0)
    andi    t1, t2, 0x0080
    beqz    t1, @@return_draw
    nop

    ; globalCtx->roomCtx.curRoom.showInvisActors
    addu    t1, s1, s4
    lbu     t2, 0x1CC1(t1)
    beqz    t2, @@return_draw
    nop

    ; globalCtx->actorCtx.lensActive
    lbu     t2, 0x1C27(s1)
    bnez    t2, @@return_draw
    nop

@@return_hide:
    andi    t5, $zero, 0x0000
    jr      ra     ; invisible
    nop

@@return_draw:
    jr      ra     ; vanilla behavior
    nop


SHOW_CHEST_WITH_INVERTED_LENS:
    ; displaced code
    lw      v0, 0x0004(s0)
    andi    t3, v0, 0x0060

    ; negate actor lens flag in rooms with inverted lens logic if the
    ; actor is a chest and lens is active

    ; Invisible Chests setting enabled
    lw      t2, CHEST_LENS_ONLY
    beqz    t2, @@return_draw_show
    nop

    ; actor->id == ACTOR_EN_BOX
    lh      t2, 0x0000(s0)
    ori     t1, $zero, 0x000A
    bne     t2, t1, @@return_draw_show
    nop

    ; actor->flags & ACTOR_FLAG_7
    lw      t2, 0x0004(s0)
    andi    t1, t2, 0x0080
    beqz    t1, @@return_draw_show
    nop

    ; globalCtx->roomCtx.curRoom.showInvisActors
    addu    t1, s1, s4
    lbu     t2, 0x1CC1(t1)
    beqz    t2, @@return_draw_show
    nop

    ; globalCtx->actorCtx.lensActive
    lbu     t2, 0x1C27(s1)
    beqz    t2, @@return_draw_show
    nop

    ; current scene ID == 16
    lh      t2, 0x00A4(s1)
    ori     t1, $zero, 0x0010
    beq     t2, t1, @@return_draw_show
    nop

    andi    v0, $zero, 0x0000   ; flags aren't referenced again, safe to delete
    jr      ra     ; visible
    nop

@@return_draw_show:
    jr      ra     ; vanilla behavior
    nop
