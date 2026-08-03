CFG_MASK_AUTOEQUIP:
.byte 0x00
.align 4

player_save_mask:
;s1 = PlayState play*
    lb      t1, CFG_MASK_AUTOEQUIP
    beqz    t1, @@Return
    lw      t1, 0x1C44(s1) ;player*
    lbu     t7, 0x014F(t1) ;player->currentMask
    la      t8, SAVE_CONTEXT
    sb      t7, 0x3B(t8) ;saveContext->savedMask (custom field)

    ; displaced code
@@Return:
    lh      t8, 0xA4(s1)
    jr      ra
    lui     t1, 0x8012

; Restore a player's worn mask on player init, as well as check for grotto/GFF
; entrance to set display name timer
player_restore_mask:
    lb      t0, CFG_MASK_AUTOEQUIP
    beqz    t0, @@CheckGrottoText
    lhu     t0, 0x1C(a1) ;player->params
    andi    t0, t0, 0xF00
    sra     t0, t0, 0x8
    addiu   t1, r0, 0x1 ;Init mode that is set when player pulled or placed master sword
    beq     t0, t1, @@CheckGrottoText

    lbu     t0, 0x3B(s2) ;saveContext->savedMask (custom field)
    sb      t0, 0x014F(a1) ;player->currentMask

@@CheckGrottoText:     ; s1 play
    lbu     t0,CURRENT_GROTTO_ID ; Check if grotto for intro text
    li      at,0xFF
    bne     t0,at,@@SetTimer
    lui     t0,0x8011  ; Check if Great Fairy Fountain for intro text
    ori     t0,0xA5D0  ; nextEntranceIndex
    lw      t0,(t0)
    li      at,0x0588 ; Colossus
    beq     at,t0,@@SetTimer
    li      at,0x0578 ; HC
    beq     at,t0,@@SetTimer
    li      at,0x04C2 ; OGC
    beq     at,t0,@@SetTimer
    li      at,0x04BE ; DMC
    beq     at,t0,@@SetTimer
    li      at,0x0315 ; DMT
    beq     at,t0,@@SetTimer
    li      at,0x0371 ; ZF
    bne     at,t0,@@Return
@@SetTimer:
    li      t0,100
    la      t1,DISPLAY_GROTTO_TIMER
    sb      t0,(t1)
@@Return:
    la      t0, 0x800FE49C ;Links entry in `gKaleidoMgrOverlayTable`
    lw      t1, 0x0(t0) ;ovlTable->loadedRamAddr
    la      t2, 0x80834000 ;vram of function to jump to in Links overlay
    lw      t3, 0xC(t0) ;ovlTable->vramStart
    subu    t4, t2, t3 ; 0x80834000 - vramStart (offset into overlay)
    addu    t5, t4, t1 ; offset + loadedRamAddr (relocated address)
    jr      t5
    nop
