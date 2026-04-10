ladder_cutscene:
    lbu	t4,1693(s0)             ; player->unk_6AD
    li	t3,3                    ; Cutscene = 3
    bne	t4,t3,@@ladder_return   ; If not in cutscene, continue as usual
    nop
    la ra,0x803a3080            ; If in cutscene, continue at 0x8084a6e0 (load argument to LinkAnimation_Update)   

@@ladder_return:                ; Original code
    lw  t8,1644(s0)
    jr  ra
    lui at,0xffdf
