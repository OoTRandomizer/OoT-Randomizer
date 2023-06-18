@fanfare_audioseq_size equ 0x1000
@fanfare_audiobank_size equ 0x4800
@fanfare_unk_size equ 0
@bgm_audioseq_size equ 0x7000
@bgm_audiobank_size equ 0x4800
@bgm_unk_size equ 0

AUDIO_THREAD_MEM_SIZE equ \
(0x37F00 - 0x6670 + @fanfare_audioseq_size + @fanfare_audiobank_size + @bgm_audioseq_size + @bgm_audiobank_size)



AUDIO_THREAD_INFO:
.word \
@fanfare_audioseq_size,     \
@fanfare_audiobank_size,    \
@fanfare_unk_size,          \
@bgm_audioseq_size,         \
@bgm_audiobank_size,        \
@bgm_unk_size

.align 0x8 //force hi() to always be the same for both vars
AUDIO_THREAD_INFO_MEM_START:
.word AUDIO_THREAD_MEM_START
AUDIO_THREAD_INFO_MEM_SIZE:
.word AUDIO_THREAD_MEM_SIZE

.align 0x10
AUDIOBANK_TABLE_EXTENDED:
.area 0x800, 0
.endarea

FONTLOADSTATUS_EXTENDED:
.area 0x80, 0
.endarea

.align 0x10
; Hack for when AudioLoad_SyncLoadFont checks fontLoadStatus
; Put the address to load into T6
AudioLoad_SyncLoadFont_StatusHack:
    addiu   a1, a1, 0x5630 ; Replaced code
    li      t6, FONTLOADSTATUS_EXTENDED
    jr      ra
    addu    t6, t6, v0


//used to calculate the remaining free size of the audio thread heap
get_audio_pointers:
    li      t9, @fanfare_audioseq_size
    li      t2, @fanfare_audiobank_size
    li      t5, @fanfare_unk_size
    li      t4, @bgm_audioseq_size
    li      t6, @bgm_audiobank_size
    jr      ra
    li      t8, @bgm_unk_size
