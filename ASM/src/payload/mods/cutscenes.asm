override_great_fairy_cutscene:
    ; a0 = global context
    ; a2 = fairy actor
    addiu   sp, sp, -0x18
    sw      ra, 0x10 (sp)

    lw      t0, 0x1D2C (a0) ; t0 = switch flags
    li      t1, 1
    sll     t1, t1, 0x18 ; t1 = ZL switch flag
    and     v0, t0, t1
    beqz    v0, @@return ; Do nothing until ZL is played
    nop

    lhu     t2, 0x02DC (a2) ; Load fairy index
    li      t3, SAVE_CONTEXT

    lhu     t4, 0xA4 (a0) ; Load scene number
    beq     t4, 0x3D, @@item_fairy
    nop

    ; Handle upgrade fairies
    addu    t4, a0, t2
    lbu     t5, 0x1D28 (t4) ; t5 = chest flag for this fairy
    bnez    t5, @@refills ; Just refills if the item is already obtained
    nop
    li      t5, 1
    sb      t5, 0x1D28 (t4) ; Mark item as obtained
    addiu   t2, t2, DELAYED_UPGRADE_FAIRIES ; t2 = cutscene override flag
    b       @@give_item
    nop

@@item_fairy:
    li      t4, 1
    sllv    t4, t4, t2 ; t4 = fairy item mask
    lbu     t5, 0x0EF2 (t3) ; t5 = fairy item flags
    and     t6, t5, t4
    bnez    t6, @@refills ; Just refills if the item is already obtained
    nop
    or      t6, t5, t4
    sb      t6, 0x0EF2 (t3) ; Mark item as obtained
    addiu   t2, t2, DELAYED_ITEM_FAIRIES ; t2 = cutscene override flag

@@give_item:
    ; Unset ZL switch
    nor     t1, t1, t1
    and     t0, t0, t1
    sw      t0, 0x1D2C (a0)

    jal     push_delayed_item
    move    a0, t2

@@refills:

    jal     health_and_magic_refill
    nop

@@return:
    lw      ra, 0x10 (sp)
    li      v0, 0 ; Prevent fairy animation

    jr      ra
    addiu   sp, sp, 0x18

;==================================================================================================

; a3 = item ID
override_ocarina_songs:
    addiu   sp, sp, -0x18
    sw      ra, 0x10 (sp)

    jal     push_delayed_item
    addi    a0, a3, -0x5A + DELAYED_OCARINA_SONGS

    li      v0, 0xFF

    lw      ra, 0x10 (sp)
    jr      ra
    addiu   sp, sp, 0x18

;==================================================================================================

override_requiem_song:
    addiu   sp, sp, -0x20
    sw      at, 0x10 (sp)
    sw      v1, 0x14 (sp)
    sw      ra, 0x18 (sp)

    jal     push_delayed_item
    li      a0, DELAYED_REQUIEM

    lw      at, 0x10 (sp)
    lw      v1, 0x14 (sp)
    lw      ra, 0x18 (sp)
    jr      ra
    addiu   sp, sp, 0x20

;==================================================================================================

override_epona_song:
    addiu   sp, sp, -0x20
    sw      a2, 0x10 (sp)
    sw      a3, 0x14 (sp)
    sw      ra, 0x18 (sp)

    lui     at, 0x8012
    addiu   at, at, 0xA5D0 ; v1 = 0x8012A5D0 # save context (sav)
    lb      t0, 0x0EDE (at) ; check learned song from malon flag
    ori     t0, t0, 0x01 ; t9 = "Invited to Sing With Child Malon"
    sb      t0, 0x0EDE (at)

    jal     push_delayed_item
    li      a0, DELAYED_EPONAS_SONG

    lw      a2, 0x10 (sp)
    lw      a3, 0x14 (sp)
    lw      ra, 0x18 (sp)
    jr      ra
    addiu   sp, sp, 0x20

;==================================================================================================

