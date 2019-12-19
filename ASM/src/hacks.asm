; Prevent Kokiri Sword from being added to inventory on game load
; Replaces:
;   sh      t9, 0x009C (v0)
.orga 0xBAED6C ; In memory: 0x803B2B6C
    nop

;==================================================================================================
; Time Travel
;==================================================================================================

; Prevents FW from being unset on time travel
; Replaces:
;   SW  R0, 0x0E80 (V1)
.orga 0xAC91B4 ; In memory: 0x80053254
    nop

; Replaces:
;   jal     8006FDCC ; Give Item
.orga 0xCB6874 ; Bg_Toki_Swd addr 809190F4 in func_8091902C
    jal     give_master_sword

; Replaces:
;   lui/addiu a1, 0x8011A5D0
.orga 0xAE5764
    j       before_time_travel
    nop

; After time travel
; Replaces:
;   jr      ra
.orga 0xAE59E0 ; In memory: 0x8006FA80
    j       after_time_travel

;==================================================================================================
; Door of Time Fix
;==================================================================================================

.orga 0xAC8608; 800526A8
    or      a0, s0
    lh      t6, 0x00A4(a0)
    li      at, 67
    nop
    nop

;==================================================================================================
; Item Overrides
;==================================================================================================

; Patch NPCs to give override-compatible items
.orga 0xDB13D3 :: .byte 0x76 ; Frog Ocarina Game
.orga 0xDF2647 :: .byte 0x76 ; Ocarina memory game
.orga 0xE2F093 :: .byte 0x34 ; Bombchu Bowling Bomb Bag
.orga 0xEC9CE7 :: .byte 0x7A ; Deku Theater Mask of Truth

; Runs when storing an incoming item to the player instance
; Replaces:
;   sb      a2, 0x0424 (a3)
;   sw      a0, 0x0428 (a3)
.orga 0xA98C30 ; In memory: 0x80022CD0
    jal     get_item_hook
    sw      a0, 0x0428 (a3)

; Override object ID (NPCs)
; Replaces:
;   lw      a2, 0x0030 (sp)
;   or      a0, s0, r0
;   jal     ...
;   lh      a1, 0x0004 (a2)
.orga 0xBDA0D8 ; In memory: 0x803950C8
    jal     override_object_npc
    or      a0, s0, r0
.skip 4
    nop

; Override object ID (Chests)
; Replaces:
;   lw      t9, 0x002C (sp)
;   or      a0, s0, r0
;   jal     ...
;   lh      a1, 0x0004 (t9)
.orga 0xBDA264 ; In memory: 0x80395254
    jal     override_object_chest
    or      a0, s0, r0
.skip 4
    nop

; Override graphic ID
; Replaces:
;   bltz    v1, A
;   subu    t0, r0, v1
;   jr      ra
;   sb      v1, 0x0852 (a0)
; A:
;   sb      t0, 0x0852 (a0)
;   jr      ra
.orga 0xBCECBC ; In memory: 0x80389CAC
    j       override_graphic
    nop
    nop
    nop
    nop
    nop

; Override chest speed
; Replaces:
;   lb      t2, 0x0002 (t1)
;   bltz    t2, @@after_chest_speed_check
;   nop
;   jal     0x80071420
;   nop
.orga 0xBDA2E8 ; In memory: 0x803952D8
    jal     override_chest_speed
    lb      t2, 0x0002 (t1)
    bltz    t3, @@after_chest_speed_check
    nop
    nop
.skip 4 * 22
@@after_chest_speed_check:

; Override text ID
; Replaces:
;   lbu     a1, 0x03 (v0)
;   sw      a3, 0x0028 (sp)
.orga 0xBE9AC0 ; In memory: 0x803A4AB0
    jal     override_text
    sw      a3, 0x0028 (sp)

; Override action ID
; Replaces:
;   lw      v0, 0x0024 (sp)
;   lw      a0, 0x0028 (sp)
;   jal     0x8006FDCC
;   lbu     a1, 0x0000 (v0)
.orga 0xBE9AD8 ; In memory: 0x803A4AC8
    jal     override_action
    lw      v0, 0x0024 (sp)
.skip 4
    lw      a0, 0x0028 (sp)

; Inventory check
; Replaces:
;   jal     0x80071420
;   sw      a2, 0x0030 (sp)
.orga 0xBDA0A0 ; In memory: 0x80395090
    jal     inventory_check
    sw      a2, 0x0030 (sp)

; Prevent Silver Gauntlets warp
; Replaces:
;   addiu   at, r0, 0x0035
.orga 0xBE9BDC ; In memory: 0x803A4BCC
    addiu   at, r0, 0x8383 ; Make branch impossible

; Change Skulltula Token to give a different item
; Replaces
;    move    a0, s1
;    jal     0x0006FDCC        ; call ex_06fdcc(ctx, 0x0071); VROM: 0xAE5D2C
;    li      a1, 0x71
;    lw      t5, 0x2C (sp)     ; t5 = what was *(ctx + 0x1c44) at the start of the function
;    li      t4, 0x0A
;    move    a0, s1
;    li      a1, 0xB4          ; a1 = 0x00b4 ("You destoryed a Gold Skulltula...")
;    move    a2, zero
;    jal     0x000DCE14        ; call ex_0dce14(ctx, 0x00b4, 0)
;    sh      t4, 0x110 (t5)    ; *(t5 + 0x110) = 0x000a
.orga 0xEC68BC
.area 0x28, 0
    lw      t5, 0x2C (sp)                ; original code
    li      t4, 0x0A                     ; original code
    sh      t4, 0x110 (t5)               ; original code
    jal     get_skulltula_token          ; call override_skulltula_token(actor)
    move    a0, s0
