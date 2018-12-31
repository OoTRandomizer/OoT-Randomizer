;==========================================================================================================
; Hacks to make Malon fast, and allow you to always get her item at the vines, even if you've rescued Talon
;==========================================================================================================

; 0xD7E344 starts a function that checks if Malon should spawn
;   + 0x54 is after credits and age have been checked
; at this point, we have the following:
;   a0 = pointer to the save context
;   a1 = pointer to the global context
;   a2 = 3
;   a3 = 1
;   v0 = not sure, but it's checked to be equal to 3 in the original code, probably has to do with credits
;   v1 = the current scene number
; the function has pushed nothing to the stack (so nothing needs to be restored)
; we are expected to return 1 if Malon should spawn, and 0 if she should not

.org 0xD7E398
                                ; this is the state we need for Malon to move to Lon Lon Ranch
    lhu  t1,0x0ed6(a0)          ; this half holds both the following flags
    andi t0,t1,0x10             ; t0 = "Talon has fled castle"
    andi t1,t1,0x04             ; t1 = "Obtained Malon's Item"
    or   t0,t0,t1               ; t0 = combination of the flags
    li   t1,0x14                ; t1 = 0x14 which is the value if both flags are set

@@hyrule_check:                 ; she should spawn at castle until Talon has fled and Item has been given
    li   at,0x5f                ; at = 0x5f (Hyrule Castle)
    bne  at,v1,@@lon_lon_check  ; if not in Hyrule Castle, try Lon Lon instead
    nop
    beq  t0,t1,@@lon_lon_check  ; if Talon and Item, try Lon Lon instead
    nop
    li   v0,1
    jr   ra                      ; return true
    nop

@@lon_lon_check:                ; she should spawn at Lon Lon only once Talon has fled and Item has been given
    bne  a2,v0,@@return_false   ; this test is in the original code, it's probably for the credits
    li   at,0x63                ; at = 0x63 (Lon Lon Ranch)
    bne  at,v1,@@return_false   ; if not in Lon Lon Ranch, return false
    lw   t2,0x10(a0)            ; t2 = is night time
    bnez t2,@@return_false      ; Malon does not spawn at Ranch at night
    nop
    bne  t0,t1,@@return_false   ; make sure Talon has fled and Item has been given
    li   v0,1
    jr   ra                     ; return true
    nop

@@return_false:
    li  v0,0
    jr ra                       ; return false
    nop


; 0xD7E110 starts a function that decides which text id Malon should use when spoken to
;   + 0x50 is after ocarina check and song check
; at this point, we have the following:
;   a0 = pointer to the global context
;   v1 = pointer to the save context
; the function needs to restore the stack and return pointer before returning
; we are expected to return a text id

