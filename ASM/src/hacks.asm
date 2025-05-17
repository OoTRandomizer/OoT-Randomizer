;==================================================================================================
; main.c hooks
;==================================================================================================
.headersize (0x800110A0 - 0xA87000)

; Runs before the game state update function
; Replaces:
;   lw      t6, 0x0018 (sp)
;   lui     at, 0x8010
.org 0x8009CAD4
    jal     before_game_state_update_hook
    nop

; Runs after the game state update function
; Replaces:
;   jr      ra
;   nop
.org 0x8009CB00
    j       after_game_state_update
    nop

;
.org 0x8009CED0
    jal     before_skybox_init

.org 0x8009CDA0
Gameplay_InitSkybox:

; Runs after scene init
; Replaces:
;   jr      ra
;   nop
.org 0x8009CEE4
    j       after_scene_init
    nop

;==================================================================================================
; Expand Audio Thread memory
;==================================================================================================

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

;==================================================================================================
; Increase Number of Audio Banks, and Audiotable (samples)
;==================================================================================================

.org 0x800B8888
    lui     t2, hi(AUDIOBANK_TABLE_EXTENDED)
.org 0x800B8898
    addiu   t2, t2, lo(AUDIOBANK_TABLE_EXTENDED)

; Hacks to increase the number of audio banks from 0x30 to 0x80
; Hacks in AudioHeap_ResetLoadStatus
; This loop is annoying because it hardcodes the start and end addresses of fontLoadStatus array instead of calculating it.
; v0 - start of array
; v1 - end of array
.org 0x800B3540
    ; Replaces
    ; lui   v1, 0x8012
    ; lui   v0, 0x8012
    ; addiu v0, v0 0x5660
    ; addiu v1, v1, 0x5630
    li      v1, FONTLOADSTATUS_EXTENDED
    li      v0, FONTLOADSTATUS_EXTENDED + 0xA0

.org 0x800B3554
    ; Replaces:
    ; lbu   t6, 0x3468(v1)
    lbu     t6, 0x00(v1)

.org 0x800B3560
    ; Replaces:
    ; sb    r0, 0x3468(v1)
    sb      r0, 0x00(v1)

; Hacks in AudioHeap_PopPersistentCache (I think)
.org 0x800B3AB8
    ; Replaces:
    ; lui   t7, 0x8013
    ; addiu t7, t7, 0x8A98
    li  t7, FONTLOADSTATUS_EXTENDED

; Hacks in AudioHeap_AllocCached (I think)
.org 0x800B3F00
    ; Replaces:
    ; lui   t3, 0x8013
    lui     t3, hi(FONTLOADSTATUS_EXTENDED)
.org 0x800B3F0C
    ; Replaces:
    ; addiu t3, t3, 0x8A98
    addiu   t3, t3, lo(FONTLOADSTATUS_EXTENDED)

; Hacks in AudioLoad_IsFontLoadComplete
.org 0x800B6E8C
; Replaces:
;   lui     t6, 0x8013
;   addu    t6, t6, a1
;   lbu     t6, 0x8A98(t6)
    lui     t6, hi(FONTLOADSTATUS_EXTENDED)
    addu    t6, t6, a1
    lbu     t6, lo(FONTLOADSTATUS_EXTENDED)(t6)
.org 0x800B6EB4
; Replaces:
;   lui     t7, 0x8013
;   addu    t7, t7, v0
;   lbu     t7, 0x8A98(t7)
    lui     t7, hi(FONTLOADSTATUS_EXTENDED)
    addu    t7, t7, v0
    lbu     t7, lo(FONTLOADSTATUS_EXTENDED)(t7)

; Hacks in AudioLoad_SetFontLoadStatus
.org 0x800B6FE0
; Replaces:
;   lui     t6, 0x8012
;   addiu   t6, t6, 0x5630
;   skip
;   lbu     t7, 0x3468(v0)
;   skip
;   skip
;   skip
;   sb      a1, 0x3468(v0)
    li      t6, FONTLOADSTATUS_EXTENDED
.skip 4
    lbu     t7, 0x00(v0)
.skip 12
    sb      a1, 0x00(v0)

; Hacks in AudioLoad_SyncLoadFont
.org 0x800B7A2C
; Replaces:
;   lui     a1, 0x8012
;   addiu   a1, a1, 0x5630
;   addu    t6, a1, v0
    jal     AudioLoad_SyncLoadFont_StatusHack
    lui     a1, 0x8012
    nop
    lbu     t7, 0x00(t6)

; Hacks in AudioLoad_AsyncLoadInner
.org 0x800B82D0
; Replaces:
;   lui     t7, 0x8013
    lui     t7, hi(FONTLOADSTATUS_EXTENDED)
.org 0x800B8310
; Replaces:
;   addu    t7, t7, v0
;   lbu     t7, 0x8A98(t7)
    addu    t7, t7, v0
    lbu     t7, lo(FONTLOADSTATUS_EXTENDED)(t7)

;==================================================================================================
; Don't Use Sandstorm Transition if gameplay_field_keep is not loaded
;==================================================================================================

.org 0x8009A2B0
.area (0x8009A340 - 0x8009A2B0), 0
    //a0 = Global Context
    //a1 = screen transition effect
    addiu   sp, sp, 0xFFE0
    sw      ra, 0x0014(sp)
    sw      a0, 0x0020(sp)
    andi    t0, a1, -2 //drop least significant bit so that we can test for 0x0E and 0x0F
    li      at, 0x000E //sandstorm effect
    bne     t0, at, @skip_check
    sw      a1, 0x0024(sp)

    b       @check_if_object_loaded
    nop
@return_check_if_object_loaded:

    bgez    v0, @skip_check
    li      at, 0x04            //replacement transition effect
    sw      at, 0x0024(sp)

@skip_check:
    lw      a2, 0x0020(sp)
    li      at, 0x121C8
    addu    a0, a2, at
    sw      a0, 0x0018(sp)
    jal     0x80002E80
    addiu   a1, r0, 0x0250

    //replacement
    lw      v0, 0x0024(sp)
    lw      a0, 0x0018(sp)
    lw      a2, 0x0020(sp)
    addiu   at, r0, 0x0001
    sra     t6, v0, 5
    bne     t6, at, @b_0x8009A368
    sw      v0, 0x0228(a0)

    lui     at, 0x800A
    addiu   t7, at, 0x8DEC
    addiu   t8, at, 0x8E18
    addiu   t9, at, 0x8C00
    addiu   t0, at, 0x9244
    addiu   t1, at, 0x8FA8
    addiu   t2, at, 0x8E24
    addiu   t3, at, 0x9250
    addiu   t4, at, 0x92A8
    addiu   t5, at, 0x92B4
.endarea

.org 0x8009A368
@b_0x8009A368:
; Resumes normal execution, hits transition effect jump table

.org 0x8009A390
.area (0x8009A3D0 - 0x8009A390), 0
; Here we overwrite part of transition effect case 0

@check_if_object_loaded:

    li      at, 0x117A4 //object table
    addu    a0, a0, at
    jal     0x80081628          //check if object file is loaded
    addiu   a1, r0, 0x02        //gameplay_field_keep
    b       @return_check_if_object_loaded
    nop

; Optimize transition effect 0 so that the routine above still fits in the function
@transition_0_jump:
    lui     at, 0x800A
    addiu   t7, at, 0x8218
    addiu   t8, at, 0x82B8
    addiu   t9, at, 0x81E0
    addiu   t0, at, 0x8700
    addiu   t1, at, 0x83FC
    addiu   t2, at, 0x82C4
    addiu   t3, at, 0x83E4
    addiu   t4, at, 0x83D8
.endarea

; Update the jump table pointer to transition effect 0

.org 0x80108CEC
.word @transition_0_jump

;==================================================================================================
; Skip using collision poly check table (performance optimization)
;==================================================================================================
; Instead some polys may be checked multiple times in a single line check, which is faster than
; using the table, particularly in large scenes.

; Skip loading the address of the table
; Replaces lw       a3, 0x004C(s2)
.org 0x8002D1E8
    nop

; Skip lookup
; Replaces lbu      t8, 0x0000(v1)
.org 0x8002D210
    li      t8, 0

; Skip updating the table
; Replaces beqz     v0, 0x8002D264
.org 0x8002D238
    beqz    v0, 0x8002D26C
; Replaces bnezl    t6, 0x8002D268
.org 0x8002D248
    bnezl   t6, 0x8002D26C

; Skip resetting the table
; Replaces:
;   lw      t0, 0x0000(s2)
;   jal     0x80033FF0
;   lhu     a1, 0x0014(t0)
.org 0x800302E8
    nop
    nop
    nop

.headersize 0

;==================================================================================================
; Remove Kokiri Sword Safety
;==================================================================================================

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
;   lui/addiu a1, 0x8011A5D0 (start of Inventory_SwapAgeEquipment)
.orga 0xAE5764
    j       before_time_travel
    nop

; After time travel
; Replaces:
;   jr      ra
.orga 0xAE59E0 ; In memory: 0x8006FA80 (end of Inventory_SwapAgeEquipment)
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
; Speed up armos push
;==================================================================================================
; In EnAm_Statue, subtract 0x1000 from this->unk_258 instead of 0x800
; This value is used as the timer for how long to push for
; This halves the number of frames that the push will occur over.
;replaces
;addiu t0, a2, 0xF800
.orga 0xC97C68
    addiu t0, a2, 0xF000

; 1.00973892212 is used instead of 1 because we are setting a speed based on sin(unk_258). When this is discretized and summed up over the duration movement, 1 does not cause the proper amount of movement.

; In EnAm_Statue, when calculating the speed, multiply by 1.00973892212 instead of 0.5 (first instance, used for collision detection?)
.orga 0xC97D68
;   replaces
;   lui     at, 0x3F00
;   mtc1    at, f8
    jal     en_am_calculation_1
    nop

; In EnAm_Statue, when calculating the speed, multiply by 1.00973892212 instead of 0.5
.orga 0xC97E20
    ;replaces
    ;lui at, 0x3F00
    ;mtc1 at, f10
    jal     en_am_calculation_2
    nop

;==================================================================================================
; Item Overrides
;==================================================================================================

; Patch NPCs to give override-compatible items
.orga 0xDB13D3 :: .byte 0x76 ; Frogs Ocarina Game
.orga 0xDF2647 :: .byte 0x76 ; Ocarina memory game
.orga 0xE2F093 :: .byte 0x34 ; Market Bombchu Bowling Bomb Bag
.orga 0xEC9CE7 :: .byte 0x7A ; Deku Theater Mask of Truth

; en_item00_update() hacks - 0x80012938

; Hook the entire en_item00_update function
; Replaced code:
;   addiu   sp, sp, -0x48
;   sw      s1, 0x0020(sp)
.headersize(0x800110A0 - 0xA87000)
.org 0x80012938
    j       en_item00_update_hook
    nop
en_item00_update_continue:

; Runs when player collides w/ Collectible (inside en_item00_update()) start of switch case at 0x80012CA4

; Override Item_Give(RUPEE_GREEN)
; Replaces:
;   OR      A0, S1, R0
;   JAL     0x8006FDCC
;   addiu   a1, r0, 0x0084
.orga 0xA88C0C ; In memory: 80012CAC
    j       item_give_hook
    or      A2, S0, R0

; Override Item_Give(RUPEE_BLUE)
; Replaces:
;   OR      A0, S1, R0
;   JAL     0x8006FDCC
;   addiu   a1, r0, 0x0084
.orga 0xA88C20 ; In memory: 80012CC0)
    j       item_give_hook
    or      A2, S0, R0

; Override Item_Give(RUPEE_RED)
; Replaces:
;   OR      A0, S1, R0
;   JAL     0x8006FDCC
;   addiu   a1, r0, 0x0084
.orga 0xA88C34 ; In memory: 80012CD4)
    j       item_give_hook
    or      A2, S0, R0

