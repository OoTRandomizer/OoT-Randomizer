Player_PostLimbHookshotCheck:      ; at = REMOTE_HOOKSHOT_ENABLED setting
    bnez    at,@@HookModelCheck    ; If enabled, use modeltype for postlimbdraw check
    lb      v0,321(s0)             ; Else, use item action. Player IA
    li      at,16                  ; Hookshot
    beq     v0,at,@@Return
    li      at,17                  ; Longshot
    bnel    v0,at,@@HookNotEquipped
    nop
    b       @@Return
    li      v0,1                   ; Using Hookshot
@@HookModelCheck:
    lb      v0,333(s0)             ; Player right hand model
    li      at,15                  ; Hookshot model
    beql    v0,at,@@Return
    li      v0,1                   ; Using Hookshot, continue heldActor etc check
@@HookNotEquipped:
    li      v0,0                   ; Not using Hookshot, no postlimbdraw activities
@@Return:
    jr      ra
    lb      t4,2130(s0)            ; displaced (player get item draw ID)
