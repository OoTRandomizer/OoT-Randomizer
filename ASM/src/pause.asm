KaleidoScopeCall_Draw:
    addiu   sp, sp, 0xFFE8
    sw      ra, 0x0014(sp)
    lui     t6, 0x8012
    lw      t6, -0x4600(t6)
    lui     v0, 0x0001
    addu    v0, v0, a0
    lh      t7, 0x0190(t6)
    slti    at, t7, 0x0003
    bnel    at, zero, lbl_8009A15C
    lw      ra, 0x0014(sp)
    lhu     v0, 0x0934(v0)
    slti    at, v0, 0x0004
    bne     at, zero, new_condition_check
    slti    at, v0, 0x0008
    bne     at, zero, lbl_8009A134
new_condition_check:
    ori     at, zero, 0x14
    beq     at, v0, lbl_8009A134
    addiu   at, at, 1
    beq     at, v0, lbl_8009A134
    addiu   at, at, 2
    beq     at, v0, lbl_8009A134
    nop
lbl_8009A124:
    slti    at, v0, 0x000B
    bne     at, zero, lbl_8009A158
    slti    at, v0, 0x0013
    beq     at, zero, lbl_8009A158
lbl_8009A134:
    lui     t9, 0x8010
    lw      t9, -0x1B44(t9)
    lui     t8, 0x8010
    addiu   t8, t8, 0xE480
    bne     t8, t9, lbl_8009A158
    lui     t9, 0x8012
    lw      t9, -0x2FBC(t9)
    jalr    t9, ra
    nop
lbl_8009A158:
    lw      ra, 0x0014(sp)
lbl_8009A15C:
    addiu   sp, sp, 0x0018
    jr      ra
    nop
    nop
    nop

kaleidoScope_SwitchCaseHack:
    addiu   sp, sp, -0x0014
    sw      ra, 0x0010(sp)
    ori     at, at, 0x760
    addu    s0, s1, at
    lui     t8, hi(D_8082B25C_RELOCATED)
    addiu   t8, t8, lo(D_8082B25C_RELOCATED)
    sw      a1, 0(t8)
    lhu     t8, 0x01D4(s0)          ; loads pauseCtx->state into t8
    ori     at, zero, 20
    beq     t8, at, case20        ; jumps to case 20 function (not working yet but thats not the issue)
    addiu   at, at, 1               ; increment at to 21
    beq     t8, at, case21        ; jumps to case 21 function (not working yet but thats not the issue)
    addiu   at, at, 1               ; increment at to 22
    beq     t8, at, case22        ; jumps to case 22 (identical to case 17 but pauseCtx->state is referenced by other code and it being 17 causes the game over text to be drawn)
    addiu   t9, t8, 0xFFFD          ; replaced code from above
    sltiu   at, t9, 0x0011          ; replaced code from above
    beq     at, zero, returnFromSwitchHack    ; replaced code from above ; return section
    ori     v0, zero, 0
    sll     t9, t9, 0x0002          ; replaced code from above
    b       return_no_new_cases              ; returns back to @@return to continue if none of the new or modified cases are being called and returns to the original code
    nop
case20:
    jal     kaleidoScope_Case20
    or      a0, s1, zero
    b       returnFromSwitchHack        ; jumps to return section of kaleidoScope_Update
    ori     v0, zero, 0
case21:
    jal     kaleidoScope_Case21
    or      a0, s1, zero
    b       returnFromSwitchHack         ; jumps to return section of kaleidoScope_Update
    ori     v0, zero, 0
case22:
    b       returnFromSwitchHack              ; jumps to case 17
    ori     v0, zero, 2
return_no_new_cases:
    ori     v0, zero, 1
returnFromSwitchHack:
    ori     at, zero, 2
    lw      ra, 0x0010(sp)
    jr      ra
    addiu   sp, sp, 0x0014

KaleidoScope_DrawPages_ConditionHack:
    addiu   sp, sp, -0x0014
    sw      ra, 0x0010(sp)
    addiu   at, zero, 7
    beq     a0, at, KaleidoScope_DrawPages_ConditionHack_continue
    addiu   at, zero, 21
    beq     a0, at, KaleidoScope_DrawPages_ConditionHack_continue
    addiu   at, zero, 20
    beq     a0, at, KaleidoScope_DrawPages_ConditionHack_continue
    slti    at, a0, 0x0008
    bne     at, zero, KaleidoScope_DrawPages_ConditionHack_skip
    slti    at, a0, 0x0012
    beql    at, zero, KaleidoScope_DrawPages_ConditionHack_skip
    nop