; Override Item_Give(RUPEE_PURPLE)
; Replaces:
;   OR      A0, S1, R0
;   JAL     0x8006FDCC
;   addiu   a1, r0, 0x0084
.orga 0xA88C48 ; In memory: 80012CE8)
    j       item_give_hook
    or      A2, S0, R0

; Override Stick Collectible
.orga 0xA88C70 ; In memory: 0x80012D10
    j       item_give_hook
    or      A2, S0, R0

; Override Nut Collectible
.orga 0xA88C7C ; In memory: 0x80012D1C
    j       item_give_hook
    or      A2, S0, R0

; Override Item_Give(ITEM_HEART)
; Replaces:
;   or      A0, S1, R0
;   JAL     0x8006FDCC
;   ADDIU   A1, R0, 0x0083
.orga 0xA88C88 ; In memory: 0x80012D28
    j       item_give_hook
    or      A2, S0, R0 ;pass actor pointer to function


; Override Bombs Collectible
.orga 0xA88CB0 ; In memory 0x80012D50
    j       item_give_hook
    or      A2, S0, R0

; Override Arrows Single Collectible
.orga 0xA88CC4 ; In memory 0x80012D64
    j       item_give_hook
    or      A2, S0, R0

; Override Arrows Small Collectible
.orga 0xA88CD8 ; In memory 0x80012D78
    j       item_give_hook
    or      A2, S0, R0

; Override Arrows Medium Collectible
.orga 0xA88CEC ; In memory  0x80012D8C
    j       item_give_hook
    or      A2, S0, R0

; Override Arrows Large Collectible
.orga 0xA88D00 ; In memory  0x80012DA0
    j       item_give_hook
    or      A2, S0, R0

; Override Seeds Collectible (as adult: 0x80012D78 and calls item_give, as child: 0x80012DB4 and uses getitemid)
.orga 0xA88D14 ; In memory: 0x80012DB4
    j       item_give_hook
    or      A2, S0, R0

; Override Magic Large Collectible
.orga 0xA88D44 ; In memory: 0x80012DE4
    j       item_give_hook
    or      A2, S0, R0

; Override Magic Small Collectible
.orga 0xA88D50 ; In memory: 0x80012DF0
    j       item_give_hook
    or      A2, S0, R0

; Hack save slot table offsets to only use 2 saves
; save slot table is stored at B71E60 in ROM
.headersize( 0x800FBF00 - 0xB71E60)
.orga 0xB71E60
SRAM_SLOTS:
.halfword 0x0020 ; slot 1
.halfword 0x2018 ; slot 2
.halfword 0x0000 ;remove slot 3
.halfword 0x4010 ; slot 1 backup
.halfword 0x6008 ; slot 2 backup
.halfword 0x0000 ; remove slot 3 backup

; Hack Write_Save function to store additional collectible flags
;.org 0x800905D4
;.orga 0xB065F4 ; In memory: 0x80090694
;   jal     Save_Write_Hook
;.orga 0xB06668 ; In memory: 0x80090708
;   jal     Save_Write_Hook
.org 0x800905D4
    j       Sram_WriteSave
    or      a1, r0, r0

; Hack Open_Save function to retrieve additional collectible flags
; At the start of the Sram_OpenSave function, SramContext address is stored in A0 and also on the stack at 0x20(SP)
; Overwrite the memcpy function at 0x800902E8
;   jal     0x80057030
;   addu    A1, T9, A3
.orga 0xB06248 ; In memory: 0x800902E8
    jal     open_save_hook
    nop

; Hack Init_Save function to zero the additional collectible flags
; Overwrite the SsSram_Read_Write call at 0x80090D84
.orga 0xB06CE4 ; In Memory: 0x80090D84
    jal     Save_Init_Write_Hook

; Verify And Load all saves function to only check slots 1 and 2.
; Overwrite the loop calculation at 0x80090974
;   slti    at, s4, 0x0003
;.orga  0xB068D4 ; In memory: 0x80090974
;   slti    at, s4, 0x0002
.org 0x80090720
    j       Sram_VerifyAndLoadAllSaves
    nop

; Hack Sram_CopySave to use our new version of the function
.org 0x80090FD0
    j       Sram_CopySave
    nop

; Hack Sram_EraseSave to actually just erase the entire slot
.org 0x80090eb8
    j       Sram_EraseSave
    nop

; Increase the size of EnItem00 instances to store the override
.orga 0xB5D6BE ; Address in ROM of the enitem00 init params
    .halfword 0x01BC ; Originally 0x019C

; Increase the size of pot instances to store chest type
.orga 0xDE8A5E ; Address in ROM of the ObjTsubo init params
    .halfword 0x01A0 ; New data starts at 0x0190

; Increase the size of flying pot instances to store chest type
.orga 0xDFB03A ; Address in ROM of the En_Tubo_Trap Init params
    .halfword 0x01AC ; New data starts at 0x019C

; Increase the size of crate instances to store chest type
.orga 0xEC856E ; Address in ROM of Obj_Kibako2 Init params
    .halfword 0x01B8 ; New data starts at 0x01A8

; Increase the size of small crate instances to store chest type
.orga 0xDE7B0E ; Address in ROM of Obj_Kibako Init params
    .halfword 0x019C ; New data starts at 0x018C

; Increase the size of beehive instances to store chest type
.orga 0xEC783E ; Address in ROM of Obj_Comb Init params
    .halfword 0x01B4 ; New data starts at 0x01A4

; Hack EnItem00_Init when it checks the scene flags to prevent killing the actor if its being overridden.
; Also use this as the point to set override data within the actor.
; replaces
;   jal     0x80020EB4
;.orga 0x0A87B10; In Memory 0x80011BB0
;   jal     Item00_KillActorIfFlagIsSet
.headersize(0x80011B98 - 0xA87AF8)
.orga 0xA87AF8 ; In Memory 0x80011B98
    jal     Item00_KillActorIfFlagIsSet
    or      a0, s0, r0
    bnez    v0, 0x800121A4
    lw      RA, 0x001c(sp)
    b       0x80011Bc0
    nop
    nop
    nop
    nop
.headersize(0)

; Hack EnItem00_Update when it checks proximity to the player to handle silver rupee collisions differently
; EnItem00_ProximityCheck_Hook will jump back into EnItem00 as appropriate.
.headersize (0x800110A0 - 0xA87000)
.org 0x80012C14 ; In Memory 0x80012C14
; Replaces
;   mtc1    at, f18
;   lwc1    f4, 0x0090(s0)
    jal     EnItem00_ProximityCheck_Hook
    nop
    ; Check our return result in v0. If it's true (actor is in proximity) then continue on the function, otherwise return
    bnez    v0, 0x80012C78 ; if v0 != 0 the player isn't in proximity, branch inside the original if where it calls Actor_HasParent before returning.
    lui     t6, 0x0001
    b       0x80012C64
    nop

; Hack EnItem00 Action Function (func_8001E304 from decomp, 0x8001251C in 1.0) used by Item_DropCollectible to not increment the time to live if its < 0
; replaces
;   lh      t6, 0x014A(s0)
;   lh      v0, 0x001C(s0)
;   addiu   at, r0, 0x0003
;   addiu   t7, t6, 0x0001
;   bne     v0, vt, 0x80012630
;   sh      t7, 0x014A(s0)
.orga 0xA88490 ; In Memory 0x80012530
    jal     EnItem00_DropCollectibleFallAction_Hack
    nop
    lh      v0, 0x001C(s0)
    addiu   at, r0, 0x0003
.skip 4
    nop

; Override the drop_id convert function s16 func_8001F404(s16 dropId) from decomp
.orga 0xA89490 ; in memory 0x80013530
    j get_override_drop_id
    nop

; Hack Item_DropCollectible when room index of the spawned actor gets set to -1.
; replaces
;   addiu   t7, r0, 0x00DC
;   addiu   at, r0, 0x0011
;   beq     v0, at, 0x80013888
;   sh      t7, 0x014a(s2)
;   addiu   at, r0, 0x0006
;   beq     v0, at, 0x80013888
;   addiu   at, r0, 0x0007
;   beq     v0, at, 0x80013888
;   addiu   t8, r0, 0xFFFF
;   sb      t8, 0x0003(s2)
.orga 0xA897C0 ; in memory 0x80013860
    jal     drop_collectible_room_hook
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

; Hack at end of Item_DropCollectible to reset the drop_collectible_override_flag
.orga 0xA897F8; in memory 0x80013898
; replaces
;   lw      ra, 0x003C(sp)
;   lw      s0, 0x0030(sp)
;   lw      s1, 0x0034(sp)
;   lw      s2, 0x0038(sp)
;   jr      ra
;   addiu   sp, sp, 0x58
    j       Item_DropCollectible_End_Hack
    lw      ra, 0x003C(sp)

; Hack at end of Item_DropCollectible2 to reset to drop_collectible_override_flag
.orga 0xA899CC; in memory 0x80013A6C
; replaces
;   lw      ra, 0x003C(sp)
;   lw      s0, 0x0030(sp)
;   lw      s1, 0x0034(sp)
;   lw      s2, 0x0038(sp)
;   jr      ra
;   addiu   sp, sp, 0x50
    j       Item_DropCollectible2_End_Hack
    lw      ra, 0x003C(sp)

; Hack Item_DropCollectibleRandom to call custom drop override function (mostly just for chus in logic)
; replaces
;   jal     0x80013530
;.orga 0xA89D4C
;    jal     get_override_drop_id

; Hack ObjTsubo_SpawnCollectible (Pot) to call our overridden spawn function
.orga 0xDE7C60
    j       ObjTsubo_SpawnCollectible_Hack
    nop

; Hack ObjKibako2_SpawnCollectible (Large crates) to call our overridden spawn function
;
.orga 0xEC8264
    j       ObjKibako2_SpawnCollectible_Hack
    nop

; Hack ObjKibako_SpawnCollectible (Small wooden crates) to call our overriden spawn function
.orga 0xDE6F60
    j       ObjKibako_SpawnCollectible_Hack
    nop

; Hack En_tubo_trap (flying pots) to call our overriden spawn function
.orga 0xDFA520
    j       EnTuboTrap_DropCollectible_Hack
    nop

; Hack ObjKibako2_Init (Large Crates) to not delete our extended flag
.orga 0xEC832C
    or      T8, T7, R0

; Hack obj_comb (beehives) to drop flagged collectibles. Get rid of the random 50% drop
; replaces
;   sh      a2, 0x001e(sp) <- keep
;   jal     0xb00cdccc    <- keep
;   sw      a3, 0x0020(sp) <- keep
;   lui     at, 0x3F00
;   mtc     at, f4
;   lh      a2, 0x001e(sp)
;   lw      a3, 0x0020(sp)
;   c.lt.s  f0, f4
;   nop
;   bc1f    0xb0ec7490
;   nop
;   addiu   a2, r0, 0xffff
.orga 0xec746c
    j       obj_comb_hook
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

; Hack in Actor_Spawn when allocating space for the actor to increase the size of every actor by a fixed amount
.headersize (0x800110A0 - 0xA87000)
.org 0x800252A8
; Replaces:
;   jal     0x80066C10 (ZeldaArena_Malloc)
;   sw      v1, 0x004C(sp)
    jal     Actor_Spawn_Malloc_Hack
    sw      v1, 0x004C(sp)


; Hack in Actor_Spawn after the null check to offset the pointer by the amount that we added to the actor, so the new data is at the start
.org 0x800252CC
; Replaces:
;   lb      t2, 0x001E(s0)
;   lui     at, 0x0001
    jal     Actor_Spawn_Shift
    nop

; Hack Actor_Spawn function so we can override actor spawns
.orga 0xA9B070 ; in memory 0x80025110
; Replaced code:
;   addiu   sp, sp, -0x58
;   sw      a2, 0x0060(sp)
    j       Actor_Spawn_Hook
    nop
Actor_Spawn_Continue_Jump_Point:

