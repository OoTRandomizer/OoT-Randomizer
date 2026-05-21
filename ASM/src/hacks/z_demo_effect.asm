.headersize (0x8092acc0 - 0x00cc8430)

;==================================================================================================
; Jabu: Kill Demo_Effect if "visited Big Octo" flag set (don't draw Zora's Sapphire on platform)
;==================================================================================================
; Replaces: sw     a1, 0x64(sp)
;           lh     v0, 0x1C(s0)
.org 0x8092ae48     ; in DemoEffect_Init
    jal    DemoEffect_KillAfterBigOcto
    sw     a1, 0x64(sp)     ; displaced

;==================================================================================================
; Override appearance of Zora's Sapphire spiritual stone inside Jabu
;==================================================================================================
; Increase the size of DemoEffect actor to store override
; Replaces: .d32 0x00000190
.org 0x8093019c
    .d32 0x000001C0

; Hook the function DemoEffect_DrawJewel
; Replaces: addiu   sp, sp, -0x78
;           sw      s3, 0x40(sp)
.org 0x8092e3f8
    j   DemoEffect_DrawJewel_Hook
    nop
DemoEffect_DrawJewel_AfterHook:
