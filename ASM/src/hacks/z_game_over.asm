;================================================================================
; Fixes child Link getting adult sword equipped when dying
;================================================================================
; Replaces  lbu     v0,104(s3)
;           li      at,59
.org 0x800e1854             ; in GameOver_Update
    jal     GameOver_RestoreBButton
    addi    ra,0x3c         ; We are skipping the entire original section to 0x800e1898

.org 0x800e1898
    move    a0,s5           ; gets trashed by the C function, restoring
