;==================================================================================================
; Settings and tables which the front-end may write
;==================================================================================================

; This is used to determine if and how the cosmetics can be patched
; It this moves then the version will no longer be valid, so it is important that this does not move
COSMETIC_CONTEXT:

COSMETIC_FORMAT_VERSION:
.word 0x1F073FE0
CFG_MAGIC_COLOR:
.halfword 0x0000, 0x00C8, 0x0000
CFG_HEART_COLOR:
.halfword 0x00FF, 0x0046, 0x0032
CFG_A_BUTTON_COLOR:
.halfword 0x005A, 0x005A, 0x00FF
CFG_B_BUTTON_COLOR:
.halfword 0x0000, 0x0096, 0x0000
CFG_C_BUTTON_COLOR:
.halfword 0x00FF, 0x00A0, 0x0000
CFG_TEXT_CURSOR_COLOR:
.halfword 0x0000, 0x0050, 0x00C8
CFG_SHOP_CURSOR_COLOR:
.halfword 0x0000, 0x0050, 0x00FF
CFG_A_NOTE_COLOR:
.halfword 0x0050, 0x0096, 0x00FF
CFG_C_NOTE_COLOR:
.halfword 0x00FF, 0x00FF, 0x0032
CFG_BOOM_TRAIL_INNER_COLOR:
.byte 0xFF, 0xFF, 0x64
CFG_BOOM_TRAIL_OUTER_COLOR:
.byte 0xFF, 0xFF, 0x64
CFG_BOMBCHU_TRAIL_INNER_COLOR:
.byte 0xFA, 0x00, 0x00
CFG_BOMBCHU_TRAIL_OUTER_COLOR:
.byte 0xFA, 0x00, 0x00
CFG_DISPLAY_DPAD:
.byte 0x01
CFG_RAINBOW_SWORD_INNER_ENABLED:
.byte 0x00
CFG_RAINBOW_SWORD_OUTER_ENABLED:
.byte 0x00
CFG_RAINBOW_BOOM_TRAIL_INNER_ENABLED:
.byte 0x00
CFG_RAINBOW_BOOM_TRAIL_OUTER_ENABLED:
.byte 0x00
CFG_RAINBOW_BOMBCHU_TRAIL_INNER_ENABLED:
.byte 0x00
CFG_RAINBOW_BOMBCHU_TRAIL_OUTER_ENABLED:
.byte 0x00
CFG_RAINBOW_NAVI_IDLE_INNER_ENABLED:
.byte 0x00
CFG_RAINBOW_NAVI_IDLE_OUTER_ENABLED:
.byte 0x00
CFG_RAINBOW_NAVI_ENEMY_INNER_ENABLED:
.byte 0x00
CFG_RAINBOW_NAVI_ENEMY_OUTER_ENABLED:
.byte 0x00
CFG_RAINBOW_NAVI_NPC_INNER_ENABLED:
.byte 0x00
CFG_RAINBOW_NAVI_NPC_OUTER_ENABLED:
.byte 0x00
CFG_RAINBOW_NAVI_PROP_INNER_ENABLED:
.byte 0x00
CFG_RAINBOW_NAVI_PROP_OUTER_ENABLED:
.byte 0x00
CFG_DPAD_DUNGEON_INFO_ENABLE:
.byte 0x01
GET_ITEM_SEQ_ID:
.halfword 0x0000
CFG_SPEEDUP_MUSIC_FOR_LAST_TRIFORCE_PIECE:
.byte 0x00
CFG_SLOWDOWN_MUSIC_WHEN_LOWHP:
.byte 0x00
CFG_RAINBOW_TUNIC_ENABLED:
.byte 0x00
CFG_TUNIC_COLORS:
.byte 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00

CFG_AUDIOBANK_TABLE_EXTENDED_ADDR:
.word AUDIOBANK_TABLE_EXTENDED

CFG_CORRECT_MODEL_COLORS:
.byte 0x00
CFG_UNINVERT_YAXIS_IN_FIRST_PERSON_CAMERA:
.byte 0x00
CFG_DPAD_ON_THE_LEFT:
.byte 0x00

CFG_SHOW_SETTING_INFO:
.byte 0x00

.area 0x20, 0
CFG_CUSTOM_MESSAGE_1:
.endarea
.area 0x20, 0
CFG_CUSTOM_MESSAGE_2:
.endarea

.align 4

; Version string
.area 0x24, 0
VERSION_STRING_TXT:
.endarea

; World string (max length "255 of 255" = 10 chars)
.area 0x10, 0
WORLD_STRING_TXT:
.endarea

; Time string
.area 0x24, 0
TIME_STRING_TXT:
.endarea

