;Accept86 Navi Hints
;==================================================================================================

;NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE => LookUpTable For NaviTexts (8 Bytes each per text
        ;2 Bytes SaveDataOffset, 1 Byte SaveDataBitoffset, 1 Byte to handle by software,
        ;2 Bytes SavedataMask, 1 Byte ItemID, 1 Byte Sphere - for each required Item)


NAVI_HINTS_GLOBALS:
.area 0x40
   Navi_Hints_cyclicLogicGlobals:  .word  0x0,0x0,0x0,0x0,0x0,0x0
   Navi_Hints_TextIDOffsetGlobal:  .word  0x0
.endarea   


NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE:
.area 0x300, 0      ;max 768 bytes for lookuptable, 96 entrys/required items -1
.endarea


Navi_Hints_cyclicLogic_HOOK:
    addiu   sp, sp, -0x2C
    sw      ra, 0x0014(sp)
    sw      a0, 0x0018(sp)
    sw      a1, 0x0024(sp)
    sw      a2, 0x0028(sp)
    
    lw t2, NAVI_HINTS_CONDITION
 beq t2, r0, @@WNAVI_CL_RETURN
    nop

    la a0, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE
                                            ;global variable 1 (Timer), 2 (showTextFlag), 
    la a1, Navi_Hints_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    la a2, Navi_Hints_TextIDOffsetGlobal


    jal Navi_CyclicLogic  ;in ___C___ cyclic logic handling
    nop

;Restore and Return
@@WNAVI_CL_RETURN:         
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    lw      a0, 0x0018(sp)
    sw      a1, 0x0024(sp)
    sw      a2, 0x0028(sp)
    addiu   sp, sp, 0x2c
    jr      ra
    nop

   
   
 ;_______LoadProgress________   
    
WNAVI_CL_LOADPROGRESS:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
                                             ;global variable 1 (Timer), 2 (showTextFlag), 
    la t1, Navi_Hints_cyclicLogicGlobals   ;3 (Max Time when Navi activated - value comes from python patched ROM Patches.py)
                                             ;4 (LastLookupTablePointer); 5(LastTextTablePointer)
                                             ;6 Timer2
    
    
    la a0, NAVI_HINTS_DATA_GENERATED_LOOKUPTABLE
    la a1, Navi_Hints_cyclicLogicGlobals 
    jal Navi_LoadProgress                   ;in ___C___ load progress
    nop
    
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop    
    
    
    
    
;_______Other Hooks__________
        
Navi_Hints_Activate_Navi_In_Dungeons_HOOK:     ;<= hack, navi in dungeons, see Navi_Hints.py

    LBU V0, 0x0002 (T8)  ; displaced code
    ORI V0, V0, 0x0100   ; displaced code
    
    lw t2, NAVI_HINTS_CONDITION
 beq t2, r0, @@NAVI_IN_DUNGEONS_END
    nop

    ori v0, r0, 0x0141       ;0x141 <= Navi activated
    sh v0, 0x0002 (t8)  
    
@@NAVI_IN_DUNGEONS_END:

    jr ra 
    nop   



NaviHints_TextID_HOOK:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    ;displaced code
    jal OOT_Navi_Saria_TextID_Generation        ;OOT vanilla function
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
    ;=> Modify v0
    lw v0, Navi_Hints_TextIDOffsetGlobal      ; Load Global Variable 5 TextIDOffset
    lw t5, Navi_Hints_TextID_Base
    addu v0, v0, t5
    andi v0, v0, 0xffff
    
    
    @@NaviHints_Return:
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop


