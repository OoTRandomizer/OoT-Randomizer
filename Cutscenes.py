from __future__ import annotations
from typing import Optional
from enum import IntEnum
from typing import TYPE_CHECKING, Literal, overload
from abc import ABC, abstractmethod

from Rom import Rom, Vec3s, Vec3i, float_to_bytes
from Settings import Settings
from SaveContext import SceneIDs
from SceneList import RecordType
from Item import ItemInfo

if TYPE_CHECKING:
    from Scene import Scenes
    from Location import Location

# The following helpers can be used when the cutscene is written in the form of CutsceneData instructions.
# This is the case for all cutscenes defined directly in their scenes, and some specific ones in their actor file.
# However some cutscenes like all the ones tied to bosses are done "manually" in their actor files in a completely different format.

def delete_cutscene(cutscene: Cutscene) -> None:
    # Instead of deleting the cutscene completely from the ROM,
    # set its frame count to a negative number to prematurely exit
    # in the game's cutscene parser in z_demo. This makes the written
    # ROM data look like CS_END, but it is not being interpreted as such.
    cutscene.frames = -1

def patch_cutscene_length(cutscene: Cutscene, new_length: int) -> None:
    cutscene.frames = new_length

# Some cutscenes sends Link in a different location at the end. The command that sets the destination also sets the length of these cutscenes.
def patch_cutscene_destination_and_length(cutscene: Cutscene, old_length: int, new_length: int, new_destination: Optional[int] = None) -> None:
    command = cutscene.find_command_by_start_frame(CutsceneCommandID.CS_CMD_DESTINATION, old_length)
    command.start_frame = new_length
    if new_destination:
        command.destination = new_destination

def patch_textbox_during_cutscene(cutscene: Cutscene, old_type: CutsceneCommandID, old_start_frame: int, textbox_id: int, new_start_frame: int, end_frame: int) -> None:
    CS_TEXT_NORMAL = 0     # CutsceneTextType, always 0 unless we want to make a choice textbox.
    CS_TEXT_NONE = 0xFFFF  # constant 0xFFFF
    if textbox_id == 0:
        text_command = CutsceneCommandText(textbox_id, new_start_frame, end_frame, CS_TEXT_NONE, 0xFFFF, 0xFFFF)
    else:
        text_command = CutsceneCommandText(textbox_id, new_start_frame, end_frame, CS_TEXT_NORMAL, 0xFFFF, 0xFFFF)
    cutscene.replace_command_at_start_frame(old_type, old_start_frame, text_command)

# This is mostly used to set flags during cutscenes.
def patch_cutscene_misc_command(cutscene: Cutscene, old_start_frame: int, start_frame: int, end_frame: int, new_misc_type: Optional[int] = None) -> None:
    command = cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_MISC, old_start_frame)
    if new_misc_type:
        command.type_id = new_misc_type
    command.start_frame = start_frame
    command.end_frame = end_frame

def patch_cutscenes(rom: Rom, scenes: Scenes, song_locations: dict[str, Location], songs_as_items: bool, settings: Settings) -> None:
    # Speed obtaining Fairy Ocarina
    lw_bridge_cutscene = scenes[SceneIDs.LOST_WOODS].headers[4].cutscene_data
    patch_cutscene_destination_and_length(lw_bridge_cutscene, 1130, 60)
    #patch_cutscene_destination_and_length(rom, 0x2151230, 60)
    # Make Link cross the whole bridge instead of stopping in the middle by moving the destination coordinate
    # of the second player cue in the cutscene.
    #rom.write_bytes(0x2150E20, [0xFF, 0xFF, 0xFA, 0x4C])
    lw_bridge_command = lw_bridge_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 20)
    lw_bridge_command.end_pos.x = -1460 # original -1282

    # Speed Zelda's Letter scene
    # Change the exit from the castle maze courtyard to Zelda's courtyard to the start of the cutscene where you get the letter.
    # Initial value 0x400 : ENTR_CASTLE_COURTYARD_ZELDA_0. New value 0x5F0 : ENTR_CASTLE_COURTYARD_ZELDA_1
    #rom.write_int16(0x290E08E, 0x05F0)
    scenes[SceneIDs.HYRULE_CASTLE_HEDGE_MAZE_DAY].headers[0].exit_list.exits[1] = 0x05F0 # original 0x0400
    # From here this cutscene is all done manually in the zl4 actor.
    # Jump a couple of states in the cutscene.
    # Original value : ZL4_CS_LEGEND (0x05), new value : ZL4_CS_PLAN (0x08).
    rom.write_byte(0xEFCBA7, 0x08)
    # In the "Plan" cutscene, jump all textbox states and go directly to when you get the letter.
    # Original value : 1, new value : 5.
    rom.write_byte(0xEFE7C7, 0x05)
    # Remove some tests to make sure Zelda doesn't wait for textboxes we just skipped.
    rom.write_int32(0xEFE938, 0x00000000)
    rom.write_int32(0xEFE948, 0x00000000)
    rom.write_int32(0xEFE950, 0x00000000)

    LEARN_SONG_TEXT_ID = 0x088B

    # Speed learning Zelda's Lullaby
    # Redirect to 0x73 : CS_DEST_HYRULE_FIELD_FROM_IMPA_ESCORT from originally 0x33 : CS_DEST_HYRULE_FIELD_FROM_ZELDAS_COURTYARD
    zl_cutscene = scenes[SceneIDs.HYRULE_CASTLE_COURTYARD].headers[5].cutscene_data
    if songs_as_items:
        #patch_cutscene_destination_and_length(rom, 0x2E8E914, 1, 0x73)
        patch_cutscene_destination_and_length(zl_cutscene, 875, 1, 0x73)
        #patch_textbox_during_cutscene(rom, 0x02E8E924, 0, 0, 16)
        patch_textbox_during_cutscene(zl_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, 0, 0, 16)
    else:
        #patch_cutscene_destination_and_length(rom, 0x2E8E914, 59, 0x73)
        patch_cutscene_destination_and_length(zl_cutscene, 875, 59, 0x73)
        location = song_locations['Song from Impa']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        # Display the Zelda's Lullaby learn Ocarina textbox at frame 0.
        # Replaces the first text command.
        #patch_learn_song_textbox_during_cutscene(rom, 0x02E8E924, 23, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        zl_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the textbox for learning the song between 17 and 32 frames.
        # Replaces the second text command.
        #patch_textbox_during_cutscene(rom, 0x2E8E930, text_id, 17, 32)
        patch_textbox_during_cutscene(zl_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 140, text_id, 17, 32)

    # Speed learning Epona's Song
    ep_cutscene = scenes[SceneIDs.LON_LON_RANCH].headers[5].cutscene_data
    if songs_as_items:
        #patch_cutscene_destination_and_length(rom, 0x029BEF68, 1)
        patch_cutscene_destination_and_length(ep_cutscene, 300, 1)
    else:
        #patch_cutscene_destination_and_length(rom, 0x029BEF68, 10)
        patch_cutscene_destination_and_length(ep_cutscene, 300, 10)
        location = song_locations['Song from Malon']
        text_id = location.item.special['text_id']
        # The cutscene actually happens after learning the song, so we don't need to change the learn song textbox.
        # Display the 0x00D2 textbox (You've learned Epona's Song!) at frame 0.
        #patch_textbox_during_cutscene(rom, 0x029BECB8, 0x00D6, 0, 9)
        patch_textbox_during_cutscene(ep_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, text_id, 0, 9)
        # Make sure no textbox shows at frame 10.
        #patch_textbox_during_cutscene(rom, 0x029BECC4, 0, 10, 11)
        patch_textbox_during_cutscene(ep_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 10, 0, 10, 11)

    # Speed up opening the royal tomb for both child and adult.
    #patch_cutscene_length(rom, 0x2025020, 1)
    #patch_cutscene_length(rom, 0x2023C80, 1)
    # Child cutscene is only referenced in z_en_okarina_tag.c, not in any scene header.
    # Adult cutscene is triggered from the same place, but it is also referenced in the 5th header.
    adult_tomb_cutscene = scenes[SceneIDs.GRAVEYARD].headers[4].cutscene_data
    child_tomb_cutscene = scenes[SceneIDs.GRAVEYARD].get_existing_record_by_vanilla_offset(0x5020, RecordType.CutsceneData)
    patch_cutscene_length(adult_tomb_cutscene, 1)
    patch_cutscene_length(child_tomb_cutscene, 1)
    # Change the first actor cue from type 1 to type 2.
    # This will make the grave explode on frame 0 instead of frame 392.
    #rom.write_byte(0x2025159, 0x02)
    #rom.write_byte(0x2023E19, 0x02)
    adult_tomb_cue = adult_tomb_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_3_10)
    child_tomb_cue = child_tomb_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_3_10)
    adult_tomb_cue.cue_id = 2
    child_tomb_cue.cue_id = 2

    # Speed learning Sun's Song
    suns_cutscene = scenes[SceneIDs.GRAVEYARD_ROYAL_FAMILY_TOMB].headers[4].cutscene_data
    if songs_as_items:
        #delete_cutscene(rom, 0x0332A4A0)
        delete_cutscene(suns_cutscene)
    else:
        location = song_locations['Song from Royal Familys Tomb']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        #patch_cutscene_length(rom, 0x0332A4A0, 60)
        patch_cutscene_length(suns_cutscene, 60)
        # Display the Sun's song learn Ocarina textbox at frame 0.
        #atch_learn_song_textbox_during_cutscene(rom, 0x332A870, 24, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        suns_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the 0x00D3 textbox (You've learned Sun's Song!) between 17 and 32 frames.
        #patch_textbox_during_cutscene(rom, 0x332A87C, 0x00D3, 17, 32)
        patch_textbox_during_cutscene(suns_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 30, text_id, 17, 32)

    # Speed Deku Seed Upgrade Scrub Cutscene
    rom.write_bytes(0xECA900, [0x24, 0x03, 0xC0, 0x00])  # scrub angle
    rom.write_bytes(0xECAE90, [0x27, 0x18, 0xFD, 0x04])  # skip straight to giving item
    rom.write_bytes(0xECB618, [0x25, 0x6B, 0x00, 0xD4])  # skip straight to digging back in
    rom.write_bytes(0xECAE70, [0x00, 0x00, 0x00, 0x00])  # never initialize cs camera
    rom.write_bytes(0xE5972C, [0x24, 0x08, 0x00, 0x01])  # timer set to 1 frame for giving item

    # Speed learning Saria's Song
    saria_cutscene = scenes[SceneIDs.SACRED_FOREST_MEADOW].headers[5].cutscene_data
    if songs_as_items:
        #delete_cutscene(rom, 0x020B1730)
        delete_cutscene(saria_cutscene)
    else:
        location = song_locations['Song from Saria']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        #patch_cutscene_length(rom, 0x020B1730, 60)
        patch_cutscene_length(saria_cutscene, 60)
        # Display the Saria's song learn Ocarina textbox at frame 0.
        #patch_learn_song_textbox_during_cutscene(rom, 0x20B1DB0, 21, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        saria_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the 0x00D1 textbox (You've learned Saria's Song!) between 17 and 32 frames.
        #patch_textbox_during_cutscene(rom, 0x20B1DBC, 0x00D1, 17, 32)
        patch_textbox_during_cutscene(saria_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 465, text_id, 17, 32)
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        #rom.write_int16s(0x020B19C8, [0x0011, 0x0000, 0x0010])  # action, start, end
        player_cue = saria_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 0)
        player_cue.cue_id = 17
        player_cue.start_frame = 0
        player_cue.end_frame = 16
        # Switch to player action 62 between frames 17 and 32.
        #rom.write_int16s(0x020B19F8, [0x003E, 0x0011, 0x0020])  # action, start, end
        player_cue = saria_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 40)
        player_cue.cue_id = 62
        player_cue.start_frame = 17
        player_cue.end_frame = 32
        # Adjust manually the Y coordinate of Link because action 62 is adult only probably?
        #rom.write_int16(0x020B1A0A, 0x01D4)
        #rom.write_int16(0x020B1A16, 0x01D4)
        player_cue.start_pos.y = 468 # original 480
        player_cue.end_pos.y = 468 # original 480

    # Play Sarias Song to Darunia
    darunia_cutscene = scenes[SceneIDs.GORON_CITY].get_existing_record_by_vanilla_offset(0x59E0, RecordType.CutsceneData)
    #delete_cutscene(rom, 0x22769E0)
    delete_cutscene(darunia_cutscene)

    # Speed up Death Mountain Trail Owl Flight
    dmt_owl_cutscene = scenes[SceneIDs.DEATH_MOUNTAIN_TRAIL].get_existing_record_by_vanilla_offset(0x1E6A0, RecordType.CutsceneData)
    #patch_cutscene_destination_and_length(rom, 0x223B6B0, 1)
    patch_cutscene_destination_and_length(dmt_owl_cutscene, 422, 1)

    # Jabu Jabu swallowing Link
    jabu_swallow_cutscene = Cutscene.decode(rom, 0xC9FC84)
    patch_cutscene_destination_and_length(jabu_swallow_cutscene, 345, 1)
    jabu_swallow_cutscene.write(rom)
    #patch_cutscene_destination_and_length(rom, 0xCA0784, 1)

    # Ruto pointing to the Zora Sapphire when you enter Big Octo's room.
    ruto_gives_reward_cutscene = Cutscene.decode(rom, 0xD03BA8)
    delete_cutscene(ruto_gives_reward_cutscene)
    ruto_gives_reward_cutscene.write(rom)
    #delete_cutscene(rom, 0xD03BA8)

    # Speed scene after Jabu Jabu's Belly
    # Cut Ruto talking to Link when entering the blue warp.
    rom.write_int32(0xCA3530, 0x00000000)

    # Speed up Lake Hylia Owl Flight
    lh_owl_cutscene = scenes[SceneIDs.LAKE_HYLIA].get_existing_record_by_vanilla_offset(0x1B0C0, RecordType.CutsceneData)
    #patch_cutscene_destination_and_length(rom, 0x20E60D0, 1)
    patch_cutscene_destination_and_length(lh_owl_cutscene, 350, 1)

    # Speed Zelda escaping from Hyrule Castle
    escape_cutscene = scenes[SceneIDs.HYRULE_FIELD].headers[5].cutscene_data
    #patch_cutscene_destination_and_length(rom, 0x1FC0CFC, 1)
    patch_cutscene_destination_and_length(escape_cutscene, 2259, 1)

    # Speed learning Song of Time
    sot_cutscene = scenes[SceneIDs.TEMPLE_OF_TIME].headers[11].cutscene_data
    if songs_as_items:
        #patch_cutscene_destination_and_length(rom, 0x0252FBA0, 1)
        patch_cutscene_destination_and_length(sot_cutscene, 853, 1)
    else:
        location = song_locations['Song from Ocarina of Time']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        #patch_cutscene_destination_and_length(rom, 0x0252FBA0, 59)
        patch_cutscene_destination_and_length(sot_cutscene, 853, 59)
        # Display the Song of Time learn Ocarina textbox at frame 0.
        #patch_learn_song_textbox_during_cutscene(rom, 0x0252FC88, 25, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        sot_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the 0x00D5 textbox (You've learned Song of Time!) between 17 and 32 frames.
        #patch_textbox_during_cutscene(rom, 0x0252FC94, 0x00D5, 17, 32)
        patch_textbox_during_cutscene(sot_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 50, text_id, 17, 32)

    # Hyrule Field small cutscene after learning Song of Time.
    oot_cutscene = scenes[SceneIDs.HYRULE_FIELD].headers[8].cutscene_data
    #delete_cutscene(rom, 0x01FC3B80)
    delete_cutscene(oot_cutscene)

    # Speed opening of Door of Time
    door_of_time_cutscene = Cutscene.decode(rom, 0xE0A170)
    patch_cutscene_length(door_of_time_cutscene, 2)
    # Set the "Opened Door of Time" flag at the first frame.
    patch_cutscene_misc_command(door_of_time_cutscene, 620, 1, 2)
    door_of_time_cutscene.write(rom)
    #patch_cutscene_length(rom, 0xE0A170, 2)
    #patch_cutscene_misc_command(rom, 0xE0A358, 1, 2)

    # Master Sword pedestal cutscene
    child_pull_sword_cutscene = Cutscene.decode(rom, 0xCB6B30)
    patch_cutscene_destination_and_length(child_pull_sword_cutscene, 230, 20)
    child_pull_sword_cutscene.write(rom)
    adult_place_sword_cutscene = Cutscene.decode(rom, 0xCB6FE0)
    patch_cutscene_destination_and_length(adult_place_sword_cutscene, 210, 20)
    adult_place_sword_cutscene.write(rom)
    #patch_cutscene_destination_and_length(rom, 0xCB6BE8, 20) # Child => Adult
    #patch_cutscene_destination_and_length(rom, 0xCB75B8, 20) # Adult => Child

    # Speed learning Song of Storms
    # The cutscene actually happens after learning the song, so we don't need to change the Ocarina texboxes.
    # But the flag for the check is set at frame 10 during the cutscene, so cut it short here, and just show the "You"ve learned.." textbox before.
    sos_cutscene = scenes[SceneIDs.WINDMILL_AND_DAMPES_GRAVE].get_existing_record_by_vanilla_offset(0xE080, RecordType.CutsceneData)
    if songs_as_items:
        #delete_cutscene(rom, 0x03041080)
        delete_cutscene(sos_cutscene)
    else:
        location = song_locations['Song from Windmill']
        text_id = location.item.special['text_id']
        #patch_cutscene_length(rom, 0x03041080, 10)
        patch_cutscene_length(sos_cutscene, 10)
        # Display the 0x00D6 textbox (You've learned Song of Storms!) at frame 0.
        #patch_textbox_during_cutscene(rom, 0x03041090, 0x00D6, 0, 9)
        patch_textbox_during_cutscene(sos_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, text_id, 0, 9)

    # Speed up Epona race start
    llr_race_cutscene = scenes[SceneIDs.LON_LON_RANCH].headers[4].cutscene_data
    #patch_cutscene_length(rom, 0x29BE980, 2)
    patch_cutscene_length(llr_race_cutscene, 2)
    # Make the race music start on frame 1.
    #rom.write_byte(0x29BE9CB, 0x01)
    llr_seq_commmand = llr_race_cutscene.find_command(CutsceneCommandID.CS_SUBCMD_START_SEQ)
    llr_seq_commmand.start_frame = 1 # original 30

    # Speed up Epona escape
    # We have to wait until Epona is on a not awkward spot.
    #patch_cutscene_length(rom, 0x1FC79E0, 84) # South
    #patch_cutscene_length(rom, 0x1FC7F00, 84) # East
    #patch_cutscene_length(rom, 0x1FC8550, 84) # West
    #patch_cutscene_length(rom, 0x1FC8B30, 42) # Front gates
    south_epona_cutscene = scenes[SceneIDs.HYRULE_FIELD].get_existing_record_by_vanilla_offset(0xF9E0, RecordType.CutsceneData)
    east_epona_cutscene = scenes[SceneIDs.HYRULE_FIELD].get_existing_record_by_vanilla_offset(0xFF00, RecordType.CutsceneData)
    west_epona_cutscene = scenes[SceneIDs.HYRULE_FIELD].get_existing_record_by_vanilla_offset(0x10550, RecordType.CutsceneData)
    gate_epona_cutscene = scenes[SceneIDs.HYRULE_FIELD].get_existing_record_by_vanilla_offset(0x10B30, RecordType.CutsceneData)
    patch_cutscene_length(south_epona_cutscene, 84)
    patch_cutscene_length(east_epona_cutscene, 84)
    patch_cutscene_length(west_epona_cutscene, 84)
    patch_cutscene_length(gate_epona_cutscene, 42)

    # Speed learning Minuet of Forest
    minuet_cutscene = scenes[SceneIDs.SACRED_FOREST_MEADOW].headers[4].cutscene_data
    if songs_as_items:
        #delete_cutscene(rom, 0x020AFF80)
        delete_cutscene(minuet_cutscene)
    else:
        location = song_locations['Sheik in Forest']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        #patch_cutscene_length(rom, 0x020AFF80, 60)
        patch_cutscene_length(minuet_cutscene, 60)
        # Display the Minuet learn Ocarina textbox at frame 0.
        #patch_learn_song_textbox_during_cutscene(rom, 0x020B0808, 5, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        minuet_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the 0x0073 textbox (You have learned the Minuet of Forest!) between 17 and 32 frames.
        #patch_textbox_during_cutscene(rom, 0x020B0814, 0x0073, 17, 32)
        patch_textbox_during_cutscene(minuet_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 500, text_id, 17, 32)
        # Restart Lost woods music on frame 33.
        #rom.write_int16s(0x020B0492, [0x0021, 0x0022])
        minuet_seq_command = minuet_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_START_SEQ, 1580)
        minuet_seq_command.start_frame = 33 # original 1580
        minuet_seq_command.end_frame = 34 # original 1581
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        #rom.write_int16s(0x020AFF90, [0x0011, 0x0000, 0x0010])  # action, start, end
        player_cue = minuet_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 0)
        player_cue.cue_id = 17     # original 5
        player_cue.start_frame = 0 # no change
        player_cue.end_frame = 16  # original 20
        # Switch to player action 62 between frames 17 and 32.
        #rom.write_int16s(0x020AFFC0, [0x003E, 0x0011, 0x0020])  # action, start, end
        player_cue = minuet_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 20)
        player_cue.cue_id = 62
        player_cue.start_frame = 17
        player_cue.end_frame = 32

    # Speed Phantom Ganon defeat scene
    # Removes the check for timers to switch between the different parts of the cutscene.
    # First part is 150 frames.
    rom.write_int32(0xC944D8, 0x00000000)
    # Second part is 350 frames.
    rom.write_int32(0xC94548, 0x00000000)
    # Third part is 50 frames.
    rom.write_int32(0xC94730, 0x00000000)
    # Fourth part is 40 frames.
    rom.write_int32(0xC945A8, 0x00000000)
    # Last part is 250 frames.
    rom.write_int32(0xC94594, 0x00000000)

    # Speed scene after Forest Temple
    # Blue warp brings us to right before Deku Sprout cutscene number 3.
    #delete_cutscene(rom, 0x207B9D0)
    deku_sprout_cutscene = scenes[SceneIDs.KOKIRI_FOREST].headers[13].cutscene_data
    delete_cutscene(deku_sprout_cutscene)

    # Speed learning Prelude of Light
    prelude_cutscene = scenes[SceneIDs.TEMPLE_OF_TIME].headers[6].cutscene_data
    if songs_as_items:
        #delete_cutscene(rom, 0x0252FD20)
        delete_cutscene(prelude_cutscene)
    else:
        location = song_locations['Sheik at Temple']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        #patch_cutscene_length(rom, 0x0252FD20, 74)
        patch_cutscene_length(prelude_cutscene, 74)
        # Display the Minuet learn Ocarina textbox at frame 0.
        #patch_learn_song_textbox_during_cutscene(rom, 0x02531328, 20, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        prelude_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the 0x0078 textbox (You have learned the Prelude of Light!) between 17 and 32 frames.
        #patch_textbox_during_cutscene(rom, 0x02531334, 0x0078, 17, 32)
        patch_textbox_during_cutscene(prelude_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 125, text_id, 17, 32)
        # Make the first action on Sheik's action list end immediately.
        #rom.write_int16(0x0252FF1C, 0x0000)
        sheik_prelude_command = prelude_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_4_3)
        sheik_prelude_command.end_frame = 0 # original 100
        # Restart Temple of Time music on frame 33.
        #rom.write_int16s(0x025313DA, [0x0021, 0x0022])
        prelude_seq_command = prelude_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_START_SEQ, 1275)
        prelude_seq_command.start_frame = 33 # original 1275
        prelude_seq_command.end_frame = 34 # original 1276

    # Speed learning Bolero of Fire
    bolero_cutscene = scenes[SceneIDs.DEATH_MOUNTAIN_CRATER].headers[4].cutscene_data
    if songs_as_items:
        #delete_cutscene(rom, 0x0224B5D0)
        delete_cutscene(bolero_cutscene)
    else:
        location = song_locations['Sheik in Crater']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        #patch_cutscene_length(rom, 0x0224B5D0, 60)
        patch_cutscene_length(bolero_cutscene, 60)
        # Display the Bolero learn Ocarina textbox at frame 0.
        #patch_learn_song_textbox_during_cutscene(rom, 0x0224D7F0, 16, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        bolero_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the 0x0073 textbox (You have learned the Bolero of Fire!) between 17 and 32 frames.
        #patch_textbox_during_cutscene(rom, 0x0224D7FC, 0x0073, 17, 32)
        patch_textbox_during_cutscene(bolero_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 120, text_id, 17, 32)
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        #rom.write_int16s(0x0224B5E0, [0x0011, 0x0000, 0x0010])  # action, start, end
        player_cue = bolero_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 0)
        player_cue.cue_id = 17     # original 5
        player_cue.start_frame = 0 # no change
        player_cue.end_frame = 16  # original 39
        # Switch to player action 62 between frames 17 and 32.
        #rom.write_int16s(0x0224B610, [0x003E, 0x0011, 0x0020])  # action, start, end
        player_cue = bolero_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 39)
        player_cue.cue_id = 62      # original 3
        player_cue.start_frame = 17 # original 39
        player_cue.end_frame = 32   # original 63
        # Put the first three actions on Sheik's action list to id 0.
        #rom.write_int16(0x0224B7F8, 0x0000)
        #rom.write_int16(0x0224B828, 0x0000)
        #rom.write_int16(0x0224B858, 0x0000)
        sheik_bolero_command = bolero_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_4_3)
        sheik_bolero_command.cue_id = 0 # original 1
        sheik_bolero_command = bolero_cutscene.find_actor_cue_by_start_frame_and_type(5, CutsceneCommandID.CS_CMD_ACTOR_CUE_4_3)
        sheik_bolero_command.cue_id = 0 # original 2
        sheik_bolero_command = bolero_cutscene.find_actor_cue_by_start_frame_and_type(59, CutsceneCommandID.CS_CMD_ACTOR_CUE_4_3)
        sheik_bolero_command.cue_id = 0 # original 1

    # Speed learning Serenade of Water
    serenade_cutscene = scenes[SceneIDs.ICE_CAVERN].headers[4].cutscene_data
    if songs_as_items:
        #delete_cutscene(rom, 0x02BEB250)
        delete_cutscene(serenade_cutscene)
    else:
        location = song_locations['Sheik in Ice Cavern']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        #patch_cutscene_length(rom, 0x02BEB250, 60)
        patch_cutscene_length(serenade_cutscene, 60)
        # Display the Serenade learn Ocarina textbox at frame 0.
        #patch_learn_song_textbox_during_cutscene(rom, 0x02BEC888, 17, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        serenade_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the 0x0075 textbox (You have learned the Serenade of Water!) between 17 and 32 frames.
        #patch_textbox_during_cutscene(rom, 0x02BEC894, 0x0075, 17, 32)
        patch_textbox_during_cutscene(serenade_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 130, text_id, 17, 32)
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        #rom.write_int16s(0x02BEB260, [0x0011, 0x0000, 0x0010])  # action, start, end
        player_cue = serenade_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 0)
        player_cue.cue_id = 17     # original 5
        player_cue.start_frame = 0 # no change
        player_cue.end_frame = 16  # original 10
        # Switch to player action 62 between frames 17 and 32.
        #rom.write_int16s(0x02BEB290, [0x003E, 0x0011, 0x0020])  # action, start, end
        player_cue = serenade_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 10)
        player_cue.cue_id = 62      # original 3
        player_cue.start_frame = 17 # original 10
        player_cue.end_frame = 32   # original 50
        # Put the first action on Sheik's action list to id 0.
        #rom.write_int16(0x02BEB538, 0x0000)
        sheik_serenade_command = serenade_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_4_3)
        sheik_serenade_command.cue_id = 0 # original 1
        # Move out Sheik's initial position to be out of the screen.
        #rom.write_int16(0x02BEB548, 0x8000)
        #rom.write_int16(0x02BEB554, 0x8000)
        sheik_serenade_command.start_pos.y = -2147483366 # original 282
        sheik_serenade_command.end_pos.y = -2147483366 # original 282
        # Restart Ice cavern music on frame 33.
        #rom.write_int16s(0x02BEC852, [0x0021, 0x0022])
        serenade_seq_command = serenade_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_START_SEQ, 1130)
        serenade_seq_command.start_frame = 33 # original 1130
        serenade_seq_command.end_frame = 34 # original 1131

    # Speed Morpha defeat cutscene
    rom.write_int16(0xD3FDA6, 0x43AF) # make the cam look at the ceiling after core burst
    rom.write_int16(0xD3FDBA, 0x0068) # jump some cutscene states, go directly to MO_DEATH_DROPLET instead of MO_DEATH_DRAIN_WATER_1
    rom.write_int16(0xD3FE1E, 0x0020) # change the timer for current state to 32 because the MO_DEATH_DROPLET state starts at timer 30
    rom.write_int16(0xD3FE46, 0xC396) # make the water level down instantly
    rom.write_int32(0xD4021C, 0x00000000) # prevent cam to do a 90 degree rotation
    rom.write_int16(0xD40392, 0x003C) # stop the NA_SE_EN_MOFER_APPEAR sfx after 2sec

    # Speed learning Nocturne of Shadow
    # Burning Kak cutscene
    #patch_cutscene_destination_and_length(rom, 0x01FFE460, 1)
    burning_kak_cutscene = scenes[SceneIDs.KAKARIKO_VILLAGE].headers[4].cutscene_data
    patch_cutscene_destination_and_length(burning_kak_cutscene, 1585, 1)
    # Nocturne of Shadow cutscene
    nocturne_cutscene = scenes[SceneIDs.KAKARIKO_VILLAGE].headers[5].cutscene_data
    if songs_as_items:
        #patch_cutscene_destination_and_length(rom, 0x2000130, 1)
        patch_cutscene_destination_and_length(nocturne_cutscene, 1048, 1)
        #patch_textbox_during_cutscene(rom, 0x02000FE0, 0, 0, 16)
        patch_textbox_during_cutscene(nocturne_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, 0, 0, 16)
    else:
        location = song_locations['Sheik in Kakariko']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        #patch_cutscene_destination_and_length(rom, 0x2000130, 58)
        patch_cutscene_destination_and_length(nocturne_cutscene, 1048, 50)
        # Display the Nocturne learn Ocarina textbox at frame 0.
        #patch_learn_song_textbox_during_cutscene(rom, 0x2000FE0, 19, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        nocturne_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the 0x0077 textbox (You have learned the Nocturne of Shadow!) between 17 and 32 frames.
        #patch_textbox_during_cutscene(rom, 0x02000FEC, 0x0077, 17, 32)
        patch_textbox_during_cutscene(nocturne_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 191, text_id, 17, 32)

    # Speed up draining the well
    # Cutscene in windmill.
    well_windmill_cutscene = Cutscene.decode(rom, 0xE0A000)
    patch_cutscene_destination_and_length(well_windmill_cutscene, 200, 1)
    #patch_cutscene_destination_and_length(rom, 0xE0A010, 1)
    # Drain well in Kakariko cutscene.
    #patch_cutscene_destination_and_length(rom, 0x2001110, 3)
    well_cutscene = scenes[SceneIDs.KAKARIKO_VILLAGE].headers[6].cutscene_data
    patch_cutscene_destination_and_length(well_cutscene, 320, 3)
    # Set the "Drain Well" flag at the second frame (first frame is used by the "Fast Windmill" flag).
    #patch_cutscene_misc_command(rom, 0x20010D8, 2, 3)
    patch_cutscene_misc_command(well_cutscene, 180, 2, 3)

    # This cutscene is not written in the shadow temple scene or in the boat actor, but directly in z_onepointdemo.c instead.
    # So not compatible with our functions.
    if settings.fast_shadow_boat:
        # bg_haka_ship changes to make the boat go faster.
        rom.write_int16(0xD1923E, 0x0000) # Timer to start moving
        rom.write_int16(0xD19426, 0x4348) # Speed x10
        rom.write_int16(0xD19436, 0x447A) # Speed x10
        # Cutscene changes so that it lasts just long enough to prevent jumping to the skulltula.
        # Remove all camera cues of the cutscene past the first one by changing the size of keyFrameCount to 1.
        rom.write_int16(0xAE010E, 0x0001)
        # Change first camera cue point of view to be less awkward.
        # Change viewFlags to 2121, this will make the camera focus on Link.
        rom.write_int16(0xB697F6, 0x2121)
        # Change the length to 4 sec instead of 2 sec.
        rom.write_int16(0xB697F8, 0x0050)
        # Change the at/eye camera values to follow Link from behind.
        # New value : { 0.0f, 0.0f, 0.0f }, { 50.0f, 30.0f, -200.0f}
        rom.write_int32s(0xB69804, [0x00000000, 0x00000000, 0x00000000, 0x42480000, 0x42480000, 0xC3480000])

    # Speed learning Requiem of Spirit
    requiem_cutscene = scenes[SceneIDs.DESERT_COLOSSUS].headers[4].cutscene_data
    if songs_as_items:
        #patch_cutscene_destination_and_length(rom, 0x0218B480, 1)
        #patch_textbox_during_cutscene(rom, 0x0218C57C, 0, 0, 16)
        patch_cutscene_destination_and_length(requiem_cutscene, 1480, 1)
        patch_textbox_during_cutscene(requiem_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, 0, 0, 16)
    else:
        location = song_locations['Sheik at Colossus']
        text_id = location.item.special['text_id']
        # Convert song ID from TEACH to PLAYBACK
        playback_id = location.item.special['song_id'] + 0x0D
        #patch_cutscene_destination_and_length(rom, 0x0218B480, 58)
        patch_cutscene_destination_and_length(requiem_cutscene, 1480, 58)
        # Display the Requiem learn Ocarina textbox at frame 0.
        #patch_learn_song_textbox_during_cutscene(rom, 0x0218C57C, 18, 0, 16)
        playback_command = CutsceneCommandTextOcarinaAction(playback_id, 0, 16, LEARN_SONG_TEXT_ID)
        requiem_cutscene.replace_command_at_start_frame(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, 0, playback_command)
        # Display the 0x0076 textbox (You have learned the Requiem of Spirit!) between 17 and 32 frames.
        #patch_textbox_during_cutscene(rom, 0x0218C588, 0x0076, 17, 32)
        patch_textbox_during_cutscene(requiem_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 295, text_id, 17, 32)
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        #rom.write_int16s(0x0218AF20, [0x0011, 0x0000, 0x0010])  # action, start, end
        player_cue = requiem_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 0)
        player_cue.cue_id = 17     # original 1
        player_cue.start_frame = 0 # no change
        player_cue.end_frame = 16  # original 120
        # Move Link's initial position during this action to be equal to his end position.
        #rom.write_int32s(0x0218AF2C, [0xFFFFFAF9, 0x00000008, 0x00000001])  # start_XYZ
        player_cue.start_pos.x = -1287 # original -1583
        player_cue.start_pos.y = 8     # original 48
        player_cue.start_pos.z = 1     # no change
        # Switch to player action 62 between frames 17 and 32.
        #rom.write_int16s(0x0218AF50, [0x003E, 0x0011, 0x0020])  # action, start, end
        player_cue = requiem_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 120)
        player_cue.cue_id = 62      # original 5
        player_cue.start_frame = 17 # original 120
        player_cue.end_frame = 32   # original 10

    # Speed Nabooru defeat scene
    knuckle_cutscene = scenes[SceneIDs.TWINROVA_BOSS_ROOM].headers[5].cutscene_data
    #patch_cutscene_length(rom, 0x2F5AF80, 5)
    patch_cutscene_length(knuckle_cutscene, 5)
    # Make the current miniboss music end on second frame.
    #rom.write_bytes(0x2F5C7DA, [0x00, 0x01, 0x00, 0x02])
    knuckle_seq_command = knuckle_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_FADEOUT_SEQ, 250)
    knuckle_seq_command.start_frame = 1 # original 250
    knuckle_seq_command.end_frame = 2   # original 350
    # Restart dungeon music on third frame.
    #rom.write_bytes(0x2F5C7A2, [0x00, 0x03, 0x00, 0x04])
    knuckle_seq_command = knuckle_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_START_SEQ, 705)
    knuckle_seq_command.start_frame = 3 # original 705
    knuckle_seq_command.end_frame = 4   # original 706
    # Kill the actors in the cutscene on the first frame by switching their first action by the last.
    # Nabooru
    #rom.write_byte(0x2F5B369, 0x09)
    nabooru_command = knuckle_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_1_4)
    nabooru_command.cue_id = 9 # original 10
    # Iron Knuckle armor part
    #rom.write_byte(0x2F5B491, 0x04)
    nabooru_command = knuckle_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_5_3)
    nabooru_command.cue_id = 4 # original 2
    # Iron Knuckle helmet
    #rom.write_byte(0x2F5B559, 0x04)
    nabooru_command = knuckle_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_6_4)
    nabooru_command.cue_id = 4 # original 2
    # Iron Knuckle armor part
    #rom.write_byte(0x2F5B621, 0x04)
    nabooru_command = knuckle_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_7_2)
    nabooru_command.cue_id = 4 # original 2
    # Iron Knuckle body
    #rom.write_byte(0x2F5B761, 0x07)
    nabooru_command = knuckle_cutscene.find_actor_cue_by_start_frame_and_type(0, CutsceneCommandID.CS_CMD_ACTOR_CUE_4_6)
    nabooru_command.cue_id = 7 # original 5
    # Shorten white flash
    #rom.write_bytes(0x2F5B842, [0x00, 0x01, 0x00, 0x05])
    knuckle_flash_command = knuckle_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_CMD_TRANSITION, 5)
    knuckle_flash_command.start_frame = 1 # original 5
    knuckle_flash_command.end_frame = 5   # original 11

    # Speed Twinrova defeat scene
    # This hacks the textbox handling function to advance the internal timer from frame 170 directly to frame 930.
    # ADDIU $at $zero 0x03A2
    # SH $at 0x0142 $s0
    # Which translates to this->work[CS_TIMER_2] = 930
    rom.write_bytes(0xD678CC, [0x24, 0x01, 0x03, 0xA2, 0xA6, 0x01, 0x01, 0x42])
    # Replaces a if (msgId2 != 0) check by if (0 != 0) to prevent textboxes from starting.
    rom.write_bytes(0xD67BA4, [0x10, 0x00])

    # Cutscene for all medallions never triggers when leaving shadow or spirit temples
    rom.write_byte(0xACA409, 0xAD)
    rom.write_byte(0xACA49D, 0xCE)

    # Speed Bridge of Light cutscene
    #patch_cutscene_length(rom, 0x292D640, 160)
    rainbow_cutscene = scenes[SceneIDs.OUTSIDE_GANONS_CASTLE].headers[4].cutscene_data
    patch_cutscene_length(rainbow_cutscene, 160)
    # Make the rainbow particles fall down between frames 1 and 108.
    #rom.write_bytes(0x292D682, [0x00, 0x01, 0x00, 0x6C])
    rainbow_cue = rainbow_cutscene.find_actor_cue_by_start_frame_and_type(160, CutsceneCommandID.CS_CMD_ACTOR_CUE_1_8)
    rainbow_cue.start_frame = 1
    rainbow_cue.end_frame = 108
    # Make Link look up to the particles by changing the type of first player cue from 5 to 39.
    #rom.write_byte(0x292D6E9, 0x27)
    player_cue = rainbow_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 0)
    player_cue.cue_id = 39 # original 5
    # Make Link look at the bridge by changing the type of second player cue from 39 to 59.
    #rom.write_byte(0x292D719, 0x32)
    player_cue = rainbow_cutscene.find_command_by_start_frame(CutsceneCommandID.CS_SUBCMD_PLAYER_CUE, 0)
    player_cue.cue_id = 50 # original 5
    # Make the rainbow bridge spawn on frame 60.
    #rom.write_int16(0x292D812, 0x003C)
    rainbow_cue = rainbow_cutscene.find_actor_cue_by_start_frame_and_type(270, CutsceneCommandID.CS_CMD_ACTOR_CUE_2_6)
    rainbow_cue.start_frame = 60
    # Remove the first textbox that shows up at frame 20.
    #patch_textbox_during_cutscene(rom, 0x292D924, 0, 20, 150)
    patch_textbox_during_cutscene(rainbow_cutscene, CutsceneCommandID.CS_SUBCMD_TEXT, 20, 0, 20, 150)

    # Speed completion of the trials in Ganon's Castle
    #patch_cutscene_destination_and_length(rom, 0x31A8090, 1)  # Forest
    #patch_cutscene_destination_and_length(rom, 0x31A8B18, 1)  # Water
    #patch_cutscene_destination_and_length(rom, 0x31A9430, 1)  # Shadow
    #patch_cutscene_destination_and_length(rom, 0x31A9E00, 1)  # Fire
    #patch_cutscene_destination_and_length(rom, 0x31AA830, 1)  # Light
    #patch_cutscene_destination_and_length(rom, 0x31AB200, 1)  # Spirit
    forest_sage_cutscene = scenes[SceneIDs.INSIDE_GANONS_CASTLE].get_existing_record_by_vanilla_offset(0x19ED0, RecordType.CutsceneData)
    water_sage_cutscene = scenes[SceneIDs.INSIDE_GANONS_CASTLE].get_existing_record_by_vanilla_offset(0x1A8D0, RecordType.CutsceneData)
    shadow_sage_cutscene = scenes[SceneIDs.INSIDE_GANONS_CASTLE].get_existing_record_by_vanilla_offset(0x1B2A0, RecordType.CutsceneData)
    fire_sage_cutscene = scenes[SceneIDs.INSIDE_GANONS_CASTLE].get_existing_record_by_vanilla_offset(0x1BC70, RecordType.CutsceneData)
    light_sage_cutscene = scenes[SceneIDs.INSIDE_GANONS_CASTLE].get_existing_record_by_vanilla_offset(0x1C6A0, RecordType.CutsceneData)
    spirit_sage_cutscene = scenes[SceneIDs.INSIDE_GANONS_CASTLE].get_existing_record_by_vanilla_offset(0x1D070, RecordType.CutsceneData)
    patch_cutscene_destination_and_length(forest_sage_cutscene, 325, 1)
    patch_cutscene_destination_and_length(fire_sage_cutscene, 325, 1)
    patch_cutscene_destination_and_length(water_sage_cutscene, 325, 1)
    patch_cutscene_destination_and_length(spirit_sage_cutscene, 325, 1)
    patch_cutscene_destination_and_length(shadow_sage_cutscene, 325, 1)
    patch_cutscene_destination_and_length(light_sage_cutscene, 315, 1)

    # Speed scenes during final battle
    # Ganondorf battle end
    # Jump directly from csState 1 to csState 9, the last one before scene transition.
    # Scene transition will happen 180 frames after that.
    rom.write_byte(0xD82047, 0x09)

    # Zelda descends
    # This is completely skipped if tower collapse is disabled.
    # Jump from csState 100 to csState 102.
    rom.write_byte(0xD82AB3, 0x66)
    # In csState 102, jump immediately to 103 after setting Zelda's position instead of 90 frames after.
    rom.write_int32(0xD82DD8, 0x00000000)
    # In csState 103, jump immediately to 104 after setting Zelda's position instead of 200 frames after.
    rom.write_int32(0xD82ED4, 0x00000000)
    # In csState 104, jump to 105 after 51 frames, because some Zelda actor variables are set at frames 10 and 50.
    rom.write_byte(0xD82FDF, 0x33)
    # Jump from csState 104 back to csState 101.
    rom.write_byte(0xD82FAF, 0x65)
    # Jump from csState 101 to csState 1055.
    rom.write_int16(0xD82D2E, 0x041F)
    # Jump from csState 1055 to csState 107.
    rom.write_int16(0xD83142, 0x006B)

    # Speed collapse of Ganon's Tower
    #patch_cutscene_destination_and_length(rom, 0x33FB328, 1)
    ganon_cutscene = scenes[SceneIDs.GANONS_TOWER_COLLAPSE_AND_ARENA].headers[4].cutscene_data
    patch_cutscene_destination_and_length(ganon_cutscene, 1120, 1)

    # After tower collapse
    # Delete a bunch of camera instructions to avoid sudden movement when getting control back.
    # Put subCamId at 0 in csState 0
    rom.write_byte(0xE82DE9, 0x00)
    # Jump from csState 1 to csState 4.
    rom.write_byte(0xE82E0F, 0x04)
    # Remove all main camera changes in csState 4.
    for byte in range(0, 80):
        rom.write_byte(0xE8343C + byte, 0x00)
    # Reduce the 100 frames wait in state 4 to 1. Next cutscene state only starts when Link gets close to Ganon.
    rom.write_int16(0xE8341A, 0x0001)
    # Ganon intro
    # Jump from state 14 to 15 instantly instead of waiting 60 frames.
    rom.write_int32(0xE83B5C, 0x00000000)
    # Jump from state 15 to 16 instantly instead of waiting 140 frames.
    rom.write_int32(0xE83D28, 0x00000000)
    # Remove the Navi textbox at the start of state 28 ("This time, we fight together!).
    rom.write_int16(0xE84C80, 0x1000)

