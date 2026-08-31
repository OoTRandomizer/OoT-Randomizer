.headersize(0x8006D8E0 - 0x00AE3840)

;=============================================================
; Move the small key counter horizontally if we have boss key.
;=============================================================

.org 0x8007594C
    ; Replaces addiu   t7, $zero, 0x001A
    ;          addiu   t8, $zero, 0x00BE
    jal     move_key_icon
    addiu   t7, $zero, 0x001A

.org 0x80075A38
    ; Replaces addiu   s2, $zero, 0x002A
    ;          addiu   t8, $zero, 0x00BE
    jal     move_key_counter
    addiu   s2, $zero, 0x002A

;=============================================================
;                   Custom item textures
;=============================================================
; Texture for transferring item from kaleidoscope to C button
; Replaces: lhu	    t7,590(a2)
;           sll	    t5,t7,0x2
;           addu	t6,t6,t5
;           lw  	t6,-29396(t6)
.org 0x80076840     ; Interface_Draw
    jal     Interface_GetCustomEquipIcon
    lhu	    a0,590(a2)      ; equipTargetItem
    move    t6,v0           ; save return value
    lw      a2,84(sp)       ; restore

; Replace load part of Interface_LoadItemIcon1 with custom C function
; Replaces: lui     at,0x1
;           ori     at,at,0x4f0
;           lui     t8,0x8012
;           addu    t8,t8,t0
;           addu    v0,v0,at
;           lw      t6,312(v0)
;           lbu     t8,-22984(t8)
;           lui     t1,0x7c
;           addiu   t1,t1,-12288
;           addiu   v1,v0,448
.org 0x8006fb8c     ; Interface_LoadItemIcon1
    lw      a0,48(sp)   ; play
    lw      a1,52(sp)   ; button
    lui     at,0x1
    ori     at,at,0x4f0
    addu    v0,v0,at
    addiu   v1,v0,448   ; interfaceCtx->loadQueue
    jal     Interface_LoadCustomItemIcon1
    sw      v1,40(sp)
    b       0x8006fbe0  ; to before osRecvMesg
    nop

; Replace load part of Interface_LoadItemIcon2 with custom C function
; Replaces: lui     at,0x1
;           ori     at,at,0x4f0
;           lui     t8,0x8012
;           addu    t8,t8,t0
;           addu    v0,v0,at
;           lw      t6,312(v0)
;           lbu     t8,-22984(t8)
;           lui     t1,0x7c
;           addiu   t1,t1,-12288
;           addiu   v1,v0,448
.org 0x8006fc3c     ; Interface_LoadItemIcon2
    lw      a0,48(sp)   ; play
    lw      a1,52(sp)   ; button
    lui     at,0x1
    ori     at,at,0x4f0
    addu    v0,v0,at
    addiu   v1,v0,448   ; interfaceCtx->loadQueue
    jal     Interface_LoadCustomItemIcon2
    sw      v1,40(sp)
    b       0x8006fc90  ; to before osRecvMesg
    nop

; Replace every Interface_Init button icon load
; Probably possible to improve
; Replaces: lui     t5,0x7c
;           slti    at,v1,240
;           beqz    at,800e1dd0
;           sll     t4,v1,0xc
.org 0x800e1da4     ; Interface_Init
    jal     Interface_LoadInitCustomItemIcon
    lw      a0,80(sp)       ; play
    b       0x800e1e90      ; jump beyond icon loading
    nop