.endarea

.orga 0xEC69AC
.area 0x28, 0
    lw      t5, 0x2C (sp)                ; original code
    li      t4, 0x0A                     ; original code
    sh      t4, 0x110 (t5)               ; original code
    jal     get_skulltula_token          ; call override_skulltula_token(actor)
    move    a0, s0
.endarea

;==================================================================================================
; Every frame hooks
;==================================================================================================

; Runs before the game state update function
; Replaces:
;   lw      t6, 0x0018 (sp)
;   lui     at, 0x8010
.orga 0xB12A34 ; In memory: 0x8009CAD4
    jal     before_game_state_update_hook
    nop

; Runs after the game state update function
; Replaces:
;   jr      ra
;   nop
.orga 0xB12A60 ; In memory: 0x8009CB00
    j       after_game_state_update
    nop

;==================================================================================================
; Scene init hook
;==================================================================================================

; Runs after scene init
; Replaces:
;   jr      ra
;   nop
.orga 0xB12E44 ; In memory: 0x8009CEE4
    j       after_scene_init
    nop


;==================================================================================================
; Freestanding models
;==================================================================================================

; Replaces:
;   jal     0x80013498 ; Piece of Heart draw function
.orga 0xA88F78 ; In memory: 0x80013018
    jal     heart_piece_draw

; Replaces:
;   jal     0x80013498 ; Collectable draw function
.orga 0xA89048 ; In memory: 0x800130E8
    jal     small_key_draw

; Replaces:
;   addiu   sp, sp, -0x48
;   sw      ra, 0x1C (sp)
.orga 0xCA6DC0
    j       heart_container_draw
    nop

.orga 0xDE1018
.area 10 * 4, 0
    jal     item_etcetera_draw
    nop
.endarea

; Replaces:
;   addiu   sp, sp, -0x18
;   sw      ra, 0x14 (sp)
.orga 0xDE1050
    j       item_etcetera_draw
    nop

; Replaces:
;   addiu   sp, sp, -0x18
;   sw      ra, 0x14 (sp)
.orga 0xE59E68
    j       bowling_bomb_bag_draw
    nop

; Replaces:
;   addiu   sp, sp, -0x18
;   sw      ra, 0x14 (sp)
.orga 0xE59ECC
    j       bowling_heart_piece_draw
    nop

; Replaces:
;   addiu   sp, sp, -0x18
;   sw      ra, 0x14 (sp)
.orga 0xEC6B04
    j       skull_token_draw
    nop

; Replaces:
;   addiu   sp, sp, -0x18
;   sw      ra, 0x14 (sp)
.orga 0xDB53E8
    j       ocarina_of_time_draw
    nop

;==================================================================================================
; File select hash
;==================================================================================================

; Runs after the file select menu is rendered
; Replaces: code that draws the fade-out rectangle on file load
.orga 0xBAF738 ; In memory: 0x803B3538
.area 0x60, 0
    jal     draw_file_select_hash
    andi    a0, t8, 0xFF ; a0 = alpha channel of fade-out rectangle

    lw      s0, 0x18 (sp)
    lw      ra, 0x1C (sp)
    jr      ra
    addiu   sp, sp, 0x88
.endarea

;==================================================================================================
; Special item sources
;==================================================================================================

; Override Light Arrow cutscene
; Replaces:
;   addiu   t8, r0, 0x0053
;   ori     t9, r0, 0xFFF8
;   sw      t8, 0x0000 (s0)
;   b       0x80056F84
;   sw      t9, 0x0008 (s0)
.orga 0xACCE88 ; In memory: 0x80056F28
    jal     push_delayed_item
    li      a0, DELAYED_LIGHT_ARROWS
    nop
    nop
    nop

; Make all Great Fairies give an item
; Replaces:
;   jal     0x8002049C
;   addiu   a1, r0, 0x0038
.orga 0xC89744 ; In memory: 0x801E3884
    jal     override_great_fairy_cutscene
    addiu   a1, r0, 0x0038

; Upgrade fairies check scene chest flags instead of magic/defense
; Mountain Summit Fairy
; Replaces:
;   lbu     t6, 0x3A (a1)
.orga 0xC89868 ; In memory: 0x801E39A8
    lbu     t6, 0x1D28 (s0)
; Crater Fairy
; Replaces:
;   lbu     t9, 0x3C (a1)
.orga 0xC898A4 ; In memory: 0x801E39E4
    lbu     t9, 0x1D29 (s0)
; Ganon's Castle Fairy
; Replaces:
;   lbu     t2, 0x3D (a1)
.orga 0xC898C8 ; In memory: 0x801E3A08
    lbu     t2, 0x1D2A (s0)

; Upgrade fairies never check for magic meter
; Replaces:
;   lbu     t6, 0xA60A (t6)
.orga 0xC892DC ; In memory: 0x801E341C
    li      t6, 1

; Item fairies never check for magic meter
; Replaces:
;   lbu     t2, 0xA60A (t2)
.orga 0xC8931C ; In memory: 0x801E345C
    li      t2, 1

