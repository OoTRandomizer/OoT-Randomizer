.headersize (0x800110a0 - 0x00a87000)

;==================================================================================================
;                               Extended minimap changes on scene entry
;==================================================================================================

; Graveyard: Always show extended minimap
;   Replaces: lui     t9,0x8010
;           lw      t9,-29672(t9)
.org 0x8006bf88     ; in Map_InitData
    b       0x8006c064          ; Go directly to DMA request
    li      a3,20               ; Extended minimap index

; Gerudo Fortress: Make extended minimap depend on Gerudo Membership Card
; instead of freeing carpenters (switch on get item: see z_message)
;   Replaces: lhu     t1,3814(a2)
;           li      at,15
;           andi    t2,t1,0xf
;           bne     v1,at,8006c064
;           nop
;           li      a3,23
.org 0x8006c04c     ; in Map_InitData
    lw      v0,164(a2)          ; Check Gerudo Card flag (a2 saveCtx)
    lui     v1,0x40
    and     v0,v0,v1
    bnezl   v0,0x8006c064       ; If zero/no flag, no extended minimap
    li      a3,23               ; If flag, load extended minimap index
    nop

; Lake Hylia: Switch minimap on scene entry depending on water level (on switch toggle:
; see Lake Hylia water level function)
;   Replaces: lw      t4,-29704(t4)
;           lw      t5,164(a2)
;           and     t6,t4,t5
;           bnez    t6,8006c064
;           nop
;           b       8006c064
.org 0x8006bfd8     ; in Map_InitData
    lhu     t3,0x0EE0(a2)       ; Lake filled flag (a2 saveCtx)
    andi    t4,t3,0x0200
    bnez    t4,0x8006c064       ; If flag zero, not filled => load extended minimap
    nop
    b       0x8006c064
    li      a3,21               ; Extended minimap index
