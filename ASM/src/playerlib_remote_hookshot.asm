PlayerHookPostlimbCheck:
    bnez    at,@@HookModelCheck    ; If enabled, use modeltype for postlimbdraw check
    nop                            ; Else, use item action
    lb      v0,321(s0)             ; Player IA
    li      at,16
    beq     v0,at,@@HookPostlimb
    nop
    li      at,17
    bne     v0,at,@@HookNotEquipped
    nop
    b       @@HookPostlimb
    nop
@@HookModelCheck:
    lb      v0,333(s0)             ; Player right hand model
    li      at,15                  ; Hookshot model
    beq     v0,at,@@HookPostlimb
    nop
@@HookNotEquipped:                 ; Not using Hookshot, no postlimbdraw activities
    lb      t4,2130(s0)            ; Player get item draw ID
    addi    ra, 0xdc               ; 0x8007bed4 (post Hookshot)
@@HookPostlimb:
    jr      ra                     ; 0x8007bdf8
    nop
