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

;================================================================================
; Prevent all magic from getting consumed if received magic refill during spellcast
;================================================================================
; Replaces: lh      v0,5108(v1)
;           lb      a0,51(v1)
;           li      t9,10
;           slt     at,v0,a0
.org 0x800727f0     ; in Magic_RequestChange
    jal     Magic_SpellAddMagicTarget
    nop
    bnez    v0,0x80072824           ; skip vanilla add magic
    lh      v0,5108(v1)             ; displaced, magicCapacity

; If magicTarget = start magic due to getting magic refill during spell cast,
; don't consume 2 points of magic
; Replaces: bne     t7,v0,0x80072a08
;           nop
;           sh      t8,5104(v1)
;           lui     at,0x800f
.org 0x800729dc     ; in Magic_Update
    jal     Magic_SpellConsumeMagicTarget
    nop
    beqz    v0,0x80072a08        ; don't change magic state
    lb      v0,51(v1)            ; restore current magic to v0
