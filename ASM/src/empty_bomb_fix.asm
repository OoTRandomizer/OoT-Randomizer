;when the bomb instance in links hand is unloading, write the correct value for "Held Item" to denote the bomb is no longer in hand

empty_bomb_fix:
   ;displaced
   lw a0, 0x001C($sp)

   li     t0, 0x0100FE00     ;load value to write for no empty bomb
   lui    t1, 0x801E
   lui    t6, 0x801D
   lw     t2, 0x0018(sp)     ;load pointer to bomb instance from stack
   lb     t3, 0xAB72(t1)     ;load byte of item in hand
   lw     t4, 0xA0EC(t6)     ;load pointer of item in hand
   li     t5, 0x02           ;load item value of bomb
   bne    t3, t5, @@return   ;if item in hand is not a bomb, return
   nop
   bne    t2, t4, @@return   ;if bomb in hand doesnt match bomb exploding, return
   nop
   sw     t0, 0xAB70(t1)     ;store 0x0100FE00 to 801DAB70
   sb     r0, 0xAB74(t1)     ;store 0x00 to 801DAB74

@@return:
   jr     ra
   nop