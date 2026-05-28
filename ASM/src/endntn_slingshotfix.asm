EnDntN_SlingshotFix:
    la      t0,SAVE_CONTEXT
    lw      t1,4(t0)                    ; Link age
    beqz    t1,@@DontGive               ; If adult, don't try to give
    lhu     t2,3826(v0)                 ; Bullet Bag received getiteminf
    andi    t3,t2,0x2000                ; Item received?
    bnez    t3,@@DontGive               ; If received, don't try to give it again
    lb      t2,615(s0)                  ; EnDnNomal->spawnedItem
    beqzl   t2,@@Return                 ; If not already spawned item,
    li      v0,1                        ; give it
@@DontGive:
    li      v0,0                        ; Adult or already got item
@@Return:
    jr      ra
    nop
