ladder_cutscene:
    lbu   t4,1693(s0)           ; player->unk_6AD
    addi  t3,t4,-3              ; Cutscene = 3, CS item = 4
    bltz  t3,@@ladder_return    ; If not CS/CS item, continue as usual
    nop
    la    ra,0x803a3080         ; Else, continue at 0x8084a6e0 (load argument to LinkAnimation_Update)

@@ladder_return:                ; Original code
    lw    t8,1644(s0)
    jr    ra
    lui   at,0xffdf
