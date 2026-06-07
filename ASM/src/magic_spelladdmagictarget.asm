Magic_SpellAddMagicTarget:          ; t0 is return value
    lh      at,5104(v1)             ; magicState
    lh      t0,5108(v1)             ; magicCapacity
    li      t9,9                    ; fill state
    bne     t9,at,@@CheckMagicStates ; If not fill state, compare current magicState
    li      t9,4
    lh      at,5106(v1)             ; if fill state from jar, instead check prevMagicState

@@CheckMagicStates:
    beq     t9,at,@@MagicAddFix     ; if state == magic meter 2 -> fix
    li      t9,2
    beq     t9,at,@@MagicAddFix     ; if state == consume -> fix
    li      t9,1
    bnel    t9,at,@@Return          ; if state == consume setup -> fix
    move    v0,zero                 ; else, return and do vanilla add magic

@@MagicAddFix:
    li      v0,1                    ; skip vanilla add magic after return
    sh      at,5104(v1)             ; Replace current with previous magic state (in case was fill)
    lb      a0,51(v1)               ; current magic
    addu    a0,a1                   ; current magic + amount = new preliminary magic
    slt     at,t0,a0
    bnezl   at,@@MagicFixTarget     ; if capacity < new magic:
    sb      t0,51(v1)               ; save capacity as current magic + fix target, else
    sb      a0,51(v1)               ; save new magic as current magic

@@MagicFixTarget:
    lh      t9,5112(v1)             ; magicTarget
    addu    t9,a1                   ; current target + amount = new preliminary target
    slt     at,t0,t9
    bnezl   at,@@Return             ; if capacity < new target:
    sh      t0,5112(v1)             ; save capacity as current target, else
    sh      t9,5112(v1)             ; save new target as current target

@@Return:
    lb      a0,51(v1)               ; restore
    slt     at,t0,a0                ; displaced
    jr      ra
    li      t9,10                   ; displaced


Magic_SpellConsumeMagicTarget:      ; Change state to stop magic consume if reached magic target (0 handled in vanilla)
    move    t5,v0                   ; Current magic
    li      v0,1                    ; Assume return will be 1 = change to STATE_METER_FLASH_1
    beql    t5,t7,@@Return          ; If current magic t5 = magicTarget t7: change state
    sh      t8,5104(v1)             ; -> set magic state to t8 = FLASH_1
    sltu    t4,t7,t5                ; If magicTarget < current magic, continue consume
    bnez    t4,@@KeepConsume        ; but if current magic < magicTarget - need to check below

    subu    t4,t7,t5                ; Check if target-2 = current magic (ok as delay)
    addiu   t4,-2                   ; In that case, player start magic = target, and lost -2 from magic consume
    bnez    t4,@@Return             ; If not, don't do anything with current magic
    sh      t8,5104(v1)             ; But change state in both cases, no more consume
    addi    t5,2                    ; If was -2: add removed 2 units of magic to restore magic
    b       @@Return
    sb      t5,51(v1)               ; Save new magic

@@KeepConsume:
    move    v0,zero                 ; Don't change magic state
@@Return:
    jr      ra
    lui     at,0x800f               ; displaced
