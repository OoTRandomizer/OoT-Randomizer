;==================================================================================================
; Item data
;==================================================================================================

; Dungeon indexes, used with the dungeon item / small key tables in the save context
DEKU_ID    equ 0
DODONGO_ID equ 1
JABU_ID    equ 2
FOREST_ID  equ 3
FIRE_ID    equ 4
WATER_ID   equ 5
SPIRIT_ID  equ 6
SHADOW_ID  equ 7
BOTW_ID    equ 8
ICE_ID     equ 9
TOWER_ID   equ 10
GTG_ID     equ 11
FORT_ID    equ 12
CASTLE_ID  equ 13

.definelabel ITEM_TABLE_ROW_SIZE, 0x10

.macro Item_Row, base_item, action_id, graphic_id, text_id, object_id, upgrade_fn, effect_fn, effect_arg1, effect_arg2
  .byte     base_item   ; 0x00
  .byte     action_id   ; 0x01
  .byte     graphic_id  ; 0x02
  .byte     text_id     ; 0x03
  .halfword object_id   ; 0x04
  .byte     effect_arg1 ; 0x06
  .byte     effect_arg2 ; 0x07
  .word     effect_fn   ; 0x08
  .word     upgrade_fn  ; 0x0C
.endmacro

ITEM_ROW_BASE_ITEM   equ 0x00
ITEM_ROW_ACTION_ID   equ 0x01
ITEM_ROW_GRAPHIC_ID  equ 0x02
ITEM_ROW_TEXT_ID     equ 0x03
ITEM_ROW_OBJECT_ID   equ 0x04
ITEM_ROW_EFFECT_ARG1 equ 0x06
ITEM_ROW_EFFECT_ARG2 equ 0x07
ITEM_ROW_EFFECT_FN   equ 0x08
ITEM_ROW_UPGRADE_FN  equ 0x0C
ITEM_ROW_IS_EXTENDED equ 0x0C ; This offset is repurposed after the upgrades are resolved

; The "base item" mostly controls the sound effect made when you receive the item. It should be
; set to something that doesn't break NPCs.

; Action ID 0x41 (give kokiri tunic) is used to indicate no action.

ITEM_TABLE:
Item_Row -1, -1, -1, -1, -1, hookshot_upgrade,  no_effect, -1, -1 ; 0x80 = Progressive Hookshot
Item_Row -1, -1, -1, -1, -1, strength_upgrade,  no_effect, -1, -1 ; 0x81 = Progressive Strength
Item_Row -1, -1, -1, -1, -1, bomb_bag_upgrade,  no_effect, -1, -1 ; 0x82 = Progressive Bomb Bag
Item_Row -1, -1, -1, -1, -1, bow_upgrade,       no_effect, -1, -1 ; 0x83 = Progressive Bow
Item_Row -1, -1, -1, -1, -1, slingshot_upgrade, no_effect, -1, -1 ; 0x84 = Progressive Slingshot
Item_Row -1, -1, -1, -1, -1, wallet_upgrade,    no_effect, -1, -1 ; 0x85 = Progressive Wallet
Item_Row -1, -1, -1, -1, -1, scale_upgrade,     no_effect, -1, -1 ; 0x86 = Progressive Scale
Item_Row -1, -1, -1, -1, -1, nut_upgrade,       no_effect, -1, -1 ; 0x87 = Progressive Nut Capacity
Item_Row -1, -1, -1, -1, -1, stick_upgrade,     no_effect, -1, -1 ; 0x88 = Progressive Stick Capacity

Item_Row 0x53, 0x41, 0x38, 0x43, 0x00EB, no_upgrade, give_bottle, 0x15, -1 ; 0x89 = Bottle with Red Potion
Item_Row 0x53, 0x41, 0x37, 0x44, 0x00EB, no_upgrade, give_bottle, 0x16, -1 ; 0x8A = Bottle with Green Potion
Item_Row 0x53, 0x41, 0x39, 0x45, 0x00EB, no_upgrade, give_bottle, 0x17, -1 ; 0x8B = Bottle with Blue Potion
Item_Row 0x53, 0x41, 0x6B, 0x46, 0x0177, no_upgrade, give_bottle, 0x18, -1 ; 0x8C = Bottle with Fairy
Item_Row 0x53, 0x41, 0x3F, 0x47, 0x00F4, no_upgrade, give_bottle, 0x19, -1 ; 0x8D = Bottle with Fish
Item_Row 0x53, 0x41, 0x67, 0x5D, 0x0173, no_upgrade, give_bottle, 0x1C, -1 ; 0x8E = Bottle with Blue Fire
Item_Row 0x53, 0x41, 0x68, 0x7A, 0x0174, no_upgrade, give_bottle, 0x1D, -1 ; 0x8F = Bottle with Bugs
Item_Row 0x53, 0x41, 0x70, 0xF9, 0x0176, no_upgrade, give_bottle, 0x1E, -1 ; 0x90 = Bottle with Big Poe
Item_Row 0x53, 0x41, 0x6A, 0x97, 0x0176, no_upgrade, give_bottle, 0x20, -1 ; 0x91 = Bottle with Poe

