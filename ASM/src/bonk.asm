CFG_DEADLY_BONKS:
    .word 0x00000000
CFG_BONK_DAMAGE:
    .halfword 0x0000
.align 8


BONK_LAST_FRAME:
    addiu   sp, sp, -0x18
    sw      ra, 0x10($sp)

    ; displaced code
    or      a0, s0, $zero
    jal     0x80390B18  ; func_80838178, static location as part of player overlay
    nop

    ; One Bonk KO setting enabled
    lw      t0, CFG_DEADLY_BONKS
    beqz    t0, @@return_bonk_frame
    nop
    ; Set player health to zero
    jal     APPLY_BONK_DAMAGE
    nop

@@return_bonk_frame:
    lw      ra, 0x10($sp)
    jr      ra
    addiu   sp, sp, 0x18


SET_BONK_FLAG:
    ; displaced code
    or      a0, s0, $zero
    addiu   a1, $zero, 0x00FF

    ; One Bonk KO setting enabled
    lw      t0, CFG_DEADLY_BONKS
    beqz    t0, @@return_bonk_flag
    nop

    ; set flag
    lbu     t0, 0x0682(s0)   ; Player state3 flag 4
    ori     t1, t0, 0x0010
    sb      t1, 0x0682(s0)

@@return_bonk_flag:
    jr      ra
    nop


CHECK_FOR_BONK_CANCEL:
    addiu   sp, sp, -0x18
    sw      ra, 0x10($sp)

    ; displaced code
    addiu   $at, $zero, 0x0002
    lui     t1, 0x8012

    ; One Bonk KO setting enabled
    lw      t8, CFG_DEADLY_BONKS
    beqz    t8, @@return_bonk_check
    nop

    ; Check if bonk flag was set and
    ; bonk animation flag (??) was cleared
    lbu     t8, 0x0682(s0)   ; Player state3 flag 4
    andi    t3, t8, 0x0010
    beqz    t3, @@return_bonk_check
    nop
    lh      t3, 0x0840(s0)   ; this->unk_850
    bnez    t3, @@return_bonk_check
    nop
    jal     APPLY_BONK_DAMAGE
    nop

@@return_bonk_check:
    lw      ra, 0x10($sp)
    jr      ra
    addiu   sp, sp, 0x18


APPLY_BONK_DAMAGE:
    ; Unset bonk kill flag
    lbu     t8, 0x0682(s0)   ; Player state3 flag 4
    andi    t3, t8, 0xFFEF
    sb      t3, 0x0682(s0)

    ; Set player health to zero
    lui     t8, 0x8012       ; Save Context (upper half)
    addiu   t8, t8, 0xA5D0   ; Save Context (lower half)
    lh      t3, 0x13C8(t8)   ; Nayru's Love Timer, range 0 - 1200
    bnez    t3, @@return_bonk
    nop
    lh      t3, CFG_BONK_DAMAGE
    bltz    t3, @@bonks_kill
    lh      t4, 0x30(t8)     ; Player Health
    lbu     t7, 0x3D(t8)     ; check if player has double defense
    beq     t7, zero, @@normal_defense
    nop
    sra     t3, t3, 1        ; halve damage from bonk
    sll     t3, t3, 0x10
    sra     t3, t3, 0x10
    
@@normal_defense:
    sub     t4, t4, t3
    sh      t4, 0x30(t8)
    b       @@return_bonk
    nop

@@bonks_kill:
    sh      $zero, 0x30(t8)  ; Player Health

@@return_bonk:
    jr      ra
    nop


KING_DODONGO_BONKS:
    ; displaced code
    lh      t2, 0x0032(s1)
    mtc1    $zero, $f16

    ; One Bonk KO setting enabled
    lw      t0, CFG_DEADLY_BONKS
    beqz    t0, @@return_bonk_kd
    nop

    ; Set King Dodongo health to zero
    lh      t1, 0x0198(s0)          ; this->numWallCollisions
    beqz    t1, @@return_bonk_kd
    nop
    sh      $zero, 0x0184(s0)       ; this->health

@@return_bonk_kd:
    jr      ra
    nop

CHECK_ROOM_MESH_TYPE:
    ; displaced code
    sll     a2, v0, 16
    sra     a2, a2, 16

    ; globalCtx->roomCtx.curRoom
    lui     $at, 0x0001
    ori     $at, $at, 0x1CBC
    addu    t6, a0, $at

    ; room->mesh->polygon.type
    lw      t7, 0x0008(t6)
    lbu     t8, 0x0000(t7)

    ; Room mesh type 1 is fixed camera areas
    ; Room mesh type 2 is follow camera areas
    ; Room mesh type 0 is ???
    ori     t7, $zero, 0x0001
    bne     t7, t8, @@return_death_subcamera
    nop
    j       0x8038D018 ; skips jal 0x8006B6FC (OnePointCutscene_Init), static location as part of player overlay
    lw      ra, 0x0024($sp)

@@return_death_subcamera:
    jr      ra
    nop
