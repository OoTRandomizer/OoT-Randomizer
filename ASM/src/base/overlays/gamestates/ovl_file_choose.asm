; File select screen

.headersize(0x80803880 - 0x00BA12C0)

; Remove most of the behaviour in the OK/Cancel part of the file select.
; This is managed manually in file_select.c instead.

; On OK

; Validation sound effect
.org 0x80810C98
; Replaces jal     func_800C806C
    nop

; Load the game
.org 0x80810CA8
; Replaces addiu   t1, $zero, 0x0006
    addiu   t1, $zero, 0x0003

; Stop the menu music
.org 0x80810CB0
; Replaces jal     func_800C7684
    nop

; On Cancel

; Cancel sound effect
.org 0x80810CDC
; Replaces jal     func_800C806C
    nop

; Go back one screen
.org 0x80810CF4
; Replaces addiu   t4, t3, 0x0001
    addiu   t4, t3, 0x0000

; Pressing B

; Cancel sound effect
.org 0x80810D2C
; Replaces jal     func_800C806C
    nop

; Go back one screen
.org 0x80810D48
; Replaces addiu   t8, t7, 0x0001
    addiu   t8, t7, 0x0000

; Remove the Controls texture if needed so we can display Password locked in its place.

.org 0x80811AD8
; Replaces lh      v0, 0x4A30(a2)
;          slti    $at, v0, 0x0024
    jal     display_controls_texture
    lh      v0, 0x4A30(a2)