override_suns_song:
    addiu   sp, sp, -0x18
    sw      v1, 0x10 (sp)
    sw      ra, 0x14 (sp)

    lui     at, 0x8012
    addiu   at, at, 0xA5D0 ; v1 = 0x8012A5D0 # save context (sav)
    lb      t0, 0x0EDE (at) ; learned song from sun's song
    ori     t0, t0, 0x04
    sb      t0, 0x0EDE (at)

    jal     push_delayed_item
    li      a0, DELAYED_SUNS_SONG

    lw      v1, 0x10 (sp)
    lw      ra, 0x14 (sp)
    jr      ra
    addiu   sp, sp, 0x18

;==================================================================================================

override_song_of_time:
    addiu   sp, sp, -0x28
    sw      a0, 0x10 (sp)
    sw      v0, 0x14 (sp)
    sw      t7, 0x18 (sp)
    sw      ra, 0x20 (sp)

    jal     push_delayed_item
    li      a0, DELAYED_SONG_OF_TIME

    li      a1, 3 ; Displaced code

    lw      a0, 0x10 (sp)
    lw      v0, 0x14 (sp)
    lw      t7, 0x18 (sp)
    lw      ra, 0x20 (sp)
    jr      ra
    addiu   sp, sp, 0x28

;==================================================================================================

override_saria_song_check:
    move    t7, v1
    lb      t4, 0x0EDF(t7)
    andi    t6, t4, 0x80
    beqz    t6, @@get_item
    li      v1, 5

    jr      ra
    li      v0, 2

@@get_item:
    jr      ra
    move    v0, v1

;==================================================================================================

set_saria_song_flag:
    lh      v0, 0xa4(t6)       ; v0 = scene
    li      t0, SAVE_CONTEXT
    lb      t1, 0x0EDF(t0)
    ori     t1, t1, 0x80
    sb      t1, 0x0EDF(t0)
    jr      ra
    nop

;==================================================================================================

; Injection for talking to the Altar in the Temple of Time
; Should set flag in save that it has been spoken to.
set_dungeon_knowledge:
    addiu   sp, sp, -0x10
    sw      ra, 0x04(sp)

    ; displaced instruction
    jal     0xD6218
    nop

    li      t4, SAVE_CONTEXT
    lh      t5, 0x0F2E(t4) ; flags
    lw      t8, 0x0004(t4) ; age

    beqz    t8, @@set_flag
    li      t6, 0x0001 ; adult bit
    li      t6, 0x0002 ; child bit

@@set_flag:
    or      t5, t5, t6
    sh      t5, 0x0F2E(t4) ; set the flag

    lw      ra, 0x04(sp)
    addiu   sp, sp, 0x10

    jr      ra
    nop
;==================================================================================================

;Break free of the talon cutscene after event flag is set

talon_break_free:

    ;displaced code
    addiu    t1, r0, 0x0041

    ;preserve registers (t0, t1, t2, t4)
    addiu    sp, sp, -0x20
    sw       t0, 0x04(sp)
    sw       t1, 0x08(sp)
    sw       t2, 0x0C(sp)
    sw       t4, 0x10(sp)

    lui    t2, 0xFFFF
    sra    t2, t2, 0x10   ;shift right 2 bytes
    lui    t0, 0x801D
    lh     t4, 0x894C(t0) ;load current value @z64_game.event_flag
    beq    t4, t2, @@msg  ;if in non-cs state, jump to next check
    nop
    sh     r0, 0x894C(t0) ;store 0 to z64_game.event_flag

@@msg:
    lui    t0, 0x801E
    lb     t2, 0x887C(t0)
    beqz   t2, @@return   ;return if msg_state_1 is 0
    nop
    lui    t1, 0x0036
    sra    t1, t1, 0x10   ;shift right 2 bytes
    sb     t1, 0x887C(t0) ;store 0x36 to msg_state_1
    lui    t1, 0x0002
    sra    t1, 0x10       ;shift right 2 bytes
    sb     t1, 0x895F(t0) ;store 0x02 to msg_state_3
    lui    t0, 0x801F
    sb     r0, 0x8D38(t0) ;store 0x00 to msg_state_2

@@return:
    lw       t4, 0x10(sp)
    lw       t2, 0x0C(sp)
    lw       t1, 0x08(sp)
    lw       t0, 0x04(sp)
    jr     ra
    addiu    sp, sp, 0x20

