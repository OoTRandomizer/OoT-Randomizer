; Change EnItem00 proximity check when it's an overridden silver rupee

; Actor stored in s0
; globalctx stored in s1
EnItem00_ProximityCheck_Hook:
; Save registers to the stack
    addiu   sp, sp, -0x30
    sw      a0, 0x10(sp)
    sw      a1, 0x14(sp)
    sw      a2, 0x18(sp)
    sw      s0, 0x1C(sp)
    sw      s1, 0x20(sp)
    sw      v1, 0x28(sp)
    sw      ra, 0x2C(sp)
; Set up args and call our hack
    or      a0, s0, r0
    jal     EnItem00_ProximityCheck_Hack
    or      a1, s1, r0
; Restore registers and return to function
    lw      a0, 0x10(sp)
    lw      a1, 0x14(sp)
    lw      a2, 0x18(sp)
    lw      s0, 0x1C(sp)
    lw      s1, 0x20(sp)
    lw      v1, 0x28(sp)
    lw      ra, 0x2C(sp)
    jr      ra
    addiu   sp, sp, 0x30

en_item00_update:
    addiu   sp, sp, -0x48
    j       en_item00_update_continue
    sw      s1, 0x20(sp)

EnItem00_Draw:
    addiu   sp, sp, -0x28
    j       EnItem00_Draw_Continue
    sw      ra, 0x14(sp)

EnItem00_Init:
   addiu   sp, sp, -0x40
   j        EnItem00_Init_Continue
   sw      s0, 0x18(sp)