KaleidoScope_DrawPages_ConditionHack_continue:
    b       KaleidoScope_DrawPages_ConditionHack_return
    ori     at, zero, 0
KaleidoScope_DrawPages_ConditionHack_skip:
    ori     at, zero, 1
    b       KaleidoScope_DrawPages_ConditionHack_return
KaleidoScope_DrawPages_ConditionHack_return:
    lw      ra, 0x0010(sp)
    jr      ra
    addiu   sp, sp, 0x0014

KaleidoScope_Draw_ContinuePromtHack:
    addiu   sp, sp, -0x0014
    sw      ra, 0x0010(sp)
    addiu   at, zero, 0x10
    or      s6, zero, a0
    beq     a0, at, KaleidoScope_Draw_Texture_Logic
    li      at, 0x14
    beq     a0, at, KaleidoScope_Draw_Texture_Logic
    li      at, 0x15
    beq     a0, at, KaleidoScope_Draw_Texture_Logic
    li      at, 0x11
    bnel    a0, at, KaleidoScope_Draw_ContinuePromtHack_skip
    lw      v1, 0x2C0(s0)
KaleidoScope_Draw_Texture_Logic:
    lui     t6, 0x8012
    lbu     t6, -0x4627(t6)
    lw      a0, 0x02C0(s0)
    sll     t8, t6, 2
    addu    a1, a1, t8
    ori     at, zero, 0x13
    slt     at, at, s6
    ori     s6, zero, 0
    beqz    at, KaleidoScope_TexUnchanged
    nop
    lui     a1, hi(ICON_STATIC_GAME_OVER)
    addiu   a1, a1, lo(ICON_STATIC_GAME_OVER)
    lw      a1, 0(a1)
    addiu   a1, a1, 0x2980
KaleidoScope_TexUnchanged:
    addiu   a2, zero, 0x0098
KaleidoScope_Draw_ContinuePromtHack_continue:
    b       KaleidoScope_Draw_ContinuePromtHack_return
    ori     at, zero, 0
KaleidoScope_Draw_ContinuePromtHack_skip:
    ori     at, zero, 1
KaleidoScope_Draw_ContinuePromtHack_return:
    lw      ra, 0x0010(sp)
    jr      ra
    addiu   sp, sp, 0x0014

kaleidoScope_Set_yOffset:
    addiu   sp, sp, -0x0014
    sw      ra, 0x0010(sp)
    slti    at, v0, 20
    beqz    at, kaleidoScope_Set_yOffset_skip ; skip setting y
    lui     at, 0x0001
    ori     at, at, 0x0760
    addu    t0, a0, at
    addiu   t7, zero, 0x0050
    sh      t7, 0x020A(t0)
kaleidoScope_Set_yOffset_continue:
    b       kaleidoScope_Set_yOffset_return
    ori     at, zero, 0
kaleidoScope_Set_yOffset_skip:
    ori     at, zero, 1
kaleidoScope_Set_yOffset_return:
    lw      ra, 0x0010(sp)
    jr      ra
    addiu   sp, sp, 0x0014

kaleidoScope_draw_select_hack:
    addiu   sp, sp, -0x0014
    sw      ra, 0x0010(sp)
    ori     at, zero, 0x0007
    beq     a1, at, kaleidoScope_draw_select_hack_continue
    ori     at, zero, 0x0014
    beq     a1, at, kaleidoScope_draw_select_hack_continue
    addiu   at, at, 0x0001
    beq     a1, at, kaleidoScope_draw_select_hack_continue
    nop
kaleidoScope_draw_select_hack_skip:
    b       kaleidoScope_draw_select_hack_return
    ori     at, zero, 1
kaleidoScope_draw_select_hack_continue:
    ori     at, zero, 0
kaleidoScope_draw_select_hack_return:
    lh      t7, 0x0238(t0)
    lui     t2, 0x8012
    lw      ra, 0x0010(sp)
    jr      ra
    addiu   sp, sp, 0x0014

ICON_STATIC_GAME_OVER:
.word 0x00000000

CFG_SAVE_AND_QUIT:
.byte 0x00