;==================================================================================================

PLAYED_WARP_SONG:
.byte 0x00
.align 4

;When a warp song is played, index the list of warp entrances in Links overlay and trigger a warp manually
;PLAYED_WARP_SONG is set so that the white fade in can be used on the other side of the warp
warp_speedup:

    la     t2, 0x800FE49C ;pointer to links overlay in RAM
    lw     t2, 0(t2)
    beqz   t2, @@return
    nop
    la     t0, GLOBAL_CONTEXT
    lui    t3, 0x0001
    ori    t3, t3, 0x04C4 ;offset of warp song played
    add    t0, t0, t3
    lh     t1, 0x0(t0)
    lui    t3, 0x0002
    ori    t3, t3, 0x26CC
    add    t2, t2, t3     ;entrance Table of Warp songs
    sll    t1, t1, 1
    addu   t2, t1, t2
    lh     t1, 0x0(t2)
    sh     t1, 0x1956(t0) ;next entrance
    la     t4, 0x801D84A0 ;globalctx+10000
    li     t1, 0x03
    sb     t1, 0x1E5E(t4) ;transition fade type
    li     t1, 0x14
    sb     t1, 0x1951(t0) ;scene load flag
    li     t1, 0x01       ;set warp flag for correct fade in
    sb     t1, PLAYED_WARP_SONG
    la     t0, SAVE_CONTEXT
    lh     t1, 0x13D2(t0) ; Timer 2 state
    beqz   t1, @@return
    nop

    li     t1, 0x01
    sh     t1, 0x13D4(t0) ; Timer 2 value

@@return:
    jr     ra
    nop

;If PLAYED_WARP_SONG is set, override the transition fade-in type to be 03 (medium speed white)
set_fade_in:
    ori    at, at, 0x241C   ;displaced
    la     t5, PLAYED_WARP_SONG
    lb     t1, 0x00(t5)
    beqz   t1, @@return
    lh     t2, 0xA4(s1)     ;scene number
    li     t3, 0x5E
    beq    t2, t3, @@return ;dont set fade if current scene is wasteland
    la     t4, 0x801D84A0   ;globalctx+10000
    li     t1, 0x03
    sb     t1, 0x1E5E(t4)   ;transition fade type
    sb     r0, 0x00(t5)     ;clear warp song flag

@@return:
    jr     ra
    nop

;==================================================================================================

; Prevent hyrule castle guards from causing a softlock.
guard_catch:
    la      v0, GLOBAL_CONTEXT
    lui     at, 0x0001
    add     v0, v0, at
    li      at, 0x047e
    sh      at, 0x1E1A(v0) ;entrance index = caught by guard
    li      at, 0x14
    jr      ra
    sb      at, 0x1E15(v0) ; trigger load

;==================================================================================================

; Allow any entrance to kak to play burning cutscene
burning_kak:
    addiu   sp, sp, -0x18
    sw      ra, 0x14(sp)
    sw      a0, 0x18(sp)
    lw      t9, 0x0004(s0)
    bnez    t9, @@default
    lw      t9, 0x0000(s0)
    li      at, 0x800F9C90 ; entrance table
    sll     t9, t9, 2
    add     at, t9, at
    lbu     at, 0x00(at)
    li      t9, 0x52
    bne     t9, at, @@default
    lw      t9, 0x0000(s0)
    lhu     v0, 0x00A6(s0)
    andi    t4, v0, 0x0007
    xori    t4, t4, 0x0007
    bnez    t4, @@default
    addiu   a0, r0, 0xAA
    jal     0x800288B4
    nop
    bnez    v0, @@default    ; Burning Kak already Watched
    lw      t9, 0x0000(s0)
    li      t9, 0xDB
    b       @@return
    sw      t9, 0x0000(s0)

@@default:
    li      at, 0x01E1

@@return:
    lw      ra, 0x14(sp)
    lw      a0, 0x18(sp)
    jr      ra
    addiu   sp, sp, 0x18
;==================================================================================================

