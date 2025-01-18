; Hack bg_spot18_basket (goron city spinning pot), bomb drops:
.headersize(0x80ac72d0 - 0xe47110)

; Update A0 parameters to store actor pointer instead of PlayState
; It's originally in s0 but gets zero'd and used as the loop variable right before the loop
; Replaces:
;   or      s0, r0, r0
;   or      a0, s4, r0
.org 0x80ac7dc8
    or      a0, s0, r0
    or      s7, r0, r0 ; Use s7 as the loop variable instead of s0
bg_spot18_basket_bombs_loopstart:

.org 0x80ac7df4
; Replaces:
;   addiu   s0, s0, 0x01
;   bnel    s0, s1, bg_spot18_basket_bombs_loopstart
;   or      a0, s4, r0
    addiu   s7, s7, 0x01 ; using s7 as loop variable so need to hack here to increment s7 instead of s0
    bnel    s7, s1, bg_spot18_basket_bombs_loopstart ; using s7 as loop variable so use it in the loop branch
    or      a0, s0, r0 ; need to copy s0 back into a0

; Replace call to Item_DropCollectible.
.org 0x80ac7dd4
; Replaces:
;   jal     Item_DropCollectible
;   li      a2, 0x04; (ITEM00_BOMBS_A)
    jal     BgSpot18Basket_BombDropHook
    or      a2, s7, r0 ; store the loop variable in a2
.skip 4
    sll     t6, s7, 0x01 ; Using s7 as loop variable

; Hack bg_spot18_basket 3 green rupee drops

.org 0x80ac7e1c
; Replaces
;   or      s0, r0, r0
    or      s7, r0, r0 ; Use s7 as loop variable
.skip 8
    or      a0, s0, r0 ; Store actor instance in a0 instead of PlayState
bg_spot18_basket_rupees_loopstart:

.org 0x80ac7e50
; Replaces
;   addiu   s0, s0, 0x01
;   bnel    s0, s1, 0x80ac7e2c
;   or      a0, s4, r0
    addiu   s7, s7, 0x01
    bnel    s7, s1, bg_spot18_basket_rupees_loopstart
    or      a0, s0, r0 ; Store actor instance in a0 again

.org 0x80ac7e30
; Replaces
;   jal     Item_DropCollectible
;   or      a2, r0, r0
    jal     BgSpot18Basket_RupeeDropHook ; Call our hack
    or      a2, s7, r0 ; store the loop variable in a2
.skip 4
    sll     t9, s7, 0x01 ; Using s7 as loop variable

; Hack bg_spot18_basket rupee drops with heart piece
.org 0x80ac7f2c ; Red rupee drop
; Replaces:
;   or      a0, s4, r0
;   or      a1, s3, r0
;   jal     Item_DropCollectible
    or      a0, s0, r0 ; store actor instance into a0 instead of PlayState
.skip 4
    jal     BgSpot18Basket_Heartpiecerupee_DropHook
.skip 8
    or      a0, s0, r0

.org 0x80ac7f54 ; Blue rupee drop
; Replaces:
;   jal     Item_DropCollectible
    jal     BgSpot18Basket_Heartpiecerupee_DropHook
