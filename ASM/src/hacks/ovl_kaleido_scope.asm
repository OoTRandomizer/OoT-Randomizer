
.headersize (0x808137c0 - 0x00bb11e0)

; Load custom item name panel
; Replaces: addu    a1,t4,t5
;           jal     DmaMgr_RequestSync
;           sw      v0,28(sp)
.org 0x80822e70     ; KaleidoScope_UpdateNamePanel
    move    a0,a3   ; play
    jal     KaleidoScope_LoadCustomName
    sw      v0,28(sp)

; Don't grey ITEM_SOLD_OUT menu item texture due to age (for Navi bell)
; Replaces: lui     v0,0x8083
;           addu    v0,v0,v1
;           lbu     v0,-25188(v0)
.org 0x80826608     ; KaleidoScope_Update
    lui     v0,0x8083
    jal     KaleidoScope_CheckAgeReqItemScreen
    addiu   v0,v0,-25188            ; gItemAgeReqs
