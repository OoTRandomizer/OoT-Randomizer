;Accept86 Navi Hints
;==================================================================================================

;NAVI_HINTS_DATA_GENERATED_TEXT_ROM => Texts with NAVI_HINTS_DATA_GENERATED_TEXT_INCREMENT_SYM increment (ROM-Address)
;NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM => LookUpTable For NaviTexts (8 Bytes each per text
        ;2 Bytes SaveDataOffset, 1 Byte SaveDataBitoffset, 1 Byte to handle by software,
        ;2 Bytes SavedataMask, 1 Byte ItemID, 1 Byte Sphere - for each required Item)

.definelabel Navi_Hints_Save_Offset, 0xD4 + (52 * 0x1C) +0x10 
        ;no chests or switches in Links house, so we can use that space hopefully
        ;right, I remembered Cow in House.... so I´m only going to use unused spaces after all


NAVI_HINTS_GLOBALS:

.area 0x40
   Navi_Hints_cyclicLogicGlobals:  .word  0x0,0x0,0x0,0x0,0x0,0x0
   Navi_Hints_TextIDOffsetGlobal:  .word  0x0
   
.endarea   


NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM:
.area 0x300, 0      ;max 768 bytes for lookuptable, 96 Entrys/required items -1
.endarea


Navi_Hints_cyclicLogic_HOOK:
    addiu   sp, sp, -0x2C
    sw      ra, 0x0014(sp)
    sw      a0, 0x0018(sp)
    sw      a1, 0x0024(sp)
    sw      a2, 0x0028(sp)

    ;lui t7, 0x8050            ;NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM
    ;ori t7, 0x0400            ;NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM  ;LookupTablePointer for Navi-Texts
    la t7, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM
                                    ;global variable 1 (Timer), 2 (showTextFlag), 
    la t1, Navi_Hints_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    lui t0, 0x0000          ;TextID-Offset


;Progress made? =>Timer Reset
    lw t6, 0x0014 (t1)       ;load global variable 6 (Timer2)
    addiu t6, t6, 0x0001     ;increment
    sw t6, 0x0014 (t1)       ;store increment global variable 6 (Timer2)
    
    ori t3, r0, 0xd9    ; 6 seconds polling rate for updates
    
 beq t6, t3, @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE   ; every minute, Check if any Progress has been made - Reset timer if progress made
    nop

    la t7, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM ; Reset t7 to LookupTable-Base

;Timercheck => otherwise say "You are doing so well, no need to bother you" 
    lw t5, 0x0008 (t1)       ;global Variable 3 - MaxTime when Navi gets activated
    lw t6, 0x0000 (t1)       ;load global variable 1 (Timer)
    addiu t6, t6, 0x0001     ;increment
    sw t6, 0x0000 (t1)       ;store increment global variable 1 (Timer)
    
 beq t6, t5, @WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE   ; Check when Timer1 expires, too (when timers are desynced)
    nop


@WNAVI_AFTER_CL_HAS_ANY_PROGRESS_BEEN_MADE:





    la t7, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM ; Reset t7 to LookupTable-Base
    lw t6, 0x0000 (t1)       ;load global variable 1 (Timer)
    lw t5, 0x0008 (t1)       ;global Variable 3 - MaxTime when Navi gets activated

    
 beq t6, t5, @WNAVI_CL_TextIDOffset_RESTORE   ; Restore TextIDOffset when Timer expired
    nop
@WNAVI_AFTER_CL_TextIDOffset_RESTORE:    
       
       
       
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

    addiu t0, t0, 1     ;TARGET Jump Here to INCREMENT_POINTERS From here is the TextID setting
    addiu t7, t7, 0x0008     ; 0x0004     ;Increment LookupTablePointer

    lb t6, 0x0003 (t7)       ;Load "IsDone" Part of LookupTable-Element
    andi t6, t6, 0x00ff
    ori t5, r0, 0x0003
 beq t6, t5, @WNAVI_CL_INCREMENT_POINTERS       ; if already got, no need to check
    nop

    ;li a1, @WNAVI_CL_INCREMENT_POINTERS          ; A1: Increment Pointers Address
    move a0, t7                                 ; t7 LookupTablePointer
    JAL @WNAVI_CL_CHECKSAVEDATA                  ;checks save Data for LookupTableEntry
    nop
    
    ori t9, r0, 1
 beq t9, v0, @WNAVI_CL_INCREMENT_POINTERS
    nop



