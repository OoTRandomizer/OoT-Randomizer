.headersize(0x808301C0  - 0x00BCDB70)
;==================================================================================================
; hooks new check function for low hp music hack
;==================================================================================================

.org 0x80846ACC
    ; replaces
    ;addiu   t5, $zero, 0x0001          # t5 = 00000001
    ;lw      v0, 0x1D20(t4)             # 00001D20
    ;beql    v0, $zero, lbl_80846AF0
    ;lw      t6, 0x0028($sp)
    ;sb      t5, 0x0027($sp)
    ;lwc1    $f0, 0x008C(v0)            # 0000008C
    ;jal     func_800C6E48
    ;sqrt.s  $f12, $f0

    jal update_seq_mode_hook
    lw a0, 0x28(sp)
    li at, 0xFF
    beq v0, at, @@DontSetSeqMode
    nop
    sb v0, 0x27(sp)
    
@@DontSetSeqMode:
    nop
    nop

.org 0x80837428
    ; replaces
    ; jal     0x800C7684
    jal      func_800F6964

