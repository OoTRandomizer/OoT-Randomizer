; Pause screen

.headersize(0x808137C0 - 0x00BB11E0)

; modified relocation entries
.org 0x8082FBFC
    .word 0x45012D1C ; should relocate hi(0x8082A388)
    .word 0x46012D24 ; should relocate lo(0x8082A388)
.org 0x8082F780
    .word 0x4500DB7C ; should relocate hi(0x80829E40)
    .word 0x4600DB84 ; should relocate lo(0x80829E40)

.org 0x8082389C
    nop
    jal       kaleidoScope_Set_yOffset
    nop
    bne       at, zero, 0x808238B0
    nop

.org 0x80822538
    jal     kaleidoScope_draw_select_hack
    nop
    bne     at, zero, 0x808226D4
    nop

.org 0x808264dc
    lui     a1, hi(0x8082a388)
    jal     kaleidoScope_SwitchCaseHack ; this branch is to a modified version of the pauseCtx->state switch case
    addiu   a1, lo(0x8082a388)
    beq     at, v0, 0x808287D8 ; jump to case 17 if v0 is 2
    nop
    beqz    v0, 0x80828BE4 ; jump to return if v0 is 0 else continue flow
    nop

.org 0x80820d94
    jal       KaleidoScope_DrawPages_ConditionHack
    nop
    bne       at, zero, 0x80821580
    nop
    nop
    nop
    nop

.org 0x8081E978
    jal     KaleidoScope_UpdatePrompt
    nop
    lw      ra, 0x001C(sp)
    jr      ra
    addiu   sp, sp, 0x0038

.org 0x80827568
    or      a0, s1, zero            ; loads playstate pointer into a0 before calling case 7 function
    jal     kaleidoScope_Case7      ; replcacement logic for the entirety of case 7
    nop
    b       0x80828BE4              ; jumps to return section of kaleidoScope_Update
    nop

.org 0x8082133C
    lui     a1, 0x8083
    jal     KaleidoScope_Draw_ContinuePromtHack
    lw      a1, -0x61C0(a1)
    bne     at, zero, 0x808214F0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