; Hack in Actor_Delete to shift the pointer back to the start of the actor that was malloc'd to include the new data.
.org 0x8002570C
; Replaces:
;   jal     0x80066C90
;   or      a0, s0, r0
.skip 4
    addiu   a0, s0, -0x10

; Hook Actor_UpdateAll when each actor is being initialized. At the call to Actor_SpawnEntry
; Used to set the flag (z-rotation) of the actor to its position in the actor table.
.orga 0xA99D48 ; In memory: 0x80023DE8
; Replaces:
;   jal     0x800255C4
    jal     Actor_UpdateAll_Hook

; Hack Actor_SpawnEntry so we can override actors being spawned
.orga 0xA9B524 ; In memory: 0x800255C4
; Replaces: Entire function
    j       Actor_SpawnEntry_Hack
    nop

.orga 0xA99C98 ; In memory: 0x80023D38
    jal     Player_SpawnEntry_Hack

; Hack the function that kills actor when changing rooms to not kill overridden collectibles?
; Hack at the call to Actor_Kill
.orga 0xA9ADAC ; In memory: 0x80024E4C
; Replaces:
;   jal     Actor_Kill
    jal     Room_Change_Actor_Kill_Hack

; ====== Wonderitem Shuffle ======

; Increase the size of wonderitem to store when they are being overridden
.orga 0xDE96FA
.halfword 0x01D0

; Hack EnWonderItem_Init to not kill the actor if the switch flag is set but it should be overridden
; Replaces
;   jal     Actor_Kill
.orga 0xDE8E54
    jal     EnWonderItem_Kill_Hack
    nop
    nop
    nop
    nop

; Hack EnWonderItem_MultitagFree to show the remaining tags
.orga 0xDE9198
; Replaces:
;   lwc1    f4, 0x0024(a2)
;   lwc1    f8, 0x0028(a2)
    jal     EnWonderItem_Multitag_DrawHook
    nop

; Hack EnWonderItem_MultitagOrdered to show the remaining tags
.orga 0xDE9408
; Replaces:
;   lwc1    f4, 0x0024(a2)
;   lwc1    f8, 0x0028(a2)
    jal     EnWonderItem_MultitagOrdered_DrawHook
    nop

; Hack at the end of EnWonderItem_MultitagFree to not set the switch flag. It is set inside EnWonderItem_DropCollectible
.orga 0xDE9250
; Replaces:
;   bltzl   a1, 0x801F8EE4
;   or      a0, s0, r0
;   jal     0x800204D0 ;Flags_SetSwitch
;   lw      a0, 0x0024(sp)
    nop
    nop
    nop
    nop

; Hack at the beginning of EnWonderItem_Update to draw a marker for the location (other than multitags)
.orga 0xDE9630
; Replaces:
;   lw      t9, 0x013c(s0)
;   or      a0, s0, r0
    jal       EnWonderItem_Update_Hook
    nop

; Hack EnWonderItem_DropCollectible to drop flagged collectibles
.orga 0xDE8C94
    j       EnWonderItem_DropCollectible_Hack
    nop

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

; Change graphic ID to be treated as unsigned
; Replaces: lb      t9, 0x0852(s0)
.orga 0xBE6538
    lbu     t9, 0x0852(s0)

; Replaces: lb      v0, 0x0852(s0)
.orga 0xAF1398
    lbu     v0, 0x0852(s0)

; Replaces: lb      v0, 0x0852(s0)
.orga 0xAF13AC
    lbu     v0, 0x0852(s0)

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

;Hack to EnItem00_Init to spawn deku shield, hylian shield, and tunic objects
.orga 0xA87DC8 ;In memory 0x80011E68
    jal object_index_or_spawn ;Replace call to z64_ObjectIndex
.orga 0xA87E24 ;In memory 0x80011EC4
    jal object_index_or_spawn ;Replace call to z64_ObjectIndex
.orga 0xA87E80 ;In memory 0x80011F20
    jal object_index_or_spawn ;Replace call to z64_ObjectIndex

; Fix autocollect magic jar wonder items
; Replaces:
;   jal     func_80022CF4
.orga 0xA880D4
    jal     enitem00_set_link_incoming_item_id

;==================================================================================================
; Freestanding models
;==================================================================================================

; Hook EnItem00_Draw
.headersize(0x800110A0 - 0xA87000)
.org 0x80012fb8
; Replaces:
;   addiu   sp, sp, -0x28
;   sw      ra, 0x14(sp)
    j   EnItem00_Draw_Hook
    nop
EnItem00_Draw_Continue:

; Replaces:
;   jal     0x80013498 ; Piece of Heart draw function
.orga 0xA88F78 ; In memory: 0x80013018
    jal     heart_piece_draw

; Replaces:
;   jal     0x80013498 ; Collectable draw function
.orga 0xA89048 ; In memory: 0x800130E8
    jal     collectible_draw_other

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
    or      a1, r0, s0   ; menu data
    jal     draw_file_select_hash
    andi    a0, t8, 0xFF ; a0 = alpha channel of fade-out rectangle

    lw      s0, 0x18 (sp)
    lw      ra, 0x1C (sp)
    jr      ra
    addiu   sp, sp, 0x88
.endarea

;==================================================================================================
; Hide file details panel
;==================================================================================================
; keep death count alpha at 0 instead of using file_detail alpha
.orga 0xBAC064 ; In memory: 0x803AFE64
    move    t7, r0 ; was: lh t7, 0x4A7E (t4)

; keep hearts alpha at 0 instead of using file_detail alpha
.orga 0xBAC1BC ; In memory: 0x803AFFBC
    move    t7, r0 ; was: lh t7, 0x4A7E (t4)

; keep stones/medals alpha at 0 instead of using file_detail alpha
.orga 0xBAC3EC ; In memory: 0x803B01EC
    move    t9, r0 ; was: lh t9, 0x4A7E (t3)

; keep detail panel alpha at 0 instead of using file_detail alpha
.orga 0xBAC94C ; In memory: 0x803B074C
    move    t9, r0 ; was: lh t9, 0x4A7E (t9)

; keep file tag alpha at 0xC8 instead of subtracting 0x19 each transition frame
.orga 0xBAE5A4 ; In memory: 0x803B23A4
    sh      t3, 0x4A6C (v1) ; was: sh t5, 0x4A6C (v1)

; prevent setting file tag alpha to 0x00 when transition is finished
.orga 0xBAE5C8 ; In memory: 0x803B23C8
    nop ; was: sh r0, 0x4A6C (v1)

; prevent increasing alpha when transitioning away from file
.orga 0xBAE864 ; In memory: 0x803B2664
    nop ; was: sh t5, 0x4A6C (v1)

; change file positions in copy menu
.orga 0xBB05FC ; In memory: 0x803B43FC
    .word 0x0000FFC0
    .word 0xFFB0FFB0

; keep file tag alpha at 0xC8 in copy menu
.orga 0xBA18C4 ; In memory: 0x803A56C4
    ori     t4, r0, 0x00C8 ; was: addiu t4, t9, 0xFFE7

.orga 0xBA1980 ; In memory: 0x803A5780
    ori     t0, r0, 0x00C8 ; was: addiu t0, t9, 0xFFE7

.orga 0xBA19DC ; In memory: 0x803A57DC
    nop ; was: sh r0, 0x4A6C (t2)

.orga 0xBA1E20 ; In memory: 0x803A5C20
    ori     t5, r0, 0x00C8 ; was: addiu t5, t4, 0x0019

.orga 0xBA18C4 ; In memory: 0x803A56C4
    ori     t4, r0, 0x00C8 ; was: ori t4, t4, 0x00C8

; keep file tag alpha at 0xC8 in erase menu
.orga 0xBA34DC ; In memory: 0x803A72DC
    ori     t8, r0, 0x00C8 ; was: addiu t8, t7, 0xFFE7

.orga 0xBA3654
    nop ; was: sh r0, 0x4A6C (t6)

.orga 0xBA39D0
    ori     t5, r0, 0x00C8 ; was: addiu t5, t4, 0x0019

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

; Reimplement KaleidoScope_DrawItemSelect
; Replaces:
;   addiu       sp, sp, -0xA8
;   sw          s5, 0x0030 (sp)
.orga 0xBB7670 ; In memory: 0x8038EFF0
    j     KaleidoScope_DrawItemSelect
    nop

;==================================================================================================
; Song Fixes
;==================================================================================================
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
    jal      Shop_Keeper_Update_ID

; Update object ID and draw ID for progressive items
.headersize(0x80862C00 - 0xC004E0)

.org 0x8086498C
    jal     shop_draw_hook

.headersize(0x808CED80 - 0xC6C5E0)

; EnOssan_State_ItemPurchased / func_808D1D08
; Run update shop items function after an item is purchased.
; Also reorganize displaced code to preserve $ra
; Replaces:
;   lh      t6, 0x001C(s0)
;   addiu   $at, $zero, 0x000A
;.org 0x808D1D48
;    jal     shop_update_offerings_hook
;    nop

.headersize(0)

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
; Mask Shop Changes for Trade Shuffle
;==================================================================================================
.orga 0xC01CD8
    jal     set_mask_text_hook

; The mask text hook replaces this instruction,
; which happens to be duplicated for EnGirlA_SetItemDescription
; but the other argument is set after the jal to EnGirlA_SetItemOutOfStock.
; Making them the same lets us avoid running the displaced code in the hook.
.orga 0xC01CEC
    or      a1, a2, $zero

; Set mask shop sold out flags after purchase if
; the slot is shuffled
.orga 0xC6F5DC
    jal     set_mask_sold_out
    nop

; Change mask shop bunny hood turn in to check the given
; shelf slot instead of the shop item ID to be compatible
; with Mask of Truth shuffled. A custom buy item function
; is used for shuffled Mask of Truth slot to prevent purchase
; without trading all masks.
.orga 0xC6F5F8
    addiu   at, $zero, 0x0002   ; Mask of Truth slot
    lui     v1, 0x8012
    lbu     t5, 0x0242(s0)      ; cursor index

; Use trade shuffle flags for mask salesman greeting
.orga 0xC70704
    j       SetupMaskShopHelloDialogOverride

; Use trade shuffle flags to loop through mask payments
.orga 0xC6D7EC
    j       TryPaybackMaskOverride
    addiu   sp, sp, 0x18             ; reset stack pointer from overrided function

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
; Empty Bomb Fix
;==================================================================================================

; Replaces:
;sw      r0, 0x0428(v0)
;sw      t5, 0x066C(v0)

.orga 0xC0E77C
    jal     empty_bomb
    sw      r0, 0x0428(v0)

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
; Roll Collision / Bonks Kill Player
;==================================================================================================

; Set player health to zero on last frame of bonk animation
; z_player func_80844708, conditional where this->unk_850 != 0 and temp >= 0 || sp44
; Replaces:
;   b       lbl_80842AE8
.orga 0xBE0234
    j       BONK_LAST_FRAME

; Prevent set and reset of player state3 flag 4, which is re-used for storing bonk state if the
; player manages to cancel the roll/bonk animation before the last frame.
; The flag does not appear to be used by the vanilla game.
; Replaces:
;   sb      t4, 0x0682(s0)
.orga 0xBE3798
    nop
; Replaces:
;   sb      t5, 0x0682(s0)
.orga 0xBE55E4
    nop

; Hook to set flag if player starts bonk animation
; Flag is unset on player death
; Replaces:
;   or      a0, s0, $zero
;   addiu   a1, $zero, 0x00FF
.orga 0xBE035C
    jal     SET_BONK_FLAG
    nop

; Hook into Player_UpdateCommon to check if bonk animation was canceled.
; If so, kill the dirty cheater.
; Replaces:
;   addiu   $at, $zero, 0x0002
;   lui     t1, 0x8012
.orga 0xBE5328
    jal     CHECK_FOR_BONK_CANCEL
    nop

