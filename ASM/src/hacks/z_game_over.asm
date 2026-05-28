;================================================================================
; Fixes child Link getting adult sword equipped when dying
;================================================================================
; Replaces  lbu     v0,104(s3)
;           li      at,59
; .org 0x800e1854             ; in GameOver_Update
;     jal     GameOver_RestoreBButton
;     addi    ra,0x3c         ; We are skipping the entire original section to 0x800e1898

;================================================================================
; Fixes child Link getting adult sword equipped when dying
;================================================================================
; Replaces  lbu     v0,104(s3)
;           li      at,59
;           move    a0,s5
;           beq     v0,at,0x800e189c
.org 0x800e1854             ; in GameOver_Update
    jal     GameOver_RestoreBButton
    nop
    b       0x800e1898      ; We are skipping the entire original section
    nop

.org 0x800e1898
    move    a0,s5           ; gets trashed by the C function, restoring