def patch_wondertalk2(rom: Rom, scenes: Scenes, settings: Settings) -> None:
    # Wonder_talk2 is an actor that displays a textbox when near a certain spot, either automatically or by pressing A (button turns to Check).
    # We remove them by moving their Y coordinate far below their normal spot.
    # wonder_talk2_y_coordinates = [
    #     0x27C00BC, 0x27C00CC, 0x27C00DC, 0x27C00EC, 0x27C00FC, 0x27C010C, 0x27C011C, 0x27C012C, # Shadow Temple Whispering Wall Maze (Room 0)
    #     0x27CE080, 0x27CE090, # Shadow Temple Truthspinner (Room 2)
    #     0x2887070, 0x2887080, 0x2887090, # GTG Entrance Room (Room 0)
    #     0x2897070, # GTG Stalfos Room (Room 1)
    #     0x28A1144, # GTG Flame Wall Maze (Room 2)
    #     0x28A60F4, 0x28A6104, # GTG Pushblock Room (Room 3)
    #     0x28AE084, # GTG Rotating Statue Room (Room 4)
    #     0x28B9174, # GTG Megaton Statue Room (Room 5)
    #     0x28BF168, 0x28BF178, 0x28BF188, # GTG Lava Room (Room 6)
    #     0x28C7134, # GTG Dinolfos Room (Room 7)
    #     0x28D0094, # GTG Ice Arrow Room (Room 8)
    #     0x28D91BC, # GTG Shellblade Room (Room 9)
    #     0x225E7E0, # Death Mountain Crater (Room 1)
    #     0x32A50E4, # Thieves' Hideout Green Cell Room 3 torches (Room 1)
    #     0x32AD0E4, # Thieves' Hideout Red Cell Room 1 torch (Room 2)
    #     0x32BD102, # Thieves' Hideout Green Cell Room 4 torches (Room 4)
    #     0x32C1134, # Thieves' Hideout Blue Cell Room 2 torches (Room 5)
    # ]
    # for address in wonder_talk2_y_coordinates:
    #     rom.write_byte(address, 0xFB)

    wonder_talk2_actor_entries = [
        # Shadow Temple Whispering Wall Maze
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[0].headers[0].actor_list.actors[7],
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[0].headers[0].actor_list.actors[8],
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[0].headers[0].actor_list.actors[9],
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[0].headers[0].actor_list.actors[10],
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[0].headers[0].actor_list.actors[11],
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[0].headers[0].actor_list.actors[12],
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[0].headers[0].actor_list.actors[13],
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[0].headers[0].actor_list.actors[14],
        # Shadow Temple Truthspinner
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[2].headers[0].actor_list.actors[3],
        scenes[SceneIDs.SHADOW_TEMPLE].rooms[2].headers[0].actor_list.actors[4],
        # GTG Entrance Room
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[0].headers[0].actor_list.actors[2],
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[0].headers[0].actor_list.actors[3],
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[0].headers[0].actor_list.actors[4],
        # GTG Stalfos Room
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[1].headers[0].actor_list.actors[2],
        # GTG Flame Wall Maze
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[2].headers[0].actor_list.actors[15],
        # GTG Pushblock Room
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[3].headers[0].actor_list.actors[10],
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[3].headers[0].actor_list.actors[11],
        # GTG Rotating Statue Room
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[4].headers[0].actor_list.actors[3],
        # GTG Megaton Statue Room
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[5].headers[0].actor_list.actors[18],
        # GTG Lava Room
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[6].headers[0].actor_list.actors[17],
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[6].headers[0].actor_list.actors[18],
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[6].headers[0].actor_list.actors[19],
        # GTG Dinolfos Room
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[7].headers[0].actor_list.actors[14],
        # GTG Ice Arrow Room
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[8].headers[0].actor_list.actors[4],
        # GTG Shellblade Room
        scenes[SceneIDs.GERUDO_TRAINING_GROUND].rooms[9].headers[0].actor_list.actors[22],
        # Death Mountain Crater
        scenes[SceneIDs.DEATH_MOUNTAIN_CRATER].rooms[1].headers[2].actor_list.actors[44],
        # Thieves' Hideout Green Cell Room 3 torches
        scenes[SceneIDs.THIEVES_HIDEOUT].rooms[1].headers[0].actor_list.actors[9],
        # Thieves' Hideout Red Cell Room 1 torch
        scenes[SceneIDs.THIEVES_HIDEOUT].rooms[2].headers[0].actor_list.actors[9],
        # Thieves' Hideout Green Cell Room 4 torches
        scenes[SceneIDs.THIEVES_HIDEOUT].rooms[4].headers[0].actor_list.actors[11],
        # Thieves' Hideout Blue Cell Room 2 torches
        scenes[SceneIDs.THIEVES_HIDEOUT].rooms[5].headers[0].actor_list.actors[14],
    ]

    # Pre-scene-framework hack replaced the first byte with 0xFB
    bit_mask1 = int.from_bytes(b'\xFB\x00', 'big', signed=True)
    bit_mask2 = int.from_bytes(b'\xFB\xFF', 'big', signed=True)
    for actor in wonder_talk2_actor_entries:
        actor.pos.y = (actor.pos.y | bit_mask1) & bit_mask2

    if 'frogs2' in settings.misc_hints:
        # Prevent setting the replaced textbox flag so that the hint is easily repeatible by walking over the spot again.
        # And move the hint spot down the log so that it doesn't pop every time a song is played, and let some room to do ocarina item glitch.
        #rom.write_int16s(0x2059412, [0x03C0, 0x00E2, 0xFAA6]) # Move coordinates. Original value : 1000, 205, -1202. New value : 960, 226, -1370.
        #rom.write_byte(0x205941F, 0xBF) # Never set the flag.
        actor = scenes[SceneIDs.ZORAS_RIVER].rooms[0].headers[0].actor_list.actors[58]
        actor.pos = Vec3s(960, 226, -1370) # original 1000, -205, -1202
        actor.params = 0x4BBF # original 0x4BBB


