; Manipulates the save context language bit based
; on the segment value for the requested text ID.
; Message lookup is moved here from the vanilla
; branches.
; t6 used for branching to JP/EN file loading
; in parent function func_800DC838 at VRAM 0x800DCB68
; 0 == JP
; 1 == EN
set_message_file_to_search:
    ; displaced code
    lhu     a1, 0x0046($sp)
    lw      a0, 0x0040($sp)

    ; Saved by vanilla code prior to jump to
    ; message lookup function. Called here so
    ; we can safely store $ra.
    sw      t0, 0x002C($sp)

    ; Message lookup saves to the stack without
    ; changing the stack pointer. Save to an
    ; unused variable to avoid changing the stack.
    or      t4, $zero, $ra

    ; call JP message lookup function exclusively
    ; since the JP/EN tables are merged.
    jal     0x800D69EC
    nop

    ; a1 contains the segment/offset word, formatted as
    ; ssoooooo
    ; where "s" is the segment and "o" is the offset.
    ; Vanilla crashes on a failed text lookup already,
    ; so we don't need to worry about bad values.
    srl     t0, a1, 0x18
    andi    t0, t0, 0x08
    sltiu   t6, t0, 0x0001

    or      $ra, $zero, t4
    jr      $ra
    nop

load_correct_message_segment:
    ; displaced code
    lbu     t6, 0x0002(v1)
    lw      a1, 0x0004(v1)

    ; shift out the offset bits
    srl     a2, a1, 0x18
    sll     a2, a2, 0x18

    ; Remaining code from func_800D69EC since
    ; it doesn't save $ra
    lw      a1, 0x0004(v1)
    addiu   v0, a0, 0x2200
    sb      t6, 0x0008(v0)
    lw      a3, 0x000C(v1)
    subu    t7, a1, a2
    addiu   v1, v1, 0x0008
    subu    t8, a3, a1
    sw      t7, 0x0000(v0)
    jr      $ra
    sw      t8, 0x0004(v0)
