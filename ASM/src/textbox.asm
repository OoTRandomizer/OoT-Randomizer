get_name_char_1:
   addiu sp, sp, -0x10
   sw    ra, 0x08 (sp)

   jal   get_name_char
   addi  a0, s3, -1

   ori   t2, v0, 0
   lw    ra, 0x08 (sp)
   addiu sp, sp, 0x10


get_name_char_2:
   addiu sp, sp, -0x10
   sw    ra, 0x08 (sp)

   jal   get_name_char
   ori   a0, s2, 0

   ori   s0, v0, 0
   lw    ra, 0x08 (sp)
   addiu sp, sp, 0x10


; a0 = char index into name
get_name_char:
   li    t0, PLAYER_NAME_ID
   lbu   t0, 0x00 (t0)

   bnez  t0, @@coop_player_name
   nop

   li    t0, SAVE_CONTEXT
   add   t0, t0, a0
   lbu   v0, 0x24 (t0)
   b     @@return
   nop

@@coop_player_name:
   sll   t0, t0, 3
   li    v0, PLAYER_NAMES
   add   t0, t0, v0
   add   t0, t0, a0
   lbu   v0, 0x00 (t0)

@@return:
   jr    ra
   nop


reset_player_name_id:
   ; displaced code
   lw    s6,48(sp)
   lw    s7,52(sp)
   lw    s8,56(sp)

   li    t0, PLAYER_NAME_ID
   sb    zero, 0x00 (t0)

   jr    ra
   nop