; In ER, set the "Obtained Epona" Flag after winning Ingo's 2nd race
ingo_race_win:
    lb      t0, OVERWORLD_SHUFFLED
    beqz    t0, @@return                ; only apply this patch in Overworld ER

    la      at, SAVE_CONTEXT
    lb      t0, 0x0ED6(at)
    ori     t0, t0, 0x01                ; "Obtained Epona" Flag
    sb      t0, 0x0ED6(at)

@@return:
    li      t0, 0
    jr      ra
    sw      t9, 0x0000(t7)              ; Displaced Code

; Rectify the "Getting Caught By Gerudo" entrance index if necessary, based on the age and current scene
; In ER, Adult should be placed at the fortress entrance when getting caught in the fortress without a hookshot, instead of being thrown in the valley
; Child should always be thrown in the stream when caught in the valley, and placed at the fortress entrance from valley when caught in the fortress
; Registers safe to override: t3-t8
gerudo_caught_entrance:
    la      t3, GLOBAL_CONTEXT
    lh      t3, 0x00A4(t3)              ; current scene number
    li      t4, 0x000C                  ; Thieves Hideout scene number
    beq     t3, t4, @@hideout           ; if we are in Thieves Hideout with connector shuffle, prevent guard throwing you in jail or the valley
    li      t4, 0x005A                  ; Gerudo Valley scene number
    bne     t3, t4, @@fortress          ; if we are not in the valley, then we are in the fortress

    li      t3, 0x01A5                  ; else, use the thrown out in valley entrance index, even if you have a hookshot
    sh      t3, 0x1E1A(at)
    b       @@return

@@hideout:
    lb      t3, HIDEOUT_SHUFFLED
    beqz    t3, @@fortress              ; if hideout shuffle is off, treat hideout the same as fortress
    la      t4, SAVE_CONTEXT
    lw      t3, 0x0000(t4)              ; last entrance index
    sh      t3, 0x1E1A(at)
    b       @@return

@@fortress:
    la      t4, SAVE_CONTEXT
    lw      t4, 0x0004(t4)              ; current age
    bnez    t4, @@fortress_entrance     ; if child, change to the fortress entrance no matter what, even if you have a hookshot

    lb      t3, OVERWORLD_SHUFFLED
    beqz    t3, @@return                ; else (if adult), only rectify entrances from inside the fortress in Overworld ER

    lh      t3, 0x1E1A(at)              ; original entrance index
    li      t4, 0x01A5                  ; "Thrown out of Fortress" entrance index
    beq     t3, t4, @@fortress_entrance ; if adult would be thrown in the valley, change to the fortress entrance (no hookshot)
    nop
    b       @@return                    ; else, keep the jail entrance index (owned hookshot)

@@fortress_entrance:
    li      t3, 0x0129                  ; Fortress from Valley entrance index
    sh      t3, 0x1E1A(at)

@@return:
    jr      ra
    nop

;==================================================================================================
;After Link recieves an item in a fairy fountain, fix position and angle to be as if the cutscene finished

GET_ITEM_TRIGGERED:
.byte 0x00
.align 4

fountain_set_posrot:
    or      a1, s1, r0     ;displaced
    la      t2, PLAYER_ACTOR
    lwc1    f4, 0x2C(t2)   ;player z pos
    li      t3, 0xC43B8000 ;-750.0f
    mtc1    t3, f6
    c.lt.s  f4, f6         ;z < 750
    nop
    bc1f   @@return        ;return if z > -750
    nop
    lwc1    f4, 0x24(t2)   ;player x pos
    li      t3, 0xC28A0000 ;-69.0f
    mtc1    t3, f6
    c.lt.s  f4, f6         ;x < -69
    nop
    bc1t   @@return        ;return if x < -69
    nop
    li      t3, 0x41C80000 ;25.0f
    mtc1    t3, f6
    c.lt.s  f4, f6         ;x < 25
    nop
    bc1f   @@return        ;return if x > 25
    nop
    la      t1, GET_ITEM_TRIGGERED
    lb      t3, 0x424(t2)  ;Get Item ID
    beqz    t3, @@skip     ;dont set flag if get item is 0
    lb      t6, 0x0(t1)
    li      t4, 0x7E       ;GI_MAX
    beq     t3, t4, @@skip ;skip for catchable items
    nop
    bnez    t6, @@skip     ;skip setting flag if its already set
    li      t4, 0x1
    sb      t4, 0x0(t1)    ;set flag
    li      t5, 0xC1A00000
    sw      t5, 0x24(t2)   ;set x
    li      t5, 0x41200000
    sw      t5, 0x28(t2)   ;set y
    li      t5, 0xC4458000
    sw      t5, 0x2C(t2)   ;set z

