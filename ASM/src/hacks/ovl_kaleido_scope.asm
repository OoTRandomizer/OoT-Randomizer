.headersize (0x808137c0 - 0x00bb11e0)

; Prevent magicFillTarget from getting overwritten if dying
; during refill (game over respawn)
; Replaces: lb  t7,51(t1)
;           sh  zero,5156(t1)
;           sh  zero,5104(t1)
;           sh  zero,5106(t1)
.org 0x80828890         ; in KaleidoScope_Update
    jal     Kaleido_GameOverFillMagic
    lb      t7,51(t1)           ; displaced
    bnez    v0,0x808288a8       ; skip zero fill target
    sh      zero,5106(t1)