; Initial Save Data table:
;
; This table describes what extra data should be written when a new save file is created. It must be terminated with
; four 0x00 bytes (which will happen by default as long as you don't fill the allotted space).
;
; Row format (4 bytes):
; AAAATTVV
; AAAA = Offset from the start of the save data
; TT = Type (0x00 = or value with current value, 0x01 = set the byte to the given value)
; VV = Value to write to the save

.area 0x400, 0
INITIAL_SAVE_DATA:
.endarea

.area 0x100, 0
EXTENDED_INITIAL_SAVE_DATA:
.endarea

.area 0xC0, 0 ; size must be at least 8 * ((max object_id parameter Patches.add_to_extended_object_table is called with) - 0x192)
EXTENDED_OBJECT_TABLE:
.endarea

FREE_BOMBCHU_DROPS:
.word 0x00

GOSSIP_HINT_CONDITION:
.word 0x00
; 0 = Mask of Truth
; 1 = Stone of Agony
; 2 = No Requirements

FREE_SCARECROW_ENABLED:
.word 0x00

JABU_ELEVATOR_ENABLE:
.byte 0x00
OCARINAS_SHUFFLED:
.byte 0x00
NO_COLLECTIBLE_HEARTS:
.byte 0x00
FAST_CHESTS:
.byte 0x01
SHUFFLE_COWS:
.byte 0x00
SONGS_AS_ITEMS:
.byte 0x00
WINDMILL_SONG_ID:
.byte 0x00
WINDMILL_TEXT_ID:
.byte 0x00
MALON_TEXT_ID:
.byte 0x00
DISABLE_TIMERS:
.byte 0x00
DUNGEONS_SHUFFLED:
.byte 0x00
OVERWORLD_SHUFFLED:
.byte 0x00
HIDEOUT_SHUFFLED:
.byte 0x00
FAST_BUNNY_HOOD_ENABLED:
.byte 0x00
FIX_BROKEN_DROPS:
.byte 0x00
SPOILER_AVAILABLE:
.byte 0x00
PLANDOMIZER_USED:
.byte 0x00
POTCRATE_TEXTURES_MATCH_CONTENTS:
.byte 0x00
KEYRING_BOSSKEY_CONDITION:
.byte 0x00
SHUFFLE_SILVER_RUPEES:
.byte 0x00
CFG_DUNGEON_INFO_SILVER_RUPEES:
.byte 0x00
CUSTOM_KEY_MODELS:
.byte 0x00
SHUFFLE_OCARINA_BUTTONS:
.byte 0x00
EPONAS_SONG_NOTES:
.byte 0x00
.align 4

; These configuration values are given fixed addresses to aid auto-trackers.
; Any changes made here should be documented in Notes/auto-tracker-ctx.md
AUTO_TRACKER_CONTEXT:
AUTO_TRACKER_VERSION:
.word 4 ; Increment this if the auto-tracker context layout changes

CFG_DUNGEON_INFO_ENABLE:
.word 0
CFG_DUNGEON_INFO_MQ_ENABLE:
.word 0
CFG_DUNGEON_INFO_MQ_NEED_MAP:
.word 0
CFG_DUNGEON_INFO_REWARD_ENABLE:
.word 0
CFG_DUNGEON_INFO_REWARD_NEED_COMPASS:
.word 0
CFG_DUNGEON_INFO_REWARD_NEED_ALTAR:
.word 0
CFG_DUNGEON_INFO_REWARD_SUMMARY_ENABLE:
.word 1
.area 14, 0xff
CFG_DUNGEON_REWARDS:
.endarea
.area 14, 0x00
CFG_DUNGEON_IS_MQ:
.endarea

RAINBOW_BRIDGE_CONDITION:
.word 0x00
; 0 = Open
; 1 = Medallions
; 2 = Dungeons
; 3 = Stones
; 4 = Vanilla
; 5 = Tokens
; 6 = Hearts

LACS_CONDITION:
.word 0x00
; 0 = Vanilla
; 1 = Medallions
; 2 = Dungeons
; 3 = Stones
; 4 = Tokens
; 5 = Hearts

RAINBOW_BRIDGE_COUNT:
.halfword 0x0064

LACS_CONDITION_COUNT:
.halfword 0x0000

TRIFORCE_HUNT_ENABLED:
.halfword 0x0000

TRIFORCE_PIECES_REQUIRED:
.halfword 0xffff

.area 8, 0x00
SPECIAL_DEAL_COUNTS:
.endarea

.area 9 * 0x17, 0x20
CFG_DUNGEON_REWARD_AREAS:
.endarea

.align 4
