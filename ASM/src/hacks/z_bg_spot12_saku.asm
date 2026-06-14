.headersize (0x80b3d9c0 - 0x00eb90f0)

; Gerudo Fortress gate to GTG actor

;==================================================================================================
; Permanent open flag GTG gate: On gate actor init, if option is enabled, check if permanent
; GTG opened flag is set and if so, enter opened action
;==================================================================================================
; Replaces: lh      a1,28(s0)
;           lw      a0,36(sp)
;           jal     Flags_GetSwitch
;           andi    a1,a1,0x3f
.org 0x80b3da54     ; in BgSpot12Saku_Init
    jal     GTGGate_CheckPermOpen
    lh      a1,28(s0)       ; displaced
    beqz    v0,0x80b3da7c   ; If temp/perm flags not set, run non-open action
    nop