Item_Row 0x53, 0x41, 0x0A, 0x06, 0x00B9, no_upgrade, give_dungeon_item, 0x01, FOREST_ID  ; 0x92 = Forest Temple Boss Key
Item_Row 0x53, 0x41, 0x0A, 0x1C, 0x00B9, no_upgrade, give_dungeon_item, 0x01, FIRE_ID    ; 0x93 = Fire Temple Boss Key
Item_Row 0x53, 0x41, 0x0A, 0x1D, 0x00B9, no_upgrade, give_dungeon_item, 0x01, WATER_ID   ; 0x94 = Water Temple Boss Key
Item_Row 0x53, 0x41, 0x0A, 0x1E, 0x00B9, no_upgrade, give_dungeon_item, 0x01, SPIRIT_ID  ; 0x95 = Spirit Temple Boss Key
Item_Row 0x53, 0x41, 0x0A, 0x2A, 0x00B9, no_upgrade, give_dungeon_item, 0x01, SHADOW_ID  ; 0x96 = Shadow Temple Boss Key
Item_Row 0x53, 0x41, 0x0A, 0x61, 0x00B9, no_upgrade, give_dungeon_item, 0x01, TOWER_ID   ; 0x97 = Ganon's Castle Boss Key

Item_Row 0x53, 0x41, 0x0B, 0x62, 0x00B8, no_upgrade, give_dungeon_item, 0x02, DEKU_ID    ; 0x98 = Deku Tree Compass
Item_Row 0x53, 0x41, 0x0B, 0x63, 0x00B8, no_upgrade, give_dungeon_item, 0x02, DODONGO_ID ; 0x99 = Dodongo's Cavern Compass
Item_Row 0x53, 0x41, 0x0B, 0x64, 0x00B8, no_upgrade, give_dungeon_item, 0x02, JABU_ID    ; 0x9A = Jabu Jabu Compass
Item_Row 0x53, 0x41, 0x0B, 0x65, 0x00B8, no_upgrade, give_dungeon_item, 0x02, FOREST_ID  ; 0x9B = Forest Temple Compass
Item_Row 0x53, 0x41, 0x0B, 0x7C, 0x00B8, no_upgrade, give_dungeon_item, 0x02, FIRE_ID    ; 0x9C = Fire Temple Compass
Item_Row 0x53, 0x41, 0x0B, 0x7D, 0x00B8, no_upgrade, give_dungeon_item, 0x02, WATER_ID   ; 0x9D = Water Temple Compass
Item_Row 0x53, 0x41, 0x0B, 0x7E, 0x00B8, no_upgrade, give_dungeon_item, 0x02, SPIRIT_ID  ; 0x9E = Spirit Temple Compass
Item_Row 0x53, 0x41, 0x0B, 0x7F, 0x00B8, no_upgrade, give_dungeon_item, 0x02, SHADOW_ID  ; 0x9F = Shadow Temple Compass
Item_Row 0x53, 0x41, 0x0B, 0xA2, 0x00B8, no_upgrade, give_dungeon_item, 0x02, BOTW_ID    ; 0xA0 = Bottom of the Well Compass
Item_Row 0x53, 0x41, 0x0B, 0x87, 0x00B8, no_upgrade, give_dungeon_item, 0x02, ICE_ID     ; 0xA1 = Ice Cavern Compass

