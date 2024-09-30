from typing import Optional

from Rom import Rom
from Settings import Settings

def delete_cutscene(rom: Rom, address: int) -> None:
    # Address is the start of the cutscene commands.
    # Insert the CS END command at the start of the file.
    rom.write_int32(address + 4, 0xFFFFFFFF)

def patch_cutscene_length(rom: Rom, address: int, new_length: int) -> None:
    # Address is the start of the cutscene commands.
    # Syntax is number of cutscene commands, then number of frames.
    rom.write_int32(address + 4, new_length)

# Some cutscenes sends Link in a different location at the end. The command that sets the destination also sets the length of these cutscenes.
def patch_cutscene_destination_and_length(rom: Rom, address: int, new_length: int, new_destination: Optional[int] = None) -> None:
    # Address is the start of the arguments of the CS_CMD_DESTINATION (or CS_TERMINATOR) command to modify.
    # The previous values should be respectively 0x000003E8 and 0x00000001.
    cmd_destination_value = rom.read_int32(address - 8)
    cmd_destination_constant = rom.read_int32(address - 4)

    if cmd_destination_value != 0x03E8 or cmd_destination_constant != 0x01:
        raise Exception("Wrong address to patch cutscene destination or length.")

    if new_destination:
        rom.write_int16(address, new_destination)
    rom.write_int16(address + 2, new_length)

def patch_textbox_during_cutscene(rom: Rom, address: int, textbox_id: int, start_frame: int, end_frame: int) -> None:
    # Address is the start of the textboxes commands during cutscene.
    # Put textbox_id at 0 to delete a textbox that would show up otherwise.
    if textbox_id == 0:
        rom.write_int16(address, 0xFFFF) # CS_TEXT_ID_NONE
        rom.write_int16(address + 2, start_frame)
        rom.write_int16(address + 4, end_frame)
        rom.write_int16(address + 6, 0xFFFF) # constant 0xFFFF
        rom.write_int16(address + 8, 0xFFFF) # CS_TEXT_ID_NONE
        rom.write_int16(address + 10, 0xFFFF) # CS_TEXT_ID_NONE
    else:
        rom.write_int16(address, textbox_id)
        rom.write_int16(address + 2, start_frame)
        rom.write_int16(address + 4, end_frame)
        rom.write_int16(address + 6, 0) # CutsceneTextType, always 0 unless we want to make a choice textbox.
        rom.write_int16(address + 8, 0xFFFF) # First choice of a choice texbox
        rom.write_int16(address + 10, 0xFFFF) # Second choice of a choice texbox

# This is a special case of the function above, because ocarina textboxes are initialized differently.
def patch_learn_song_textbox_during_cutscene(rom: Rom, address: int, ocarina_song_id: int, start_frame: int, end_frame: int) -> None:
    # Address is the start of the textboxes commands during cutscene.
    rom.write_int16(address, ocarina_song_id)
    rom.write_int16(address + 2, start_frame)
    rom.write_int16(address + 4, end_frame)
    rom.write_int16(address + 6, 0x0002) # constant CS_TEXT_OCARINA_ACTION
    rom.write_int16(address + 8, 0x088B) # id of the textbox used to replay a song on Ocarina, also constant
    rom.write_int16(address + 10, 0xFFFF) # Unused

def patch_cutscene_scene_transition(rom: Rom, address: int, transition_type: int, start_frame: int, end_frame:int) -> None:
    # Address is the start of the textboxes commands during cutscene.
    rom.write_int16(address, transition_type) # CS_TEXT_ID_NONE
    rom.write_int16(address + 2, start_frame)
    rom.write_int16(address + 4, end_frame)
    rom.write_int16(address + 6, end_frame)

# This is mostly used to set flags during cutscenes.
def patch_cutscene_misc_command(rom: Rom, address: int, start_frame:int, end_frame:int, new_misc_type: Optional[int] = None) -> None:
    # Address should be the start of the CS_MISC command.
    if new_misc_type:
        rom.write_int16(address, new_misc_type)
    rom.write_int16(address + 2, start_frame)
    rom.write_int16(address + 4, end_frame)

