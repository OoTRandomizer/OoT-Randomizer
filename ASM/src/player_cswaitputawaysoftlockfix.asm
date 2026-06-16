Player_CSWaitPutAwaySoftlockFix:   ; a1 = play
    addiu   sp,sp,-24
    sw      ra,16(sp)
    move    v0,zero             ; assume return false/no function flow change
    lw      a2,48(sp)           ; displaced, player
    move    a0,a2               ; displaced
    lh      t0,0xa4(a1)         ; scene id
    li      at,0x64             ; outside Ganon
    bne     at,t0,@@Return      ; skip if not outside
    ; add further scenes here if necessary, along with other conditions if needed
    lbu     t0,0x434(a0)        ; player csAction
    bnezl   t0,@@Return         ; if csAction is NONE, just return
@@StartCutscene:
    li      v0,1                ; else, return true/start cutscene by running function
@@Return:
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24