Item_Row 0x53, 0x41, 0x1C, 0x88, 0x00C8, no_upgrade, give_dungeon_item, 0x04, DEKU_ID    ; 0xA2 = Deku Tree Map
Item_Row 0x53, 0x41, 0x1C, 0x89, 0x00C8, no_upgrade, give_dungeon_item, 0x04, DODONGO_ID ; 0xA3 = Dodongo's Cavern Map
Item_Row 0x53, 0x41, 0x1C, 0x8A, 0x00C8, no_upgrade, give_dungeon_item, 0x04, JABU_ID    ; 0xA4 = Jabu Jabu Map
Item_Row 0x53, 0x41, 0x1C, 0x8B, 0x00C8, no_upgrade, give_dungeon_item, 0x04, FOREST_ID  ; 0xA5 = Forest Temple Map
Item_Row 0x53, 0x41, 0x1C, 0x8C, 0x00C8, no_upgrade, give_dungeon_item, 0x04, FIRE_ID    ; 0xA6 = Fire Temple Map
Item_Row 0x53, 0x41, 0x1C, 0x8E, 0x00C8, no_upgrade, give_dungeon_item, 0x04, WATER_ID   ; 0xA7 = Water Temple Map
Item_Row 0x53, 0x41, 0x1C, 0x8F, 0x00C8, no_upgrade, give_dungeon_item, 0x04, SPIRIT_ID  ; 0xA8 = Spirit Temple Map
Item_Row 0x53, 0x41, 0x1C, 0xA3, 0x00C8, no_upgrade, give_dungeon_item, 0x04, SHADOW_ID  ; 0xA9 = Shadow Temple Map
Item_Row 0x53, 0x41, 0x1C, 0xA5, 0x00C8, no_upgrade, give_dungeon_item, 0x04, BOTW_ID    ; 0xAA = Bottom of the Well Map
Item_Row 0x53, 0x41, 0x1C, 0x92, 0x00C8, no_upgrade, give_dungeon_item, 0x04, ICE_ID     ; 0xAB = Ice Cavern Map

Item_Row 0x53, 0x41, 0x02, 0x93, 0x00AA, no_upgrade, give_small_key, FOREST_ID, -1 ; 0xAC = Forest Temple Small Key
Item_Row 0x53, 0x41, 0x02, 0x94, 0x00AA, no_upgrade, give_small_key, FIRE_ID,   -1 ; 0xAD = Fire Temple Small Key
Item_Row 0x53, 0x41, 0x02, 0x95, 0x00AA, no_upgrade, give_small_key, WATER_ID,  -1 ; 0xAE = Water Temple Small Key
Item_Row 0x53, 0x41, 0x02, 0xA6, 0x00AA, no_upgrade, give_small_key, SPIRIT_ID, -1 ; 0xAF = Spirit Temple Small Key
Item_Row 0x53, 0x41, 0x02, 0xA9, 0x00AA, no_upgrade, give_small_key, SHADOW_ID, -1 ; 0xB0 = Shadow Temple Small Key
Item_Row 0x53, 0x41, 0x02, 0x9B, 0x00AA, no_upgrade, give_small_key, BOTW_ID,   -1 ; 0xB1 = Bottom of the Well Small Key
Item_Row 0x53, 0x41, 0x02, 0x9F, 0x00AA, no_upgrade, give_small_key, GTG_ID,    -1 ; 0xB2 = Gerudo Training Small Key
Item_Row 0x53, 0x41, 0x02, 0xA0, 0x00AA, no_upgrade, give_small_key, FORT_ID,   -1 ; 0xB3 = Gerudo Fortress Small Key
Item_Row 0x53, 0x41, 0x02, 0xA1, 0x00AA, no_upgrade, give_small_key, CASTLE_ID, -1 ; 0xB4 = Ganon's Castle Small Key

Item_Row 0x53, 0x3D, 0x43, 0x0C, 0x00F8, no_upgrade, give_biggoron_sword, -1, -1 ; 0xB5 = Biggoron Sword

