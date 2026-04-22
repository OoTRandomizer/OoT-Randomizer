; Call C function for using item on D-pad
Player_CallUseDpadItem:
    addiu   sp,sp,-8
    sw      ra,(sp)
    jal     Player_UseDpadItem        ; return in v0: 1 if used D-pad item, else 0
    sw      v1,4(sp)                  ; needs to be saved
    beqz    v0,@@DidntUseReturn       ; if didn't use item, continue normal function
    lw      ra,(sp)
    b       @@DidUseReturn            ; else, go to 0x80832134 (end of calling function)
    addi    ra,0x74                   
@@DidntUseReturn:
    lw      v1,4(sp)                  ; restore for continue function
    move    a3,zero                   ; displaced
    li      a1,4                      ; displaced
@@DidUseReturn:
    jr      ra
    addiu   sp,sp,8