;==================================================================================================
; Pause menu
;==================================================================================================

; Create a blank texture, overwriting a Japanese item description
.orga 0x89E800
.fill 0x400, 0

; Don't display hover boots in the bullet bag/quiver slot if you haven't gotten a slingshot before becoming adult
; Replaces:
;   lbu     t4, 0x0000 (t7)
;   and     t6, v1, t5
.orga 0xBB6CF0
    jal     equipment_menu_fix
    nop

; Use a blank item description texture if the cursor is on an empty slot
; Replaces:
;   sll     t4, v1, 10
;   addu    a1, t4, t5
.orga 0xBC088C ; In memory: 0x8039820C
    jal     menu_use_blank_description
    nop

;==================================================================================================
; Equipment menu
;==================================================================================================

; Left movement check
; Replaces:
;   beqz    t3, 0x8038D9FC
;   nop
.orga 0xBB5EAC ; In memory: 0x8038D834
    nop
    nop

; Right movement check
; Replaces:
;   beqz    t3, 0x8038D9FC
;   nop
.orga 0xBB5FDC ; In memory: 0x8038D95C
nop
nop

; Upward movement check
; Replaces:
;   beqz    t6, 0x8038DB90
;   nop
.orga 0xBB6134 ; In memory: 0x8038DABC
nop
nop

; Downward movement check
; Replaces:
;   beqz    t9, 0x8038DB90
;   nop
.orga 0xBB61E0 ; In memory: 0x8038DB68
nop
nop

; Remove "to Equip" text if the cursor is on an empty slot
; Replaces:
;   lbu     v1, 0x0000 (t4)
;   addiu   at, r0, 0x0009
.orga 0xBB6688 ; In memory: 0x8038E008
    jal     equipment_menu_prevent_empty_equip
    nop

; Prevent empty slots from being equipped
; Replaces:
;   addu    t8, t4, v0
;   lbu     v1, 0x0000 (t8)
.orga 0xBB67C4 ; In memory: 0x8038E144
    jal     equipment_menu_prevent_empty_equip
    addu    t4, t4, v0

;==================================================================================================
; Item menu
;==================================================================================================

; Left movement check
; Replaces:
;   beq     s4, t5, 0x8038F2B4
;   nop
.orga 0xBB77B4 ; In memory: 0x8038F134
    nop
    nop

; Right movement check
; Replaces:
;   beq     s4, t4, 0x8038F2B4
;   nop
.orga 0xBB7894 ; In memory: 0x8038F214
    nop
    nop

; Upward movement check
; Replaces:
;   beq     s4, t4, 0x8038F598
;   nop
.orga 0xBB7BA0 ; In memory: 0x8038F520
    nop
    nop

; Downward movement check
; Replaces:
;   beq     s4, t4, 0x8038F598
;   nop
.orga 0xBB7BFC ; In memory: 0x8038F57C
    nop
    nop

; Remove "to Equip" text if the cursor is on an empty slot
; Replaces:
;   addu    s1, t6, t7
;   lbu     v0, 0x0000 (s1)
.orga 0xBB7C88 ; In memory: 0x8038F608
    jal     item_menu_prevent_empty_equip
    addu    s1, t6, t7

; Prevent empty slots from being equipped
; Replaces:
;   lbu     v0, 0x0000 (s1)
;   addiu   at, r0, 0x0009
.orga 0xBB7D10 ; In memory: 0x8038F690
    jal     item_menu_prevent_empty_equip
    nop

;==================================================================================================
; Song Fixes
;==================================================================================================

; Replaces:
;   lw      t5, 0x8AA0(t5)
.orga 0xAE5DF0 ; In memory: 8006FE90
    jal     suns_song_fix

; Replaces:
;   addu    at, at, s3
.orga 0xB54E5C ; In memory: 800DEEFC
    jal     suns_song_fix_event

; Replaces:
;   addu    at, at, s3
.orga 0xB54B38 ; In memory: 800DEBD8
    jal     warp_song_fix

;==================================================================================================
; Initial save
;==================================================================================================

; Replaces:
;   sb      t0, 32(s1)
;   sb      a1, 33(s1)
.orga 0xB06C2C ; In memory: ???
    jal     write_initial_save
    sb      t0, 32(s1)

;==================================================================================================
; Enemy Hacks
;==================================================================================================

; Replaces:
;   beq     t1, at, 0x801E51E0
.orga 0xD74964 ; In memory: 0x801E51B4
    b       skip_steal_tunic  ; disable like-like stealing tunic
.orga 0xD74990
    skip_steal_tunic:

;==================================================================================================
; Ocarina Song Cutscene Overrides
;==================================================================================================

; Replaces:
;   jal     0x800288B4
.orga 0xACCDE0 ; In memory: 0x80056E80
    jal     give_sarias_gift

; a3 = item ID
; Replaces:
;   li      v0, 0xFF
;   ... (2 instructions)
;   sw      t7, 0xA4 (t0)
.orga 0xAE5DF8 ; In memory: 0x8006FE98
    jal     override_ocarina_songs
.skip 0x8
    nop

; Replaces
;   lui     at, 0x1
;   addu    at, at, s0
.orga 0xAC9ABC ; In memory: 0x80053B5C
    jal     override_requiem_song
    nop

