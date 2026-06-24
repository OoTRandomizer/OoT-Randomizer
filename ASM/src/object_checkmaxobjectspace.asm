Object_CheckMaxObjectSpace:
    addiu   t1,t1,15        ; displaced
    and     v0,t1,at        ; displaced
    lw      t1,4(a0)        ; objectCtx space end
    sltu    at,v0,t1        ; next object start pointer < space end?
    beqzl   at,@@Return     ; if yes, return pointer (v0)
    move    v0,zero         ; if not - memory full, return NULL, let caller deal with it
@@Return:
    jr      ra
    nop
