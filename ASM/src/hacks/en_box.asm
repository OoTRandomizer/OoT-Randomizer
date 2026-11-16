.headersize (0x80868750 - 0x00c06030)

; Call function to load extra object if neeeded for a trap.
; Replaces  move    s0,a0
;           move    s1,a1
;           sw      ra,44(sp)
.org 0x808687f4     ; in EnBox_Init
    sw      ra,44(sp)
    jal     EnBox_CallLoadObject
    move    s0,a0