;lw $t7, 0xa4($v1)
;lui $v0, 0x200
;addiu $v0, $v0, 0x24a0
;and $t8, $t6, $t7
.orga 0xE09F68
    lb  t7,0x0EDE(v1) ; check learned song from sun's song
.skip 4
.skip 4
    andi t8, t7, 0x04
;addiu $t7, $zero, 1
.orga 0xE09FB0
    jal override_suns_song

; lw $t7, 0xa4($s0)
; lui $t3, 0x8010
; addiu $t3, $t3, -0x70cc
; and $t8, $t6, $t7
.orga 0xB06400
    lb  t7,0x0EDE(s0) ; check learned song from ZL
.skip 4
.skip 4
    andi t8, t7, 0x02

; Impa does not despawn from Zelda Escape CS
.orga 0xD12F78
    li  t7, 0

;li v1, 5
.orga 0xE29388
    j   override_saria_song_check

;lh v0, 0xa4(t6)       ; v0 = scene
.orga 0xE2A044
    jal  set_saria_song_flag

; li a1, 3
.orga 0xDB532C
    jal override_song_of_time

;==================================================================================================
; Fire Arrow location spawn condition
;==================================================================================================

; Replaces a check for whether fire arrows are in the inventory
; The item spawns if t9 == at
.orga 0xE9E1B8
.area 6 * 4, 0
    lw      t9, (GLOBAL_CONTEXT + 0x1D38) ; Chest flags
    andi    t9, t9, 0x1
    ori     at, r0, 0
.endarea

;==================================================================================================
; Epona Check Override
;==================================================================================================

.orga 0xA9E838
    j       Check_Has_Epona_Song

;==================================================================================================
; Shop Injections
;==================================================================================================

; Check sold out override
.orga 0xC004EC
    j        Shop_Check_Sold_Out

; Allow Shop Item ID up to 100 instead of 50
; slti at, v1, 0x32
.orga 0xC0067C
    slti     at, v1, 100

; Set sold out override
; lh t6, 0x1c(a1)
.orga 0xC018A0
    jal      Shop_Set_Sold_Out

; Only run init function if ID is in normal range
; jr t9
.orga 0xC6C7A8
    jal      Shop_Keeper_Init_ID
.orga 0xC6C920
    jal      Shop_Keeper_Init_ID

; Override Deku Salescrub sold out check
; addiu at, zero, 2
; lui v1, 0x8012
; bne v0, at, 0xd8
; addiu v1, v1, -0x5a30
; lhu t9, 0xef0(v1)
.orga 0xEBB85C
    jal     Deku_Check_Sold_Out
    .skip 4
    bnez    v0, @Deku_Check_True
    .skip 4
    b       @Deku_Check_False
.orga 0xEBB8B0
@Deku_Check_True:
.orga 0xEBB8C0
@Deku_Check_False:

; Ovveride Deku Scrub set sold out
; sh t7, 0xef0(v0)
.orga 0xDF7CB0
    jal     Deku_Set_Sold_Out

;==================================================================================================
; Dungeon info display
;==================================================================================================

; Talk to Temple of Time Altar injection
; Replaces:
;   jal     0xD6218
.orga 0xE2B0B4
    jal     set_dungeon_knowledge


;==================================================================================================
; V1.0 Scarecrow Song Bug
;==================================================================================================

; Replaces:
;   jal     0x80057030 ; copies Scarecrow Song from active space to save context
.orga 0xB55A64 ; In memory 800DFB04
    jal     save_scarecrow_song

;==================================================================================================
; Override Player Name Text
;==================================================================================================

; Replaces
;   lui   t2,0x8012
;   addu  t2,t2,s3
;   lbu   t2,-23053(t2)
.orga 0xB51694
    jal     get_name_char_1
    ;addi    a0, s3, -1
    ;ori     t2, v0, 0

; Replaces
;   lui   s0,0x8012
;   addu  s0,s0,s2
;   lbu   s0,-23052(s0)
.orga 0xB516C4
    jal     get_name_char_2
    ;ori     a0, s2, 0
    ;ori     s0, v0, 0

; Replaces
;   lw      s6,48(sp)
;   lw      s7,52(sp)
;   lw      s8,56(sp)
.orga 0xB52784
    jal     reset_player_name_id
    nop
    lw      ra, 0x3C (sp)

;==================================================================================================
; Text Fixes
;==================================================================================================

; Skip text overrides for GS Token and Biggoron Sword
; Replaces
;   li      at, 0x0C
.orga 0xB5293C
    b       skip_GS_BGS_text
.orga 0xB529A0
skip_GS_BGS_text:

;==================================================================================================
; Empty bomb fix
;==================================================================================================

; Replaces:
;   lw      a1, 0x0018 (sp) ; bomb ovl+134
;   lw      a0, 0x001C (sp)
.orga 0xC0E404
    jal     empty_bomb_fix
    lw      a1, 0x0018 (sp)

;==================================================================================================
; Damage Multiplier
;==================================================================================================

; Replaces:
;   lbu     t7, 0x3d(a1)
;   beql    t7, zero, 0x20
;   lh      t8, 0x30(a1)
;   bgezl   s0, 0x20
;   lh      t8, 0x30(a1)
;   sra     s0, s0, 1    ; double defense
;   sll     s0, s0, 0x10
;   sra     s0, s0, 0x10 ; s0 = damage

