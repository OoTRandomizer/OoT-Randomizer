.n64
.relativeinclude on

.create "../roms/patched.z64", 0
.incbin "../roms/base.z64"

;==================================================================================================
; Constants
;==================================================================================================

.include "constants.asm"
.include "addresses.asm"

;==================================================================================================
; Base game editing region
;==================================================================================================

.include "boot.asm"
.include "hacks.asm"
.include "malon.asm"

;==================================================================================================
; New code region
;==================================================================================================

;Working Navi accept86
.org WORKING_NAVI_DATA_GENERATED_TEXT_INCREMENT_SYM  ; see addresses.asm, this is only done so we get a symbol


.org WORKING_NAVI_DATA_GENERATED_TEXT_SYM  ; see addresses.asm, this is only done so we get a symbol in symbols_RAM.json



.headersize (0x80400000 - 0x03480000)

.org 0x80400000
.area 0x10000

.area 0x20, 0
RANDO_CONTEXT:
.word COOP_CONTEXT
.word COSMETIC_CONTEXT
.word extern_ctxt
.endarea

.include "coop_state.asm" ; This should always come first
.include "config.asm"
.include "init.asm"
.include "item_overrides.asm"
.include "cutscenes.asm"
.include "shop.asm"
.include "every_frame.asm"
.include "menu.asm"
.include "time_travel.asm"
.include "song_fix.asm"
.include "scarecrow.asm"
.include "empty_bomb_fix.asm"
.include "initial_save.asm"
.include "textbox.asm"
.include "fishing.asm"
.include "bgs_fix.asm"
.include "chus_in_logic.asm"
.include "rainbow_bridge.asm"
.include "gossip_hints.asm"
.include "potion_shop.asm"
.include "jabu_elevator.asm"
.include "dampe.asm"
.include "dpad.asm"
.include "chests.asm"
.include "bunny_hood.asm"
.include "magic_color.asm"
.include "debug.asm"
.include "cow.asm"
.include "lake_hylia.asm"
.include "timers.asm"
.include "shooting_gallery.asm"
.include "saria_hints_repeat.asm"  ;accept86
.include "textload.asm"     ;accept86
.include "working_navi.asm" ;accept86
.importobj "../build/bundle.o"
.align 8
FONT_TEXTURE:
.incbin("../resources/font.bin")
DPAD_TEXTURE:
.incbin("../resources/dpad.bin")

.endarea

.close