; Hook to Game Over cutscene init in Player actor to prevent adding a subcamera
; in scenes with fixed cameras like Link's House or outside Temple of Time.
; The game crashes in these areas if the cutscene subcamera to rotate around
; Link as he dies is added.
; Replaces
;   sll     a2, v0, 16
;   sra     a2, a2, 16
.orga 0xBD200C
    jal     CHECK_ROOM_MESH_TYPE
    nop

;==================================================================================================
; Roll Collision / Bonks Kills King Dodongo
;==================================================================================================

; King Dodongo tracks the number of wall hits when rolling in order to transition from
; the rolling animation to walking. Add a hook to the actor update function to check
; this variable and set actor health to zero if bonks are not zero.
; Replaces:
;   lh      t2, 0x0032(s1)
;   mtc1    $zero, $f16
.orga 0xC3DC04
    jal     KING_DODONGO_BONKS
    nop

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

; Fix GC Rolling Goron as Adult to always work
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
; Disable fishing anti-piracy checks
;==================================================================================================
; Replaces: sltiu   v0, v0, 1
.orga 0xDBEC80
    li      v0, 0

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

; en_bom_bowl_man actor changes to prize selection using new flags
; Replaces:
;   jr      t7
.orga 0xE2E070
    jal     select_bombchu_bowling_prize
    lhu     a0, 0x0232(s0)
    or      v1, v0, $zero
    b       skip_bombchu_bowling_prize_switch
    sh      v1, 0x004E($sp)

.orga 0xE2E0E0
skip_bombchu_bowling_prize_switch:

; set new bombchu bowling flags in scene collectible flags, skipping
; inf_table flags
; Replaces:
;   lh      v0, 0x014A(a2)
;   addiu   $at, $zero, 0x0001
;   beq     v0, $zero, lbl_80AAEFA4
;   nop
;   beq     v0, $at, lbl_80AAEFBC
.orga 0xE2EDD4
    jal     set_bombchu_bowling_prize_flag
    lh      a0, 0x014A(a2)
    nop
    nop
    nop

; en_js actor changes to prevent buying bombchus before finding a shuffled source
.orga 0xE5B5C8
    jal     logic_chus__carpet_dude_1
.orga 0xE5B5DC
    jal     logic_chus__carpet_dude_2

;==================================================================================================
; Override Collectible 05 to be a Bombchus (5) drop instead of the unused Arrow (1) drop
;==================================================================================================
; Replaces: 0x80011D30
.orga 0xB7BD24
    .word 0x80011D88

; Replaces: li   a1, 0x03
.orga 0xA8801C
    li      a1, 0x96 ; Give Item Bombchus (5)
.orga 0xA88CCC
    li      a1, 0x96 ; Give Item Bombchus (5)

; Replaces: lui     t5, 0x8012
;           lui     at, 0x00FF
.orga 0xA89268
    jal     chu_drop_draw
    lui     t5, 0x8012

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

.orga 0xE2BE10
    jal     potion_shop_buy_hook
    nop

.orga 0xE2BDDC
    jal     potion_shop_check_empty_bottle

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
; Stone of Agony indicator
;==================================================================================================

; Replaces:
;   c.lt.s  f0, f2
.orga 0xBE4A14
    jal     agony_distance_hook

    ; Replaces:
;   c.lt.s  f4, f6
.orga 0xBE4A40
    jal     agony_vibrate_hook

; Replaces:
;   addiu   sp, sp, 0x20
;   jr      ra
.orga 0xBE4A60
    j       agony_post_hook
    nop

;==================================================================================================
; Blue Warps
;==================================================================================================

; Child blue warps
; Replaces:
;   jal     func_809056E8 ; DoorWarp1_PlayerInRange
.orga 0xCA2F38 ; In Memory: 0x80905778
    jal     DoorWarp1_PlayerInRange_Overwrite

; Ruto blue warp
; Replaces:
;   jal     func_809056E8 ; DoorWarp1_PlayerInRange
.orga 0xCA3404 ; In Memory: 0x80905C44
    jal     DoorWarp1_PlayerInRange_Overwrite

; Adult blue warps
; Replaces:
;   jal     func_809056E8 ; DoorWarp1_PlayerInRange
.orga 0xCA3A10 ; In Memory: 0x80906250
    jal     DoorWarp1_PlayerInRange_Overwrite

; As the above replaces overlay functions with a global function,
; Need to null out the reloc entries

; Child blue warps
; Replaces:
;   .word   0x44001258
.orga 0xCA5D4C
.word   0x00000000

; Ruto blue warp
; Replaces:
;   .word   0x44001724
.orga 0xCA5D7C
.word   0x00000000

; Adult blue warps
; Replaces:
;   .word   0x44001D30
.orga 0xCA5E08
.word   0x00000000


; Overwrite warp conditions for Shadow and Spirit medallions

; Replaces:
;   lui     t3, 0x8010
;   lw      t3, -0x7404(t3)
;   lw      t4, 0x00A4(v1)
;   or      a0, s0, $zero
;   addiu   a1, $zero, 0x0069
;   and     t5, t3, t4
.orga 0xCA3EA0 ; In Memory: 0x809066E0
    nop
    jal     DoorWarp1_IsSpiritRewardObtained
    nop
    or      t5, v0, $zero
    or      a0, s0, $zero
    addiu   a1, $zero, 0x0069

; Replaces:
;   lui     t2, 0x8010
;   lw      t2, -0x7400(t2)
;   lw      t3, 0x00A4(v1)
;   or      a0, s0, $zero
;   addiu   a1, $zero, 0x006A
;   and     t4, t2, t3
.orga 0xCA3F30 ; In Memory: 0x80906770
    nop
    jal     DoorWarp1_IsShadowRewardObtained
    nop
    or      t4, v0, $zero
    or      a0, s0, $zero
    addiu   a1, $zero, 0x006A


; Overwrite Item_Give to set data and flags from skipped cutscenes


; Kokiri Emerald

; Replaces:
;   jal     Item_Give
.orga 0xCA3158 ; In Memory: 0x80905998
    jal     DoorWarp1_KokiriEmerald_Overwrite
.orga 0xCA3168
    addiu   t5, $zero, 0x0457 ; nextEntranceIndex
.orga 0xCA3174
    ori     t6, $zero, 0 ; nextCutsceneIndex


; Goron Ruby

; Replaces:
;   jal     Item_Give
.orga 0xCA30D8 ; In Memory: 0x80905918
    jal     DoorWarp1_GoronRuby_Overwrite
.orga 0xCA30E8
    addiu   t2, $zero, 0x047A ; nextEntranceIndex
.orga 0xCA30F4
    ori     t3, $zero, 0 ; nextCutsceneIndex


; Zora Sapphire

; Replaces:
;   jal     Item_Give
.orga 0xCA36F0 ; In Memory: 0x80905F30
    jal     DoorWarp1_ZoraSapphire_Overwrite
.orga 0xCA3710
    ori     t5, $zero, 0 ; nextCutsceneIndex


; Forest medallion

; Replaces:
;   jal     Item_Give
.orga 0xCA3D18 ; In Memory: 0x80906558
    jal     DoorWarp1_ForestMedallion_Overwrite
; Set destination
.orga 0xCA3D30
    addiu   t3, $zero, 0x05E8 ; nextEntranceIndex


; Fire medallion

; Replaces:
;   jal     Item_Give
.orga 0xCA3DA4 ; In Memory: 0x809065E4
    jal     DoorWarp1_FireMedallion_Overwrite
; Set destination
.orga 0xCA3DBC
    addiu   t9, $zero, 0x0564 ; nextEntranceIndex
.orga 0xCA3DC8
    ori     t1, $zero, 0


; Water medallion

; Replaces:
;   jal     Item_Give
.orga 0xCA3E30 ; In Memory: 0x80906670
    jal     DoorWarp1_WaterMedallion_Overwrite
; Set destination
.orga 0xCA3E48
    addiu   t7, $zero, 0x04E6 ; nextEntranceIndex


; Spirit medallion

; Replaces:
;   jal     Item_Give
.orga 0xCA3EC0 ; In Memory: 0x80906700
    jal     DoorWarp1_SpiritMedallion_Overwrite
; Set destination
.orga 0xCA3ED8
    addiu   t6, $zero, 0x0610 ; nextEntranceIndex


; Shadow medallion

; Replaces:
;   jal     Item_Give
.orga 0xCA3F50 ; In Memory: 0x80906790
    jal     DoorWarp1_ShadowMedallion_Overwrite
; Set destination
.orga 0xCA3F68
    addiu   t5, $zero, 0x0580 ; nextEntranceIndex

;==================================================================================================
; Correct Chest Sizes
;==================================================================================================

.org 0xC0796E
; Replaces .halfword 0x01EC
; Increases chest actor (en_box) instance size
    .halfword 0x01F0

.orga 0xC06198
; Replaces sb  t9,0x01E9(s0)
    jal     GET_CHEST_OVERRIDE_WRAPPER

; Chest Size
; Replaces lbu   v0,0x01E9(s0)
.orga 0xC064BC
    lbu     v0,0x01EC(s0)
.orga 0xC06E5C
    lbu     v0,0x01EC(s0)
.orga 0xC07494
    lbu     v0,0x01EC(s0)
.orga 0xC07230
    lbu     v0,0x01EC(s0)

;==================================================================================================
; Draw Chest Base and Lid
;==================================================================================================

.org 0xC0754C
    j   draw_chest
    nop

; set chest_base front texture
.org 0xFEB000 + 0x6F0 - 0x3296C0 + 0x3296D8
.word   0xDE000000, 0x09000000

.org 0xFEB000 + 0x6F0 - 0x3296C0 + 0x3297B8
.word   0xDE000000, 0x09000000

; set chest_base base texture
.org 0xFEB000 + 0x6F0 - 0x3296C0 + 0x329758
.word   0xDE000000, 0x09000010

.org 0xFEB000 + 0x6F0 - 0x3296C0 + 0x329810
.word   0xDE000000, 0x09000010

; set chest_lid front texture
.org 0xFEB000 + 0x10C0 - 0x32A090 + 0x32A0A8
.word   0xDE000000, 0x09000000
.org 0xFEB000 + 0x10C0 - 0x32A090 + 0x32A1C8
.word   0xDE000000, 0x09000000

; set chest_lid base texture
.org 0xFEB000 + 0x10C0 - 0x32A090 + 0x32A158
.word   0xDE000000, 0x09000010

;==================================================================================================
; Increase transparency of red ice in CTMC
;==================================================================================================

; In a function called by red ice init
; Replaces addiu    t7, $zero, 0x00FF
.orga 0xDB3244
    j       red_ice_alpha
;   sw      t6, 0x0154(a0) ; delay slot unchanged, sets the idle action function
; Next 3 instructions are skipped, now done in red_ice_alpha instead.
;   sh      t7, 0x01F0(a0)
;   jr      ra
;   nop

;==================================================================================================
; Invisible Chests
;==================================================================================================

; z_actor, offset 0x5F58
; Hooks into actor draw logic for invisible actors and lens of truth.
; If invisible chests is enabled, chests in rooms with inverted lens
; functionality (hide instead of show) will not be drawn at all unless
; lens is active.
; replaces
;   lw      v0, 0x0004(s0)
;   andi    t3, v0, 0x0060
.orga 0xA9AAF0
    jal     SHOW_CHEST_WITH_INVERTED_LENS
    nop
; replaces
;   sll     t9, s2,  2
;   addu    t0, s7, t9
.orga 0xA9AB0C
    jal     HIDE_CHEST_WITH_INVERTED_LENS
    nop

;==================================================================================================
; Forest Twisted Hallway Chest
;==================================================================================================

; z_bg_mori_hineri, offset 0x0934
; replace chest object logic with should_draw_forest_hallway_chest
.orga 0xCB1288
    or      a0, s1, r0 ; actor
    jal     should_draw_forest_hallway_chest
    or      a1, s2, r0 ; game
    beqz    v0, @draw_forest_hallway_chest_lid_end
    nop
    nop
    b       @draw_forest_hallway_chest_start
    lui     t9, 0xDB06 ; G_MOVEWORD segment 06