.orga 0xAE807C
    bgez    s0, @@continue ; check if damage is negative
    lh      t8, 0x30(a1)   ; load hp for later
    jal     Apply_Damage_Multiplier
    nop
    lh      t8, 0x30(a1)   ; load hp for later
    nop
    nop
    nop
@@continue:

;==================================================================================================
; Skip Scarecrow Song
;==================================================================================================

; Replaces:
;   lhu     t0, 0x04C6 (t0)
;   li      at, 0x0B
.orga 0xEF4F98
    jal adapt_scarecrow
    nop

;==================================================================================================
; Talon Cutscene Skip
;==================================================================================================

; Replaces: lw      a0, 0x0018(sp)
;           addiu   t1, r0, 0x0041

.orga 0xCC0038
    jal    talon_break_free
    lw     a0, 0x0018(sp)

;==================================================================================================
; Patches.py imports
;==================================================================================================

; Remove intro cutscene
.orga 0xB06BB8
    li      t9, 0

; Change Bombchu Shop to be always open
.orga 0xC6CEDC
    li      t3, 1

; Fix child shooting gallery reward to be static
.orga 0xD35EFC
    nop

; Fix Link the Goron to always work
.orga 0xED2FAC
    lb      t6, 0x0F18(v1)

.orga 0xED2FEC
    li      t2, 0

.orga 0xAE74D8
    li      t6, 0


; Fix King Zora Thawed to always work
.orga 0xE55C4C
    li t4, 0

.orga 0xE56290
    nop
    li t3, 0x401F
    nop

; Fix target in woods reward to be static
.orga 0xE59CD4
    nop
    nop

; Fix adult shooting gallery reward to be static
.orga 0xD35F54
    b_a     0xD35F78


; Learning Serenade tied to opening chest in room
.orga 0xC7BCF0
    lw      t9, 0x1D38(a1) ; Chest Flags
    li      t0, 0x0004     ; flag mask
    lw      v0, 0x1C44(a1) ; needed for following code
    nop
    nop
    nop
    nop

; Dampe Chest spawn condition looks at chest flag instead of having obtained hookshot
.orga 0xDFEC3C
    lw      t8, (SAVE_CONTEXT + 0xDC + (0x48 * 0x1C)) ; Scene clear flags
    addiu   a1, sp, 0x24
    andi    t9, t8, 0x0010 ; clear flag 4
    nop

; Darunia sets an event flag and checks for it
; TODO: Figure out what is this for. Also rewrite to make things cleaner
.orga 0xCF1AB8
    nop
    lw      t1, lo(SAVE_CONTEXT + 0xED8)(t8)
    andi    t0, t1, 0x0040
    ori     t9, t1, 0x0040
    sw      t9, lo(SAVE_CONTEXT + 0xED8)(t8)
    li      t1, 6

;==================================================================================================
; Easier Fishing
;==================================================================================================

; Make fishing less obnoxious
.orga 0xDBF428
    jal     easier_fishing
    lui     at, 0x4282
    mtc1    at, f8
    mtc1    t8, f18
    swc1    f18, 0x019C(s2)

.orga 0xDBF484
    nop

.orga 0xDBF4A8
    nop

; set adult fish size requirement
.orga 0xDCBEA8
    lui     at, 0x4248

.orga 0xDCBF24
    lui     at, 0x4248

; set child fish size requirements
.orga 0xDCBF30
    lui     at, 0x4230

.orga 0xDCBF9C
    lui     at, 0x4230

; Fish bite guaranteed when the hook is stable
; Replaces: lwc1    f10, 0x0198(s0)
;           mul.s   f4, f10, f2
.orga 0xDC7090
    jal     fishing_bite_when_stable
    lwc1    f10, 0x0198(s0)

; Remove most fish loss branches
.orga 0xDC87A0
    nop
.orga 0xDC87BC
    nop
.orga 0xDC87CC
    nop

; Prevent RNG fish loss
; Replaces: addiu   at, zero, 0x0002
.orga 0xDC8828
    move    at, t5

;==================================================================================================
; Bombchus In Logic Hooks
;==================================================================================================

.orga 0xE2D714
    jal     logic_chus__bowling_lady_1
    lui     t9, 0x8012
    li      t1, 0xBF
    nop

.orga 0xE2D890
    jal     logic_chus__bowling_lady_2
    nop

.orga 0xC01078
    jal     logic_chus__shopkeeper
    nop
    nop
    nop
    nop
    nop

;==================================================================================================
; Rainbow Bridge
;==================================================================================================

.orga 0xE2B434
.area 0x30, 0
    jal     rainbow_bridge
    nop
.endarea

;==================================================================================================
; Gossip Stone Hints
;==================================================================================================

.orga 0xEE7B84
.area 0x24, 0
    jal     gossip_hints
    lw      a0, 0x002C(sp) ; global context
.endarea

;==================================================================================================
; Potion Shop Fix
;==================================================================================================

.orga 0xE2C03C
    jal     potion_shop_fix
    addiu   v0, v0, 0xA5D0 ; displaced

;==================================================================================================
; Jabu Jabu Elevator
;==================================================================================================

;Replaces: addiu t5, r0, 0x0200
.orga 0xD4BE6C
    jal     jabu_elevator

;==================================================================================================
; DPAD Display
;==================================================================================================
;
; Replaces lw    t6, 0x1C44(s6)
;          lui   t8, 0xDB06
.orga 0xAEB67C ; In Memory: 0x8007571C
    jal     dpad_draw
    nop

