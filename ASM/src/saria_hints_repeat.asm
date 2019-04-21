;Accept86 Saria hints repeat
;==================================================================================================
    
.definelabel Saria_Gossip_Save_Offset, 0xD4 + (57 * 0x1C) +0x10 



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
    srl t1, a1, 3       ; equals / 8
    
    ;get Bitoffset
    andi t2, a1, 0x7    ; equals % 8
    
    ;calc byte to save
    ori t6, t6, 0x1C
    multu t1, t6
    mflo t6
    addu t4, t4, t6
    lb t3, (Saria_Gossip_Save_Offset) (t4)
    ori t5, r0, 0x0001
    sllv t5, t5, t2
    or t3, t3, t5
    
    ;save
    sb t3, (Saria_Gossip_Save_Offset) (t4)    
    
    jr ra
    nop
    
    

    
@SARIA_GOSSIP_LOAD_ALL_FROM_SAVE:

    li   t4, SAVE_CONTEXT 
    
    ;load progress bits    
    lui t5, 0x0000                          ;current bitindex
    lb  t8, (Saria_Gossip_Save_Offset)(t4)  ;current loadbitmask from savedata
    
    lui at, 0           ; index
    
    J @SARIA_GOSSIP_LOADPROGRESS_INITJUMP
    nop
    
@SARIA_GOSSIP_LOADPROGRESS_NEXT:    
    
    addiu t5, t5, 1
    addiu at, at, 1
    
@SARIA_GOSSIP_LOADPROGRESS_INITJUMP:     

    ori t3, r0, 40
    slt t6, at, t3
    
 bne t6, r0, @WSARIA_GOSSIP_LOADPROGRESS_END ; Escape at end of loop <= THIS IS THE RETURN OUT
    nop
    

    
; here we load our progress
   slti t3, t5, 8     ; t5 bitindex still ok?
 bne t3, r0, @@SARIA_GOSSIP_LOADPROGRESS_NO_NEXTBYTE
   nop
   
   ; if a byte is complete, next one
   lui t5, 0x0000
   addiu t4, t4, 1
   
   andi t9, t4, 0x0003      ; equals %4
 bne t9, r0, @@SARIA_GOSSIP_LOADPROGRESS_NO_NEXTBYTE    ; if t4 bytecount modulo 4 is 0 => next unused savedata section
   nop
   ;here we go to the next unused savedata section
   addiu t4, t4, (0x1C-4)  
   
@@SARIA_GOSSIP_LOADPROGRESS_NO_NEXTBYTE:

   lb  t8, (Saria_Gossip_Save_Offset)(t4)

;here we check our t8 progress-saveflag-bits
    ori t9, r0, 1
    sllv t9, t9, t5
    and t8, t8, t9

 beq r0, t8, @SARIA_GOSSIP_LOADPROGRESS_NEXT  
    nop
;bit set for this entry

    ;===Do something here
    nop
    
    
    J @SARIA_GOSSIP_LOADPROGRESS_NEXT
    nop
   
@WSARIA_GOSSIP_LOADPROGRESS_END: 

    ;dont overwrite ff end of lookuptable

    jr ra
    nop    
    
    
    
    