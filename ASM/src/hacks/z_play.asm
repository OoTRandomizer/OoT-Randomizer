.headersize (0x80114dd0 - 0x00b8ad30)

;================================================================================
; Fixes crashing when too many subcameras spawn, because the main camera pointer
; gets set to NULL (Spirit Temple mirror room etc)
;================================================================================
; Replaces  bne a1,at,8009d248  (branch if camId not -1/NONE)
;           sll v0,a1,0x10
.org 0x8009d238                    ; in Play_ClearCamera
    jal   Play_ClearCameraAvoidMain
    nop
