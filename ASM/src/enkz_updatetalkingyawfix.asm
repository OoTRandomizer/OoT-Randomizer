EnKz_UpdateTalkingYawFix:
    addiu   sp,sp,-24
    sw      ra,16(sp)
; First check if KZ is talking, if so update talkstate -> return
    lw      t9,80(sp)       ; talkstate pointer
    lh      t0,0(t9)        ; talkstate
    lw      t9,92(sp)       ; updateTalkState function
    beqz    t0,@@CheckYaw   ; if talkstate not idle, update talkstate
    move    a0,s1           ; play

    jalr    t9
    move    a1,s0           ; actor
    lw      t9,80(sp)       ; talkstate pointer
    sh      v0,0(t9)        ; save returned talkstate
    b       @@Return
    move    v0,zero         ; don't continue caller function

; Else check KZ-player yaw and if OK, set attention enabled flag + run GetScreenPos
@@CheckYaw:
    addiu   a0,s0,8         ; actor home pos
    lw      t0,7236(s1)     ; player address (s1 play)
    jal     Math_Vec3f_Yaw  ; get yaw
    addiu   a1,t0,36        ; player world pos

    mtc1    v0,$f4          ; yaw result from function
    cvt.s.w $f4,$f4
    lh      t7,182(s0)      ; actor shape rot
    mtc1    t7,$f8
    cvt.s.w $f8,$f8
    sub.s   $f0,$f4,$f8     ; yaw - shaperot y
    abs.s   $f0,$f0         ; absolute value of difference
    lui     at,0x44e3       ; 1820.0f
    addiu   at,0x8000
    mtc1    at,$f2
    c.lt.s  $f2,$f0
    bc1f    @@SetAttention  ; if yaw diff < 1820, set attention enabled flag
    lw      t1,4(s0)        ; actor flags
    li      at,-2           ; else, unset attention enabled actor flag
    and     t1,t1,at
    sw      t1,4(s0)
    b       @@Return
    move    v0,zero         ; don't continue caller function

@@SetAttention:
    ori     t1,t1,1
    sw      t1,4(s0)        ; save set attention flag
    li      v0,1            ; continue caller function
    addiu   a3,sp,64        ; displaced, 40 + extra 24
    addiu   a2,sp,66        ; displaced, 42 + extra
    move    a1,s0           ; displaced
    jal     Actor_GetScreenPos
    move    a0,s1

@@Return:
    lw      ra,16(sp)
    jr      ra
    addiu   sp,sp,24