# Gaps in IDs are intentional
# https://github.com/zeldaret/oot/blob/7235af2249843fb68740111b70089bad827a4730/include/z64cutscene.h#L35-L165
class CutsceneCommandID(IntEnum):
    CS_CMD_CAM_EYE_SPLINE               = 0x0001
    CS_CMD_CAM_AT_SPLINE                = 0x0002
    CS_CMD_MISC                         = 0x0003
    CS_CMD_LIGHT_SETTING                = 0x0004
    CS_CMD_CAM_EYE_SPLINE_REL_TO_PLAYER = 0x0005
    CS_CMD_CAM_AT_SPLINE_REL_TO_PLAYER  = 0x0006
    CS_CMD_CAM_EYE                      = 0x0007
    CS_CMD_CAM_AT                       = 0x0008
    CS_CMD_RUMBLE_CONTROLLER            = 0x0009
    CS_CMD_PLAYER_CUE                   = 0x000A
    CS_CMD_UNIMPLEMENTED_B              = 0x000B
    CS_CMD_UNIMPLEMENTED_D              = 0x000D
    CS_CMD_ACTOR_CUE_1_0                = 0x000E
    CS_CMD_ACTOR_CUE_0_0                = 0x000F
    CS_CMD_ACTOR_CUE_1_1                = 0x0010
    CS_CMD_ACTOR_CUE_0_1                = 0x0011
    CS_CMD_ACTOR_CUE_0_2                = 0x0012
    CS_CMD_TEXT                         = 0x0013
    CS_CMD_UNIMPLEMENTED_15             = 0x0015
    CS_CMD_UNIMPLEMENTED_16             = 0x0016
    CS_CMD_ACTOR_CUE_0_3                = 0x0017
    CS_CMD_ACTOR_CUE_1_2                = 0x0018
    CS_CMD_ACTOR_CUE_2_0                = 0x0019
    CS_CMD_UNIMPLEMENTED_1A             = 0x001A
    CS_CMD_UNIMPLEMENTED_1B             = 0x001B
    CS_CMD_UNIMPLEMENTED_1C             = 0x001C
    CS_CMD_ACTOR_CUE_3_0                = 0x001D
    CS_CMD_ACTOR_CUE_4_0                = 0x001E
    CS_CMD_ACTOR_CUE_6_0                = 0x001F
    CS_CMD_UNIMPLEMENTED_20             = 0x0020
    CS_CMD_UNIMPLEMENTED_21             = 0x0021
    CS_CMD_ACTOR_CUE_0_4                = 0x0022
    CS_CMD_ACTOR_CUE_1_3                = 0x0023
    CS_CMD_ACTOR_CUE_2_1                = 0x0024
    CS_CMD_ACTOR_CUE_3_1                = 0x0025
    CS_CMD_ACTOR_CUE_4_1                = 0x0026
    CS_CMD_ACTOR_CUE_0_5                = 0x0027
    CS_CMD_ACTOR_CUE_1_4                = 0x0028
    CS_CMD_ACTOR_CUE_2_2                = 0x0029
    CS_CMD_ACTOR_CUE_3_2                = 0x002A
    CS_CMD_ACTOR_CUE_4_2                = 0x002B
    CS_CMD_ACTOR_CUE_5_0                = 0x002C
    CS_CMD_TRANSITION                   = 0x002D
    CS_CMD_ACTOR_CUE_0_6                = 0x002E
    CS_CMD_ACTOR_CUE_4_3                = 0x002F
    CS_CMD_ACTOR_CUE_1_5                = 0x0030
    CS_CMD_ACTOR_CUE_7_0                = 0x0031
    CS_CMD_ACTOR_CUE_2_3                = 0x0032
    CS_CMD_ACTOR_CUE_3_3                = 0x0033
    CS_CMD_ACTOR_CUE_6_1                = 0x0034
    CS_CMD_ACTOR_CUE_3_4                = 0x0035
    CS_CMD_ACTOR_CUE_4_4                = 0x0036
    CS_CMD_ACTOR_CUE_5_1                = 0x0037
    CS_CMD_ACTOR_CUE_6_2                = 0x0039
    CS_CMD_ACTOR_CUE_6_3                = 0x003A
    CS_CMD_UNIMPLEMENTED_3B             = 0x003B
    CS_CMD_ACTOR_CUE_7_1                = 0x003C
    CS_CMD_UNIMPLEMENTED_3D             = 0x003D
    CS_CMD_ACTOR_CUE_8_0                = 0x003E
    CS_CMD_ACTOR_CUE_3_5                = 0x003F
    CS_CMD_ACTOR_CUE_1_6                = 0x0040
    CS_CMD_ACTOR_CUE_3_6                = 0x0041
    CS_CMD_ACTOR_CUE_3_7                = 0x0042
    CS_CMD_ACTOR_CUE_2_4                = 0x0043
    CS_CMD_ACTOR_CUE_1_7                = 0x0044
    CS_CMD_ACTOR_CUE_2_5                = 0x0045
    CS_CMD_ACTOR_CUE_1_8                = 0x0046
    CS_CMD_UNIMPLEMENTED_47             = 0x0047
    CS_CMD_ACTOR_CUE_2_6                = 0x0048
    CS_CMD_UNIMPLEMENTED_49             = 0x0049
    CS_CMD_ACTOR_CUE_2_7                = 0x004A
    CS_CMD_ACTOR_CUE_3_8                = 0x004B
    CS_CMD_ACTOR_CUE_0_7                = 0x004C
    CS_CMD_ACTOR_CUE_5_2                = 0x004D
    CS_CMD_ACTOR_CUE_1_9                = 0x004E
    CS_CMD_ACTOR_CUE_4_5                = 0x004F
    CS_CMD_ACTOR_CUE_1_10               = 0x0050
    CS_CMD_ACTOR_CUE_2_8                = 0x0051
    CS_CMD_ACTOR_CUE_3_9                = 0x0052
    CS_CMD_ACTOR_CUE_4_6                = 0x0053
    CS_CMD_ACTOR_CUE_5_3                = 0x0054
    CS_CMD_ACTOR_CUE_0_8                = 0x0055
    CS_CMD_START_SEQ                    = 0x0056
    CS_CMD_STOP_SEQ                     = 0x0057
    CS_CMD_ACTOR_CUE_6_4                = 0x0058
    CS_CMD_ACTOR_CUE_7_2                = 0x0059
    CS_CMD_ACTOR_CUE_5_4                = 0x005A
    CS_CMD_ACTOR_CUE_0_9                = 0x005D
    CS_CMD_ACTOR_CUE_1_11               = 0x005E
    CS_CMD_ACTOR_CUE_0_10               = 0x0069
    CS_CMD_ACTOR_CUE_2_9                = 0x006A
    CS_CMD_ACTOR_CUE_0_11               = 0x006B
    CS_CMD_ACTOR_CUE_3_10               = 0x006C
    CS_CMD_UNIMPLEMENTED_6D             = 0x006D
    CS_CMD_ACTOR_CUE_0_12               = 0x006E
    CS_CMD_ACTOR_CUE_7_3                = 0x006F
    CS_CMD_UNIMPLEMENTED_70             = 0x0070
    CS_CMD_UNIMPLEMENTED_71             = 0x0071
    CS_CMD_ACTOR_CUE_7_4                = 0x0072
    CS_CMD_ACTOR_CUE_6_5                = 0x0073
    CS_CMD_ACTOR_CUE_1_12               = 0x0074
    CS_CMD_ACTOR_CUE_2_10               = 0x0075
    CS_CMD_ACTOR_CUE_1_13               = 0x0076
    CS_CMD_ACTOR_CUE_0_13               = 0x0077
    CS_CMD_ACTOR_CUE_1_14               = 0x0078
    CS_CMD_ACTOR_CUE_2_11               = 0x0079
    CS_CMD_ACTOR_CUE_0_14               = 0x007B
    CS_CMD_FADE_OUT_SEQ                 = 0x007C
    CS_CMD_ACTOR_CUE_1_15               = 0x007D
    CS_CMD_ACTOR_CUE_2_12               = 0x007E
    CS_CMD_ACTOR_CUE_3_11               = 0x007F
    CS_CMD_ACTOR_CUE_4_7                = 0x0080
    CS_CMD_ACTOR_CUE_5_5                = 0x0081
    CS_CMD_ACTOR_CUE_6_6                = 0x0082
    CS_CMD_ACTOR_CUE_1_16               = 0x0083
    CS_CMD_ACTOR_CUE_2_13               = 0x0084
    CS_CMD_ACTOR_CUE_3_12               = 0x0085
    CS_CMD_ACTOR_CUE_7_5                = 0x0086
    CS_CMD_ACTOR_CUE_4_8                = 0x0087
    CS_CMD_ACTOR_CUE_5_6                = 0x0088
    CS_CMD_ACTOR_CUE_6_7                = 0x0089
    CS_CMD_ACTOR_CUE_0_15               = 0x008A
    CS_CMD_ACTOR_CUE_0_16               = 0x008B
    CS_CMD_TIME                         = 0x008C
    CS_CMD_ACTOR_CUE_1_17               = 0x008D
    CS_CMD_ACTOR_CUE_7_6                = 0x008E
    CS_CMD_ACTOR_CUE_9_0                = 0x008F
    CS_CMD_ACTOR_CUE_0_17               = 0x0090
    CS_CMD_DESTINATION                  = 0x03E8
    # rando-specific command IDs to categorize subcommands
    CS_SUBCMD_CAM_POINT                 = 0x1000
    CS_SUBCMD_TEXT_NONE                 = 0x1001
    CS_SUBCMD_TEXT                      = 0x1002
    CS_SUBCMD_TEXT_OCARINA_ACTION       = 0x1003
    CS_SUBCMD_ACTOR_CUE                 = 0x1004
    CS_SUBCMD_PLAYER_CUE                = 0x1005
    CS_SUBCMD_START_SEQ                 = 0x1006
    CS_SUBCMD_STOP_SEQ                  = 0x1007
    CS_SUBCMD_FADEOUT_SEQ               = 0x1008
    CS_SUBCMD_MISC                      = 0x1009
    CS_SUBCMD_LIGHT_SETTING             = 0x100A
    CS_SUBCMD_RUMBLE_CONTROLLER         = 0x100B
    CS_SUBCMD_TIME                      = 0x100C
    CS_SUBCMD_UNK_DATA                  = 0x100D
    # resume vanilla command IDs
    CS_CMD_END                          = 0xFFFFFFFF

