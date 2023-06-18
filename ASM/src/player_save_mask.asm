CFG_MASK_AUTOEQUIP:
.byte 0x00
.align 4

player_save_mask:
    lb      t0, CFG_MASK_AUTOEQUIP
    beqz    t0, @@return
    lhu     t0, 0x1C(a1) ;player->params
    andi    t0, t0, 0xF00
    sra     t0, t0, 0x8
    addiu   t1, r0, 0x1 ;Init mode that is set when player pulled or placed master sword
    beq     t0, t1, @@return

    lbu     t0, 0x3B(s2) ;saveContext->savedMask (custom field)
    sb      t0, 0x014F(a1) ;player->currentMask
@@return:
    la      t0, 0x800FE49C ;Links entry in `gKaleidoMgrOverlayTable`
    lw      t1, 0x0(t0) ;ovlTable->loadedRamAddr
    la      t2, 0x80834000 ;vram of function to jump to in Links overlay
    lw      t3, 0xC(t0) ;ovlTable->vramStart
    subu    t4, t2, t3 ; 0x80834000 - vramStart (offset into overlay)
    addu    t5, t4, t1 ; offset + loadedRamAddr (relocated address)
    jr      t5
    nop