.orga 0xCB12C8
@draw_forest_hallway_chest_start:

; z_bg_mori_hineri, offset 0x0A24
; replace gSPMatrix, gSPDisplayList with draw_forest_hallway_chest_base
.orga 0xCB1374
    jal     draw_forest_hallway_chest_base
    nop
    b       @draw_forest_hallway_chest_base_end
    nop
.orga 0xCB13B8
@draw_forest_hallway_chest_base_end:

; z_bg_mori_hineri, offset 0x0AE0
; replace gSPMatrix, gSPDisplayList with draw_forest_hallway_chest_lid
.orga 0xCB1430
    jal     draw_forest_hallway_chest_lid
    nop
    b       @draw_forest_hallway_chest_lid_end
    nop
.orga 0xCB1474 ; also end of function
@draw_forest_hallway_chest_lid_end:

;==================================================================================================
; Draw Pot Textures
;==================================================================================================

; replaces ObjTsubo_Draw
.org 0xDE89FC
    j       draw_pot_hack
    nop

; replaces EnGSwitch_DrawPot
.orga 0xDF3FC0
    j       draw_hba_pot_hack
    nop

; replaces EnTuboTrap_Draw
.orga 0xDFAFC4
    j       draw_flying_pot_hack
    nop

.org 0xF6D000 + 0x17870 + 0x18 ; gameplay_dangeon_keep file start + dlist offset + gDPSetTextureImage offset
.word   0xDE000000, 0x09000000 ; jump to the custom dlist at segment 09

.org 0xF6D000 + 0x17870 + 0xD8 ; gameplay_dangeon_keep file start + dlist offset + gDPSetTextureImage offset
.word   0xDE000000, 0x0A000000 ; jump to the custom dlist at segment 0A

.org 0xF6D000 + 0x17870 + 0x138 ; gameplay_dangeon_keep file start + dlist offset + gDPSetTextureImage offset
.word   0xDE000000, 0x09000000 ; jump to the custom dlist at segment 09

.org 0x1738000 + 0x17C0 + 0x18 ; object_tsubo file start + dlist offset + gDPSetTextureImage offset
.word   0xDE000000, 0x09000000 ; jump to the custom dlist at segment 09

.org 0x1738000 + 0x17C0 + 0x108 ; object_tsubo file start + dlist offset + gDPSetTextureImage offset
.word   0xDE000000, 0x0A000000 ; jump to the custom dlist at segment 0A

;==================================================================================================
; Draw Crate Textures
;==================================================================================================

.orga 0xEC8528
    j       ObjKibako2_Draw
    nop

.orga 0x18B6000 + 0x960 + 0x18 ; load top texture
.word   0xDE000000, 0x09000000
.orga 0x18B6000 + 0x960 + 0x50 ; load palette
.word   0xDE000000, 0x09000010
.orga 0x18B6000 + 0x960 + 0xC0 ; load side texture
.word   0xDE000000, 0x09000020

; hacks to use ci8 textures instead of ci4
.orga 0x18B6990 ; hack loadblock (top)
.word 0xF3000000, 0x073FF200 ; load 1024 texels to tmem, 512b per line (8 words)

.orga 0x18B69A0 ; hack settile (top)
.word 0xF5480800, 0x00098250 ; texel size G_IM_SIZ_8b, 256b per line (4 words)

.orga 0x18B69D0 ; loadTLUT
.word 0xF0000000, 0x073FF000 ; 256 color palette

.orga 0x18B6A38 ; hack loadblock (side)
.word 0xF3000000, 0x073FF200

.orga 0x18B6A48 ; hack settile (side)
.word 0xF5480800, 0x00098250

;==================================================================================================
; Draw Small Crate Textures
;==================================================================================================

.orga 0xDE7AC8
    j       ObjKibako_Draw
    nop

.orga 0xF6D000 + 0x5290 + 0x18 ; gameplay_dangeon_keep file start + dlist offset + gDPSetTextureImage offset
.word   0xDE000000, 0x09000000 ; jump to the custom dlist at segment 09

;==================================================================================================
; Draw Beehive Textures
;==================================================================================================

;Hook ObjComb_Update to use our new function
.orga 0xEC764C
    j       ObjComb_Update
    nop


;Hook ObjComb_Draw call to set up custom dlist stuff
;Replaces:
;   addiu   sp, sp, -0x30
;   sw      s0, 0x0014(sp)
;   sw      ra, 0x001c(sp)
;   sw      s1, 0x0018(sp)
;.orga 0xEC76C4
;   addiu   sp, sp, -0x30
;   sw      ra, 0x001c(sp)
;   jal     ObjComb_Draw_Hook
;   nop

;.orga 0xF5F000 + 0x95B0 + 0x18 ; gameplay_field_keep file start + beehive dlist offset + gDPSetTextureImage offset
;.word   0xDE000000, 0x09000000 ; jump to the custom dlist at segment 09

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
;manually set next entrance and fade out type
.orga 0xBEA044
   jal      warp_speedup
   nop

.orga 0xB10CC0 ;set fade in type after the warp
    jal     set_fade_in
    lui     at, 0x0001


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
.orga 0xBD6958
    jal extended_object_lookup_GI
    nop

; extends object table lookup for on scene loads
.orga 0xAF76B8
    sw      ra, 0x0C (sp)
    jal extended_object_lookup_load
    subu    t7, r0, a2
    lw      ra, 0x0C (sp)

; extends object table lookup for shop item load
.orga 0xAF74F8
    sw      ra, 0x44 (sp)
    jal extended_object_lookup_shop
    nop
    lw      ra, 0x44 (sp)

; extends object table lookup for shop item load after you unpause
.orga 0xAF7650
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
; Trade Quest Shuffle Flag Hooks
;==================================================================================================
; Handle custom flags for trade item revert on savewarp
; Replaces
;   lbu     t4, 0x0000(t9)
;   addu    t5, s0, t4
.orga 0xB064E0 ; VRAM 0x80090580
    jal     update_shiftable_trade_item_save_hook
    nop

; Control if Grog can spawn in Lost Woods
.orga 0xE20BC8
    jal     check_grog_spawn_flags

; Control if the skull kid near Grog/Fado can spawn in Lost Woods
; Replaces
;   addu    t9, t9, t8
;   lbu     t9, -0x59BC(t9)
.orga 0xDEF73C
    jal     check_skull_kid_spawn_flags
    nop

; Set traded flag after giving skull mask to the skull kid (en_skj).
; Commands reorganized to fit and prevent displaced code.
.orga 0xDF141C
    jal     set_skull_mask_traded_flag
    lw      s0, 0x0018($sp)
    lw      $ra, 0x001C($sp)
    jr      $ra
    addiu   $sp, $sp, 0x0020

; Set traded flag after giving keaton mask to the guard (en_heishi2).
.orga 0xD1B894
    jal     set_keaton_mask_traded_flag

; Set traded flag after giving spooky mask to the graveyard kid (en_cs).
.orga 0xE60D00
    jal     set_spooky_mask_traded_flag

; Set traded flag after giving bunny hood to the running man (en_mm).
.orga 0xE50888
    jal     set_bunny_hood_traded_flag

; Skip BGS flag checks for Biggoron trade dialog

; EnGo2_GetTextIdGoronDmtBiggoron
; BGS flag text ID is the same as the claim check branch. Skip it.
; This has the side effect that if claim check is traded in and
; the adult trade item is changed to an item earlier than prescription,
; Biggoron will use his early-game text throwing shade at Medigoron.
; Replaces
;   lbu     t6, 0x003E(a1)
.orga 0xED3298
    or      t6, $zero, $zero

; EnGo2_GetStateGoronDmtBiggoron
; Prevents duping the BGS get item cutscene if claim check is
; presented again. Update to use the trade quest "traded"
; flags in DMC unk_00_ scene flags.
; Replaces
;   lbu     t8, -0x59F2(t8)
.orga 0xED337C
    jal     check_claim_check_traded

; EnGo2_BiggoronSetTextId
; First instance controls Biggoron's response after the
; claim check has been turned in, including if claim check
; is presented to him again. Modify to use the trade quest
; "traded" flags and also if the adult trade item is the claim
; check. The second part is important to allow turning in
; the broken sword and eyedrops after claim check has been
; turned in. Since v0 (bgs flag state) is immediately checked
; in the next branch, change this branch check to use t8
; Replaces
;   lbu     v0, 0x003E(v1)
;   or      a0, a1, $zero
;   beq     v0, $zero, lbl_80B58CFC
.orga 0xED43E4
    jal     check_claim_check_traded
    or      a0, a1, $zero
    beq     t8, $zero, claim_check_not_traded
.orga 0xED442C
claim_check_not_traded:

; Skip setting the BGS flag after turning in the claim check
; Replaces
;   sb      t8, 0x003E(v0)
.orga 0xED6574
    nop

; Change Biggoron animation if adult trade quest shuffle is on
; to always in pain until the eye drops are turned in.
; Replaces
;   lbu     v0, 0x0074(t4)
.orga 0xED5C04
    jal     check_if_biggoron_should_cry_eye_hook
.orga 0xED4860
    jal     check_if_biggoron_should_cry_anim_hook
    nop
.orga 0xED5784
    jal     check_if_biggoron_should_cry_sfx_hook
    nop

; Disable Cucco lady overriding her get item ID
; as adult if Pocket Egg not obtained. The correct
; ID is already set by this point.
.orga 0xE1E9A0
    jal     check_cucco_lady_talk_exch_hook
.orga 0xE1E9DC
    jal     check_cucco_lady_talk_none_hook
.orga 0xE1ECD4
    jal     check_cucco_lady_exchange_id_hook
.orga 0xE1ECDC
    nop
.orga 0xE1ED64
    jal     check_cucco_lady_flag_hook
    nop

; Prevent turning in trade items more than once.
; Nullfies target actor if custom trade quest flag for the
; presented item is set. Without a target actor, falls through
; to default cutscene item text.
; EXCEPTION: Claim check can be presented multiple times to
; match vanilla behavior. "Traded" flags are checked in the
; Biggoron actor to prevent duping.
.orga 0xBD6CD0 ; player actor vram 0x80839320
    jal     check_trade_item_traded

; Update owned trade items after eggs hatch
; Replaces
;   lui     a0, 0x8012
;   addiu   a0, a0, 0xA5D0
;   or      v0, $zero, $zero
.orga 0xAE795C
    jal     update_shiftable_trade_item_egg_hook
    nop
    lw      ra, 0x14($sp)
    addiu   sp, sp, 0x18
    jr      ra
    nop

; Prevent losing masks to SOLD OUT if child trade shuffle
; or single child mask shuffle is on
.orga 0xAE72D0
    jal     check_if_mask_sells_out
    nop
    bnez    v1, return_null_item_id
    nop
    nop

.orga 0xAE734C
return_null_item_id:

; Custom CanBuy shop function for right side masks to
; always check for all masks traded. Overwrites unused
; functions EnGirlA_CanBuy_Unk19 and EnGirlA_CanBuy_Unk20
.orga 0xC00FF4
    addiu   $sp, $sp, -0x18
    sw      $ra, 0x0014($sp)
    jal     CanBuy_RightSideMask
    nop
    lw      $ra, 0x0014($sp)
    jr      $ra
    addiu   $sp, $sp, 0x18
    nop
    nop
    nop

; Prevent reverting Zelda's Letter to Chicken when
; save warping from Zelda's courtyard before talking
; to Impa. Only applied if trade shuffle is on.
.orga 0xB06424
    jal     handle_child_zelda_savewarp
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

; Prevent obtaining the item on Zelda's Letter more
; than once.
.orga 0xEFE9B4
;.orga 0xEFE958
    jal     check_zelda_cutscene_watched
    nop
    bnez    v0, end_child_zelda_cutscene
    lbu     v1, 0x01F8(s0)
