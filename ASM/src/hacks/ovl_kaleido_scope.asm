
.headersize (0x808137c0 - 0x00bb11e0)

; Prevent magicFillTarget from getting overwritten if dying
; during refill (game over respawn)
; Replaces: sh	zero,5104(t1)
;           sh	zero,5106(t1)
.org 0x80828898         ; in KaleidoScope_Update
    jal     Kaleido_GameOverFillMagic
    sh	    zero,5106(t1)       ; displaced
