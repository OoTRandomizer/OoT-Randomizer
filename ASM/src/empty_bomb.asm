;At the end of the bombs explosion it sets a bunch of variables if Link is still holding the bomb instance.
;This hooks into that check and sets three additional variables to prevent empty bomb
;This is NOT the same fix that was made in version 1.1 of the game.
;Doing it this way prevents the Bomb OI glitch that the OoT devs added in 1.1 and onwards.

empty_bomb:
   sw      t5, 0x066C(v0) ;displaced
   sb      r0, 0x141(v0)  ;Action Parameter 1
   sb      r0, 0x144(v0)  ;Action Parameter 2
   li      t6, 0xFE
   jr      ra
   sb      t6, 0x142(v0)  ;Last Held Item ID