.org 0xD7E160
    lh  t0,0xA4(a0)     ; t0 = current scene number
    li  at,0x63         ; at = 0x63 (Lon Lon Ranch)
    bne at,t0,@@not_in_ranch ; if not in Lon Lon, she's in Hyrule Castle
    li  v0,0x2049       ; v0 = 0x2049 ('... Let's sing together.')
    b   @@return
    nop

@@not_in_ranch:
    lhu  t1,0x0ed6(v1)  ; this half holds the following flag
    andi t1,t1,0x04     ; t1 = "Obtained Malon's Item"
    bnez t1,@@return    ; if we haven't obtained the item, give the item
    li  v0,0x2044       ; v = 0x2044 'Set the egg to C to incubate it...'
    li  v0,0x2043       ; v = 0x2043 '... Would you mind finding my dad? ... <gives item>'

@@return:
return_from_the_other_function:
    lw  ra,20(sp)
    addiu   sp,sp,24    ; restore stack
    jr  ra              ; return v0 (whatever text id was chosen)
    nop



; 0xD7E818 is a function that sets a value in Malon's actor that makes Link get the item from her (ev0)
;   + 0x78 is where the flag/scene checks take place
; at this point, we have the following:
;   a0 = pointer to the Malon actor
;   a2 = pointer to the global context
;   t1 = current scene number
;   at = 0x5f (Hyrule Castle)
;   v0 = pointer to save context

.org 0xD7E890
    nop                         ;bne     t1,at,@@not_hyrule  ; if scene is not Hyrule Castle
    addiu   v0,v0,0xa5d0        ; v0 = 0x8012a5d0 # save context
    lhu     t2,0x0ed6(v0)       ; this byte holds the two flags below
    andi    t3,t2,0x10          ; t3 = "Talon has fled castle"
    b       @@safe              ; skip code that may have reallocations
    andi    t2,t2,0x04          ; t2 = "Obtained Malon's Item"

@@unsafe:
    jal     0x00020eb4
    nop
    nop
    nop
    lui     v0,0x8012
    addiu   v0,v0,0xa5d0

@@safe:
    li      t3,0x14             ; t3 = 0x14 which is the value if both flags are set
    lui     t6,0x8010
    or      t2,t2,t3            ; t2 = combination of the flags
    bne     t2,t3,ev0_return    ; check that both flags are true to continue this path
    lh      t9,472(a0)

@@not_hyrule:
    li      t6,0x01
    lb      t7,0x0EDE(v0)       ; check learned song from malon flag
    and     t8,t6,t7            ; t8 = "Has Epona's Song"
    bnezl   t8,ev0_return       ; return if we have Malon's song

.org 0xD7E920
ev0_return:


;
; ; Replaces:
; ;   addiu v0,v0,0xa5d0
; .org 0xD7E760
;     lw    t8,68(sp)         ; t8 = global context
;
; ; Replaces:
; ;   lhu   t8,3798(v0)
; .org 0xD7E76C
;     lh    t8,0xA4(t8)       ; t8 = current scene number
;
; ; Replaces:
; ;   andi  t9,t8,0x10
; ;   beqz  t9,ev_egg
; .org 0xD7E778
;     li    t9,0x5f           ; t9 = 0x5f (Hyrule Castle)
;     beq   t8,t9,ev_egg      ; jump if the scene is Hyrule Castle
;
; ; Replace:
; ;   lw  t1,164(v0)
; .org 0xD7E788
;     lw  t1,0xA674(v0)       ; t1 = quest status
;
; .org 0xD7E7A0
; ev_egg:


; This is the hook to change Malon's event ev1
; See malon_extra.asm for description of what this is changing
; Replaces:
;   lui   t2,0x8012
;   lhu   t2,-19290(t2)
;   andi  t3,t2,0x40
;   beqzl t3,@@return_block
;   lw    ra,28(sp)
;.org 0xD7EA48
;    lw    a1,44(sp)         ; a1 = pointer to the global context
;    jal   malon_ev1_hack    ; run the extra checks
;    nop                     ; Note that malon_ev1_hack will be able to return
;    nop                     ; to the return address of the current function
;    nop                     ; (fixing the stack appropriately)




; 0xD7E670 is Malon's initialization function
; the original check sets event to cb0 if Talon has fled, or Epona's Song is owned, and sets cb1 otherwise
; instead, we will check if we are in Hyrule castle, or Epona's song is owned, for event cb0
; note that we need to be insainly careful not to change any instructions that may be reallocated,
; or else it would cause issues and other changes would need to be made

.org 0xD7E76C
    lw      t8,68(sp)           ; t8 = global context
    lui     t3,0x809f
    lui     t0,0x8010
    lh      t8,0xA4(t8)         ; t8 = current scene number

    lb      t1,0x0EDE(v0)
    ;lw      t1,164(v0)          ; t1 = quest status

    addiu   t3,t3,4392          ; t3 = 0x809f1128 ( ev0 )

    li      t0,0x01
    ;lw      t0,-29660(t0)       ; t0 = malon's song mask

    move    a0,s0               ; a0 = actor pointer to set up function call
    lui     t4,0x809f
    addiu   t4,t4,4840          ; t4 = 0x809f12e8 ( ev1 )
    and     t2,t0,t1            ; t2 = "Has Malon's Song"
    bnez    t2,@@set_ev0        ; if "Has Malon's Song", set event to ev0
    li      t9,0x5f             ; t9 = 0x5f (Hyrule Castle)
    bne     t9,t8,set_ev1       ; otherwise if not in Hyrule Castle, set event to ev1
@@set_ev0:
    sw      t3,384(s0)          ; write f_9f1128 to actor + 0x180

.org 0xD7E7B8
set_ev1:


; Replaces
; lw  t6,-29660(t6)
; lw  t7,164(v1)
.org 0xD7E140
    li  t6,0x01
    lb  t7,0x0EDE(v1) ; check learned song from malon flag

.org 0xD7EBBC
    jal override_epona_song ;bne v0,at,loc_0x00000408 ; if v0? == 7 then: Return // if preview is not done

.org 0xD7EC1C
    nop     ; bne t8,at,loc_0x00000488 ; if t8 != 3 then: Return // if song not played successfully
    li t1,5 ;li  t1,42        ; t1 = 0x2A


;ctx = 0x801C84A0
;1da2ba = 0157 = Entrance
;1da2fe = 2a -> fade swipe = white circle
;         03 -> fade swipe = white fade
;1da2b5 = 1a -> start transition

;12B9E2 = fff1 ????

;#5f0