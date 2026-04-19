PlayerFrozenElectrifiedMagicReset:
    addiu   sp,sp,4
    sw      ra,4(sp)
    li      t4,4                        ; MAGIC_STATE_METER_FLASH_2 (waiting for consume)
    la      t5,SAVE_CONTEXT
    lh      t6,5104(t5)                 ; gSaveContext.magicState
    bnel    t4,t6,@@MagicResetReturn    ; Reset if flash 2 state
    lw      ra,4(sp)
    jal     Magic_Reset                 ; Call vanilla magic reset
    nop
    lw      ra,4(sp)
@@MagicResetReturn:
    addiu   sp,sp,-4
    jr      ra
    li      a1,255                      ; Displaced

PlayerSetFaroreMagicState:
    li      t4,1            ; MAGIC_STATE_CONSUME_SETUP
    sh      t4,5104(v0)     ; gSaveContext.magicState
    jr      ra
    sw      t5,3720(v0)     ; Displaced
