.headersize(0x80b55150- 0xed0880)

; Hack ObjMure3 Function that spawns the rupee circle (6 green + 1 red in the center)
; Hack the green rupee circle part
; Hook before calling Item_DropCollectible2 to set up our parameters
.org 0x80b553b8
; Replaces:
;   or      a0, s5, r0
    jal     obj_mure3_drop_params_hack

; Hook call to Item_DropCollectible2 when it's spawning the green rupees
.org 0x80b553c8
; Replaces:
;   jal     Item_DropCollectible2
    jal     Obj_Mure3_RupeeCircle_DropRupee

; Hack the red rupee part. This works because s0 should still have the loop index set at this point in the function.
.org 0x80b5540c
; Replaces:
;   or      a0, s5, r0
    jal     obj_mure3_drop_params_hack

; Hook call to Item_DropCollectible2 when it's spawning the red rupee
.org 0x80b55420
; Replaces:
;   jal     Item_DropCollectible2
    jal     Obj_Mure3_RupeeCircle_DropRupee

; replaces
;   or      a1, s6, r0
;   addiu   a2, r0, 0x4000
;.orga 0xED0AEC
;   jal     obj_mure3_hack
;   nop
; Hack the red rupee part
; replaces
;   lwc1    f8, 0x002c(s2)
;   addiu   a2, r0, 0x4002
;.orga 0xED0B48
;   jal     obj_mure3_redrupee_hack
;   lwc1    f8, 0x002c(s2)