;==================================================================================================
; Correct Chest Sizes
;==================================================================================================
; Replaces lbu   v0,0x01E9(s0)
.orga 0xC064BC
    jal     GET_CHEST_OVERRIDE_SIZE_WRAPPER
.orga 0xC06E5C
    jal     GET_CHEST_OVERRIDE_SIZE_WRAPPER
.orga 0xC07494
    jal     GET_CHEST_OVERRIDE_SIZE_WRAPPER

; Replaces sw    t8,8(t6)
;          lbu   v0,489(s0)
.orga 0xC0722C
    jal     GET_CHEST_OVERRIDE_SIZE_WRAPPER
    sw      t8,8(t6)

; Replaces lbu   t9,0x01E9(s0)
.orga 0xC075A8
    jal     GET_CHEST_OVERRIDE_COLOR_WRAPPER
.orga 0xC07648
    jal     GET_CHEST_OVERRIDE_COLOR_WRAPPER

;==================================================================================================
; Cast Fishing Rod without B Item
;==================================================================================================

.orga 0xBCF914 ; 8038A904
    jal     keep_fishing_rod_equipped
    nop

.orga 0xBCF73C ; 8038A72C
    sw      ra, 0x0000(sp)
    jal     cast_fishing_rod_if_equipped
    nop
    lw      ra, 0x0000(sp)

;==================================================================================================
; Big Goron Fix
;==================================================================================================
;
;Replaces: beq     $zero, $zero, lbl_80B5AD64

.orga 0xED645C
    jal     bgs_fix
    nop

;==================================================================================================
; Hot Rodder Goron without Bomb Bag
;==================================================================================================
;
;Replaces: LW   T8, 0x00A0 (V0)
.orga 0xED2858
    addi    t8, r0, 0x0008

;==================================================================================================
; Warp song speedup
;==================================================================================================
;
.orga 0xBEA044
   jal      warp_speedup
   nop
   

;==================================================================================================
; Dampe Digging Fix
;==================================================================================================
;
; Dig Anywhere
.orga 0xCC3FA8
    sb      at, 0x1F8(s0)

; Always First Try
.orga 0xCC4024
    nop

; Leaving without collecting dampe's prize won't lock you out from that prize
.orga 0xCC4038
    jal     dampe_fix
    addiu   t4, r0, 0x0004

.orga 0xCC453C
    .word 0x00000806
;==================================================================================================
; Drawbridge change
;==================================================================================================
;
; Replaces: SH  T9, 0x00B4 (S0)
.orga 0xC82550
   nop

;==================================================================================================
; Never override menu subscreen index
;==================================================================================================

; Replaces: bnezl t7, 0xAD1988 ; 0x8005BA28
.orga 0xAD193C ; 0x8005B9DC
    b . + 0x4C


;==================================================================================================
; Extended Objects Table 
;==================================================================================================

; extends object table lookup for on chest open
.org 0xBD6958
    jal extended_object_lookup_GI
    nop

; extends object table lookup for on scene loads
.org 0xAF76B8
    sw      ra, 0x0C (sp)
    jal extended_object_lookup_load
    subu    t7, r0, a2
    lw      ra, 0x0C (sp)

; extends object table lookup for shop item load
.org 0xAF74F8
    sw      ra, 0x44 (sp)
    jal extended_object_lookup_shop
    nop
    lw      ra, 0x44 (sp)

; extends object table lookup for shop item load after you unpause
.org 0xAF7650
    sw      ra, 0x34 (sp)
    jal extended_object_lookup_shop_unpause
    nop
    lw      ra, 0x34 (sp)

;==================================================================================================
; Cow Shuffle
;==================================================================================================

.orga 0xEF36E4
    jal cow_item_hook
    nop

.orga 0xEF32B8
    jal cow_after_init
    nop
    lw  ra, 0x003C (sp)

.orga 0xEF373C
    jal cow_bottle_check
    nop
    
;==================================================================================================
; Make Bunny Hood like Majora's Mask
;==================================================================================================

; Replaces: mfc1    a1, f12
;           mtc1    t7, f4
.orga 0xBD9A04
    jal bunny_hood
    nop

;==================================================================================================
; Prevent hyrule guards from casuing a softlock if they're culled 
;==================================================================================================
.orga 0xE24E7C
    jal guard_catch
    nop

;==================================================================================================
; Never override Heart Colors
;==================================================================================================

; Replaces:
;   SH A2, 0x020E (V0)
;   SH T9, 0x0212 (V0)
;   SH A0, 0x0216 (V0)
.orga 0xADA8A8
    nop
    nop
    nop

; Replaces:
;   SH T5, 0x0202 (V0)
.orga 0xADA97C
    nop

.orga 0xADA9A8
    nop

.orga 0xADA9BC
    nop


.orga 0xADAA64
    nop

.orga 0xADAA74
    nop
    nop


.orga 0xADABA8
    nop

.orga 0xADABCC
    nop

.orga 0xADABE4
    nop

;==================================================================================================
; Magic Meter Colors
;==================================================================================================
; Replaces: sh  r0, 0x0794 (t6)
;           lw  t7, 0x0000 (v0)
;           sh  r0, 0x0796 (t7)
;           lw  t7, 0x0000 (v0)
;           sh  r0, 0x0798 (t8)
.orga 0xB58320
    sw      ra, 0x0000 (sp)
    jal     magic_colors
    nop
    lw      ra, 0x0000 (sp)
    nop
    

