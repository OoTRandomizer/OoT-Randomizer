.headersize(0x80b4f150 - 0x00eca880)

;================================================================================
; Fix softlock when re-hitting slingshot game scrub target before receiving item
;================================================================================
; Replaces  lhu     t2,3826(v0)
;           andi    t3,t2,0x2000
.org 0x80b4f704             ; in EnDntNomal_TargetWait
    jal     EnDntN_SlingshotFix
    lb      t2,615(s0)      ; EnDnNomal->spawnedItem
