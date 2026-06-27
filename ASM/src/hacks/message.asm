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

;================================================================================
; Repoint vanilla message character width table
;================================================================================
; This file is included by ASM/src/hacks.asm as hacks/message.asm.
; Do not add a jump hook for this feature: the vanilla Message_DrawText index math
; already does exactly what we need.  Only the table base used by the existing
; sFontWidths load is redirected to LANG_CHAR_WIDTHS.
;
; Original addressing pattern:
;   index = character * 4
;   load  = sFontWidths - (' ' * 4) + index
;
; Because ' ' == 0x20 and 0x20 * sizeof(f32) == 0x80, the replacement base is
; LANG_CHAR_WIDTHS - 0x80.

.headersize(0x800D5EF0 - 0x00B4BE50)

; Keep these local to hacks/message.asm.  addresses.asm is intentionally not used
; because it is for global runtime pointers rather than local z_message patch sites.
.definelabel MESSAGE_OPEN_TEXT_VRAM,        0x800DC838

.org MESSAGE_OPEN_TEXT_VRAM - 0x279C
    lui     at, hi(LANG_CHAR_WIDTHS - 0x80)

.org MESSAGE_OPEN_TEXT_VRAM - 0x278C
    lwc1    f16, lo(LANG_CHAR_WIDTHS - 0x80)(at)
