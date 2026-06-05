.headersize (0x80114dd0 - 0x00b8ad30)

;================================================================================
; Fixes crashing when too many subcameras spawn, because the main camera pointer
; gets set to NULL (Spirit Temple mirror room etc)
;================================================================================
; Replaces  sll     a1,a1,0x10
;           sra     a1,a1,0x10
;           sw      ra,20(sp)
;           move    a2,a0
;           li      at,-1
;           bne     a1,at,8009d248  (branch if camId not -1/NONE)
;           sll     v0,a1,0x10

.org 0x8009d224                     ; in Play_ClearCamera
    sw      ra,20(sp)               ; displaced
    jal     Play_ClearCameraAvoidMain
    move    a2,a0                   ; displaced
    beql    v0,t3,0x8009d274        ; camId MAIN (t3 = 1), skip to end function
    nop
    beq     v0,t4,0x8009d248        ; not MAIN/NONE (t4 = 2), remove pointer
    move    v0,t1                   ; restore v0 as t1