@@skip:
    beqz    t6, @@return
    nop
    bnez    t3, @@return
    li      t5, 0x8000
    sh      t5, 0xB6(t2)   ;set angle
    sb      r0, 0x0(t1)    ;set flag to 0

@@return:
    jr      ra
    nop

;==================================================================================================
SOS_ITEM_GIVEN:
.byte 0x00
.align 4

sos_skip_demo:
    la      t2, PLAYER_ACTOR
    lw      t3, 0x66C(t2)
    li      t4, 0xCFFFFFFF ;~30000000
    and     t3, t3, t4
    jr      ra
    sw      t3, 0x66C(t2)  ;unset flag early so link can receive item asap

;game has loaded 0x800000 into at, player into v0, and stateFlags2 into t6
sos_handle_staff:
    addiu   sp, sp, -0x20
    sw      ra, 0x14(sp)
    sw      a0, 0x18(sp)
    or      t7, t6, at
    sw      t7, 0x680(v0) ;stateFlags2 |= 0x800000
    li      a0, 0x01
    jal     0x8006D8E0    ;Interface_ChangeAlpha, hide hud
    nop
    lb      t0, SONGS_AS_ITEMS
    bnez    t0, @@return
    nop
    la      a0, GLOBAL_CONTEXT
    lb      a1, WINDMILL_SONG_ID
    jal     0x800DD400    ;show song staff
    nop
@@return:
    lw      a0, 0x18(sp)
    lw      t0, 0x138(a0) ;overlayEntry
    lw      t1, 0x10(t0)  ;overlay ram start
    addiu   t2, t1, 0x3D4 ;offset in the overlay for next actionFunc
    sw      t2, 0x29C(a0) ;set next actionFunc
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x20

sos_handle_item:
    addiu   sp, sp, -0x20
    sw      ra, 0x14(sp)
    sw      a0, 0x18(sp)
    lb      t0, SONGS_AS_ITEMS
    bnez    t0, @@songs_as_items
    nop
    la      t1, 0x801D887C
    lb      t0, 0x0(t1) ;msgMode
    li      t3, 0x36
    bne     t0, t3, @@next_check
    nop
    lb      t0, SOS_ITEM_GIVEN
    bnez    t0, @@next_check
    nop

@@passed_first_check: ;play sound, show text, set flag, return
    li      t0, 1
    sb      t0, SOS_ITEM_GIVEN
    la      a0, GLOBAL_CONTEXT
    lbu     a1, WINDMILL_TEXT_ID
    li      a2, 0
    jal     0x800DCE14    ;show text
    nop
    li      a0, 0x4802    ;NA_SE_SY_CORRECT_CHIME
    jal     0x800646F0    ;play "correct" sound
    nop
    b       @@return
    nop

@@songs_as_items: ;give item then branch to the common ending code
    la      a0, GLOBAL_CONTEXT
    li      a1, 0x65       ;sos Item ID
    jal     0x8006FDCC     ;Item_Give
    nop
    li      a0, 0x32
    jal     0x8006D8E0     ;Interface_ChangeAlpha, bring hud back
    nop
    b       @@common
    nop

@@next_check:
    lw      a0, 0x18(sp)   ;this
    la      a1, GLOBAL_CONTEXT
    jal     0x80022AD0     ;Actor_TextboxIsClosing in decomp, checks for closed text
    nop
    beqz    v0, @@return   ;return if text isnt closed yet
    nop
    lb      t0, SOS_ITEM_GIVEN
    beqz    t0, @@return
    nop