# ZAPD command groups for calculating cutscene byte length
# 0x30 cue length
ACTOR_CUE_COMMANDS = [
    CutsceneCommandID.CS_CMD_PLAYER_CUE,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_1,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_1,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_2,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_3,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_2,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_4_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_6_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_4,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_3,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_1,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_1,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_4_1,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_5,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_4,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_2,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_2,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_4_2,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_5_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_6,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_4_3,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_5,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_7_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_3,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_3,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_6_1,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_4,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_4_4,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_5_1,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_6_2,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_6_3,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_7_1,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_8_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_5,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_6,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_6,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_7,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_4,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_7,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_5,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_8,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_6,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_7,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_8,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_7,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_5_2,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_9,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_4_5,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_10,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_8,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_9,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_4_6,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_5_3,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_8,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_6_4,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_7_2,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_5_4,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_9,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_11,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_10,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_9,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_11,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_10,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_12,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_7_3,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_7_4,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_6_5,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_12,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_10,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_13,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_13,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_14,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_11,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_14,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_15,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_12,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_11,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_4_7,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_5_5,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_6_6,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_16,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_2_13,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_3_12,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_7_5,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_4_8,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_5_6,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_6_7,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_15,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_16,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_1_17,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_7_6,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_9_0,
    CutsceneCommandID.CS_CMD_ACTOR_CUE_0_17,
]
# 0x30 subcommand length
GENERIC_COMMANDS = [
    CutsceneCommandID.CS_CMD_MISC,
    CutsceneCommandID.CS_CMD_LIGHT_SETTING,
    CutsceneCommandID.CS_CMD_START_SEQ,
    CutsceneCommandID.CS_CMD_STOP_SEQ,
    CutsceneCommandID.CS_CMD_FADE_OUT_SEQ,
]
# 0x30 cam point length
CAMERA_COMMANDS = [
    CutsceneCommandID.CS_CMD_CAM_EYE_SPLINE,
    CutsceneCommandID.CS_CMD_CAM_AT_SPLINE,
    CutsceneCommandID.CS_CMD_CAM_EYE_SPLINE_REL_TO_PLAYER,
    CutsceneCommandID.CS_CMD_CAM_AT_SPLINE_REL_TO_PLAYER,
]
# Not used in vanilla game, but defined in cutscene parser
NULL_COMMANDS = [
    CutsceneCommandID.CS_CMD_CAM_EYE,
    CutsceneCommandID.CS_CMD_CAM_AT,
]

# Not used by ZAPD, but these are all structurally identical.
# ZAPD groups these with generic commands (0x30 entry size)
SEQUENCE_COMMANDS = [
    CutsceneCommandID.CS_CMD_START_SEQ,
    CutsceneCommandID.CS_CMD_STOP_SEQ,
    CutsceneCommandID.CS_CMD_FADE_OUT_SEQ,
]


# Tables that contain pointers to scene/room file assets

# z_demo tables
ENTRANCE_CUTSCENE_TABLE_ADDRESS = 0xB65C64
UNKNOWN_LIST_CUTSCENES = 0xB65D74 # does not include NULL first entry

# z_demo_kekkai list
SAGE_CUTSCENES = 0xECF8EC


