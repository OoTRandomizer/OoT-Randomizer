;Accept86 WorkingNavi
;==================================================================================================

;WORKING_NAVI_DATA_GENERATED_TEXT_ROM => Texts with WORKING_NAVI_DATA_GENERATED_TEXT_INCREMENT_SYM increment (ROM-Address)
;WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM => LookUpTable For NaviTexts (8 Bytes each per text
        ;2 Bytes SaveDataOffset, 1 Byte SaveDataBitoffset, 1 Byte to handle by software,
        ;2 Bytes SavedataMask, 1 Byte ItemID, 1 Byte Sphere - for each required Item)

.definelabel working_navi_Save_Offset, 0xD4 + (52 * 0x1C) ;no chests or switches in Links house, so we can use that space hopefully




.org WORKING_NAVI_RAM

WORKING_NAVI_GLOBALS:

.area 0x40

.data:
   working_navi_cyclicLogicGlobals:  .word  0x0,0x0,0x0,0x0,0x0,0x0
   working_navi_TextPointerGlobal:  .word  0x0
   
.endarea   
   
.text:




.org WORKING_NAVI_DATA_CODE  ; see changed build.asm and addresses.asm
.area 0x4F0


working_navi_cyclicLogic_HOOK:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)

    ;lui t0, 0x0350            ;WORKING_NAVI_DATA_GENERATED_TEXT_ROM
    ;ori t0, 0x0700            ;WORKING_NAVI_DATA_GENERATED_TEXT_ROM ;TextTablePointer for Navi-Texts
    li t0, WORKING_NAVI_DATA_GENERATED_TEXT_ROM
    ;lui t7, 0x8050            ;WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM
    ;ori t7, 0x0400            ;WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM  ;LookupTablePointer for Navi-Texts
    li t7, WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM
                                    ;global variable 1 (Timer), 2 (showTextFlag), 
    la t1, working_navi_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2


;Progress made? =>Timer Reset
    lw t6, 0x0014 (t1)       ;load global variable 6 (Timer2)
    addiu t6, t6, 0x0001     ;increment
    sw t6, 0x0014 (t1)       ;store increment global variable 6 (Timer2)
    
    ori t3, r0, 0xd90    ; 1 minute
    
 beq t6, t3, @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE   ; every minute, Check if any Progress has been made - Reset timer if progress made
    nop

    li t7, WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM ; Reset t7 to LookupTable-Base

;Timercheck => otherwise say "You are doing so well, no need to bother you" 
    lw t5, 0x0008 (t1)       ;global Variable 3 - MaxTime when Navi gets activated
    lw t6, 0x0000 (t1)       ;load global variable 1 (Timer)
    addiu t6, t6, 0x0001     ;increment
    sw t6, 0x0000 (t1)       ;store increment global variable 1 (Timer)
    
 beq t6, t5, @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE   ; Check when Timer1 expires, too (when timers are desynced)
    nop


@WNAVI_AFTER_CL_HAS_ANY_PROGRESS_BEEN_MADE:





    li t7, WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM ; Reset t7 to LookupTable-Base
    lw t6, 0x0000 (t1)       ;load global variable 1 (Timer)
    lw t5, 0x0008 (t1)       ;global Variable 3 - MaxTime when Navi gets activated

    
 beq t6, t5, @WNAVI_CL_TEXTPOINTER_RESTORE   ; Restore Textpointer when Timer expired
    nop
@WNAVI_AFTER_CL_TEXTPOINTER_RESTORE:    
       
       
       
;actual timertest        
    slt t4, t6, t5           ;Test : t6(timer) less than t5 (global variable with TimerBase)
    ori t3, r0, 0x0001
    
    
 beq t4, t3, @WNAVI_CL_TIMER_NOK       ;BRANCH Jump over to @WNAVI_CL_TIMER_NOK when Timer not allowing Navi Text Output
    nop
    
    lui t4, 0x0000
    sw t4, 0x0000 (t1)       ;Reset Timer on global Variable 1, if timer was ok >= MaxTime
     
    
    
;after Timer OK => give useful text - calculate next Text
    addiu t7, t7, 0xfff8     ;From here is the LookupTablePointer setting. Decrement T7 LookupTablePointer by 4

@WNAVI_CL_INCREMENT_POINTERS:

    addiu t0, t0, WORKING_NAVI_DATA_GENERATED_TEXT_INCREMENT_SYM     ;TARGET Jump Here to INCREMENT_POINTERS From here is the TextTablePointer setting. Increment T0 TextTablePointer by 3C
    addiu t7, t7, 0x0008     ; 0x0004     ;Increment LookupTablePointer

    lb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    andi t6, t6, 0x00ff
    ori t5, r0, 0x0003
 beq t6, t5, @WNAVI_CL_INCREMENT_POINTERS       ; if already got, no need to check
    nop

    li a1, @WNAVI_CL_INCREMENT_POINTERS          ; A1: Increment Pointers Address
    move a2, t7                                 ; t7 LookupTablePointer
    jal @WNAVI_CL_CHECKSAVEDATA                  ;checks save Data for LookupTableEntry
    nop



;then set Textpointer

    ;when t0 not changed, no need to save
    lw t6, 0x0010 (t1)       ;load last Textpointer
 beq t6, t0, @@WNAVI_CL_NOTCHANGED_BRANCH
    nop
    
  ;Here: Textpointer has changed
    la t2, working_navi_TextPointerGlobal
    sw t0, 0x0000 (t2)       ; Store T0 in Global Variable 5 Textpointer
    sw t7, 0x000c (t1)       ; Save Global Variable 4 LastLookupTablePointer
    sw t0, 0x0010 (t1)       ; save last Textpointer
    lui t3, 0x0000
    sw t3, 0x0000 (t1)       ; Reset Timer TBD test this
    
    
@@WNAVI_CL_NOTCHANGED_BRANCH:
        

;Restore and Return
@WNAVI_CL_RETURN:         
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr      ra
    nop





;_______Subroutines for cyclic logic__________

    
@WNAVI_CL_TEXTPOINTER_RESTORE:
    la t3, working_navi_TextPointerGlobal
    la t1, working_navi_cyclicLogicGlobals
    lw t2, 0x0010 (t1)       ;Load Backup of lastTexpointer (normally t0, but that is generated from the ground up again)
    sw t2, 0x0000 (t3)       ;Store t2 in Global Variable 5 Textpointer, which was "You are doing so well, no need to bother you"
    

    ori t3, r0, 0x0001
    sw t3, 0x0004 (t1) ;ShowTextFlag set
    
    
    lui t2, 0x8011
    ori t2, 0xA608
    ori t3, r0, 0x0009   ;Manipulate OOT Navi Timer
    sb t3, 0x0000 (t2)
    
    
   
    J @WNAVI_AFTER_CL_TEXTPOINTER_RESTORE
    nop    
    
    
@WNAVI_CL_TIMER_NOK:
    la t1, working_navi_cyclicLogicGlobals
    
    ori t3, r0, 0x0001
    lw t2, 0x0004 (t1)          ;ShowTextFlag
 beq t2, t3, @WNAVI_CL_RETURN
    nop
    
    la t1, working_navi_TextPointerGlobal
    li t0, WORKING_NAVI_DATA_GENERATED_TEXT_ROM
    sw t0, 0x0000 (t1)       ;Store T0 in Global Variable 5 Textpointer
   
    J @WNAVI_CL_RETURN
    nop    

;_______Subroutine1__________
@WNAVI_CL_CHECKSAVEDATA: ;ARGUMENTS: a1=LABEL TO INCREMENT LookupTable; a2=LookupTablePointer

    lb t6, 0x0003 (a2)       ;Load "IsDone" Part of LookupTable-Element
    andi t6, t6, 0x00ff      ;BitMaskFilter
    ori t5, r0, 0x00ff
    
    
 beq t6, t5, @WNAVI_CL_INT_CHECKSAVEDATA_RETURN       ;BRANCH - EndofTable? to AFTER_TEXT_POINTER_UPDATE
    nop

    lw t6, 0x0000 (a2)       ;Load SaveDataOffset from LookupTablePointer in T6
    srl t6, t6, 16         
    andi t6, t6, 0xffff      ;Mask SaveDataOffset
    
 bne t6, r0, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP1       ;BRANCH - if LookupTable Offset is 0 Jump Back INCREMENT_POINTERS
    nop
    jr a1
    nop
@@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP1:
    
    
    lb t3, 0x0002 (a2)       ;Load SaveDataBitOffset
    andi t3, t3, 0x00ff

    lui t4, 0x8011           ;Load SaveDataBasePointer to Add to SaveDataOffset
    ori t4, t4, 0xa5d0       ;RAM Address NTSC1.0 0x8011A5D0 https://wiki.cloudmodding.com/oot/Save_Format#Save_File_Validation 

    addu t6, t6, t4          ;Get Resulting SaveDataPointer with Offset in t6
    lw t4, 0x0000 (t6)       ;T4: Resulting SaveDataElementWord
    srlv t4, t4, t3
    andi t3, t4, 0x00ff
    andi t4, t4, 0xffff
    
    lui t6, 0x0
    ori t6, 0xff
 beq t3, t6, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP2       ;BRANCH If SaveDataElementWord is FF => didnt get item
    nop     
    
;ItemID    
    lb t3, 0x0006 (a2)       ;Load ItemID
    andi t3, t3, 0x00ff
    
    lw t5, 0x0004 (a2)        ;load savemask in t5
    srl t5, t5, 16           ;Only max 2 Bytes large
    andi t5, t5, 0xffff
    and t4, t4, t5        ;mask saveData with saveDatamask
    
 bne t3, r0, @WNAVI_CL_CHECKSAVEDATA_ITEMID     ; to be tested
    nop
    
    
;Savemask 
    ;mask already done

 beq t4, r0, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP2       ;BRANCH If SaveData has this Item => Go to INCREMENT_POINTERS/a1
    nop
    jr a1
    nop
    
@@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP2:


    ori t6, r0, 0xffff
    ;the mask could be FF => save data has item if not FF
 beq t6, t5, @WNAVI_CL_SAVEMASKFF               ;BRANCH, MASK is FF, check savedata different
    nop
    
 
@WNAVI_CL_INT_CHECKSAVEDATA_RETURN:   
    jr ra
    nop
    
    
    
    
;____Sub-Subroutine1___    
@WNAVI_CL_SAVEMASKFF:        ; TARGET if Savedatamask is FF

    ;Savemask is FF
    ;t4: SaveDataElementWord , t5 SaveDataMask
    
 beq t4, t5, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP3       ;BRANCH If SaveData mask FF and Savedata not FF Item aquired => Go to INCREMENT_POINTERS/a1
    nop
    jr a1
    nop
@@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP3:


    J @WNAVI_CL_INT_CHECKSAVEDATA_RETURN
    nop



;____Sub-Subroutine2___
@WNAVI_CL_CHECKSAVEDATA_ITEMID: 
    ;t3 is ItemID
    ;t4: SaveDataElementWord 
    
;Check rutos letter / Bottle with letter
    ori t5, r0, 0x001B  ; item ID to compare

 bne t3, t5, @WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP5
    nop
    ;here it is rutos letter to check
    lui t6, 0x8011
    ori t6, t6, 0xa656 ;get bottle base address
    
    ;Bottle1
    lb t4, 0x0000 (t6)  
    andi t4, t4, 0x00ff
 bne t4, t5, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO1
    nop
    jr a1
    nop
@@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO1:
    
    ;Bottle2
    lb t4, 0x0001 (t6)  
    andi t4, t4, 0x00ff
 bne t4, t5, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO2
    nop
    jr a1
    nop
@@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO2:  
    
    ;Bottle3
    lb t4, 0x0002 (t6)  
    andi t4, t4, 0x00ff
 bne t4, t5, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO3
    nop
    jr a1
    nop
@@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO3: 
    
    ;Bottle4
    lb t4, 0x0003 (t6)  
    andi t4, t4, 0x00ff
 bne t4, t5, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO4
    nop
    jr a1
    nop
@@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO4:


; not needed anymore, because save and load in savedata now
;    ;King Zora Moved?
;    lui t6, 0x8011 
;    ori t6, t6, 0xB4AB ;get King Zora moved address
;    lb t4, 0x0000 (t6)  
;    andi t4, t4, 0x0008
    
; beq t4, r0, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO5 
;    nop
;    jr a1
;    nop
;@@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP_RUTO5:    
    
    J @WNAVI_CL_INT_CHECKSAVEDATA_RETURN
    nop  
    
    
@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP5:     
    
;normal item ID check
    andi t4, t4, 0x00ff
    sltu t6,t4,t3   ; SaveData < ItemID?
    ori t2, r0, 0x0001
    
 beq t6, t2, @@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP4       ;BRANCH If SaveData < ItemID, dont got item
    nop
    jr a1
    nop
@@WNAVI_CL_INT_CHECKSAVEDATA_DONT_JUMP4:


    J @WNAVI_CL_INT_CHECKSAVEDATA_RETURN
    nop  
    
    
    
    
    

;_______Subroutine2_______
@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE:
    la t1, working_navi_cyclicLogicGlobals
    lui t3, 0x0000
    sw t3, 0x0014 (t1)       ;Reset global variable 6 (Timer2)
    
    jal @WNAVI_CL_SAVEPROGRESS       ; <== Save progress in save, this is called every minute
    nop
    
    li t7, WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM

    J @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_INITJUMP
    nop
    
    
    
@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_GOT_ITEM:  
    lui t6, 0x0000
    lb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    ori t6, t6, 0x0001       ;Save Flag for gotten Item
    sb t6, 0x0003 (t7)
    
    ori t3, r0, 0x0001
    
; Reset ShowText, Reset Timer, if Item is newly gotten
 bne t6, t3, @@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_NO_TIMERRESET
    nop
    ori t6, t6, 0x0003       ;Save Flag for gotten Item "before"
    sb t6, 0x0003 (t7)
    
    la t4, working_navi_cyclicLogicGlobals
    lui t3, 0x0000
    sw t3, 0x0004 (t4) ;Reset ShowTextFlag
    sw t3, 0x0000 (t4) ;Reset Timer1 (NaviDelay)
@@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_NO_TIMERRESET:    
    
@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_ITEM_NOT_GOTTEN:
    addiu t7, t7, 0x0008     ; 0x0004     ;Increment LookupTablePointer
    
@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_INITJUMP:     

    ori t3, r0, 0x00ff
    lb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    andi t6, t6, 0x00ff      ;BitMaskFilter
    
 beq t3, t6, @WNAVI_AFTER_CL_HAS_ANY_PROGRESS_BEEN_MADE ; Escape at end of loop <= THIS IS THE RETURN OUT
    nop
    

    li a1, @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_GOT_ITEM     ; A1: Item Got Jump Address
    move a2, t7                                 ; t7 LookupTablePointer
    JAL @WNAVI_CL_CHECKSAVEDATA                  ;checks save Data for LookupTableEntry
    nop

    J @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE_ITEM_NOT_GOTTEN
    nop
    
    ;Heres no Return needed, always go to end of lookuptable
    
   
    
    
    
@WNAVI_CL_SAVEPROGRESS:
                                             ;global variable 1 (Timer), 2 (showTextFlag), 
    la t1, working_navi_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    lw t6, 0x0000 (t1)       ;load global variable timer
    li   t4, SAVE_CONTEXT 
    
    ; store timer in save  
    sw  t6, (working_navi_Save_Offset)(t4)
    addiu t4, t4, 4
    
    ; store show text flag
    lw t6, 0x0004 (t1)
    sb  t6, (working_navi_Save_Offset)(t4)
    addiu t4, t4, 1
    
;save progress bits    
    li t7, WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM
    lui t5, 0x0000
    lui t8, 0x0000
    
    J @WNAVI_CL_SAVEPROGRESS_INITJUMP
    nop
    
    
@WNAVI_CL_SAVEPROGRESS_NEXT:    
    
    addiu t7, t7, 0x0008     ; 0x0004     ;Increment LookupTablePointer
    addiu t5, t5, 1
    