Item_Row 0x4D, 0x83, 0xF7, 0x55, 0x00B7, no_upgrade,      no_effect, -1, -1 ; 0xB6 = Recovery Heart
Item_Row 0x4D, 0x92, 0xDB, 0xE6, 0x00D8, arrows_to_rupee, no_effect, -1, -1 ; 0xB7 = Arrows (5)
Item_Row 0x4D, 0x93, 0xDA, 0xE6, 0x00D8, arrows_to_rupee, no_effect, -1, -1 ; 0xB8 = Arrows (10)
Item_Row 0x4D, 0x94, 0xD9, 0xE6, 0x00D8, arrows_to_rupee, no_effect, -1, -1 ; 0xB9 = Arrows (30)
Item_Row 0x4D, 0x8E, 0xE0, 0x32, 0x00CE, bombs_to_rupee,  no_effect, -1, -1 ; 0xBA = Bombs (5)
Item_Row 0x4D, 0x8F, 0xE0, 0x32, 0x00CE, bombs_to_rupee,  no_effect, -1, -1 ; 0xBB = Bombs (10)
Item_Row 0x4D, 0x90, 0xE0, 0x32, 0x00CE, bombs_to_rupee,  no_effect, -1, -1 ; 0xBC = Bombs (20)
Item_Row 0x4D, 0x8C, 0xEE, 0x34, 0x00BB, no_upgrade,      no_effect, -1, -1 ; 0xBD = Deku Nuts (5)
Item_Row 0x4D, 0x8D, 0xEE, 0x34, 0x00BB, no_upgrade,      no_effect, -1, -1 ; 0xBE = Deku Nuts (10)

Item_Row 0x4F, 0x41, 0x13, 0xE9, 0x00BD, no_upgrade,    give_defense, -1, -1 ; 0xBF = Double Defense
Item_Row 0x4F, 0x41, 0x1E, 0xE4, 0x00CD, magic_upgrade, give_magic,   -1, -1 ; 0xC0 = Progressive Magic Meter
Item_Row 0x4F, 0x41, 0x1F, 0xE8, 0x00CD, no_upgrade,    double_magic, -1, -1 ; 0xC1 = Double Magic

Item_Row -1, -1, -1, -1, -1, bombchu_upgrade,  no_effect, -1, -1 ; 0xC2 = Progressive Bombchus
Item_Row 0x53, 0x41, 0x46, 0x4A, 0x010E, ocarina_upgrade,  give_fairy_ocarina, -1, -1 ; 0xC3 = Progressive Ocarina

Item_Row 0x53, 0x41, 0x03, 0xB0, 0x00B6, no_upgrade, give_song, 6, -1  ; 0xC4 = Minuet of Forest
Item_Row 0x53, 0x41, 0x04, 0xB1, 0x00B6, no_upgrade, give_song, 7, -1  ; 0xC5 = Bolero of Fire
Item_Row 0x53, 0x41, 0x05, 0xB2, 0x00B6, no_upgrade, give_song, 8, -1  ; 0xC6 = Serenade of Water
Item_Row 0x53, 0x41, 0x06, 0xB3, 0x00B6, no_upgrade, give_song, 9, -1  ; 0xC7 = Requiem of Spirit
Item_Row 0x53, 0x41, 0x07, 0xB6, 0x00B6, no_upgrade, give_song, 10, -1 ; 0xC8 = Nocturn of Shadow
Item_Row 0x53, 0x41, 0x08, 0xB7, 0x00B6, no_upgrade, give_song, 11, -1 ; 0xC9 = Prelude of Light

Item_Row 0x53, 0x41, 0x04, 0xB8, 0x00B6, no_upgrade, give_song, 12, -1 ; 0xCA = Zelda's Lullaby
Item_Row 0x53, 0x41, 0x06, 0xB9, 0x00B6, no_upgrade, give_song, 13, -1 ; 0xCB = Epona's Song
Item_Row 0x53, 0x41, 0x03, 0xBA, 0x00B6, no_upgrade, give_song, 14, -1 ; 0xCC = Saria's Song
Item_Row 0x53, 0x41, 0x08, 0xBB, 0x00B6, no_upgrade, give_song, 15, -1 ; 0xCD = Sun's Song
Item_Row 0x53, 0x41, 0x05, 0xBC, 0x00B6, no_upgrade, give_song, 16, -1 ; 0xCE = Song of Time
Item_Row 0x53, 0x41, 0x07, 0xBD, 0x00B6, no_upgrade, give_song, 17, -1 ; 0xCF = Song of Storms

;==================================================================================================
; Item upgrade functions
;==================================================================================================

no_upgrade:
    jr      ra
    ori     v0, a1, 0

;==================================================================================================

hookshot_upgrade:
    lbu     t0, 0x7D (a0) ; Load hookshot from inventory

    beq     t0, 0xFF, @@return
    li      v0, 0x08 ; Hookshot

    li      v0, 0x09 ; Longshot

@@return:
    jr      ra
    nop

;==================================================================================================