@@common:
    lw      a0, 0x18(sp)
    lw      t0, 0x138(a0)  ;overlayEntry
    lw      t1, 0x10(t0)   ;overlay ram start
    addiu   t2, t1, 0x35C  ;offset in the overlay for next actionFunc
    sw      t2, 0x29C(a0)  ;set next actionFunc
    la      v0, SAVE_CONTEXT
    lhu     t1, 0x0EE0(v0)
    ori     t2, t1, 0x0020
    sh      t2, 0x0EE0(v0) ;gSaveContext.eventChkInf[6] |= 0x20
    lw      t0, 0x4(a0)
    li      t1, 0xFFFEFFFF
    and     t0, t0, t1
    sw      t0, 0x4(a0)    ;actor.flags &= ~0x10000
@@return:
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x20

;if link is getting an item dont allow the windmill guy to talk
sos_talk_prevention:
    lh      t7, 0xB6(s0)   ; displaced
    lhu     t9, 0xB4AE(t9) ; displaced
    la      t1, PLAYER_ACTOR
    lw      t2, 0x428(t1)  ; interactRangeActor
    beqz    t2, @@no_item
    nop
    lb      t2, 0x424(t1)  ; get item id
    li      t1, 0x7E
    bne     t2, t1, @@item
    nop

@@no_item:
    jr      ra
    li      t2, 0

@@item:
    jr      ra
    li      t2, 1

;==================================================================================================
;move royal tombstone if draw function is null
move_royal_tombstone:
    lw      t6, 0x134(a0)  ;grave draw function
    bnez    t6, @@return
    li      t6, 0x44800000 ;new x pos
    sw      t6, 0x24(a0)
@@return:
    jr      ra
    lw      t6, 0x44(sp)

;==================================================================================================

heavy_block_set_switch:
    addiu   a1, s0, 0x01A4 ;displaced
    addiu   sp, sp, -0x20
    sw      ra, 0x14(sp)
    sw      a1, 0x18(sp)
    lh      a1, 0x1C(s1)
    sra     a1, a1, 8
    jal     0x800204D0     ;set switch flag
    andi    a1, a1, 0x3F
    lw      a1, 0x18(sp)
    lw      ra, 0x14(sp)
    jr      ra
    addiu   sp, sp, 0x20

heavy_block_posrot:
    sw      t9, 0x66C(s0)  ;displaced
    lw      t2, 0x428(s0)  ;interactActor (block)
    la      t1, PLAYER_ACTOR
    lh      t3, 0xB6(t2)   ;block angle
    addi    t3, t3, 0x8000 ;180 deg
    jr      ra
    sh      t3, 0xB6(t1)   ;store to links angle to make him face block

heavy_block_set_link_action:
    la      t0, PLAYER_ACTOR
    lb      t2, 0x0434(t0)
    li      t3, 0x08
    bne     t2, t3, @@return
    li      t1, 0x07       ;action 7
    sb      t1, 0x0434(t0) ;links action
@@return:
    jr      ra
lwc1    f6, 0x0C(s0)   ;displaced

heavy_block_shorten_anim:
    la      t0, PLAYER_ACTOR
    lw      t1, 0x01AC(t0)   ;current animation
    li      t2, 0x04002F98   ;heavy block lift animation
    bne     t1, t2, @@return ;return if not heavy block lift
    lw      t3, 0x1BC(t0)    ;current animation frame
    li      t4, 0x42CF0000
    bne     t3, t4, @@check_end
    li      t5, 0x43640000   ;228.0f
    b       @@return
    sw      t5, 0x1BC(t0)    ;throw block
@@check_end:
    li      t4, 0x43790000   ;249.0f
    bne     t3, t4, @@return
    li      t1, 0x803A967C
    sw      t1, 0x664(t0)
@@return:
    jr      ra
    addiu   a1, s0, 0x01A4   ;displaced

; Hook return for DemoEffect_DrawJewel
DemoEffect_DrawJewel:
; Replaced code
    addiu   sp, sp, -0x78
    sw      s3, 0x40(sp)
    jr      a2
    nop

SKIP_N64_LOGO:
.byte 0x00
.align 4

skip_nintendo_logo:
    ; Displaced code
    lui     v0, 0x8012

    lb      t4, SKIP_N64_LOGO
    beqz    t4, @@return
    nop

    li      t3, 0x01

@@return:
    jr      ra
    nop