def patch_cutscenes(rom: Rom, songs_as_items: bool, settings: Settings) -> None:
    # Speed scene after Deku Tree
    # Deku Tree talking to Link.
    # Cut to 1 frame and redirect destination to the get Emerald cutscene (0x07).
    patch_cutscene_destination_and_length(rom, 0x2077E20, 1, 0x07)
    # Recieve the Emerald cutscene.
    patch_cutscene_destination_and_length(rom, 0x2078A10, 31)
    # Display the 0x0080 textbox (You got the Kokiri's Emerald!) between 0 and 30 frames.
    patch_textbox_during_cutscene(rom, 0x2079570, 0x0080, 0, 30)
    # Display no text between 30 and 40 frames.
    patch_textbox_during_cutscene(rom, 0x207957C, 0, 30, 40)

    # Speed obtaining Fairy Ocarina
    patch_cutscene_destination_and_length(rom, 0x2151230, 60)
    # Make Link cross the whole bridge instead of stopping in the middle by moving the destinate coordinate
    # of the first player cue in the cutscene.
    rom.write_bytes(0x2150E20, [0xFF, 0xFF, 0xFA, 0x4C])

    # Speed Zelda's Letter scene
    # Change the exit from the castle maze courtyard to Zelda's courtyard to the start of the cutscene where you get the letter.
    # Initial value 0x400 : ENTR_CASTLE_COURTYARD_ZELDA_0. New value 0x5F0 : ENTR_CASTLE_COURTYARD_ZELDA_1
    rom.write_int16(0x290E08E, 0x05F0)
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

    # Speed learning Zelda's Lullaby
    # Redirect to 0x73 : CS_DEST_HYRULE_FIELD_FROM_IMPA_ESCORT from originally 0x33 : CS_DEST_HYRULE_FIELD_FROM_ZELDAS_COURTYARD
    if songs_as_items:
        patch_cutscene_destination_and_length(rom, 0x2E8E914, 1, 0x73)
        patch_textbox_during_cutscene(rom, 0x02E8E924, 0, 0, 16)
    else:
        patch_cutscene_destination_and_length(rom, 0x2E8E914, 59, 0x73)
        # Display the Zelda's Lullaby learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x02E8E924, 23, 0, 16)
        # Display the 0x00D4 textbox (You've learned Zelda's Lullaby!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x2E8E930, 0x00D4, 17, 32)

    # Speed learning Epona's Song
    if songs_as_items:
        patch_cutscene_destination_and_length(rom, 0x029BEF68, 1)
    else:
        patch_cutscene_destination_and_length(rom, 0x029BEF68, 10)
        # The cutscene actually happens after learning the song, so we don't need to change the learn song textbox.
        # Display the 0x00D2 textbox (You've learned Epona's Song!) at frame 0.
        patch_textbox_during_cutscene(rom, 0x029BECB8, 0x00D6, 0, 9)
        # Make sure no textbox shows at frame 10.
        patch_textbox_during_cutscene(rom, 0x029BECC4, 0, 10, 11)

    # Speed up opening the royal tomb for both child and adult
    patch_cutscene_length(rom, 0x2025020, 1)
    patch_cutscene_length(rom, 0x2023C80, 1)
    # Change the first actor cue from type 1 to type 2.
    # This will make the grave explode on frame 0 instead of frame 392.
    rom.write_byte(0x2025159, 0x02)
    rom.write_byte(0x2023E19, 0x02)

    # Speed learning Sun's Song
    if songs_as_items:
        delete_cutscene(rom, 0x0332A4A0)
    else:
        patch_cutscene_length(rom, 0x0332A4A0, 60)
        # Display the Sun's song learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x332A870, 24, 0, 16)
        # Display the 0x00D3 textbox (You've learned Sun's Song!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x332A87C, 0x00D3, 17, 32)

    # Speed Deku Seed Upgrade Scrub Cutscene
    rom.write_bytes(0xECA900, [0x24, 0x03, 0xC0, 0x00])  # scrub angle
    rom.write_bytes(0xECAE90, [0x27, 0x18, 0xFD, 0x04])  # skip straight to giving item
    rom.write_bytes(0xECB618, [0x25, 0x6B, 0x00, 0xD4])  # skip straight to digging back in
    rom.write_bytes(0xECAE70, [0x00, 0x00, 0x00, 0x00])  # never initialize cs camera
    rom.write_bytes(0xE5972C, [0x24, 0x08, 0x00, 0x01])  # timer set to 1 frame for giving item

    # Speed learning Saria's Song
    if songs_as_items:
        delete_cutscene(rom, 0x020B1730)
    else:
        patch_cutscene_length(rom, 0x020B1730, 60)
        # Display the Saria's song learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x20B1DB0, 21, 0, 16)
        # Display the 0x00D1 textbox (You've learned Saria's Song!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x20B1DBC, 0x00D1, 17, 32)
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        rom.write_int16s(0x020B19C8, [0x0011, 0x0000, 0x0010])  # action, start, end
        # Switch to player action 62 between frames 17 and 32.
        rom.write_int16s(0x020B19F8, [0x003E, 0x0011, 0x0020])  # action, start, end
        # Adjust manually the Y coordinate of Link because action 62 is adult only probably?
        rom.write_int16(0x020B1A0A, 0x01D4)
        rom.write_int16(0x020B1A16, 0x01D4)

    # Play Sarias Song to Darunia
    delete_cutscene(rom, 0x22769E0)

    # Speed scene after Dodongo's Cavern
    patch_cutscene_destination_and_length(rom, 0x2221E88, 59)
    # Display the 0x0081 textbox (You got the Goron's Ruby!) between 0 and 58 frames.
    patch_textbox_during_cutscene(rom, 0x2223308, 0x0081, 0, 58)

    # Speed up Death Mountain Trail Owl Flight
    patch_cutscene_destination_and_length(rom, 0x223B6B0, 1)

    # Jabu Jabu swallowing Link
    patch_cutscene_destination_and_length(rom, 0xCA0784, 1)

    # Ruto pointing to the Zora Sapphire when you enter Big Octo's room.
    delete_cutscene(rom, 0xD03BA8)

    # Speed scene after Jabu Jabu's Belly
    # Cut Ruto talking to Link when entering the blue warp.
    rom.write_int32(0xCA3530, 0x00000000)
    patch_cutscene_destination_and_length(rom, 0x2113340, 59)
    # Display the 0x0081 textbox (You got the Zora's Sapphire!) between 0 and 58 frames.
    patch_textbox_during_cutscene(rom, 0x2113C18, 0x0082, 0, 58)
    # Ensure the initial white screen will stay on screen for 59 frames and not switch briefly to the next cutscene.
    patch_cutscene_scene_transition(rom, 0x21131D0, 1, 0, 59)

    # Speed up Lake Hylia Owl Flight
    patch_cutscene_destination_and_length(rom, 0x20E60D0, 1)

    # Speed Zelda escaping from Hyrule Castle
    patch_cutscene_destination_and_length(rom, 0x1FC0CFC, 1)

    # Speed learning Song of Time
    if songs_as_items:
        patch_cutscene_destination_and_length(rom, 0x0252FBA0, 1)
    else:
        patch_cutscene_destination_and_length(rom, 0x0252FBA0, 59)
        # Display the Song of Time learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x0252FC88, 25, 0, 16)
        # Display the 0x00D5 textbox (You've learned Song of Time!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x0252FC94, 0x00D5, 17, 32)

    # Hyrule Field small cutscene after learning Song of Time.
    delete_cutscene(rom, 0x01FC3B80)

    # Speed opening of Door of Time
    patch_cutscene_length(rom, 0xE0A170, 2)
    # Set the "Opened Door of Time" flag at the first frame.
    patch_cutscene_misc_command(rom, 0xE0A358, 1, 2)

    # Master Sword pedestal cutscene
    patch_cutscene_destination_and_length(rom, 0xCB6BE8, 20) # Child => Adult
    patch_cutscene_destination_and_length(rom, 0xCB75B8, 20) # Adult => Child

    # Speed learning Song of Storms
    # The cutscene actually happens after learning the song, so we don't need to change the Ocarina texboxes.
    # But the flag for the check is set at frame 10 during the cutscene, so cut it short here, and just show the "You"ve learned.." textbox before.
    if songs_as_items:
         delete_cutscene(rom, 0x03041080)
    else:
        patch_cutscene_length(rom, 0x03041080, 10)
        # Display the 0x00D6 textbox (You've learned Song of Storms!) at frame 0.
        patch_textbox_during_cutscene(rom, 0x03041090, 0x00D6, 0, 9)

    # Speed up Epona race start
    patch_cutscene_length(rom, 0x29BE980, 2)
    # Make the race music start on frame 1.
    rom.write_byte(0x29BE9CB, 0x01)

    # Speed up Epona escape
    # We have to wait until Epona is on a not awkward spot.
    patch_cutscene_length(rom, 0x1FC79E0, 84) # South
    patch_cutscene_length(rom, 0x1FC7F00, 84) # East
    patch_cutscene_length(rom, 0x1FC8550, 84) # West
    patch_cutscene_length(rom, 0x1FC8B30, 42) # Front gates

    # Speed learning Minuet of Forest
    if songs_as_items:
        delete_cutscene(rom, 0x020AFF80)
    else:
        patch_cutscene_length(rom, 0x020AFF80, 60)
        # Display the Minuet learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x020B0808, 5, 0, 16)
        # Display the 0x0073 textbox (You have learned the Minuet of Forest!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x020B0814, 0x0073, 17, 32)
        # Restart Lost woods music on frame 33.
        rom.write_int16s(0x020B0492, [0x0021, 0x0022])
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        rom.write_int16s(0x020AFF90, [0x0011, 0x0000, 0x0010])  # action, start, end
        # Switch to player action 62 between frames 17 and 32.
        rom.write_int16s(0x020AFFC1, [0x003E, 0x0011, 0x0020])  # action, start, end

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
    # Saria becomes a Sage cutscene.
    # Cut to 59 frames and redirect to the third part of the Deku Sprout cutscene (0x45).
    patch_cutscene_destination_and_length(rom, 0xD4ED68, 59, 0x45)
    # Display the 0x003E textbox (You received the Forest Medallion!) between 0 and 58 frames.
    patch_textbox_during_cutscene(rom, 0xD4ED78, 0x003E, 0, 58)
    # Deku Sprout cutscene number 3.
    delete_cutscene(rom, 0x207B9D0)

    # Speed learning Prelude of Light
    if songs_as_items:
        delete_cutscene(rom, 0x0252FD20)
    else:
        patch_cutscene_length(rom, 0x0252FD20, 74)
         # Display the Minuet learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x02531328, 20, 0, 16)
        # Display the 0x0078 textbox (You have learned the Prelude of Light!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x02531334, 0x0078, 17, 32)
        # Make the first action on Sheik's action list end immediately.
        rom.write_int16(0x0252FF1C, 0x0000)
        # Restart Temple of Time music on frame 33.
        rom.write_int16s(0x025313DA, [0x0021, 0x0022])

    # Speed learning Bolero of Fire
    if songs_as_items:
        delete_cutscene(rom, 0x0224B5D0)
    else:
        patch_cutscene_length(rom, 0x0224B5D0, 60)
        # Display the Bolero learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x0224D7F0, 16, 0, 16)
        # Display the 0x0073 textbox (You have learned the Bolero of Fire!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x0224D7FC, 0x0073, 17, 32)
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        rom.write_int16s(0x0224B5E0, [0x0011, 0x0000, 0x0010])  # action, start, end
        # Switch to player action 62 between frames 17 and 32.
        rom.write_int16s(0x0224B610, [0x003E, 0x0011, 0x0020])  # action, start, end
        # Put the first three actions on Sheik's action list to id 0.
        rom.write_int16(0x0224B7F8, 0x0000)
        rom.write_int16(0x0224B828, 0x0000)
        rom.write_int16(0x0224B858, 0x0000)

    # Speed scene after Fire Temple
    # Crater volcano erupting from Kakariko.
    patch_cutscene_destination_and_length(rom, 0x2001848, 1)
    # Darunia becomes a Sage cutscene.
    patch_cutscene_destination_and_length(rom, 0xD100B4, 59)
    # Display the 0x003C textbox (You received the Fire Medallion!) between 0 and 58 frames.
    patch_textbox_during_cutscene(rom, 0xD10134, 0x003C, 0, 58)

    # Speed learning Serenade of Water
    if songs_as_items:
        delete_cutscene(rom, 0x02BEB250)
    else:
        patch_cutscene_length(rom, 0x02BEB250, 60)
        # Display the Serenade learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x02BEC888, 17, 0, 16)
        # Display the 0x0075 textbox (You have learned the Serenade of Water!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x02BEC894, 0x0075, 17, 32)
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        rom.write_int16s(0x02BEB260, [0x0011, 0x0000, 0x0010])  # action, start, end
        # Switch to player action 62 between frames 17 and 32.
        rom.write_int16s(0x02BEB290, [0x003E, 0x0011, 0x0020])  # action, start, end
        # Put the first action on Sheik's action list to id 0.
        rom.write_int16(0x02BEB538, 0x0000)
        # Move out Sheik's initial position to be out of the screen.
        rom.write_int16(0x02BEB548, 0x8000)
        rom.write_int16(0x02BEB554, 0x8000)
        # Restart Ice cavern music on frame 33.
        rom.write_int16s(0x02BEC852, [0x0021, 0x0022])

    # Speed scene after Water Temple
    # Ruto becomes a Sage cutscene.
    patch_cutscene_destination_and_length(rom, 0xD5A458, 59)
    # Display the 0x003D textbox (You received the Water Medallion!) between 0 and 58 frames.
    patch_textbox_during_cutscene(rom, 0xD5A3A8, 0x003D, 0, 58)
    # Set the "Restored Lake Hylia water" flag at the first frame.
    patch_cutscene_misc_command(rom, 0x20D0B68, 1, 2)
    # Lake Hylia restored water cutscene.
    patch_cutscene_destination_and_length(rom, 0x20D0D20, 2)

    # Speed learning Nocturne of Shadow
    # Burning Kak cutscene
    patch_cutscene_destination_and_length(rom, 0x01FFE460, 1)
    # Nocturne of Shadow cutscene
    if songs_as_items:
        patch_cutscene_destination_and_length(rom, 0x2000130, 1)
        patch_textbox_during_cutscene(rom, 0x02000FE0, 0, 0, 16)
    else:
        patch_cutscene_destination_and_length(rom, 0x2000130, 58)
        # Display the Nocturne learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x2000FE0, 19, 0, 16)
        # Display the 0x0077 textbox (You have learned the Nocturne of Shadow!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x02000FEC, 0x0077, 17, 32)

    # Speed up draining the well
    # Cutscene in windmill.
    patch_cutscene_destination_and_length(rom, 0xE0A010, 1)
    # Drain well in Kakariko cutscene.
    patch_cutscene_destination_and_length(rom, 0x2001110, 3)
    # Set the "Drain Well" flag at the second frame (first frame is used by the "Fast Windmill" flag).
    patch_cutscene_misc_command(rom, 0x20010D8, 2, 3)

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

    # Speed scene after Shadow Temple
    # Impa becomes a Sage cutscene.
    patch_cutscene_destination_and_length(rom, 0xD13EC8, 59)
    # Display the 0x0041 textbox (You received the Shadow Medallion!) between 0 and 58 frames.
    patch_textbox_during_cutscene(rom, 0xD13E18, 0x0041, 0, 58)

    # Speed learning Requiem of Spirit
    if songs_as_items:
        patch_cutscene_destination_and_length(rom, 0x0218B480, 1)
        patch_textbox_during_cutscene(rom, 0x0218C57C, 0, 0, 16)
    else:
        patch_cutscene_destination_and_length(rom, 0x0218B480, 58)
        # Display the Requiem learn Ocarina textbox at frame 0.
        patch_learn_song_textbox_during_cutscene(rom, 0x0218C57C, 18, 0, 16)
        # Display the 0x0076 textbox (You have learned the Requiem of Spirit!) between 17 and 32 frames.
        patch_textbox_during_cutscene(rom, 0x0218C588, 0x0076, 17, 32)
        # Modify Link's actions so that he doesn't have the cutscene's behaviour.
        # Switch to player action 17 between frames 0 and 16.
        rom.write_int16s(0x0218AF20, [0x0011, 0x0000, 0x0010])  # action, start, end
        # Move Link's initial position during this action to be equal to his end position.
        rom.write_int32s(0x0218AF2C, [0xFFFFFAF9, 0x00000008, 0x00000001])  # start_XYZ
        # Switch to player action 62 between frames 17 and 32.
        rom.write_int16s(0x0218AF50, [0x003E, 0x0011, 0x0020])  # action, start, end

    # Speed Nabooru defeat scene
    patch_cutscene_length(rom, 0x2F5AF80, 5)
    # Make the current miniboss music end on second frame.
    rom.write_bytes(0x2F5C7DA, [0x00, 0x01, 0x00, 0x02])
    # Restart dungeon music on third frame.
    rom.write_bytes(0x2F5C7A4, [0x00, 0x03, 0x00, 0x04])
    # Kill the actors in the cutscene on the first frame by switching their first action by the last.
    # Nabooru
    rom.write_byte(0x2F5B369, 0x09)
    # Iron Knuckle armor part
    rom.write_byte(0x2F5B491, 0x04)
    # Iron Knuckle helmet
    rom.write_byte(0x2F5B559, 0x04)
    # Iron Knuckle armor part
    rom.write_byte(0x2F5B621, 0x04)
    # Iron Knuckle body
    rom.write_byte(0x2F5B761, 0x07)
    # Shorten white flash
    rom.write_bytes(0x2F5B842, [0x00, 0x01, 0x00, 0x05])

    # Speed Twinrova defeat scene
    # This hacks the textbox handling function to advance the internal timer from frame 170 directly to frame 930.
    # ADDIU $at $zero 0x03A2
    # SH $at 0x0142 $s0
    # Which translates to this->work[CS_TIMER_2] = 930
    rom.write_bytes(0xD678CC, [0x24, 0x01, 0x03, 0xA2, 0xA6, 0x01, 0x01, 0x42])
    # Replaces a if (msgId2 != 0) check by if (0 != 0) to prevent textboxes from starting.
    rom.write_bytes(0xD67BA4, [0x10, 0x00])

    # Speed scene after Spirit Temple
    # Nabooru becomes a Sage cutscene.
    patch_cutscene_destination_and_length(rom, 0xD3A0A8, 59)
    # Display the 0x003F textbox (You received the Spirit Medallion!) between 0 and 58 frames.
    patch_textbox_during_cutscene(rom, 0xD39FF0, 0x003F, 0, 58)

    # Cutscene for all medallions never triggers when leaving shadow or spirit temples
    rom.write_byte(0xACA409, 0xAD)
    rom.write_byte(0xACA49D, 0xCE)

    # Speed Bridge of Light cutscene
    patch_cutscene_length(rom, 0x292D640, 160)
    # Make the rainbow particles fall down between frames 1 and 108.
    rom.write_bytes(0x292D682, [0x00, 0x01, 0x00, 0x6C])
    # Make Link look up to the particles by changing the type of first player cue from 5 to 39.
    rom.write_byte(0x292D6E9, 0x27)
    # Make Link look at the bridge by changing the type of second player cue from 39 to 59.
    rom.write_byte(0x292D719, 0x32)
    # Make the rainbow bridge spawn on frame 60.
    rom.write_int16(0x292D812, 0x003C)
    # Remove the first textbox that shows up at frame 20.
    patch_textbox_during_cutscene(rom, 0x292D924, 0, 20, 150)

    # Speed completion of the trials in Ganon's Castle
    patch_cutscene_destination_and_length(rom, 0x31A8090, 1)  # Forest
    patch_cutscene_destination_and_length(rom, 0x31A9E00, 1)  # Fire
    patch_cutscene_destination_and_length(rom, 0x31A8B18, 1)  # Water
    patch_cutscene_destination_and_length(rom, 0x31A9430, 1)  # Shadow
    patch_cutscene_destination_and_length(rom, 0x31AB200, 1)  # Spirit
    patch_cutscene_destination_and_length(rom, 0x31AA830, 1)  # Light

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
    patch_cutscene_destination_and_length(rom, 0x33FB328, 1)

    # After tower collapse
    # Jump from csState 1 to csState 4, 100 frames before giving back control. Next state only starts when Link gets near Ganon.
    rom.write_byte(0xE82E0F, 0x04)
    # Ganon intro
    # Jump from state 14 to 15 instantly instead of waiting 60 frames.
    rom.write_int32(0xE83B5C, 0x00000000)
    # Jump from state 15 to 16 instantly instead of waiting 140 frames.
    rom.write_int32(0xE83D28, 0x00000000)
    # Remove the Navi textbox at the start of state 28 ("This time, we fight together!).
    rom.write_int16(0xE84C80, 0x1000)

