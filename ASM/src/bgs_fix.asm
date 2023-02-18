;Big Goron Fix
;Zero out the pointer to the actor that big goron is interacting with
;This change is done in the 1.2 version of the game

bgs_fix:
    sw       r0, 0x0118(a0) ;zero out pointer in goron instance
    addiu    ra, ra, 0x30   ;increment ra to simulate original branch
    jr       ra             ;return
    sw       t6, 0x0180(a0) ;displaced
