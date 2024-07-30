CFG_DEADLY_BONKS:
    .word 0x00000000
CFG_BONK_DAMAGE:
    .halfword 0x0000
.align 8


BONK_LAST_FRAME:
    addiu   sp, sp, -0x18
    sw      ra, 0x10($sp)

    ; Bonk damage enabled
    lw      t0, CFG_DEADLY_BONKS
    beqz    t0, @@return_bonk_frame
    nop
    ; Set player health to zero
    jal     APPLY_BONK_DAMAGE
    nop

@@return_bonk_frame:
    lw      ra, 0x10($sp)
    addiu   sp, sp, 0x18

    ; skipped code at end of func_808427BC after replaced branch statement
    lw      s0, 0x0020($sp)
    addiu   $sp, $sp, 0x0050
    jr      ra
    nop


SET_BONK_FLAG:
    ; displaced code
    or      a0, s0, $zero
    addiu   a1, $zero, 0x00FF

    ; Bonk damage enabled
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

    ; Bonk damage enabled
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
    bltz    t4, @@bonks_kill
    nop
    sh      t4, 0x30(t8)
    b       @@cmg_entrance_hack
    nop

@@bonks_kill:
    sh      $zero, 0x30(t8)  ; Player Health

@@cmg_entrance_hack:
    lh      t3, 0x30(t8)                ; Skip scene check if player will survive the damage
    bnez    t3, @@return_bonk
    nop
    la      t7, GLOBAL_CONTEXT          ; Only change flags if we're in the Treasure Box Shop
    lh      t3, 0x00A4(t7)              ; current scene number
    li      t4, 0x0010                  ; Treasure Box Shop scene number
    bne     t3, t4, @@return_bonk
    nop
    lb      t3, SHUFFLE_CHEST_GAME      ; don't reset anything if TCG shuffle is enabled
    bnez    t3, @@return_bonk
    nop
    ; Set scene temp flags to zero to re-lock doors
    sw      $zero, 0x1D2C(t7)
    ; Chests should be reset on scene load, but just in case
    sw      $zero, 0x1D38(t7)
    ; Remove any keys in the player's inventory for Treasure Box Shop
    sb      $zero, 0x00CC(t8)

@@return_bonk:
    jr      ra
    nop


KING_DODONGO_BONKS:
    ; One Bonk KO setting enabled
    lh      t0, CFG_BONK_DAMAGE
    addiu   t2, $zero, 0xFFFE
    bne     t0, t2, @@return_bonk_kd
    nop

    ; Set King Dodongo health to zero
    lh      t1, 0x0198(s1)          ; this->numWallCollisions
    beqz    t1, @@return_bonk_kd
    nop
    sh      $zero, 0x0184(s1)       ; this->health

@@return_bonk_kd:
    ; displaced code
    lh      t2, 0x0032(s1)
    mtc1    $zero, $f16
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
    ; Skip jal 0x8006B6FC (OnePointCutscene_Init) at end of func_80834508.
    ; Previously used hard-coded address at end of function, but making that
    ; address relative to $ra broke on VC. Not much left in the function, so
    ; reproduced here instead of trying to go back to just after the hook.
    lw      ra, 0x0024($sp)
    lw      s0, 0x0020($sp)
    addiu   $sp, $sp, 0x0030

@@return_death_subcamera:
    jr      ra
    nop
