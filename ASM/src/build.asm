.n64
.relativeinclude on

.create "../roms/patched.z64", 0
.incbin "../roms/base.z64"

;==================================================================================================
; Base game editing region
;==================================================================================================

.include "hacks.asm"
.include "malon.asm"

;==================================================================================================
; New code region
;==================================================================================================

.headersize (0x80400000 - 0x03480000)

.include "constants.asm"

.org 0x80401000
.area 0x1000, 0
.include "config.asm"
.endarea

.org 0x80402000
.area 0x50, 0
.include "state.asm"
.endarea

.org 0x80402050
.area 0x2000, 0
.include "extended_items.asm"
.include "item_overrides.asm"
.include "cutscenes.asm"
.include "every_frame.asm"
.include "menu.asm"
.include "time_travel.asm"
.include "song_fix.asm"
.include "initial_save.asm"
.endarea

.close
