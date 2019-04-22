;Accept86 Saria hints repeat
;==================================================================================================
    
.definelabel Saria_Gossip_Save_Offset, 0xD4 + (57 * 0x1C) +0x10 

Saria_Hints_Globals:  .word  0x0, 0x0, 0x0   ;1:last TextID loaded, 2:internal GossipText index
                                             ;3:Activation

Saria_TextID_HOOK:
    addiu   sp, sp, -0x40
    sw      ra, 0x0014(sp)
    sw      at, 0x0018(sp)
    sw      t1, 0x001C(sp)
    sw      t2, 0x0020(sp)
    sw      t3, 0x0024(sp)
    sw      t4, 0x0028(sp)
    sw      t5, 0x002C(sp)
    sw      t6, 0x0030(sp)
    sw      t7, 0x0034(sp)
    sw      t8, 0x0038(sp)
    sw      t9, 0x003C(sp)

    ;displaced code
    sh t9, 0x62F9 (at)
    
    ;t9 is the TextID
    
    la t1, Saria_Hints_Globals
    lw t2, 0x0000 (t1)      ;Load Last TextID
    
    ori t3, r0, 0x00e0  ; ID-You want to talk to Saria, right?
 beq t2, t3, @@Saria_TextID_StartNew
    nop
    
    ori t3, r0, 0x00e3  ; ID-Do you want to talk to Saria again?
 beq t2, t3, @@Saria_TextID_StartNew
    nop
    
    J @@Saria_TextID_Continue
    nop
    
@@Saria_TextID_StartNew:
    sw r0, 0x0004 (t1)          ;Reset Text Index
    
@@Saria_TextID_Continue:
    sw t9, 0x0000 (t1)          ;Save Last TextID
    
    
    lw t2, 0x0008 (t1)          ;Load Activation
 bne t2, r0, @@Saria_TextID_Change
    nop
           
    
; Is it a Saria Text?    
    
    ori t2, r0, 0x0160                  ;saria Text ID low
    slt t1, t2, t9        

 beq t1, r0, @@Saria_TextID_END      ;BRANCH if reqested Textpointer A1 < Min
    nop
    
    ori t2, r0, 0x016c                  ;saria Text ID high - TBD is this correct? 
    slt t1, t9, t2   
    
  beq t1, r0, @@Saria_TextID_END      ;BRANCH if reqested Textpointer A1 < Min
    nop     
 
@@Saria_TextID_Change: 
    ori t2, r0, 0x0001
    sw t2, 0x0008 (t1)          ;save Activation  
     
    jal @GET_NEXT_GOSSIP_ID
    nop
    move t9, v0                 ; Modify T9 with the new TextID
    sh t9, 0x62F9 (at)


@@Saria_TextID_END:
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    lw      at, 0x0018(sp)
    lw      t1, 0x001C(sp)
    lw      t2, 0x0020(sp)
    lw      t3, 0x0024(sp)
    lw      t4, 0x0028(sp)
    lw      t5, 0x002C(sp)
    lw      t6, 0x0030(sp)
    lw      t7, 0x0034(sp)
    lw      t8, 0x0038(sp)
    lw      t9, 0x003C(sp)
    addiu   sp, sp, 0x40
    jr ra
    nop  










SARIA_HINTS_GOSSIP_READING: ;arguments: a1 = Textpointer, a2 = TextID
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    ; Get Message Text Index offset
    jal @get_SariaIndexOffset_ByTextPointer
    nop
    ; v0 has the indexoffset now

    move a1, v0                     ;a1 is indexoffset of gossiptext now
    jal @SARIA_GOSSIP_SAVEPROGRESS
    nop
    

    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop    
    
    
    
@get_SariaIndexOffset_ByTextPointer:    ; arguments: a1 is gossip Textpointer to find

    li t1, TABLE_START_RAM
    ori t4, r0, 0x0401  ;TextStart GossipTexts
    
@@get_SariaIndexOffset_ByID_inc:
    addiu t1, t1, 8 
    lh t3, 0x0000 (t1)
 bne t3, t4, @@get_SariaIndexOffset_ByID_inc 
    nop
    
    lui t7, 0x0000
    j @@get_SariaIndexOffset_ByID_initjump
    nop
@@get_SariaIndexOffset_ByID_inc2:
    addiu t1, t1, 8 
