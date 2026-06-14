.headersize (0x80a8f100 - 0x00e11a40)

; Gerudo white clothes guards

;==================================================================================================
; Permanent open flag GTG gate: In gate guard check for card function, if option is enabled,
; if permanent GTG open flag is set, do not offer talk
;==================================================================================================
; Replaces: lui     t6,0x8010
;           lui     t7,0x8012
;           lw      t7,-22924(t7)
;           lw      t6,-29624(t6)
.org 0x80a8fca8     ; in EnGe1_CheckForCard_GTGGuard
    jal     EnGe1_GTGCheckPermGateOpen
    nop
    bnez    v0,0x80a8fcf8       ; Go to return in this function if perm flag set
    nop

;==================================================================================================
; Permanent open flag GTG gate: On opening GTG gate, if option is enabled, set permanent GTG
; open scene flag (flag 4)
;==================================================================================================
; Replaces: jal     Flags_SetSwitch
;           lw      a0,28(sp)
.org 0x80a8f9f8     ; in EnGe1_Open_GTGGuard
    jal     EnGe1_GTGSetPermGateOpen
    lw      a0,28(sp)           ; displaced