;then set TextIDOffset

    ;when t0 not changed, no need to save
    lw t6, 0x0010 (t1)       ;load last TextIDOffset
 beq t6, t0, @@WNAVI_CL_NOTCHANGED_BRANCH
    nop
    
  ;Here: TextIDOffset has changed
    la t2, Navi_Hints_TextIDOffsetGlobal
    sw t0, 0x0000 (t2)       ; Store T0 in Global Variable 5 TextIDOffset
    sw t7, 0x000c (t1)       ; Save Global Variable 4 LastLookupTablePointer
    sw t0, 0x0010 (t1)       ; save last TextIDOffset
    lui t3, 0x0000
    sw t3, 0x0000 (t1)       ; Reset Timer TBD test this
    
    
@@WNAVI_CL_NOTCHANGED_BRANCH:
        

;Restore and Return
@WNAVI_CL_RETURN:         
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    lw      a0, 0x0018(sp)
    sw      a1, 0x0024(sp)
    sw      a2, 0x0028(sp)
    addiu   sp, sp, 0x2c
    jr      ra
    nop





;_______Subroutines for cyclic logic__________

@WNAVI_CL_TextIDOffset_RESTORE:
    la t3, Navi_Hints_TextIDOffsetGlobal
    la t1, Navi_Hints_cyclicLogicGlobals
    lw t2, 0x0010 (t1)       ;Load Backup of lastTexpointer (normally t0, but that is generated from the ground up again)
    sw t2, 0x0000 (t3)       ;Store t2 in Global Variable 5 TextIDOffset, which was "You are doing so well, no need to bother you"
    

    ori t3, r0, 0x0001
    sw t3, 0x0004 (t1) ;ShowTextFlag set
    
    
    lui t2, 0x8011
    ori t2, 0xA608
    ori t3, r0, 0x0009   ;Manipulate OOT Navi Timer
    sb t3, 0x0000 (t2)
    
    
   
    J @WNAVI_AFTER_CL_TextIDOffset_RESTORE
    nop    
    
    
    
@WNAVI_CL_TIMER_NOK:
    la t1, Navi_Hints_cyclicLogicGlobals
    
    ori t3, r0, 0x0001
    lw t2, 0x0004 (t1)          ;ShowTextFlag
 beq t2, t3, @WNAVI_CL_RETURN
    nop
    
    la t1, Navi_Hints_TextIDOffsetGlobal
    sw r0, 0x0000 (t1)       ;Store 0 in Global Variable 5 TextID-Offset
   
    J @WNAVI_CL_RETURN
    nop    




@WNAVI_CL_CHECKSAVEDATA: ;ARGUMENTS: a0=LookupTablePointer
    addiu   sp, sp, -0x24
    sw      ra, 0x0014(sp)
    sw      t1, 0x0018(sp)
    sw      t7, 0x001c(sp)
    sw      t0, 0x0020(sp)

    jal Navi_CheckSaveData
    nop
    
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    lw      t1, 0x0018(sp)
    lw      t7, 0x001c(sp)
    lw      t0, 0x0020(sp)
    addiu   sp, sp, 0x24
    jr ra
    nop
    
    

@WNAVI_CL_HAS_ANY_PROGRESS_BEEN_MADE:
   
    addiu   sp, sp, -0x24
    sw      ra, 0x0014(sp)
    sw      t1, 0x0018(sp)
    sw      t7, 0x001c(sp)
    sw      t0, 0x0020(sp)


    la a0, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM
    la a1, Navi_Hints_cyclicLogicGlobals 
    jal Navi_has_any_progress_been_made
    nop
    
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    lw      t1, 0x0018(sp)
    lw      t7, 0x001c(sp)
    lw      t0, 0x0020(sp)
    addiu   sp, sp, 0x24
    
    J  @WNAVI_AFTER_CL_HAS_ANY_PROGRESS_BEEN_MADE
    nop



   
   
 ;_______Save and Load__________   
    
    
