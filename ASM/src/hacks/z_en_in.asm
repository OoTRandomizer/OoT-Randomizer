.headersize (0x809c05a0 - 0x00d50720)

; Make Ingo say "I'll never let you leave this ranch" (vanilla text)
; when talking to him after winning the race (for overworld ER)
; Replaces: lui     v1,0x8012
;           addiu   v1,v1,-23088
;           lhu     a0,3798(v1)
;           andi    t7,a0,0x100
.org 0x809c0628
    jal     EnIn_TalkAfterEponaFix
    move    v0,zero         ; assume not post race
    bnezl   v0,0x809c0748   ; if post race, go to return
    li      v0,0x203c       ; set vanilla post race text
