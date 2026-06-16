EnIn_TalkAfterEponaFix:
    lui     t1,0x8012
    lhu     t1,-17974(t1)   ; race state flags
    li      at,6            ; post race win state
    andi    t1,t1,0xf
    beql    t1,at,@@Return  ; return 1 if post race
    li      v0,1            ; else, continue and run displaced
    lui     v1,0x8012       ; displaced
    addiu   v1,v1,-23088    ; displaced
    lhu     a0,3798(v1)     ; displaced
    andi    t7,a0,0x100     ; displaced
@@Return:
    jr      ra
    nop
