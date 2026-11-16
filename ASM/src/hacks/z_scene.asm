.headersize (0x80114dd0 - 0x00b8ad30)

; Object load: Add check to ensure that new object to be loaded
; fits within object context space, else return NULL
; Replaces  addu    t1,t4,t0
;           addiu   t1,t1,15
;           and     v0,t1,at
.org 0x8008178c     ; in func_800982FC
    jal     Object_CheckMaxObjectSpace
    addu    t1,t4,t0        ; displaced
    lw      ra,12(sp)       ; ra is already saved by another hack, but not saved in vanilla func_800982FC