class Cutscene:
    def __init__(self, vrom_address: int = 0) -> None:
        self.vrom_address: int = vrom_address
        self.commands: list[CutsceneCommand] = []
        self.frames: int = 0
        self.original_length: int = 0

    @staticmethod
    def decode(rom: Rom, vrom_address: int) -> Cutscene:
        cutscene = Cutscene(vrom_address)
        cutscene.parse(rom)
        return cutscene

    def parse(self, rom: Rom) -> None:
        cursor = self.vrom_address
        rom_end = len(rom.buffer)
        # Use while loop with undefined end instead of for loop with num_commands
        #num_commands = rom.read_int32(cursor)
        self.frames = rom.read_s32(cursor + 0x04)
        cursor += 0x08
        cutscene_command_id = rom.read_int32(cursor)
        while cursor < rom_end and cutscene_command_id != CutsceneCommandID.CS_CMD_END:
            cutscene_command_id = rom.read_int32(cursor)
            if cutscene_command_id in ACTOR_CUE_COMMANDS:
                cues, cursor = CutsceneCommandActorCueList.decode(rom, cursor)
                self.commands.append(cues)
            elif cutscene_command_id == CutsceneCommandID.CS_CMD_MISC:
                cmd_list, cursor = CutsceneCommandMiscList.decode(rom, cursor)
                self.commands.append(cmd_list)
            elif cutscene_command_id == CutsceneCommandID.CS_CMD_LIGHT_SETTING:
                cmd_list, cursor = CutsceneCommandLightSettingList.decode(rom, cursor)
                self.commands.append(cmd_list)
            elif cutscene_command_id in SEQUENCE_COMMANDS:
                cmd_list, cursor = CutsceneCommandSequenceList.decode(rom, cursor)
                self.commands.append(cmd_list)
            elif cutscene_command_id in CAMERA_COMMANDS:
                cam, cursor = CutsceneCommandCamSpline.decode(rom, cursor)
                self.commands.append(cam)
            elif cutscene_command_id == CutsceneCommandID.CS_CMD_TEXT:
                cmd, cursor = CutsceneCommandTextList.decode(rom, cursor)
                self.commands.append(cmd)
            elif cutscene_command_id == CutsceneCommandID.CS_CMD_TIME:
                cmd, cursor = CutsceneCommandTimeList.decode(rom, cursor)
                self.commands.append(cmd)
            elif cutscene_command_id == CutsceneCommandID.CS_CMD_RUMBLE_CONTROLLER:
                cmd, cursor = CutsceneCommandRumbleControllerList.decode(rom, cursor)
                self.commands.append(cmd)
            elif cutscene_command_id == CutsceneCommandID.CS_CMD_TRANSITION:
                cmd, cursor = CutsceneCommandTransition.decode(rom, cursor)
                self.commands.append(cmd)
            elif cutscene_command_id == CutsceneCommandID.CS_CMD_DESTINATION:
                cmd, cursor = CutsceneCommandDestination.decode(rom, cursor)
                self.commands.append(cmd)
            elif cutscene_command_id == CutsceneCommandID.CS_CMD_END:
                cursor += 0x08
            else:
                cmd, cursor = CutsceneCommandUnknownDataList.decode(rom, cursor)
                self.commands.append(cmd)
        self.original_length = cursor - self.vrom_address

    def encode(self) -> bytearray:
        bytes = bytearray()
        # CS_BEGIN
        bytes.extend(len(self.commands).to_bytes(4, 'big'))
        bytes.extend(self.frames.to_bytes(4, 'big', signed=True))
        # Cutscene commands
        for command in self.commands:
            bytes.extend(command.encode())
        # CS_END
        bytes.extend(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
        return bytes

    def write(self, rom: Rom) -> None:
        cutscene_bytes = self.encode()
        if len(cutscene_bytes) > self.original_length:
            raise Exception(f'Tried to write cutscene larger than the original to VROM address {self.vrom_address:08X}, (original: {self.original_length:08X} bytes, new: {len(cutscene_bytes):08X} bytes)')
        rom.write_bytes(self.vrom_address, cutscene_bytes)

    def get_commands(self, include_sub_commands: bool) -> list[CutsceneCommand]:
        cmds = [command for command in self.commands]
        if include_sub_commands:
            cmds.extend([sub_command for command in self.commands for sub_command in command.sub_commands])
        return cmds

    @overload
    def find_command(self, id: Literal[CutsceneCommandID.CS_CMD_PLAYER_CUE], include_sub_commands: bool = True) -> Optional[CutsceneCommandActorCueList]: ...
    @overload
    def find_command(self, id: Literal[CutsceneCommandID.CS_SUBCMD_START_SEQ], include_sub_commands: bool = True) -> Optional[CutsceneCommandStartSequence]: ...

    # Returns first instance of a given command ID
    def find_command(self, id: CutsceneCommandID, include_sub_commands: bool = True) -> Optional[CutsceneCommand]:
        found_cmds = list(filter(lambda c: c.id == id, self.get_commands(include_sub_commands)))
        if len(found_cmds) > 0:
            return found_cmds[0]
        else:
            return None

    @overload
    def find_command_by_start_frame(self, id: Literal[CutsceneCommandID.CS_CMD_DESTINATION], frame: int, include_sub_commands: bool = True) -> Optional[CutsceneCommandDestination]: ...
    @overload
    def find_command_by_start_frame(self, id: Literal[CutsceneCommandID.CS_SUBCMD_PLAYER_CUE], frame: int, include_sub_commands: bool = True) -> Optional[CutsceneCommandActorCue]: ...
    @overload
    def find_command_by_start_frame(self, id: Literal[CutsceneCommandID.CS_SUBCMD_START_SEQ], frame: int, include_sub_commands: bool = True) -> Optional[CutsceneCommandStartSequence]: ...
    @overload
    def find_command_by_start_frame(self, id: Literal[CutsceneCommandID.CS_SUBCMD_FADEOUT_SEQ], frame: int, include_sub_commands: bool = True) -> Optional[CutsceneCommandFadeOutSequence]: ...
    @overload
    def find_command_by_start_frame(self, id: Literal[CutsceneCommandID.CS_SUBCMD_MISC], frame: int, include_sub_commands: bool = True) -> Optional[CutsceneCommandMisc]: ...
    @overload
    def find_command_by_start_frame(self, id: Literal[CutsceneCommandID.CS_CMD_TRANSITION], frame: int, include_sub_commands: bool = True) -> Optional[CutsceneCommandTransition]: ...

    # Returns first instance of a given command ID that triggers on the specified start frame
    def find_command_by_start_frame(self, id: CutsceneCommandID, frame: int, include_sub_commands: bool = True) -> Optional[CutsceneCommand]:
        found_cmds = list(filter(lambda c: c.id == id and c.start_frame == frame, self.get_commands(include_sub_commands)))
        if len(found_cmds) > 0:
            return found_cmds[0]
        else:
            return None

    def find_actor_cue_by_start_frame_and_type(self, frame: int, cue_type: int) -> CutsceneCommandActorCue:
        found_cmds = list(filter(lambda c: c.id == cue_type, self.get_commands(False)))
        if len(found_cmds) > 0:
            found_cues = list(filter(lambda c: c.start_frame == frame, [cue for cmd in found_cmds for cue in cmd.sub_commands]))
            if len(found_cues) > 0:
                return found_cues[0]
            else:
                return None
        else:
            return None

    # Replaces first instance of a given command ID with the specified command
    def replace_command(self, id: CutsceneCommandID, command: CutsceneCommand) -> None:
        cmd_idx = 0
        while self.commands[cmd_idx].id != id and cmd_idx < len(self.commands):
            cmd_idx += 1
        if cmd_idx >= len(self.commands):
            raise Exception(f'Could not find cutscene command ID {id.value:08X} in cutscene at vrom address {self.vrom_address:08X}')
        self.commands[cmd_idx] = command

    # Replaces first instance of a given sub command ID with the specified command
    def replace_sub_command(self, id: CutsceneCommandID, command: CutsceneCommand) -> None:
        cmd_idx = 0
        while cmd_idx < len(self.commands):
            subcmd_idx = 0
            if len(self.commands[cmd_idx].sub_commands) > 0:
                while self.commands[cmd_idx].sub_commands[subcmd_idx].id != id and subcmd_idx < len(self.commands[cmd_idx].sub_commands):
                    subcmd_idx += 1
            if subcmd_idx < len(self.commands[cmd_idx].sub_commands):
                break
            cmd_idx += 1
        if cmd_idx >= len(self.commands):
            raise Exception(f'Could not find cutscene sub command ID {id.value:08X} in cutscene at vrom address {self.vrom_address:08X}')
        self.commands[cmd_idx].sub_commands[subcmd_idx] = command

    # Replaces first entry in a list-style cutscene command matching the specified command ID
    def replace_first_sub_command(self, id: CutsceneCommandID, command: CutsceneCommand) -> None:
        cmd_idx = 0
        while self.commands[cmd_idx].id != id and cmd_idx < len(self.commands):
            cmd_idx += 1
        if cmd_idx >= len(self.commands):
            raise Exception(f'Could not find cutscene command ID {id.value:08X} in cutscene at vrom address {self.vrom_address:08X}')
        if len(self.commands[cmd_idx].sub_commands) < 1:
            raise Exception(f'Cannot replace cutscene sub command in an empty cutscene command list of type {id.value:08X} at vrom address {self.vrom_address:08X}')
        self.commands[cmd_idx].sub_commands[0] = command

    # Replaces first command or list-style command sub-command matching the specified command ID
    # and the specified start frame. This should be unique per-cutscene.
    def replace_command_at_start_frame(self, id: CutsceneCommandID, start_frame: int, new_command: CutsceneCommand) -> None:
        cmd_idx = -1
        sub_idx = -1
        for idx, command in enumerate(self.commands):
            if command.id == id and command.start_frame == start_frame:
                cmd_idx = idx
                break
            for idx2, sub_command in enumerate(command.sub_commands):
                if sub_command.id == id and sub_command.start_frame == start_frame:
                    cmd_idx = idx
                    sub_idx = idx2
                    break
            if sub_idx >= 0:
                break
        if sub_idx >= 0:
            self.commands[cmd_idx].sub_commands[sub_idx] = new_command
        elif cmd_idx >= 0:
            self.commands[cmd_idx] = new_command
        else:
            raise Exception(f'Could not find cutscene command ID {id.value:08X} in cutscene at vrom address {self.vrom_address:08X}')


class CutsceneCommand(ABC):
    def __init__(self, id: CutsceneCommandID, start_frame: int = 0, end_frame: int = 0) -> None:
        self.id: CutsceneCommandID = id
        self.start_frame: int = start_frame
        self.end_frame: int = end_frame
        self.sub_commands: list[CutsceneCommand] = []

    @abstractmethod
    def encode(self) -> bytearray:
        raise NotImplementedError(f'Cannot encode undefined cutscene command with id {self.id.value:08X} from frame {self.start_frame} to {self.end_frame}')


class CutsceneCommandCamPoint(CutsceneCommand):
    def __init__(self, continue_flag: int, roll: int, frame: int, view_angle: float, pos: Vec3s, unused: int) -> None:
        super().__init__(CutsceneCommandID.CS_SUBCMD_CAM_POINT, frame)
        self.continue_flag: int = continue_flag
        self.roll: int = roll
        self.view_angle: float = view_angle
        self.pos: Vec3s = pos
        self.unused: int = unused

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandCamPoint:
        return CutsceneCommandCamPoint(
            rom.read_s8(cursor),
            rom.read_byte(cursor + 0x01),
            rom.read_int16(cursor + 0x02),
            rom.read_float(cursor + 0x04),
            Vec3s.decode(rom, cursor + 0x08),
            rom.read_int16(cursor + 0x0E)
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.continue_flag.to_bytes(1, 'big', signed=True))
        bytes.extend(self.roll.to_bytes(1, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(float_to_bytes(self.view_angle))
        bytes.extend(self.pos.encode())
        bytes.extend(self.unused.to_bytes(2, 'big'))
        return bytes


class CutsceneCommandCamSpline(CutsceneCommand):
    def __init__(self, id: CutsceneCommandID, start_frame: int, end_frame: int, points: list[CutsceneCommandCamPoint] = None) -> None:
        super().__init__(id, start_frame, end_frame)
        self.sub_commands: list[CutsceneCommandCamPoint] = points or []

    @staticmethod
    def decode(rom: Rom, address: int) -> tuple[CutsceneCommandCamSpline, int]:
        cursor = address
        cam = CutsceneCommandCamSpline(
            CutsceneCommandID(rom.read_int32(cursor)),
            rom.read_int16(cursor + 0x06),
            rom.read_int16(cursor + 0x08)
        )
        cursor += 0x0C
        continue_flag = 0
        while continue_flag != -1:
            cam_point = CutsceneCommandCamPoint.decode(rom, cursor)
            continue_flag = cam_point.continue_flag
            cam.sub_commands.append(cam_point)
            cursor += 0x10
        return cam, cursor

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(int.to_bytes(1, 2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(int.to_bytes(0, 2, 'big'))
        for point in self.sub_commands:
            bytes.extend(point.encode())
        return bytes


class CutsceneCommandMisc(CutsceneCommand):
    def __init__(self, id: int, start_frame: int, end_frame: int, unused0: int, unused1: int, unused2: int, unused3: int, unused4: int, unused5: int, unused6: int, unused7: int, unused8: int, unused9: int, unused10: int) -> None:
        # ID in this case is the from CutsceneMiscType, not a cutscene command ID
        super().__init__(CutsceneCommandID.CS_SUBCMD_MISC, start_frame, end_frame)
        self.type_id: int = id
        self.unused0: int = unused0
        self.unused1: int = unused1
        self.unused2: int = unused2
        self.unused3: int = unused3
        self.unused4: int = unused4
        self.unused5: int = unused5
        self.unused6: int = unused6
        self.unused7: int = unused7
        self.unused8: int = unused8
        self.unused9: int = unused9
        self.unused10: int = unused10

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandMisc:
        return CutsceneCommandMisc(
            rom.read_int16(cursor),
            rom.read_int16(cursor + 0x02),
            rom.read_int16(cursor + 0x04),
            rom.read_int16(cursor + 0x06),
            rom.read_int32(cursor + 0x08),
            rom.read_int32(cursor + 0x0C),
            rom.read_int32(cursor + 0x10),
            rom.read_int32(cursor + 0x14),
            rom.read_int32(cursor + 0x18),
            rom.read_int32(cursor + 0x1C),
            rom.read_int32(cursor + 0x20),
            rom.read_int32(cursor + 0x24),
            rom.read_int32(cursor + 0x28),
            rom.read_int32(cursor + 0x2C),
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.type_id.to_bytes(2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(self.unused0.to_bytes(2, 'big'))
        bytes.extend(self.unused1.to_bytes(4, 'big'))
        bytes.extend(self.unused2.to_bytes(4, 'big'))
        bytes.extend(self.unused3.to_bytes(4, 'big'))
        bytes.extend(self.unused4.to_bytes(4, 'big'))
        bytes.extend(self.unused5.to_bytes(4, 'big'))
        bytes.extend(self.unused6.to_bytes(4, 'big'))
        bytes.extend(self.unused7.to_bytes(4, 'big'))
        bytes.extend(self.unused8.to_bytes(4, 'big'))
        bytes.extend(self.unused9.to_bytes(4, 'big'))
        bytes.extend(self.unused10.to_bytes(4, 'big'))
        return bytes


class CutsceneCommandMiscList(CutsceneCommand):
    def __init__(self, id: CutsceneCommandID, start_frame: int = 0, end_frame: int = 0, sub_commands: list[CutsceneCommandMisc] = None) -> None:
        super().__init__(id, start_frame, end_frame)
        self.sub_commands: list[CutsceneCommandMisc] = sub_commands or []

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandMiscList, int]:
        cmd_list = CutsceneCommandMiscList(
            CutsceneCommandID(rom.read_int32(cursor))
        )
        num_entries = rom.read_int32(cursor + 0x04)
        for i in range(num_entries):
            cmd_list.sub_commands.append(CutsceneCommandMisc.decode(rom, cursor + 0x08 + 0x30 * i))
        return cmd_list, cursor + 0x08 + 0x30 * num_entries

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(len(self.sub_commands).to_bytes(4, 'big'))
        for cmd in self.sub_commands:
            bytes.extend(cmd.encode())
        return bytes


class CutsceneCommandLightSetting(CutsceneCommand):
    def __init__(self, light_setting: int, start_frame: int, end_frame: int, unused0: int, unused1: int, unused2: int, unused3: int, unused4: int, unused5: int, unused6: int, unused7: int, unused8: int, unused9: int, unused10: int) -> None:
        super().__init__(CutsceneCommandID.CS_SUBCMD_LIGHT_SETTING, start_frame, end_frame)
        self.light_setting: int = light_setting
        self.unused0: int = unused0
        self.unused1: int = unused1
        self.unused2: int = unused2
        self.unused3: int = unused3
        self.unused4: int = unused4
        self.unused5: int = unused5
        self.unused6: int = unused6
        self.unused7: int = unused7
        self.unused8: int = unused8
        self.unused9: int = unused9
        self.unused10: int = unused10

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandLightSetting:
        return CutsceneCommandLightSetting(
            # first byte always 0
            rom.read_byte(cursor + 0x01) - 1,
            rom.read_int16(cursor + 0x02),
            rom.read_int16(cursor + 0x04),
            rom.read_int16(cursor + 0x06),
            rom.read_int32(cursor + 0x08),
            rom.read_int32(cursor + 0x0C),
            rom.read_int32(cursor + 0x10),
            rom.read_int32(cursor + 0x14),
            rom.read_int32(cursor + 0x18),
            rom.read_int32(cursor + 0x1C),
            rom.read_int32(cursor + 0x20),
            rom.read_int32(cursor + 0x24),
            rom.read_int32(cursor + 0x28),
            rom.read_int32(cursor + 0x2C),
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(int.to_bytes(0, 1, 'big'))
        bytes.extend((self.light_setting + 1).to_bytes(1, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(self.unused0.to_bytes(2, 'big'))
        bytes.extend(self.unused1.to_bytes(4, 'big'))
        bytes.extend(self.unused2.to_bytes(4, 'big'))
        bytes.extend(self.unused3.to_bytes(4, 'big'))
        bytes.extend(self.unused4.to_bytes(4, 'big'))
        bytes.extend(self.unused5.to_bytes(4, 'big'))
        bytes.extend(self.unused6.to_bytes(4, 'big'))
        bytes.extend(self.unused7.to_bytes(4, 'big'))
        bytes.extend(self.unused8.to_bytes(4, 'big'))
        bytes.extend(self.unused9.to_bytes(4, 'big'))
        bytes.extend(self.unused10.to_bytes(4, 'big'))
        return bytes


class CutsceneCommandLightSettingList(CutsceneCommand):
    def __init__(self, start_frame: int = 0, end_frame: int = 0, sub_commands: list[CutsceneCommandLightSetting] = None) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_LIGHT_SETTING, start_frame, end_frame)
        self.sub_commands: list[CutsceneCommandLightSetting] = sub_commands or []

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandLightSettingList, int]:
        light_list = CutsceneCommandLightSettingList()
        num_entries = rom.read_int32(cursor + 0x04)
        for i in range(num_entries):
            light_list.sub_commands.append(CutsceneCommandLightSetting.decode(rom, cursor + 0x08 + 0x30 * i))
        return light_list, cursor + 0x08 + 0x30 * num_entries

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(len(self.sub_commands).to_bytes(4, 'big'))
        for cmd in self.sub_commands:
            bytes.extend(cmd.encode())
        return bytes


class CutsceneCommandRumbleController(CutsceneCommand):
    def __init__(self, unused0: int, start_frame: int, end_frame: int, source_strength: int, duration: int, decrease_rate: int, unused1: int, unused2: int) -> None:
        super().__init__(CutsceneCommandID.CS_SUBCMD_RUMBLE_CONTROLLER, start_frame, end_frame)
        self.source_strength: int = source_strength
        self.duration: int = duration
        self.decrease_rate: int = decrease_rate
        self.unused0: int = unused0
        self.unused1: int = unused1
        self.unused2: int = unused2

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandRumbleController:
        return CutsceneCommandRumbleController(
            rom.read_int16(cursor),
            rom.read_int16(cursor + 0x02),
            rom.read_int16(cursor + 0x04),
            rom.read_byte(cursor + 0x06),
            rom.read_byte(cursor + 0x07),
            rom.read_byte(cursor + 0x08),
            rom.read_byte(cursor + 0x09),
            rom.read_int16(cursor + 0x0A)
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.unused0.to_bytes(2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(self.source_strength.to_bytes(1, 'big'))
        bytes.extend(self.duration.to_bytes(1, 'big'))
        bytes.extend(self.decrease_rate.to_bytes(1, 'big'))
        bytes.extend(self.unused1.to_bytes(1, 'big'))
        bytes.extend(self.unused2.to_bytes(2, 'big'))
        return bytes


class CutsceneCommandRumbleControllerList(CutsceneCommand):
    def __init__(self, start_frame: int = 0, end_frame: int = 0, sub_commands: list[CutsceneCommandRumbleController] = None) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_RUMBLE_CONTROLLER, start_frame, end_frame)
        self.sub_commands: list[CutsceneCommandRumbleController] = sub_commands or []

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandRumbleControllerList, int]:
        rumble_list = CutsceneCommandRumbleControllerList()
        num_entries = rom.read_int32(cursor + 0x04)
        for i in range(num_entries):
            rumble_list.sub_commands.append(CutsceneCommandRumbleController.decode(rom, cursor + 0x08 + 0x0C * i))
        return rumble_list, cursor + 0x08 + 0x0C * num_entries

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(len(self.sub_commands).to_bytes(4, 'big'))
        for cmd in self.sub_commands:
            bytes.extend(cmd.encode())
        return bytes


class CutsceneCommandActorCue(CutsceneCommand):
    def __init__(self, command_id: CutsceneCommandID, id: int, start_frame: int, end_frame: int, rot: Vec3s, start_pos: Vec3i, end_pos: Vec3i, unused0: float, unused1: float, unused2: float) -> None:
        # ID in this case is the cue ID, not a cutscene command ID
        if command_id == CutsceneCommandID.CS_CMD_PLAYER_CUE:
            cue_command_id = CutsceneCommandID.CS_SUBCMD_PLAYER_CUE
        else:
            cue_command_id = CutsceneCommandID.CS_SUBCMD_ACTOR_CUE
        super().__init__(cue_command_id, start_frame, end_frame)
        self.cue_id: int = id
        self.rot: Vec3s = rot
        self.start_pos: Vec3i = start_pos
        self.end_pos: Vec3i = end_pos
        # decomp has these as floats for some reason
        self.unused0: float = unused0
        self.unused1: float = unused1
        self.unused2: float = unused2

    @staticmethod
    def decode(rom: Rom, cursor: int, command_id: CutsceneCommandID) -> CutsceneCommandActorCue:
        return CutsceneCommandActorCue(
            command_id,
            rom.read_int16(cursor),
            rom.read_int16(cursor + 0x02),
            rom.read_int16(cursor + 0x04),
            Vec3s.decode(rom, cursor + 0x06),
            Vec3i.decode(rom, cursor + 0x0C),
            Vec3i.decode(rom, cursor + 0x18),
            rom.read_float(cursor + 0x24),
            rom.read_float(cursor + 0x28),
            rom.read_float(cursor + 0x2C)
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.cue_id.to_bytes(2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(self.rot.encode())
        bytes.extend(self.start_pos.encode())
        bytes.extend(self.end_pos.encode())
        bytes.extend(float_to_bytes(self.unused0))
        bytes.extend(float_to_bytes(self.unused1))
        bytes.extend(float_to_bytes(self.unused2))
        return bytes


class CutsceneCommandActorCueList(CutsceneCommand):
    def __init__(self, id: CutsceneCommandID, start_frame: int = 0, end_frame: int = 0, cues: list[CutsceneCommandActorCue] = None) -> None:
        super().__init__(id, start_frame, end_frame)
        self.sub_commands: list[CutsceneCommandActorCue] = cues or []

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandActorCueList, int]:
        cue_list = CutsceneCommandActorCueList(
            CutsceneCommandID(rom.read_int32(cursor))
        )
        num_entries = rom.read_int32(cursor + 0x04)
        for i in range(num_entries):
            cue_list.sub_commands.append(CutsceneCommandActorCue.decode(rom, cursor + 0x08 + 0x30 * i, cue_list.id))
        return cue_list, cursor + 0x08 + 0x30 * num_entries

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(len(self.sub_commands).to_bytes(4, 'big'))
        for cue in self.sub_commands:
            bytes.extend(cue.encode())
        return bytes


class CutsceneCommandText(CutsceneCommand):
    def __init__(self, id: int, start_frame: int, end_frame: int, text_type: int, alt_id1: int, alt_id2: int) -> None:
        # ID in this case is the text ID, not a cutscene command ID
        super().__init__(CutsceneCommandID.CS_SUBCMD_TEXT, start_frame, end_frame)
        self.text_id: int = id
        self.text_type: int = text_type
        self.alt_id1: int = alt_id1
        self.alt_id2: int = alt_id2

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandText:
        return CutsceneCommandText(
            rom.read_int16(cursor),
            rom.read_int16(cursor + 0x02),
            rom.read_int16(cursor + 0x04),
            rom.read_int16(cursor + 0x06),
            rom.read_int16(cursor + 0x08),
            rom.read_int16(cursor + 0x0A),
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.text_id.to_bytes(2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(self.text_type.to_bytes(2, 'big'))
        bytes.extend(self.alt_id1.to_bytes(2, 'big'))
        bytes.extend(self.alt_id2.to_bytes(2, 'big'))
        return bytes


class CutsceneCommandTextNone(CutsceneCommand):
    def __init__(self, start_frame: int, end_frame: int) -> None:
        # ID in this case is the text ID, not a cutscene command ID
        super().__init__(CutsceneCommandID.CS_SUBCMD_TEXT_NONE, start_frame, end_frame)

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandTextNone:
        return CutsceneCommandTextNone(
            rom.read_int16(cursor + 0x02),
            rom.read_int16(cursor + 0x04)
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(int.to_bytes(0xFFFF, 2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(int.to_bytes(0xFFFF, 2, 'big'))
        bytes.extend(int.to_bytes(0xFFFF, 2, 'big'))
        bytes.extend(int.to_bytes(0xFFFF, 2, 'big'))
        return bytes


class CutsceneCommandTextOcarinaAction(CutsceneCommand):
    def __init__(self, ocarina_action: int, start_frame: int, end_frame: int, message_id: int) -> None:
        super().__init__(CutsceneCommandID.CS_SUBCMD_TEXT_OCARINA_ACTION, start_frame, end_frame)
        self.ocarina_action: int = ocarina_action
        self.message_id: int = message_id

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandTextOcarinaAction:
        return CutsceneCommandTextOcarinaAction(
            rom.read_int16(cursor),
            rom.read_int16(cursor + 0x02),
            rom.read_int16(cursor + 0x04),
            rom.read_int16(cursor + 0x08)
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.ocarina_action.to_bytes(2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(int.to_bytes(0x0002, 2, 'big'))
        bytes.extend(self.message_id.to_bytes(2, 'big'))
        bytes.extend(int.to_bytes(0xFFFF, 2, 'big'))
        return bytes


class CutsceneCommandTextList(CutsceneCommand):
    def __init__(self, id: CutsceneCommandID, start_frame: int = 0, end_frame: int = 0, cmds: list[CutsceneCommandText | CutsceneCommandTextNone | CutsceneCommandTextOcarinaAction] = None) -> None:
        super().__init__(id, start_frame, end_frame)
        self.sub_commands: list[CutsceneCommandText | CutsceneCommandTextNone | CutsceneCommandTextOcarinaAction] = cmds or []

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandTextList, int]:
        text_list = CutsceneCommandTextList(
            CutsceneCommandID(rom.read_int32(cursor))
        )
        num_entries = rom.read_int32(cursor + 0x04)
        for i in range(num_entries):
            if rom.read_int16(cursor + 0x08 + 0x0C * i + 0x06) == 0x0002:
                text_list.sub_commands.append(CutsceneCommandTextOcarinaAction.decode(rom, cursor + 0x08 + 0x0C * i))
            elif rom.read_int16(cursor + 0x08 + 0x0C * i) == 0xFFFF:
                text_list.sub_commands.append(CutsceneCommandTextNone.decode(rom, cursor + 0x08 + 0x0C * i))
            else:
                text_list.sub_commands.append(CutsceneCommandText.decode(rom, cursor + 0x08 + 0x0C * i))
        return text_list, cursor + 0x08 + 0x0C * num_entries

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(len(self.sub_commands).to_bytes(4, 'big'))
        for text_cmd in self.sub_commands:
            bytes.extend(text_cmd.encode())
        return bytes


class CutsceneCommandTransition(CutsceneCommand):
    def __init__(self, transition_type: int, start_frame: int = 0, end_frame: int = 0) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_TRANSITION, start_frame, end_frame)
        self.transition_type: int = transition_type

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandTransition, int]:
        return CutsceneCommandTransition(
            rom.read_int16(cursor + 0x08),
            rom.read_int16(cursor + 0x0A),
            rom.read_int16(cursor + 0x0C)
        ), cursor + 0x10

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(int.to_bytes(1, 4, 'big'))
        bytes.extend(self.transition_type.to_bytes(2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        return bytes


class CutsceneCommandSequenceCommand(CutsceneCommand):
    def __init__(self, command_type: CutsceneCommandID, id: int, start_frame: int, end_frame: int, unused0: int, unused1: int, unused2: int, unused3: int, unused4: int, unused5: int, unused6: int, unused7: int) -> None:
        # ID in this case is the sequence ID, not a cutscene command ID
        if command_type == CutsceneCommandID.CS_CMD_START_SEQ:
            sub_type = CutsceneCommandID.CS_SUBCMD_START_SEQ
        elif command_type == CutsceneCommandID.CS_CMD_STOP_SEQ:
            sub_type = CutsceneCommandID.CS_SUBCMD_STOP_SEQ
        elif command_type == CutsceneCommandID.CS_CMD_FADE_OUT_SEQ:
            sub_type = CutsceneCommandID.CS_SUBCMD_FADEOUT_SEQ
        else:
            raise Exception(f'Unimplemented cutscene audio sequence command ID {command_type:04X}')
        super().__init__(sub_type, start_frame, end_frame)
        self.seq_id: int = id
        self.unused0: int = unused0
        self.unused1: int = unused1
        self.unused2: int = unused2
        self.unused3: int = unused3
        self.unused4: int = unused4
        self.unused5: int = unused5
        self.unused6: int = unused6
        self.unused7: int = unused7

    @staticmethod
    def decode(rom: Rom, cursor: int, command_type: int) -> CutsceneCommandSequenceCommand:
        return CutsceneCommandSequenceCommand(
            command_type,
            rom.read_int16(cursor) - 1, # not true for FADE_OUT, but shouldn't be a practical impact
            rom.read_int16(cursor + 0x02),
            rom.read_int16(cursor + 0x04),
            rom.read_int16(cursor + 0x06),
            rom.read_int32(cursor + 0x08),
            rom.read_int32(cursor + 0x0C),
            rom.read_int32(cursor + 0x10),
            rom.read_int32(cursor + 0x14),
            rom.read_int32(cursor + 0x18),
            rom.read_int32(cursor + 0x1C),
            rom.read_int32(cursor + 0x20),
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend((self.seq_id + 1).to_bytes(2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(self.unused0.to_bytes(2, 'big'))
        bytes.extend(self.unused1.to_bytes(4, 'big'))
        bytes.extend(self.unused2.to_bytes(4, 'big'))
        bytes.extend(self.unused3.to_bytes(4, 'big'))
        bytes.extend(self.unused4.to_bytes(4, 'big'))
        bytes.extend(self.unused5.to_bytes(4, 'big'))
        bytes.extend(self.unused6.to_bytes(4, 'big'))
        bytes.extend(self.unused7.to_bytes(4, 'big'))
        bytes.extend(int.to_bytes(0, 12, 'big'))
        return bytes


class CutsceneCommandSequenceList(CutsceneCommand):
    def __init__(self, id: CutsceneCommandID, start_frame: int = 0, end_frame: int = 0, sub_commands: list[CutsceneCommandSequenceCommand] = None) -> None:
        super().__init__(id, start_frame, end_frame)
        self.sub_commands: list[CutsceneCommandSequenceCommand] = sub_commands or []

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandSequenceList, int]:
        cmd_list = CutsceneCommandSequenceList(
            CutsceneCommandID(rom.read_int32(cursor))
        )
        num_entries = rom.read_int32(cursor + 0x04)
        for i in range(num_entries):
            cmd_list.sub_commands.append(CutsceneCommandSequenceCommand.decode(rom, cursor + 0x08 + 0x30 * i, cmd_list.id))
        return cmd_list, cursor + 0x08 + 0x30 * num_entries

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(len(self.sub_commands).to_bytes(4, 'big'))
        for cmd in self.sub_commands:
            bytes.extend(cmd.encode())
        return bytes


# Convenience classes for start/stop/fade out sequences. All data is handled the same for each command.
class CutsceneCommandStartSequence(CutsceneCommandSequenceCommand):
    def __init__(self, seq_id: int, start_frame: int, end_frame: int, unused0: int, unused1: int, unused2: int, unused3: int, unused4: int, unused5: int, unused6: int, unused7: int) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_START_SEQ, seq_id, start_frame, end_frame, unused0, unused1, unused2, unused3, unused4, unused5, unused6, unused7)

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandSequenceCommand:
        return CutsceneCommandSequenceCommand.decode(rom, cursor, CutsceneCommandID.CS_CMD_START_SEQ)

class CutsceneCommandStartSequenceList(CutsceneCommandSequenceList):
    def __init__(self, start_frame: int = 0, end_frame: int = 0, sub_commands: list[CutsceneCommandSequenceCommand] = None) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_START_SEQ, start_frame, end_frame, sub_commands)


class CutsceneCommandStopSequence(CutsceneCommandSequenceCommand):
    def __init__(self, seq_id: int, start_frame: int, end_frame: int, unused0: int, unused1: int, unused2: int, unused3: int, unused4: int, unused5: int, unused6: int, unused7: int) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_STOP_SEQ, seq_id, start_frame, end_frame, unused0, unused1, unused2, unused3, unused4, unused5, unused6, unused7)

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandSequenceCommand:
        return CutsceneCommandSequenceCommand.decode(rom, cursor, CutsceneCommandID.CS_CMD_STOP_SEQ)


class CutsceneCommandStopSequenceList(CutsceneCommandSequenceList):
    def __init__(self, start_frame: int = 0, end_frame: int = 0, sub_commands: list[CutsceneCommandSequenceCommand] = None) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_STOP_SEQ, start_frame, end_frame, sub_commands)


class CutsceneCommandFadeOutSequence(CutsceneCommandSequenceCommand):
    def __init__(self, seq_player: int, start_frame: int, end_frame: int, unused0: int, unused1: int, unused2: int, unused3: int, unused4: int, unused5: int, unused6: int, unused7: int) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_FADE_OUT_SEQ, seq_player, start_frame, end_frame, unused0, unused1, unused2, unused3, unused4, unused5, unused6, unused7)

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandSequenceCommand:
        return CutsceneCommandSequenceCommand.decode(rom, cursor, CutsceneCommandID.CS_CMD_FADE_OUT_SEQ)


class CutsceneCommandFadeOutSequenceList(CutsceneCommandSequenceList):
    def __init__(self, start_frame: int = 0, end_frame: int = 0, sub_commands: list[CutsceneCommandSequenceCommand] = None) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_FADE_OUT_SEQ, start_frame, end_frame, sub_commands)


class CutsceneCommandTime(CutsceneCommand):
    def __init__(self, unused0: int, start_frame: int, end_frame: int, hour: int, minute: int) -> None:
        super().__init__(CutsceneCommandID.CS_SUBCMD_TIME, start_frame, end_frame)
        self.hour: int = hour
        self.minute: int = minute
        self.unused0: int = unused0

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandTime:
        return CutsceneCommandTime(
            rom.read_int16(cursor),
            rom.read_int16(cursor + 0x02),
            rom.read_int16(cursor + 0x04),
            rom.read_byte(cursor + 0x06),
            rom.read_byte(cursor + 0x07)
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.unused0.to_bytes(2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(self.hour.to_bytes(1, 'big'))
        bytes.extend(self.minute.to_bytes(1, 'big'))
        bytes.extend(int.to_bytes(0, 4, 'big'))
        return bytes


class CutsceneCommandTimeList(CutsceneCommand):
    def __init__(self, start_frame: int = 0, end_frame: int = 0, sub_commands: list[CutsceneCommandTime] = None) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_TIME, start_frame, end_frame)
        self.sub_commands: list[CutsceneCommandTime] = sub_commands or []

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandTimeList, int]:
        time_list = CutsceneCommandTimeList()
        num_entries = rom.read_int32(cursor + 0x04)
        for i in range(num_entries):
            time_list.sub_commands.append(CutsceneCommandTime.decode(rom, cursor + 0x08 + 0x0C * i))
        return time_list, cursor + 0x08 + 0x0C * num_entries

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(len(self.sub_commands).to_bytes(4, 'big'))
        for cmd in self.sub_commands:
            bytes.extend(cmd.encode())
        return bytes


class CutsceneCommandDestination(CutsceneCommand):
    def __init__(self, destination: int, start_frame: int = 0, end_frame: int = 0) -> None:
        super().__init__(CutsceneCommandID.CS_CMD_DESTINATION, start_frame, end_frame)
        self.destination: int = destination

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandDestination, int]:
        return CutsceneCommandDestination(
            rom.read_int16(cursor + 0x08),
            rom.read_int16(cursor + 0x0A),
            rom.read_int16(cursor + 0x0C)
        ), cursor + 0x10

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(int.to_bytes(1, 4, 'big'))
        bytes.extend(self.destination.to_bytes(2, 'big'))
        bytes.extend(self.start_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        bytes.extend(self.end_frame.to_bytes(2, 'big'))
        return bytes


class CutsceneCommandUnknownData(CutsceneCommand):
    def __init__(self, unk1: int, unk2: int, unk3: int, unk4: int, unk5: int, unk6: int, unk7: int, unk8: int, unk9: int, unk10: int, unk11: int, unk12: int) -> None:
        # ID in this case is the from CutsceneMiscType, not a cutscene command ID
        super().__init__(CutsceneCommandID.CS_SUBCMD_UNK_DATA)
        self.unk1: int = unk1
        self.unk2: int = unk2
        self.unk3: int = unk3
        self.unk4: int = unk4
        self.unk5: int = unk5
        self.unk6: int = unk6
        self.unk7: int = unk7
        self.unk8: int = unk8
        self.unk9: int = unk9
        self.unk10: int = unk10
        self.unk11: int = unk11
        self.unk12: int = unk12

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CutsceneCommandUnknownData:
        return CutsceneCommandUnknownData(
            rom.read_int32(cursor),
            rom.read_int32(cursor + 0x04),
            rom.read_int32(cursor + 0x08),
            rom.read_int32(cursor + 0x0C),
            rom.read_int32(cursor + 0x10),
            rom.read_int32(cursor + 0x14),
            rom.read_int32(cursor + 0x18),
            rom.read_int32(cursor + 0x1C),
            rom.read_int32(cursor + 0x20),
            rom.read_int32(cursor + 0x24),
            rom.read_int32(cursor + 0x28),
            rom.read_int32(cursor + 0x2C),
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.unk1.to_bytes(4, 'big'))
        bytes.extend(self.unk2.to_bytes(4, 'big'))
        bytes.extend(self.unk3.to_bytes(4, 'big'))
        bytes.extend(self.unk4.to_bytes(4, 'big'))
        bytes.extend(self.unk5.to_bytes(4, 'big'))
        bytes.extend(self.unk6.to_bytes(4, 'big'))
        bytes.extend(self.unk7.to_bytes(4, 'big'))
        bytes.extend(self.unk8.to_bytes(4, 'big'))
        bytes.extend(self.unk9.to_bytes(4, 'big'))
        bytes.extend(self.unk10.to_bytes(4, 'big'))
        bytes.extend(self.unk11.to_bytes(4, 'big'))
        bytes.extend(self.unk12.to_bytes(4, 'big'))
        return bytes


class CutsceneCommandUnknownDataList(CutsceneCommand):
    def __init__(self, id: CutsceneCommandID, start_frame: int = 0, end_frame: int = 0, sub_commands: list[CutsceneCommandUnknownData] = None) -> None:
        super().__init__(id, start_frame, end_frame)
        self.sub_commands: list[CutsceneCommandUnknownData] = sub_commands or []

    @staticmethod
    def decode(rom: Rom, cursor: int) -> tuple[CutsceneCommandUnknownDataList, int]:
        cmd_list = CutsceneCommandUnknownDataList(
            CutsceneCommandID(rom.read_int32(cursor))
        )
        num_entries = rom.read_int32(cursor + 0x04)
        for i in range(num_entries):
            cmd_list.sub_commands.append(CutsceneCommandUnknownData.decode(rom, cursor + 0x08 + 0x30 * i))
        return cmd_list, cursor + 0x08 + 0x30 * num_entries

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.value.to_bytes(4, 'big'))
        bytes.extend(len(self.sub_commands).to_bytes(4, 'big'))
        for cmd in self.sub_commands:
            bytes.extend(cmd.encode())
        return bytes