@@get_SariaIndexOffset_ByID_initjump:
    lw t3, 0x0004 (t1)
    lui t5, 0x00ff
    ori t5, t5, 0xffff
    and t3, t3, t5
    li t4, TEXT_START
    addu t3, t3, t4
    addiu t7, t7, 0x0001
    
 bne t3, a1, @@get_SariaIndexOffset_ByID_inc2 
    nop
    
    ;now in t7 is the indexoffset
    move v0, t7
    
    jr ra
    nop
    
    
    
     
    
@SARIA_GOSSIP_SAVEPROGRESS: ; a1 = bitIndex to store

    li   t4, SAVE_CONTEXT 
    
    ;get byteoffset
    srl t3, a1, 5       ; equals / 32
    
    ;get Bitoffset
    andi t2, a1, 0x1F    ; equals % 32
    
    ;calc byte to save
    ori t6, r0, 0x1C
    multu t3, t6
    mflo t6
    addu t4, t4, t6
    lw t3, (Saria_Gossip_Save_Offset) (t4)
    ori t5, r0, 0x0001
    sllv t5, t5, t2
    or t3, t3, t5
    
    ;save
    sw t3, (Saria_Gossip_Save_Offset) (t4)    
    
    jr ra
    nop
    
    

    
@GET_NEXT_GOSSIP_ID:
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    li   t4, SAVE_CONTEXT 
    
    ;load progress bits    
    lui t5, 0x0000                          ;current bitindex
    lb  t8, (Saria_Gossip_Save_Offset)(t4)  ;current loadbitmask from savedata
    
    la t1, Saria_Hints_Globals
    lui at, 0x0000          ; current Index

@Get_Next_GossipID_NEXT:
    ori t3, r0, 40
    slt t6, at, t3
    
 beq t6, r0, @WGet_Next_GossipID_END ; Escape at end of loop <= THIS IS THE RETURN OUT
    nop
    
; here we load our progress
   slti t3, t5, 8     ; t5 bitindex still ok?
 bne t3, r0, @@Get_Next_GossipID_NO_NEXTBYTE
   nop
   
   ; if a byte is complete, next one
   lui t5, 0x0000
   addiu t4, t4, 1
   
   andi t9, t4, 0x0003      ; equals %4
 bne t9, r0, @@Get_Next_GossipID_NO_NEXTBYTE    ; if t4 bytecount modulo 4 is 0 => next unused savedata section
   nop
   ;here we go to the next unused savedata section
   addiu t4, t4, (0x1C-4)  
   
@@Get_Next_GossipID_NO_NEXTBYTE:

   lb  t8, (Saria_Gossip_Save_Offset)(t4)

;here we check our t8 progress-saveflag-bits
    ori t9, r0, 1
    sllv t9, t9, t5
    and t8, t8, t9
    
    addiu t5, t5, 1             ;Increase Bitindex
    addiu at, at, 1             ;Increase CurrentIndex
    
 beq r0, t8, @Get_Next_GossipID_NEXT  
    nop
    
;bit set for this entry

    lw t2, 0x0004 (t1)      ; load lastIndex
    slt t3, at, t2
 bne t3, r0, @Get_Next_GossipID_NEXT        ;NextEntry if continuation not reached
    nop
    
    sw at, 0x0004 (t1)      ; save lastIndex
    
    ;set TextID by entry found
    move a1, at
    jal @get_SariaTextID_byIndexOffset
    nop
    
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop  
   
@WGet_Next_GossipID_END: 

    ;set TextID
    ori v0, r0, 0x00e3  ;Do you want to talk to Saria again?
    sw r0, 0x0008 (t1)  ;reset activation

    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop    
    
    
    
    
    
@get_SariaTextID_byIndexOffset:    ; arguments: a1 is IndexOffset

    li t1, TABLE_START_RAM
    ori t4, r0, 0x0401  ;TextStart GossipTexts
    
@@get_SariaIndexOffset_ByID_inc:
    addiu t1, t1, 8 
    lh t3, 0x0000 (t1)
 bne t3, t4, @@get_SariaIndexOffset_ByID_inc 
    nop
    
    ori t2, r0, 0x0008
    multu a1, t2
    mflo t2
    
    addu t1, t1, t2
    
    ;now in t1 is the TextTableAddress
    lh v0, 0x0000 (t1)
    
    jr ra
    nop
    
    
    