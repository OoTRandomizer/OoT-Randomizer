; Hook to c function to drop our collectible for beehives
; put actor in a0
; put current params into a1.
obj_comb_hook:
    or      a1, a2, r0
    jal     obj_comb_drop_collectible
    or      a0, r0, a3 ; copy actor point from a3 to a0.
    lw      ra, 0x0014(sp)
    jr      ra
    addiu   sp, sp, 0x20


; Hook to c function to draw beehive textures
; Left here if we ever want to do beehive textures
;ObjComb_Draw_Hook:
;    addiu   sp, sp, -0x30
;    sw      ra, 0x001C(sp)
;    sw      s0, 0x0014(sp)
;    sw      s1, 0x0018(sp)
;    sw      a0, 0x0020(sp)
;    sw      a1, 0x0024(sp)
;
;    jal     ObjComb_Draw_Hack
;    nop
;
;    lw      s1, 0x0018(sp)
;    lw      s0, 0x0014(sp)
;    lw      a0, 0x0020(sp)
;    lw      a1, 0x0024(sp)
;    lw      ra, 0x1C(sp)
;    addiu   sp, sp, 0x30

; Replaced code
;    sw      s1, 0x0018(sp)
;    jr      ra
;    sw      s0, 0x0014(sp)
