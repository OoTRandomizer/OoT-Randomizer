; Call C function for using item on D-pad
Player_CallUseDpadItem:
    addiu   sp,sp,-24
    sw      ra,16(sp)
    sw      v1,20(sp)                 ; needs to be saved
    sw      t3,24(sp)
    jal     Player_UseDpadItem        ; Return in v0: 1 if used D-pad item, else 0
    nop
    beqzl   v0,@@DidntUse             ; If didn't use item, continue normal function
    li      t0,0                      ; and return false (t0 because v0 used in caller)
    b       @@Return                  ; If used, return true
    li      t0,1                      ; = go to end of calling function
@@DidntUse:
    lw      v1,20(sp)
    lw      t3,24(sp)
    move    a3,zero                   ; displaced
    li      a1,4                      ; displaced
    lhu     a0,0(t3)                  ; displaced
@@Return:
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24