WNAVI_CL_SAVEPROGRESS:
                                             ;global variable 1 (Timer), 2 (showTextFlag), 
    la t1, Navi_Hints_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    lw t6, 0x0000 (t1)       ;load global variable timer
    li   t4, SAVE_CONTEXT 
    
    ; store timer in save  
    sw  t6, (Navi_Hints_Save_Offset)(t4)
    ;addiu t4, t4, 4
    ;here we go to the next unused savedata section
    addiu t4, t4, 0x1C  
    
    ; store show text flag
    lw t6, 0x0004 (t1)
    sb  t6, (Navi_Hints_Save_Offset)(t4)
    addiu t4, t4, 1
    
;save progress bits    
    la t7, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM
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
   sb  t8, (Navi_Hints_Save_Offset)(t4)
   addiu t4, t4, 1
   lui t8, 0x0000
   
   andi t9, t4, 0x0003
 bne t9, r0, @@WNAVI_CL_SAVEPROGRESS_NO_NEXTBYTE    ; if t4 bytecount modulo 4 is 0 => next unused savedata section
   nop
   ;here we go to the next unused savedata section
   addiu t4, t4, (0x1C-4)   
   
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

    sb  t8, (Navi_Hints_Save_Offset)(t4)
   
    jr ra
    nop    
    
    
    
@WNAVI_CL_LOADPROGRESS:
                                             ;global variable 1 (Timer), 2 (showTextFlag), 
    la t1, Navi_Hints_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    la a0, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM
    la a1, Navi_Hints_cyclicLogicGlobals 
    jal Navi_LoadProgress
    nop
    
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop    
    
    
    
    
;_______Other Hooks__________

Navi_Hints_Extended_Init_On_Saveloads_HOOK: ;<= Hook on Saveloads
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    ; Init global variables (for cyclic logic)
    la t1, Navi_Hints_TextIDOffsetGlobal
    sw r0, 0x0000 (t1)       ;Store T0 in Global Variable 5 TextID-Offset
   
    la t7, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE_SYM
                                    ;global variable 1 (Timer), 2 (showtextflag), 
    la t1, Navi_Hints_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    ori t0, r0, 1  ;The TextID-Offset Backup is not on "You are doing so well, no need to bother you" but on the first real hint
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
    
    
        
Navi_Hints_Activate_Navi_In_Dungeons_HOOK:     ;<= hack, navi in dungeons, see Navi_Hints.py

    ori v0, r0, 0x0141       ;0x41 <= Navi activated
    sh v0, 0x0002 (t8)  ; displaced code

    jr ra 
    nop   



NaviHints_TextID_HOOK:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    ;displaced code
    jal OOT_Navi_Saria_TextID_Generation
    nop
    
    
    lw t2, NAVI_HINTS_CONDITION
 beq t2, r0, @@NaviHints_Return
    nop
    
    ;first check if Navi text
    
    ori t2, r0, (0x0141 -1)                  ;Navi Text ID low
    slt t1, t2, v0        

 beq t1, r0, @@NaviHints_Return      ;BRANCH if reqested Textpointer A1 < Min
    nop
    
    ori t2, r0, (0x015f +1)                  ;Navi Text ID high    
    slt t1, v0, t2   
    
  beq t1, r0, @@NaviHints_Return      ;BRANCH if reqested Textpointer A1 < Min
    nop     
    
    ; OK its a Navi Text
    ;=> Modify r0
    la t2, Navi_Hints_TextIDOffsetGlobal
    lw v0, 0x0000 (t2)       ; Load Global Variable 5 TextIDOffset
    addiu v0, v0, Navi_Hints_TextID_Base
    andi v0, v0, 0xffff
    
    @@NaviHints_Return:


    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop


