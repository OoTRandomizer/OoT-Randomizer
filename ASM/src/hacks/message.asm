.headersize(0x800D5EF0 - 0x00B4BE50)

.org 0x800DCE38
    ; Replaces jal     func_800DC838
    jal     grab_textbox_id

;================================================================================
; Fixes crashing when learning non-warp songs during Nayru's love when cutscenes
; are on and song playback enabled.
;================================================================================
; Replaces  li  t7,1      (msgCtx->stateTimer = 1)
.org 0x800debb8     ; in Message_DrawMain
    li  t7,2        ; Add one extra frame between Ocarina effect and Nayru killed

;================================================================================
; Repoint vanilla non-wide message character width table
;================================================================================
; This file is included by ASM/src/hacks.asm as hacks/message.asm.
;
; Object/map note for this hack context:
;   .headersize maps z_message_z_game_over.o .text offset 0 to VRAM 0x800D5EF0.
;   Message_OpenText is .text + 0x6948, therefore 0x800DC838 here.
;   The sFontWidths HI/LO relocation sites are Message_OpenText - 0x279C / -0x278C.
;
; LANG_CHAR_WIDTHS is added after CFG_BOSSES in config.asm. Newly-added config labels
; are not always visible in this armips pass, so this uses the already-visible
; CFG_BOSSES anchor instead of referencing LANG_CHAR_WIDTHS directly.
;
; Current config layout:
;   CFG_BOSSES size = 21 * 0x9 = 0xBD
;   LANG_CHAR_WIDTHS starts at CFG_BOSSES + 0xBD
;   vanilla raw-byte index compensation = 0x20 * sizeof(f32) = 0x80
;   load base = LANG_CHAR_WIDTHS - 0x80 = CFG_BOSSES + 0x3D

.definelabel MESSAGE_OPEN_TEXT_VRAM, 0x800DC838

.org MESSAGE_OPEN_TEXT_VRAM - 0x279C
    lui     at, hi(LANG_CHAR_WIDTHS - 0x80)

.org MESSAGE_OPEN_TEXT_VRAM - 0x278C
    lwc1    f16, lo(LANG_CHAR_WIDTHS - 0x80)(at)


;================================================================================
; JP/wide text metrics runtime switch
;================================================================================
; The old Python-side immediate patch was fragile because it depended on exact ROM
; offsets. Hook the JP branch in Message_OpenText instead. Non-JP text still uses
; the original English branch. JP/wide languages call the C helper, which checks
; LANG_WIDE_TEXT_ENGLISH_METRICS and writes either vanilla JP metrics or English-like
; metrics at runtime.
;
; Original JP branch in z_message_z_game_over.o:
;   Message_OpenText + 0x108  (.text + 0x6A50)  starts JP metrics writes
;   Message_OpenText + 0x144  (.text + 0x6A8C)  rejoins after metrics selection

.definelabel MESSAGE_OPEN_TEXT_JP_METRICS_VRAM, MESSAGE_OPEN_TEXT_VRAM + 0x108
.definelabel MESSAGE_OPEN_TEXT_AFTER_METRICS_VRAM, MESSAGE_OPEN_TEXT_VRAM + 0x144

.org MESSAGE_OPEN_TEXT_JP_METRICS_VRAM
.area 0x24, 0
    ; Preserve the live values used after the metrics block.
    addiu   sp, sp, -0x08
    sw      v1, 0x0000(sp)      ; current textId
    jal     Message_ApplyJpTextMetrics
    sw      a1, 0x0004(sp)      ; gSaveContext pointer
    lw      v1, 0x0000(sp)
    lw      a1, 0x0004(sp)
    addiu   sp, sp, 0x08
    b       MESSAGE_OPEN_TEXT_AFTER_METRICS_VRAM
    nop
.endarea

;================================================================================
; Item icon placement override
;================================================================================
; Do not replace Message_LoadItemIcon as a whole.  The original function also
; performs the icon DMA request, map special-case palette writes, msgBufPos++,
; and choiceNum=1.  Reimplementing that in C proved fragile and caused icons to
; disappear on hardware/emulator.
;
; Instead, keep the vanilla function body and only replace the two tiny blocks
; that load sIconItem32XOffsets[language] / sIconItem24XOffsets[language].
; The patched blocks ask C for the desired offset, then resume the original
; function before the DMA setup.  This is the trampoline-style hook we want:
;
;   caller jal Message_LoadItemIcon
;       -> vanilla prologue
;       -> patched offset block
;       -> original DMA/setup/msgBufPos/choiceNum code
;       -> original return to caller
;
; The helper implements the three cases:
;   English/non-JP: use EN icon offsets
;   normal JP:      use JP icon offsets
;   JP wide metrics:use EN icon offsets

