.headersize (0x809087d0 - 0x00ca5f80)

; Torches overlay

;================================================================================
; Rotate flame collider of slanted torches
;================================================================================
; Rotate the flameCollider if X/Z rotated torch + set new light pos
; Replaces: lh      v1,28(s0)
;           sw      v0,472(s0)
.org 0x80908914             ; in ObjSyokudai_Draw
    jal     ObjSyokudai_CallRotateFlameCollider
    nop

; Don't update flameCollider position on actor update, set only once
; in ObjSyokudai_RotateFlameCollider for normal and slanted
; Replaces: jal     Collider_UpdateCylinder
.org 0x80908e7c
    nop
