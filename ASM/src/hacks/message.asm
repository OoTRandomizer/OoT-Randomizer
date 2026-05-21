.headersize(0x800D5EF0 - 0x00B4BE50)

.org 0x800DCE38
    ; Replaces jal     func_800DC838
    jal     grab_textbox_id

;================================================================================
; Fixes crashing when learning non-warp songs during Nayru's love when cutscenes
; are on and song playback enabled.
;================================================================================
; Replaces  li  t7,1      (msgCtx->stateTimer = 1)
.org 0x800debb8     ; in Message_DrawMain
    li  t7,2        ; Add one extra frame between Ocarina effect and Nayru killed
