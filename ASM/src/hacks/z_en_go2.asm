
.headersize (0x80b56910 - 0x00ed2040)

; Goron overlay (including Link Goron, Biggoron)

;================================================================================
; Biggoron: Set EnGo2->reverse variable when turning in Claim Check/receiving BGS
; to delay changing action function by one frame (see below; fixes interface bug)
;================================================================================
; Replaces: sb      t8,62(v0)
.org 0x80b5ae44     ; in EnGo2_SetGetItem
    sb      t8,510(s0)

;================================================================================
; Biggoron: In "idle" action function, if EnGo2->reverse is set, unset it and
; return without calling any functions further down (i.e. EnGo2_IsCameraModified)
;================================================================================
; Replaces: lbu     t6,513(s0)
;           li      at,1
.org 0x80b5a76c     ; in EnGo2_Action_80A46B40
    jal     EnGo2_BiggoronIdleClaimCheck
    lbu     t6,513(s0)      ; displaced