def patch_wondertalk2(rom: Rom) -> None:
    # Wonder_talk2 is an actor that displays a textbox when near a certain spot, either automatically or by pressing A (button turns to Check).
    # We remove them by moving their Y coordinate far below their normal spot.
    wonder_talk2_y_coordinates = [
        0x27C00BC, 0x27C00CC, 0x27C00DC, 0x27C00EC, 0x27C00FC, 0x27C010C, 0x27C011C, 0x27C012C, # Shadow Temple Whispering Wall Maze (Room 0)
        0x27CE080, 0x27CE090, # Shadow Temple Truthspinner (Room 2)
        0x2887070, 0x2887080, 0x2887090, # GTG Entrance Room (Room 0)
        0x2897070, # GTG Stalfos Room (Room 1)
        0x28A1144, # GTG Flame Wall Maze (Room 2)
        0x28A60F4, 0x28A6104, # GTG Pushblock Room (Room 3)
        0x28AE084, # GTG Rotating Statue Room (Room 4)
        0x28B9174, # GTG Megaton Statue Room (Room 5)
        0x28BF168, 0x28BF178, 0x28BF188, # GTG Lava Room (Room 6)
        0x28C7134, # GTG Dinolfos Room (Room 7)
        0x28D0094, # GTG Ice Arrow Room (Room 8)
        0x28D91BC, # GTG Shellblade Room (Room 9)
        0x225E7E0, # Death Mountain Crater (Room 1)
        0x32A50E4, # Thieves' Hideout Green Cell Room 3 torches (Room 1)
        0x32AD0E4, # Thieves' Hideout Red Cell Room 1 torch (Room 2)
        0x32BD102, # Thieves' Hideout Green Cell Room 4 torches (Room 4)
        0x32C1134, # Thieves' Hideout Blue Cell Room 2 torches (Room 5)
    ]
    for address in wonder_talk2_y_coordinates:
        rom.write_byte(address, 0xFB)