;==================================================================================================
; Add ability to control Lake Hylia's water level
;==================================================================================================
.orga 0xD5B264
    jal Check_Fill_Lake

.orga 0xD5B660
    j   Fill_Lake_Destroy
    nop

.orga 0xEE7E4C
    jal Hit_Gossip_Stone

.orga 0x26C10E3
    .byte 0xFF ; Set generic grotto text ID to load from grotto ID

;==================================================================================================
; Disable trade quest timers in ER
;==================================================================================================
; Replaces: lui     at, 0x800F
;           sw      r0, 0x753C(at)
.orga 0xAE986C ; in memory 8007390C
    j   disable_trade_timers
    lui at, 0x800F

;==================================================================================================
; Remove Shooting gallery actor when entering the room with the wrong age
;==================================================================================================
.orga 0x00D357D4
    jal shooting_gallery_init ; addiu   t6, zero, 0x0001


;==================================================================================================
; static context init hook
;==================================================================================================
.orga 0xAC7AD4
    jal     Static_ctxt_Init

;==================================================================================================
; burning kak from any entrance to kak
;==================================================================================================
; Replaces: lw      t9, 0x0000(s0)
;           addiu   at, 0x01E1
.orga 0xACCD34
    jal     burning_kak
    lw      t9, 0x0000(s0)

;==================================================================================================
; Set the Obtained Epona Flag when winning the 2nd Ingo Race in ER
;==================================================================================================
; Replaces: lw      t9, 0x0024(s0)
;           sw      t9, 0x0000(t7)
.orga 0xD52698
    jal     ingo_race_win
    lw      t9, 0x0024(s0)

;==================================================================================================
; Magic Bean Salesman Shuffle
;==================================================================================================
; Replaces: addu    v0, v0, t7
;           lb      v0, -0x59A4(v0)
.orga 0xE20410
    jal     bean_initial_check
    nop

; Replaces: addu    t0, v0, t9
;           lb      t1, 0x008C(t0)
.orga 0xE206DC
    jal     bean_enough_rupees_check
    nop

; Replaces: addu    t7, t7, t6
;           lb      t7, -0x59A4(t7)
.orga 0xE20798
    jal     bean_rupees_taken
    nop

; Replaces: sw    a0, 0x20(sp)
;           sw    a1, 0x24(sp)
.orga 0xE2076C
    jal     bean_buy_item_hook
    sw      a0, 0x20(sp)

;==================================================================================================
; Load Audioseq using dmadata
;==================================================================================================
; Replaces: lui     a1, 0x0003
;           addiu   a1, a1, -0x6220
.orga 0xB2E82C ; in memory 0x800B88CC
    lw      a1, 0x8000B188

;==================================================================================================
; Load Audiotable using dmadata
;==================================================================================================
; Replaces: lui     a1, 0x0008
;           addiu   a1, a1, -0x6B90
.orga 0xB2E854
    lw      a1, 0x8000B198

;==================================================================================================
; Handle grottos shuffled with other entrances
;==================================================================================================
; Replaces: lui     at, 1
;           addu    at, at, a3
.orga 0xCF73C8
    jal     grotto_entrance
    lui     at, 1

; Replaces: addu    at, at, a3
;           sh      t6, 0x1E1A(at)
.orga 0xBD4C58
    jal     scene_exit_hook
    addu    at, at, a3

;==================================================================================================
; Handle navi grotto attraction
;==================================================================================================

; Replaces: lw      s0, 0x0018($sp)
;           addiu   $sp, $sp, 0x0028
;           jr      $ra
;           nop
.orga 0xCF7158 ; 80959AC8
    or      a0, s0, r0
    lw      s0, 0x0018(sp)
    j       door_ana_init_post
    addiu   sp, sp, 0x0028


; Replaces: sw      t8, 0x0014($sp)
;           sw      a3, 0x0010($sp)
.orga 0xCF72A8 ; 80959C18
    jal     door_ana_becomes_visible_hook
    or      a0, s0, r0
    

; update Actor Flags
;.orga 0xCF7C94
;    .word 0x0A000009

;==================================================================================================
; Getting Caught by Gerudo NPCs in ER
;==================================================================================================
; Replaces: lui     at, 0x0001
;           addu    at, at, a1
.orga 0xE11F90  ; White-clothed Gerudo
    jal     gerudo_caught_entrance
    nop
.orga 0xE9F678  ; Patrolling Gerudo
    jal     gerudo_caught_entrance
    nop
.orga 0xE9F7A8  ; Patrolling Gerudo
    jal     gerudo_caught_entrance
    nop

; Replaces: lui     at, 0x0001
;           addu    at, at, v0
.orga 0xEC1120  ; Gerudo Fighter
    jal     gerudo_caught_entrance
    nop

;==================================================================================================
; Song of Storms Effect Trigger Changes
;==================================================================================================
; Allow a storm to be triggered with the song in any environment
; Replaces: lui     t5, 0x800F
;           lbu     t5, 0x1648(t5)
.orga 0xE6BF4C
    li      t5, 0
    nop

; Remove the internal cooldown between storm effects (to open grottos, grow bean plants...)
; Replaces: bnez     at, 0x80AECC6C
.orga 0xE6BEFC
    nop