@WNAVI_CL_SAVEPROGRESS_INITJUMP:     

    ori t3, r0, 0x00ff
    lb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    andi t6, t6, 0x00ff      ;BitMaskFilter
    
 beq t3, t6, @WWNAVI_CL_SAVEPROGRESS_END ; Escape at end of loop <= THIS IS THE RETURN OUT
    nop
    
; here we save our progress
   slti t3, t5, 8     ; t5 bitindex still ok?
 bne t3, r0, @@WNAVI_CL_SAVEPROGRESS_NO_NEXTBYTE
   nop
   
   ; if a byte is complete, save
   lui t5, 0x0000
   sb  t8, (working_navi_Save_Offset)(t4)
   addiu t4, t4, 1
   lui t8, 0x0000
   
@@WNAVI_CL_SAVEPROGRESS_NO_NEXTBYTE:

 beq r0, t6, @WNAVI_CL_SAVEPROGRESS_NEXT
    nop
;here we build our t8 progress-saveflag-bytes
    ori t9, r0, 1
    sllv t9, t9, t5
    or t8, t8, t9
    
    J @WNAVI_CL_SAVEPROGRESS_NEXT
    nop
   
@WWNAVI_CL_SAVEPROGRESS_END: 

    sb  t8, (working_navi_Save_Offset)(t4)
   
    jr ra
    nop    
    
.endarea     
    
;==================================================================================================

.org WORKING_NAVI_DATA_CODE2  ; see changed build.asm and addresses.asm
.area 0x1F0

working_navi_TextLoadLogic_HOOK:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    lui t2, 0x0000          ;just 0 in T2 for using with compares    
    
    lui t3, 0x0093          ; TBD why did this value change since Rando 1.0?
    ori t3, t3, 0x2ea0      ;TextLoadPointerMin old: 0x4af0
    slt t1, t3, a1          ;comparison, A1 = requested Textloadpointer of the game
    
 beq t1, t2, @@WNAVI_TLL_LOAD_TEXT      ;BRANCH if reqested Textpointer A1 < Min NaviSection: Jump LOAD_TEXT
    nop
    
    lui t3, 0x0093          ; TBD why did this value change since Rando 1.0?
    ori t3, t3, 0x37ac      ; TextLoadPointer max old: 0x5400
    slt t1, a1, t3          ;A1 < T3 (Max) req Textpointer A1 < Max NaviSection

 beq t1, t2, @@WNAVI_TLL_LOAD_TEXT      ;BRANCH if Textpointer < Max => Jump LOAD_TEXT
    nop
    
                            ; T7 Global Variable 5 Textpointer
    la t7, working_navi_TextPointerGlobal
    lw a1, 0x0000 (t7)      ; IF req Textpointer A1 in NaviSection => Load GlobalVar with Text of workingNavi in A1
    ;set dmaloadsize to textsize
    ori a2, r0, WORKING_NAVI_DATA_GENERATED_TEXT_INCREMENT_SYM
    
    ; Reset Textpointer stuff(cyclic logic), so the message isnt shown twice
    la t1, working_navi_TextPointerGlobal
    li t0, WORKING_NAVI_DATA_GENERATED_TEXT_ROM
    sw t0, 0x0000 (t1)       ;Store T0 in Global Variable  Textpointer (Reset)
    la t2, working_navi_cyclicLogicGlobals
    lui t3, 0x0000
    sw t3, 0x0004 (t2) ;ShowTextFlag Reset
    
    
    
    li t0, WORKING_NAVI_DATA_GENERATED_TEXT_ROM     ; if Text says "You are doing so well..." / Textpointer is on base, dont reset timer
 beq t0, a1, @@WNAVI_TLL_LOAD_TEXT
    nop
    
    sw t3, 0x0000 (t2) ;Timer1 Reset

    
@@WNAVI_TLL_LOAD_TEXT:        ;TARGET LOAD_TEXT
    jal 0x80000DF0          ;DMALoad Text in
    nop
    
         
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr      ra
    nop

;==================================================================================================


