; Grotto Load Table
;
; This table describes all data needed to load into each grotto with the correct content.
; There is one entry for each grotto (33 grottos).
;
; Entry format (4 bytes):
; EEEECC00
; EEEE = Entrance index (to enter the correct grotto room)
; CC = Grotto content (content to load generic grottos with, changes chests, scrubs, gossip stones...)
.area 33 * 4, 0
GROTTO_LOAD_TABLE:
.endarea

; Grotto Exit List
;
; This List defines the entrance index used when exiting each grotto.
; There is one entrance index for each grotto, in the same order as the Grotto Load Table.
.area 33 * 2, 0
GROTTO_EXIT_LIST:
.endarea

; Temporary byte used when loading inside grottos to indicate which grotto we are in when exiting
CURRENT_GROTTO_ID:
.byte 0xFF
.align 4


; Player Actor code: Runs when the player hits any exit collision, right after getting the entrance index from the scene exit list
; Adds code to handle entering (or exiting) grottos from (or to) any entrance (needed when randomizing entrances)
; t6 = entrance index of the exit the player just hit
; at = global context pointer
scene_exit_hook:
    la      t2, CURRENT_GROTTO_ID
    lbu     t3, 0x0000(t2)          ; get the value of the dynamic grotto id byte
    li      t4, 0xFF
    sb      t4, 0x0000(t2)          ; reset the dynamic grotto id to 0xFF (default)

    li      t0, 0x7FFF
    bne     t6, t0, @@normal        ; if not a grotto exit, skip to the normal routine

    ; Translate to the correct grotto exit
    la      t1, GROTTO_EXIT_LIST
    beq     t3, t4, @@return        ; if the dynamic grotto id is not set (== 0xFF), keep 0x7FFF as the entrance index
    sll     t3, t3, 1
    addu    t1, t1, t3
    lhu     t6, 0x0000(t1)          ; use the entrance index from the grotto exit list for that grotto

@@normal:
    ; Handle grotto load indexes to be translated if necessary
    addiu   sp, sp, -0x10
    sw      ra, 0x04 (sp)
    sw      a0, 0x08 (sp)

    jal     handle_grotto_load
    move    a0, t6
    move    t6, v0

    lw      ra, 0x04 (sp)
    lw      a0, 0x08 (sp)
    addiu   sp, sp, 0x10

@@return:
    jr      ra
    sh      t6, 0x1E1A(at)          ; set the entrance index to load in the context


; Grotto Actor code: Runs when the player hits a grotto collision, right before setting the entrance index to load
; Adds code to allow the actor to lead to any entrance index if the grotto scene var is >= 2 (normally either 0 or 1)
; t5 = entrance index to use (already set to a grotto entrance index based on the usual grotto actor routine)
; s0 = grotto actor data pointer
grotto_entrance:
    lhu     t0, 0x001C(s0)          ; t0 = actor variable
    sra     t0, t0, 12
    andi    t0, t0, 0xF             ; t0 = grotto scene var (0 = grotto scene, 1 = fairy fountain scene, 2+ = use zrot)
    slti    t1, t0, 2
    bne     t1, zero, @@return      ; if scene var < 2, skip to use the already defined grotto entrance index
    nop
    lhu     t5, 0x0018(s0)          ; else, use the actor zrot as the entrance index

    ; Handle grotto load indexes to be translated if necessary
    addiu   sp, sp, -0x10
    sw      ra, 0x04 (sp)
    sw      a0, 0x08 (sp)

    jal     handle_grotto_load
    move    a0, t5
    move    t5, v0

    lw      ra, 0x04 (sp)
    lw      a0, 0x08 (sp)
    addiu   sp, sp, 0x10

@@return:
    jr      ra
    addu    at, at, a3              ; displaced code


; Translate the given entrance index to a grotto load if it corresponds to one
; a0 = entrance index
; returns v0 = new entrance index
handle_grotto_load:
    li      t0, 0x7FF9
    sub     t0, a0, t0
    bgez    t0, @@return            ; dynamic exits (entrance indexes > 0x7FF9) shouldn't be translated
    li      t0, 0x1000
    sub     t0, a0, t0
    bltz    t0, @@return            ; normal exits (entrance indexes < 0x1000) shouldn't be translated either

    ; Translate to grotto load
    la      t1, SAVE_CONTEXT
    la      t2, GROTTO_LOAD_TABLE
    la      t3, CURRENT_GROTTO_ID
    sb      t0, 0x0000(t3)          ; set the grotto id to use when exiting the grotto
    sll     t0, t0, 2
    addu    t2, t2, t0
    lhu     a0, 0x0000(t2)          ; use the entrance index of the grotto we want to load in
    lbu     t0, 0x0002(t2)
    sb      t0, 0x1397(t1)          ; set the grotto content to load with

@@return:
    jr      ra
    move    v0, a0


set_grotto_scene_layer_hook:
    ; Displaced code
    lb      a1, 0x0000(v0)

    addiu   sp, sp, -0x20
    sw      ra, 0x04(sp)
    sw      a1, 0x08(sp)
    sw      a2, 0x0C(sp)
    sw      v0, 0x10(sp)
    sw      v1, 0x14(sp)
    jal     SetGrottoSceneLayer
    nop
    lw      a1, 0x08(sp)
    lw      a2, 0x0C(sp)
    lw      v0, 0x10(sp)
    lw      v1, 0x14(sp)
    lw      ra, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x20


set_grotto_entrance_hook:
    addiu   sp, sp, -0x10
    sw      ra, 0x04(sp)
    sw      a0, 0x08(sp)
    sw      a1, 0x0C(sp)
    addu    a0, s0, $zero
    addu    a1, a3, $zero
    jal     SetGrottoEntranceIndex
    nop
    lw      a1, 0x0C(sp)
    lw      a0, 0x08(sp)
    lw      ra, 0x04(sp)
    jr      ra
    addiu   sp, sp, 0x10

override_respawn_params_hook:
    addiu   sp, sp, -0x20
    sw      ra, 0x04(sp)
    sw      a0, 0x08(sp)
    sw      a1, 0x0C(sp)
    sw      s0, 0x10(sp)
    sw      s1, 0x14(sp)
    sw      s2, 0x18(sp)
    sw      t6, 0x1C(sp)
    addu    a0, s0, $zero
    jal     OverrideRespawnPlayerParams
    nop
    lw      t6, 0x1C(sp)
    lw      s0, 0x10(sp)
    lw      s1, 0x14(sp)
    lw      s2, 0x18(sp)
    lw      a1, 0x0C(sp)
    lw      a0, 0x08(sp)
    lw      ra, 0x04(sp)
    sb      t6, 0x137B(s2)
    lh      v0, 0x00A4(s1)
    jr      ra
    addiu   sp, sp, 0x20
