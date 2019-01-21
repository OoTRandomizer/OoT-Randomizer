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

.headersize (0x80400000 - 0x03480000)

.org 0x80400000
.area 0x10000
.area 0x1000
.include "coop_state.asm" ; This should always come first
.endarea
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
.include "debug.asm"
.importobj "../build/bundle.o"
.align 8
FONT_TEXTURE:
.incbin("../resources/font.bin")
DPAD_TEXTURE:
.incbin("../resources/dpad.bin")
.endarea

.close
