deku_mouth_condition:
    lw      t5, 4(v1)               ; 0 = Adult, 1 = Child
    lb      t6, DUNGEONS_SHUFFLED
    or      t7, t5, t6
    beqz    t7, @@mouth_closed      ; If both adult and dungeons not shuffled, closed mouth.
    nop
    beqz    t6, @@mouth_open        ; If child and dungeons not shuffled, open mouth.
    nop
    lhu     t6, 0x0ED4(v1)          ; event_chk_inf[0]
    andi    t6, t6, 0x0010          ; "Showed Mido Sword & Shield"
    or      t6, t6, t5
    beqz    t6, @@mouth_closed      ; If both adult and haven't shown Mido the Sword and Shield, closed mouth.
    nop
@@mouth_open:
    jr      ra
    li      t7, 1
@@mouth_closed:
    jr      ra
    li      t7, 0