@WNAVI_CL_LOADPROGRESS:
                                             ;global variable 1 (Timer), 2 (showTextFlag), 
    la t1, working_navi_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    
    li   t4, SAVE_CONTEXT 
    
    ; load timer from save  
    lw  t6, (working_navi_Save_Offset)(t4)
    sw t6, 0x0000 (t1)       ;save global variable timer
    addiu t4, t4, 4
    
    ; store show text flag
    lbu  t6, (working_navi_Save_Offset)(t4)
    sw t6, 0x0004 (t1)
    addiu t4, t4, 1
    
    
    ;load progress bits    
    li t7, WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM
    lui t5, 0x0000
    lb  t8, (working_navi_Save_Offset)(t4)
    
    J @WNAVI_CL_LOADPROGRESS_INITJUMP
    nop
    
    
@WNAVI_CL_LOADPROGRESS_NEXT:    
    
    addiu t7, t7, 0x0008     ; 0x0004     ;Increment LookupTablePointer
    addiu t5, t5, 1
    
@WNAVI_CL_LOADPROGRESS_INITJUMP:     

    ori t3, r0, 0x00ff
    lb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    andi t6, t6, 0x00ff
    
 beq t3, t6, @WWNAVI_CL_LOADPROGRESS_END ; Escape at end of loop <= THIS IS THE RETURN OUT
    nop
    
    lui t6, 0x0000
    sb t6, 0x0003 (t7)       ;Reset "IsDone" Part of LookupTable-Element
    
; here we load our progress
   slti t3, t5, 8     ; t5 bitindex still ok?
 bne t3, r0, @@WNAVI_CL_LOADPROGRESS_NO_NEXTBYTE
   nop
   
   ; if a byte is complete, next one
   lui t5, 0x0000
   addiu t4, t4, 1
   
@@WNAVI_CL_LOADPROGRESS_NO_NEXTBYTE:

   lb  t8, (working_navi_Save_Offset)(t4)

;here we check our t8 progress-saveflag-bits
    ori t9, r0, 1
    sllv t9, t9, t5
    and t8, t8, t9

 beq r0, t8, @WNAVI_CL_LOADPROGRESS_NEXT  
    nop
;bit set for this lookuptableentry
    ori t6, r0, 0x0003
    sb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    
    J @WNAVI_CL_LOADPROGRESS_NEXT
    nop
   
@WWNAVI_CL_LOADPROGRESS_END: 

    ;dont overwrite ff end of lookuptable
    ;andi t8, t8, 0x00ff      ;BitMaskFilter
    ;sb t8, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    
    

    jr ra
    nop    
    
    




working_navi_Extended_Init_On_Saveloads_HOOK: ;<= Hook on Saveloads
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    ; Init global variables (for cyclic logic)
    la t1, working_navi_TextPointerGlobal
    li t0, WORKING_NAVI_DATA_GENERATED_TEXT_ROM
    sw t0, 0x0000 (t1)       ;Store T0 in Global Variable 5 Textpointer
   
    li t7, WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM
                                    ;global variable 1 (Timer), 2 (showtextflag), 
    la t1, working_navi_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    addiu t0, t0, WORKING_NAVI_DATA_GENERATED_TEXT_INCREMENT_SYM  ;The Textpointer Backup is not on "You are doing so well, no need to bother you" but on the first real hint
    sw t0, 0x0010 (t1)
    sw t7, 0x000C (t1)
    sw r0, 0x0014 (t1)       ;reset global variable 6 (Timer2)
    
    
    jal @WNAVI_CL_LOADPROGRESS  ; Load progress from save
    nop
    
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop
    
    
    
    
    
working_navi_Activate_Navi_In_Dungeons_HOOK:     ;<= hack, navi in dungeons, see working_navi.py

    ori v0, r0, 0x0141       ;0x41 <= Navi activated
    sh v0, 0x0002 (t8)  ; displaced code

    jr ra 
    nop   
    

.endarea 


    
.org WORKING_NAVI_DATA_GENERATED_TEXT_SYM  ; see addresses.asm, this is only done so we get a symbol in symbols_RAM.json
.area 0x1000
nop
.endarea



