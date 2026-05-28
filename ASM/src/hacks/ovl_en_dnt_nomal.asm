.headersize (0x80b4f150 - 0x00eca880)

;================================================================================
; Fix softlock when re-hitting slingshot game scrub target before receiving item
; (checks both vanilla checks + spawnedItem)
;================================================================================
; Replaces  lui     v0,0x8012
;           addiu   v0,v0,-23088
;           lw      t1,4(v0)
;           beqzl   t1,80b4f7d4
;           lw      ra,36(sp)
;           lhu     t2,3826(v0)
.org 0x80b4f6f0             ; in EnDntNomal_TargetWait
    jal     EnDntN_SlingshotFix
    nop
    beqzl   v0,0x80b4f7d4   ; go to return if not giving bag
    lw      ra,36(sp)
    b       0x80b4f714      ; else continue function
    nop