.orga 0xEFEA68
end_child_zelda_cutscene:
.orga 0xEFEA00
    nop

; Courtyard guards never block the way after talking to Zelda.
; En_Heishi1 init function branch logic nulled for EVENTCHKINF_80.
.orga 0xCD5E30
    nop
.orga 0xCD5E7C
    b       courtyard_guards_kill
.orga 0xCD5E8C
courtyard_guards_kill:

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
; burning kak from any entrance to kak (except the grottos)
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
; Load Audiobank using dmadata
;==================================================================================================
; Replaces: lui     a1, 0x0001
;           addiu   a1, a1, 0xD390
.orga 0xB2E840 ; in memory 0x800B88E0
    lw      a1, 0x8000B178

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
; Getting caught by Gerudo NPCs after obtaining Gerudo Card
;==================================================================================================
; Use unused message ID 0x6013 as our replacement text with two choice options
; Set custom callback to handle the new textbox choices
.orga 0xE1216C  ; White-clothed Gerudo
    jal     offer_jail_hook
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
; King Zora Init Moved Check Override
;==================================================================================================
; Replaces: lhu     t0, 0x0EDA(v0)
;           or      a0, s0, zero
;           andi    t1, t0, 0x0008

.orga 0xE565D0
    jal     kz_moved_check
    nop
    or      a0, s0, zero

; ==================================================================================================
; HUD Button Colors
; ==================================================================================================
; Fix HUD Start Button to allow a value other than 00 for the blue intensity
; Replaces: andi    t6, t7, 0x00FF
.orga 0xAE9ED8
    ori     t6, t7, 0x0000 ; add blue intensity to the start button color (Value Mutated in Cosmetics.py)

; Handle Dynamic Shop Cursor Colors
.orga 0xC6FF30
.area 0x4C, 0
    mul.s   f16, f10, f0
    mfc1    a1, f8          ; color delta 1 (for extreme colors)
    trunc.w.s f18, f16
    mfc1    a2, f18         ; color delta 2 (for general colors)
    swc1    f0, 0x023C(a0)  ; displaced code

    addiu   sp, sp, -0x18
    sw      ra, 0x04(sp)
    jal     shop_cursor_colors
    nop
    lw      ra, 0x04(sp)
    addiu   sp, sp, 0x18

    jr      ra
    nop
.endarea

; ==================================================================================================
; Chain Horseback Archery Rewards
; ==================================================================================================
; Replaces: jal     0x80022AD0
;           sw      a0, 0x0018(sp)
.orga 0xE12A04
    jal     handle_hba_rewards_chain
    sw      a0, 0x0018(sp)

; Replaces: sw      t6, 0x02A4(a0)
.orga 0xE12A20
    sw      v1, 0x02A4(a0)

;==================================================================================================
; Remove File 3 From File Select
;==================================================================================================
;Main Menu Up
; Replaces: sh      t6, 0xCA2A(at)
;           lh      t7, 0x4A2A(v1)
.orga 0xBAA168
    jal     skip_3_up_main
    sh      t6, 0xCA2A(at)

;Main Menu Down
; Replaces: sh      t5, 0xCA2A(at)
;           lh      t6, 0x4A2A(v1)
.orga 0xBAA198
    jal     skip_3_down_main
    sh      t5, 0xCA2A(at)

;Copy From Up
; Replaces: sh      t7, 0xCA2A(at)
;           lh      v1, 0x4A2A(t0)
.orga 0xBA16AC
    jal     skip_3_up_copy_from
    sh      t7, 0xCA2A(at)

;Copy From Down
; Replaces: sh      t9, 0xCA2A(at)
;           lh      v1, 0x4A2A(t0)
.orga 0xBA16E0
    jal     skip_3_down_copy_from
    sh      t9, 0xCA2A(at)

;Copy To Up
; Replaces: sh      t5, 0xCA2A(at)
;           lh      t6, 0x4A38(t0)
;           lh      v1, 0x4A2A(t0)
.orga 0xBA1C68
    jal     skip_3_up_copy_to
    sh      t5, 0xCA2A(at)
    lh      t6, 0x4A38(t0)

;Copy To Down
; Replaces: sh      t9, 0xCA2A(at)
;           lh      v1, 0x4A2A(t0)
.orga 0xBA1CD0
    jal     skip_3_down_copy_to
    sh      t9, 0xCA2A(at)

;Special Case For Copy File 2 Down
; Replaces: sh      t3, 0xCA2A(at)
;           lh      v1, 0x4A2A(t0)
.orga 0xBA1D04
    jal     skip_3_down_copy_to_2
    nop

;Erase Up
; Replaces: sh      t9, 0xCA2A(at)
;           lh      v1, 0x4A2A(t0)
.orga 0xBA32CC
    jal     skip_3_up_erase
    sh      t9, 0xCA2A(at)

;Erase Down
; Replaces: sh      t3, 0xCA2A(at)
;           lh      v1, 0x4A2A(t0)
.orga 0xBA3300
    jal     skip_3_down_erase
    sh      t3, 0xCA2A(at)

;File 3 Position
; Replaces: or      a0, s0, r0
;           lh      t3, 0x4A2E(a2)
.orga 0xBAF4F4
    jal     move_file_3
    or      a0, s0, r0

; Ignore File 3 when checking for available copy slot
; Replaces: lbu     t6, 0x001C(v0)
.orga 0xBAA3AC ; In memory: 0x803AE1AC
    or      t6, a1, r0

;==================================================================================================
; Make Twinrova Wait For Link
;==================================================================================================
;Hook into twinrova update function and check for links height
; Replaces: sw      s2, 0x44(sp)
;           sw      s0, 0x3C(sp)
.orga 0xD68D68
    jal     rova_check_pos
    sw      s2, 0x44(sp)

;If the height check hasnt been met yet, branch to the end of the update function
;This freezes twinrova until the condition is met
; Replaces: sdc1    f24, 0x30(sp)
;           lw      s2, 0x1C44(s3)
;           addiu   t6, r0, 0x03
;           sb      t6, 0x05B0(s1)
;           lbu     t7, 0x07AF(s3)
;           mfc1    a2, f22
;           mfc1    a3, f20
.orga 0xD68D70
    la      t1, START_TWINROVA_FIGHT
    lb      t1, 0x00(t1)
    beqz    t1, @Twinrova_Update_Return
    lw      ra, 0x4C(sp)
    jal     twinrova_displaced
    sdc1    f24, 0x30(sp)
.orga 0xD69398
@Twinrova_Update_Return:

;nop various things in the init function
.orga 0xD62100
    jal     twinrova_set_action_ice
.orga 0xD62110
    lui     at, 0x4248
.orga 0xD62128
    nop
.orga 0xD621CC
    jal     twinrova_set_action_fire
.orga 0xD621DC
    lui     at, 0x4248
.orga 0xD6215C
    nop
.orga 0xD6221C
    nop
.orga 0xD73118 ;reloc
    nop
.orga 0xD73128 ;reloc
    nop

;Update alpha of the portal
;Replaces: lbu     t8, 0x00(v0)
.orga 0xD69C80
    jal     rova_portal

;Update position of the ice portal
.orga 0xD6CC18
    jal     ice_pos
    nop

;Update position of the fire portal
.orga 0xD6CDD4
    jal     fire_pos
    nop

;==================================================================================================
; Fix Links Angle in Fairy Fountains
;==================================================================================================

;Hook great fairy update function and set position/angle when conditions are met
; Replaces: or      a0, s0, r0
;           or      a1, s1, r0
.orga 0xC8B24C
    jal     fountain_set_posrot
    or      a0, s0, r0

;==================================================================================================
; Prevent Carpenter Boss Softlock
;==================================================================================================
; Replaces: or      a1, s1, r0
;           addiu   a2, r0, 0x22
.orga 0xE0EC50
    jal     prevent_carpenter_boss_softlock
    or      a1, s1, r0

;==================================================================================================
; Skip Song Playback When Learning Songs
;==================================================================================================
; this hack sets the learning song ID to 0 (minuet) which forces the playback to be skipped.
; this change does not affect the value passed to Item_Give, so you still recieve the right song.
; this allows other actors to be responsible for showing the "you learned" text and avoids undesireable
; effects like suns song playback skipping time
;
; Replaces: sh      a2, 0x63ED(at)
.orga 0xB55428
    sh      r0, 0x63ED(at)

;==================================================================================================
; Skip Song of Storms Song Demonstration
;==================================================================================================
;skip playing the song demonstration
; Replaces: jal     0x800DD400 ;plays song demo
.orga 0xE42C00
   jal     sos_skip_demo

;hook at the beginning of the song playback function to do a few things:
;set player stateFlags2, change interface alpha, show song staff, change actionFunc
;if songs as items is on, dont show the staff
; Replaces: addiu    a0, a2, 0x20D8
.orga 0xE42B5C
   jal     sos_handle_staff

;after the `sos_handle_staff` hook, skip the rest of the original function
.orga 0xE42B64
   b       0xE42B64 + (4 * 14)
   nop

;hook into the function where the windmill guy is waiting for song playback
;for no songs as items: handle showing text at the right time
;for songs as items: give the item, set flags, set actionFunc and return
.orga 0xE429DC
   jal     sos_handle_item
   nop

;after the `sos_handle_item` hook, skip the rest of the original function
.orga 0xE429E4
   b       0xE429E4 + (4 * 84)
   nop

;dont allow link to talk to the windmill guy if he is recieving an item
; Replaces: lh      t6, 0x8A(s0)
;           lh      t7, 0xB6(s0)
;           lhu     t9, 0xB4AE(t9)
;           lw      v1, 0x1C44(s1)
.orga 0xE42C44
   jal     sos_talk_prevention
   lh      t6, 0x8A(s0)   ;displaced
   bnez_a  t2, 0xE42D64
   lw      v1, 0x1C44(s1) ;displaced

;==================================================================================================
; Fix Zelda in Final Battle
;==================================================================================================
;change zeldas actionFunc index from 07 to 0C
; Replaces: addiu    t6, r0, 0x07
.orga 0xE7CC90
    addiu    t6, r0, 0x0C

;change animation to wait anim if its not set yet
; Replaces: beqz     a1
;           or       a2, r0, r0
;           lui      a1, 0x0600
;           addiu    a1, a1, 0x6F04
;           addiu    a3, r0, 0x0000
.orga 0xE7D19C
    jal      zelda_check_anim
    lui      a1, 0x0600
    beq_a    a1, t0, 0xE7D1B4
    or       a2, r0, r0
    addiu    a3, r0, 0x0000

;set flag so tower collapse cs never attempts to play (tower collapse sequence on)
; Replaces: andi     t7, t6, 0xFF7F
.orga 0xE81128
    ori     t7, t6, 0x0080

;==================================================================================================
; Override Links call to SkelAnime_ChangeLinkAnimDefaultStop
;==================================================================================================
;override the call to SkelAnime_ChangeLinkAnimDefaultStop in 80388BBC to allow for
;special cases when changing links animation
; Replaces: jal      0x8008C178
.orga 0xBCDBD8
    jal     override_changelinkanimdefaultstop

;==================================================================================================
; Fix Royal Tombstone Cutscene
;==================================================================================================
;when the cutscene starts, move the grave back a bit so that the hole is not covered
; Replaces: sw       a1, 0x44(sp)
;           lw       t6, 0x44(sp)
.orga 0xCF7AD4
    jal     move_royal_tombstone
    sw      a1, 0x44(sp)

;==================================================================================================
; Speed Up Gold Gauntlets Rock Throw
;==================================================================================================
;replace onepointdemo calls for the different cases so the cutscene never plays
;for cases 0 and 4 set position so that the rock lands in the right place

;case 1: light trial (breaks on impact)
; Replaces: jal       0x8006B6FC
.orga 0xCDF3EC
    nop

;case 0: fire trial
; Replaces: jal       0x8006B6FC
.orga 0xCDF404
    nop