strength_upgrade:
    lbu     t0, 0xA3 (a0) ; Load strength from inventory
    andi    t0, t0, 0xC0 ; Mask bits to isolate strength

    beqz    t0, @@return
    li      v0, 0x54 ; Goron Bracelet

    beq     t0, 0x40, @@return
    li      v0, 0x35 ; Silver Gauntlets

    li      v0, 0x36 ; Gold Gauntlets

@@return:
    jr      ra
    nop

;==================================================================================================

bomb_bag_upgrade:
    lbu     t0, 0xA3 (a0) ; Load bomb bag from inventory
    andi    t0, t0, 0x18 ; Mask bits to isolate bomb bag

    beqz    t0, @@return
    li      v0, 0x32 ; Bomb Bag

    beq     t0, 0x08, @@return
    li      v0, 0x33 ; Bigger Bomb Bag

    li      v0, 0x34 ; Biggest Bomb Bag

@@return:
    jr      ra
    nop

;==================================================================================================

bow_upgrade:
    lbu     t0, 0xA3 (a0) ; Load quiver from inventory
    andi    t0, t0, 0x03 ; Mask bits to isolate quiver

    beqz    t0, @@return
    li      v0, 0x04 ; Bow

    beq     t0, 0x01, @@return
    li      v0, 0x30 ; Big Quiver

    li      v0, 0x31 ; Biggest Quiver

@@return:
    jr      ra
    nop

;==================================================================================================

slingshot_upgrade:
    lbu     t0, 0xA2 (a0) ; Load bullet bag from inventory
    andi    t0, t0, 0xC0 ; Mask bits to isolate bullet bag

    beqz    t0, @@return
    li      v0, 0x05 ; Slingshot

    beq     t0, 0x40, @@return
    li      v0, 0x60 ; Bullet Bag (40)

    li      v0, 0x7B ; Bullet Bag (50)

@@return:
    jr      ra
    nop

;==================================================================================================

wallet_upgrade:
    lbu     t0, 0xA2 (a0) ; Load wallet from inventory
    andi    t0, t0, 0x30 ; Mask bits to isolate wallet

    beqz    t0, @@return
    li      v0, 0x45 ; Adult's Wallet

    li      v0, 0x46 ; Giant's Wallet

@@return:
    jr      ra
    nop

;==================================================================================================

scale_upgrade:
    lbu     t0, 0xA2 (a0) ; Load scale from inventory
    andi    t0, t0, 0x06 ; # Mask bits to isolate scale

    beqz    t0, @@return
    li      v0, 0x37 ; Silver Scale

    li      v0, 0x38 ; Gold Scale

@@return:
    jr      ra
    nop

;==================================================================================================

nut_upgrade:
    lbu     t0, 0xA1 (a0) ; Load nut limit from inventory
    andi    t0, t0, 0x20 ; Mask bits to isolate nut limit, upper bit only

    beqz    t0, @@return
    li      v0, 0x79 ; 30 Nuts

    li      v0, 0x7A ; 40 Nuts

@@return:
    jr      ra
    nop

;==================================================================================================

stick_upgrade:
    lbu     t0, 0xA1 (a0) ; Load stick limit from inventory
    andi    t0, t0, 0x04 ; Mask bits to isolate stick limit, upper bit only

    beqz    t0, @@return
    li      v0, 0x77 ; 20 Sticks

    li      v0, 0x78 ; 30 Sticks

@@return:
    jr      ra
    nop

;==================================================================================================

magic_upgrade:
    lbu     t0, 0x32 (a0) ; Load magic level from inventory

    beqz    t0, @@return
    li      v0, 0xC0 ; Single Magic

    li      v0, 0xC1 ; Double Magic

@@return:
    jr      ra
    nop

;==================================================================================================

arrows_to_rupee:
    lbu     t0, 0xA3 (a0) ; Load quiver from inventory
    andi    t0, t0, 0x03 ; Mask bits to isolate quiver

    beqz    t0, @@return
    li      v0, 0x4D ; Blue Rupee

    ori     v0, a1, 0

@@return:
    jr      ra
    nop

;==================================================================================================

bombs_to_rupee:
    lbu     t0, 0xA3 (a0) ; Load bomb bag from inventory
    andi    t0, t0, 0x18 ; Mask bits to isolate bomb bag

    beqz    t0, @@return
    li      v0, 0x4D ; Blue Rupee

    ori     v0, a1, 0

@@return:
    jr      ra
    nop

;==================================================================================================
; Item effect functions
;==================================================================================================