.definelabel MESSAGE_LOAD_ITEM_ICON_VRAM, 0x800DA16C
.definelabel MESSAGE_LOAD_ITEM_ICON_32_OFFSET_BLOCK_VRAM, 0x800DA1B8
.definelabel MESSAGE_LOAD_ITEM_ICON_32_AFTER_OFFSET_BLOCK_VRAM, 0x800DA214
.definelabel MESSAGE_LOAD_ITEM_ICON_24_OFFSET_BLOCK_VRAM, 0x800DA248
.definelabel MESSAGE_LOAD_ITEM_ICON_24_AFTER_OFFSET_BLOCK_VRAM, 0x800DA2A0

; Restore the vanilla entry in case this patch is applied on top of the previous
; full-function trampoline build.
.org MESSAGE_LOAD_ITEM_ICON_VRAM
    addiu   sp, sp, -0x0030
    sw      a1, 0x0034(sp)

; 32x32 item icons.  Replaces the language-array offset load and the following
; register writes up to the vanilla DMA setup.
.org MESSAGE_LOAD_ITEM_ICON_32_OFFSET_BLOCK_VRAM
.area (MESSAGE_LOAD_ITEM_ICON_32_AFTER_OFFSET_BLOCK_VRAM - MESSAGE_LOAD_ITEM_ICON_32_OFFSET_BLOCK_VRAM), 0
    jal     Message_GetItemIcon32XOffsetRuntime
    nop

    ; Reload values that may have been clobbered by the C helper.
    lui     t1, 0x8012
    addiu   t1, t1, 0xBA00        ; gRegEditor pointer holder = 0x8011BA00
    lw      v1, 0x0000(t1)
    lh      t6, 0x0B00(v1)        ; R_TEXT_INIT_XPOS
    or      t9, v0, r0            ; selected icon X offset

    subu    t2, t6, t9
    sh      t2, 0x0522(v1)        ; R_TEXTBOX_ICON_XPOS
    lh      t3, 0x003A(sp)        ; y argument low half
    addiu   t4, t3, 0x0006        ; y + ((44 - 32) / 2)
    sh      t4, 0x0524(v1)        ; R_TEXTBOX_ICON_YPOS
    ori     t7, r0, 0x0020
    sh      t7, 0x052A(v1)        ; R_TEXTBOX_ICON_DIMENSION

    ; Set up the registers expected by the original DMA block at 0x800DA214.
    ori     at, r0, 0x8000
    lui     t9, 0x007C
    addiu   t9, t9, 0xD000        ; icon_item_static VROM base
    lhu     a3, 0x0036(sp)        ; itemId low half
    sll     t6, a3, 0x0C          ; itemId * ITEM_ICON_SIZE
    b       MESSAGE_LOAD_ITEM_ICON_32_AFTER_OFFSET_BLOCK_VRAM
    nop
.endarea

; 24x24 quest/reward icons.  Same idea as the 32x32 path, but resume before the
; vanilla quest-icon DMA setup.
.org MESSAGE_LOAD_ITEM_ICON_24_OFFSET_BLOCK_VRAM
.area (MESSAGE_LOAD_ITEM_ICON_24_AFTER_OFFSET_BLOCK_VRAM - MESSAGE_LOAD_ITEM_ICON_24_OFFSET_BLOCK_VRAM), 0
    jal     Message_GetItemIcon24XOffsetRuntime
    nop

    lui     t1, 0x8012
    addiu   t1, t1, 0xBA00        ; gRegEditor pointer holder = 0x8011BA00
    lw      v1, 0x0000(t1)
    lh      t2, 0x0B00(v1)        ; R_TEXT_INIT_XPOS
    or      t5, v0, r0            ; selected icon X offset

    subu    t7, t2, t5
    sh      t7, 0x0522(v1)        ; R_TEXTBOX_ICON_XPOS
    lh      t8, 0x003A(sp)
    addiu   t6, t8, 0x000A        ; y + ((44 - 24) / 2)
    sh      t6, 0x0524(v1)        ; R_TEXTBOX_ICON_YPOS
    ori     t3, r0, 0x0018
    sh      t3, 0x052A(v1)        ; R_TEXTBOX_ICON_DIMENSION

    ; Original quest-icon path computes itemId * 0x900 into t2 before adding the
    ; VROM base at 0x800DA2A0.
    lhu     a3, 0x0036(sp)
    sll     t2, a3, 0x03
    addu    t2, t2, a3
    sll     t2, t2, 0x08
    ori     at, r0, 0x8000
    b       MESSAGE_LOAD_ITEM_ICON_24_AFTER_OFFSET_BLOCK_VRAM
    nop
