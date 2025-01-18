.n64
.relativeinclude on

; version guard, prevent people from building with older armips versions
.if (version() < 110)
.notice version()
.error   "Detected armips build is too old. Please install https://github.com/Kingcom/armips version 0.11 or later."
.endif

.create "../roms/patched.z64", 0
.incbin "../roms/base.z64"

.include "macros.asm"
.include "constants.asm"
.include "addresses.asm"

;==================================================================================================
; Base game editing region
;==================================================================================================

.include "base/boot.asm"
.include "base/hacks.asm"

; Code Segment
.include "base/code/z_en_item00.asm"
.include "base/code/z_parameter.asm"

; Virtual Memory Start
.include "base/overlays/gamestates/ovl_title.asm"
.include "base/overlays/gamestates/ovl_file_choose.asm"

.include "base/overlays/actors/ovl_Bg_Gate_Shutter.asm"
.include "base/overlays/actors/ovl_Bg_Haka_Tubo.asm"
.include "base/overlays/actors/ovl_Bg_Spot18_Basket.asm"
.include "base/overlays/actors/ovl_En_Dns.asm"
.include "base/overlays/actors/ovl_En_Kz.asm"
.include "base/overlays/actors/ovl_obj_Mure3.asm"
.include "base/overlays/actors/ovl_En_Ma1.asm"
.include "base/overlays/actors/ovl_En_Md.asm"
.include "base/overlays/actors/ovl_En_Weather_Tag.asm"

;==================================================================================================
; Payload code region
;==================================================================================================

.headersize (0x80400000 - 0x03480000)

.org    0x80400000
.area   0x00200000 ; payload max memory
PAYLOAD_START:

.area 0x20, 0
RANDO_CONTEXT:
.word COOP_CONTEXT
.word COSMETIC_CONTEXT
.word extern_ctxt
.word AUTO_TRACKER_CONTEXT
.endarea

.include "payload/coop_state.asm" ; This should always come first
.include "payload/config.asm"
.include "payload/init.asm"
.include "payload/mods/item_overrides.asm"
.include "payload/mods/cutscenes.asm"
.include "payload/mods/shop.asm"
.include "payload/every_frame.asm"
.include "payload/mods/menu.asm"
.include "payload/mods/time_travel.asm"
.include "payload/mods/song_fix.asm"
.include "payload/mods/scarecrow.asm"
.include "payload/mods/empty_bomb.asm"
.include "payload/mods/initial_save.asm"
.include "payload/mods/fishing.asm"
.include "payload/mods/bgs_fix.asm"
.include "payload/mods/chus_in_logic.asm"
.include "payload/mods/rainbow_bridge.asm"
.include "payload/mods/lacs_condition.asm"
.include "payload/mods/gossip_hints.asm"
.include "payload/mods/potion_shop.asm"
.include "payload/mods/jabu_elevator.asm"
.include "payload/mods/dampe.asm"
.include "payload/mods/dpad.asm"
.include "payload/mods/chests.asm"
.include "payload/mods/red_ice.asm"
.include "payload/mods/bunny_hood.asm"
.include "payload/mods/colors.asm"
.include "payload/mods/debug.asm"
.include "payload/mods/extended_objects.asm"
.include "payload/mods/cow.asm"
.include "payload/mods/lake_hylia.asm"
.include "payload/mods/timers.asm"
.include "payload/mods/shooting_gallery.asm"
.include "payload/mods/damage.asm"
.include "payload/mods/bonk.asm"
.include "payload/mods/bean_salesman.asm"
.include "payload/mods/grotto.asm"
.include "payload/mods/deku_mouth_condition.asm"
.include "payload/mods/audio.asm"
.include "payload/mods/king_zora.asm"
.include "payload/mods/carpenter_boss.asm"
.include "payload/mods/twinrova_wait.asm"
.include "payload/mods/boomerang.asm"
.include "payload/mods/file_select.asm"
.include "payload/mods/zelda.asm"
.include "payload/mods/link_anim.asm"
.include "payload/mods/malon_hooks.asm"
.include "payload/mods/bigocto.asm"
.include "payload/mods/agony.asm"
.include "payload/mods/horseback_archery.asm"
.include "payload/mods/items_as_adult.asm"
.include "payload/mods/carpet_salesman.asm"
.include "payload/mods/medigoron.asm"
.include "payload/mods/misc_colors.asm"
.include "payload/mods/door_of_time_col_fix.asm"
.include "payload/mods/mask_deequip.asm"
.include "payload/mods/trade_quests.asm"
.include "payload/mods/blue_fire_arrows.asm"
.include "payload/mods/gerudo_guard.asm"
.include "payload/mods/save.asm"
.include "payload/drop_overrides/obj_mure3.asm"
.include "payload/drop_overrides/bg_haka_tubo.asm"
.include "payload/drop_overrides/bg_spot18_basket.asm"
.include "payload/drop_overrides/obj_comb.asm"
.include "payload/drop_overrides/en_wonderitem.asm"
.include "payload/mods/actor.asm"
.include "payload/mods/rand_seed.asm"
.include "payload/mods/messages.asm"
.include "payload/mods/player_save_mask.asm"
.include "payload/mods/gohma.asm"
.include "payload/mods/camera_init.asm"
.include "payload/mods/chest_game.asm"
.include "payload/mods/en_item00.asm"
.include "payload/mods/volvagia.asm"
.include "payload/mods/key_counter.asm"
.include "payload/mods/armos.asm"
.include "payload/mods/ocarina_buttons.asm"
.include "payload/mods/fairy_ocarina.asm"
.include "payload/mods/en_dns.asm"
.include "payload/mods/bg_gate_shutter.asm"

.align 0x10
.importobj "../build/bundle.o"

.align 0x10

; This address bump avoids an audio issue where random crackling or buzzing noises play at possibly
; very high volume during the entire game, even on the N64 logo screen. If this issue reappears,
; double this number.
;
; For possible proper fixes, see:
; https://discord.com/channels/274180765816848384/512048482677424138/1251961594380947587
.skip 0x200

AUDIO_THREAD_MEM_START:
.skip AUDIO_THREAD_MEM_SIZE
PAYLOAD_END:
.endarea ; payload max memory

.close