no_effect:
    jr      ra
    nop

;==================================================================================================

give_biggoron_sword:
    ; a0 = save context
    li      t0, 0x01
    sb      t0, 0x3E (a0) ; Set flag to make the sword durable
    jr      ra
    nop

;==================================================================================================

give_bottle:
    ; a0 = save context
    ; a1 = item code to store
    addiu   t0, a0, 0x86 ; t0 = First bottle slot
    li      t1, -1 ; t1 = Bottle slot offset

@@loop:
    addiu   t1, t1, 1
    bgt     t1, 3, @@return ; No free bottle slots
    nop

    ; Check whether slot is full
    addu    t2, t0, t1
    lbu     t3, 0x00 (t2)
    bne     t3, 0xFF, @@loop
    nop

    ; Found an open slot
    sb      a1, 0x00 (t2)

@@return:
    jr      ra
    nop

;==================================================================================================

give_dungeon_item:
    ; a0 = save context
    ; a1 = mask (0x01 = boss key, 0x02 = compass, 0x04 = map)
    ; a2 = dungeon index
    addiu   t0, a0, 0xA8
    addu    t0, t0, a2 ; t0 = address of this dungeon's items
    lbu     t1, 0x00 (t0)
    or      t1, t1, a1
    sb      t1, 0x00 (t0)
    jr      ra
    nop

;==================================================================================================

give_small_key:
    ; a0 = save context
    ; a1 = dungeon index
    addiu   t0, a0, 0xBC
    addu    t0, t0, a1 ; t0 = address of this dungeon's key count
    lb      t1, 0x00 (t0)
    bgez    t1, @not_negative
    nop
    li      t1, 0x00
@not_negative:
    addiu   t1, t1, 1
    sb      t1, 0x00 (t0)
    jr      ra
    nop

;==================================================================================================

give_defense:
    ; a0 = save context
    li      t0, 0x01
    sb      t0, 0x3D (a0) ; Set double defense flag
    li      t0, 0x14
    sb      t0, 0xCF (a0) ; Set number of hearts to display as double defense
    li      t0, 0x0140
    sh      t0, 0x1424 (a0) ; Give health refill
    jr      ra
    nop

give_magic:
    ; a0 = save context
    li      t0, 1
    sb      t0, 0x32 (a0) ; Set meter level
    sb      t0, 0x3A (a0) ; Required for meter to persist on save load
    li      t0, 0x30
    sh      t0, 0x13F4 (a0) ; Set meter size
    sb      t0, 0x33 (a0) ; Fill meter
    jr      ra
    nop

double_magic:
    ; a0 = save context
    li      t0, 2
    sb      t0, 0x32 (a0) ; Set meter level
    li      t0, 1
    sb      t0, 0x3A (a0) ; Required for meter to persist on save load
    sb      t0, 0x3C (a0) ; Required for meter to persist on save load
    li      t0, 0x60
    sh      t0, 0x13F4 (a0) ; Set meter size
    sb      t0, 0x33 (a0) ; Fill meter
    jr      ra
    nop

;==================================================================================================

bombchu_upgrade:
    lbu     t0, 0x7C (a0) ; Load bomchu from inventory
    beq     t0, 0xFF, @@return
    li      v0, 0x6B ; Bombchu 20 pack

    lbu     t0, 0x94 (a0) ; Load bombchu count from inventory
    sltiu   t0, t0, 0x06
    beqz    t0, @@return  ; if 
    li      v0, 0x6A ; Bombchu 5 Pack

    li      v0, 0x03 ; Bombchu 10 Pack

@@return:
    jr      ra
    nop

;==================================================================================================

ocarina_upgrade:
    lbu     t0, 0x7B (a0) ; Load ocarina from inventory

    beq     t0, 0xFF, @@return
    ori     v0, a1, 0 ; Fairy Ocarina (unchanged)

    li      v0, 0x0C ; Ocarina of Time

@@return:
    jr      ra
    nop

give_fairy_ocarina:
    ; a0 = save context
    li      t0, 0x07
    sb      t0, 0x7B (a0)
    jr      ra
    nop

;==================================================================================================

give_song:
    ; a0 = save context
    ; a1 = quest bit
    li      t0, 1
    sllv    t0, t0, a1
    lw      t1, 0xA4(a0)
    or      t1, t1, t0
    sw      t1, 0xA4(a0)
    jr      ra
    nop