;==================================================================================================
; Change the Light Arrow Cutscene trigger condition.
;==================================================================================================
.orga 0xACCE18
    jal     lacs_condition_check
    lw      v0, 0x00A4(s0)
    beqz_a  v1, 0x00ACCE9C
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

;==================================================================================================
; Fix Lab Diving to always be available
;==================================================================================================
; Replaces: lbu     t7, -0x709C(t7)
;           lui     a1, 0x8012
;           addiu   a1, a1, 0xA5D0      ; a1 = save context
;           addu    t8, a1, t7
;           lbu     t9, 0x0074(t8)      ; t9 = owned adult trade item
.orga 0xE2CC1C
    lui     a1, 0x8012
    addiu   a1, a1, 0xA5D0      ; a1 = save context
    lh      t0, 0x0270(s0)      ; t0 = recent diving depth (in meters)
    bne     t0, zero, @skip_eyedrops_dialog
    lbu     t9, 0x008A(a1)      ; t9 = owned adult trade item

.orga 0xE2CC50
@skip_eyedrops_dialog:

;==================================================================================================
; Change Gerudo Guards to respond to the Gerudo's Card, not freeing the carpenters.
;==================================================================================================
; Patrolling Gerudo
.orga 0xE9F598
    lui     t6, 0x8012
    lhu     t7, 0xA674(t6)
    andi    t8, t7, 0x0040
    beqzl   t8, @@return
    move    v0, zero
    li      v0, 1
@@return:
    jr      ra
    nop
    nop
    nop
    nop

; White-clothed Gerudo
.orga 0xE11E94
    lui     v0, 0x8012
    lhu     v0, 0xA674(v0)
    andi    t6, v0, 0x0040
    beqzl   t6, @@return
    move    v0, zero
    li      v0, 1
@@return:
    jr      ra
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

;==================================================================================================
; In Dungeon ER, open Deku Tree's mouth as adult if Mido has been shown the sword/shield.
;==================================================================================================
.orga 0xC72C64
    jal     deku_mouth_condition
    move    a0, s0
    lui     a1, 0x808D
    bnez_a  t7, 0xC72C8C
    nop

;==================================================================================================
; Running Man should fill wallet when trading Bunny Hood.
;==================================================================================================
.orga 0xE50888
    li      a0, 999

;==================================================================================================
; Change relevant checks to Bomb Bag
;==================================================================================================
; Bazaar Shop
; Replaces: lw      t6, -0x73C4(t6)
;           lw      t7, 0x00A4(v0)
.orga 0xC0082C
    li      t6, 0x18
    lw      t7, 0x00A0(v0)

; Goron Shop
; Replaces: lhu     t7, 0x0ED8(v1)
;           andi    t8, t7, 0x0020
.orga 0xC6ED84
    lhu     t7, 0x00A2(v1)
    andi    t8, t7, 0x0018

; Deku Salesman
; Replaces: lw      t6, -0x73C4(t6)
;           lw      t7, 0x00A4(v0)
.orga 0xDF7A90
    li      t6, 0x18
    lw      t7, 0x00A0(v0)

; Bazaar Goron
; Replaces: lw      t6, -0x73C4(t6)
;           lw      t7, 0x00A4(a2)
.orga 0xED5A28
    li      t6, 0x18
    lw      t7, 0x00A0(a2)

;==================================================================================================
; HUD Rupee Icon color
;==================================================================================================
; Replaces: lui     at, 0xC8FF
;           addiu   t8, s1, 0x0008
;           sw      t8, 0x02B0(s4)
;           sw      t9, 0x0000(s1)
;           lhu     t4, 0x0252(s7)
;           ori     at, at, 0x6400      ; at = HUD Rupee Icon Color
.orga 0xAEB764
    addiu   t8, s1, 0x0008
    sw      t8, 0x02B0(s4)
    jal     rupee_hud_color
    sw      t9, 0x0000(s1)
    lhu     t4, 0x0252(s7)
    move    at, v0
    
;==================================================================================================
; Expand Audio Thread memory
;==================================================================================================

.headersize (0x800110A0 - 0xA87000)

//reserve the audio thread's heap
.org 0x800C7DDC 
.area 0x1C
    lui     at, hi(AUDIO_THREAD_INFO_MEM_START)
    lw      a0, lo(AUDIO_THREAD_INFO_MEM_START)(at)
    jal     0x800B8654
    lw      a1, lo(AUDIO_THREAD_INFO_MEM_SIZE)(at)
    lw      ra, 0x0014(sp)
    jr      ra
    addiu   sp, sp, 0x0018
.endarea

//allocate memory for fanfares and primary/secondary bgm
.org 0x800B5528
.area 0x18, 0
    jal     get_audio_pointers
.endarea

.org 0x800B5590
.area (0xE0 - 0x90), 0
    li      a0, 0x80128A50
    li      a1, AUDIO_THREAD_INFO
    jal     0x80057030 //memcopy
    li      a2, 0x18
    li      a0, 0x80128A50
    jal     0x800B3D18
    nop
    li      a0, 0x80128A5C
    jal     0x800B3DDC
    nop
.endarea

.headersize 0

;==================================================================================================
; King Zora Init Moved Check Override
;==================================================================================================
; Replaces: lhu     t0, 0x0EDA(v0)
;           or      a0, s0, zero
;           andi    t1, t0, 0x0008
.orga 0xE565D0
    jal     kz_moved_check
    nop
    or      a0, s0, zero
