.headersize (0x80114dd0 - 0x00b8ad30)

; Reduce the input needed to show the crash debugger to the first
; combination (L + R and Z).
; (To show instantly, nop 0x800af360 and 0x800af64c.)
; Replaces:     move    s0,s2
;               jal     osGetTime   0x800048c0
.org 0x800ae828     ; in Fault_WaitForButtonCombo
    b       @Fault_WaitButtons_Return
    nop

.org 0x800aea64     ; just label
    @Fault_WaitButtons_Return:
