;==================================================================================================
; Mido
;==================================================================================================

.headersize(0x80AE2870 - 0xE61B50)
; TODO: remove
.headersize(0x80803880 - 0x00BA12C0)

; ==================================================================================================
; Change flags used to spawn Mido outside Deku and inside his house as child.
; Now requires the flags for showing Mido a sword/shield, Mido talking to you after Deku Tree's death,
; as well as either Obtained Zelda's Letter or beating Deku Tree to move Mido to his house.
; ==================================================================================================
.orga 0xE62948
    sw      a0, 0(sp)
    lh      v0, 0x00A4(a1)          ; Current Scene
    lui     v1, 0x8012              ; Save Context (upper half)
    li      at, 0x0055              ; Scene ID for Kokiri Forest
    addiu   v1, v1, 0xA5D0          ; Save Context (lower half)
    lhu     t0, 0x0ED4(v1)          ; event_chk_inf[0]
    andi    t1, t0, 0x0080          ; "Obtained Kokiri Emerald & Deku Tree Dead"
    andi    t2, t0, 0x0010          ; "Showed Mido Sword & Shield"
    lhu     t0, 0x0EDC(v1)          ; event_chk_inf[4]
    andi    t3, t0, 0x0001          ; "Obtained Zelda's Letter"
    lhu     t0, 0x0ED6(v1)          ; event_chk_inf[1]
    andi    t5, t0, 0x1000          ; "Spoke to Mido After Deku Tree's Death"
    or      t6, t1, t3              ; Composite of "Obtained Kokiri Emerald & Deku Tree Dead" and "Obtained Zelda's Letter"
    or      t7, t2, t5              ; Composite of "Showed Mido Sword & Shield" and "Spoke to Mido After Deku Tree's Death"
    bne     v0, at, @@midos_house   ; If the current scene isn't Kokiri Forest, move to the Mido's House section.
    li      t8, 0x1010              ; This is the hex value of t7 if both its flags are set.
    beqz    t6, @@success           ; If neither flag in t6 are set, spawn Mido.
    nop
    beq     t7, t8, @@failure       ; If both flags in t7 are set, don't spawn Mido.
    nop
@@success:
    jr      ra                      ; Return (spawn Mido).
    li      v0, 1
@@midos_house:
    li      at, 0x0028              ; Scene ID for Mido's House
    bne     v0, at, @@lost_woods    ; If current scene isn't Mido's House, move to the Lost Woods section.
    nop
    beqz    t6, @@failure           ; If neither flag in t6 are set, don't spawn Mido.
    nop
    bne     t7, t8, @@failure       ; If both flags in t7 aren't set, don't spawn Mido.
    nop
    lw      t4, 0x0004(v1)          ; Link's Current Age
    bnez    t4, @@success           ; If Link is a child, spawn Mido.
    nop
@@lost_woods:
    li      at, 0x005B              ; Scene ID for Lost Woods.
    beq     v0, at, @@success       ; If current scene is Lost Woods, spawn Mido.
    nop
@@failure:
    jr      ra                      ; Return (don't spawn Mido).
    move    v0, zero
; This block consisted of 41 instructions, below are nop instructions to make this 41 instructions long.
    nop
    nop
    nop
    nop

; ==================================================================================================
; Changes Mido's conversation flow in Kokiri. By default, he prioritizes talking about
; Deku Tree's death instead of asking for you to get a Sword and Shield. This doesn't
; matter normally but is a major issue for entrance randomizer.
; ==================================================================================================
.orga 0xE62630
    sh      zero, 0x01F8(a0)
    addiu   v1, v1, 0xA5D0
    lhu     t9, 0x0ED4(v1)      ; If this is t9, it saves setting it later for the next branch.
    li      t7, 0x0090          ; Mask for "Showed Mido Sword & Shield" and "Obtained Kokiri Emerald & Deku Tree Dead"
    and     t8, t9, t7
    bne_a   t8, t7, 0x00E62660
    nop
    b_a     0x00E626DC
    li      v0, 0x1045          ; Mido complaining about Deku Tree's death.
    nop
    nop
    nop
