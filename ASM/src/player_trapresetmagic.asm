Player_FrozenElectrifiedMagicReset:
    addiu   sp,sp,-8                    ; Extra -4 because Magic_Reset stores at (sp) without decreasing sp
    sw      ra,4(sp)
    li      t4,4                        ; MAGIC_STATE_METER_FLASH_2 (waiting for consume)
    la      t5,SAVE_CONTEXT
    lh      t6,5104(t5)                 ; gSaveContext.magicState
    bnel    t4,t6,@@MagicResetReturn    ; Reset if flash 2 state
    addiu   sp,sp,8
    jal     Magic_Reset                 ; Call vanilla magic reset
    nop
    lw      ra,4(sp)
    addiu   sp,sp,8
@@MagicResetReturn:                     ; If other state, ra is unchanged, don't need to load it
    jr      ra
    li      a1,255                      ; Displaced

Player_SetFaroreMagicState:
    li      t4,1            ; MAGIC_STATE_CONSUME_SETUP
    sh      t4,5104(v0)     ; into gSaveContext.magicState
    jr      ra
    sw      t5,3720(v0)     ; Displaced
