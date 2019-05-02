init:
    addiu   sp, sp, -0x18
    sw      ra, 0x10 (sp)

    jal     c_init
    nop

<<<<<<< HEAD
    ; Accept86 DMA in working NAVI - not needed anymore? nows just extended rom for texts
    ;lui a1, 0x0349
    ;lui a0, 0x8041
    ;jal 0x80000DF0          ;DMALoad JAL 0x80000DF0
    ;lui a2, 0x0001          ; TBD make sure its the right size - Texts don't have to be loaded in
    
    ;jal     working_navi_ExtendedInit ;Now done on saveload-hook instead
    ;nop
    
    
    ; Displaced code - from before the hook
=======
    ; Displaced code
>>>>>>> origin/HEAD
    lui     v0, 0x8012
    addiu   v0, v0, 0xD2A0
    addiu   t6, r0, 0x0140
    lui     at, 0x8010
    sw      t6, 0xE500 (at)

    lw      ra, 0x10 (sp)
    jr      ra
    addiu   sp, sp, 0x18


Static_ctxt_Init:
    li      t0, RANDO_CONTEXT
    sw      t0, 0x15D4(v0)
    jr      ra    
    ; Displaced code
    li      v0, 0x15C0
