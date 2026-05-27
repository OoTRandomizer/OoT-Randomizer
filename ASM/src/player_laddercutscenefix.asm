Player_LadderCutsceneFix:
    lbu   t4,1693(s0)                   ; player->unk_6AD
    addi  t3,t4,-3                      ; Cutscene = 3, CS item = 4
    bltzl t3,@@Return                   ; If not CS/CS item, continue as usual
    li    v0,0                          ; 0 for no branching
    li    v0,1                          ; Otherwise, 1 for branching
@@Return:
    lui   at,0xffdf                     ; displaced
    ori   at,at,0xffff                  ; displaced
    jr    ra
    and   t9,t8,at                      ; displaced
