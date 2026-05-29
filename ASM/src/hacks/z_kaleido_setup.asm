.headersize (0x8005B860 - 0xAD17C0)

; Check for held start button after unpausing to frame advance
; z_kaleido_setup.c, KaleidoSetup_Update, replaces the existing start button branch
; Replaces
;   addiu   $at, $zero, 0x1000
;   lui     a0, 0x8012
;   andi    t0, t9, 0x1000
;   bne     t0, $at, lbl_8005BA74
.org 0x8005B994
    jal     KaleidoSetup_Update_HasPressedStart_Hook
    nop
    nop
    beqzl   v0, DoNotOpenPauseMenu
.org 0x8005BA74
DoNotOpenPauseMenu:

.headersize 0