;case 4: outside ganons castle
; Replaces: jal       0x8006B6FC
.orga 0xCDF420
    jal     heavy_block_set_switch

;set links position and angle to the center of the block as its being lifted
; Replaces: or         t9, t8, at
;           sw         t9, 0x66C(s0)
.orga 0xBD5C58
    jal      heavy_block_posrot
    or       t9, t8, at

;set links action to 7 so he can move again
; Replaces: swc1      f4, 0x34(sp)
;           lwc1      f6, 0x0C(s0)
.orga 0xCDF638
    jal     heavy_block_set_link_action
    swc1    f4, 0x34(sp)

;reduce quake timer for case 1
;Replaces: addiu      a1, r0, 0x03E7
.orga 0xCDF790
    addiu      a1, r0, 0x1E

;skip parts of links lifting animation
;Replaces: sw         a1, 0x34(sp)
;          addiu      a1, s0, 0x01A4
.orga 0xBE1BC8
    jal    heavy_block_shorten_anim
    sw     a1, 0x34(sp)

;slightly change rock throw trajectory to land in the right place
;Replaces: lui        at, 0x4220
.orga 0xBE1C98
    lui    at, 0x4218

;==================================================================================================
; Skip Malons Song Demonstration
;==================================================================================================
;skip function call to show song demonstration
.orga 0xD7EB4C
    nop

;go straight to item function for songs as items
;Replaces: sw     t0, 0x04(a2)
;          sw     t1, 0x0180(a2)
.orga 0xD7EB70
    jal    malon_goto_item
    sw     t0, 0x04(a2)

;skip check for dialog state to be 7 (demonstration finished)
.orga 0xD7EBBC
    nop

;check for songs as items to handle song staff
;Replaces: jal    0x800DD400
.orga 0xD7EBC8
    jal    malon_handle_staff

;various changes to final actionFunc before normal cutscene would start
.orga 0xD7EBF0
    addiu   sp, sp, -0x18 ;move stuff around to save ra
    sw      ra, 0x14(sp)
    jal     malon_ra_displaced
    lw      v0, 0x1C44(a1)
.skip 4 * 1
    nop
.skip 4 * 2
    jal    malon_songs_as_items ;make branch fail if songs as items is on
    lhu    t8, 0x04C6(t8)
.skip 4 * 5
    nop
.skip 4 * 1
    jal    malon_show_text  ;dont set next cutscene index, also show text if song
.skip 4 * 2
    nop        ;dont set transition fade type
.skip 4 * 4
    nop        ;dont set load flag
.skip 4 * 2
    j      malon_check_give_item

;set relevant flags and restore malon so she can talk again
.orga 0xD7EC70
    j    malon_reload

;==================================================================================================
; Clean Up Big Octo Room For Multiple Visits
;==================================================================================================
;make link drop ruto if "visited big octo" flag is set
;Replaces: lh     t9, 0x1C(s0)
;          lh     t6, 0x1C(s0)
.orga 0xD4BCB0
    jal    drop_ruto
    lh     t9, 0x1C(s0)

;kill Demo_Effect if "visited big octo" flag is set
;Replaces: sw     a1, 0x64(sp)
;          lh     v0, 0x1C(s0)
.orga 0xCC85B8
    jal    check_kill_demoeffect
    sw     a1, 0x64(sp)

;==================================================================================================
; Override appearance of Zoras Sapphire spiritual stone inside Jabu
;==================================================================================================
.headersize(0x8092ACC0 - 0x00CC8430)
; Increase the size of DemoEffect actor to store override
.org 0x8093019c
; Replaces: .d32 0x00000190
.d32 0x000001C0

; Hook the function DemoEffect_DrawJewel
.org 0x8092e3f8
; Replaces:
;   addiu   sp, sp, -0x78
;   sw      s3, 0x40(sp)
    j   DemoEffect_DrawJewel_Hook
    nop
DemoEffect_DrawJewel_AfterHook:

;==================================================================================================
; Use Sticks and Masks as Adult
;==================================================================================================
; Deku Stick
; Replaces: addiu   t8, v1, 0x0008
;           sw      t8, 0x02C0(t7)
.orga 0xAF1814
    jal     stick_as_adult
    nop

; Masks
; Replaces: sw      t6, 0x0004(v0)
;           lb      t7, 0x013F(s0)
.orga 0xBE5D8C
    jal     masks_as_adult
    nop

;==================================================================================================
; Carpet Salesman Shop Shuffle
;==================================================================================================
; Replaces: sw      a1, 0x001C(sp)
;           sw      a2, 0x0020(sp)
.orga 0xE5B2F4
    jal     carpet_inital_message
    sw      a1, 0x001C(sp)

; Replaces: lui     a3, 0x461C
;           ori     a3, a3, 0x4000
.orga 0xE5B538
    jal     carpet_buy_item_hook
    lui     a3, 0x461C

;==================================================================================================
; Medigoron Shop Shuffle
;==================================================================================================
; Replaces: lui     a3, 0x43CF
;           ori     a3, a3, 0x8000
.orga 0xE1FEAC
    jal     medigoron_buy_item_hook
    lui     a3, 0x43CF

; Replaces: lui     v1, 0x8012
;           addiu   v1, v1, 0xA5D0
;           lw      t6, 0x0004(v1)
;           addiu   at, zero, 0x0005
;           addiu   v0, zero, 0x0011
;           beq     t6, zero, @medigoron_check_2nd_part
;           lui     a0, 0x8010
;           b       @medigoron_check_2nd_part
;           addiu   v0, zero, 0x0005
; @medigoron_check_2nd_part:
.orga 0xE1F72C
    addiu   sp, sp, -0x18
    sw      ra, 0x14(sp)
    jal     medigoron_inital_check
    nop
    lw      ra, 0x14(sp)
    addiu   sp, sp, 0x18
    slti    at, v0, 5
    bnez    at, @medigoron_check_return
    addiu   at, zero, 0x0005

.orga 0xE1F794
@medigoron_check_return:


;==================================================================================================
; Chest Game Keysanity
;==================================================================================================
; Replaces: sh     t8, 0x0204(s0)
;           sw     $zero, 0x0118(s0)

.orga 0xE94B9C ; In Memory 0x80B1946C
    addiu   t3, $zero, 0x908B ; Replaces text ID 0x002D

.orga 0xE94B30
    jal     chestgame_buy_item_hook
    sh      t8, 0x0204(s0)

; Replaces: sw     t3, 0x0014($sp)
;           sw     t2, 0x0010($sp)
.orga 0xE94774
    jal     chestgame_initial_message
    sw      t3, 0x0014($sp)

; Skip instruction to reset TCG chest flags
; Replaces: sw     $zero, 0x1D38(t8)
;           lhu    t0, 0x1402(v0)
.orga 0xE9474C
    jal     chestgame_no_reset_flag
    nop

; Skip instruction to set TCG keys to 0 every reload
; Replaces: sb      t9, 0x00BC(t1)
;           addiu   t2, s0, 0x0184
.orga 0xE94760
    jal     chestgame_no_reset_keys
    nop

; Change Chests so items don't change 50/50 between the room
; Inserts additonal code at: mtc1    $at, $f8
.orga 0xE435B4
    jal     chestgame_remove_chest_rng

; Change GetItemID that TCG Salesman gives while title card is up
.orga 0xE94C14
    addiu   a2, $zero, 0x0071   ; replaces 0x0042 (generic key) with 0x0071 (chest game key)

; Show a key in the unopened chest regardless of chest
; contents if the tcg_requires_lens setting is enabled.
; Left/right do the same check for the get item ID,
; but use different registers for the actor spawn branch
; and chest actor references for coordinates.
; Replaces:
;   lwc1    $f0, 0x0024(v1)
;   lwc1    $f2, 0x0028(v1)
.orga 0xE43964
    jal chestgame_force_game_loss_left
    nop
; Replaces:
;   lwc1    $f0, 0x0024(v0)
;   lwc1    $f2, 0x0028(v0)
.orga 0xE43A0C
    jal chestgame_force_game_loss_right
    nop

;==================================================================================================
; Bombchu Ticking Color
;==================================================================================================
; Replaces: ctc1    t9, $31
;           ori     t5, t4, 0x00FF
.orga 0xD5FF94
    jal     bombchu_back_color
    ctc1    t9, $31

;==================================================================================================
; Repoint English Message Table to JP
;==================================================================================================
;To make room for more message table entries, store the jp table pointer to the english one as well.
;The rest of this hack is implemented in Messages.py
; Replaces: sw      t7, 0x00(a1)
.orga 0xB575C8
    sw      t6, 0x00(a1)

; Dynamically load the en/jp message files for text lookup. Both files are utilized to make room
; for additional text. The jp file is filled first. The segment value for the requested text ID
; is used to manipulate the language bit to tell Message_OpenText (func_800DC838) which file
; to load and search. Hook at VRAM 0x800DCB60 in message.s
.orga 0xB52AC0
    jal     set_message_file_to_search
    nop

; The message lookup function uses a fixed reference to the first entry's segment to strip it from
; the combined segment/offset word. Since we have mixed segments in the table now, this is no
; longer safe. Load the correct segment into register a2 from the current message.
.orga 0xB4C980
    j       load_correct_message_segment
    nop

; Since message lookup already occurs in the above hook, remove the lookup from both the JP and EN
; branches.
.orga 0xB52AD0 ; JP branch
    nop
    nop
    nop
    nop
.orga 0xB52B64 ; EN branch
    nop
    nop

;==================================================================================================
; Null Boomerang Pointer in Links Instance
;==================================================================================================
;Clear the boomerang pointer in Links instance when the boomerangs destroy function runs.
;This fixes an issue where the boomerang trail color hack checks this pointer to write data.
; Replaces: sw      a0, 0x18(sp)
.orga 0xC5A9F0
    jal     clear_boomerang_pointer

;===================================================================================================
;Kill Door of Time collision when the cutscene starts
;===================================================================================================
.orga 0xCCE9A4
    jal     kill_door_of_time_col ; Replaces lui     $at, 0x3F80
    lw      a0, 0x011C(s0) ; replaces mtc1    $at, $f6

;===================================================================================================
; Don't grey out Goron's Bracelet as adult.
;===================================================================================================
.orga 0xBB66DC
    sh      zero, 0x025E(s6) ; Replaces: sh      v1, 0x025E(s6)
.orga 0xBC780C
    .byte 0x09               ; Replaces: 0x01

;==================================================================================================
; Prevent Mask de-equip if not on a C-button
;==================================================================================================
.orga 0xBCF8CC
    jal     mask_check_trade_slot   ; sb      zero, 0x014F(t0)

;===================================================================================================
; Randomize Frog Song Purple Rupees
;===================================================================================================
; Replaces: addiu   t1, zero, 0x55
.orga 0xDB1338
    addiu   t1, v0, 0x65

;===================================================================================================
; Allow ice arrows to melt red ice
;===================================================================================================
.orga 0xDB32C8
    jal     blue_fire_arrows ; replaces addiu at, zero, 0x00F0

;===================================================================================================
; Give each cursed skulltula house resident a different text ID, for skulltula reward hints
;===================================================================================================
.orga 0xEA2664
    addiu   t1, t1, 0x9003

;==================================================================================================
; Base Get Item Draw Override
;==================================================================================================
.orga 0xACD020
.area 0x44
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    jal     base_draw_gi_model
    nop
    lw      ra, 0x0014(sp)
    jr      ra
    addiu   sp, sp, 0x18
.endarea

;==================================================================================================
; TEMPORARILY COMMENTED OUT: Until issues with increasing the allocation size of the model are resolved
; Increases max size of GI Models
;==================================================================================================
; Replaces: addiu   a0, $zero, 0x2008
; .orga 0xBE2930
;    addiu   a0, $zero, 0x6000