.endarea

;================================================================================
; Wide/Japanese newline metrics override
;================================================================================
; The normal newline path reads R_TEXT_LINE_SPACING and R_TEXT_INIT_XPOS directly.
; Hook it so wide_text_english_metrics also controls line distance even if a later
; game path restores the vanilla JP register values.

.definelabel MESSAGE_DRAW_TEXT_WIDE_NEWLINE_VRAM,       0x800D7CF8
.definelabel MESSAGE_DRAW_TEXT_WIDE_AFTER_NEWLINE_VRAM, 0x800D7D1C

.org MESSAGE_DRAW_TEXT_WIDE_NEWLINE_VRAM
.area (MESSAGE_DRAW_TEXT_WIDE_AFTER_NEWLINE_VRAM - MESSAGE_DRAW_TEXT_WIDE_NEWLINE_VRAM), 0
    jal     Message_ApplyWideTextNewline
    or      a0, s1, r0          ; s1 = &play->msgCtx in Message_DrawTextWide
    b       MESSAGE_DRAW_TEXT_WIDE_AFTER_NEWLINE_VRAM
    nop
.endarea


;================================================================================
; Wide/Japanese choice cursor placement override
;================================================================================
; The selection arrow does not get its base Y positions from the two calls to
; Message_HandleChoiceSelection alone.  The actual 2-choice/3-choice Y registers
; are initialized earlier in Message_Update with the decompiled logic:
;
;   R_TEXT_CHOICE_XPOS       = XREG(66) = 48
;   JP R_TEXT_CHOICE_YPOS          = XREG(67..69) = textboxY + 7 / +25 / +43
;   EN/non-JP R_TEXT_CHOICE_YPOS  = XREG(67..69) = textboxY + 20 / +32 / +44
;   JP wide English-metrics YPOS  = XREG(67..69) = textboxY + 7 / +19 / +31
;
; Hook the two selection-update calls through a wrapper that preserves vanilla
; input behavior and derives the cursor row from the same values used by
; Message_DrawTextWide: R_TEXT_INIT_YPOS, the number of newlines before the choice
; control, the selected row, and R_TEXT_LINE_SPACING. This avoids mixing textbox
; target coordinates with rendered text coordinates.
;
; The C-side gRegEditor accessor must use the US NTSC 1.0 pointer holder at
; 0x8011BA00 and then advance 0x14 bytes to RegEditor.data. Without that +0x14,
; XREG(67..69) are read as XREG(57..59), which places the arrow near screen top.
;
; Keep the JP initialization hook as a vanilla-compatible fallback for message
; forms where the decoded choice control cannot be found.

.definelabel MESSAGE_HANDLE_CHOICE_SELECTION_VRAM, 0x800D6290
.definelabel MESSAGE_HANDLE_CHOICE_SELECTION_2_CHOICE_CALL_VRAM, 0x800E02A8
.definelabel MESSAGE_HANDLE_CHOICE_SELECTION_3_CHOICE_CALL_VRAM, 0x800E02D4
.definelabel MESSAGE_CHOICE_YPOS_JP_BLOCK_VRAM, 0x800E0E60
.definelabel MESSAGE_CHOICE_YPOS_AFTER_BLOCK_VRAM, 0x800E0EC4

.org MESSAGE_HANDLE_CHOICE_SELECTION_2_CHOICE_CALL_VRAM
    jal     Message_HandleChoiceSelection_WideAware

.org MESSAGE_HANDLE_CHOICE_SELECTION_3_CHOICE_CALL_VRAM
    jal     Message_HandleChoiceSelection_WideAware

; Replace only the JP +7/+25/+43 initialization block.  t0 and t1 are live after
; this block, so preserve them across the C helper.
.org MESSAGE_CHOICE_YPOS_JP_BLOCK_VRAM
.area (MESSAGE_CHOICE_YPOS_AFTER_BLOCK_VRAM - MESSAGE_CHOICE_YPOS_JP_BLOCK_VRAM), 0
    addiu   sp, sp, -0x08
    sw      t0, 0x0000(sp)
    sw      t1, 0x0004(sp)
    jal     Message_ApplyWideTextChoiceCursorInitMetrics
    nop
    lw      t0, 0x0000(sp)
    lw      t1, 0x0004(sp)
    addiu   sp, sp, 0x08
    b       MESSAGE_CHOICE_YPOS_AFTER_BLOCK_VRAM
    nop
.endarea

;================================================================================
; Wide/Japanese message width override lookup
;================================================================================
; Replaces the post-draw width handling in Message_DrawTextWide. The vanilla code
; has several hard-coded JP punctuation advances, then a 16px default. For the
; language override system, the C helper first searches LANG_WIDE_CHAR_WIDTH_*
; and returns default 16 when the character is not listed. This keeps ROM usage
; low and gives CHAR_WIDTHS precedence over every wide character.
;
; Offsets from z_message_z_game_over.o:
;   Message_DrawTextWide = .text + 0x1C10
;   default glyph draw setup starts at .text + 0x2E30
;   post Message_DrawTextChar width handling starts at .text + 0x2E50
;   next loop continuation starts at .text + 0x2F84
;
; v3 only changed metrics in Message_OpenText. Some message paths can still render
; with stale JP scale/spacing, so v4 also reapplies metrics immediately before
; every wide glyph is drawn. This guarantees Message_DrawTextChar sees the
; English-like R_TEXT_CHAR_SCALE value and later newline handling sees the
; English-like R_TEXT_LINE_SPACING value.

.definelabel MESSAGE_DRAW_TEXT_WIDE_BEFORE_DRAW_VRAM, 0x800D8D20
.definelabel MESSAGE_DRAW_TEXT_WIDE_AFTER_WIDTH_VRAM,  0x800D8E74
.definelabel MESSAGE_DRAW_TEXT_CHAR_VRAM,              0x800D6470

.org MESSAGE_DRAW_TEXT_WIDE_BEFORE_DRAW_VRAM
.area (MESSAGE_DRAW_TEXT_WIDE_AFTER_WIDTH_VRAM - MESSAGE_DRAW_TEXT_WIDE_BEFORE_DRAW_VRAM), 0
    ; Ensure R_TEXT_CHAR_SCALE / R_TEXT_LINE_SPACING / R_TEXT_INIT_XPOS are current
    ; before Message_DrawTextChar computes sCharTexSize and sCharTexScale.
    ; The current wide character is in t0/t8 depending on the path; preserve the
    ; canonical t0 value on the stack before calling C helpers.
    or      t0, t0, r0          ; current wide character was reloaded into t0 by prior paths
    sw      t0, 0x0050(sp)
    jal     Message_ApplyJpTextDrawMetrics
    nop

    ; Displaced vanilla setup for Message_DrawTextChar.
    ; Message_DrawTextChar is a vanilla z_message function and is not visible as a
    ; symbol in this armips pass, so call its local VRAM address explicitly.
    ;   t9 = font->charTexBuf base saved at 0x58(sp)
    ;   charTexIdx = 0x128(sp)
    ;   a0 = play, a1 = texture pointer, a2 = &gfx
    lw      t0, 0x0050(sp)       ; restore current wide character after helper call
    lw      t9, 0x0058(sp)
    lhu     t8, 0x0128(sp)
    lw      a0, 0x0138(sp)
    addiu   a2, sp, 0x0124
    addu    a1, t9, t8
    jal     MESSAGE_DRAW_TEXT_CHAR_VRAM
    addiu   a1, a1, 0x0008

    lw      t0, 0x0050(sp)       ; Message_DrawTextChar clobbers t-registers

    ; displaced: charTexIdx += FONT_CHAR_TEX_SIZE
    lhu     t7, 0x0128(sp)
    addiu   t7, t7, 0x0080
    sh      t7, 0x0128(sp)

    ; a0 = current wide character, a1 = R_TEXT_CHAR_SCALE
    lw      t6, 0x0000(s7)       ; gRegEditor pointer, as used by vanilla Message_DrawTextWide
    or      a0, r0, t0
    jal     Message_GetWideCharScaledAdvance
    lh      a1, 0x0B06(t6)

    ; msgCtx->textPosX += scaled advance
    lh      t6, 0x63D8(s0)
    addiu   at, s1, 0x7FFF
    addu    t7, t6, v0
    sh      t7, 0x63D9(at)

    ; Message_DrawTextChar and helper calls clobber t-register constants used by
    ; the next loop iteration.
    ori     t1, r0, 0x819F
    ori     t2, r0, 0x81A3
    ori     t3, r0, 0x81A4
    ori     t4, r0, 0x81A5
    ori     t5, r0, 0x8170

    b       MESSAGE_DRAW_TEXT_WIDE_AFTER_WIDTH_VRAM
    nop
.endarea