;===================================================================================================
; Remove the cutscene when throwing a bomb at the rock in front of Dodongo's cavern
;===================================================================================================
.orga 0xD55998
    nop
    nop
    nop
    nop
    nop

.orga 0xD55A80
    nop
    nop
    nop
    nop
    nop
    nop

;==================================================================================================
; Seeding RNG
;==================================================================================================

; Truth spinner seeding RNG
; Replaces:
;   jal     func_800CDCCC
.orga 0xDB9E14
    jal     rand_seed_truth_spinner

;==================================================================================================
; Save current mask on scene change
;==================================================================================================
; Player_Destroy (0x80848BB4) - Its easier to just re-write the function than make a hook.
.orga 0xBE6564
    addiu   sp, sp, -0x10
    sw      ra, 0xC($sp)
    sw      s1, 0x8($sp)
    sw      s0, 0x4($sp)
    move    s0, a0
    move    s1, a1
    la      t0, SAVE_CONTEXT
    lui     t1, 0x0001
    addu    t1, t1, a1 ; PlayState + 0x10000
    lbu     t2, 0x1DE8(t1) ; playState->linkAgeOnLoad
    lbu     t3, 0x014F(a0) ; player->currentMask
    sw      t2, 0x0004(t0) ; saveContext->linkAge
    sb      t3, 0x003B(t0) ; this seems to be an empty slot
    move    a0, a1
    jal     0x8001AE04 ; Effect_Delete
    lw      a1, 0x660(s0) ; player->meleeWeaponEffectIndex
    jal     0x80072548 ; Magic_Reset
    move    a0, s1
    lw      ra, 0xC(sp)
    lw      s1, 0x8(sp)
    lw      s0, 0x4(sp)
    jr      ra
    addiu   sp, sp, 0x10
    ; Remove the rest of the old function
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

;==================================================================================================
; Load current mask on scene change
;==================================================================================================
; Player_Init (0x80844DE8)
; Replaces:
;jal     func_80834000
.orga 0xBE28EC
    jal     player_restore_mask

; Dumb hack to not relocate the function call to player_restore_mask
.orga 0xBF2C14
    nop

; Save the current mask on file save
; replaces
;lh      t8, 0xA4(s1)
;lui     t1, 0x8012
; SaveContext->save.info.playerData.savedSceneId = play->sceneId;
.orga 0xBC5120
    jal     player_save_mask
    nop

;===================================================================================================
; Link the Goron gives the item on either first choice selected
;===================================================================================================
; Replaces: addiu   t5, $zero, 0x3035
.orga 0xED3170
    addiu   t5, $zero, 0x3036
; Replaces: addiu   t9, $zero, 0x3033
.orga 0xED31B8
    addiu   t9, $zero, 0x3036

;===================================================================================================
; Fix Bongo cutscene start not skipped if jumpslash at the last possible frame
;===================================================================================================
; Replaces: slti    $at, a2, 0x0222
.orga 0xDA1D60
    slti    $at, a2, 0x0221
; Replaces: addiu   t9, $zero, 0x0222
.orga 0xDA1F94
    addiu   t9, $zero, 0x0221

;===================================================================================================
; Prevent Gohma from being stunned when climbing
;===================================================================================================
; Replaces lui     a1, 0x40A0
;          lui     a2, 0x3F00
.orga 0xC48BD4
    jal     gohma_climb
    nop

;===================================================================================================
; Prevent crash when diving in shallow water due to poorly initialized camera data
;===================================================================================================
; Replaces sw      v0, 0x011C(s0)
;          lh      t2, 0x014C(s0)
.orga 0xABDD10
    jal     camera_init
    nop

;===================================================================================================
;Update tunic color code to point to new table
;===================================================================================================
.orga 0xAEFFD0
;    lui     T9, 0x8040
;    ori   T9, T9, 0xC6EC
;    lui     T9, hi(tunic_colors)
;    ori   T9, T9, lo(tunic_colors)
    li  T9, CFG_TUNIC_COLORS

;===================================================================================================
; Various speedups
;===================================================================================================
; Scarecrow spawn cutscene
; Replaces jal     func_8006BA10
.orga 0xEF502C
    nop

; Water Temple Entrance Gate cutscene and timer
; Replaces addiu   t6, $zero, 0x0064
.orga 0xD5B53C
    addiu   t6, $zero, 0x0000
; Replaces jal     func_8006B6FC
.orga 0xD5B940
    nop
; x3 Speed on gate opening
; Replaces lui     a2, 0x3F19
.orga 0xD5B5FC
    lui     a2, 0x3FE6

; Gerudo Gate opening
; Replaces lui     a1, 0x3FCC
;          lui     a2, 0x3CF5
.orga 0xEB8ED8
   lui     a1, 0x41A0
   lui     a2, 0x41A0
; Replaces jal     func_8006B6FC
.orga 0xEB8E4C
    nop
; Replaces addiu   t7, $zero, 0x0028
.orga 0xEB8E6C
    addiu   t7, $zero, 0x0000

; Forest Red/Blue poe painting hit cutscene removed
; Replaces jal     func_8006B6FC
.orga 0xCE1600
    nop

; Biggoron puts the eyedrops
; Put eyedrops animation timer at 0 and skip the cutscene
; Replaces sh      t2, 0x0582(s0)
.orga 0xED665C
    sh      $zero, 0x0582(s0)
; Replaces jal     func_8006B6FC
.orga 0xED6670
    nop

; Scrub leader hiding for 1 frame instead of 300 when you show Skull Mask
; Replaces addiu   a1, $zero, 0x012C
.orga 0xEC8D20
    addiu   a1, $zero, 0x0001

; patch skulls spawn when the insect digs in and not 3sec after
; Replaces: slti    $at, t7, 0x003C
.orga 0xEFA318
    slti    $at, t7, 0x0001

; Carpenter Escape
; Timer before they escape succesfully
; Replaces 0x00000064
.orga 0xE10794
    .word 0x00000001
; Replaces 0x0000006E
.orga 0xE107A4
    .word 0x00000001
; Replaces 0x00000064
.orga 0xE107B4
    .word 0x00000001
; Replaces 0x00000078
.orga 0xE107C4
   .word 0x00000001
; Cutscene
; Replaces jal     func_800218EC
.orga 0xE0FF64
    nop

; Lake Hylia Shot the sun cutscene trigger
; Replaces sb      t8, -0x461C($at)
.orga 0xE9E268
    nop

; Forest Basement pillars cutscenes removed
; Replaces jal     func_8006B6FC
.orga 0xCC5DE8
    nop
; Replaces jal     func_8006B6FC
.orga 0xCC5DF4
    nop
; Replaces jal     func_8006B6FC
.orga 0xCC5F70
    nop
; Replaces jal     func_8006B6FC
.orga 0xCC604C
    nop
; Forest Basement pillars speed 3.0 by increments of 1.0 instead of 0.6 by increments of 0.02
; Replaces lui     a1, 0x3F19
.orga 0xCC5F14
    lui     a1, 0x4040
; Replaces lui     a2, 0x3CA3
.orga 0xCC5F18
    lui     a2, 0x3F80

;===================================================================================================
; Prevent Gohma from being stunned when climbing
;===================================================================================================
; Replaces lui     a1, 0x40A0
;          lui     a2, 0x3F00
.orga 0xC48BD4
    jal     gohma_climb
    nop

;===================================================================================================
; Prevent crash when diving in shallow water due to poorly initialized camera data
;===================================================================================================
; Replaces sw      v0, 0x011C(s0)
;          lh      t2, 0x014C(s0)
.orga 0xABDD10
    jal     camera_init
    nop

;===================================================================================================
;Update tunic color code to point to new table
;===================================================================================================
.orga 0xAEFFD0
;    lui     T9, 0x8040
;    ori   T9, T9, 0xC6EC
;    lui     T9, hi(tunic_colors)
;    ori   T9, T9, lo(tunic_colors)
    li  T9, CFG_TUNIC_COLORS

;==================================================================================================
; Shuffle Reward for Catching Hyrule Loach
;==================================================================================================
; Randomize the loach reward
; replaces mtc1 zero, f18
.orga 0xDCC138
    jal     give_loach_reward

; update sinking lure location so that it is available in any of the four positions
; replaces
; subu t2, v1, 2
; sll t2, t2, 1
.orga 0xDCC7E4
    jal     increment_sSinkingLureLocation
    lbu     t2, 0x34DB(a0)

; Modify loach behavior to pay attention to the sinking lure
; First call handles when loach is sitting on the bottom of the pond
; replaces
; addiu   $at, $zero, 0xFFFE
; and     t1, t8, at
.orga 0xdc689c
    jal     make_loach_follow_lure
    lw      t8, 0x0134(s0)

; Second call handles when loach periodically surfaces
; replaces
; addiu     at, zero, 0xFFFE
; and       t7, t9, at
; <skip>
; sw        t7, 0x0004(s0)
.orga 0xDC6AF0
    jal     make_loach_follow_lure
    lw      t8, 0x0134(s0)
.skip 4
    sw      t1, 0x0004(s0)
;=========================================================================================
; Add custom message control characters
;=========================================================================================

; In Message_Decode at the last control code check (0x01 for new line)
; Replaces
;   addiu   at, r0, 0x0001
;   bne     v0, at, 0x800DC580
.headersize (0x800110A0 - 0xA87000)
.org 0x800DC568
    j       Message_Decode_Control_Code_Hook
    nop

;===================================================================================================
; Shuffle individual ocarina notes hack
;===================================================================================================
; Ocarina buttons
.orga 0xB37EB0
; Replaced code:
;   lui     at, 0x8012
;   sw      t7, 0x1F24(at)
    jal     ocarina_buttons
    nop

;===================================================================================================
; Overrides the function that gives Fairy Ocarina on the Lost Woods Bridge
;===================================================================================================
.orga 0xACCDFC
; Replaces Item_Give(play, ITEM_OCARINA_FAIRY)
    jal      fairy_ocarina_getitem_override
    nop

;===================================================================================================
; Move the small key counter horizontally if we have boss key, to make room for the BK icon.
;===================================================================================================
; Replaces addiu   t7, $zero, 0x001A
;          addiu   t8, $zero, 0x00BE
.orga 0xAEB8AC
    jal     move_key_icon
    addiu   t8, $zero, 0x00BE

; Replaces
;          addiu   s2, $zero, 0x002A
;          addiu   t8, $zero, 0x00BE
.orga 0xAEB998
    jal     move_key_counter
    addiu   t8, $zero, 0x00BE

;===================================================================================================
; Adds a textbox for adult shooting gallery if game was played without a bow
;===================================================================================================
.orga 0xD36164
; Replaces sw      t4, 0x01EC(a2)
;          sw      t1, 0x0118(a2)
    jal     shooting_gallery_no_bow
    nop

;===================================================================================================
; Cancel Volvagia flying form hitbox when her health is already at O
;===================================================================================================
; Replaces addiu   a2, $zero, 0x0004
;          andi    t6, a1, 0x0002
.orga 0xCEA41C
    jal     volvagia_flying_hitbox
    nop

;================================================================================
; Reset choiceNum when decoding a new message
; prevents weird text alignment when going from message box with icon to no icon
;================================================================================
; Replaces sh   $zero, 0x4c0(at)
;          lhu  a3, 0x4c0(a3)
.org 0x800DA34C
    j       Message_Decode_reset_msgCtx.textPosX
    nop

.include "hacks/en_item00.asm"
.include "hacks/ovl_bg_gate_shutter.asm"
.include "hacks/ovl_bg_haka_tubo.asm"
.include "hacks/ovl_bg_spot18_basket.asm"
.include "hacks/ovl_en_dns.asm"
.include "hacks/ovl_en_ko.asm"
.include "hacks/ovl_en_kz.asm"
.include "hacks/ovl_obj_mure3.asm"
.include "hacks/z_parameter.asm"
.include "hacks/z_title.asm"
.include "hacks/z_file_choose.asm"
.include "hacks/ovl_en_changer.asm"
